#!/usr/bin/env python3
"""kinetic - dimension (r05) score: 40 s cinematic-techno at 120 BPM, F minor.
Bar = 2 s. Visual cuts at 4/8/14/20/28/34 s are bar lines; impacts at 1/36 s.
Output: /tmp/r05-score.wav (48 kHz stereo)."""
import numpy as np, wave, struct

SR = 48000; DUR = 40.0; N = int(SR * DUR)
BPM = 120.0; BEAT = 60.0 / BPM; BAR = 4 * BEAT  # 2 s
rng = np.random.default_rng(20261019)

L = np.zeros(N); R = np.zeros(N)

def t_of(sec): return int(sec * SR)

def add(buf, sig, at, gain=1.0):
    i = t_of(at); n = min(len(sig), len(buf) - i)
    if n > 0 and i >= 0: buf[i:i+n] += sig[:n] * gain

def env(n, a=0.002, d=0.15, s=0.0, r=0.05, sus_level=0.0):
    """ADSR in samples-from-seconds."""
    a_n, d_n, r_n = int(a*SR), int(d*SR), int(r*SR)
    s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([
        np.linspace(0, 1, max(1, a_n)),
        np.linspace(1, sus_level, max(1, d_n)),
        np.full(s_n, sus_level),
        np.linspace(sus_level, 0, max(1, r_n)),
    ])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))

def lp1(x, cutoff):
    """one-pole lowpass; cutoff may be scalar or per-sample array."""
    n = len(x)
    y = np.empty(n); acc = 0.0
    if np.isscalar(cutoff):
        a = float(np.exp(-2 * np.pi * cutoff / SR))
        for i in range(n):
            acc = (1 - a) * x[i] + a * acc; y[i] = acc
    else:
        c = np.asarray(cutoff, dtype=float)
        for i in range(n):
            a = float(np.exp(-2 * np.pi * c[i] / SR))
            acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y

LPF = lp1

def hp1(x, cutoff):
    return x - LPF(x, cutoff)

# ---------------- instruments ----------------
def kick(dur=0.42, f0=125, f1=44, punch=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 26)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    click = rng.standard_normal(n) * np.exp(-t * 320) * 0.45 * punch
    return np.tanh((body + click) * 1.7) * 0.95

def sub(dur, freq):
    n = int(dur * SR); t = np.arange(n) / SR
    w = np.sin(2 * np.pi * freq * t) * 0.9 + np.sin(2 * np.pi * freq * 2 * t) * 0.12
    return w * env(n, 0.006, dur*0.4, 0, dur*0.45, 0.75)

def clap(dur=0.3):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    bursts = np.zeros(n)
    for off, g in ((0.0, 1.0), (0.011, 0.8), (0.022, 0.6)):
        i = int(off * SR)
        seg = np.exp(-(np.arange(n - i)) / SR * 55) * g
        bursts[i:] += noise[i:] * seg
    w = LPF(bursts, 3200)
    return w * 0.85

def hat(dur=0.07, open_=False):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    w = hp1(LPF(noise, 11000), 7200)
    return w * np.exp(-t * (18 if open_ else 60)) * 0.5

def pluck(dur, freq, detune=0.004, bright=2400):
    n = int(dur * SR); t = np.arange(n) / SR
    w = np.zeros(n)
    for d in (-detune, 0, detune):
        ph = 2 * np.pi * freq * (1 + d) * t
        saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
        w += saw
    w = LPF(w / 3, bright)
    return w * env(n, 0.003, dur*0.55, 0, dur*0.4, 0.12)

def lead(dur, freq):
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.0035 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t / 0.25, 0, 1)
    w = np.zeros(n)
    for d, g in ((-0.006, 1), (0, 1.1), (0.006, 1), (0.012, 0.5)):
        ph = 2 * np.pi * freq * (1 + d) * np.cumsum(vib) / SR
        w += (2 * ((ph / (2 * np.pi)) % 1) - 1) * g
    cut = 900 + 1800 * np.exp(-t * 3)
    w = LPF(w / 3.6, 2200) * (0.6 + 0.4 * np.exp(-t * 2.2))
    return w * env(n, 0.012, dur*0.35, 0, dur*0.5, 0.45)

