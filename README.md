# Todozee Premium — Palm Astrology API

A FastAPI service that takes a palm photo + which hand it is, runs it through
**Google Gemma 4 E2B** (a local multimodal LLM), and returns a short plain-language
summary plus 7 day-themed daily messages. Every request (input image + output JSON)
is persisted to disk so you can replay or audit any reading later.

> **Honest disclaimer.** This is **not** real palmistry. There is no computer vision
> for palm lines, no astrology engine, no ephemeris. A general-purpose multimodal
> LLM is prompted to *act* like a palmistry expert. Treat the output as entertainment,
> not measurement.

---

## Features

- **Single endpoint that does it all** — `POST /palm/read` takes an image + a `hand`
  ("left" / "right") and returns a structured summary + 7-day predictions.
- **Plain-language summary** — separate LLM call that produces a 50-70 word summary
  mentioning the four main lines (heart, head, life, fate) in everyday English.
- **No-palm detection** — if the vision model decides the image isn't a clear palm,
  the endpoint short-circuits with a concise `400` instead of generating 7 wasted essays.
- **Persistent request log** — every request writes the original image **and** a JSON
  record (input metadata + output) under `request_logs/`, keyed by timestamp + image
  MD5. Browse them via `GET /logs` / `GET /logs/{record_id}`.
- **Degrades gracefully** — if the model can't load, a deterministic image-hash-seeded
  fallback reading is used so requests never fail outright.
- **Health-checkable** — `GET /` and `GET /health` report model readiness + device.

---

## Quick start

```bash
# 1) Clone
git clone https://github.com/kvsabhiram/Todozee_Palm-Reader.git
cd Todozee_Palm-Reader

# 2) Create a venv (the one in this repo's .gitignore is named ./palm_astro/)
python3.12 -m venv palm_astro
source palm_astro/bin/activate

# 3) Install runtime deps + torch (pick the variant that matches your hardware)
pip install -r requirements.txt
# GPU (CUDA 12.8, incl. RTX 50-series / Blackwell):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
# CPU-only (slow):
# pip install torch torchvision

# 4) Run
python palm_astrology_api.py
# or, equivalently:
python -m palm_api.main
```

First launch downloads ~10 GB of weights to `~/.cache/huggingface/`.
`google/gemma-4-E2B-it` is **Apache-2.0** — **no HF token / gating required**.

Once you see `🚀 API ready on port 7003 | device=cuda`, the API is live.
Swagger docs: <http://localhost:7003/docs>

---

## Configuration

All knobs come from environment variables — see [`palm_api/config.py`](palm_api/config.py).

| Variable          | Default                  | Description                                            |
|-------------------|--------------------------|--------------------------------------------------------|
| `MODEL_ID`        | `google/gemma-4-E2B-it`  | Any HF multimodal `AutoModelForImageTextToText` model. |
| `API_PORT`        | `7003`                   | Port uvicorn binds to.                                 |
| `MAX_NEW_TOKENS`  | `900`                    | Cap for the palm-analysis generation.                  |
| `HF_TOKEN`        | unset                    | Only needed for gated models; gemma-4-E2B is not gated.|
| `LOG_DIR`         | `./logs`                 | Daily app log files.                                   |
| `STORAGE_DIR`     | `./request_logs`         | Per-request image + JSON records.                      |

---

## API

### `GET /health` (and `/`)
```json
{ "status": "ok", "model": "google/gemma-4-E2B-it",
  "model_ready": true, "device": "cuda" }
```

### `POST /palm/read`
**Form fields:**
- `file` — palm image (`.jpg` / `.jpeg` / `.png` / `.webp` / `.gif`)
- `hand` — `"left"` or `"right"` (required)

**Example:**
```bash
curl -F file=@palm.jpg -F hand=right http://localhost:7003/palm/read
```

