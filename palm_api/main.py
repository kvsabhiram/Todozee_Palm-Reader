"""Process entrypoint: prints the banner and starts uvicorn."""
from __future__ import annotations

# Allow running this file directly (`python palm_api/main.py`) by giving
# it a parent-package context so the relative imports below resolve.
if __name__ == "__main__" and __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "palm_api"  # noqa: A001

import uvicorn

from .config import API_PORT, LOG_FILE, logger


def main() -> None:
    logger.info("=" * 80)
    logger.info("🔮 TODOZEE PREMIUM — PALM ASTROLOGY API (Local Gemma)")
    logger.info("Listening on http://0.0.0.0:%d", API_PORT)
    logger.info("Docs:        http://localhost:%d/docs", API_PORT)
    logger.info("Log file:    %s", LOG_FILE.resolve())
    logger.info("=" * 80)

    uvicorn.run(
        "palm_api.app:app",
        host="0.0.0.0",
        port=API_PORT,
        reload=False,
        log_config=None,   # use our logging config
    )


if __name__ == "__main__":
    main()
