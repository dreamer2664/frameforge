"""KINETIC REEL v2 score — 157 BPM, cut-locked to the act timeline.
Produced-sound design: layered drums, sidechained sub, filtered saw plucks,
stereo pads, risers/impacts on cuts, bus saturation, reverb send. Not raw beeps.
"""
import numpy as np
from pathlib import Path

SR = 44100
BPM = 157.0
BEAT = 60.0 / BPM          # 0.3822
BAR = 4 * BEAT             # 1.5288
DUR = 12.8
N = int(SR * DUR)
rng = np.random.default_rng(20261018)

L = np.zeros(N)
R = np.zeros(N)
# reverb send buses
SND_L = np.zeros(N)
SND_R = np.zeros(N)


def idx(t):
    return int(t * SR)


def add(buf, t, sig, gain=1.0):
    i = idx(t)
    n = min(len(sig), N - i)
    if n > 0 and i >= 0:
        buf[i:i + n] += sig[:n] * gain


def add_st(t, sig, gain=1.0, pan=0.0, send=0.0):
    gl = gain * math_cos_pan(pan, 0)
    gr = gain * math_cos_pan(pan, 1)
    add(L, t, sig, gl)
    add(R, t, sig, gr)
    if send > 0:
        add(SND_L, t, sig, gl * send)
        add(SND_R, t, sig, gr * send)


def math_cos_pan(pan, side):
    # pan -1..1
    ang = (pan + 1) * math.pi / 4
    return math.cos(ang) if side == 0 else math.sin(ang)


import math


def env_exp(n, tau, attack=0.002):
    t = np.arange(n) / SR
    e = np.exp(-t / tau)
    a = int(attack * SR)
    if a > 1:
        e[:a] *= np.linspace(0, 1, a)
    return e


def onepole_lp(x, cutoff_arr):
    """time-varying one-pole lowpass"""
    y = np.empty_like(x)
    acc = 0.0
    dt = 1.0 / SR
    for i in range(len(x)):
        rc = 1.0 / (2 * math.pi * cutoff_arr[i])
        a = dt / (rc + dt)
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def onepole_hp(x, cutoff):
    a = math.exp(-2 * math.pi * cutoff / SR)
    y = np.empty_like(x)
    prev_x = 0.0
    prev_y = 0.0
    for i in range(len(x)):
        y[i] = a * (prev_y + x[i] - prev_x)
        prev_x = x[i]
        prev_y = y[i]
    return y


def noise(n):
    return rng.standard_normal(n)


# ---------------- instruments ----------------
def kick():
    n = int(0.28 * SR)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t / 0.028)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.115)
    click = onepole_hp(noise(n), 2600) * np.exp(-t / 0.004) * 0.35
    return np.tanh((body + click) * 1.6) * 0.95


def sub(f0, dur, duck_env=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f0 * t) + 0.28 * np.sin(4 * np.pi * f0 * t)
    e = np.minimum(1, t / 0.012) * np.exp(-t / (dur * 0.62))
    s = np.tanh(s * 1.35) * e
    if duck_env is not None:
        s *= duck_env[:n]
    return s


def clap():
    n = int(0.32 * SR)
    t = np.arange(n) / SR
    body = np.zeros(n)
    for k, off in enumerate((0.0, 0.011, 0.021)):
        o = int(off * SR)
        seg = noise(n - o) * np.exp(-np.arange(n - o) / SR / 0.012)
        body[o:] += seg * (1 - k * 0.22)
    tail = noise(n) * np.exp(-t / 0.14) * 0.35
    s = onepole_hp(body + tail, 900)
    s = onepole_lp(s, np.full(n, 3600.0))
    return s * 0.6


def hat(open_=False):
    dur = 0.16 if open_ else 0.045
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = onepole_hp(noise(n), 7000)
    s = onepole_lp(s, np.full(n, 11000.0))
    return s * np.exp(-t / (0.055 if open_ else 0.014)) * (0.17 if open_ else 0.115)


def pluck(f0, dur=0.24, bright=2600):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = 0.5 * (2 * ((t * f0) % 1) - 1) + 0.5 * (2 * ((t * f0 * 1.006) % 1) - 1)
    cut = 320 + (bright - 320) * np.exp(-t / 0.07)
    s = onepole_lp(s, cut)
    return s * env_exp(n, dur * 0.38)


