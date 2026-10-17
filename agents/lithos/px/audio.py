#!/usr/bin/env python3
"""THE LONG LIGHT — score synthesiser (lithos).

Everything here is synthesised: no samples, no stock loops, no third-party
recordings. Cue times are DERIVED from the picture's geometry:

  - dial ticks: the exact times the gnomon shadow's edge crosses each
    inscribed station (scene.dial_geometry(), computed from the sun keys);
  - colonnade ticks: the times the camera passes each pier (sampled from the
    camera keys);
  - the terminus landing: the moment the shadow tip reaches "ideas, in motion."

If the picture is retimed, re-derive this score from the storyboard.

Usage:
  python3 audio.py --out work/audio
"""
from __future__ import annotations

import argparse
import math
import subprocess
import wave
from pathlib import Path

import numpy as np

import scene as S

HERE = Path(__file__).resolve().parent
SR = 48000
FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")
FFPROBE = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffprobe")


# ------------------------------------------------------------------ helpers
def write_wav24(path, L, R):
    """Hand-rolled 24-bit stereo WAV (the stdlib wave module writes 24-bit wrong)."""
    L = np.clip(L, -1.0, 1.0)
    R = np.clip(R, -1.0, 1.0)
    n = len(L)
    il = (L * 8388607.0).astype(np.int32)
    ir = (R * 8388607.0).astype(np.int32)
    inter = np.empty((n, 2), dtype=np.int32)
    inter[:, 0] = il
    inter[:, 1] = ir
    raw4 = inter.tobytes()
    # pack true 24-bit: the low 3 bytes of each int32 (sign-safe for our range)
    b = np.frombuffer(raw4, dtype=np.uint8).reshape(-1, 4)[:, :3].tobytes()
    data_rate = SR * 2 * 3
    hdr = b"RIFF" + (36 + len(b)).to_bytes(4, "little") + b"WAVEfmt " + \
        (16).to_bytes(4, "little") + (1).to_bytes(2, "little") + (2).to_bytes(2, "little") + \
        SR.to_bytes(4, "little") + data_rate.to_bytes(4, "little") + (6).to_bytes(2, "little") + \
        (24).to_bytes(2, "little") + b"data" + len(b).to_bytes(4, "little")
    Path(path).write_bytes(hdr + b)


def read_wav_f32(path):
    """Decode any wav to float32 stereo via ffmpeg (never parse 24-bit by hand)."""
    out = subprocess.check_output([
        FFMPEG, "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"])
    x = np.frombuffer(out, dtype=np.float32).reshape(-1, 2)
    return x[:, 0].copy(), x[:, 1].copy()


def noise(n, seed, lo=None, hi=None):
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n).astype(np.float64)
    if lo or hi:
        X = np.fft.rfft(x)
        f = np.fft.rfftfreq(n, 1 / SR)
        if lo:
            X[f < lo] = 0
        if hi:
            X[f > hi] = 0
        x = np.fft.irfft(X, n)
    return x / max(np.abs(x).max(), 1e-9)


def env_ad(n, attack, decay, sr=SR):
    a = int(attack * sr)
    d = int(decay * sr)
    e = np.zeros(n)
    a = min(a, n)
    e[:a] = np.linspace(0, 1, a) ** 1.5
    rest = n - a
    if rest > 0:
        d = min(d, rest)
        e[a:a + d] = np.exp(-np.linspace(0, 5, d))
    return e


def place(buf, sig, t0, gain=1.0, pan=0.0):
    """pan: -1 left .. +1 right"""
    i = int(t0 * SR)
    n = len(sig)
    if i < 0:
        sig = sig[-i:]
        n = len(sig)
        i = 0
    j = min(i + n, buf.shape[0])
    m = j - i
    if m <= 0:
        return
    gl = gain * math.sqrt(0.5 * (1 - pan))
    gr = gain * math.sqrt(0.5 * (1 + pan))
    buf[i:j, 0] += sig[:m] * gl
    buf[i:j, 1] += sig[:m] * gr


