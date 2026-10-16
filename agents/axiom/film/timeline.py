#!/usr/bin/env python3
"""axiom timeline — turns MEASURED narration durations + the shot plan into the film clock.

Nothing here estimates speech length from character counts: every cue duration comes from
the generated WAV (work/narration/<voice>/manifest.json). Output: work/timeline.json with
shot spans, chapter spans, per-cue beat offsets inside each shot, and the audio cue map.
"""
from __future__ import annotations

import json
from pathlib import Path

from film.script import CHAPTERS

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"

PAUSE_AFTER = 0.30          # between sentences
PAUSE_CHAPTER = 1.15        # breathing room at a chapter boundary
CARD_DUR = 4.3              # chapter card overlay length
FILM_PRE = 1.6              # silence + music before the first line
END_TAIL = 7.0              # music/end-card tail after the last line


def load_manifest(voice: str) -> dict:
    p = WORK / "narration" / voice / "manifest.json"
    if not p.exists():
        raise SystemExit(f"missing narration manifest {p} — run tools/narrate.py first")
    return json.loads(p.read_text())


def fake_manifest(seconds_per_cue: float = 6.0) -> dict:
    """Structure test only: never used for a delivered render (no measured durations)."""
    from film.script import all_cues
    cues = {cid: {"text": text, "file": "", "duration": seconds_per_cue} for _ch, cid, text in all_cues()}
    return {"voice": "placeholder", "cue_count": len(cues), "cues": cues, "synthetic": True}


def build(voice: str = "am_michael", fake_seconds: float | None = None,
          out: Path | None = None) -> dict:
    man = fake_manifest(fake_seconds) if fake_seconds else load_manifest(voice)
    cues = man["cues"]

    # ---------------------------------------------------- cue clock ----
    t = FILM_PRE
    cue_clock = {}
    chapter_clock = {}
    for ch in CHAPTERS:
        ch_start = t
        for cid, _text in ch["sentences"]:
            c = cues[cid]
            cue_clock[cid] = {"start": round(t, 3), "dur": c["duration"],
                              "end": round(t + c["duration"], 3), "file": c["file"]}
            t += c["duration"]
            t += PAUSE_AFTER
        # chapter boundary: last pause replaced by a longer beat
        t += PAUSE_CHAPTER - PAUSE_AFTER
        chapter_clock[ch["id"]] = {"start": round(ch_start, 3), "end": round(t, 3),
                                   "card": ch["card"], "title": f"Chapter {ch['id']}"}
    total_speech_end = t
    t += END_TAIL

    # ---------------------------------------------------- shot clock ----
    shots, warnings = [], []
    flat = [(ch, sh) for ch in CHAPTERS for sh in ch["shots"]]
    for ch, sh in flat:
        first, last = sh["cues"][0], sh["cues"][-1]
        c0, c1 = cue_clock[first], cue_clock[last]
        shots.append({
            "id": sh["id"], "chapter": ch["id"], "scene": sh["scene"], "bg": sh.get("bg", "parchment"),
            "params": sh.get("params", {}), "cue_ids": list(sh["cues"]),
            "first_cue_start": c0["start"], "last_cue_end": c1["end"],
            "post": sh.get("post", 0.6), "pre": sh.get("pre", 0.6),
            "start": c0["start"], "end": c1["end"] + sh.get("post", 0.6),
        })
    # a shot may not run past the first cue of the shot that follows it.
    # A cue deliberately shared by two consecutive shots is cut inside that cue.
    for a, b in zip(shots, shots[1:]):
        if b["cue_ids"][0] in a["cue_ids"]:
            shared = b["cue_ids"][0]
            limit = cue_clock[shared]["end"] - 0.25
        else:
            limit = b["first_cue_start"] + 0.05
        if a["end"] > limit:
            over = a["end"] - limit
            a["end"] = round(limit, 3)
            warnings.append(f"{a['id']}: post trimmed {over:.2f}s so {b['id']}'s first cue lands after its cut")
    # contiguity: every shot starts exactly where the previous one ends
    for i, s_ in enumerate(shots):
        if i == 0:
            s_["start"] = round(max(0.0, s_["first_cue_start"] - s_["pre"]), 3)
        else:
            s_["start"] = shots[i - 1]["end"]
        if s_["start"] > s_["first_cue_start"]:
            warnings.append(f"{s_['id']}: cut lands {s_['start']-s_['first_cue_start']:.2f}s after its first cue")
        s_["dur"] = round(s_["end"] - s_["start"], 3)
        s_["cues"] = {cid: {"at": round(cue_clock[cid]["start"] - s_["start"], 3),
                            "dur": cue_clock[cid]["dur"],
                            "end": round(cue_clock[cid]["end"] - s_["start"], 3)}
                      for cid in s_["cue_ids"]}

    # ---------------------------------------------------- chapter cards ----
    for ch in CHAPTERS:
        cc = chapter_clock[ch["id"]]
        first_cue = cue_clock[ch["sentences"][0][0]]
        second_cue = cue_clock[ch["sentences"][1][0]] if len(ch["sentences"]) > 1 else None
        card_start = max(0.0, first_cue["start"] - 1.15)
        card_end = min(card_start + CARD_DUR, (second_cue["start"] + 0.6) if second_cue else first_cue["end"])
        cc["card_start"] = round(card_start, 3)
        cc["card_end"] = round(card_end, 3)
        cc["card_dur"] = round(card_end - card_start, 3)

    # ------------------------------------------------- shots per chapter ----
    for ch in CHAPTERS:
        ids = [s["id"] for s in shots if s["chapter"] == ch["id"]]
        chapter_clock[ch["id"]]["shots"] = ids
        chapter_clock[ch["id"]]["length"] = round(
            sum(s["dur"] for s in shots if s["chapter"] == ch["id"]), 2)

    tl = {
        "voice": voice, "revision": "r01", "placeholder_timing": bool(fake_seconds),
        "total_duration": round(t, 3),
        "speech_end": round(total_speech_end, 3),
        "shot_count": len(shots), "cue_count": len(cue_clock),
        "chapters": chapter_clock, "cues": cue_clock, "shots": shots,
        "warnings": warnings,
    }
    out = out or (WORK / "timeline.json")
    Path(out).write_text(json.dumps(tl, indent=2) + "\n")
    return tl


if __name__ == "__main__":
    import sys
    voice = sys.argv[1] if len(sys.argv) > 1 else "am_michael"
    tl = build(voice)
    print(json.dumps({"total_duration": tl["total_duration"], "shots": tl["shot_count"],
                      "cues": tl["cue_count"], "warnings": tl["warnings"],
                      "chapters": {k: v["length"] for k, v in tl["chapters"].items()}}, indent=2))
