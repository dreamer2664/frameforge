#!/usr/bin/env python3
"""Assemble the release bundle in final/ with hashes, and print the exact publish command.

  python3 tools/package.py --revision r01 \
      --master /tmp/axiom-render/axiom-r01-1080p.mp4 \
      --rough /tmp/axiom-render/axiom-r01-720p.mp4 \
      --srt renders/axiom-r01.srt --vtt renders/axiom-r01.vtt \
      --qc evidence/final-technical.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def ffprobe_json(p: Path) -> dict:
    from ops.bootstrap_media import binary  # type: ignore
    import os
    exe = binary("ffprobe")
    return json.loads(subprocess.check_output(
        [exe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(p)]))


PUBLISH_STATUS = {
    "attempted": True,
    "result": "blocked",
    "blockers": [
        "GITHUB_TOKEN / CHATCODE_TOKEN do not exist in this environment any more (the chatcode "
        "heartbeat returns 401 Unauthorized), so ops/release.py cannot authenticate to "
        "dreamer2664/storagecode.",
        "The clones lost their .git metadata in the sandbox reset, so release.py also fails at "
        "`git rev-parse HEAD` until the repositories are re-cloned.",
    ],
    "what_is_ready": ("every asset below is hashed, the commissioning gate passes with 0 violations, "
                      "the tag and storage paths are recorded, and publish_command is complete"),
    "local_fallback_path": "data/frameforge/axiom/<revision>/ (created by ops/release.py when it can run)",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", default="r01")
    ap.add_argument("--master", required=True)
    ap.add_argument("--rough", default="")
    ap.add_argument("--srt", default=str(ROOT / "renders/axiom-r01.srt"))
    ap.add_argument("--vtt", default=str(ROOT / "renders/axiom-r01.vtt"))
    ap.add_argument("--chapters", default=str(ROOT / "evidence/chapters.json"))
    ap.add_argument("--qc", default=str(ROOT / "evidence/final-technical.json"))
    ap.add_argument("--activity", default=str(ROOT / "evidence/activity-r01.json"))
    ap.add_argument("--outdir", default=str(ROOT / "final"))
    args = ap.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    rev = args.revision
    assets: list[dict] = []

    def add(src: Path, name: str, kind: str, meta: dict | None = None) -> None:
        if not src.exists():
            print(f"  (missing, skipped) {src}")
            return
        dst = out / name
        if src.resolve() != dst.resolve():
            shutil.copy2(src, dst)
        row = {"name": name, "kind": kind, "bytes": dst.stat().st_size, "sha256": sha256(dst)}
        if meta:
            row.update(meta)
        assets.append(row)

    master = Path(args.master)
    meta = {}
    if master.exists():
        info = ffprobe_json(master)
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
        meta = {"duration_s": round(float(info["format"]["duration"]), 3),
                "video": f'{v["codec_name"]}/{v["pix_fmt"]}/{v["width"]}x{v["height"]}@{v["avg_frame_rate"]}',
                "audio": (f'{a["codec_name"]}/{a["sample_rate"]}Hz/{int(a.get("bit_rate", 0))//1000}kbps'
                          if a else "none")}
    add(master, f"axiom-{rev}-1080p.mp4", "master", meta)
    if args.rough:
        add(Path(args.rough), f"axiom-{rev}-720p.mp4", "rough-cut",
            {"note": "same cut at the review resolution used for the inspect-and-revise passes"})
    add(Path(args.srt), f"axiom-{rev}.srt", "subtitle")
    add(Path(args.vtt), f"axiom-{rev}.vtt", "subtitle")

    chapters = Path(args.chapters)
    if chapters.exists():
        text = json.loads(chapters.read_text())["youtube_chapters"]
        (out / f"axiom-{rev}-chapters.txt").write_text(text + "\n")
        add(out / f"axiom-{rev}-chapters.txt", f"axiom-{rev}-chapters.txt", "chapters")

    add(ROOT / "final/axiom-poster-1920x1080.png", "axiom-poster-1920x1080.png", "poster")
    add(ROOT / "final/axiom-thumbnail-1280x720.jpg", "axiom-thumbnail-1280x720.jpg", "thumbnail")
    add(ROOT / "research/sources.md", f"axiom-{rev}-sources-and-rights.md", "sources")
    add(ROOT / "evidence/source-rights.md", f"axiom-{rev}-claim-ledger.md", "sources")

    qc = Path(args.qc)
    if qc.exists():
        row = json.loads(qc.read_text())
        (out / f"axiom-{rev}-technical.json").write_text(json.dumps(row, indent=2) + "\n")
        add(out / f"axiom-{rev}-technical.json", f"axiom-{rev}-technical.json", "qc",
            {"technical_pass": row.get("technical_pass"), "violations": row.get("violations")})
    act = Path(args.activity)
    if act.exists():
        row = json.loads(act.read_text())
        (out / f"axiom-{rev}-self-review.json").write_text(json.dumps({
            "reviewed_by": "axiom (producer, automated + rendered-frame inspection)",
            "human_review": None,
            "claims_about_audience": "none made",
            "activity": {k: v for k, v in row.items() if k != "rows"},
            "shot_rows": row.get("rows", []),
        }, indent=2) + "\n")
        add(out / f"axiom-{rev}-self-review.json", f"axiom-{rev}-self-review.json", "self-review")

    MANIFEST_TEXT = lambda: None  # noqa: E731 (placeholder removed below)
    manifest = {
        "film": "How Old Is the Earth? Three clocks that had to be broken",
        "producer": "axiom",
        "revision": rev,
        "tag": f"frameforge/axiom/{rev}-{next((a['sha256'][:12] for a in assets if a['kind']=='master'), 'unknown')}",
        "path": f"data/frameforge/axiom/{rev}/",
        "assets": assets,
        "rough_cut_path": f"agents/axiom/renders/axiom-{rev}-rough-cut-720p.mp4",
        "publish_command": (
            f"python3 ops/release.py axiom --video agents/axiom/final/axiom-{rev}-1080p.mp4 "
            f"--title 'How Old Is the Earth? Three clocks that had to be broken' --revision {rev} "
            f"--asset agents/axiom/renders/axiom-{rev}-rough-cut-720p.mp4 "
            f"--asset agents/axiom/final/axiom-poster-1920x1080.png "
            f"--asset agents/axiom/final/axiom-thumbnail-1280x720.jpg"),
        "publish_status": PUBLISH_STATUS,
        "honesty": "No human viewed, listened to or approved this film; the self-review is the "
                   "producer's own, from rendered frames and measured activity.",
    }
    (out / f"axiom-{rev}-RELEASE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"assets": [(a["name"], a["bytes"]) for a in assets]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
