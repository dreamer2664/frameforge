#!/usr/bin/env python3
"""mg.score - synthesized score for the title machine.

120 BPM (beat = 0.5 s). Every accent comes from storyboard.json beats: the
score is derived from the picture's event map, not placed by ear.
"""
import json
import math
import subprocess
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
SB = json.loads((ROOT / "storyboard.json").read_text())
SR = 48000
DUR = SB["format"]["duration_seconds"]
N = int(DUR * SR)


def env(n, a, d, s=0.0, r=None, sus_level=0.0):
    t = np.arange(n) / SR
    e = np.ones(n) * sus_level
    ai = int(a * SR)
    di = int(d * SR)
    if ai > 0:
        e[:ai] = np.linspace(0, 1, ai)
    if di > 0:
        e[ai:ai + di] = np.linspace(1, s, di)
    e[ai + di:] = s
    return e


def place(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    n = min(len(sig), len(buf) - i0)
    if n <= 0:
        return
    l = gain * (1 - max(0, pan))
    r = gain * (1 + min(0, pan))
    buf[i0:i0 + n, 0] += sig[:n] * l
    buf[i0:i0 + n, 1] += sig[:n] * r


def kick(dur=0.42, f0=118, f1=42):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 22)
    ph = 2 * math.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 8.5)
    click = np.random.default_rng(3).normal(0, 1, n) * np.exp(-t * 320) * 0.25
    return body + click


def hat(dur=0.07, seed=1, bright=1.0):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n)
    # crude highpass: difference
    x = np.diff(np.concatenate([[0], x]))
    return x * np.exp(-np.arange(n) / SR * 90) * 0.4 * bright


def bass(dur=0.46, f=55.0, seed=2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * math.pi * f * t) * 0.8 + 0.25 * np.sin(4 * math.pi * f * t)
    return x * env(n, 0.004, dur * 0.9, 0.0)


def whoosh(dur=0.55, rise=True, seed=5):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n)
    x = np.convolve(x, np.ones(6) / 6, 'same')
    t = np.arange(n) / SR
    e = (t / dur) ** 2.0 if rise else (1 - t / dur) ** 1.8
    return x * e * 0.55


