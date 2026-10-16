#!/usr/bin/env python3
"""Measure visual activity per shot, from actually rendered frames.

Answers two commission criteria with numbers instead of adjectives:
  * "no greater than 12 s unchanging holds without justification"
  * "an interval should introduce an intentional visual action every ~4-10 s"

Method: render each shot at 1 s (configurable) intervals at low scale, then compare
consecutive frames by mean absolute pixel difference. A step counts as an ACTION if the
difference exceeds `--action-thresh` (default 1.6/255 mean abs, which ignores pure
compression noise at these scales). Longest run of sub-`--hold-thresh` steps = longest hold.

Usage:
  python3 tools/holdcheck.py --timeline work/timeline.json --out evidence/activity-r01.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from film.render import render_frame  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", default=str(ROOT / "work/timeline.json"))
    ap.add_argument("--out", default=str(ROOT / "evidence/activity.json"))
    ap.add_argument("--step", type=float, default=1.0)
    ap.add_argument("--scale", type=float, default=0.25)
    ap.add_argument("--action-thresh", type=float, default=1.6)
    ap.add_argument("--hold-thresh", type=float, default=0.55)
    args = ap.parse_args()

    tl = json.loads(Path(args.timeline).read_text())
    W, H = int(1920 * args.scale), int(1080 * args.scale)
    rows = []
    worst = {"hold_s": 0.0, "shot": None, "at": None}
    for shot in tl["shots"]:
        n = max(2, int(shot["dur"] / args.step) + 1)
        ts = [shot["start"] + i * (shot["dur"] / (n - 1)) for i in range(n)]
        prev = None
        diffs = []
        for t in ts:
            a = np.asarray(render_frame(tl, t, args.scale, W, H).convert("L"), dtype=np.float32)
            if prev is not None:
                diffs.append(float(np.abs(a - prev).mean()))
            prev = a
        # longest run of consecutive hold-steps, in seconds
        run = best = 0
        best_at = None
        for i, d in enumerate(diffs):
            if d < args.hold_thresh:
                run += 1
                if run > best:
                    best, best_at = run, ts[i + 1 - run]
            else:
                run = 0
        secs = best * args.step
        actions = sum(1 for d in diffs if d >= args.action_thresh)
        rows.append({
            "shot": shot["id"], "scene": shot["scene"], "chapter": shot["chapter"],
            "dur": round(shot["dur"], 2), "start": round(shot["start"], 2),
            "longest_hold_s": round(secs, 2), "hold_from": round(best_at, 2) if best_at else None,
            "actions": actions,
            "action_interval_s": round(shot["dur"] / actions, 2) if actions else None,
            "max_step_diff": round(max(diffs), 3) if diffs else 0.0,
        })
        if secs > worst["hold_s"]:
            worst = {"hold_s": secs, "shot": shot["id"], "at": best_at}

    holds = [r["longest_hold_s"] for r in rows]
    ivs = [r["action_interval_s"] for r in rows if r["action_interval_s"]]
    out = {
        "method": ("rendered frames at %.2fs steps at %.2f scale, compared by mean absolute "
                   "pixel difference; action >= %.2f, hold < %.2f (0-255 grey levels)"
                   % (args.step, args.scale, args.action_thresh, args.hold_thresh)),
        "timeline": str(args.timeline),
        "shots": len(rows),
        "longest_hold_overall_s": round(worst["hold_s"], 2),
        "longest_hold_shot": worst["shot"],
        "shots_over_12s_hold": [r["shot"] for r in rows if r["longest_hold_s"] > 12.0],
        "shots_with_no_action": [r["shot"] for r in rows if r["actions"] == 0],
        "median_action_interval_s": round(float(np.median(ivs)), 2) if ivs else None,
        "p90_action_interval_s": round(float(np.percentile(ivs, 90)), 2) if ivs else None,
        "mean_longest_hold_s": round(float(np.mean(holds)), 2),
        "rows": rows,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
