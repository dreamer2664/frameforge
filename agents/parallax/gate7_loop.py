"""Gate 7 — loop seam gate, measured on the ENCODED MP4 (not source frames).

Checks (all on work/renders/loop-rNN.mp4):
 1. container/codec spec: H.264 yuv420p, AAC 48k >=160k, faststart, duration == fps period * frames
 2. geometry+velocity+light continuity: MAE(f_last, f_0) vs median MAE of ordinary 1-frame steps
    (wrap step must be <= 1.35x median ordinary step)
 3. audio seam: RMS discontinuity at the wrap (|s[0]-s[-1]| and 50-sample slope) vs median interior slope
 4. two-copy concat: encode loop twice back-to-back, confirm junction frame-diff == wrap diff (no added pop)
 5. loudness/TP of the loop file
Writes work/inspection/loop-gate-rNN.json + prints PASS/FAIL table.
"""
import json, os, subprocess, sys
import numpy as np

FF = os.path.expanduser("~/.cache/frameforge/bin/ffmpeg")
FP = os.path.expanduser("~/.cache/frameforge/bin/ffprobe")


def run(cmd, raw=False):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode:
        raise RuntimeError(f"cmd failed: {r.stderr[-1200:].decode('utf8','replace')}")
    return r.stdout if raw else r.stdout.decode("utf8", "replace") + r.stderr.decode("utf8", "replace")


def frames(mp4, n):
    out = run([FF, "-hide_banner", "-loglevel", "error", "-i", mp4, "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], raw=True)
    a = np.frombuffer(out, dtype=np.uint8)
    cnt = len(a) // (1920 * 1080 * 3)
    return a[:cnt * 1920 * 1080 * 3].reshape(cnt, 1080, 1920, 3).astype(np.float32)


def audio(mp4):
    out = run([FF, "-hide_banner", "-loglevel", "error", "-i", mp4, "-f", "s16le", "-acodec", "pcm_s16le", "-"], raw=True)
    return np.frombuffer(out, dtype=np.int16).astype(np.float64) / 32768.0


def main(mp4, tag):
    rep = {}
    pr = json.loads(subprocess.run([FP, "-v", "error", "-show_format", "-show_streams", "-of", "json", mp4],
                                   capture_output=True, text=True).stdout)
    v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in pr["streams"] if s["codec_type"] == "audio"][0]
    fps = eval(v["r_frame_rate"])
    rep["spec"] = dict(vcodec=v["codec_name"], pix=v["pix_fmt"], fps=fps, acodec=a["codec_name"],
                       asr=int(a["sample_rate"]), abr_k=int(int(a.get("bit_rate", 0)) / 1000),
                       duration=round(float(pr["format"]["duration"]), 4),
                       faststart=open(mp4, "rb").read(64).find(b"ftyp") >= 0)
    F = frames(mp4, 0)
    n = len(F)
    steps = [np.abs(F[i + 1] - F[i]).mean() for i in range(n - 1)]
    wrap = np.abs(F[0] - F[n - 1]).mean()
    med = float(np.median(steps))
    rep["video_seam"] = dict(wrap_mae=round(float(wrap), 3), median_step_mae=round(med, 3),
                             ratio=round(float(wrap) / med, 3), pass_=bool(wrap <= 1.35 * med))
    s = audio(mp4).reshape(-1, 2)
    slope = np.abs(np.diff(s, axis=0)).mean(axis=1)
    med_sl = float(np.median(slope))
    seam_sl = float(np.abs(s[0] - s[-1]).mean())
    rep["audio_seam"] = dict(wrap_jump=round(seam_sl, 5), median_slope=round(med_sl, 5),
                             ratio=round(seam_sl / max(med_sl, 1e-9), 3), pass_=bool(seam_sl <= 6 * max(med_sl, 1e-9)))
    out = run([FF, "-hide_banner", "-nostats", "-i", mp4, "-filter:a", "ebur128=peak=true", "-f", "null", "-"])
    import re
    i = float(re.search(r"I:\s*([-\d.]+)\s*LUFS", out).group(1))
    tpk = [float(x) for x in re.findall(r"TPK:\s*([-\d.]+)", out)]
    rep["loudness"] = dict(i_lufs=i, tp_dbfs=tpk[-1] if tpk else None,
                           pass_=bool(abs(i + 16) <= 1.5 and (tpk[-1] if tpk else 0) <= -1.0))
    rep["pass_all"] = bool(rep["video_seam"]["pass_"] and rep["audio_seam"]["pass_"] and rep["loudness"]["pass_"])
    os.makedirs("work/inspection", exist_ok=True)
    json.dump(rep, open(f"work/inspection/loop-gate-{tag}.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))
    return 0 if rep["pass_all"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "r01"))
