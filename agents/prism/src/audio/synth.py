#!/usr/bin/env python3
"""PRISM / PROOF — original soundtrack synthesiser (48 kHz stereo).

Every sound is generated here from first principles (oscillators, seeded
noise, FFT filtering). No samples, no libraries of recorded audio:
rights-clean by construction (see RIGHTS.md).

Temporal truth comes from evidence/events.json — the same constants the
visuals use — so SFX hits land on their visual frames exactly (±0 samples).
"""
import json
import sys
import wave
import numpy as np

SR = 48000
FPS = 30
FRAMES = 750
DUR = FRAMES / FPS                      # 25.000 s
N = int(SR * DUR)                       # 1 200 000 samples
SEED = 0x50524F4F

rng = np.random.default_rng(SEED)

L = np.zeros(N, dtype=np.float64)
R = np.zeros(N, dtype=np.float64)


def f2s(frame):                          # frame -> sample index (exact)
    return int(round(frame / FPS * SR))


def add(sig, at, gain=1.0, pan=0.0):
    """Mix sig into the stereo buffers at sample `at`. pan in [-1,1]."""
    at = int(at)
    n = min(len(sig), N - at)
    if n <= 0:
        return
    gl = gain * np.sqrt(0.5 * (1 - pan))
    gr = gain * np.sqrt(0.5 * (1 + pan))
    L[at:at + n] += sig[:n] * gl
    R[at:at + n] += sig[:n] * gr


def env(n, a, d, sustain=0.0, r=None, curve='exp'):
    """attack/decay envelope, length n samples."""
    t = np.arange(n) / SR
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na) ** 1.5
    nd = int(d * SR)
    if nd > 0:
        seg = np.arange(nd) / nd
        dec = (1 - seg) ** 2 if curve == 'exp' else np.exp(-4 * seg)
        e[na:na + nd] = dec[:max(0, n - na)]
    return e * (1 - sustain) + sustain


def sine(freq, n, phase=0.0, sweep_to=None):
    t = np.arange(n) / SR
    if sweep_to is None:
        return np.sin(2 * np.pi * freq * t + phase)
    f0, f1 = freq, sweep_to
    k = np.log(f1 / f0) / (n / SR)
    return np.sin(2 * np.pi * f0 * (np.exp(k * t) - 1) / k + phase)


def saw(freq, n):
    t = np.arange(n) / SR
    x = (t * freq) % 1.0
    return 2 * x - 1


def noise(n, seed_off=0):
    return rng.standard_normal(n)


def fft_filter(sig, lo=None, hi=None, tilt=0.0):
    """Brickwall-ish smooth band via FFT with raised-cosine edges."""
    n = len(sig)
    F = np.fft.rfft(sig)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 0.5 * (1 + np.tanh((f - lo) / (lo * 0.25 + 1)))
    if hi:
        m *= 0.5 * (1 - np.tanh((f - hi) / (hi * 0.25 + 1)))
    if tilt:
        m *= (f / 1000.0) ** tilt
    return np.fft.irfft(F * m, n)


def onepole_lp(sig, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    out = np.empty_like(sig)
    acc = 0.0
    for i in range(len(sig)):           # small signals only
        acc = a * acc + (1 - a) * sig[i]
        out[i] = acc
    return out


# ---------------------------------------------------------------- instruments
def kick(gain=1.0, click=0.5):
    n = int(0.34 * SR)
    body = sine(120, n, sweep_to=41) * env(n, 0.001, 0.30)
    cl = fft_filter(noise(int(0.012 * SR)), lo=1200) * 0.6 * click
    s = body + np.concatenate([cl, np.zeros(n - len(cl))])
    return s * gain


def sub_drop(gain=1.0):
    n = int(1.5 * SR)
    s = sine(64, n, sweep_to=27) * env(n, 0.002, 1.4)
    s += sine(32, n) * env(n, 0.002, 1.2) * 0.7
    return s * gain


def crash(gain=1.0, dur=1.1, hi=9000):
    n = int(dur * SR)
    s = fft_filter(noise(n), lo=900, hi=hi) * env(n, 0.001, dur * 0.9)
    return s * gain


def tick(gain=1.0, freq=2400, pan=0.0):
    n = int(0.05 * SR)
    s = fft_filter(noise(n), lo=freq * 0.7, hi=freq * 2.2) * env(n, 0.0005, 0.04)
    s += sine(freq, n) * env(n, 0.0005, 0.03) * 0.4
    return s * gain, pan


def hat(gain=1.0, pan=0.2):
    n = int(0.09 * SR)
    s = fft_filter(noise(n), lo=6000) * env(n, 0.0005, 0.07)
    return s * gain, pan


def slam(gain=1.0):
    """typographic impact: filtered noise transient + low thud"""
    n = int(0.5 * SR)
    s = fft_filter(noise(int(0.06 * SR)), lo=300, hi=2600) * env(int(0.06 * SR), 0.0004, 0.05)
    s = np.concatenate([s, np.zeros(n - len(s))])
    s += sine(96, n, sweep_to=52) * env(n, 0.001, 0.34) * 0.9
    return s * gain


def stamp(gain=1.0):
    n = int(0.7 * SR)
    s = fft_filter(noise(int(0.05 * SR)), lo=500, hi=3800) * env(int(0.05 * SR), 0.0004, 0.045)
    s = np.concatenate([s, np.zeros(n - len(s))])
    s += sine(70, n, sweep_to=44) * env(n, 0.001, 0.5) * 1.1
    s += fft_filter(noise(n), lo=200, hi=900) * env(n, 0.004, 0.4) * 0.35
    return s * gain


def pad_chord(freqs, dur, gain=1.0, bright=700):
    n = int(dur * SR)
    s = np.zeros(n)
    for i, f in enumerate(freqs):
        det = 1 + 0.0015 * (i % 3 - 1)
        s += saw(f * det, n) * 0.22
        s += sine(f * 2, n, phase=i) * 0.10
    s = fft_filter(s, hi=bright)
    e = env(n, 0.6, 0.0, sustain=1.0)
    nd = int(1.2 * SR)
    e[-nd:] *= np.linspace(1, 0, nd) ** 1.5
    na = int(0.5 * SR)
    e[:na] *= np.linspace(0, 1, na) ** 2
    return s * e * gain


def drone(dur, gain=1.0):
    n = int(dur * SR)
    s = sine(55, n) * 0.5 + sine(55 * 1.006, n) * 0.4 + sine(27.5, n) * 0.5
    s += fft_filter(noise(n), lo=200, hi=900) * 0.10
    e = np.ones(n)
    na = int(1.2 * SR)
    e[:na] = np.linspace(0, 1, na) ** 2
    return s * e * gain


def riser(dur, gain=1.0):
    n = int(dur * SR)
    s = fft_filter(noise(n), lo=400, hi=12000, tilt=0.5)
    e = np.linspace(0, 1, n) ** 2.4
    s *= e
    s += sine(220, n, sweep_to=880) * e * 0.25
    return s * gain


def stab(freqs, gain=1.0):
    n = int(0.42 * SR)
    s = np.zeros(n)
    for f in freqs:
        s += saw(f, n) * 0.3 + sine(f / 2, n) * 0.3
    s = fft_filter(s, lo=120, hi=3200)
    return s * env(n, 0.001, 0.36) * gain


# ------------------------------------------------------------------ the score
ev = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'evidence/events.json'))
HITS = {h['id']: h['frame'] for h in ev['hits']}

