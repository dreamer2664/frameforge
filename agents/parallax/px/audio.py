#!/usr/bin/env python3
"""Original composed score for the parallax KINETIC film.

Everything is synthesised: no samples, no external audio assets.

hero  : 40.0 s, 48 kHz, five movements matched to the storyboard beats.
loop  : 9.6 s, 48 kHz, strictly periodic so the audio seam is exact.

The mix is deliberately sparse: a low stone drone, dry percussive taps
synced to the reveal of each carved letter, hinge scrapes when the stone
lets go, a rising cluster for the gate, and one warm chord for the
monument.  A synthetic room is applied to place everything in a hall.
"""
from __future__ import annotations

import argparse
import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, lfilter

SR = 48000
FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")
FFPROBE = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffprobe")


# ----------------------------------------------------------------- utilities
def noise(n, rng):
    return rng.standard_normal(n).astype(np.float32)


def lowpass(x, cutoff, order=2, sr=SR):
    b, a = butter(order, cutoff / (sr * 0.5), btype="low")
    return lfilter(b, a, x).astype(np.float32)


def highpass(x, cutoff, order=2, sr=SR):
    b, a = butter(order, cutoff / (sr * 0.5), btype="high")
    return lfilter(b, a, x).astype(np.float32)


def bandpass(x, lo, hi, order=2, sr=SR):
    b, a = butter(order, [lo / (sr * 0.5), hi / (sr * 0.5)], btype="band")
    return lfilter(b, a, x).astype(np.float32)


def env(n, attack, decay, sustain=0.0, hold=0.0, release=0.0, sr=SR):
    """Simple ADSR over n samples."""
    a = max(int(attack * sr), 1)
    d = max(int(decay * sr), 1)
    h = max(int(hold * sr), 0)
    r = max(int(release * sr), 0)
    s = max(n - a - d - h - r, 0)
    parts = []
    parts.append(np.linspace(0.0, 1.0, a, dtype=np.float32))
    parts.append(np.linspace(1.0, sustain, d, dtype=np.float32))
    if h:
        parts.append(np.full(h, sustain, dtype=np.float32))
    if s:
        parts.append(np.full(s, sustain, dtype=np.float32))
    if r:
        parts.append(np.linspace(sustain, 0.0, r, dtype=np.float32))
    e = np.concatenate(parts)
    if len(e) < n:
        e = np.concatenate([e, np.zeros(n - len(e), dtype=np.float32)])
    return e[:n]


def sine(freq, n, sr=SR, phase=0.0):
    t = np.arange(n, dtype=np.float32) / sr
    return np.sin(2 * np.pi * freq * t + phase).astype(np.float32)


def add_at(buf, x, pos):
    """Mix x into buf at sample pos, clipping the tail."""
    pos = int(pos)
    if pos >= len(buf):
        return
    m = min(len(x), len(buf) - pos)
    buf[pos:pos + m] += x[:m]


# ------------------------------------------------------------------ the room
def room_ir(dur=2.2, seed=5, sr=SR):
    """Synthetic hall: exponentially decaying noise with a few early taps."""
    rng = np.random.default_rng(seed)
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    decay = np.exp(-t * 2.6).astype(np.float32)
    ir = noise(n, rng) * decay
    for delay_ms, gain in ((17, 0.5), (29, 0.38), (43, 0.3), (67, 0.22), (101, 0.16)):
        d = int(delay_ms * sr / 1000)
        ir[d] += gain
    ir = lowpass(ir, 5200)
    ir = highpass(ir, 60)
    ir /= np.maximum(np.abs(ir).max(), 1e-9)
    return ir


def convolve(x, ir):
    n = len(x) + len(ir) - 1
    nfft = 1 << int(math.ceil(math.log2(n)))
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)
    return y[:len(x)].astype(np.float32)


