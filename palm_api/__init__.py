"""Todozee Premium — Palm Astrology API package.

Module map (read in this order):
  config.py        — env vars, paths, logger
  utils.py         — small standalone helpers
  gemma_model.py   — LocalGemma model wrapper (load + generate)
  prompts.py       — text prompt templates (analysis, summary, daily x7)
  fallback_data.py — canned palmistry phrases used when the LLM isn't ready
  predictor.py     — PalmAstrologyPredictor (analyze, summary, predictions)
  storage.py       — save_request_record (persists every request to disk)
  app.py           — FastAPI app, response models, routes, middleware
  main.py          — entrypoint: prints banner, starts uvicorn
"""