def hall_ir(tail=1.1, seed=5):
    """Open-air court impulse: a few early reflections + a short warm tail."""
    n = int(tail * SR)
    ir = np.zeros((n, 2))
    rng = np.random.default_rng(seed)
    # early reflections (floor + parapet + piers)
    for dt, g, pan in [(0.017, 0.42, -0.25), (0.023, 0.38, 0.30), (0.031, 0.30, -0.55),
                       (0.043, 0.26, 0.55), (0.061, 0.20, 0.0)]:
        i = int(dt * SR)
        ir[i, 0] += g * math.sqrt(0.5 * (1 - pan))
        ir[i, 1] += g * math.sqrt(0.5 * (1 + pan))
    # diffuse tail
    t = np.arange(n) / SR
    decay = np.exp(-t * 4.2) * (1 - np.exp(-t * 260))
    tailn = rng.normal(0, 1, (n, 2)) * decay[:, None]
    # gentle low-pass on the tail
    X = np.fft.rfft(tailn, axis=0)
    f = np.fft.rfftfreq(n, 1 / SR)
    X[f > 4200] *= 0.25
    tailn = np.fft.irfft(X, n, axis=0)
    ir += tailn * 0.055
    ir[0, :] += 0.62  # direct
    return ir / np.abs(ir[0]).max()  # normalise on the DIRECT tap, not the tail


def convolve(buf, ir):
    n = buf.shape[0]
    m = n + len(ir) - 1
    nf = 1 << (m - 1).bit_length()
    out = np.zeros((n, 2))
    for c in (0, 1):
        y = np.fft.irfft(np.fft.rfft(buf[:, c], nf) * np.fft.rfft(ir[:, c], nf), nf)
        out[:, c] = y[:n]
    return out


def convolve_circular(buf, ir, period):
    """Circular convolution on `period` samples — keeps a loop periodic."""
    out = np.zeros_like(buf)
    n = period
    nf = n  # the transform length MUST equal the loop length (periodicity)
    for c in (0, 1):
        seg = np.zeros(nf)
        seg[:n] = buf[:n, c]
        h = np.zeros(nf)
        h[:len(ir)] = ir[:nf, c] if len(ir) > nf else ir[:, c]
        y = np.fft.irfft(np.fft.rfft(seg) * np.fft.rfft(h), nf)
        out[:n, c] = y[:n]
    return out


def soft_limit(x, ceiling=0.32):
    return np.tanh(x / ceiling) * ceiling


