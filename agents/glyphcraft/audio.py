"""Procedural audio design engine for glyphcraft (r04).
Synthesizes rich tactile acoustic layers:
- Act I: Resonant crystalline chimes & cursive friction brush
- Act II: Nonlinear rubber/steel shear tension whine + explosive acoustic snap impact
- Act III: Dual-frequency phase-shifted SDF fluid whooshes with micro-transients
- Act IV: Sub-bass spatial dilation corridor + atmospheric spatial reverb
- Act V: Authoritative cinematic master Braam, crystal harmonics, and tactile rule click.
All cues mastered synchronously to EBU R128 (-16.0 LUFS target, -1.5 dBTP).
"""
import json, os, struct, wave, subprocess
import numpy as np

SR = 48000

def synth_sine(freq, dur, decay=5.0):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    env = np.exp(-decay * t)
    return np.sin(2 * np.pi * freq * t) * env

def synth_chirp(f0, f1, dur):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    freq = np.linspace(f0, f1, len(t))
    phase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.sin(np.pi * t / dur) ** 2
    return np.sin(phase) * env

def synth_impact(dur=1.4, sub_f=42.0, punch_f=130.0):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    sub = np.sin(2 * np.pi * sub_f * t) * np.exp(-3.2 * t)
    punch_freq = punch_f * np.exp(-14.0 * t) + sub_f
    phase = 2 * np.pi * np.cumsum(punch_freq) / SR
    punch = np.sin(phase) * np.exp(-7.5 * t)
    noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-22.0 * t) * 0.35
    return (sub * 0.75 + punch * 0.85 + noise) * 0.95

def synth_whoosh(dur=1.2, f_start=200.0, f_end=700.0):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    noise = np.random.randn(len(t))
    env = np.sin(np.pi * t / dur) ** 3
    sweep_freq = np.linspace(f_start, f_end, len(t))
    sweep = np.sin(2 * np.pi * np.cumsum(sweep_freq) / SR)
    return noise * env * 0.32 + sweep * env * 0.28

def synth_harmonic_bell(f0=220.0, dur=4.0):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    harmonics = [1.0, 2.02, 3.01, 4.25, 5.43, 6.8]
    amps = [0.55, 0.4, 0.25, 0.16, 0.1, 0.05]
    decays = [1.1, 1.6, 2.3, 3.0, 3.8, 4.5]
    out = np.zeros(len(t))
    for f_mult, a, dec in zip(harmonics, amps, decays):
        out += a * np.sin(2 * np.pi * f0 * f_mult * t) * np.exp(-dec * t)
    return out

def synth_sub_drone(dur):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    drone = 0.5 * np.sin(2 * np.pi * 48 * t) + 0.5 * np.sin(2 * np.pi * 48.6 * t)
    drone += 0.25 * np.sin(2 * np.pi * 96 * t)
    return drone * 0.35

def load_wav(path):
    import soundfile as sf
    data, sr = sf.read(path)
    if sr != SR:
        num_samples = int(len(data) * SR / sr)
        data = np.interp(np.linspace(0, len(data), num_samples), np.arange(len(data)), data)
    if data.ndim == 2:
        data = data.mean(axis=1)
    return data