**Response (200):**
```json
{
  "generated_at": "2026-06-12T11:14:22",
  "model_used": "google/gemma-4-E2B-it",
  "hand": "right",
  "summary": "The heart line shows ... The head line ... life line ... fate line ...",
  "weekly_predictions": [
    { "date": "2026-06-12", "day_name": "Friday", "day_of_week": 4,
      "prediction": "Embrace Connection. …" },
    /* …six more days… */
  ]
}
```

**Error responses:**
- `400 {"detail": "Field 'hand' must be 'left' or 'right'."}`
- `400 {"detail": "Unsupported file format '.bmp'. Use: .gif, .jpeg, .jpg, .png, .webp"}`
- `400 {"detail": "No palm detected. Please upload a clear photo of a palm."}`
- `500 {"detail": "Internal server error"}`

### `GET /logs?limit=50`
Newest-first list of saved request records:
```json
[
  { "record_id": "20260612_111422_…_36ff0e8b",
    "received_at": "2026-06-12T11:14:22",
    "status": "ok",
    "model_used": "google/gemma-4-E2B-it",
    "hand": "right",
    "summary_preview": "The heart line shows …" },
  …
]
```

### `GET /logs/{record_id}`
Full saved record — same shape as the file on disk: `input` (filename, image file,
byte size, md5, hand) + `output` (palm_reading, summary, weekly_predictions).

---

## Pipeline (what happens on every request)

```
            ┌──────────────────────────────────────────────┐
POST  ────► │ 1. validate ext + hand                       │
            │ 2. analyze_palm_image_bytes(image, hand)     │  ← multimodal LLM call
            │ 3. no_palm_detected(reading)? → 400 short    │
            │ 4. generate_summary(reading)                 │  ← text LLM call
            │ 5. generate_weekly_predictions(reading)      │  ← 7 text LLM calls
            │ 6. save_request_record(image + JSON)         │  ← writes to request_logs/
            │ 7. return PalmReadingResponse                │
            └──────────────────────────────────────────────┘
```

Per request: 1 image-conditioned generation + 1 summary + 7 daily ≈ **~30 s on
a single RTX 5090** (sequential daily generations dominate).

---

## Project layout

The runtime lives in the [`palm_api/`](palm_api/) package; the top-level
[`palm_astrology_api.py`](palm_astrology_api.py) is a backwards-compat shim.

```
palm_astro/
├── palm_astrology_api.py          # 5-line shim → palm_api.main:main()
├── requirements.txt
├── README.md
├── .gitignore
└── palm_api/                      # the real code
    ├── __init__.py
    ├── config.py                  # env vars, log/storage dirs, logger setup
    ├── utils.py                   # get_image_hash, no_palm_detected
    ├── gemma_model.py             # LocalGemma wrapper + dep flags + device picker
    ├── prompts.py                 # palm-analysis + summary + 7 daily prompts
    ├── fallback_data.py           # canned palmistry phrases (used if LLM unavailable)
    ├── predictor.py               # PalmAstrologyPredictor (analyze/summary/weekly)
    ├── storage.py                 # save_request_record (image + JSON per request)
    ├── app.py                     # FastAPI app, response models, routes, middleware
    └── main.py                    # uvicorn entrypoint (banner + run)
```

Runtime-only (gitignored, created automatically):
- `logs/palm_api_YYYYMMDD.log` — per-day rolling app log.
- `request_logs/{timestamp}_{md5[:8]}.{json,jpg}` — every request's input + output.
- `palm_astro/` — virtual environment.

---

## Hardware notes

Tested on an NVIDIA RTX 5090 (32 GB, Blackwell / sm_120) with **torch 2.11.0+cu128**.
Blackwell GPUs require the cu128 build of torch — anything older will fail to use
the GPU. The Gemma-4 processor pulls in a video processor, which is why
`torchvision` is a hard runtime requirement (not just an extra).

Approximate GPU footprint with the default model: **~9 GB** in bf16.

---

## License

The application code is released under the MIT License.
The underlying model `google/gemma-4-E2B-it` is licensed Apache 2.0 by Google.
