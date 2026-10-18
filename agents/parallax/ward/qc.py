#!/usr/bin/env python3
"""Mux + measure 'LAST SHIFT - WARD 7', and build the review sheets.

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
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")
FFPROBE = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffprobe")
TITLE = "last shift - ward 7"


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


def frames_luma(path, width=240, src_h=1920, src_w=1080):
    """Mean luma per frame (decoded, not from the encoder's claims).

    The raw stream is consumed in bounded chunks: a portrait 70 s film is
    ~380 MB of gray at 320 px and this box has 1.9 GB of RAM.
    """
    height = int(round(width * src_h / src_w / 2) * 2)
    frame_bytes = height * width
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-i", str(path),
           "-vf", f"scale={width}:-2", "-pix_fmt", "gray", "-f", "rawvideo", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    means = []
    buf = b""
    try:
        while True:
            chunk = proc.stdout.read(frame_bytes * 8)
            if not chunk:
                break
            buf += chunk
            n = len(buf) // frame_bytes
            if n:
                a = np.frombuffer(buf[: n * frame_bytes], np.uint8).reshape(n, height, width)
                means.append(a.astype(np.float32).mean(axis=(1, 2)))
                buf = buf[n * frame_bytes:]
    finally:
        proc.stdout.close()
        proc.wait()
    if not means:
        return np.zeros(0, np.float32)
    return np.concatenate(means)


def extract(path, times, outdir, width=540):
    outdir.mkdir(parents=True, exist_ok=True)
    made = []
    for t in times:
        dst = outdir / (f"t{t:06.2f}".replace(".", "_") + ".png")
        r = run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}",
                 "-i", str(path), "-frames:v", "1", "-vf", f"scale={width}:-2", str(dst)])
        if r.returncode == 0 and dst.exists():
            made.append(str(dst))
    return made


def sheet(images, out, cols=6, cell_w=300, label_h=24, title=""):
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
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 15)
        big = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 22)
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
        d.text((cx + 6, cy + im.height + 3), name.replace("t", "t=").replace("_", "."),
               fill=(220, 220, 210), font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet_img.save(out)
    return str(out)


KEY = [0.6, 1.6, 2.4, 3.6, 4.6, 6.2, 7.6, 9.4, 10.6, 11.6,
       13.4, 14.6, 15.8, 17.2, 19.6, 21.4, 22.8, 23.8, 25.2, 26.4,
       28.0, 30.0, 31.4, 33.0, 35.4, 36.6, 38.6, 40.4, 42.8, 44.2,
       46.4, 48.8, 50.2, 52.4, 53.8, 55.4, 56.4, 58.6, 60.2, 62.0,
       63.4, 65.4, 67.0, 68.8]


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
    luma = frames_luma(master, src_h=int(v["height"]), src_w=int(v["width"]))
    report["frames_decoded"] = int(luma.size)
    report["luma_first"] = round(float(luma[:5].mean()), 2)
    report["luma_last"] = round(float(luma[-5:].mean()), 2)
    report["luma_max"] = round(float(luma.max()), 2)
    report["luma_min"] = round(float(luma.min()), 2)
    d1 = np.abs(np.diff(luma))
    report["luma_change_mean"] = round(float(d1.mean()), 3)
    report["static_frames_over_0.5s"] = int((d1 < 0.5).sum())
    step = max(1, int(round(0.5 * report["fps"])))
    tl = [{"t": round(i / report["fps"], 2), "luma": round(float(luma[i]), 1)}
          for i in range(0, luma.size, step)]
    (out / "technical.json").write_text(json.dumps({"report": report, "luma_timeline": tl}, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if not args.no_sheets:
        sd = Path(args.sheets)
        dur = report["duration_s"]
        times = [round(0.5 * i, 2) for i in range(int(dur * 2) + 1)]
        imgs = extract(master, times, sd / "frames")
        sheet(imgs, sd / "grid_2fps.png", cols=8, cell_w=260,
              title=f"{TITLE} - every 0.5 s - {report['width']}x{report['height']} @ {report['fps']:.0f}fps")
        imgs2 = extract(master, KEY, sd / "key")
        sheet(imgs2, sd / "key_frames.png", cols=6, cell_w=300, title=f"{TITLE} - key frames")
        print("sheets:", sd / "grid_2fps.png", sd / "key_frames.png")


if __name__ == "__main__":
    main()
