#!/usr/bin/env python3
"""The score for 'LAST SHIFT - WARD 7' - 70.000 s of original night-shift dread.

No voice: the story is carried by the picture and the caption track, so this is
a pure music bed, written against the film's own clock.

Tempo 80 BPM (beat 0.75 s, bar 3.0 s).  The bed is a cold room tone with a
slow sub pulse, a clock tick that starts at 03:00 and never stops, and a
hospital-metal vocabulary: lift doors, lift arrival, trolley squeak, a door
handle, footsteps, and one white-noise hit on the flash.

Structure
    00.0 - 03.5  room tone, sub swell, clock starts
    03.5 - 19.0  plan + rules: pulse, ticks, low pad
    19.0 - 26.6  lift lobby: metallic slide at 22.4, arrival clunk at 23.3
    26.6 - 34.2  shift log: tremolo, a wrong bell at 29.8
    34.2 - 41.6  forty-one doors: a sweep of clicks, riser
    41.6 - 57.6  corridor: heartbeat, trolley, footsteps, breath, impact
    57.8 - 70.0  end card: resolving drone, final bell, tail out

    python3 score.py --out work/audio/score.wav
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, lfilter

SR = 48000
DUR = 70.0
BPM = 80.0
BEAT = 60.0 / BPM
BAR = BEAT * 4


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


def bandpass(x, lo, hi, order=2, sr=SR):
    b, a = butter(order, [lo / (sr * 0.5), hi / (sr * 0.5)], btype="band")
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


def noise_ir(dur=2.4, seed=5, sr=SR):
    rng = np.random.default_rng(seed)
    n = int(dur * sr)
    ir = noise(n, rng) * exp_env(n, dur * 0.30, sr)
    ir[: int(0.014 * sr)] *= 0.35
    return ir


def convolve(x, ir):
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
def pulse(rng, level=1.0, decay=0.09, f0=120.0):
    n = int(0.36 * SR)
    t = np.arange(n) / SR
    f = f0 * np.exp(-t * 24.0) + 41.0
    body = np.sin(2 * math.pi * np.cumsum(f) / SR) * exp_env(n, decay)
    click = noise(n, rng) * exp_env(n, 0.004) * 0.28
    return lowpass(body + click, 2200, 1) * level


def tick(level=0.5, dur=0.028):
    """A dry mechanical clock tick."""
    n = int(dur * SR)
    x = noise(n, np.random.default_rng(77)) * exp_env(n, 0.006)
    x = highpass(x, 2600, 2) * level
    return x


def sub(freq, dur, level=1.0, sr=SR):
    n = int(dur * sr)
    x = sine(freq, n, sr) * exp_env(n, dur * 0.55, sr)
    return x * level


def bass(freq, dur, cutoff=420.0, level=0.5, seed=3):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = saw(freq, n) * 0.7 + saw(freq * 1.004, n) * 0.3
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / 0.008) * exp_env(n, dur * 0.40)
    return lowpass(x, cutoff, 2) * env * level


def pad(freqs, dur, level=0.2, detune=0.0035, seed=7, cutoff=1900.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for k in (-1, 1):
            out += sine(f * (1 + detune * k), n) * 0.5
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.8
    return lowpass(out, cutoff, 2) * env * level


def impact(dur=2.4, seed=13, level=1.0, f0=95.0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * np.exp(-t * 8.0) + 33.0
    boom = np.sin(2 * math.pi * np.cumsum(f) / SR) * exp_env(n, 0.32)
    air = highpass(noise(n, rng) * exp_env(n, 0.09), 1500, 2) * 0.30
    return (boom + air) * level


def riser(dur=1.4, seed=21, level=0.5, f_lo=200.0, f_hi=3200.0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = noise(n, rng)
    sweep = 0.5 + 0.5 * np.sin(2 * math.pi * (f_lo + (f_hi - f_lo) * (t / dur) ** 2) * t)
    x = highpass(x, 500, 1) * sweep
    return x * (t / dur) ** 1.7 * level


def bell(freq, dur, level=0.3, seed=31):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = sine(freq, n) * 0.7 + sine(freq * 2.76, n) * 0.24 + sine(freq * 5.40, n) * 0.09
    x *= exp_env(n, dur * 0.20)
    x += noise(n, rng) * exp_env(n, 0.008) * 0.09
    return x * level


def metal(dur=1.1, level=0.5, seed=41, lo=900.0, hi=5200.0, tilt=1.0):
    """A metal scrape / lift-door slide."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = noise(n, rng)
    x = bandpass(x, lo, hi, 2)
    env = np.clip(t / (dur * 0.35), 0, 1) * exp_env(n, dur * 0.5)
    return x * env * level * (0.5 + tilt * t / dur)