# ----------------------------------------------------------------- elements
def drone(dur, sr=SR, seed=11):
    """The stone room tone: a low fifth with a slow beating detune."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    out = np.zeros(n, dtype=np.float32)
    for f, g, det in ((55.0, 0.55, 0.13), (82.5, 0.30, 0.19), (110.0, 0.16, 0.07)):
        for d in (-det, det):
            ph = 2 * np.pi * (f + d) * t
            out += g * 0.5 * np.sin(ph).astype(np.float32)
    # a very slow breathing amplitude
    out *= (0.75 + 0.25 * np.sin(2 * np.pi * 0.045 * t)).astype(np.float32)
    out = lowpass(out, 400)
    return out


def stone_tap(sr=SR, seed=3, dur=0.5, bright=900.0):
    """A dry struck-stone tick."""
    n = int(dur * sr)
    rng = np.random.default_rng(seed)
    x = noise(n, rng)
    x = bandpass(x, 180, bright)
    x *= env(n, 0.0008, dur, sr=sr) ** 2.2
    body = sine(132.0, n) * env(n, 0.002, 0.20, sr=sr) * 0.5
    return (x * 0.9 + body).astype(np.float32)


def hinge_scrape(dur, seed=7, sr=SR):
    """Stone sliding on stone."""
    n = int(dur * sr)
    rng = np.random.default_rng(seed)
    x = noise(n, rng)
    x = bandpass(x, 260, 2400)
    e = env(n, 0.18, 0.1, sustain=0.7, hold=dur * 0.45, release=dur * 0.35, sr=sr)
    x *= e
    # a rubbing amplitude modulation
    t = np.arange(n, dtype=np.float32) / sr
    x *= (0.6 + 0.4 * np.sin(2 * np.pi * 7.5 * t + seed)).astype(np.float32)
    return x


def sub_swell(dur, f0=38.0, f1=26.0, sr=SR):
    """A slow descending sub for the release."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    k = t / max(dur, 1e-6)
    phase = 2 * np.pi * (f0 * t + (f1 - f0) * t * t / (2 * max(dur, 1e-6)))
    x = np.sin(phase).astype(np.float32)
    x *= env(n, 1.2, 0.8, sustain=0.85, hold=dur * 0.4, release=dur * 0.25, sr=sr)
    return x


def rising_cluster(dur, seed=9, sr=SR):
    """A harmonic cluster that tightens as the gate assembles."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    k = np.clip(t / max(dur, 1e-6), 0, 1)
    out = np.zeros(n, dtype=np.float32)
    base = 220.0
    for i, mult in enumerate((1, 1.5, 2, 3, 4, 5, 6)):
        f = base * mult * (1.0 + 0.06 * k * i)
        amp = (0.16 / (1 + 0.5 * i)) * (0.25 + 0.75 * k)
        out += amp * np.sin(2 * np.pi * f * t).astype(np.float32)
    # a tremolo that speeds up
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * (1.2 + 5.5 * k) * t).astype(np.float32)
    out *= trem
    out = lowpass(out, 5200)
    return out


def impact(dur=2.4, seed=13, sr=SR):
    """The camera passing through the gate: a body hit with a long tail."""
    n = int(dur * sr)
    rng = np.random.default_rng(seed)
    x = noise(n, rng)
    x = lowpass(x, 2600)
    x *= env(n, 0.002, dur, sr=sr) ** 1.6
    body = sine(58.0, n) * env(n, 0.003, 1.2, sr=sr) * 0.8
    body += sine(87.0, n) * env(n, 0.003, 0.7, sr=sr) * 0.35
    return (x * 0.7 + body).astype(np.float32)


def chord(dur, freqs=(220.0, 329.63, 415.30, 659.26), sr=SR):
    """The monument: one warm chord that breathes."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    out = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(freqs):
        for d in (-0.09, 0.09):
            amp = 0.30 / (1 + 0.45 * i)
            out += amp * np.sin(2 * np.pi * (f + d) * t).astype(np.float32)
    out *= (0.72 + 0.28 * np.sin(2 * np.pi * 0.08 * t)).astype(np.float32)
    out = lowpass(out, 3200)
    return out


