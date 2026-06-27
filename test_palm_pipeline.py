"""End-to-end pipeline test: 20 real palm images → /palm/read → report.

Steps:
  1. Download the public sample of ud-biometrics/open-palm-hand-images (~180 MB
     parquet, 50 rows) — cached locally so re-runs are fast.
  2. Filter to genuine palm rows (labels 1-5; skips Print_*/Replay_* spoof samples).
  3. POST 20 images to /palm/read with alternating hand=left/right.
  4. Print a results table + summary stats and save full results to JSON.

Usage:
  python test_palm_pipeline.py
"""
from __future__ import annotations

import io
import json
import sys
import time
from pathlib import Path

import pyarrow.parquet as pq
import requests

ROOT = Path("/home/ubuntu/palm_astro")
PARQUET_URL = ("https://huggingface.co/datasets/ud-biometrics/"
               "open-palm-hand-images/resolve/refs%2Fconvert%2Fparquet/"
               "default/train/0000.parquet")
PARQUET_LOCAL = ROOT / "test_palm.parquet"
IMG_DIR = ROOT / "test_palm_images"
RESULTS_FILE = ROOT / "test_results.json"
API = "http://localhost:7003/palm/read"
HEALTH = "http://localhost:7003/health"
N = 20

# From the HF schema for this dataset
LABEL_NAMES = ["1", "2", "3", "4", "5",
               "Print_1", "Print_2", "Print_3", "Print_4", "Print_5",
               "Replay_1", "Replay_2", "Replay_3", "Replay_4", "Replay_5"]
REAL_LABELS = {"1", "2", "3", "4", "5"}


def check_server():
    try:
        r = requests.get(HEALTH, timeout=5)
        info = r.json()
        if not info.get("model_ready"):
            sys.exit(f"Server not ready: {info}")
        print(f"Server OK | model={info['model']} device={info['device']}")
    except Exception as e:
        sys.exit(f"Server unreachable at {HEALTH}: {e}")


def download_parquet():
    if PARQUET_LOCAL.exists():
        print(f"Parquet cached ({PARQUET_LOCAL.stat().st_size / 1e6:.1f} MB)")
        return
    print(f"Downloading parquet → {PARQUET_LOCAL.name} …")
    with requests.get(PARQUET_URL, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(PARQUET_LOCAL, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
    print(f"Downloaded {PARQUET_LOCAL.stat().st_size / 1e6:.1f} MB")


def extract_images():
    IMG_DIR.mkdir(exist_ok=True)
    table = pq.read_table(PARQUET_LOCAL)
    images_col = table.column("image").to_pylist()
    labels_col = table.column("label").to_pylist()
    saved = []
    for img, lbl in zip(images_col, labels_col):
        if not (0 <= lbl < len(LABEL_NAMES)):
            continue
        if LABEL_NAMES[lbl] not in REAL_LABELS:
            continue
        img_bytes = img["bytes"] if isinstance(img, dict) else img
        if not img_bytes:
            continue
        p = IMG_DIR / f"palm_{len(saved):02d}.jpg"
        p.write_bytes(img_bytes)
        saved.append(p)
        if len(saved) >= N:
            break
    print(f"Saved {len(saved)} palm images → {IMG_DIR}")
    return saved


def post_one(p: Path, hand: str) -> dict:
    t0 = time.time()
    try:
        with open(p, "rb") as f:
            r = requests.post(API,
                              files={"file": (p.name, f, "image/jpeg")},
                              data={"hand": hand},
                              timeout=600)
    except Exception as e:
        return {"image": p.name, "hand": hand, "error": str(e),
                "elapsed_s": round(time.time() - t0, 1)}
    elapsed = round(time.time() - t0, 1)
    body = r.json() if r.text else {}
    return {
        "image": p.name, "hand": hand, "status": r.status_code,
        "elapsed_s": elapsed,
        "summary_chars": len(body.get("summary", "")) if r.ok else 0,
        "n_predictions": len(body.get("weekly_predictions", [])) if r.ok else 0,
        "model_used": body.get("model_used"),
        "detail": body.get("detail", "") if not r.ok else "",
        "summary_preview": (body.get("summary", "")[:120] + "…")
            if r.ok and body.get("summary") else "",
    }


def main():
    check_server()
    download_parquet()
    images = extract_images()
    if not images:
        sys.exit("No images extracted.")

    print(f"\nTesting {len(images)} images against {API} …\n")
    print(f"{'#':>2}  {'image':<14} {'hand':<5}  {'http':>4}  "
          f"{'elapsed':>7}  {'summ':>5}  {'preds':>5}  notes")
    print("-" * 80)
    results = []
    for i, p in enumerate(images):
        hand = "left" if i % 2 == 0 else "right"
        res = post_one(p, hand)
        results.append(res)
        notes = res.get("detail") or res.get("error") or ""
        print(f"{i:>2}  {p.name:<14} {hand:<5}  "
              f"{res.get('status', '---')!s:>4}  "
              f"{res.get('elapsed_s', '?'):>5}s   "
              f"{res.get('summary_chars', 0):>5}  "
              f"{res.get('n_predictions', 0):>5}  {notes[:40]}")

    RESULTS_FILE.write_text(json.dumps(results, indent=2))

    # Summary
    n_ok       = sum(1 for r in results if r.get("status") == 200)
    n_no_palm  = sum(1 for r in results
                     if r.get("status") == 400 and "No palm" in (r.get("detail") or ""))
    n_bad_hand = sum(1 for r in results
                     if r.get("status") == 400 and "hand" in (r.get("detail") or "").lower())
    n_err      = sum(1 for r in results if "error" in r)
    n_other    = len(results) - n_ok - n_no_palm - n_bad_hand - n_err
    elapsed    = [r["elapsed_s"] for r in results if "elapsed_s" in r and r.get("status") == 200]
    avg_t      = sum(elapsed) / len(elapsed) if elapsed else 0
    summ_ok    = sum(1 for r in results
                     if r.get("status") == 200 and r.get("summary_chars", 0) > 30)
    preds_ok   = sum(1 for r in results
                     if r.get("status") == 200 and r.get("n_predictions", 0) == 7)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Tested:                       {len(results)}")
    print(f"  HTTP 200 (full reading):      {n_ok}")
    print(f"  HTTP 400 (no palm detected):  {n_no_palm}")
    print(f"  HTTP 400 (bad hand value):    {n_bad_hand}")
    print(f"  Transport errors:             {n_err}")
    print(f"  Other:                        {n_other}")
    print(f"  Avg latency (200s only):      {avg_t:.1f}s")
    print(f"  200s with summary > 30 chars: {summ_ok}/{n_ok}")
    print(f"  200s with 7-day predictions:  {preds_ok}/{n_ok}")
    print(f"  Results JSON:                 {RESULTS_FILE}")


if __name__ == "__main__":
    main()