# Act I — the claim (0.0–6.0 s)
add(drone(6.4, 0.50), 0)
for fr in (24, 54, 84, 114, 144):                     # sparse calibration ticks
    s, pan = tick(0.16, 2100 + (fr % 5) * 180, pan=(-0.3 if fr % 2 else 0.3))
    add(s, f2s(fr), pan=pan)
add(slam(0.85), f2s(HITS['H-t2']))                    # "A CLAIM IS NOISE."
add(slam(1.00), f2s(HITS['H-claim']))                 # F1 assertion
add(crash(0.30, 0.9, 7000), f2s(HITS['H-claim']))

# Act II — measurement (6.0–15.0 s), 120 bpm quarters = every 15 frames
add(pad_chord([110.0, 164.81, 220.0, 329.63], 9.4, 0.16, 900), f2s(180))
for k, fr in enumerate(range(180, 450, 15)):          # pulse build
    g = 0.30 + 0.30 * (k / 18)
    add(kick(g, click=0.35 + 0.3 * k / 18), f2s(fr))
    if fr + 8 < 450:
        s, pan = hat(0.10 + 0.10 * k / 18, pan=0.25 if k % 2 else -0.25)
        add(s, f2s(fr + 8), pan=pan)
for fr in range(196, 442, 30):                        # counter ticks
    s, pan = tick(0.09, 3200, pan=0.1)
    add(s, f2s(fr), pan=pan)
add(slam(0.80), f2s(HITS['H-t5']))                    # "MEASURE EVERYTHING."
add(slam(0.90), f2s(HITS['H-m1']))                    # F2
add(riser(3.0, 0.34), f2s(300))                       # build into F3
add(slam(1.00), f2s(HITS['H-m2']))                    # F3
add(crash(0.34, 1.0, 8000), f2s(HITS['H-m2']))

# Act III — verdict (15.0–22.0 s)
add(sub_drop(1.05), f2s(HITS['H-verdict']))           # F4 white-out
add(crash(0.55, 1.6, 11000), f2s(HITS['H-verdict']))
add(slam(0.95), f2s(HITS['H-proof']))                 # hero PROOF
add(pad_chord([87.31, 130.81, 174.61, 261.63], 7.2, 0.20, 1100), f2s(483))
add(stab([220.0, 277.18, 329.63], 0.85), f2s(HITS['H-stab1']))   # MEASURED.
add(stab([246.94, 311.13, 369.99], 0.85), f2s(HITS['H-stab2']))  # REPRODUCIBLE.
add(stab([261.63, 329.63, 392.00], 0.95), f2s(HITS['H-signed'])) # SIGNED. + F5
add(crash(0.22, 0.5, 9000), f2s(HITS['H-signed']))

# Act IV — receipt (22.0–25.0 s)
add(pad_chord([87.31, 110.0, 130.81, 174.61, 220.0], 3.6, 0.22, 800), f2s(660))
add(stamp(1.00), f2s(HITS['H-receipt']))              # F6 receipt stamp
s, pan = tick(0.20, 1800, pan=0.0)                    # final tick
add(s, f2s(HITS['H-last']))
fade = int(0.35 * SR)                                 # documented design fade
L[-fade:] *= np.linspace(1, 0, fade) ** 1.5
R[-fade:] *= np.linspace(1, 0, fade) ** 1.5

# ------------------------------------------------------------------ mixdown
mix = np.stack([L, R], axis=1)
mix = np.tanh(mix * 1.15) * 0.85                     # gentle soft clip
peak = np.max(np.abs(mix))
mix = mix / peak * 0.891                             # -1.0 dBFS headroom pre-loudnorm

out = sys.argv[2] if len(sys.argv) > 2 else 'audio/master_pre.wav'
pcm = (mix * 32767).astype('<i2')
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f'wrote {out}: {len(mix)/SR:.3f}s peak={peak:.3f}')
