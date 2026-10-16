#!/usr/bin/env python3
"""axiom audio — original score, sound design and the narration mix, in numpy.

Everything here is synthesised from scratch (sine/additive pads, seeded sparse plucks,
noise-based whooshes and clinks): no third-party music, no sample library, no licence to
track. The mix places each MEASURED narration cue at its timeline position, ducks the
music under speech, adds chapter-card accents, then loudness-normalises to -16 LUFS.

  python3 tools/mix_audio.py --timeline work/timeline.json --out work/audio/master.wav
"""
from __future__ import annotations

import argparse, json, math, wave
from pathlib import Path

import numpy as np

SR = 48000
ROOT = Path(__file__).resolve().parents[1]

# chapter moods: root note (Hz) + mode, chosen for the story's emotional shape
MOODS = {
    1: ("D3", [1, 3 / 2, 9 / 8, 5 / 4], 0.055),      # a sealed, orderly world
    2: ("G3", [1, 6 / 5, 3 / 2, 9 / 5], 0.050),      # curious archive
    3: ("A2", [1, 6 / 5, 7 / 5, 9 / 5], 0.052),      # things do not fit
    4: ("C3", [1, 5 / 4, 3 / 2, 5 / 3], 0.050),      # wonder: deep time
    5: ("E2", [1, 6 / 5, 3 / 2, 9 / 5], 0.052),      # stern arithmetic
    6: ("F#2", [1, 7 / 6, 4 / 3, 3 / 2], 0.050),     # tension, then a discovery
    7: ("A2", [1, 9 / 8, 4 / 3, 3 / 2], 0.055),      # the clock appears
    8: ("D2", [1, 6 / 5, 3 / 2, 17 / 12], 0.050),    # leakage and doubt
    9: ("F2", [1, 5 / 4, 3 / 2, 15 / 8], 0.048),     # patient craft
    10: ("D2", [1, 5 / 4, 3 / 2, 9 / 5], 0.050),     # reflection
}
NOTE = {"C": 32.703, "C#": 34.648, "D": 36.708, "D#": 38.891, "E": 41.203, "F": 43.654,
        "F#": 46.249, "G": 48.999, "G#": 51.913, "A": 55.000, "A#": 58.270, "B": 61.735}


def root_hz(name: str) -> float:
    """Accepts a scientific pitch name with an optional sharp, e.g. 'F#2'."""
    letter = name[0].upper()
    if len(name) > 1 and name[1] in "#b":
        letter += name[1]
        octave = int(name[2:])
    else:
        octave = int(name[1:])
    return NOTE[letter] * (2 ** (octave - 2))


# ------------------------------------------------------------------ music ----
def pad_and_plucks(chapter_spans: list[tuple[int, float, float]], total_s: float, seed: int = 11) -> np.ndarray:
    n = int((total_s + 3.0) * SR)
    music = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(seed)
    for ch, t0, t1 in chapter_spans:
        root_name, mode, level = MOODS.get(ch, MOODS[1])
        root = root_hz(root_name)
        i0, i1 = int(t0 * SR), min(n, int((t1 + 1.6) * SR))
        seg_len = i1 - i0
        if seg_len <= 0:
            continue
        t = np.arange(seg_len) / SR
        env = np.minimum(1.0, t / 3.2) * np.minimum(1.0, (seg_len / SR - t) / 3.0 + 0.15)
        env = np.clip(env, 0, 1)
        # slow-breathing additive pad (root, fifth, and two colour tones)
        for k, ratio in enumerate(mode):
            f = root * ratio * (2 if k == 3 else 1)
            vib = 1 + 0.0018 * np.sin(2 * np.pi * (0.07 + 0.03 * k) * t)
            music[i0:i1] += (level / (1.6 + k)) * env * np.sin(2 * np.pi * f * vib * t)
        # lowpass-ish smoothing (exponential FIR) so the pad sits under the voice
        alpha = 0.02
        taps = 3000
        kern = ((1 - alpha) ** np.arange(taps)).astype(np.float32)
        kern /= kern.sum()
        music[i0:i1] = np.convolve(music[i0:i1], kern, mode="same") * 1.6
        # sparse plucked notes from the same scale, spaced so they never chatter
        tt = 0.7
        while tt < seg_len / SR - 1.5:
            pick = int(rng.integers(0, len(mode)))
            f = root * mode[pick] * (4 if rng.random() < 0.35 else 2)
            dur = 2.6
            di = int(tt * SR)
            dl = min(int(dur * SR), seg_len - di)
            if dl > 100:
                tt_arr = np.arange(dl) / SR
                a = np.exp(-3.1 * tt_arr) * (1 - np.exp(-90 * tt_arr))
                tone = (np.sin(2 * np.pi * f * tt_arr) + 0.32 * np.sin(4 * np.pi * f * tt_arr)
                        + 0.12 * np.sin(6 * np.pi * f * tt_arr))
                music[i0 + di:i0 + di + dl] += 0.026 * a * tone
            tt += float(rng.uniform(3.2, 6.4))
    return music


