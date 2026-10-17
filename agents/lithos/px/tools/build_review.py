#!/usr/bin/env python3
"""Assemble the exact-file review material for the final masters.

Produces, from the delivered MP4s (not from the renderer):

  work/qc/technical.json      measured technical report (codec, loudness, gate)
  work/qc/frames/              the <= 0.5 s review grid at full size
  work/qc/dense/               dense 0.1-0.2 s samples around the transitions
  work/qc/phone/               640x360 phone check
  work/review/sheet-*.png      contact sheets of the grid, for visual review
  work/review/loop-frames/     the loop's own grid (one frame per 0.4 s)
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import sheet  # noqa: E402

FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")


def main():
    hero = HERE / "work/renders/hero-master.mp4"
    loop = HERE / "work/renders/loop-master.mp4"
    if not hero.exists() or not loop.exists():
        raise SystemExit("masters missing")
    qc = HERE / "work/qc"
    cmd = [sys.executable, str(HERE / "qc.py"),
           "--hero", str(hero), "--loop", str(loop),
           "--out", str(qc), "--frames", "--dense", "--gate",
           "--source-loop", str(HERE / "work/audio/loop.wav")]
    subprocess.run(cmd, check=True)

    # the loop's own grid
    ldir = HERE / "work/review/loop-frames"
    ldir.mkdir(parents=True, exist_ok=True)
    times = [round(0.4 * i, 2) for i in range(25)]
    for t in times:
        out = ldir / f"t{t:06.2f}.png"
        if out.exists():
            continue
        subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                        "-ss", f"{t:.2f}", "-i", str(loop), "-frames:v", "1",
                        "-update", "1", str(out)], check=False)

    # contact sheets of the review grid (20 frames each)
    frames = sorted((qc / "frames").glob("t*.png"))
    review = HERE / "work/review"
    review.mkdir(parents=True, exist_ok=True)
    per = 20
    for i in range(0, len(frames), per):
        chunk = frames[i:i + per]
        tmp = review / f"_chunk{i}"
        tmp.mkdir(exist_ok=True)
        for f in chunk:
            (tmp / f.name).write_bytes(f.read_bytes())
        import subprocess as sp
        sp.run([sys.executable, str(HERE / "sheet.py"), "--src", str(tmp),
                "--out", str(review / f"sheet-{i // per:02d}.png"),
                "--cols", "4", "--cell", "440"], check=True)
        for f in tmp.glob("*.png"):
            f.unlink()
        tmp.rmdir()
    import subprocess as sp
    sp.run([sys.executable, str(HERE / "sheet.py"), "--src", str(ldir),
            "--out", str(review / "sheet-loop.png"), "--cols", "5", "--cell", "360"], check=False)
    sp.run([sys.executable, str(HERE / "sheet.py"), "--src", str(qc / "phone"),
            "--out", str(review / "sheet-phone.png"), "--cols", "6", "--cell", "300"], check=False)
    print(json.dumps({"frames": len(frames),
                      "sheets": sorted(p.name for p in review.glob("sheet-*.png"))}, indent=2))


if __name__ == "__main__":
    main()
