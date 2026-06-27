"""High-level palm-analysis + prediction logic.

The predictor uses LocalGemma for any LLM call, but degrades gracefully to
canned fallbacks from `fallback_data` when the model isn't ready.
"""
from __future__ import annotations

import logging
import random
import time
from datetime import datetime, timedelta
from typing import List, Optional

from .config import MAX_NEW_TOKENS
from .fallback_data import (
    DAILY_FALLBACK_MESSAGES,
    DAY_NAMES,
    DEFAULT_SUMMARY,
    FATE_LINE_READINGS,
    FINGER_READINGS,
    GUIDANCE_PARAGRAPHS,
    HAND_SHAPE_READINGS,
    HEAD_LINE_READINGS,
    HEART_LINE_READINGS,
    LIFE_LINE_READINGS,
    MOUNT_READINGS,
    SPECIAL_MARKINGS,
)
from .gemma_model import LocalGemma
from .prompts import DAILY_PROMPTS, PALM_ANALYSIS_PROMPT, SUMMARY_PROMPT
from .utils import get_image_hash


class PalmAstrologyPredictor:
    """Orchestrates palm analysis, summary, and 7-day predictions."""

    def __init__(self, gemma: LocalGemma):
        self.gemma = gemma
        self._log = logging.getLogger("predictor")

    # ── palm image analysis ──────────────────────────────────────────────
    def analyze_palm_image_bytes(self, image_bytes: bytes,
                                 hand: str = "right") -> str:
        img_hash = get_image_hash(image_bytes)
        self._log.info("Analyzing palm image | bytes=%d hash=%s hand=%s",
                       len(image_bytes), img_hash[:12], hand)

        if not self.gemma.ready:
            self._log.warning("Model not ready — using dynamic fallback reading")
            return self.get_dynamic_fallback_palm_reading(image_bytes)

        prompt = PALM_ANALYSIS_PROMPT.format(
            analysis_id=img_hash[:12],
            hand_upper=hand.upper(),
        )

        try:
            text = self.gemma.generate_with_image(prompt, image_bytes,
                                                  max_new_tokens=MAX_NEW_TOKENS)
            if not text.strip():
                raise RuntimeError("Empty generation")
            self._log.info("Palm reading generated | chars=%d", len(text))
            return text
        except Exception as e:
            self._log.exception("Gemma palm analysis failed: %s", e)
            self._log.warning("Falling back to dynamic reading.")
            return self.get_dynamic_fallback_palm_reading(image_bytes)

    # ── plain-language summary ───────────────────────────────────────────
    def generate_summary(self, palm_reading: str) -> str:
        """Short layperson summary mentioning the four main palm lines."""
        if not self.gemma.ready:
            return DEFAULT_SUMMARY

        prompt = SUMMARY_PROMPT.format(palm_reading=palm_reading)
        try:
            text = self.gemma.generate_text(prompt, max_new_tokens=180).strip()
            self._log.info("Summary generated | chars=%d", len(text))
            return text
        except Exception as e:
            self._log.exception("Summary generation failed: %s", e)
            return DEFAULT_SUMMARY

    # ── daily + weekly predictions ───────────────────────────────────────
    def generate_daily_prediction(self, palm_reading: str,
                                  day_of_week: int) -> str:
        if not self.gemma.ready:
            return self.get_fallback_daily_prediction(day_of_week)

        prompt = DAILY_PROMPTS[day_of_week].format(palm_reading=palm_reading)
        self._log.info("Generating prediction for %s", DAY_NAMES[day_of_week])
        try:
            text = self.gemma.generate_text(prompt, max_new_tokens=250)
            return text.strip() or self.get_fallback_daily_prediction(day_of_week)
        except Exception as e:
            self._log.exception("Daily prediction failed for %s: %s",
                                DAY_NAMES[day_of_week], e)
            return self.get_fallback_daily_prediction(day_of_week)

    def get_fallback_daily_prediction(self, day_of_week: int) -> str:
        return DAILY_FALLBACK_MESSAGES.get(day_of_week, DAILY_FALLBACK_MESSAGES[0])

    def generate_weekly_predictions(self, palm_reading: str,
                                    start_date: Optional[datetime] = None
                                    ) -> List[dict]:
        if start_date is None:
            start_date = datetime.now()
        self._log.info("Building 7-day predictions from %s",
                       start_date.strftime("%Y-%m-%d"))
        t0 = time.time()

        predictions = []
        for day_offset in range(7):
            target_date = start_date + timedelta(days=day_offset)
            dow = target_date.weekday()
            prediction = self.generate_daily_prediction(palm_reading, dow)
            predictions.append({
                "date": target_date.strftime("%Y-%m-%d"),
                "day_name": DAY_NAMES[dow],
                "day_of_week": dow,
                "prediction": prediction,
            })
        self._log.info("Weekly predictions built in %.1fs", time.time() - t0)
        return predictions

    # ── dynamic fallback (LLM unavailable) ───────────────────────────────
    def get_dynamic_fallback_palm_reading(self, image_bytes: bytes) -> str:
        """Same image → same canned reading (seeded by image MD5)."""
        img_hash = get_image_hash(image_bytes)
        seed = int(img_hash, 16)
        rng = random.Random(seed)

        heart = rng.choice(HEART_LINE_READINGS)
        head  = rng.choice(HEAD_LINE_READINGS)
        life  = rng.choice(LIFE_LINE_READINGS)
        fate  = rng.choice(FATE_LINE_READINGS)
        hand_element, hand_desc = rng.choice(HAND_SHAPE_READINGS)
        finger_obs = rng.sample(FINGER_READINGS, 2)
        chosen_mounts = rng.sample(MOUNT_READINGS, 3)
        mount_texts = [f"  • {name}: {rng.choice([dev, flat])}"
                       for name, dev, flat in chosen_mounts]
        marking = rng.choice(SPECIAL_MARKINGS)
        guidance = rng.choice(GUIDANCE_PARAGRAPHS)

        self._log.info("Generated fallback reading | seed=%s element=%s",
                       img_hash[:8], hand_element)

        return f"""Palm Analysis — Personalized Reading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Major Lines:

  Heart Line:
  {heart}

  Head Line:
  {head}

  Life Line:
  {life}

  Fate Line:
  {fate}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hand Characteristics:

  Shape ({hand_element} hand):
  {hand_desc}

  Fingers:
  • {finger_obs[0]}
  • {finger_obs[1]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mounts:

{chr(10).join(mount_texts)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Special Markings:

  {marking}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Guidance:

  {guidance}"""
