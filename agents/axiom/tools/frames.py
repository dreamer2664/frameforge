#!/usr/bin/env python3
"""axiom frame extractor / contact-sheet builder.

Robust against end-of-file seeks (the shared helper's tail sample can miss).
Usage:
  python3 frames.py VIDEO --out DIR --every 15
  python3 frames.py VIDEO --out DIR --times 0,3.5,7.25
  python3 frames.py VIDEO --out DIR --every 2 --cols 4 --tw 480
Writes: frame-<idx>-<sec>.jpg, sheet-<n>.jpg, manifest.json
"""
import argparse, json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw

FFMPEG = str(Path.home() / ".cache/frameforge/bin/ffmpeg")
FFPROBE = str(Path.home() / ".cache/frameforge/bin/ffprobe")


def probe(video: Path):
    out = subprocess.check_output(
        [FFPROBE, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video)]
    )
    meta = json.loads(out)
    dur = float(meta["format"]["duration"])
    v = next(s for s in meta["streams"] if s.get("codec_type") == "video")
    return dur, int(v["width"]), int(v["height"])


def grab(video: Path, sec: float, dest: Path, dur: float) -> bool:
    """Grab exactly one frame near `sec`; clamped inside the stream."""
    sec = max(0.0, min(sec, dur - 0.05))
    for attempt in (sec, max(0.0, sec - 0.5), max(0.0, sec - 1.5)):
        cmd = [FFMPEG, "-v", "error", "-ss", f"{attempt:.3f}", "-i", str(video),
               "-frames:v", "1", "-q:v", "3", "-y", str(dest)]
        try:
            subprocess.run(cmd, check=True, timeout=90, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            continue
        if dest.exists() and dest.stat().st_size > 0:
            return True
    return False


def build_sheets(frames, out: Path, cols: int, tw: int, th: int, labels):
    sheets = []
    per = cols * 6
    for n in range(0, len(frames), per):
        batch = frames[n:n + per]
        rows = math.ceil(len(batch) / cols)
        canvas = Image.new("RGB", (cols * tw, rows * (th + 26)), (18, 20, 26))
        d = ImageDraw.Draw(canvas)
        for i, (path, label) in enumerate(zip(batch, labels[n:n + per])):
            with Image.open(path) as im:
                im = im.convert("RGB")
                im.thumbnail((tw, th))
                x = (i % cols) * tw + (tw - im.width) // 2
                y = (i // cols) * (th + 26)
                canvas.paste(im, (x, y))
            d.text(((i % cols) * tw + 6, (i // cols) * (th + 26) + th + 6), label, fill=(235, 235, 240))
        sheet = out / f"sheet-{n // per:03d}.jpg"
        canvas.save(sheet, quality=88)
        sheets.append(str(sheet))
    return sheets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--every", type=float)
    ap.add_argument("--times", type=str)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--tw", type=int, default=440)
    a = ap.parse_args()

    video = Path(a.video).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    dur, w, h = probe(video)
    if a.times:
        times = sorted({float(t) for t in a.times.split(",") if t.strip()})
    elif a.every:
        times = [round(i * a.every, 3) for i in range(int(dur // a.every) + 1)]
        if times[-1] < dur - 0.2:
            times.append(round(dur - 0.1, 3))
        else:
            times[-1] = round(dur - 0.1, 3)
    else:
        raise SystemExit("need --every or --times")

    th = int(a.tw * h / w)
    frames, labels, failed = [], [], []
    for i, sec in enumerate(times):
        p = out / f"frame-{i:05d}-{sec:07.3f}s.jpg"
        if not p.exists() and not grab(video, sec, p, dur):
            failed.append(sec)
            continue
        frames.append(p)
        labels.append(f"{sec:.3f}s")
    sheets = build_sheets(frames, out, a.cols, a.tw, th, labels)
    manifest = {
        "video": str(video), "duration_s": dur, "geometry": [w, h],
        "sampled_at_seconds": times, "frames_written": len(frames), "failed_seconds": failed,
        "sheets": sheets,
        "review_status": "NOT REVIEWED merely because these images were generated. Open every sheet; record observations.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: manifest[k] for k in ("duration_s", "geometry", "frames_written", "failed_seconds", "sheets")}, indent=2))


if __name__ == "__main__":
    sys.exit(main())
