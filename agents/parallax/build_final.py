"""parallax final mux: loudness-normalise procedural WAVs, encode hero+loop MP4s to master spec.

Usage: python3 agents_build/build_final.py
Reads  work/audio/hero-r01.wav, work/audio/loop-r01.wav, work/hero_r01/f*.png, work/loop_r01/f*.png
Writes work/audio/hero-final.wav, work/audio/loop-final.wav,
       work/renders/hero-r01.mp4, work/renders/loop-r01.mp4  (+ .json probe receipts)
"""
import glob, json, os, subprocess, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = os.path.expanduser("~/.cache/frameforge/bin/ffmpeg")
FP = os.path.expanduser("~/.cache/frameforge/bin/ffprobe")
TARGET_I = -16.0
TARGET_TP = -1.0


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{cmd[:4]} failed: {r.stderr[-1500:]}")
    return r.stdout + r.stderr


def read_wav(p):
    out = run([FF, "-hide_banner", "-loglevel", "error", "-i", p, "-f", "s16le", "-acodec", "pcm_s16le", "-"])
    a = np.frombuffer(out.encode("latin1") if isinstance(out, str) else out, dtype=np.int16)
    return a


def read_wav_bytes(p):
    r = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", p, "-f", "s16le", "-acodec", "pcm_s16le", "-"],
                       capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])
    return np.frombuffer(r.stdout, dtype=np.int16)


def write_wav(path, x, sr=48000):
    x = np.clip(x, -1.0, 1.0)
    xi = (x * 32767.0).astype("<i2")
    if xi.ndim == 1:
        xi = xi[:, None]
    with open(path + ".raw", "wb") as f:
        f.write(xi.tobytes())
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(sr), "-ac", str(xi.shape[1]),
         "-i", path + ".raw", path])
    os.remove(path + ".raw")


def measure(path):
    out = run([FF, "-hide_banner", "-nostats", "-i", path, "-filter:a", "ebur128=peak=true", "-f", "null", "-"])
    i = tp = None
    for ln in out.splitlines():
        ln = ln.strip()
        if ln.startswith("I:"):
            i = float(ln.split()[1])
        if ln.startswith("Peak:") or "TPK:" in ln and ln.startswith("TPK") is False and "TPK:" in ln:
            pass
    # true peak from the summary block
    import re
    m = re.search(r"True peak:\s*\n\s*Peak:\s*([-\d.]+)\s*dBFS", out)
    if m:
        tp = float(m.group(1))
    else:
        m2 = re.findall(r"TPK:\s*([-\d.]+)", out)
        tp = float(m2[-1]) if m2 else None
    return i, tp


def normalise(src, dst):
    i, tp = measure(src)
    gain = 10 ** ((TARGET_I - i) / 20.0)
    x = read_wav_bytes(src).astype(np.float64) / 32768.0
    x = x.reshape(-1, 2)
    x = x * gain
    peak = np.abs(x).max()
    tp_lin = 10 ** (TARGET_TP / 20.0)
    if peak > tp_lin:
        x = x * (tp_lin / peak)
    write_wav(dst, x)
    i2, tp2 = measure(dst)
    return dict(src_i=i, src_tp=tp, gain_db=20 * np.log10(gain), out_i=i2, out_tp=tp2)


def encode_video(frames_glob, fps, wav, out, duration=None):
    frames = sorted(glob.glob(frames_glob))
    cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", "-framerate", str(fps),
           "-start_number", str(int(os.path.basename(frames[0])[1:6])),
           "-i", os.path.dirname(frames[0]) + "/f%05d.png", "-i", wav,
           "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    if duration:
        cmd += ["-t", str(duration)]
    cmd += ["-movflags", "+faststart", out]
    run(cmd)


def probe(out):
    r = subprocess.run([FP, "-v", "error", "-show_format", "-show_streams", "-of", "json", out],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    v = [s for s in d["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in d["streams"] if s["codec_type"] == "audio"][0]
    return dict(sha256=None, duration=float(d["format"]["duration"]), size=int(d["format"]["size"]),
                vcodec=v["codec_name"], pix=v["pix_fmt"], w=v["width"], h=v["height"],
                fps=eval(v["r_frame_rate"]), acodec=a["codec_name"], asr=int(a["sample_rate"]),
                abr=int(a.get("bit_rate", 0)))


if __name__ == "__main__":
    rec = {}
    rec["hero_audio"] = normalise(f"{ROOT}/work/audio/hero-r01.wav", f"{ROOT}/work/audio/hero-final.wav")
    rec["loop_audio"] = normalise(f"{ROOT}/work/audio/loop-r01.wav", f"{ROOT}/work/audio/loop-final.wav")
    if glob.glob(f"{ROOT}/work/hero_r01/f*.png"):
        encode_video(f"{ROOT}/work/hero_r01/f*.png", 24, f"{ROOT}/work/audio/hero-final.wav",
                     f"{ROOT}/work/renders/hero-r01.mp4", duration=44.5)
        rec["hero"] = probe(f"{ROOT}/work/renders/hero-r01.mp4")
    if glob.glob(f"{ROOT}/work/loop_r01/f*.png"):
        encode_video(f"{ROOT}/work/loop_r01/f*.png", 25, f"{ROOT}/work/audio/loop-final.wav",
                     f"{ROOT}/work/renders/loop-r01.mp4", duration=10.24)
        rec["loop"] = probe(f"{ROOT}/work/renders/loop-r01.mp4")
    json.dump(rec, open(f"{ROOT}/work/build_receipt.json", "w"), indent=1)
    print(json.dumps(rec, indent=1))
