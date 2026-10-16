#!/usr/bin/env python3
"""Sidecar subtitles + chapter timecodes from the real timeline.

One cue per subtitle line (the narration sentences were written as speaking-length lines,
so they are never split or merged here — what is timed is what is spoken).

Usage:
  python3 tools/subtitles.py --timeline work/timeline.json \
      --srt renders/axiom-r01.srt --vtt renders/axiom-r01.vtt \
      --chapters evidence/chapters.json [--shift 0.0]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from film import script  # noqa: E402


def stamp(t: float, sep: str) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s, ms = s + 1, 0
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def cue_text() -> dict[str, str]:
    out: dict[str, str] = {}
    for ch in script.CHAPTERS:
        for cid, text in ch["sentences"]:
            out[cid] = " ".join(text.split())
    return out


def wrap_lines(text: str, width: int = 42) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines or [""]


def screens(text: str, max_lines: int = 3, width: int = 42) -> list[str]:
    """Split one narration cue into readable on-screen blocks (<=3 lines of <=42 chars).

    Timing for each block is proportional to its share of the cue's characters, so the total
    still exactly covers the cue: the sidecar never drifts from the measured narration."""
    lines = wrap_lines(text, width)
    out: list[str] = []
    for i in range(0, len(lines), max_lines):
        out.append("\n".join(lines[i:i + max_lines]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", default=str(ROOT / "work/timeline.json"))
    ap.add_argument("--srt", default=str(ROOT / "renders/axiom-r01.srt"))
    ap.add_argument("--vtt", default=str(ROOT / "renders/axiom-r01.vtt"))
    ap.add_argument("--chapters", default=str(ROOT / "evidence/chapters.json"))
    ap.add_argument("--shift", type=float, default=0.0, help="seconds to add to every cue")
    args = ap.parse_args()

    tl = json.loads(Path(args.timeline).read_text())
    text = cue_text()
    cues = sorted(tl["cues"].items(), key=lambda kv: kv[1]["start"])

    srt: list[str] = []
    idx = 0
    for cid, c in cues:
        blocks = screens(text.get(cid, f"[missing text for {cid}]"))
        total_chars = sum(len(b) for b in blocks) or 1
        t0, span = c["start"] + args.shift, c["end"] - c["start"]
        acc = 0
        for j, b in enumerate(blocks):
            b0 = t0 + span * acc / total_chars
            acc += len(b)
            b1 = t0 + span * acc / total_chars if j < len(blocks) - 1 else c["end"] + args.shift
            idx += 1
            srt.append(f"{idx}\n{stamp(b0, ',')} --> {stamp(b1, ',')}\n{b}\n")
    Path(args.srt).parent.mkdir(parents=True, exist_ok=True)
    Path(args.srt).write_text("\n".join(srt))

    vtt = ["WEBVTT", "", "NOTE speaker: axiom film narrator (synthetic voice am_michael)",
           "NOTE blocks belong to the measured narration cue named in the cue id; timing is proportional within the cue", ""]
    idx = 0
    for cid, c in cues:
        blocks = screens(text.get(cid, f"[missing text for {cid}]"))
        total_chars = sum(len(b) for b in blocks) or 1
        t0, span = c["start"] + args.shift, c["end"] - c["start"]
        acc = 0
        for j, b in enumerate(blocks):
            b0 = t0 + span * acc / total_chars
            acc += len(b)
            b1 = t0 + span * acc / total_chars if j < len(blocks) - 1 else c["end"] + args.shift
            idx += 1
            vtt.append(f"cue{idx} {cid}\n{stamp(b0, '.')} --> {stamp(b1, '.')}\n{b}\n")
    Path(args.vtt).parent.mkdir(parents=True, exist_ok=True)
    Path(args.vtt).write_text("\n".join(vtt))

    chap = []
    for cid, c in sorted(tl["chapters"].items(), key=lambda kv: int(kv[0])):
        chap.append({
            "chapter": int(cid),
            "card": c["card"],
            "card_start": round(c["card_start"] + args.shift, 3),
            "story_start": round(c["start"] + args.shift, 3),
            "end": round(c["end"] + args.shift, 3),
            "length_s": round(c["length"], 2),
            "shots": len(c["shots"]),
            "cue_from": c["shots"][0] if c["shots"] else None,
        })
    meta = {
        "film": "How Old Is the Earth? The clocks that had to be broken",
        "producer": "axiom",
        "revision": tl.get("revision", "r01"),
        "total_duration_s": tl["total_duration"],
        "cues": len(cues),
        "subtitle_blocks": idx,
        "shots": tl.get("shot_count"),
        "chapters": chap,
        "youtube_chapters": "\n".join(
            ("00:00:00" if i == 0 else stamp(c["card_start"], ":")[:8]) + f" {c['chapter']}. {c['card']}"
            for i, c in enumerate(chap)
        ),
    }
    Path(args.chapters).parent.mkdir(parents=True, exist_ok=True)
    Path(args.chapters).write_text(json.dumps(meta, indent=2))
    print(json.dumps({"srt": args.srt, "vtt": args.vtt, "cues": len(cues), "blocks": idx,
                      "chapters": len(chap)}, indent=2))
    print(meta["youtube_chapters"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
