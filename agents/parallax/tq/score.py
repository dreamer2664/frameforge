#!/usr/bin/env python3
"""The score for 'cadence' - 15.000 s of original electronic bed.

Written for this film: a 120 BPM pulse (one beat = 0.5 s, the same grid the
picture is cut on) with a low sub, filtered bass, ticks, a warm pad for the
light section and a rising noise riser into the orange flash.  Every hit is
placed against a picture event, so the sound and the edit share one clock.

    python3 score.py --out work/audio/score.wav
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, lfilter

SR = 48000
DUR = 15.0
BPM = 120.0
BEAT = 60.0 / BPM


# --------------------------------------------------------------------------- #
# small synth toolbox
# --------------------------------------------------------------------------- #
def noise(n, rng):
    return rng.normal(0.0, 1.0, n)


def lowpass(x, cutoff, order=2, sr=SR):
    b, a = butter(order, cutoff / (sr * 0.5), btype="low")
    return lfilter(b, a, x)


def highpass(x, cutoff, order=2, sr=SR):
    b, a = butter(order, cutoff / (sr * 0.5), btype="high")
    return lfilter(b, a, x)


def sine(freq, n, sr=SR, phase=0.0):
    t = np.arange(n) / sr
    return np.sin(2 * math.pi * freq * t + phase)


def saw(freq, n, sr=SR, phase=0.0):
    t = np.arange(n) / sr
    p = (freq * t + phase) % 1.0
    return 2.0 * p - 1.0


def add_at(buf, x, pos):
    i = int(pos * SR)
    if i >= buf.size:
        return
    n = min(x.size, buf.size - i)
    buf[i:i + n] += x[:n]


def exp_env(n, decay, sr=SR):
    t = np.arange(n) / sr
    return np.exp(-t / decay)


def noise_ir(dur=1.9, seed=5, sr=SR):
    rng = np.random.default_rng(seed)
    n = int(dur * sr)
    ir = noise(n, rng) * exp_env(n, dur * 0.32, sr)
    ir[: int(0.012 * sr)] *= 0.4
    return ir


def convolve(x, ir):
    """Exact linear convolution by FFT (a python loop over the IR is far too slow)."""
    n = x.size
    m = ir.size
    size = 1
    while size < n + m - 1:
        size *= 2
    X = np.fft.rfft(x, size)
    H = np.fft.rfft(ir, size)
    return np.fft.irfft(X * H, size)[:n]


# --------------------------------------------------------------------------- #
# voices
# --------------------------------------------------------------------------- #
def kick(rng):
    n = int(0.34 * SR)
    t = np.arange(n) / SR
    f = 120.0 * np.exp(-t * 26.0) + 44.0
    body = np.sin(2 * math.pi * np.cumsum(f) / SR) * exp_env(n, 0.085)
    click = noise(n, rng) * exp_env(n, 0.004) * 0.35
    return lowpass(body + click, 2600, 1)


def hat(rng, dur=0.045, bright=9000.0, level=0.5):
    n = int(dur * SR)
    x = noise(n, rng) * exp_env(n, dur * 0.30)
    x = highpass(x, bright, 2)
    return x * level


def sub(freq, dur, level=1.0):
    n = int(dur * SR)
    x = sine(freq, n) * exp_env(n, dur * 0.55)
    return x * level


def bass(freq, dur, cutoff=520.0, level=0.5, seed=3):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = saw(freq, n) * 0.7 + saw(freq * 1.005, n) * 0.3
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / 0.006) * exp_env(n, dur * 0.42)
    x = lowpass(x, cutoff, 2) * env
    return x * level


def pad(freqs, dur, level=0.22, detune=0.004, seed=7):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for k in (-1, 1):
            out += sine(f * (1 + detune * k), n) * 0.5
    # slow swell
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7
    out = lowpass(out, 2400, 2) * env
    return out * level


def impact(dur=2.2, seed=13, level=1.0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 90.0 * np.exp(-t * 9.0) + 34.0
    boom = np.sin(2 * math.pi * np.cumsum(f) / SR) * exp_env(n, 0.30)
    air = noise(n, rng) * exp_env(n, 0.10) * 0.30
    air = highpass(air, 1400, 2)
    return (boom + air) * level


def riser(dur=1.2, seed=21, level=0.5):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = noise(n, rng)
    # crude sweeping band: multiply by a moving sine then low/high pass
    sweep = 0.5 + 0.5 * np.sin(2 * math.pi * (180 + 2400 * (t / dur) ** 2) * t)
    x = x * sweep
    x = highpass(x, 600, 1)
    env = (t / dur) ** 1.6
    return x * env * level


def bell(freq, dur, level=0.3, seed=31):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = (sine(freq, n) * 0.7 + sine(freq * 2.76, n) * 0.25 + sine(freq * 5.4, n) * 0.1)
    x *= exp_env(n, dur * 0.22)
    x += noise(n, rng) * exp_env(n, 0.01) * 0.1
    return x * level


# --------------------------------------------------------------------------- #
# arrangement
# --------------------------------------------------------------------------- #
def build() -> np.ndarray:
    rng = np.random.default_rng(101)
    n = int(DUR * SR)
    dry = np.zeros(n)
    wet = np.zeros(n)

    def put(x, pos, verb=0.22):
        add_at(dry, x, pos)
        if verb > 0:
            add_at(wet, x, pos)

    # --- picture events -------------------------------------------------- #
    hits = [
        0.45, 1.50, 2.02, 2.50, 2.96, 3.66, 4.20, 4.75, 5.25, 5.46,
        6.00, 6.50, 7.00, 7.36, 7.58, 8.50, 9.25, 9.92, 10.35, 11.12,
        11.50, 12.20, 12.60,
    ]

    # pulse: a soft kick on every beat of the film, stronger where the cut is
    t = 0.0
    while t < DUR - 0.05:
        accent = 0.95 if (abs(t * 2 - round(t * 2)) < 1e-6 and int(round(t * 2)) % 4 == 0) else 0.55
        if t < 1.9:
            accent *= 0.45
        if 3.6 < t < 5.5:
            accent *= 0.7
        if t > 12.4:
            accent *= max(0.0, 1.0 - (t - 12.4) / 1.6)
        if t > 13.9:
            accent = 0.0
        put(kick(rng) * 0.85 * accent, t, 0.16)
        put(hat(rng, 0.038, 9500, 0.20 * accent), t + BEAT / 2, 0.12)
        t += BEAT

    # sub line: A - A - F - G  (one bar each)
    bass_notes = [55.0, 55.0, 43.65, 49.0]
    for bar in range(7):
        base = bar * 2.0
        if base > DUR:
            break
        f = bass_notes[bar % 4]
        for k in range(4):
            pos = base + k * 0.5
            if pos > DUR - 0.2:
                break
            lvl = 0.42 if k in (0, 2) else 0.24
            put(bass(f, 0.46, 520 + 180 * (k == 0), lvl, seed=bar * 10 + k), pos, 0.18)

    # the low drone that holds the opening together
    d = 55.0
    drone = sine(d, n) * 0.10 + sine(d * 1.5, n) * 0.05
    env = np.clip(np.linspace(0.0, 1.0, n) / 3.0, 0, 1) * np.clip((DUR - np.arange(n) / SR) / 2.4, 0, 1)
    put(drone * env, 0.0, 0.30)

    # section hits
    for i, h in enumerate(hits):
        if h >= DUR:
            continue
        if h in (0.45, 3.66, 5.46, 7.36, 9.92, 11.12):
            put(impact(2.2, 13 + i, 0.85), h, 0.35)
        else:
            put(impact(0.9, 13 + i, 0.34), h, 0.28)

    # riser into the flash
    put(riser(1.30, 21, 0.42), 6.10, 0.3)
    put(riser(0.70, 23, 0.30), 7.36, 0.35)

    # pad for the light section
    put(pad([220.0, 261.63, 329.63, 392.0, 440.0], 4.6, 0.16, 0.005, 5), 7.60, 0.45)
    put(pad([220.0, 261.63, 329.63, 392.0, 440.0], 3.2, 0.13, 0.005, 5), 11.40, 0.5)
    put(bell(880.0, 2.4, 0.16, 31), 11.50, 0.6)
    put(bell(1318.5, 2.0, 0.10, 33), 12.05, 0.6)

    # arp under the app beat
    notes = [440.0, 523.25, 659.25, 523.25]
    for k in range(8):
        pos = 3.70 + k * 0.25
        put(bell(notes[k % 4], 0.6, 0.07, 40 + k), pos, 0.35)

    # a low swell under the closing fade
    sw = sine(41.2, n) * 0.10
    e = np.clip((np.arange(n) / SR - 12.2) / 1.2, 0, 1) * np.clip((DUR - np.arange(n) / SR) / 2.0, 0, 1)
    put(sw * e, 0.0, 0.4)

    # reverb
    ir = noise_ir(1.9, 5)
    ir = ir / (np.sqrt((ir ** 2).sum()) + 1e-9) * 0.055
    verb = convolve(wet, ir)
    mix = dry + verb

    # final fades
    fade_in = np.clip(np.arange(n) / (0.02 * SR), 0, 1)
    fade_out = np.clip((DUR - np.arange(n) / SR) / 1.6, 0, 1)
    mix *= fade_in * fade_out
    # soft limiter: the reference bed is dense and peak-controlled, not spiky
    mix = np.tanh(mix * 1.30) / math.tanh(1.30)
    return mix


def write_wav(path: Path, x: np.ndarray, sr: int = SR):
    path.parent.mkdir(parents=True, exist_ok=True)
    st = np.stack([x, x], axis=1)
    st = np.clip(st, -1.0, 1.0)
    data = (st * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


def measure(x: np.ndarray, sr: int = SR):
    peak = float(np.abs(x).max())
    rms = float(np.sqrt((x ** 2).mean()))
    return {"peak": peak, "rms": rms, "lufs_est": 20 * math.log10(rms + 1e-12) - 3.0}


FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")


def ffmpeg_loudness(path: Path):
    import subprocess
    out = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", str(path),
                          "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr.splitlines()
    k = max((i for i, l in enumerate(out) if l.strip() == "Summary:"), default=0)
    lufs = tp = None
    for line in out[k:]:
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "work" / "audio" / "score.wav"))
    ap.add_argument("--target-lufs", type=float, default=-16.0)
    ap.add_argument("--target-tp", type=float, default=-1.5)
    args = ap.parse_args()
    out = Path(args.out)
    x = build()
    write_wav(out, x)
    lufs, tp = ffmpeg_loudness(out)
    gain = 1.0
    if lufs is not None:
        gain = 10.0 ** ((args.target_lufs - lufs) / 20.0)
    x2 = x * gain
    write_wav(out, x2)
    lufs2, tp2 = ffmpeg_loudness(out)
    for _ in range(3):
        peak = float(np.abs(x2).max())
        if peak > 0.80:
            x2 *= 0.80 / peak
        write_wav(out, x2)
        lufs2, tp2 = ffmpeg_loudness(out)
        if lufs2 is None:
            break
        if abs(lufs2 - args.target_lufs) < 0.15:
            break
        g = 10.0 ** ((args.target_lufs - lufs2) / 20.0)
        if 0.9 < g < 1.1:
            break
        x2 = np.tanh(x2 * g * 1.25) / math.tanh(1.25)
    m = measure(x2)
    print(json.dumps({"out": str(out), "dur": len(x2) / SR, "gain_db": round(20 * math.log10(gain), 2),
                      "integrated_lufs": lufs2, "true_peak_dbtp": tp2, **m}, indent=2))


if __name__ == "__main__":
    main()