def saw_chord(freqs, dur, attack=0.01, bright=1800, decay=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (0.994, 1.0, 1.006):
            s += 2 * ((t * f * det) % 1) - 1
    s /= (len(freqs) * 3)
    cut = bright * (0.35 + 0.65 * np.exp(-t / (decay or dur * 0.5)))
    s = onepole_lp(s, cut)
    e = np.minimum(1, t / attack) * np.exp(-t / (decay or dur * 0.55))
    return s * e


def pad(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det, amp in ((0.987, 0.7), (1.0, 1.0), (1.013, 0.7), (2.0, 0.25)):
            s += amp * (2 * ((t * f * det) % 1) - 1)
    s /= len(freqs) * 3
    cut = 240 + 2100 * np.minimum(1, t / (dur * 0.55))
    s = onepole_lp(s, cut)
    e = np.minimum(1, t / 0.45) * np.minimum(1, np.maximum(0, (dur - t) / 0.5))
    return s * e * 0.8


def riser(dur=0.85, f0=180, f1=1400):
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = t / dur
    f = f0 * (f1 / f0) ** u
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = 0.5 * np.sin(ph) + 0.6 * onepole_hp(noise(n), 400) * (0.2 + u)
    return s * (u ** 1.6) * 0.55


def impact():
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (58 * np.exp(-t / 0.22) + 34) * t) * np.exp(-t / 0.3)
    wash = onepole_lp(onepole_hp(noise(n), 2200), np.full(n, 7500.0)) * np.exp(-t / 0.32) * 0.22
    return np.tanh((boom + wash) * 1.2) * 0.9


def rev_swell(dur=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = onepole_hp(noise(n), 1200) * (t / dur) ** 2.2
    return s * 0.5


# ---------------- arrangement ----------------
F1, AF2, CF3, EF3, F3, GF3, AF3, CF4, EF4, F4 = (
    43.65, 87.31, 130.81, 155.56, 174.61, 185.0, 207.65, 261.63, 311.13, 349.23)

# --- kick pattern (four-on-floor with syncopated ghosts), from 1.55 ---
kick_times = []
t = 1.55
while t < 11.55:
    bar_pos = ((t - 1.55) / BEAT) % 4
    if bar_pos < 3.99:
        kick_times.append(t)
    if 6.0 <= t < 11.2 and abs(bar_pos - 2.75) < 0.01:
        kick_times.append(t + BEAT * 0.5)  # syncopated push
    t += BEAT
kick_times.append(11.55)
# montage stabs
kick_times += [11.55 + i * 0.19 for i in range(4)]

duck = np.ones(N)
for kt in kick_times:
    i = idx(kt)
    n = int(0.24 * SR)
    if 0 <= i < N:
        seg = np.linspace(1, 1, min(n, N - i))
        tt = np.arange(len(seg)) / SR
        seg = 0.42 + 0.58 * np.minimum(1, tt / 0.16) ** 0.8
        duck[i:i + len(seg)] = np.minimum(duck[i:i + len(seg)], seg)
for kt in kick_times:
    add_st(kt, kick(), 1.05, 0.0, 0.06)

# --- claps on 2 & 4 from 1.55 ---
t = 1.55 + BEAT
while t < 11.55:
    add_st(t, clap(), 0.55, 0.06, 0.22)
    t += 2 * BEAT

# --- hats: 8ths from 4.35, 16ths from 10.0 ---
t = 4.35
while t < 11.55:
    step = BEAT / 2 if t < 10.0 else BEAT / 4
    op = abs(((t - 4.35) / BEAT) % 4 - 2.75) < 0.02
    add_st(t, hat(op), 0.8 if op else 0.62, 0.22 if int(t * 20) % 2 else -0.18, 0.03)
    t += step

# --- sub bass line (roots), from 1.55 ---
bass_notes = [(1.55, F1), (2.71, F1), (3.10, AF2 / 2), (3.48, CF3 / 2), (4.35, F1),
              (5.50, F1), (5.89, AF2 / 2), (6.27, F1), (7.43, EF3 / 2), (7.81, F1),
              (8.0, AF2 / 2), (9.16, CF3 / 2), (9.55, F1), (10.0, EF3 / 2), (11.16, F1)]
for bt, f in bass_notes:
    dur = 0.42
    s = sub(f, dur, duck_env=duck[idx(bt):idx(bt) + int(dur * SR)])
    add_st(bt, s, 0.85, 0.0, 0.0)

# --- pluck motif (intro then continuing) ---
motif = [(0.0, F3), (0.38, AF3), (0.76, CF4), (1.14, AF3), (1.33, GF3)]
for mt, f in motif:
    add_st(mt, pluck(f, 0.3), 0.7, -0.12, 0.22)
for rep, base in enumerate((1.55, 3.10, 6.27, 7.81, 9.36)):
    for k, (dt, f) in enumerate(motif[:4]):
        add_st(base + dt, pluck(f * (2 if rep >= 3 else 1), 0.26), 0.55, -0.1 + 0.05 * k, 0.22)

# --- stab chords at section starts ---
for st, ch in ((1.55, (F3, AF3, CF4)), (4.35, (AF3, CF4, EF4)), (6.0, (F3, AF3, EF4)),
               (8.0, (CF4, EF4, F4)), (10.0, (AF3, CF4, EF4))):
    add_st(st, saw_chord(ch, 0.5, bright=2400), 0.5, 0.0, 0.28)

# --- pads 8.0-11.2 (the lift) ---
for pt, ch, dur in ((8.0, (F3, AF3, CF4, EF4), 1.7), (9.55, (EF3, GF3, CF4, EF4), 1.8), (11.0, (F3, AF3, CF4), 1.1)):
    s = pad(ch, dur)
    add_st(pt, s, 0.34, -0.25, 0.42)
    add_st(pt + 0.012, s, 0.34, 0.25, 0.42)

# --- arp 6.0-11.55 (16ths, alternating octaves) ---
arp_seq = [F4, AF3, CF4, EF4, F4, CF4, AF3, F4]
t = 6.0
k = 0
while t < 11.55:
    f = arp_seq[k % len(arp_seq)] * (2 if (k // len(arp_seq)) % 2 else 1)
    add_st(t, pluck(f, 0.16, 3200), 0.30, 0.32 if k % 2 else -0.22, 0.16)
    t += BEAT / 4
    k += 1

# --- risers / impacts / swells at cuts ---
add_st(0.72, riser(0.82, 160, 900), 0.6, 0.0, 0.2)
add_st(5.28, riser(0.7, 220, 1600), 0.55, 0.0, 0.2)
for ct in (1.55, 6.0, 8.0, 10.0):
    add_st(ct, impact(), 0.75, 0.0, 0.25)
add_st(11.02, rev_swell(0.62), 0.65, 0.0, 0.35)
# montage hits
for i in range(4):
    add_st(11.55 + i * 0.19, impact(), 0.42, (-1) ** i * 0.2, 0.22)
add_st(12.0, impact(), 0.95, 0.0, 0.42)
add_st(12.0, saw_chord((F3, AF3, CF4, F4), 1.4, attack=0.01, bright=1600, decay=0.9), 0.32, 0.0, 0.5)

# ---------------- reverb send (exponential noise IR, cheap convolution) ----------------
ir_n = int(1.5 * SR)
ir_t = np.arange(ir_n) / SR
ir = noise(ir_n) * np.exp(-ir_t / 0.38)
ir[: int(0.012 * SR)] = 0
ir /= np.abs(ir).sum() / 30
wet_l = np.convolve(SND_L, ir)[:N]
wet_r = np.convolve(SND_R, ir * 0.94)[:N]
L += wet_l * 0.13
R += wet_r * 0.13

# ---------------- master: stereo width, saturation, limit ----------------
mid = (L + R) / 2
side = onepole_lp((L - R) / 2, np.full(N, 9500.0)) * 1.05
L = np.tanh((mid + side) * 1.22)
R = np.tanh((mid - side) * 1.22)

# tiny head fade-in / tail fade-out
fi = int(0.01 * SR)
L[:fi] *= np.linspace(0, 1, fi)
R[:fi] *= np.linspace(0, 1, fi)
fo = int(0.12 * SR)
L[-fo:] *= np.linspace(1, 0, fo)
R[-fo:] *= np.linspace(1, 0, fo)

out = np.stack([L, R], axis=1)
peak = np.abs(out).max()
out = out / peak * 0.89
pcm = (out * 32767).astype(np.int16)

import wave
Path('/home/user/work/frameforge/agents/lithos/reel/work').mkdir(parents=True, exist_ok=True)
with wave.open('/home/user/work/frameforge/agents/lithos/reel/work/score2.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('SCORE2_OK', DUR, 's  peak', round(float(peak), 3))