def impact(dur=1.1, seed=7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 98 * np.exp(-t * 5) + 38
    ph = 2 * math.pi * np.cumsum(f) / SR
    boom = np.sin(ph) * np.exp(-t * 3.2)
    rng = np.random.default_rng(seed)
    noise = np.convolve(rng.normal(0, 1, n), np.ones(12) / 12, 'same') * np.exp(-t * 11) * 0.5
    return boom * 0.9 + noise


def riser(dur=1.2, seed=9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n)
    # amplitude modulated rising tone
    f = 180 + 900 * (t / dur) ** 2
    ph = 2 * math.pi * np.cumsum(f) / SR
    tone = np.sin(ph) * 0.4
    e = (t / dur) ** 1.6
    return (x * 0.22 + tone) * e


def pad(dur, freqs, seed=11):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    rng = np.random.default_rng(seed)
    for k, f in enumerate(freqs):
        det = 1 + 0.0035 * (k - 1)
        x += np.sin(2 * math.pi * f * det * t + rng.uniform(0, 6.28)) / len(freqs)
    return x


def build():
    buf = np.zeros((N, 2))
    beats = {b["id"]: b["t"] for b in SB["beats"]}

    # --- groove bed: 120 BPM from t=0 to ~11.9
    beat = 0.5
    for i in range(0, 24):
        t = i * beat
        if t > 11.95:
            break
        place(buf, kick(), t, gain=0.85 if i % 2 == 0 else 0.55)
        place(buf, hat(0.07, seed=i, bright=1.0), t + 0.25, gain=0.22, pan=0.15)
        place(buf, hat(0.05, seed=40 + i, bright=0.7), t + 0.375, gain=0.12, pan=-0.2)
        if i % 2 == 1:
            place(buf, hat(0.12, seed=80 + i, bright=1.2), t, gain=0.28, pan=-0.1)
        if i % 4 in (0, 3):
            place(buf, bass(0.46, 55 if i % 8 < 4 else 41.2), t, gain=0.42)

    # pads: sections
    place(buf, pad(4.2, [220, 277, 330]) * np.hanning(int(4.2 * SR)) ** 0.5, 0.0, gain=0.10, pan=-0.1)
    place(buf, pad(3.0, [246, 311, 370]) * np.hanning(int(3.0 * SR)) ** 0.5, 4.3, gain=0.11, pan=0.1)
    place(buf, pad(2.9, [233, 294, 349]) * np.hanning(int(2.9 * SR)) ** 0.5, 8.6, gain=0.13, pan=0.0)

    # --- picture-derived accents
    place(buf, whoosh(0.5, rise=True), 0.85, gain=0.30)          # wordmark forms
    place(buf, whoosh(0.42, rise=True, seed=6), beats["whip_tools"] - 0.12, gain=0.5)
    place(buf, whoosh(0.4, rise=False, seed=8), beats["chips_land"], gain=0.35)
    place(buf, impact(0.5, seed=10), beats["click"], gain=0.38)   # click
    place(buf, impact(1.1), beats["hard_cut"], gain=0.75)         # hard cut
    for k in range(6):                                            # typing ticks
        place(buf, hat(0.04, seed=200 + k, bright=1.4), beats["prompt1"] + 0.12 * k, gain=0.10)
    for k in range(4):
        place(buf, hat(0.04, seed=220 + k, bright=1.4), beats["card_out_p2"] + 0.1 * k, gain=0.10)
    place(buf, riser(1.0, seed=12), beats["card_in"] - 0.75, gain=0.20)
    place(buf, impact(0.9, seed=13), beats["card_in"], gain=0.5)
    place(buf, whoosh(0.5, rise=False, seed=14), beats["card_out_p2"], gain=0.45)
    place(buf, riser(1.25, seed=15), beats["anticipation"], gain=0.34)   # build to the flip
    place(buf, impact(1.4, seed=16), beats["flip"], gain=0.95)           # biggest hit
    place(buf, whoosh(0.45, rise=True, seed=17), beats["flip"] - 0.1, gain=0.4)
    place(buf, impact(0.8, seed=18), beats["whoosh"], gain=0.45)
    place(buf, whoosh(0.35, rise=True, seed=19), beats["logo_back"], gain=0.3)
    for k in range(8):  # outro letters
        place(buf, hat(0.05, seed=240 + k, bright=1.3), beats["outro_type"] + 0.055 * k, gain=0.12)
    place(buf, impact(1.0, seed=20), beats["lockup"], gain=0.42)
    place(buf, whoosh(0.22, rise=False, seed=21), beats["streak_exit"], gain=0.55)

    # soft limiter
    buf = np.tanh(buf * 1.1) * 0.92
    return buf



def pack24(buf):
    ints = np.clip(buf * 8388607, -8388608, 8388607).astype(np.int32)
    out = np.empty((ints.shape[0], 6), dtype=np.uint8)
    for ch in range(2):
        v = ints[:, ch]
        out[:, ch * 3 + 0] = (v & 0xFF).astype(np.uint8)
        out[:, ch * 3 + 1] = ((v >> 8) & 0xFF).astype(np.uint8)
        out[:, ch * 3 + 2] = ((v >> 16) & 0xFF).astype(np.uint8)
    return out


def measure(path):
    out = subprocess.run(["/home/user/.cache/frameforge/bin/ffmpeg", "-hide_banner", "-i", str(path),
                          "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    import re
    js = out[out.rfind("{"):out.rfind("}") + 1]
    d = json.loads(js)
    return float(d["input_i"]), float(d["input_tp"])


def main():
    out_dir = ROOT / "work"
    out_dir.mkdir(exist_ok=True)
    buf = build()
    wav = out_dir / "score.wav"
    # 24-bit wav
    import wave
    packed = pack24(buf)
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(packed.tobytes())
    # gain fit on the AAC encode
    m4a = out_dir / "score.m4a"
    for pass_i in range(4):
        subprocess.run(["/home/user/.cache/frameforge/bin/ffmpeg", "-y", "-v", "error",
                        "-i", str(wav), "-c:a", "aac", "-b:a", "256k", str(m4a)], check=True)
        lufs, tp = measure(m4a)
        print(f"pass {pass_i}: {lufs} LUFS  {tp} dBTP", flush=True)
        if abs(lufs + 16.0) <= 0.4 and tp <= -1.0:
            break
        gain = min(-16.0 - lufs, -1.2 - tp) if tp > -1.2 else -16.0 - lufs
        buf = np.clip(buf * (10 ** (gain / 20)), -1, 1)
        packed = pack24(buf)
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(3)
            w.setframerate(SR)
            w.writeframes(packed.tobytes())
    print("score written:", wav, m4a)


if __name__ == "__main__":
    main()
