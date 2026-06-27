"""Per-request persistence: writes the input image + a JSON output record."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import STORAGE_DIR, logger
from .utils import get_image_hash


def save_request_record(image_bytes: bytes,
                        filename: str,
                        status: str,
                        model_id: str,
                        hand: Optional[str] = None,
                        palm_reading: Optional[str] = None,
                        summary: Optional[str] = None,
                        predictions: Optional[List[dict]] = None) -> Optional[str]:
    """Persist one request's input image + output to STORAGE_DIR.

    Writes two files per request, both keyed by `{timestamp}_{md5[:8]}`:
      - the raw uploaded image (original extension preserved)
      - a `.json` record with `input` and `output` sections

    Never raises — a save failure is logged but won't break the response.
    """
    try:
        img_hash = get_image_hash(image_bytes)
        ts = datetime.now()
        record_id = f"{ts.strftime('%Y%m%d_%H%M%S_%f')}_{img_hash[:8]}"
        ext = Path(filename or "").suffix.lower() or ".img"

        img_path = STORAGE_DIR / f"{record_id}{ext}"
        img_path.write_bytes(image_bytes)

        record = {
            "record_id": record_id,
            "received_at": ts.isoformat(timespec="seconds"),
            "status": status,
            "model_used": model_id,
            "input": {
                "filename": filename,
                "image_file": img_path.name,
                "image_bytes": len(image_bytes),
                "image_md5": img_hash,
                "hand": hand,
            },
            "output": {
                "palm_reading": palm_reading,
                "summary": summary,
                "weekly_predictions": predictions,
            },
        }
        json_path = STORAGE_DIR / f"{record_id}.json"
        json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2),
                             encoding="utf-8")
        logger.info("💾 Saved request | id=%s status=%s image=%s json=%s",
                    record_id, status, img_path.name, json_path.name)
        return record_id
    except Exception as e:
        logger.exception("Failed to save request record: %s", e)
        return None
