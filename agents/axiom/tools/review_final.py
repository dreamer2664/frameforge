#!/usr/bin/env python3
"""Final-file visual check on the DELIVERED master.

Implements the commission's review gate rather than approximating it:
  * a frame every 5 s of the delivered file
  * the first and last visible frame of every shot (start / end)
  * contact sheets, a per-frame index and a coverage report with honest limits

  python3 tools/review_final.py --master final/axiom-r01-1080p.mp4 \
      --timeline work/timeline.json --out work/review/final5 \
      --report evidence/final-review-r01.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FFMPEG = str(Path.home() / ".cache/frameforge/bin/ffmpeg")
FFPROBE = str(Path.home() / ".cache/frameforge/bin/ffprobe")

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)


def probe(path: Path) -> dict:
    return json.loads(subprocess.check_output(
        [FFPROBE, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]))


def grab(master: Path, t: float, dest: Path, w: int) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{max(0.0, t):.3f}", "-i", str(master),
                        "-frames:v", "1", "-vf", f"scale={w}:-1", str(dest)],
                       capture_output=True, text=True)
    return r.returncode == 0 and dest.exists()


def grid_pass(master: Path, step: float, dur: float, outdir: Path, w: int) -> list[Path]:
    """One decode pass, one frame every `step` seconds (fast, exact timestamps known)."""
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(master),
                    "-vf", f"fps=1/{step},scale={w}:-1", "-q:v", "3",
                    str(outdir / "g-%04d.jpg")], check=True)
    files = sorted(outdir.glob("g-*.jpg"))
    return files


def sheet(files: list[Path], labels: list[str], out: Path, cols: int, tw: int, title: str) -> Path:
    if not files:
        return out
    ims = [Image.open(p).convert("RGB") for p in files]
    th = int(tw * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    band = 20
    sh = Image.new("RGB", (cols * tw, 30 + rows * (th + band)), (18, 18, 22))
    d = ImageDraw.Draw(sh)
    d.text((8, 7), title, font=FONT, fill=(236, 232, 220))
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x, y = (i % cols) * tw, 30 + (i // cols) * (th + band)
        sh.paste(im.resize((tw, th)), (x, y))
        d.text((x + 5, y + th + 2), lab, font=FONT, fill=(214, 210, 200))
    sh.save(out, quality=86)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--timeline", default=str(ROOT / "work/timeline.json"))
    ap.add_argument("--out", default=str(ROOT / "work/review/final5"))
    ap.add_argument("--report", default=str(ROOT / "evidence/final-review-r01.json"))
    ap.add_argument("--step", type=float, default=5.0)
    ap.add_argument("--tw", type=int, default=320)
    ap.add_argument("--cols", type=int, default=8)
    args = ap.parse_args()

    master = Path(args.master).resolve()
    tl = json.loads(Path(args.timeline).read_text())
    info = probe(master)
    dur = float(info["format"]["duration"])
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    # ---- pass A: the 5 s grid, from the delivered file
    grid = grid_pass(master, args.step, dur, outdir / "grid", args.tw)
    grid_ts = [round(i * args.step, 2) for i in range(len(grid))]

    # ---- pass B: every shot start and end, seeked exactly
    bnd = outdir / "bounds"
    bnd.mkdir(parents=True, exist_ok=True)
    bfiles, blabels, bindex = [], [], []
    for shot in tl["shots"]:
        for which, t in (("start", shot["start"] + 0.05), ("end", max(0.0, shot["end"] - 0.05))):
            p = bnd / f"{shot['id']}-{which}-{t:07.2f}s.jpg"
            if grab(master, t, p, args.tw):
                bfiles.append(p)
                blabels.append(f"{shot['id']} {which} {t:.1f}s")
                bindex.append({"shot": shot["id"], "which": which, "t": round(t, 3),
                               "scene": shot["scene"], "dur": round(shot["dur"], 2)})

    # ---- sheets
    sheets = []
    for i in range(0, len(grid), args.cols * 6):
        chunk = grid[i:i + args.cols * 6]
        labs = [f"{t:.0f}s" for t in grid_ts[i:i + args.cols * 6]]
        sheets.append(str(sheet(chunk, labs, outdir / f"sheet-grid-{i//(args.cols*6):03d}.jpg",
                                args.cols, args.tw,
                                f"DELIVERED MASTER — every {args.step:.0f}s — {labs[0]} to {labs[-1]}")))
    for i in range(0, len(bfiles), args.cols * 6):
        chunk = bfiles[i:i + args.cols * 6]
        labs = blabels[i:i + args.cols * 6]
        sheets.append(str(sheet(chunk, labs, outdir / f"sheet-bounds-{i//(args.cols*6):03d}.jpg",
                                args.cols, args.tw,
                                f"DELIVERED MASTER — shot starts and ends — {labs[0]} to {labs[-1]}")))

    report = {
        "master": str(master),
        "master_bytes": master.stat().st_size,
        "duration_s": round(dur, 3),
        "method": ("frames decoded from the delivered MP4 with FFmpeg: a fixed %ss grid over the whole "
                   "runtime, plus the first and last visible frame of every shot seeked individually"
                   % args.step),
        "grid": {"interval_s": args.step, "frames": len(grid),
                 "expected": int(dur // args.step) + 1,
                 "first_t": grid_ts[0] if grid_ts else None, "last_t": grid_ts[-1] if grid_ts else None,
                 "coverage_percent": round(100.0 * len(grid) / (int(dur // args.step) + 1), 1)},
        "shot_boundaries": {"shots": len(tl["shots"]), "frames": len(bfiles),
                            "expected": 2 * len(tl["shots"]),
                            "coverage_percent": round(100.0 * len(bfiles) / (2 * len(tl["shots"])), 1),
                            "index": bindex},
        "sheets": sheets,
        "limits_recorded_honestly": [
            "Sampled stills cannot certify motion, pacing continuity or audio; motion is judged from "
            "measured frame-to-frame differences (tools/holdcheck.py) and audio from measured "
            "loudness/true-peak on the same delivered file.",
            "No human watched or listened to this film; no audience, engagement or approval claim is made.",
            "Frames are decoded to contact sheets at reduced size for reading; full-resolution stills "
            "for the revised shots are kept separately in evidence/pass1 and evidence/pass2.",
        ],
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("sheets", "shot_boundaries")}, indent=2))
    print(json.dumps(report["grid"], indent=2))
    print(f"sheets={len(sheets)} bounds_frames={len(bfiles)} report={args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
