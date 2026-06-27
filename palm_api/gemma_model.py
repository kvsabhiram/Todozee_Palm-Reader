"""Local Gemma model wrapper + dependency-availability flags + device picker.

This is the only module that touches torch / transformers / PIL. Other
modules import `LocalGemma` from here and don't care which backend is used.
"""
from __future__ import annotations

import io
import logging
import threading
import time

from .config import HF_TOKEN, MAX_NEW_TOKENS, MODEL_ID, logger as _logger

# ── optional heavy imports ──────────────────────────────────────────────
try:
    from PIL import Image
    PIL_AVAILABLE = True
    _logger.info("✅ Pillow available")
except ImportError:
    PIL_AVAILABLE = False
    Image = None  # type: ignore[assignment]
    _logger.warning("⚠️  Pillow not installed. Run: pip install pillow")

try:
    import torch
    TORCH_AVAILABLE = True
    _logger.info("✅ torch %s available | CUDA: %s | MPS: %s",
                 torch.__version__,
                 torch.cuda.is_available(),
                 getattr(torch.backends, "mps", None)
                 and torch.backends.mps.is_available())
except ImportError:
    TORCH_AVAILABLE = False
    torch = None  # type: ignore[assignment]
    _logger.warning("⚠️  torch not installed. Run: pip install torch")

try:
    from transformers import AutoModelForImageTextToText, AutoProcessor
    TRANSFORMERS_AVAILABLE = True
    _logger.info("✅ transformers available")
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    AutoModelForImageTextToText = None  # type: ignore[assignment]
    AutoProcessor = None  # type: ignore[assignment]
    _logger.warning("⚠️  transformers not installed or too old: %s", e)
    _logger.warning("   Run: pip install -U transformers>=5.9.0")


def pick_device_and_dtype():
    """Pick best available device + dtype."""
    if not TORCH_AVAILABLE:
        return "cpu", None
    if torch.cuda.is_available():
        return "cuda", torch.bfloat16
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps", torch.float16
    return "cpu", torch.float32


class LocalGemma:
    """Thread-safe wrapper around a locally loaded Gemma model."""

    def __init__(self, model_id: str = MODEL_ID):
        self.model_id = model_id
        self.processor = None
        self.model = None
        self.device = "cpu"
        self.dtype = None
        self.ready = False
        self._lock = threading.Lock()      # serialize generate() calls
        self._log = logging.getLogger("gemma")

    def load(self) -> None:
        """Load the model weights into memory. Blocking — call once at startup."""
        if not (TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE and PIL_AVAILABLE):
            self._log.error("Cannot load model — missing dependencies "
                            "(transformers=%s torch=%s pillow=%s)",
                            TRANSFORMERS_AVAILABLE, TORCH_AVAILABLE, PIL_AVAILABLE)
            return

        self.device, self.dtype = pick_device_and_dtype()
        self._log.info("Loading model → device=%s dtype=%s model=%s",
                       self.device, self.dtype, self.model_id)

        t0 = time.time()
        try:
            kwargs = {}
            if HF_TOKEN:
                kwargs["token"] = HF_TOKEN

            self.processor = AutoProcessor.from_pretrained(self.model_id, **kwargs)
            self._log.info("Processor loaded in %.1fs", time.time() - t0)

            t1 = time.time()
            self.model = AutoModelForImageTextToText.from_pretrained(
                self.model_id,
                torch_dtype=self.dtype,
                device_map=self.device if self.device != "cpu" else None,
                low_cpu_mem_usage=True,
                **kwargs,
            )
            if self.device == "cpu":
                self.model = self.model.to("cpu")
            self.model.eval()
            self._log.info("Model loaded in %.1fs (total %.1fs)",
                           time.time() - t1, time.time() - t0)

            self.ready = True
            self._log.info("✅ Model is ready for inference.")

        except Exception as e:
            self._log.exception("❌ Failed to load model: %s", e)
            self.ready = False

    # ── core generation helpers ────────────────────────────────────────────
    def _generate(self, messages: list, max_new_tokens: int = MAX_NEW_TOKENS) -> str:
        """Run generation with a lock so concurrent requests don't collide on GPU."""
        if not self.ready:
            raise RuntimeError("Model not ready")

        with self._lock:
            t0 = time.time()
            inputs = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(self.model.device, dtype=self.dtype if self.dtype else None)

            input_len = inputs["input_ids"].shape[-1]
            self._log.info("Generating | input_tokens=%d max_new=%d",
                           input_len, max_new_tokens)

            with torch.inference_mode():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.85,
                    top_p=0.95,
                )

            new_tokens = output[0][input_len:]
            text = self.processor.decode(new_tokens, skip_special_tokens=True).strip()
            dt = time.time() - t0
            self._log.info("Generated | out_tokens=%d  elapsed=%.1fs  tok/s=%.1f",
                           len(new_tokens), dt,
                           len(new_tokens) / dt if dt > 0 else 0)
            return text

    def generate_with_image(self, prompt: str, image_bytes: bytes,
                            max_new_tokens: int = MAX_NEW_TOKENS) -> str:
        """Multimodal: text + image → text."""
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": pil_img},
                {"type": "text",  "text":  prompt},
            ],
        }]
        return self._generate(messages, max_new_tokens=max_new_tokens)

    def generate_text(self, prompt: str, max_new_tokens: int = 300) -> str:
        """Text-only generation."""
        messages = [{
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }]
        return self._generate(messages, max_new_tokens=max_new_tokens)
