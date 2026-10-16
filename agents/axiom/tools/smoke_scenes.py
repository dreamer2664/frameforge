#!/usr/bin/env python3
"""axiom scene smoke test — draw every shot at several local times, at low scale,
and build contact sheets. Catches exceptions, missing props and dead compositions
before any expensive render.

  python3 tools/smoke_scenes.py [--timeline work/timeline.test.json] [--scale 0.30] [--samples 3]
"""
from __future__ import annotations

import argparse, json, sys, traceback
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))          # so `film` is importable as a package
sys.path.insert(0, str(ROOT / "tools"))

from film import timeline as tlmod  # noqa: E402
from film.render import render_frame  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", default=None)
    ap.add_argument("--scale", type=float, default=0.30)
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "work" / "smoke"))
    a = ap.parse_args()

    if a.timeline:
        tl = json.loads(Path(a.timeline).read_text())
    else:
        tl = tlmod.build("smoke", fake_seconds=6.0, out=ROOT / "work" / "timeline-smoke.json")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    W, H = int(1920 * a.scale), int(1080 * a.scale)

    frames, errors = [], []
    for shot in tl["shots"]:
        dur = shot["dur"]
        for i in range(a.samples):
            local = dur * (0.15 + 0.7 * i / max(1, a.samples - 1)) if a.samples > 1 else dur * 0.5
            t = shot["start"] + local
            try:
                img = render_frame(tl, t, a.scale, W, H)
                p = out / f"{shot['id']}-{i}.jpg"
                img.save(p, quality=86)
                frames.append((p, f"{shot['id']} {shot['scene']} {t:.1f}s"))
            except Exception as e:
                errors.append(f"{shot['id']} {shot['scene']} t={t:.2f}: {type(e).__name__}: {e}")
                traceback.print_exc()
    # contact sheets, 4 columns
    cols, tw = 4, W
    per = cols * 5
    sheets = []
    for n in range(0, len(frames), per):
        batch = frames[n:n + per]
        rows = (len(batch) + cols - 1) // cols
        canvas = Image.new("RGB", (cols * tw, rows * (H + 24)), (16, 18, 24))
        d = ImageDraw.Draw(canvas)
        for i, (p, label) in enumerate(batch):
            with Image.open(p) as im:
                canvas.paste(im, ((i % cols) * tw, (i // cols) * (H + 24)))
            d.text(((i % cols) * tw + 6, (i // cols) * (H + 24) + H + 5), label, fill=(235, 235, 240))
        sp = out / f"smoke-{n//per:02d}.jpg"
        canvas.save(sp, quality=84)
        sheets.append(str(sp))
    report = {"shots": len(tl["shots"]), "frames": len(frames), "errors": errors, "sheets": sheets}
    (out / "smoke-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"shots": report["shots"], "frames": report["frames"],
                      "errors": errors, "sheets": sheets}, indent=2))


if __name__ == "__main__":
    main()
