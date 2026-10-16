#!/usr/bin/env python3
"""axiom narration builder — one local Kokoro process, cached per cue, real durations.

Why not ops/tts.py per cue: that re-loads the ONNX model for every sentence (~170x).
This helper loads it once, caches each cue WAV by sha1(text|voice|speed|lang), trims
leading/trailing silence, and writes work/narration/manifest.json with MEASURED
durations. Noninteractive by design: the voice is chosen by the producer, never polled.

Usage:
  python3 tools/narrate.py --voice am_michael --speed 0.98            # all cues
  python3 tools/narrate.py --voice af_heart --only 1.1,1.2            # subset
  python3 tools/narrate.py --voice bm_george --sample                 # 5-cue voice sample
"""
from __future__ import annotations

import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(os.environ.get("FRAMEFORGE_CACHE", Path.home() / ".cache/frameforge"))
VENV_PY = CACHE / "voice-venv" / "bin" / "python"
MODELS = CACHE / "voice-models"

sys.path.insert(0, str(ROOT / "film"))
from script import all_cues  # noqa: E402

SAMPLE_IDS = ["1.1", "5.3", "7.4", "9.8", "10.10"]


def synth(voice: str, speed: float, lang: str, jobs: list[dict]):
    """Run inside the kokoro venv: synthesize every job that is not already cached."""
    payload = json.dumps(jobs)
    code = f'''
import json, sys
from pathlib import Path
import soundfile as sf
import numpy as np
from kokoro_onnx import Kokoro

payload = json.loads({payload!r})
voice, speed, lang = {voice!r}, {speed!r}, {lang!r}
k = Kokoro(str(Path({str(MODELS/'kokoro-v1.0.onnx')!r})), str(Path({str(MODELS/'voices-v1.0.bin')!r})))
out = []
for job in payload:
    dest = Path(job["out"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        out.append({{"id": job["id"], "status": "cached"}}); continue
    samples, sr = k.create(job["text"], voice=voice, speed=speed, lang=lang)
    a = np.asarray(samples, dtype="float32")
    peak = float(np.max(np.abs(a))) or 1.0
    # trim leading/trailing near-silence (below -55 dB of the peak), keep 40 ms pad
    thr = peak * 0.0018
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx):
        pad = int(0.04 * sr)
        a = a[max(0, idx[0]-pad): min(len(a), idx[-1]+pad)]
    sf.write(str(dest), a, sr)
    out.append({{"id": job["id"], "status": "made", "samples": int(len(a)), "sr": int(sr)}})
print(json.dumps(out))
'''
    if not VENV_PY.exists():
        sys.exit(f"missing kokoro venv at {VENV_PY} — run agents/axiom/tools/bootstrap_env.sh first")
    env = {k: v for k, v in os.environ.items() if k not in ("CHATCODE_TOKEN", "GITHUB_TOKEN", "GH_TOKEN")}
    proc = subprocess.run([str(VENV_PY), "-c", code], capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        print(proc.stdout[-2000:]); print(proc.stderr[-4000:]); sys.exit("kokoro synthesis failed")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="am_michael")
    ap.add_argument("--speed", type=float, default=0.98)
    ap.add_argument("--lang", default="en-us")
    ap.add_argument("--only", default=None)
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()

    outdir = Path(a.outdir) if a.outdir else ROOT / "work" / "narration" / a.voice
    cues = [(cid, text) for _ch, cid, text in all_cues()]
    if a.sample:
        cues = [c for c in cues if c[0] in SAMPLE_IDS]
    if a.only:
        keep = {s.strip() for s in a.only.split(",")}
        cues = [c for c in cues if c[0] in keep]

    jobs, meta = [], {}
    for cid, text in cues:
        h = hashlib.sha1(f"{text}|{a.voice}|{a.speed}|{a.lang}".encode()).hexdigest()[:12]
        fname = f"{cid.replace('.', '_')}-{h}.wav"
        jobs.append({"id": cid, "text": text, "out": str(outdir / fname)})
        meta[cid] = {"text": text, "file": str(outdir / fname), "hash": h}

    for j in jobs:
        Path(j["out"]).parent.mkdir(parents=True, exist_ok=True)
    results = synth(a.voice, a.speed, a.lang, jobs)
    made = sum(1 for r in results if r["status"] == "made")
    print(f"kokoro: {made} synthesized, {len(results)-made} cached of {len(results)} cues")

    # measure real durations in the main interpreter (soundfile is in the venv; use wave module)
    import wave
    total = 0.0
    for cid, m in meta.items():
        with wave.open(m["file"], "rb") as w:
            dur = w.getnframes() / w.getframerate()
            m["duration"] = round(dur, 4)
            m["sample_rate"] = w.getframerate()
            m["bytes"] = Path(m["file"]).stat().st_size
        total += dur
    man = {
        "voice": a.voice, "speed": a.speed, "lang": a.lang,
        "engine": "kokoro-onnx 0.6.1 (Kokoro-82M, Apache-2.0)",
        "synthetic": True, "cue_count": len(meta),
        "total_speech_seconds": round(total, 2),
        "words": sum(len(m["text"].split()) for m in meta.values()),
        "cues": meta,
    }
    out = outdir / "manifest.json"
    if a.sample:
        out = outdir / "sample-manifest.json"
    out.write_text(json.dumps(man, indent=2) + "\n")
    print(json.dumps({k: man[k] for k in ("voice", "cue_count", "total_speech_seconds", "words")}, indent=2))
    print("manifest:", out)


if __name__ == "__main__":
    main()
