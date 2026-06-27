"""Environment-driven config + log directories + the package logger.

Importing this module sets up logging (basicConfig) as a side effect, so
every other module can just `from .config import logger`.
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# ── runtime knobs ────────────────────────────────────────────────────────
MODEL_ID       = os.getenv("MODEL_ID", "google/gemma-4-E2B-it")
API_PORT       = int(os.getenv("API_PORT", "7003"))
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "900"))
HF_TOKEN       = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")

# ── persistent locations ─────────────────────────────────────────────────
LOG_DIR     = Path(os.getenv("LOG_DIR", "./logs"))
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "./request_logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / f"palm_api_{datetime.now().strftime('%Y%m%d')}.log"

# ── logging ──────────────────────────────────────────────────────────────
_log_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=_log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
# Quiet down noisy dependencies
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)

logger = logging.getLogger("palm_api")
logger.info("=" * 80)
logger.info("Logger initialized. Writing to: %s", LOG_FILE.resolve())
logger.info("=" * 80)
logger.info("Config | MODEL_ID=%s  PORT=%d  MAX_NEW_TOKENS=%d  HF_TOKEN=%s",
            MODEL_ID, API_PORT, MAX_NEW_TOKENS, "set" if HF_TOKEN else "not set")