def clunk(dur=0.9, level=1.0, seed=51):
    """A lift car arriving: a metal hit with a short ring."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 150.0 * np.exp(-t * 16.0) + 48.0
    body = np.sin(2 * math.pi * np.cumsum(f) / SR) * exp_env(n, 0.10)
    ring = (sine(2140.0, n) * 0.5 + sine(3170.0, n) * 0.3) * exp_env(n, 0.16)
    air = highpass(noise(n, rng) * exp_env(n, 0.006), 2200, 2) * 0.22
    return (body + ring + air) * level


def squeak(dur=1.5, level=0.5, seed=61):
    """A linen trolley wheel: a narrow moving band."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = noise(n, rng)
    f = 1500 + 700 * np.sin(2 * math.pi * 1.7 * t)
    mod = 0.5 + 0.5 * np.sin(2 * np.pi * f * t)
    x = bandpass(x * mod, 1100, 4200, 2)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.4
    return x * env * level


def step(level=0.6, seed=71, low=0.0):
    """One footstep on a hard floor."""
    rng = np.random.default_rng(seed)
    n = int(0.20 * SR)
    t = np.arange(n) / SR
    f = 95.0 * np.exp(-t * 30.0) + 52.0
    body = np.sin(2 * math.pi * np.cumsum(f) / SR) * exp_env(n, 0.045)
    grit = highpass(noise(n, rng) * exp_env(n, 0.010), 1800, 2) * 0.18
    return (body + grit) * level * (1.0 - low)


