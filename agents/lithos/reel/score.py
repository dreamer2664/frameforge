#!/usr/bin/env python3
"""reel.score - 157 BPM bed + beat-aligned hits for the reel. -> work/score.wav/.m4a"""
import math
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 12.8
BPM = 157.0
BEAT = 60.0 / BPM          # 0.3822 s
S16 = BEAT / 4             # 0.0955 s
FF = str(Path.home() / ".cache/frameforge/bin/ffmpeg")

rng = np.random.RandomState(3)
t = np.arange(int(DUR * SR)) / SR


def env_ad(n, a, d, curve=2.0):
    e = np.ones(n)
    na = max(1, int(a * SR))
    nd = max(1, int(d * SR))
    e[:na] = np.linspace(0, 1, na)
    tail = np.linspace(1, 0, min(nd, n)) ** curve
    e[-len(tail):] *= tail
    return e


def place(buf, sig, t0):
    i0 = int(t0 * SR)
    i1 = min(len(buf), i0 + len(sig))
    if i0 >= len(buf) or i1 <= i0:
        return
    buf[i0:i1] += sig[:i1 - i0]


def kick(dur=0.16, f0=120, f1=44, amp=0.9):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt * 22)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(ph) * (np.linspace(1, 0, n) ** 1.7)


def hat(dur=0.05, amp=0.16):
    n = int(dur * SR)
    x = rng.randn(n) * (np.linspace(1, 0, n) ** 3)
    # crude highpass
    return amp * (x - np.convolve(x, np.ones(6) / 6, mode="same"))


def tick(dur=0.035, f=2400, amp=0.14):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    return amp * np.sin(2 * np.pi * f * tt) * (np.linspace(1, 0, n) ** 2.4)


def whoosh(dur=0.42, amp=0.5, rise=True):
    n = int(dur * SR)
    x = rng.randn(n)
    e = np.linspace(0, 1, n) ** 2 if rise else np.linspace(1, 0, n) ** 2
    y = x * e
    # band sweep via modulation
    tt = np.arange(n) / SR
    y *= (0.5 + 0.5 * np.sin(2 * np.pi * (60 + 240 * (tt / dur)) * tt))
    return amp * y


def impact(dur=0.8, amp=1.0, f=58):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    body = np.sin(2 * np.pi * f * tt * (1 + 0.6 * np.exp(-tt * 16))) * (np.linspace(1, 0, n) ** 1.4)
    noise = rng.randn(n) * (np.linspace(1, 0, n) ** 3) * 0.45
    return amp * (body * 0.9 + noise)


def riser(dur=1.0, amp=0.35):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 180 * (1 + 5 * (tt / dur) ** 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(ph) * (tt / dur) ** 1.5


def bass_note(f, dur, amp=0.32):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt)
    return amp * x * (np.linspace(1, 0, n) ** 1.2)


def pad(freqs, dur, amp=0.10):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * tt + rng.rand()) for f in freqs) / len(freqs)
    e = np.ones(n)
    e[:2000] = np.linspace(0, 1, 2000)
    e[-4000:] = np.linspace(1, 0, 4000)
    return amp * x * e


mix = np.zeros(int(DUR * SR))

# ---- bed: 16th pulse from 2.38 to end
t0 = 2.38
while t0 < 12.6:
    place(mix, tick(amp=0.12), t0)
    place(mix, hat(amp=0.10), t0)
    t0 += S16

# kick on quarters from 2.38
t0 = 2.38
while t0 < 12.5:
    place(mix, kick(amp=0.7), t0)
    t0 += BEAT

# offbeat bass
for i in range(27):
    t0 = 2.38 + i * BEAT
    if t0 > 12.4:
        break
    f = [55, 55, 73.4, 65.4][i % 4]
    place(mix, bass_note(f, BEAT * 0.9), t0)

