"""parallax procedural score — deterministic, frame-exact, no samples.

Hero: drone bed + camera-speed air + event cues from the scene JSON.
Loop: every oscillator an integer multiple of 1/10.24 Hz => seamless wrap.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

SR = 48000


def _rng(seed):
    return np.random.default_rng(seed)


def _t(n):
    return np.arange(n, dtype=np.float64) / SR


def _env_exp(n, tau):
    return np.exp(-_t(n) / tau)


def _noise(n, rng):
    return rng.uniform(-1, 1, n)


def _onepole_lp(x, cutoff):
    a = math.exp(-2 * math.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = a * acc + (1 - a) * x[i]
        y[i] = acc
    return y


def _bp(x, f0, q=6.0):
    """cheap bandpass: lp(x) - lp(lp(x)) shifted; adequate for air/whoosh."""
    lp1 = _onepole_lp(x, f0 * (1 + 1.0 / q))
    lp2 = _onepole_lp(lp1, f0 * (1 + 1.0 / q))
    hp = _onepole_lp(x, f0 / q)
    return lp1 - lp2 - (x - hp) * 0.0


def _sweep_bp(x, f_start, f_end, q=5.0):
    """time-varying resonant filter via per-block one-pole (blocks of 512)."""
    n = len(x)
    out = np.empty_like(x)
    B = 512
    nb = int(math.ceil(n / B))
    acc = 0.0
    acc2 = 0.0
    for b in range(nb):
        u = b / max(1, nb - 1)
        fc = f_start * (f_end / f_start) ** u
        a = math.exp(-2 * math.pi * fc / SR)
        s = slice(b * B, min(n, (b + 1) * B))
        xb = x[s]
        y1 = np.empty_like(xb)
        y2 = np.empty_like(xb)
        for i in range(len(xb)):
            acc = a * acc + (1 - a) * xb[i]
            acc2 = a * acc2 + (1 - a) * acc
            y1[i] = acc
            y2[i] = acc2
        out[s] = (y1 - y2) * (1 + q) * 0.5
    return out


def _place(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    n = min(len(sig), len(buf[0]) - i0)
    if n <= 0:
        return
    gl = gain * math.sqrt(0.5 * (1 - pan))
    gr = gain * math.sqrt(0.5 * (1 + pan))
    buf[0][i0:i0 + n] += sig[:n] * gl
    buf[1][i0:i0 + n] += sig[:n] * gr


def cam_speed_curve(scene_path, dur, hz=50.0):
    sys.path.insert(0, str(Path(__file__).resolve().parent / "engine"))
    from scene import Scene
    sc = Scene(scene_path)
    ts = np.arange(0, dur, 1.0 / hz)
    pts = np.array([sc.camera(float(t)).pos for t in ts])
    v = np.linalg.norm(np.diff(pts, axis=0), axis=1) * hz
    v = np.concatenate([v, v[-1:]])
    # upsample to audio rate with smoothing
    x = np.arange(len(v))
    xi = np.clip(np.arange(int(dur * SR)) / SR * hz, 0, len(v) - 1)
    curve = np.interp(xi, x, v)
    k = int(SR * 0.25)
    ker = np.hanning(k)
    ker /= ker.sum()
    return np.convolve(curve, ker, mode="same")


def hero_audio(scene_path, out, dur=None):
    d = json.load(open(scene_path))
    dur = dur or d["duration"]
    n = int(dur * SR)
    t = _t(n)
    rng = _rng(20261016)
    L = np.zeros(n); R = np.zeros(n)
    buf = [L, R]

    # ---- drone bed: detuned partials, slow morph
    parts = [(55.0, 0.30), (55.0 * 1.006, 0.22), (82.5, 0.14), (110.0, 0.10), (165.0, 0.05)]
    bed = np.zeros(n)
    for f, a in parts:
        ph = rng.uniform(0, 2 * math.pi)
        lfo = 0.75 + 0.25 * np.sin(2 * math.pi * 0.055 * t + ph * 0.3)
        bed += a * lfo * np.sin(2 * math.pi * f * t + ph)
    bed *= 0.55
    # paper-world lift: brighten bed between 25-33s
    lift = np.clip((t - 24.5) / 1.2, 0, 1) * np.clip((33.0 - t) / 1.5, 0, 1)
    bed += lift * 0.10 * np.sin(2 * math.pi * 220.0 * t) * (0.6 + 0.4 * np.sin(2 * math.pi * 0.4 * t))
    _place(buf, bed, 0.0, 0.9)

    # ---- air: filtered noise, cutoff/level follow camera speed
    speed = cam_speed_curve(scene_path, dur)
    sn = np.clip(speed / max(1e-6, np.percentile(speed, 97)), 0, 1.4)
    noise = _noise(n, rng)
    air = _sweep_bp(noise, 240, 240, q=1.0)  # placeholder, replaced below block-wise
    air = np.empty(n)
    B = 2048
    acc = 0.0
    acc2 = 0.0
    for b in range(0, n, B):
        s = slice(b, min(n, b + B))
        u = sn[s].mean()
        fc = 300 + 2600 * min(1.0, u)
        a = math.exp(-2 * math.pi * fc / SR)
        xb = noise[s]
        y1 = np.empty_like(xb); y2 = np.empty_like(xb)
        for i in range(len(xb)):
            acc = a * acc + (1 - a) * xb[i]
            acc2 = a * acc2 + (1 - a) * acc
            y1[i] = acc; y2[i] = acc2
        air[s] = (y1 - y2) * (0.35 + 1.5 * min(1.0, u))
    _place(buf, air, 0.0, 0.30)

    # ---- cues
    for c in d.get("cues", []):
        k = c["kind"]; t0 = c["t"]
        pan = c.get("pan", 0.0)
        if k == "ignite":
            s = _env_exp(int(1.6 * SR), 0.5) * np.sin(2 * math.pi * 330 * _t(int(1.6 * SR)))
            _place(buf, s, t0, 0.22, pan)
        elif k == "whoosh":
            m = int(1.5 * SR)
            s = _sweep_bp(_noise(m, rng), 180, 1900, q=4.0) * np.sin(np.pi * np.arange(m) / m) ** 1.5
            _place(buf, s, t0, 0.55, -0.3)
        elif k == "tick":
            m = int(0.22 * SR)
            f0 = 1500 + 900 * ((int(round(t0, 1) * 10) % 7) / 7.0)
            tt = _t(m)
            s = (_env_exp(m, 0.035) * np.sin(2 * math.pi * f0 * tt)
                 + 0.6 * _env_exp(m, 0.022) * np.sin(2 * math.pi * f0 * 2.76 * tt)
                 + 0.5 * _env_exp(m, 0.05) * np.sin(2 * math.pi * 140 * tt))
            _place(buf, s, t0, 0.30, pan)
        elif k == "gate":
            m = int(0.9 * SR)
            tt = _t(m)
            f = 75 * np.power(45 / 75, tt / 0.9)
            s = _env_exp(m, 0.22) * np.sin(2 * math.pi * np.cumsum(f) / SR)
            s += 0.4 * _sweep_bp(_noise(m, rng), 900, 240, q=3.0) * _env_exp(m, 0.15)
            _place(buf, s, t0, 0.5, pan)
        elif k == "swell":
            m = int(1.4 * SR)
            u = np.arange(m) / m
            s = _sweep_bp(_noise(m, rng), 200, 1500, q=3.0) * u ** 2.5
            _place(buf, s, t0, 0.42, pan)
        elif k == "boom":
            m = int(1.6 * SR)
            tt = _t(m)
            f = 60 * np.power(28 / 60, tt / 1.6)
            s = _env_exp(m, 0.5) * np.sin(2 * math.pi * np.cumsum(f) / SR)
            s += 0.25 * _onepole_lp(_noise(m, rng), 220) * _env_exp(m, 0.3)
            _place(buf, s, t0, 0.62, pan)
        elif k == "chime":
            m = int(2.2 * SR)
            tt = _t(m)
            s = sum(a * _env_exp(m, tau) * np.sin(2 * math.pi * f * tt + rng.uniform(0, 6))
                    for f, a, tau in [(880, 0.5, 0.7), (1320, 0.3, 0.5), (1760, 0.18, 0.35)])
            _place(buf, s, t0, 0.24, pan)
        elif k == "settle":
            m = int(3.0 * SR)
            tt = _t(m)
            s = 0.4 * np.sin(2 * math.pi * 110 * tt) * np.clip(tt / 1.2, 0, 1) * _env_exp(m, 2.2)
            s += 0.12 * _env_exp(m, 1.4) * np.sin(2 * math.pi * 660 * tt)
            _place(buf, s, t0, 0.4, pan)

    stereo = np.stack([L, R])
    # soft clip
    stereo = np.tanh(stereo * 1.1) / np.tanh(1.1)
    write_wav(out, stereo)
    return out


def loop_audio(out, dur=10.24, seed=7):
    n = int(round(dur * SR))          # 491520 = 480 AAC frames
    t = _t(n)
    rng = _rng(seed)
    f0 = 1.0 / dur                    # 0.09765625 Hz
    L = np.zeros(n); R = np.zeros(n)
    # harmonic drone (integer multiples of f0 => periodic)
    for k, a in [(560, 0.30), (561, 0.16), (840, 0.12), (1120, 0.08), (1681, 0.04)]:
        ph = rng.uniform(0, 2 * math.pi)
        L += a * np.sin(2 * math.pi * k * f0 * t + ph)
        R += a * np.sin(2 * math.pi * k * f0 * t + ph + 0.35)
    # periodic air: inverse-FFT of harmonic comb with random phases
    spec = np.zeros(n // 2 + 1, dtype=complex)
    idx = np.arange(300, 5000)
    ph = rng.uniform(0, 2 * math.pi, len(idx))
    amp = (1.0 / (idx ** 0.8)) * 12.0
    spec[idx] = amp * np.exp(1j * ph)
    air = np.fft.irfft(spec, n)
    air /= max(1e-9, np.abs(air).max())
    L += 0.16 * air
    R += 0.16 * np.roll(air, n // 7)
    # orbit tick per quarter period (periodic)
    for q in range(4):
        i0 = int(q * n / 4)
        m = int(0.25 * SR)
        tt = _t(m)
        s = _env_exp(m, 0.05) * np.sin(2 * math.pi * (1400 + 300 * q) * tt) * 0.5
        m = min(m, n - i0)
        L[i0:i0 + m] += s[:m] * 0.22
        R[i0:i0 + m] += s[:m] * 0.22
    stereo = np.stack([L, R])
    stereo = np.tanh(stereo * 1.05) / np.tanh(1.05)
    write_wav(out, stereo)
    return out


def write_wav(path, stereo):
    import wave
    x = np.clip(stereo, -1, 1)
    xi = (x * 32767.0).T.astype("<i2")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(xi.tobytes())
    print(f"wrote {path}: {len(stereo[0])} stereo samples, {len(stereo[0])/SR:.6f}s at {SR} Hz")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["hero", "loop"], default="hero")
    ap.add_argument("--scene", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--duration", type=float, default=None)
    a = ap.parse_args()
    if a.kind == "hero":
        hero_audio(a.scene or str(Path(__file__).parent / "scenes_px" / "hero.json"), a.out, a.duration)
    else:
        loop_audio(a.out)