def shimmer(dur, cycles, sr=SR, seed=17):
    """A periodic band of air that opens and closes once per loop."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    rng = np.random.default_rng(seed)
    x = noise(n, rng)
    x = bandpass(x, 2400, 7000)
    x *= (0.35 + 0.65 * np.sin(2 * np.pi * cycles * t / dur)).astype(np.float32)
    return x


def limit(x, knee=0.22, ceiling=0.72):
    """Soft-knee limiter: keeps transients from pushing the true peak over
    the delivery limit, so the mix can still sit at the target loudness."""
    a = np.abs(x)
    over = np.maximum(a - knee, 0.0)
    comp = knee + over / (1.0 + over / max(ceiling - knee, 1e-6))
    y = np.sign(x) * np.minimum(a, comp)
    return y.astype(np.float32)


# --------------------------------------------------------------------- mix
def hero(dur=40.0, sr=SR):
    n = int(dur * sr)
    rng = np.random.default_rng(2024)
    L = np.zeros(n, dtype=np.float32)
    R = np.zeros(n, dtype=np.float32)

    # --- movement 1: the room tone, quiet
    d = drone(dur, sr)
    env1 = env(n, 2.2, 1.0, sustain=0.55, hold=dur * 0.5, release=3.0, sr=sr)
    d = d * env1 * 0.5
    L += d
    R += d * 0.97

    # --- movement 2: one dry tap per revealed letter
    for i, t0 in enumerate((6.00, 6.85, 7.70, 8.55, 9.40, 10.25, 11.10)):
        tap = stone_tap(sr=sr, seed=30 + i, bright=700 + 120 * i) * 0.55
        pan = (i / 6.0 - 0.5) * 0.5
        add_at(L, tap * (0.5 - pan * 0.5), t0 * sr)
        add_at(R, tap * (0.5 + pan * 0.5), t0 * sr)

    # --- movement 3: the stone lets go
    sw = sub_swell(4.6, sr=sr) * 0.85
    add_at(L, sw, 14.4 * sr)
    add_at(R, sw, 14.4 * sr)
    for i in range(7):
        sc = hinge_scrape(1.9, seed=40 + i, sr=sr) * (0.30 - 0.02 * i)
        t0 = 15.0 + i * 0.15
        pan = (i / 6.0 - 0.5) * 0.8
        add_at(L, sc * (0.5 - pan * 0.5), t0 * sr)
        add_at(R, sc * (0.5 + pan * 0.5), t0 * sr)

    # --- movement 4: the gate
    cl = rising_cluster(7.4, sr=sr) * 0.55
    add_at(L, cl, 22.0 * sr)
    add_at(R, cl * 0.96, 22.0 * sr)
    for i, t0 in enumerate((22.4, 24.2, 25.6, 26.8, 27.8, 28.6)):
        tap = stone_tap(sr=sr, seed=60 + i, bright=520 + 150 * i) * 0.4
        add_at(L, tap, t0 * sr)
        add_at(R, tap, t0 * sr)

    # --- the passage through
    im = impact(sr=sr) * 0.9
    add_at(L, im, 29.3 * sr)
    add_at(R, im, 29.3 * sr)

    # --- movement 5: the monument
    ch = chord(dur - 29.0, sr=sr) * 0.85
    ce = env(n - int(29.0 * sr), 2.0, 1.0, sustain=0.75, hold=4.0, release=3.5, sr=sr)
    ch = ch * ce
    add_at(L, ch, 29.0 * sr)
    add_at(R, ch * 0.95, 29.0 * sr)
    for i, t0 in enumerate((32.2, 33.4, 34.6, 35.8)):
        tap = stone_tap(sr=sr, seed=80 + i, bright=420 + 90 * i) * 0.30
        add_at(L, tap, t0 * sr)
        add_at(R, tap, t0 * sr)

    # --- a breath of air in the last movement
    sh = shimmer(dur - 31.0, cycles=1, sr=sr) * 0.05
    add_at(L, sh, 31.0 * sr)
    add_at(R, sh * 0.9, 31.0 * sr)

    # --- the hall
    ir = room_ir()
    wetL = convolve(L, ir) * 0.34
    wetR = convolve(R, ir * 0.93) * 0.34
    L = L * 0.86 + wetL
    R = R * 0.86 + wetR
    L = limit(L)
    R = limit(R)

    # fade the very first and last instants so nothing clicks
    fade = int(0.05 * sr)
    L[:fade] *= np.linspace(0, 1, fade).astype(np.float32)
    R[:fade] *= np.linspace(0, 1, fade).astype(np.float32)
    L[-fade:] *= np.linspace(1, 0, fade).astype(np.float32)
    R[-fade:] *= np.linspace(1, 0, fade).astype(np.float32)
    return np.stack([L, R], axis=1)


def loop(dur=9.6, sr=SR):
    """A strictly periodic score: every partial completes whole cycles, the
    noise is synthesised from periodic partials, and the reverb is circular,
    so the last sample flows into the first with no discontinuity."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    L = np.zeros(n, dtype=np.float32)
    R = np.zeros(n, dtype=np.float32)

    def add_wrap(buf, x, pos):
        pos = int(pos) % len(buf)
        m = min(len(x), len(buf) - pos)
        buf[pos:pos + m] += x[:m]
        if m < len(x):
            buf[:len(x) - m] += x[m:]

    base = 1.0 / dur                       # the fundamental of the loop
    # the drone: partials that are exact multiples of 1/dur
    for mult, g in ((55, 0.42), (82.5, 0.24), (110, 0.15), (165, 0.07), (220, 0.05)):
        f = base * round(mult / base)
        det = base * 1.0
        for d in (-det, det):
            L += g * 0.5 * np.sin(2 * np.pi * (f + d) * t).astype(np.float32)
            R += g * 0.5 * np.sin(2 * np.pi * (f - d) * t + 0.4).astype(np.float32)

    # a raking band of air, built from periodic partials (no noise)
    for k, g in ((3, 0.030), (5, 0.022), (7, 0.016), (11, 0.010), (13, 0.007)):
        f = base * round(2600.0 / base) * 0 + base * round((2600.0 * k / 97.0) / base)
        for d in (0, 1, 2):
            L += g * np.sin(2 * np.pi * (f + d * base) * t + k).astype(np.float32)
            R += g * np.sin(2 * np.pi * (f - d * base) * t + k + 0.7).astype(np.float32)

    # a stone tick four times per loop, its tail wrapping past the seam
    for i, off in enumerate((0.6, 3.0, 5.4, 7.8)):
        tap = stone_tap(sr=sr, seed=90 + i, bright=620 + 90 * i) * 0.42
        add_wrap(L, tap, int(off * sr))
        add_wrap(R, tap, int(off * sr))

    # a sub pulse twice per loop
    for off in (1.2, 6.0):
        n0 = int(dur / 2 * sr)
        x = sine(41.0, n0) * env(n0, 0.25, 0.6, sustain=0.5, hold=0.4, release=0.5, sr=sr) * 0.5
        add_wrap(L, x, int(off * sr))
        add_wrap(R, x, int(off * sr))

    # circular reverb: the tail wraps into the head of the loop
    ir = room_ir(dur=1.6, seed=21)
    L = L * 0.85 + circular_convolve(L, ir) * 0.30
    R = R * 0.85 + circular_convolve(R, ir * 0.94) * 0.30
    L = limit(L, knee=0.26, ceiling=0.78)
    R = limit(R, knee=0.26, ceiling=0.78)
    return np.stack([L, R], axis=1)