def measure_lufs(path):
    out = subprocess.check_output([FFMPEG, "-hide_banner", "-i", str(path),
                                   "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
                                  stderr=subprocess.STDOUT).decode()
    i = out.rfind("Summary:")
    chunk = out[i:]
    lufs = None
    tp = None
    for line in chunk.splitlines():
        if "I:" in line and "LUFS" in line and lufs is None:
            try:
                lufs = float(line.split("I:")[1].split("LUFS")[0].strip())
            except Exception:
                pass
        if "Peak:" in line and tp is None:
            try:
                tp = float(line.split("Peak:")[1].split("dBFS")[0].strip())
            except Exception:
                pass
    return lufs, tp


# ------------------------------------------------------- picture-derived cues
def cue_times():
    """Every hit time in the score, computed from the storyboard geometry."""
    dial = S.dial_geometry()
    station_ts = [d["t"] for d in dial[:-1]]
    terminus_t = dial[-1]["t"]
    # colonnade ticks: camera x(t) crossing each pier x during the walk
    keys = S.STORY["camera"]["keys"]
    pier_ts = []
    for px in S.STORY["world"]["colonnade"]["x"]:
        if px > 0:
            continue
        prev_x = None
        for i in range(800):
            t = 8.0 + (17.0 - 8.0) * i / 799
            k = S.sample_keys(keys, t, ["eye"])
            x = float(k["eye"][0])
            if prev_x is not None and prev_x < px <= x:
                pier_ts.append(round(t, 3))
                break
            if prev_x is not None and prev_x > px >= x:
                pier_ts.append(round(t, 3))
                break
            prev_x = x
    return {"stations": station_ts, "terminus": terminus_t,
            "piers": sorted(pier_ts), "exit": 3.55, "vault_blade": 2.15}


# ------------------------------------------------------------------- voices
def tick(seed, tone=1450.0, dur=0.5, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * math.pi * tone * t) * np.exp(-t * 22)
    body += 0.55 * np.sin(2 * math.pi * tone * 1.48 * t) * np.exp(-t * 30)
    nz = noise(n, seed, lo=900, hi=6500) * np.exp(-t * 42) * 0.5 * bright
    return (body * 0.55 + nz) * env_ad(n, 0.001, dur)


def whoosh(dur=1.2, seed=9, rise=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    nz = noise(n, seed, lo=180, hi=2400)
    e = (t / dur) ** 2.2 if rise else (1 - t / dur) ** 1.6
    return nz * e


def pad_chord(freqs, dur, attack=1.2, release=2.0, seed=1, detune=0.004):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k, f in enumerate(freqs):
        for d in (-detune, 0.0, detune):
            ph = (k * 1.7 + d * 100) % (2 * math.pi)
            x += np.sin(2 * math.pi * f * (1 + d) * t + ph) / len(freqs)
        x += 0.22 * np.sin(2 * math.pi * 2 * f * t + k) / len(freqs)
    e = np.minimum(1.0, t / attack) * np.exp(-np.maximum(0, t - (dur - release)) / (release / 3))
    return x * e * 0.30


def sub_pulse(dur=1.6, f0=62.0, f1=41.0, seed=3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 2.2)
    ph = 2 * math.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 1.35)


# -------------------------------------------------------------------- hero
def build_hero():
    st = S.STORY
    dur = st["format"]["duration_seconds"]
    n = int(dur * SR)
    buf = np.zeros((n, 2))
    cues = cue_times()
    print("cue times:", cues, flush=True)

    # air bed: wind + rumble, following the light
    air = noise(n, 21, lo=220, hi=1500) * 0.030
    t = np.arange(n) / SR
    air *= (0.75 + 0.25 * np.sin(2 * math.pi * t / 17.0))
    rumble = noise(n, 22, lo=28, hi=90) * 0.055
    buf[:, 0] += air * 0.9 + rumble
    buf[:, 1] += air * 1.1 + rumble

    # the light's drone: a warm open fifth that grows with the sun
    drone = pad_chord([110.0, 164.8, 220.0, 329.6], dur, attack=3.5, release=6.0)
    swell = 0.35 + 0.65 * np.clip((t - 2.0) / 26.0, 0, 1) ** 1.4
    drone *= swell
    place(buf, drone, 0.0, gain=0.42, pan=-0.12)
    place(buf, drone * 0.85, 0.012, gain=0.36, pan=0.16)

    # vault: the blade of sun sweeping the C's interior
    place(buf, whoosh(1.9, seed=31, rise=True), 0.9, gain=0.16)
    place(buf, sub_pulse(2.2, 78, 52), 1.9, gain=0.30)

    # exit through the mouth of the C
    place(buf, whoosh(1.5, seed=32, rise=True), cues["exit"] - 0.75, gain=0.30)
    place(buf, sub_pulse(2.6, 92, 47), cues["exit"], gain=0.42)
    place(buf, tick(41, tone=980.0, dur=0.9, bright=0.7), cues["exit"] + 0.05, gain=0.16)

    # colonnade: dry ticks as the piers pass (derived from camera x(t))
    for i, pt in enumerate(cues["piers"]):
        place(buf, tick(50 + i, tone=1180 + 90 * i, dur=0.42, bright=0.8), pt,
              gain=0.15, pan=-0.35 + 0.25 * i)

    # the dial: the shadow's edge crosses each station (exact geometry)
    for i, st_t in enumerate(cues["stations"]):
        place(buf, tick(60 + i, tone=1320 + 120 * i, dur=0.55), st_t,
              gain=0.30, pan=-0.30 + 0.20 * i)
        place(buf, sub_pulse(1.1, 70 + 4 * i, 48), st_t, gain=0.16)

    # the sentence completes
    place(buf, sub_pulse(3.2, 84, 44), cues["terminus"], gain=0.50)
    place(buf, pad_chord([146.8, 220.0, 277.2, 369.9], 7.0, attack=1.6, release=3.0),
          cues["terminus"] - 0.4, gain=0.46, pan=0.05)
    place(buf, tick(70, tone=1760.0, dur=1.1, bright=1.2), cues["terminus"], gain=0.14)
    shimmer = noise(n, 77, lo=3200, hi=9000) * np.clip((t - cues["terminus"]) / 2.0, 0, 1) * \
        np.exp(-np.maximum(0, t - cues["terminus"] - 2.0) / 3.0) * 0.045
    buf[:, 0] += shimmer
    buf[:, 1] += shimmer * 0.9

    # the close: a warm sustained third
    place(buf, pad_chord([220.0, 277.2, 329.6], 9.0, attack=2.5, release=5.0), 33.0,
          gain=0.34, pan=-0.08)

    # the courtyard
    buf = convolve(buf, hall_ir())
    return buf, cues


# -------------------------------------------------------------------- loop
def build_loop():
    st = S.STORY
    T = st["loop"]["duration_seconds"]
    n = int(T * SR)
    t = np.arange(n) / SR
    a = 2 * math.pi * t / T
    buf = np.zeros((n, 2))

    # periodic air: only integer cycles over T
    for k, (f, g) in enumerate([(1 / T, 0.028), (2 / T, 0.018), (3 / T, 0.010)]):
        buf[:, 0] += np.sin(2 * math.pi * f * t * 1 + k) * g
        buf[:, 1] += np.sin(2 * math.pi * f * t * 1 + k + 1.1) * g
    # irfft(rfft(x, n), n) output is exactly periodic over n — no blending needed
    air = noise(n, 23, lo=220, hi=1400) * 0.065
    air_hi = noise(n, 24, lo=800, hi=2600) * 0.028
    buf[:, 0] += air + air_hi
    buf[:, 1] += air * 1.05 + air_hi * 0.92

    # the shadow's metronome: two soft ticks per period (transients away from 0)
    for tt, tone, pan in [(0.6, 1240.0, -0.3), (5.4, 1480.0, 0.3)]:
        sig = tick(80 + int(tt * 10), tone=tone, dur=0.8)
        place(buf, sig, tt, gain=0.055, pan=pan)

    # wrapped sub pulse at 3.0 and 7.8
    for tt, f0 in [(3.0, 66.0), (7.8, 58.0)]:
        sig = sub_pulse(1.2, f0, 44.0)
        place(buf, sig, tt, gain=0.045)

    # warm pad on the loop's period (integer harmonics)
    for k, (h, g) in enumerate([(2, 0.095), (3, 0.066), (4, 0.046), (6, 0.028)]):
        buf[:, 0] += np.sin(2 * math.pi * h * t / T + k * 1.3) * g
        buf[:, 1] += np.sin(2 * math.pi * h * t / T + k * 1.3 + 0.4) * g

    ir = hall_ir()
    buf = convolve_circular(buf, ir, n)
    return buf


# ------------------------------------------------------------------- main
def normalise_and_encode(buf, wav_path, m4a_path, target_lufs=-16.0, peak_ceiling=-2.0):
    wav_path = Path(wav_path)
    m4a_path = Path(m4a_path)
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    # soft limit, then at most 3 STATIC gain passes (one gain applied per pass,
    # never re-normalising the peak silently — the handoff's audio lesson)
    buf = soft_limit(buf, ceiling=0.32)
    lufs, tp = None, None
    total_gain_db = 0.0
    for pass_i in range(3):
        write_wav24(wav_path, buf[:, 0], buf[:, 1])
        encode(wav_path, m4a_path)
        lufs, tp = measure_lufs(m4a_path)
        print(f"pass {pass_i}: {lufs} LUFS, true peak {tp} dBTP", flush=True)
        if abs(lufs - target_lufs) <= 0.4 and tp <= peak_ceiling:
            break
        gain_db = target_lufs - lufs
        if tp + gain_db > peak_ceiling:
            gain_db = peak_ceiling - tp
        if abs(gain_db) < 0.05:
            break
        total_gain_db += gain_db
        gain = 10 ** (gain_db / 20.0)
        print(f"  static gain {gain_db:+.2f} dB (cumulative {total_gain_db:+.2f} dB)", flush=True)
        buf = buf * gain
    print(f"final: {lufs} LUFS, true peak {tp} dBTP", flush=True)
    return lufs, tp


def encode(wav_path, m4a_path):
    subprocess.check_call([FFMPEG, "-y", "-v", "error", "-i", str(wav_path),
                           "-c:a", "aac", "-b:a", "224k", "-ar", "48000",
                           "-movflags", "+faststart", str(m4a_path)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="work/audio")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    hero, cues = build_hero()
    print("building hero score...", flush=True)
    normalise_and_encode(hero, out / "hero.wav", out / "hero.m4a")

    print("building loop score...", flush=True)
    loop = build_loop()
    normalise_and_encode(loop, out / "loop.wav", out / "loop.m4a")

    # seam measurement on the source (sample-exact)
    L, R = read_wav_f32(out / "loop.wav")
    step = float(np.hypot(L[0] - L[-1], R[0] - R[-1]))
    inner = float(np.mean(np.hypot(np.diff(L), np.diff(R))))
    print(f"loop seam step {step:.6f} vs interior mean step {inner:.6f} "
          f"(ratio {step / max(inner, 1e-9):.3f})")
    (out / "cues.json").write_text(
        __import__("json").dumps(cues, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