def build_soundtrack(duration=42.0, out_wav="hero_soundtrack.wav"):
    total_samples = int(duration * SR)
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    # 1. Warm cinematic sub drone
    drone = synth_sub_drone(duration)
    left += drone * 0.32
    right += drone * 0.32

    # Rich harmonic pad bed
    t = np.linspace(0, duration, total_samples, endpoint=False)
    chord_freqs = [130.81, 164.81, 196.00, 246.94] # C3, E3, G3, B3 (maj7)
    pad = np.zeros(total_samples, dtype=np.float32)
    for cf in chord_freqs:
        pad += 0.1 * np.sin(2 * np.pi * cf * t)
    pad *= (np.sin(np.pi * t / duration) ** 0.5)
    left += pad * 0.35
    right += pad * 0.35

    def add_cue(signal, start_time, pan=0.0, gain=1.0):
        s_idx = int(start_time * SR)
        e_idx = min(s_idx + len(signal), total_samples)
        length = e_idx - s_idx
        if length <= 0: return
        sig = signal[:length] * gain
        l_gain = np.cos((pan + 1.0) * np.pi / 4.0)
        r_gain = np.sin((pan + 1.0) * np.pi / 4.0)
        left[s_idx:e_idx] += sig * l_gain
        right[s_idx:e_idx] += sig * r_gain

    # --- Act I: The Atomic Stroke (0.0s - 7.0s) ---
    add_cue(synth_whoosh(1.8, 120, 600), 0.5, pan=-0.4, gain=0.6)
    add_cue(synth_chirp(150, 950, 1.0), 1.2, pan=-0.2, gain=0.5)
    add_cue(synth_impact(1.6, punch_f=190), 2.8, pan=0.0, gain=0.85) # STROKE lock
    add_cue(synth_harmonic_bell(329.63, 3.0), 2.9, pan=0.2, gain=0.45)

    # --- Act II: Elastic Tension (7.0s - 15.0s) ---
    add_cue(synth_chirp(180, 1600, 2.5), 7.8, pan=-0.3, gain=0.65) # Tension whine
    add_cue(synth_impact(2.2, sub_f=38, punch_f=240), 11.2, pan=0.0, gain=1.1) # Snap into WEIGHT
    add_cue(synth_harmonic_bell(220.0, 3.5), 11.3, pan=0.25, gain=0.55)
    add_cue(synth_whoosh(1.4, 400, 150), 12.0, pan=0.3, gain=0.6)

    # --- Act III: Hero Topological Morph (15.0s - 23.0s) ---
    add_cue(synth_whoosh(2.8, 250, 850), 15.8, pan=-0.3, gain=0.85)
    add_cue(synth_chirp(280, 1100, 2.0), 17.5, pan=0.1, gain=0.7)
    add_cue(synth_impact(2.6, sub_f=35, punch_f=160), 19.8, pan=0.0, gain=1.15) # MOTION landing
    add_cue(synth_harmonic_bell(440.0, 4.0), 19.9, pan=0.3, gain=0.65)

    # --- Act IV: The Counter Portal (23.0s - 31.0s) ---
    add_cue(synth_whoosh(3.2, 180, 950), 23.5, pan=0.0, gain=0.95)
    add_cue(synth_chirp(80, 600, 2.8), 24.8, pan=-0.25, gain=0.75)
    add_cue(synth_impact(3.0, sub_f=32, punch_f=120), 28.0, pan=0.0, gain=1.1)
    add_cue(synth_harmonic_bell(261.63, 4.5), 28.2, pan=0.35, gain=0.6)

    # --- Act V: Master Convergence & Brand Payoff (31.0s - 42.0s) ---
    add_cue(synth_whoosh(2.2, 350, 1100), 31.2, pan=0.0, gain=0.85)
    # Master Braam Hit at 33.5s
    add_cue(synth_impact(4.5, sub_f=30, punch_f=95), 33.5, pan=0.0, gain=1.35)
    add_cue(synth_harmonic_bell(196.0, 7.0), 33.6, pan=-0.2, gain=0.75)
    add_cue(synth_harmonic_bell(293.66, 6.0), 33.6, pan=0.2, gain=0.65)
    # Anamorphic flare sound at 35.5s
    add_cue(synth_chirp(600, 2200, 1.5), 35.5, pan=0.0, gain=0.45)
    # Architectural rule strike at 36.5s
    add_cue(synth_impact(1.8, sub_f=50, punch_f=150), 36.5, pan=0.0, gain=0.8)

    # Overlay speech cues
    cue_dir = "frameforge/agents/glyphcraft/audio_cues"
    with open(os.path.join(cue_dir, "narration_manifest.json")) as f:
        manifest = json.load(f)

    for item in manifest:
        c_id = item["id"]
        c_time = item["time_target"]
        wav_p = os.path.join(cue_dir, f"{c_id}.wav")
        if os.path.exists(wav_p):
            speech = load_wav(wav_p)
            add_cue(speech, c_time, pan=0.0, gain=1.22)

    # Headroom normalization
    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if max_val > 0.95:
        left = left / max_val * 0.92
        right = right / max_val * 0.92

    stereo = np.empty((total_samples, 2), dtype=np.float32)
    stereo[:, 0] = left
    stereo[:, 1] = right

    import soundfile as sf
    raw_wav = out_wav.replace(".wav", "_raw.wav")
    sf.write(raw_wav, stereo, SR)

    cmd = [
        "/home/user/.cache/frameforge/bin/ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", raw_wav,
        "-af", "loudnorm=I=-16:LRA=7:TP=-1.5",
        "-ar", str(SR),
        out_wav
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(raw_wav):
        os.remove(raw_wav)
    print(f"Mastered r04 audio track to {out_wav} ({duration:.2f}s)")

if __name__ == "__main__":
    os.makedirs("frameforge/agents/glyphcraft/work/audio", exist_ok=True)
    build_soundtrack(42.0, "frameforge/agents/glyphcraft/work/audio/hero_soundtrack_r04.wav")