def breath(dur=2.4, level=0.5, seed=81):
    """Something exhaling in the dark."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = noise(n, rng)
    x = bandpass(x, 300, 2400, 2)
    env = np.clip(np.sin(np.pi * np.clip(t / dur, 0, 1)), 0, 1) ** 2.2
    return x * env * level


# --------------------------------------------------------------------------- #
# arrangement
# --------------------------------------------------------------------------- #
def build() -> np.ndarray:
    rng = np.random.default_rng(707)
    n = int(DUR * SR)
    dry = np.zeros(n)
    wet = np.zeros(n)

    def put(x, pos, verb=0.22):
        add_at(dry, x, pos)
        if verb > 0:
            add_at(wet, x, pos)

    # --- room tone: the building breathing -------------------------------- #
    room = lowpass(noise(n, rng), 700, 2) * 0.045
    room += sine(51.0, n) * 0.030 + sine(76.5, n) * 0.012
    room += sine(99.0, n) * 0.006
    put(room, 0.0, 0.25)

    # --- the clock: one tick per second, from 3.0 s to the end ------------- #
    for k in range(int(DUR) - 3):
        pos = 3.0 + k
        lvl = 0.16 + 0.05 * math.sin(k * 0.7)
        put(tick(lvl), pos, 0.18)

    # --- the pulse: a slow sub, only where the film is alive ---------------- #
    t = 0.0
    while t < DUR - 0.05:
        if t >= 3.2:
            lvl = 0.20
            if 19.0 <= t < 26.6:
                lvl = 0.26
            if 41.6 <= t < 57.6:
                lvl = 0.34
            if t >= 58.0:
                lvl = max(0.0, 0.20 - (t - 58.0) / 12.0)
            put(pulse(rng, lvl * 0.55), t, 0.14)
        t += BEAT * 2

    # --- the low drone that holds the night together ----------------------- #
    drone = sine(36.7, n) * 0.085 + sine(55.0, n) * 0.035 + sine(73.4, n) * 0.018
    env = np.clip(np.arange(n) / SR / 4.0, 0, 1) * np.clip((DUR - np.arange(n) / SR) / 3.0, 0, 1)
    put(drone * env, 0.0, 0.32)

    # --- 03.5 - 19.0: the plan and the rules ------------------------------- #
    # a slow minor figure, one bar per 3 s, entering under the rules
    for bar, base in enumerate(np.arange(3.6, 19.0, BAR)):
        f = [55.0, 55.0, 49.0, 43.65][bar % 4]
        put(bass(f, 1.35, 380, 0.26, seed=bar), base, 0.16)
    put(pad([220.0, 261.63, 329.63, 392.0], 9.0, 0.085, 0.003, 3, 1500), 7.4, 0.5)
    put(pad([174.61, 220.0, 261.63], 6.0, 0.075, 0.003, 4, 1400), 12.4, 0.5)
    put(bell(659.25, 2.2, 0.055, 31), 6.9, 0.6)

    # --- 19.0 - 26.6: the lift --------------------------------------------- #
    for bar, base in enumerate(np.arange(19.0, 26.0, BAR)):
        f = [43.65, 43.65, 41.2, 38.89][bar % 4]
        put(bass(f, 1.35, 320, 0.30, seed=40 + bar), base, 0.16)
    put(metal(1.25, 0.34, 41, 700, 4200, 1.2), 22.35, 0.30)      # doors slide
    put(clunk(1.10, 0.60, 51), 23.28, 0.38)                        # car arrives
    put(bell(311.13, 3.0, 0.075, 33), 23.30, 0.65)                 # the wrong note
    put(pad([110.0, 146.83, 155.56], 7.0, 0.07, 0.004, 9, 1200), 19.2, 0.5)

    # --- 26.6 - 34.2: the shift log ---------------------------------------- #
    for bar, base in enumerate(np.arange(26.8, 33.8, BAR)):
        f = [41.2, 41.2, 38.89, 41.2][bar % 4]
        put(bass(f, 1.25, 300, 0.24, seed=60 + bar), base, 0.18)
    # a thin tremolo, like a fluorescent tube that will not settle
    trem = 0.5 + 0.5 * np.sin(2 * math.pi * 5.4 * np.arange(n) / SR)
    put(lowpass(noise(n, rng), 900, 2) * trem * 0.030, 27.0, 0.3)
    put(bell(233.08, 3.4, 0.085, 35), 29.75, 0.7)                  # the wrong bell
    put(impact(1.6, 71, 0.30), 30.4, 0.35)

    # --- 34.2 - 41.6: forty-one doors open --------------------------------- #
    for i in range(41):
        pos = 34.55 + i * 0.115
        lvl = 0.09 + 0.05 * (i / 41.0)
        put(tick(lvl, 0.020), pos, 0.45)
    put(riser(3.2, 21, 0.30, 180, 2600), 34.3, 0.35)
    put(pad([55.0, 58.27, 82.41], 7.0, 0.09, 0.005, 11, 1400), 34.5, 0.5)
    put(impact(2.0, 81, 0.34), 40.9, 0.40)

    # --- 41.6 - 57.6: the corridor ----------------------------------------- #
    # heartbeat: two thumps per bar
    t = 41.8
    while t < 57.4:
        put(sub(41.0, 0.30, 0.42), t, 0.18)
        put(sub(38.0, 0.26, 0.26), t + 0.30, 0.18)
        t += 1.10
    put(squeak(2.6, 0.30, 61), 42.2, 0.35)
    put(squeak(1.9, 0.20, 62), 45.4, 0.35)
    for i in range(7):                                             # footsteps
        put(step(0.30 - i * 0.02, 71 + i), 48.35 + i * 0.62, 0.30)
    put(breath(2.6, 0.24, 81), 50.6, 0.4)
    put(impact(2.6, 91, 0.42, 85.0), 53.15, 0.45)                 # something ran
    put(riser(2.0, 23, 0.42, 300, 5200), 53.3, 0.35)
    put(impact(3.2, 101, 0.85, 70.0), 55.28, 0.5)                # the flash
    put(metal(1.6, 0.26, 43, 500, 3600, 0.4), 55.0, 0.35)
    put(pad([110.0, 116.54, 174.61], 12.0, 0.075, 0.006, 13, 1100), 42.0, 0.55)

    # --- 57.8 - 70.0: the end card ------------------------------------------ #
    put(pad([87.31, 130.81, 174.61], 9.0, 0.085, 0.003, 15, 1500), 58.4, 0.6)
    put(bell(523.25, 3.2, 0.085, 37), 60.2, 0.65)
    put(bell(392.00, 3.6, 0.070, 39), 61.6, 0.65)
    put(impact(2.6, 111, 0.42, 62.0), 64.6, 0.45)                # rule four lands
    put(bell(261.63, 4.0, 0.10, 43), 65.0, 0.7)
    tail = np.clip((DUR - np.arange(n) / SR) / 2.6, 0, 1)
    put(sine(36.7, n) * 0.10 * tail, 0.0, 0.4)

    # --- reverb -------------------------------------------------------------- #
    ir = noise_ir(2.4, 5)
    ir = ir / (np.sqrt((ir ** 2).sum()) + 1e-9) * 0.05
    mix = dry + convolve(wet, ir)

    # bus compression: the bed has to sit under a voice-free mix without
    # spiking, so the crest is tamed before the loudness pass
    a = math.exp(-1.0 / (0.06 * SR))
    env = lfilter([1 - a], [1, -a], np.abs(mix))
    thr = 0.30
    over = np.maximum(0.0, env - thr)
    mix = mix * (1.0 - 0.65 * np.minimum(1.0, over / thr))

    fade_in = np.clip(np.arange(n) / (0.04 * SR), 0, 1)
    fade_out = np.clip((DUR - np.arange(n) / SR) / 1.8, 0, 1)
    mix *= fade_in * fade_out
    mix = np.tanh(mix * 1.25) / math.tanh(1.25)
    return mix


def write_wav(path: Path, x: np.ndarray, sr: int = SR):
    path.parent.mkdir(parents=True, exist_ok=True)
    st = np.clip(np.stack([x, x], axis=1), -1.0, 1.0)
    data = (st * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


def measure(x: np.ndarray, sr: int = SR):
    peak = float(np.abs(x).max())
    rms = float(np.sqrt((x ** 2).mean()))
    return {"peak": round(peak, 4), "rms": round(rms, 4)}


FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")


def ffmpeg_loudness(path: Path):
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
    ap.add_argument("--target-tp", type=float, default=-1.2)
    args = ap.parse_args()
    out = Path(args.out)
    x = build()
    lufs = tp = None
    for _ in range(8):
        write_wav(out, x)
        lufs, tp = ffmpeg_loudness(out)
        if lufs is None:
            break
        x = x * (10.0 ** ((args.target_lufs - lufs) / 20.0))
        write_wav(out, x)
        lufs, tp = ffmpeg_loudness(out)
        if tp is not None and tp > args.target_tp:
            x = x * (10.0 ** ((args.target_tp - tp) / 20.0))
            write_wav(out, x)
            lufs, tp = ffmpeg_loudness(out)
        if lufs is not None and abs(lufs - args.target_lufs) < 0.2 and (tp or -9) <= args.target_tp + 0.1:
            break
    print(json.dumps({"out": str(out), "dur": round(len(x) / SR, 3),
                      "integrated_lufs": lufs, "true_peak_dbtp": tp, **measure(x)}, indent=2))


if __name__ == "__main__":
    main()
