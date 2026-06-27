"""Backwards-compatible entrypoint. The real code lives in the palm_api/ package.

Run either of:
    python palm_astrology_api.py
    python -m palm_api.main
"""
from palm_api.main import main

if __name__ == "__main__":
    main()
