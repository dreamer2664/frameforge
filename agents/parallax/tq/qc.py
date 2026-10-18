#!/usr/bin/env python3
"""Mux + measure the reel, and build the review sheets.

  python3 qc.py --film work/render/film-silent.mp4 --score work/audio/score.wav \
      --out work/qc --master work/render/film-master.mp4 --sheets work/review

Measures the delivered file (not the renderer's internals): container, codecs,
frame count, duration, faststart, EBU R128 loudness, true peak, a luma timeline
and a per-frame-change profile; then writes labelled contact sheets for the
exact-file review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")
FFPROBE = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffprobe")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    out = run([FFPROBE, "-v", "error", "-print_format", "json", "-show_format",
               "-show_streams", str(path)])
    return json.loads(out.stdout)


def loudness(path):
    out = run([FFMPEG, "-hide_banner", "-nostats", "-i", str(path),
               "-filter_complex", "ebur128=peak=true", "-f", "null", "-"]).stderr.splitlines()
    k = max((i for i, l in enumerate(out) if l.strip() == "Summary:"), default=0)
    lufs = tp = None
    for line in out[k:]:
        parts = line.split()
        for i, tok in enumerate(parts):
            if tok in ("I:", "Peak:") and i + 1 < len(parts):
                try:
                    val = float(parts[i + 1])
                except ValueError:
                    continue
                if tok == "I:":
                    lufs = val
                else:
                    tp = val
    return lufs, tp


def faststart(path):
    with open(path, "rb") as fh:
        head = fh.read(64 * 1024)
    moov = head.find(b"moov")
    mdat = head.find(b"mdat")
    return bool(moov != -1 and (mdat == -1 or moov < mdat))


def mux(silent, score, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(silent), "-i", str(score),
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-shortest", "-movflags", "+faststart", str(out)]
    r = run(cmd)
    if r.returncode != 0:
        raise SystemExit("mux failed: " + r.stderr[-800:])
    return out


def frames_luma(path, width=320):
    """Mean luma per frame (decoded, not from the encoder's claims)."""
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-i", str(path),
           "-vf", f"scale={width}:-2", "-pix_fmt", "gray", "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    height = int(round(width * 1080 / 1920 / 2) * 2)
    a = np.frombuffer(raw, np.uint8).reshape(-1, height, width)
    return a.astype(np.float32).mean(axis=(1, 2))


def extract(path, times, outdir, width=960):
    outdir.mkdir(parents=True, exist_ok=True)
    made = []
    for t in times:
        dst = outdir / (f"t{t:06.2f}".replace(".", "_") + ".png")
        r = run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}",
                 "-i", str(path), "-frames:v", "1", "-vf", f"scale={width}:-2", str(dst)])
        if r.returncode == 0 and dst.exists():
            made.append(str(dst))
    return made


def sheet(images, out, cols=4, cell_w=460, label_h=26, title=""):
    if not images:
        return None
    ims = []
    for p in images:
        im = Image.open(p).convert("RGB")
        h = int(im.height * cell_w / im.width)
        ims.append((p, im.resize((cell_w, h), Image.LANCZOS)))
    rows = (len(ims) + cols - 1) // cols
    cell_h = max(i.height for _, i in ims) + label_h
    W = cols * cell_w
    H = rows * cell_h + (34 if title else 0)
    sheet_img = Image.new("RGB", (W, H), (18, 18, 18))
    d = ImageDraw.Draw(sheet_img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 16)
        big = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
        big = font
    if title:
        d.text((10, 6), title, fill=(240, 240, 235), font=big)
    for i, (p, im) in enumerate(ims):
        cx = (i % cols) * cell_w
        cy = (i // cols) * cell_h + (34 if title else 0)
        sheet_img.paste(im, (cx, cy))
        name = Path(p).stem
        d.text((cx + 6, cy + im.height + 4), name.replace("t", "t=").replace("_", "."),
               fill=(220, 220, 210), font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet_img.save(out)
    return str(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--film", required=True)
    ap.add_argument("--score", default=None)
    ap.add_argument("--master", default=None)
    ap.add_argument("--out", default="work/qc")
    ap.add_argument("--sheets", default="work/review")
    ap.add_argument("--no-sheets", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    film = Path(args.film)
    master = film
    if args.score and args.master:
        master = mux(film, Path(args.score), Path(args.master))

    p = probe(master)
    v = next((s for s in p["streams"] if s.get("codec_type") == "video"), None)
    a = next((s for s in p["streams"] if s.get("codec_type") == "audio"), None)
    lufs, tp = loudness(master)
    n, d = v["r_frame_rate"].split("/")
    report = {
        "master": str(master),
        "bytes": int(p["format"]["size"]),
        "sha256": hashlib.sha256(master.read_bytes()).hexdigest(),
        "duration_s": round(float(p["format"]["duration"]), 3),
        "video_codec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
        "profile": v.get("profile"), "width": v.get("width"), "height": v.get("height"),
        "fps": float(n) / float(d), "nb_frames": v.get("nb_frames"),
        "audio_codec": a.get("codec_name") if a else None,
        "audio_rate": int(a["sample_rate"]) if a else None,
        "audio_channels": a.get("channels") if a else None,
        "integrated_lufs": lufs, "true_peak_dbtp": tp,
        "faststart": faststart(master),
        "av_tail_mismatch_s": round(abs(float(v.get("duration", 0)) - float(a.get("duration", 0))), 3) if a and v else None,
    }
    luma = frames_luma(master)
    report["frames_decoded"] = int(luma.size)
    report["luma_first"] = round(float(luma[:5].mean()), 2)
    report["luma_last"] = round(float(luma[-5:].mean()), 2)
    report["luma_max"] = round(float(luma.max()), 2)
    report["luma_min"] = round(float(luma.min()), 2)
    # the picture must actually change
    d1 = np.abs(np.diff(luma))
    report["luma_change_mean"] = round(float(d1.mean()), 3)
    report["static_frames_over_0.5s"] = int((d1 < 0.5).sum())
    # sample the luma every 0.5 s for the timeline
    step = max(1, int(round(0.5 * report["fps"])))
    tl = [{"t": round(i / report["fps"], 2), "luma": round(float(luma[i]), 1)}
          for i in range(0, luma.size, step)]
    (out / "technical.json").write_text(json.dumps({"report": report, "luma_timeline": tl}, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if not args.no_sheets:
        sd = Path(args.sheets)
        dur = report["duration_s"]
        times = [round(0.25 * i, 2) for i in range(int(dur * 4) + 1)]
        imgs = extract(master, times, sd / "frames")
        sheet(imgs, sd / "grid_4fps.png", cols=4, cell_w=460,
              title=f"cadence - every 0.25 s - {report['width']}x{report['height']} @ {report['fps']:.0f}fps")
        key = [0.2, 1.3, 2.4, 2.9, 3.9, 4.6, 5.6, 6.4, 7.45, 8.2, 9.0, 9.8,
               10.3, 10.9, 11.4, 12.0, 12.5, 13.4, 14.0, 14.8]
        imgs2 = extract(master, key, sd / "key")
        sheet(imgs2, sd / "key_frames.png", cols=4, cell_w=460,
              title="cadence - key frames")
        print("sheets:", sd / "grid_4fps.png", sd / "key_frames.png")


if __name__ == "__main__":
    main()
