"""FastAPI application: response models, middleware, and the routes.

Routes:
  GET  /                  — health check
  GET  /health            — health check (same payload)
  POST /palm/read         — image + hand → short summary + 7-day predictions
  GET  /logs              — list recently saved request records (newest first)
  GET  /logs/{record_id}  — full saved record (input metadata + output)
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import API_PORT, MODEL_ID, STORAGE_DIR, logger
from .gemma_model import LocalGemma
from .predictor import PalmAstrologyPredictor
from .storage import save_request_record
from .utils import no_palm_detected


# ═══════════════════════════════════════════════════════════════════════════
#                               APP + SINGLETONS
# ═══════════════════════════════════════════════════════════════════════════
app = FastAPI(
    title="Todozee Premium — Palm Astrology API",
    description="AI-powered 7-day palm-astrology predictions from a LOCAL Gemma model. "
                "Input: palm image + hand side.",
    version="3.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singletons (model loaded at startup via _startup hook below)
gemma = LocalGemma(MODEL_ID)
predictor = PalmAstrologyPredictor(gemma)


# ═══════════════════════════════════════════════════════════════════════════
#                            MIDDLEWARE + STARTUP
# ═══════════════════════════════════════════════════════════════════════════
@app.middleware("http")
async def log_requests(request: Request, call_next):
    req_log = logging.getLogger("http")
    client = request.client.host if request.client else "-"
    t0 = time.time()
    req_log.info("→ %s %s  from=%s", request.method, request.url.path, client)
    try:
        response = await call_next(request)
    except Exception as e:
        req_log.exception("✗ Unhandled error on %s %s: %s",
                          request.method, request.url.path, e)
        return JSONResponse(status_code=500,
                            content={"detail": "Internal server error"})
    dt = (time.time() - t0) * 1000
    req_log.info("← %s %s  status=%d  %.0fms",
                 request.method, request.url.path, response.status_code, dt)
    return response


@app.on_event("startup")
def _startup():
    logger.info("Starting model load at app startup...")
    gemma.load()
    if gemma.ready:
        logger.info("🚀 API ready on port %d | device=%s", API_PORT, gemma.device)
    else:
        logger.warning("⚠️  API started in DEGRADED mode — model not loaded. "
                       "Dynamic fallback readings will be used.")


# ═══════════════════════════════════════════════════════════════════════════
#                              RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════
class DailyPrediction(BaseModel):
    date: str
    day_name: str
    day_of_week: int
    prediction: str


class PalmReadingResponse(BaseModel):
    generated_at: str
    model_used: str
    hand: str
    summary: str
    weekly_predictions: List[DailyPrediction]


class HealthResponse(BaseModel):
    status: str
    model: str
    model_ready: bool
    device: str


class LogEntry(BaseModel):
    record_id: str
    received_at: str
    status: str
    model_used: str
    hand: Optional[str] = None
    summary_preview: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
#                                  ROUTES
# ═══════════════════════════════════════════════════════════════════════════
def _validate_upload(filename: str) -> None:
    allowed_ext = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ext = Path(filename or "").suffix.lower()
    if ext not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Use: {', '.join(sorted(allowed_ext))}",
        )


def _health_payload() -> HealthResponse:
    return HealthResponse(
        status="ok" if gemma.ready else "degraded",
        model=gemma.model_id,
        model_ready=gemma.ready,
        device=gemma.device,
    )


@app.get("/", response_model=HealthResponse)
def root():
    return _health_payload()


@app.get("/health", response_model=HealthResponse)
def health():
    return _health_payload()


@app.post("/palm/read", response_model=PalmReadingResponse)
async def read_palm(
    file: UploadFile = File(..., description="Palm image (jpg, png, webp, gif)"),
    hand: str = Form(..., description="Which hand: 'left' or 'right'"),
):
    """Palm image + hand side → short summary + 7-day predictions."""
    _validate_upload(file.filename or "")
    hand_norm = (hand or "").strip().lower()
    if hand_norm not in ("left", "right"):
        raise HTTPException(
            status_code=400,
            detail="Field 'hand' must be 'left' or 'right'.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    logger.info("▶ /palm/read  file=%s size=%d hand=%s",
                file.filename, len(image_bytes), hand_norm)

    palm_reading = predictor.analyze_palm_image_bytes(image_bytes, hand=hand_norm)
    if no_palm_detected(palm_reading):
        logger.info("▶ /palm/read  no palm detected in image")
        save_request_record(image_bytes, file.filename or "",
                            status="no_palm", model_id=gemma.model_id,
                            hand=hand_norm, palm_reading=palm_reading)
        raise HTTPException(
            status_code=400,
            detail="No palm detected. Please upload a clear photo of a palm.",
        )

    summary = predictor.generate_summary(palm_reading)
    predictions = predictor.generate_weekly_predictions(palm_reading)
    save_request_record(image_bytes, file.filename or "",
                        status="ok", model_id=gemma.model_id,
                        hand=hand_norm, palm_reading=palm_reading,
                        summary=summary, predictions=predictions)

    return PalmReadingResponse(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        model_used=gemma.model_id,
        hand=hand_norm,
        summary=summary,
        weekly_predictions=[DailyPrediction(**p) for p in predictions],
    )


# ── /logs: browse persisted request records ─────────────────────────────
def _safe_record_id(record_id: str) -> str:
    if "/" in record_id or "\\" in record_id or ".." in record_id:
        raise HTTPException(status_code=400, detail="Invalid record id.")
    return record_id


@app.get("/logs", response_model=List[LogEntry])
def list_logs(limit: int = 50):
    """List recently saved request records, newest first. ?limit=N (max 500)."""
    limit = max(1, min(limit, 500))
    json_files = sorted(STORAGE_DIR.glob("*.json"), reverse=True)[:limit]
    entries: List[LogEntry] = []
    for jp in json_files:
        try:
            data = json.loads(jp.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Skipping unreadable record %s: %s", jp.name, e)
            continue
        out = data.get("output") or {}
        summary = (out.get("summary") or "") or ""
        entries.append(LogEntry(
            record_id=data.get("record_id", jp.stem),
            received_at=data.get("received_at", ""),
            status=data.get("status", "?"),
            model_used=data.get("model_used", ""),
            hand=(data.get("input") or {}).get("hand"),
            summary_preview=(summary[:160] + "…") if len(summary) > 160 else summary,
        ))
    return entries


@app.get("/logs/{record_id}")
def get_log(record_id: str):
    """Full saved record (input metadata + output) by record_id."""
    record_id = _safe_record_id(record_id)
    jp = STORAGE_DIR / f"{record_id}.json"
    if not jp.exists():
        raise HTTPException(status_code=404, detail="Record not found.")
    try:
        return json.loads(jp.read_text(encoding="utf-8"))
    except Exception as e:
        logger.exception("Failed to read record %s: %s", record_id, e)
        raise HTTPException(status_code=500, detail="Record unreadable.")