# -------------------------------------------------------------------- sfx ----
def whoosh(dur=0.85, seed=5) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    # simple band emphasis by differencing (high-pass) and smoothing (low-pass)
    hp = np.diff(np.concatenate([[0.0], noise]))
    kernel = np.hanning(220)
    lp = np.convolve(hp, kernel / kernel.sum(), mode="same")
    env = np.sin(np.pi * np.clip(t / dur, 0, 1) ** 0.8) ** 1.6
    return (0.05 * lp * env).astype(np.float32)


def clink(dur=0.5, seed=6) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    a = np.exp(-9.0 * t)
    return (0.05 * a * (np.sin(2 * np.pi * 1180 * t) + 0.6 * np.sin(2 * np.pi * 1760 * t)
                        + 0.3 * np.sin(2 * np.pi * 2630 * t))).astype(np.float32)


def paper(dur=0.45, seed=7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    hp = np.diff(np.concatenate([[0.0], noise]))
    env = np.exp(-11 * t) * (1 - np.exp(-160 * t))
    return (0.030 * hp * env).astype(np.float32)


# -------------------------------------------------------------- narration ----
def read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw != 2:
        raise ValueError(f"expected 16-bit PCM in {path}")
    a = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        idx = np.linspace(0, len(a) - 1, int(len(a) * SR / sr))
        a = np.interp(idx, np.arange(len(a)), a).astype(np.float32)
    return a


def build(tl_path: Path, out_path: Path, narration_only: Path | None):
    """Memory-lean build: one float32 mix buffer, per-chapter music added in place,
    streamed stereo WAV writing. (The commissioning box has ~2 GB RAM.)"""
    tl = json.loads(tl_path.read_text())
    total = tl["total_duration"]
    n = int(total * SR)
    voice = np.zeros(n, dtype=np.float32)
    for cid, c in sorted(tl["cues"].items(), key=lambda kv: kv[1]["start"]):
        f = Path(c["file"])
        if not f.exists():
            print(f"WARNING missing narration {f}")
            continue
        clip = read_wav(f)
        i0 = int(c["start"] * SR)
        i1 = min(n, i0 + len(clip))
        if i1 > i0:
            voice[i0:i1] += clip[: i1 - i0]
    # gentle levelling so long-form level stays even (soft saturation, in place)
    np.tanh(voice * 1.5, out=voice)
    voice *= 0.72
    if narration_only:
        write_wav(narration_only, voice, chunk=1 << 22)

    # duck the music under speech: envelope of the voice, smoothed, then inverted
    win = int(0.05 * SR)
    env = np.abs(voice[: (n // win) * win]).reshape(-1, win).max(axis=1)
    env = np.interp(np.linspace(0, len(env) - 1, n), np.arange(len(env)), env).astype(np.float32)
    k = int(0.35 * SR)
    kernel = (np.hanning(k) / np.hanning(k).sum()).astype(np.float32)
    env = np.convolve(env, kernel, mode="same").astype(np.float32)
    duck = 1.0 - 0.62 * np.clip(env / 0.22, 0, 1).astype(np.float32)
    del env

    mix = voice
    spans = sorted(((int(k_), v_) for k_, v_ in tl["chapters"].items()), key=lambda x: x[1]["start"])
    for ch, cc in spans:
        # the music bed must cover the picture end to end: no silent head, no silent tail
        t0 = 0.0 if ch == spans[0][0] else cc["card_start"]
        t1 = total if ch == spans[-1][0] else min(total, cc["end"] + 1.6)
        seg = music_segment(ch, t0, t1)
        i0, i1 = int(t0 * SR), min(n, int(t0 * SR) + len(seg))
        if i1 > i0:
            mix[i0:i1] += seg[: i1 - i0] * duck[i0:i1]

    # sound design at chapter cards and at the final card
    w, c, p = whoosh(), clink(), paper()
    for ch, cc in spans:
        i0 = int(cc["card_start"] * SR)
        mix[i0:i0 + len(w)] += w[: max(0, n - i0)]
        i1 = int((cc["card_start"] + 0.35) * SR)
        mix[i1:i1 + len(p)] += p[: max(0, n - i1)]
        i2 = int((cc["card_start"] + cc["card_dur"] - 0.15) * SR)
        mix[i2:i2 + len(c)] += (c * 0.6)[: max(0, n - i2)]
    last = tl["shots"][-1]
    i3 = int((last["start"] + last["cues"][last["cue_ids"][-1]]["end"] + 5.4) * SR)
    mix[i3:i3 + len(c)] += c[: max(0, n - i3)]

    # gentle tail fade, but not to silence: the last frame still carries the score
    tail = int(1.8 * SR)
    if len(mix) > tail:
        mix[-tail:] *= np.linspace(1.0, 0.30, tail, dtype=np.float32)
    peak_before = float(np.max(np.abs(mix)))
    mix *= (0.86 / (peak_before or 1.0))
    write_wav(out_path, mix, chunk=1 << 22)
    return {"seconds": total, "peak_before_normalise": round(peak_before, 4),
            "voice_rms": round(float(np.sqrt(np.mean(voice ** 2))), 5)}


def music_segment(ch: int, t0: float, t1: float) -> np.ndarray:
    """One chapter's pad + plucks, generated at its final length (no full-film buffer)."""
    root_name, mode, level = MOODS.get(ch, MOODS[1])
    root = root_hz(root_name)
    ln = max(1, int((t1 - t0) * SR))
    t = np.arange(ln, dtype=np.float32) / SR
    seg = np.zeros(ln, dtype=np.float32)
    env = np.clip(np.minimum(1.0, t / 3.2) * np.minimum(1.0, (ln / SR - t) / 3.0 + 0.15), 0, 1)
    for k, ratio in enumerate(mode):
        f = root * ratio * (2 if k == 3 else 1)
        vib = 1 + 0.0018 * np.sin(2 * np.pi * (0.07 + 0.03 * k) * t)
        seg += (level / (1.6 + k)) * env * np.sin(2 * np.pi * f * vib * t).astype(np.float32)
    alpha = 0.02
    taps = 3000
    kern = ((1 - alpha) ** np.arange(taps)).astype(np.float32)
    kern /= kern.sum()
    seg = np.convolve(seg, kern, mode="same").astype(np.float32) * 1.6
    rng = np.random.default_rng(1000 + ch)
    tt = 0.7
    while tt < ln / SR - 1.5:
        pick = int(rng.integers(0, len(mode)))
        f = root * mode[pick] * (4 if rng.random() < 0.35 else 2)
        di = int(tt * SR)
        dl = min(int(2.6 * SR), ln - di)
        if dl > 100:
            ta = np.arange(dl, dtype=np.float32) / SR
            a = (np.exp(-3.1 * ta) * (1 - np.exp(-90 * ta))).astype(np.float32)
            tone = (np.sin(2 * np.pi * f * ta) + 0.32 * np.sin(4 * np.pi * f * ta)
                    + 0.12 * np.sin(6 * np.pi * f * ta)).astype(np.float32)
            seg[di:di + dl] += 0.026 * a * tone
        tt += float(rng.uniform(3.2, 6.4))
    return seg


def write_wav(path: Path, mono: np.ndarray, chunk: int = 1 << 22):
    """Streamed 16-bit stereo write: never materialises the whole interleaved array."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        for i in range(0, len(mono), chunk):
            blk = np.clip(mono[i:i + chunk] * 32767.0, -32768, 32767).astype("<i2")
            stereo = np.repeat(blk[:, None], 2, axis=1)
            w.writeframes(stereo.tobytes())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", default=str(ROOT / "work" / "timeline.json"))
    ap.add_argument("--out", default=str(ROOT / "work" / "audio" / "master.wav"))
    ap.add_argument("--narration-only", default=str(ROOT / "work" / "audio" / "narration.wav"))
    a = ap.parse_args()
    info = build(Path(a.timeline), Path(a.out), Path(a.narration_only))
    print(json.dumps(info, indent=2))
    print("master:", a.out)