def circular_convolve(x, ir):
    """Convolution on a circle: the tail of the impulse response wraps to the
    head, which is what makes a loop seamless."""
    n = len(x)
    # the transform length IS the loop length, so the result is exactly
    # periodic: the impulse tail wraps into the head
    nfft = n
    irf = np.zeros(nfft, dtype=np.float64)
    m = min(len(ir), n)
    irf[:m] = ir[:m]
    y = np.fft.irfft(np.fft.rfft(x.astype(np.float64), nfft) * np.fft.rfft(irf), nfft)
    return y.astype(np.float32)


# ------------------------------------------------------------------- output
def write_wav(path, data, sr=SR, normalise_peak=True):
    """Write a 24-bit PCM WAV (hand-rolled header: the wave module mishandles
    24-bit frames)."""
    import struct
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if normalise_peak:
        peak = float(np.abs(data).max())
        if peak > 0:
            data = data / peak * 0.98
    pcm = np.clip(data, -1.0, 1.0)
    flat = (pcm.reshape(-1) * 8388607.0).astype(np.int32)
    b = np.empty((flat.size, 3), dtype=np.uint8)
    b[:, 0] = flat & 0xFF
    b[:, 1] = (flat >> 8) & 0xFF
    b[:, 2] = (flat >> 16) & 0xFF
    raw = b.tobytes()
    ch = data.shape[1]
    hdr = (b"RIFF" + struct.pack("<I", 36 + len(raw)) + b"WAVE"
           + b"fmt " + struct.pack("<IHHIIHH", 16, 1, ch, sr, sr * ch * 3, ch * 3, 24)
           + b"data" + struct.pack("<I", len(raw)))
    path.write_bytes(hdr + raw)
    return path