def pad(dur, freqs, level=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    w = np.zeros(n)
    for f in freqs:
        for d in (-0.004, 0.004):
            ph = 2 * np.pi * f * (1 + d) * t
            w += (2 * ((ph / (2 * np.pi)) % 1) - 1)
    w = LPF(w / (2 * len(freqs) * 1.6), 1500)
    return w * env(n, dur*0.18, dur*0.1, 0, dur*0.55, 0.85) * level

def impact(dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (58 * np.exp(-t * 2.2) + 34) * t) * np.exp(-t * 3.2)
    noise = LPF(rng.standard_normal(n), 900) * np.exp(-t * 9) * 0.7
    tail = LPF(rng.standard_normal(n), 2400) * np.exp(-t * 1.3) * 0.16
    return np.tanh((boom * 1.25 + noise + tail)) * 0.9

def riser(dur, f_from=180, f_to=2400, noise_only=False):
    n = int(dur * SR); t = np.arange(n) / SR
    k = t / dur
    if noise_only:
        w = rng.standard_normal(n)
        w = hp1(LPF(w, 600 + 9000 * k), 400 + 4000 * k)
    else:
        f = f_from * (f_to / f_from) ** k
        ph = 2 * np.pi * np.cumsum(f) / SR
        w = 0.5 * (2 * ((ph / (2 * np.pi)) % 1) - 1) + 0.5 * hp1(rng.standard_normal(n), 2000)
        w = LPF(w, 1200 + 7000 * k)
    return w * (k ** 1.6) * 0.55

def reverse_cymbal(dur=1.4):
    n = int(dur * SR); t = np.arange(n) / SR
    w = hp1(rng.standard_normal(n), 5200) * np.exp(-t * 2.4)
    return w[::-1] * 0.5

def whoosh(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    k = t / dur
    w = LPF(rng.standard_normal(n), 500 + 5200 * np.sin(np.pi * k))
    return w * np.sin(np.pi * k) ** 1.5 * 0.6

# ---------------- arrangement ----------------
# Note freqs: F minor. F2=87.31, Ab2=103.83, C3=130.81, Eb3=155.56, F3=174.61
F1, C2, F2, Ab2, Eb3, F3, Ab3, C4, Eb4, F4 = 43.65, 65.41, 87.31, 103.83, 155.56, 174.61, 207.65, 261.63, 311.13, 349.23

# --- Bar 0-2 (0-4 s): intro: drone + tick + the ignition impact at 1.0 s ---
drone = pad(4.4, [F1, C2, F2], level=0.42)
add(L, drone, 0.0, 1.0); add(R, drone, 0.0, 1.0)
for i in range(8):  # ticking 8ths
    add(L, hat(0.05), i * 0.25, 0.5); add(R, hat(0.05), i * 0.25 + 0.004, 0.5)
add(L, riser(1.0, 120, 900), 0.0, 0.8); add(R, riser(1.0, 120, 900), 0.0, 0.8)
# ignition: impact on beat 2 (t=1.0), explosion whoosh right after
add(L, impact(1.9), 1.0, 1.05); add(R, impact(1.9), 1.0, 1.05)
add(L, whoosh(1.1), 1.05, 0.8); add(R, whoosh(1.1), 1.08, 0.8)
add(L, reverse_cymbal(1.2), 2.6, 0.55); add(R, reverse_cymbal(1.2), 2.62, 0.55)
for b in (2.0, 2.5, 3.0, 3.5):
    add(L, kick(), b, 0.9); add(R, kick(), b, 0.9)

# --- Bar 2-4 (4-8 s): build: pulse kicks + sub + stabs ---
for i in range(8):
    b = 4 + i * 0.5
    add(L, kick(), b, 1.0); add(R, kick(), b, 1.0)
    if i % 2 == 1:
        add(L, clap(), b, 0.75); add(R, clap(), b + 0.006, 0.75)
    add(L, hat(0.05), b + 0.25, 0.55); add(R, hat(0.05), b + 0.256, 0.55)
    add(L, sub(0.42, F1), b, 0.95); add(R, sub(0.42, F1), b, 0.95)
for b in (4.0, 5.0, 6.0, 7.0):
    st = pluck(0.5, C4)
    add(L, st, b, 0.5); add(R, st, b + 0.012, 0.5)
add(L, riser(1.4, 200, 2200), 6.6, 1.0); add(R, riser(1.4, 200, 2200), 6.6, 1.0)

# --- Bar 4-7 (8-14 s): DROP 1: 4-on-floor + arp ---
for i in range(12):
    b = 8 + i * 0.5
    add(L, kick(), b, 1.05); add(R, kick(), b, 1.05)
    if i % 2 == 1:
        add(L, clap(0.32), b, 0.85); add(R, clap(0.32), b + 0.007, 0.85)
    add(L, hat(0.05), b + 0.25, 0.6); add(R, hat(0.05), b + 0.256, 0.6)
    add(L, sub(0.45, F1 if i % 4 < 2 else Eb3/2), b, 1.0); add(R, sub(0.45, F1 if i % 4 < 2 else Eb3/2), b, 1.0)
arp_notes = [F3, Ab3, C4, Eb4, C4, Ab3, F3, C4]
for i in range(24):
    b = 8 + i * 0.25
    n_ = arp_notes[i % len(arp_notes)]
    p = pluck(0.26, n_)
    add(L, p, b, 0.42); add(R, p, b + 0.014, 0.42)
# tunnel fill 11.5-12
for i in range(8):
    add(L, hat(0.04), 11.5 + i * 0.0625, 0.4 + i * 0.05); add(R, hat(0.04), 11.5 + i * 0.0625 + 0.004, 0.4 + i * 0.05)

# --- Bar 7-10 (14-20 s): groove + motif (material act) ---
motif = [(14.0, F4, 0.75), (14.75, Eb4, 0.5), (15.25, C4, 0.75), (16.0, Ab3, 1.0),
         (17.0, C4, 0.5), (17.5, Eb4, 0.5), (18.0, F4, 1.25), (19.25, Eb4, 0.75)]
for at, f, d in motif:
    s_ = lead(d, f)
    add(L, s_, at, 0.62); add(R, s_, at + 0.018, 0.62)
for i in range(12):
    b = 14 + i * 0.5
    add(L, kick(), b, 1.05); add(R, kick(), b, 1.05)
    if i % 2 == 1:
        add(L, clap(0.32), b, 0.85); add(R, clap(0.32), b + 0.007, 0.85)
    add(L, hat(0.05), b + 0.25, 0.55); add(R, hat(0.05), b + 0.256, 0.55)
    add(L, sub(0.45, F1 if i % 4 < 2 else Ab2/2), b, 1.0); add(R, sub(0.45, F1 if i % 4 < 2 else Ab2/2), b, 1.0)
# wire-phase sparkle 17.9
for i in range(6):
    add(L, hat(0.04, True), 17.9 + i * 0.125, 0.35); add(R, hat(0.04, True), 17.9 + i * 0.125 + 0.005, 0.35)

# --- Bar 10-14 (20-28 s): STORM ---
add(L, riser(1.6, 150, 3200), 18.4, 1.1); add(R, riser(1.6, 150, 3200), 18.4, 1.1)
add(L, impact(1.4), 20.0, 1.0); add(R, impact(1.4), 20.0, 1.0)
for i in range(32):
    b = 20 + i * 0.25
    if i % 2 == 0:
        add(L, kick(0.36), b, 1.1); add(R, kick(0.36), b, 1.1)
        add(L, sub(0.22, F1 if i % 8 < 4 else Eb3/2), b, 1.05); add(R, sub(0.22, F1 if i % 8 < 4 else Eb3/2), b, 1.05)
    else:
        add(L, hat(0.045), b, 0.6); add(R, hat(0.045), b + 0.005, 0.6)
    if i % 8 == 4:
        add(L, clap(0.28), b, 0.9); add(R, clap(0.28), b + 0.007, 0.9)
# offbeat stabs
for i in range(8):
    b = 21 + i * 2
    st = pluck(0.34, [Ab3, C4, Eb4, F4][i % 4])
    add(L, st, b + 0.25, 0.5); add(R, st, b + 0.264, 0.5)
# tension strings 24-28 (tremolo saw)
n_str = int(4 * SR); t_str = np.arange(n_str) / SR
w_str = np.zeros(n_str)
for f, g in ((F2, 1), (Ab2, 0.8), (C2, 0.7), (F3, 0.55)):
    ph = 2 * np.pi * f * t_str
    w_str += (2 * ((ph / (2 * np.pi)) % 1) - 1) * g
trem = 0.65 + 0.35 * np.sin(2 * np.pi * 7 * t_str)
w_str = LPF(w_str * trem, 900 + 2600 * (t_str / 4))
w_str *= np.clip(t_str / 4, 0, 1) ** 1.3 * 0.32
add(L, w_str, 24.0); add(R, w_str, 24.012)
add(L, riser(2.2, 220, 4200, noise_only=True), 25.8, 1.15); add(R, riser(2.2, 220, 4200, noise_only=True), 25.8, 1.15)

# --- Bar 14-17 (28-34 s): ANTHEM (monolith) ---
add(L, impact(2.2), 28.0, 1.1); add(R, impact(2.2), 28.0, 1.1)
padw = pad(6.2, [F2, C2, Ab2, F3], level=0.62)
add(L, padw, 28.0); add(R, padw, 28.02)
for i in range(6):  # half-time drums
    b = 28 + i * 1.0
    add(L, kick(0.5), b, 1.1); add(R, kick(0.5), b, 1.1)
    add(L, clap(0.36), b + 0.5, 0.8); add(R, clap(0.36), b + 0.508, 0.8)
    add(L, sub(0.9, F1), b, 1.0); add(R, sub(0.9, F1), b, 1.0)
anthem = [(28.5, F4, 1.4), (30.0, Eb4, 0.9), (31.0, C4, 1.4), (32.5, Ab3, 1.5)]
for at, f, d in anthem:
    s_ = lead(d, f) * 0.9
    add(L, s_, at, 0.66); add(R, s_, at + 0.02, 0.66)
for i in range(12):  # rolling hats into finale
    add(L, hat(0.045), 32 + i * 0.1667, 0.3 + i * 0.035); add(R, hat(0.045), 32 + i * 0.1667 + 0.004, 0.3 + i * 0.035)
add(L, riser(1.8, 180, 3600), 32.2, 1.1); add(R, riser(1.8, 180, 3600), 32.2, 1.1)

# --- Bar 17-20 (34-40 s): FINALE ---
add(L, impact(2.4), 34.0, 1.15); add(R, impact(2.4), 34.0, 1.15)
add(L, reverse_cymbal(1.6), 34.4, 0.7); add(R, reverse_cymbal(1.6), 34.43, 0.7)
# implosion riser 34.5-36
add(L, riser(1.5, 260, 3000, noise_only=True), 34.5, 0.95); add(R, riser(1.5, 260, 3000, noise_only=True), 34.5, 0.95)
add(L, impact(3.2), 36.0, 1.25); add(R, impact(3.2), 36.0, 1.25)
resolve = pad(4.0, [F2, Ab2, C2, F3], level=0.72)
add(L, resolve, 36.0); add(R, resolve, 36.015)
for at, f, d in ((36.1, F4, 1.6), (37.8, C4, 1.8)):
    s_ = lead(d, f) * 0.7
    add(L, s_, at, 0.55); add(R, s_, at + 0.022, 0.55)
for i, b in enumerate((36.0, 37.0, 38.0, 39.0)):
    add(L, kick(0.42), b, 0.55 - i * 0.12); add(R, kick(0.42), b, 0.55 - i * 0.12)
    add(L, sub(0.8, F1), b, 0.5 - i * 0.1); add(R, sub(0.8, F1), b, 0.5 - i * 0.1)
for i in range(16):  # fading ticks
    add(L, hat(0.04), 36.5 + i * 0.21, 0.22 * (1 - i / 16)); add(R, hat(0.04), 36.5 + i * 0.21 + 0.005, 0.22 * (1 - i / 16))

# ---------------- master ----------------
# gentle sidechain pump on the whole bus against the kick grid (sub feel)
pump = np.ones(N)
kick_times = [1.0] + [4 + i * 0.5 for i in range(8)] + [8 + i * 0.5 for i in range(12)] + \
             [14 + i * 0.5 for i in range(12)] + [20 + i * 0.5 for i in range(16)] + \
             [28 + i * 1.0 for i in range(6)] + [36, 37, 38, 39]
for kt in kick_times:
    i = t_of(kt); n = int(0.18 * SR)
    if i + n <= N:
        pump[i:i+n] *= np.linspace(0.72, 1.0, n)
L *= pump; R *= pump

# soft clip + level
L = np.tanh(L * 0.85) * 1.05
R = np.tanh(R * 0.85) * 1.05
# fade tail
tail = np.ones(N)
tail[t_of(39.45):] = np.linspace(1, 0, N - t_of(39.45))
L *= tail; R *= tail

peak = max(np.abs(L).max(), np.abs(R).max())
L /= peak / 0.94; R /= peak / 0.94

out = '/tmp/r05-score.wav'
with wave.open(out, 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    inter = np.empty(N * 2, dtype=np.int16)
    inter[0::2] = np.clip(L * 32767, -32768, 32767).astype(np.int16)
    inter[1::2] = np.clip(R * 32767, -32768, 32767).astype(np.int16)
    w.writeframes(inter.tobytes())
print('SCORE3_OK', DUR, 's  peak', round(float(peak), 3))
