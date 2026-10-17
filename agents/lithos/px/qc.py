#!/usr/bin/env python3
"""Technical QC + review material for the parallax masters.

Measures, on the *delivered files* (not on the renderer's internals):

  * container / codec / pixel format / frame rate / AAC rate and bitrate
  * faststart (top-level atom order, moov before mdat)
  * integrated loudness (EBU R128) and true peak
  * picture 1920x1080 and a 640x360 "phone" legibility check
  * the review frame grid: every <= 0.5 s, plus dense 0.1-0.2 s samples
    around the structural transitions
  * the loop gate on the *encoded* loop: geometry (image-plane displacement
    between consecutive frames), position and velocity continuity across the
    wrap, light phase (mean luminance continuity) and the audio seam
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")
FFPROBE = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffprobe")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    out = run([FFPROBE, "-v", "error", "-print_format", "json",
               "-show_format", "-show_streams", str(path)])
    return json.loads(out.stdout)


def loudness(path):
    """Integrated LUFS + true peak from the ebur128 summary block."""
    out = run([FFMPEG, "-hide_banner", "-nostats", "-i", str(path),
               "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    lines = out.stderr.splitlines()
    k = max((i for i, l in enumerate(lines) if l.strip() == "Summary:"), default=0)
    lufs = tp = None
    for line in lines[k:]:
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


def atom_order(path):
    """Return the top-level box order of the MP4 (faststart = moov before mdat)."""
    boxes = []
    with open(path, "rb") as f:
        while True:
            head = f.read(8)
            if len(head) < 8:
                break
            size = int.from_bytes(head[:4], "big")
            kind = head[4:8].decode("latin-1")
            boxes.append(kind)
            if size == 1:
                size = int.from_bytes(f.read(8), "big")
                f.seek(size - 16, 1)
            elif size == 0:
                break
            else:
                f.seek(size - 8, 1)
    return boxes


def faststart(path):
    boxes = atom_order(path)
    if "moov" not in boxes:
        return None
    if "mdat" not in boxes:
        return True
    return boxes.index("moov") < boxes.index("mdat")


def grab(path, out_png, width=None, height=None, ss=None, sseof=None):
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.3f}"]
    if sseof is not None:
        cmd += ["-sseof", f"{sseof:.3f}"]
    cmd += ["-i", str(path)]
    if width:
        cmd += ["-vf", f"scale={width}:{height}"]
    cmd += ["-frames:v", "1", "-update", "1", str(out_png)]
    run(cmd)
    return out_png


def extract(path, times, out_dir, width=1920, height=1080):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    made = 0
    for t in times:
        p = out_dir / f"t{t:07.3f}.png"
        if p.exists():
            continue
        grab(path, p, width, height, ss=t)
        made += 1
    return {"dir": str(out_dir), "extracted_now": made,
            "total": len(list(out_dir.glob("t*.png")))}


def phase_shift(a, b):
    """Sub-pixel displacement (dx, dy) that best aligns image b onto image a."""
    a = a - a.mean()
    b = b - b.mean()
    win = np.hanning(a.shape[0])[:, None] * np.hanning(a.shape[1])[None, :]
    A = np.fft.rfft2(a * win)
    B = np.fft.rfft2(b * win)
    R = A * np.conj(B)
    R /= np.maximum(np.abs(R), 1e-9)
    corr = np.fft.irfft2(R, s=a.shape)
    idx = np.unravel_index(np.argmax(corr), corr.shape)
    peak = corr[idx]
    dy, dx = idx
    if dy > corr.shape[0] // 2:
        dy -= corr.shape[0]
    if dx > corr.shape[1] // 2:
        dx -= corr.shape[1]
    # parabolic refinement (x profile is a row, y profile is a column)
    def refine(v, n):
        y0, y1, y2 = v[(n - 1) % len(v)], v[n], v[(n + 1) % len(v)]
        d = y0 - 2 * y1 + y2
        return 0.5 * (y0 - y2) / d if abs(d) > 1e-12 else 0.0
    rx = refine(corr[idx[0], :], idx[1])
    ry = refine(corr[:, idx[1]], idx[0])
    return float(dx + rx), float(dy + ry), float(peak)



def brute_shift(a, b, span=10):
    """Best integer (dx, dy) that aligns b onto a by minimising the mean abs diff."""
    best = (0, 0, 1e9)
    h, w = a.shape
    for dy in range(-span, span + 1):
        for dx in range(-span, span + 1):
            ys0, ys1 = max(0, dy), min(h, h + dy)
            yd0, yd1 = max(0, -dy), min(h, h - dy)
            xs0, xs1 = max(0, dx), min(w, w + dx)
            xd0, xd1 = max(0, -dx), min(w, w - dx)
            if ys1 - ys0 < 32 or xs1 - xs0 < 32:
                continue
            d = float(np.abs(a[ys0:ys1, xs0:xs1] - b[yd0:yd1, xd0:xd1]).mean())
            if d < best[2]:
                best = (dx, dy, d)
    return best

def loop_gate(loop_path, work_dir):
    """Geometry / position / velocity / light-phase / audio-seam gate on the encoded loop."""
    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    p = probe(loop_path)
    v = next(s for s in p["streams"] if s.get("codec_type") == "video")
    fps = eval(v.get("avg_frame_rate", "25/1"))
    nframes = int(v.get("nb_frames") or 0)
    if not nframes:
        cnt = run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_frames",
                   "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(loop_path)])
        try:
            nframes = int(cnt.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            nframes = 0
    dur = float(p["format"]["duration"])

    # --- last 4 frames and first 4 frames, full resolution (by frame index, not timestamp)
    edge_dir = work / "edge"
    edge_dir.mkdir(parents=True, exist_ok=True)
    for old in edge_dir.glob("edge_*.png"):
        old.unlink()
    if nframes < 8:
        nframes = 8
    sel = f"select='lt(n\\,4)+gte(n\\,{nframes - 4})'"
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(loop_path),
         "-vf", sel, "-fps_mode", "passthrough", "-start_number", "0", str(edge_dir / "edge_%03d.png")])
    edge_files = sorted(edge_dir.glob("edge_*.png"))
    if len(edge_files) < 8:
        raise RuntimeError(f"edge frame extraction failed: {len(edge_files)} files")
    # the select filter emits the frames in file order, so the first four
    # outputs are the first frames of the loop and the last four are the last
    # frames; map them accordingly (last0 must be the final frame)
    names = []
    for i in range(4):
        names.append(("first%d" % i, edge_files[i]))
    for i in range(4):
        names.append(("last%d" % (3 - i), edge_files[4 + i]))
    imgs = {}
    for k, pth in names:
        imgs[k] = np.asarray(Image.open(pth).convert("L"), dtype=np.float32)
    means = {k: float(v_.mean()) for k, v_ in imgs.items()}

    def diff(x, y):
        return float(np.abs(imgs[x] - imgs[y]).mean())

    order = ["last3", "last2", "last1", "last0", "first0", "first1", "first2", "first3"]
    steps = []
    for a, b in zip(order, order[1:]):
        dx, dy, pk = phase_shift(imgs[a], imgs[b])
        bdx, bdy, berr = brute_shift(imgs[a], imgs[b])
        steps.append({"from": a, "to": b, "mean_abs_diff": round(diff(a, b), 4),
                      "dx_px": round(dx, 4), "dy_px": round(dy, 4),
                      "match_peak": round(pk, 4),
                      "brute_dx_px": bdx, "brute_dy_px": bdy,
                      "brute_err": round(berr, 4)})
    interior = [s for s in steps if not (s["from"] == "last0" and s["to"] == "first0")]
    wrap = next(s for s in steps if s["from"] == "last0" and s["to"] == "first0")
    interior_diffs = [s["mean_abs_diff"] for s in interior]
    interior_dx = [abs(s["brute_dx_px"]) for s in interior]
    interior_dy = [abs(s["brute_dy_px"]) for s in interior]
    wrap_bdx = wrap["brute_dx_px"]
    wrap_bdy = wrap["brute_dy_px"]

    # light phase: mean luminance continuity across the wrap
    light_step = means["last0"] - means["first0"]
    light_max_interior = max(abs(means[s] - means[t]) for s, t in
                             zip(order, order[1:]) if not (s == "last0" and t == "first0"))

    # audio seam on the encoded file
    raw_p = work / "loop-f32.raw"
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(loop_path),
         "-vn", "-f", "f32le", "-ac", "1", "-ar", "48000", str(raw_p)])
    raw = np.fromfile(raw_p, dtype=np.float32)
    if raw.size > 8192:
        wrap_step = float(abs(raw[0] - raw[-1]))
        d = np.abs(np.diff(raw))
        local_p999 = float(np.percentile(d, 99.9))
        local_max = float(d.max())
    else:
        wrap_step = local_p999 = local_max = float("nan")

    return {
        "encoded_loop": str(loop_path),
        "fps": fps, "frames": nframes, "duration_s": round(dur, 3),
        "frame_steps": steps,
        "geometry": {
            "wrap_mean_abs_diff": wrap["mean_abs_diff"],
            "interior_mean_abs_diff_min": round(min(interior_diffs), 4),
            "interior_mean_abs_diff_max": round(max(interior_diffs), 4),
            "wrap_within_interior_range": bool(min(interior_diffs) <= wrap["mean_abs_diff"] <= max(interior_diffs) * 1.35 + 0.05),
        },
        "position_velocity": {
            "wrap_dx_px": wrap_bdx, "wrap_dy_px": wrap_bdy,
            "wrap_corr_dx_px": wrap["dx_px"], "wrap_corr_dy_px": wrap["dy_px"],
            "interior_abs_dx_px": [round(v, 4) for v in interior_dx],
            "interior_abs_dy_px": [round(v, 4) for v in interior_dy],
            "velocity_continuous": bool(abs(wrap_bdx) <= max(interior_dx) * 1.5 + 1.0 and
                                        abs(wrap_bdy) <= max(interior_dy) * 1.5 + 1.0),
        },
        "light_phase": {
            "mean_luma_last0": round(means["last0"], 4),
            "mean_luma_first0": round(means["first0"], 4),
            "wrap_luma_step": round(light_step, 4),
            "max_interior_luma_step": round(light_max_interior, 4),
            "continuous": bool(abs(light_step) <= max(light_max_interior, 0.05) * 1.6 + 0.05),
        },
        "audio_seam": {
            "wrap_sample_step": round(wrap_step, 6),
            "local_p999_step": round(local_p999, 6),
            "local_max_step": round(local_max, 6),
            "seam_ok": bool(wrap_step <= max(local_p999, 1e-4) * 4 + 1e-3),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", required=True)
    ap.add_argument("--loop", required=True)
    ap.add_argument("--out", default="work/qc")
    ap.add_argument("--frames", action="store_true")
    ap.add_argument("--dense", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--source-loop", default=None, help="uncompressed loop wav for the sample-exact seam")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {"generated_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
              .isoformat(timespec="seconds")}
    durations = {}
    for tag, path in (("hero", Path(args.hero)), ("loop", Path(args.loop))):
        if not path.exists():
            report[tag] = {"error": "missing", "path": str(path)}
            continue
        p = probe(path)
        v = next((s for s in p["streams"] if s.get("codec_type") == "video"), None)
        a = next((s for s in p["streams"] if s.get("codec_type") == "audio"), None)
        lufs, tp = loudness(path)
        dur = float(p["format"]["duration"])
        durations[tag] = dur
        fps = None
        if v and v.get("r_frame_rate"):
            n, d = v["r_frame_rate"].split("/")
            fps = float(n) / float(d)
        entry = {
            "path": str(path),
            "bytes": int(p["format"]["size"]),
            "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
            "duration_s": round(dur, 3),
            "video_codec": v["codec_name"] if v else None,
            "pix_fmt": v["pix_fmt"] if v else None,
            "profile": v.get("profile") if v else None,
            "width": v["width"] if v else None,
            "height": v["height"] if v else None,
            "fps": fps,
            "nb_frames": v.get("nb_frames") if v else None,
            "audio_codec": a["codec_name"] if a else None,
            "audio_sample_rate": int(a["sample_rate"]) if a else None,
            "audio_channels": a.get("channels") if a else None,
            "audio_bitrate_bps": int(a.get("bit_rate") or 0) if a else None,
            "integrated_lufs": lufs,
            "true_peak_dbtp": tp,
            "faststart": faststart(path),
            "atom_order": atom_order(path),
            "video_duration_s": round(float(v["duration"]), 3) if v and v.get("duration") else None,
            "audio_duration_s": round(float(a["duration"]), 3) if a and a.get("duration") else None,
        }
        if v and a and v.get("duration") and a.get("duration"):
            entry["av_tail_mismatch_s"] = round(abs(float(v["duration"]) - float(a["duration"])), 3)
        if tag == "hero":
            entry["duration_in_spec_35_55"] = bool(35.0 <= dur <= 55.0)
        else:
            entry["duration_in_spec_8_12"] = bool(8.0 <= dur <= 12.0)
            entry["loop_samples_at_48k"] = int(round(dur * 48000))
        report[tag] = entry

    if args.frames and durations.get("hero"):
        times = [round(0.5 * i, 2) for i in range(int(durations["hero"] * 2) + 1)]
        report["review_frames_0p5s"] = extract(Path(args.hero), times, out / "frames")
        report["phone_frames_640x360"] = extract(Path(args.hero), times[::2], out / "phone",
                                                 width=640, height=360)
    if args.dense and durations.get("hero"):
        dense = []
        for centre in (3.5, 8.0, 11.05, 17.0, 18.5, 20.3, 22.1, 23.9, 26.0, 29.5, 34.0):
            for k in range(-3, 4):
                t = round(centre + k * 0.05, 2)
                if 0 <= t <= durations["hero"]:
                    dense.append(t)
        report["dense_samples_0p1s"] = extract(Path(args.hero), sorted(set(dense)), out / "dense")
    if args.gate and durations.get("loop"):
        report["loop_gate"] = loop_gate(Path(args.loop), out / "gate")
        if args.source_loop and Path(args.source_loop).exists():
            raw_p = out / "gate" / "source-f32.raw"
            run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                 "-i", str(args.source_loop), "-vn", "-f", "f32le", "-ac", "1",
                 "-ar", "48000", str(raw_p)])
            src = np.fromfile(raw_p, dtype=np.float32)
            if src.size > 2:
                peak = float(np.abs(src).max())
                step = float(abs(src[0] - src[-1]))
                report["loop_gate"]["audio_seam"]["source_wav_sample_step"] = round(step, 8)
                report["loop_gate"]["audio_seam"]["source_wav_peak"] = round(peak, 6)
                report["loop_gate"]["audio_seam"]["source_wav_relative_step"] = round(step / max(peak, 1e-9), 8)
                report["loop_gate"]["audio_seam"]["source_samples"] = int(src.size)

    (out / "technical.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