# ---- intro
place(mix, kick(0.3, 100, 40, 0.7), 0.08)
place(mix, whoosh(0.5, 0.22, rise=True), 0.02)
place(mix, tick(0.09, 1600, 0.3), 0.33)
place(mix, pad([110, 165, 220], 2.6, 0.13), 0.0)

# ---- storyboard accents
place(mix, whoosh(0.35, 0.4), 1.55)          # whip to type
place(mix, impact(0.7, 0.85, 52), 1.95)      # invert flash
place(mix, tick(0.1, 1900, 0.28), 2.45)      # design flies
place(mix, riser(0.55, 0.3), 3.42)           # zoom-through build
place(mix, impact(0.9, 0.95, 48), 3.98)      # orange flood
place(mix, whoosh(0.3, 0.34, rise=False), 4.30)
place(mix, impact(0.6, 0.5, 64), 5.20)       # pattern
place(mix, whoosh(0.42, 0.42, rise=False), 5.60)   # smear melt
place(mix, impact(1.0, 1.0, 46), 6.00)       # burst
place(mix, whoosh(0.4, 0.3), 6.35)
place(mix, riser(0.5, 0.26), 7.55)
place(mix, impact(0.9, 0.9, 50), 7.95)       # implode
place(mix, whoosh(0.35, 0.3, rise=False), 8.02)
place(mix, tick(0.08, 2100, 0.24), 9.20)     # mitosis
place(mix, impact(0.7, 0.55, 56), 10.00)     # dashboard
place(mix, whoosh(0.45, 0.36), 11.20)        # defocus
for i, tt in enumerate((11.55, 11.63, 11.71, 11.79, 11.87)):
    place(mix, impact(0.35, 0.6 - i * 0.07, 70 + i * 12), tt)   # recap hits
place(mix, impact(1.1, 1.0, 42), 12.00)      # end card
place(mix, pad([98, 147, 196], 1.2, 0.16), 11.95)

# gentle master shaping
mix *= 0.86
mix = np.tanh(mix * 1.25) * 0.92
# fade tail
fade = np.ones_like(mix)
nf = int(0.25 * SR)
fade[-nf:] = np.linspace(1, 0, nf)
mix *= fade

peak = np.abs(mix).max()
mix = mix / peak * 0.89

out = Path("work")
out.mkdir(exist_ok=True)


def pack24(x):
    x = np.clip(x, -1, 1)
    ints = (x * 8388607).astype(np.int32)
    b = np.zeros((ints.shape[0], 3), np.uint8)
    v = ints.astype(np.uint32)
    b[:, 0] = v & 255
    b[:, 1] = (v >> 8) & 255
    b[:, 2] = (v >> 16) & 255
    return b.tobytes()


stereo = np.stack([mix, mix], axis=1)
with wave.open(str(out / "score.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(3)
    w.setframerate(SR)
    w.writeframes(pack24(stereo.ravel()))

# loudnorm pass -> m4a, keep measured near -16 LUFS
for i in range(4):
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", str(out / "score.wav"),
                        "-af", "loudnorm=I=-16:TP=-1.5:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    js = r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1]
    import json
    try:
        m = json.loads(js)
    except Exception:
        break
    li, tp = float(m["input_i"]), float(m["input_tp"])
    if abs(li + 16) < 0.4 and tp <= -1.4:
        print(f"pass{i}: {li} LUFS {tp} dBTP - in spec")
        break
    gain = (-16.0) - li
    gain = max(-6, min(6, gain))
    print(f"pass{i}: {li} LUFS {tp} dBTP -> gain {gain:+.2f}")
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", str(out / "score.wav"),
                    "-af", f"volume={gain}dB", str(out / "score_fit.wav")], check=True)
    (out / "score.wav").replace(out / "score_old.wav")
    (out / "score_fit.wav").replace(out / "score.wav")

subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", str(out / "score.wav"),
                "-c:a", "aac", "-b:a", "192k", str(out / "score.m4a")], check=True)
print("wrote work/score.wav + score.m4a")