def measure(path):
    """Integrated LUFS and true peak via ffmpeg's ebur128 filter."""
    out = subprocess.run(
        [FFMPEG, "-hide_banner", "-nostats", "-i", str(path),
         "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True)
    txt = out.stderr
    lufs = tp = None
    lines = txt.splitlines()
    # the summary block is the authoritative reading
    try:
        k = next(i for i, l in enumerate(lines) if l.strip() == "Summary:")
    except StopIteration:
        k = 0
    for line in lines[k:]:
        parts = line.split()
        for i, tok in enumerate(parts):
            if tok == "I:" and i + 1 < len(parts):
                try:
                    lufs = float(parts[i + 1])
                except ValueError:
                    pass
            if tok == "Peak:" and i + 1 < len(parts):
                try:
                    tp = float(parts[i + 1])
                except ValueError:
                    pass
    if lufs is None:                       # fall back to the last live reading
        for line in reversed(lines):
            if "LUFS" in line and " I:" in line:
                try:
                    lufs = float(line.split("I:")[1].split()[0])
                    break
                except (IndexError, ValueError):
                    pass
    return lufs, tp, txt


def normalise(path, target_lufs=-16.0, target_tp=-1.5):
    """Measure once, apply one static gain (a static gain shifts integrated
    loudness and true peak by exactly the same amount), write once, verify."""
    data = read_wav(path)
    lufs, tp, _txt = measure(path)
    if lufs is None or tp is None:
        return lufs, tp
    gain_db = target_lufs - lufs
    if tp + gain_db > target_tp:
        gain_db = target_tp - tp
    data = data * (10 ** (gain_db / 20.0))
    write_wav(path, data, normalise_peak=False)
    lufs2, tp2, _ = measure(path)
    return lufs2, tp2


def read_wav(path):
    import array
    with wave.open(str(path), "rb") as w:
        ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if sw == 3:
        usable = len(raw) - (len(raw) % 3)
        b = np.frombuffer(raw[:usable], dtype=np.uint8).reshape(-1, 3)
        ints = (b[:, 0].astype(np.int32)
                | (b[:, 1].astype(np.int32) << 8)
                | (b[:, 2].astype(np.int32) << 16))
        ints = np.where(ints & 0x800000, ints - (1 << 24), ints)
        out = ints.astype(np.float32) / 8388608.0
    elif sw == 4:
        a = array.array("i")
        a.frombytes(raw)
        out = np.array(a, dtype=np.float32) / 2147483648.0
    else:
        a = array.array("h")
        a.frombytes(raw)
        out = np.array(a, dtype=np.float32) / 32768.0
    return out.reshape(-1, ch)


def encode(src, dst, bitrate=192000):
    subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
         "-c:a", "aac", "-b:a", str(bitrate), "-ar", "48000", "-ac", "2",
         "-movflags", "+faststart", str(dst)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="work/audio")
    ap.add_argument("--bitrate", type=int, default=192000)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print("composing hero score ...", flush=True)
    h = hero()
    write_wav(out / "hero.wav", h)
    lufs, tp = normalise(out / "hero.wav")
    print(f"  hero: {lufs:.2f} LUFS, true peak {tp:.2f} dBTP", flush=True)
    encode(out / "hero.wav", out / "hero.m4a", args.bitrate)

    print("composing loop score ...", flush=True)
    lp = loop()
    write_wav(out / "loop.wav", lp)
    lufs, tp = normalise(out / "loop.wav")
    print(f"  loop: {lufs:.2f} LUFS, true peak {tp:.2f} dBTP", flush=True)
    encode(out / "loop.wav", out / "loop.m4a", args.bitrate)

    # seam check: the loop's last samples must continue into its first
    d = read_wav(out / "loop.wav")
    step = float(np.abs(d[0] - d[-1]).max())
    print(f"  loop seam step: {step:.5f} (peak {np.abs(d).max():.3f})", flush=True)


if __name__ == "__main__":
    main()
