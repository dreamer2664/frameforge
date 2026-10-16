"""Procedural audio design engine for glyphcraft.
Synthesizes rich tactile acoustic layers (sub-bass, impacts, snaps, friction risers, resonant harmonics)
and layers neural speech cues at precisely mapped timestamps.
Mastered to EBU R128 (-16.0 LUFS target, -1.5 dBTP).
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
    # linear frequency sweep
    freq = np.linspace(f0, f1, len(t))
    phase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.sin(np.pi * t / dur) ** 2
    return np.sin(phase) * env

def synth_impact(dur=1.2, sub_f=45.0, punch_f=120.0):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    sub = np.sin(2 * np.pi * sub_f * t) * np.exp(-3.5 * t)
    # pitch drop on punch
    punch_freq = punch_f * np.exp(-15.0 * t) + sub_f
    phase = 2 * np.pi * np.cumsum(punch_freq) / SR
    punch = np.sin(phase) * np.exp(-8.0 * t)
    noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-25.0 * t) * 0.3
    return (sub * 0.7 + punch * 0.8 + noise) * 0.9

def synth_whoosh(dur=1.0, f_center=400.0):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    noise = np.random.randn(len(t))
    # bandpass envelope
    env = np.sin(np.pi * t / dur) ** 3
    # modulate noise with sweep
    sweep = np.sin(2 * np.pi * np.linspace(150, 600, len(t)) * t)
    return noise * env * 0.3 + sweep * env * 0.2

def synth_harmonic_bell(f0=220.0, dur=3.5):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    harmonics = [1.0, 2.02, 3.01, 4.25, 5.43]
    amps = [0.6, 0.4, 0.25, 0.15, 0.08]
    decays = [1.2, 1.8, 2.5, 3.2, 4.0]
    out = np.zeros(len(t))
    for f_mult, a, dec in zip(harmonics, amps, decays):
        out += a * np.sin(2 * np.pi * f0 * f_mult * t) * np.exp(-dec * t)
    return out

def synth_sub_drone(dur):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    # Slow undulating sub 50Hz and 55Hz beating
    drone = 0.5 * np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 50.5 * t)
    # gentle warmth overtone
    drone += 0.2 * np.sin(2 * np.pi * 100 * t)
    return drone * 0.35

def load_wav(path):
    import soundfile as sf
    data, sr = sf.read(path)
    if sr != SR:
        # resample via scipy or simple interp
        num_samples = int(len(data) * SR / sr)
        data = np.interp(np.linspace(0, len(data), num_samples), np.arange(len(data)), data)
    if data.ndim == 2:
        data = data.mean(axis=1)
    return data

def build_soundtrack(duration=42.0, out_wav="hero_audio.wav"):
    total_samples = int(duration * SR)
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    # 1. Background drone & cinematic bed
    drone = synth_sub_drone(duration)
    # subtle stereo width
    left += drone * 0.3
    right += drone * 0.3

    # Add gentle ambient chord texture (pads)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    pad = 0.15 * (np.sin(2 * np.pi * 130.81 * t) + np.sin(2 * np.pi * 164.81 * t) + np.sin(2 * np.pi * 196.00 * t))
    pad *= (np.sin(np.pi * t / duration) ** 0.5)
    left += pad * 0.3
    right += pad * 0.3

    def add_cue(signal, start_time, pan=0.0, gain=1.0):
        s_idx = int(start_time * SR)
        e_idx = min(s_idx + len(signal), total_samples)
        length = e_idx - s_idx
        if length <= 0: return
        sig = signal[:length] * gain
        # Panning: -1.0 left, 1.0 right
        l_gain = np.cos((pan + 1.0) * np.pi / 4.0)
        r_gain = np.sin((pan + 1.0) * np.pi / 4.0)
        left[s_idx:e_idx] += sig * l_gain
        right[s_idx:e_idx] += sig * r_gain

    # --- Act I: The Atomic Stroke (0.0s - 7.0s) ---
    add_cue(synth_chirp(100, 800, 0.8), 0.8, pan=-0.3, gain=0.6)
    add_cue(synth_impact(1.5, punch_f=180), 2.2, pan=0.0, gain=0.8)
    add_cue(synth_harmonic_bell(329.63, 2.5), 2.3, pan=0.2, gain=0.4)
    add_cue(synth_whoosh(1.2, 500), 4.5, pan=0.4, gain=0.5)

    # --- Act II: Elastic Tension (7.0s - 15.0s) ---
    add_cue(synth_chirp(200, 1400, 2.0), 8.0, pan=-0.2, gain=0.5)
    add_cue(synth_impact(2.0, sub_f=40, punch_f=220), 10.5, pan=0.0, gain=0.95)
    add_cue(synth_whoosh(1.5, 700), 12.0, pan=0.3, gain=0.7)

    # --- Act III: Hero Topological Morph (15.0s - 23.0s) ---
    add_cue(synth_whoosh(2.5, 300), 15.5, pan=-0.4, gain=0.8)
    add_cue(synth_chirp(300, 950, 1.8), 17.0, pan=0.0, gain=0.6)
    add_cue(synth_impact(2.5, sub_f=38, punch_f=140), 18.5, pan=0.0, gain=1.1)
    add_cue(synth_harmonic_bell(440.0, 3.5), 18.6, pan=0.3, gain=0.6)

    # --- Act IV: The Counter Portal (23.0s - 31.0s) ---
    add_cue(synth_whoosh(3.0, 250), 23.2, pan=0.0, gain=0.85)
    add_cue(synth_chirp(80, 500, 2.5), 24.5, pan=-0.3, gain=0.7)
    add_cue(synth_impact(2.8, sub_f=35, punch_f=110), 27.0, pan=0.0, gain=1.0)
    add_cue(synth_harmonic_bell(261.63, 4.0), 27.2, pan=0.4, gain=0.55)

    # --- Act V: Master Convergence & Brand Payoff (31.0s - 42.0s) ---
    add_cue(synth_whoosh(2.0, 400), 31.0, pan=0.0, gain=0.8)
    add_cue(synth_impact(4.0, sub_f=32, punch_f=90), 33.0, pan=0.0, gain=1.2) # Master hit
    add_cue(synth_harmonic_bell(196.0, 6.0), 33.1, pan=-0.2, gain=0.7)
    add_cue(synth_harmonic_bell(293.66, 5.5), 33.1, pan=0.2, gain=0.6)
    add_cue(synth_impact(2.0, sub_f=45, punch_f=130), 38.0, pan=0.0, gain=0.7) # Final rule strike

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
            add_cue(speech, c_time, pan=0.0, gain=1.2)

    # Normalize audio to prevent clipping before ffmpeg loudnorm
    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if max_val > 0.95:
        left = left / max_val * 0.92
        right = right / max_val * 0.92

    # Interleave to stereo
    stereo = np.empty((total_samples, 2), dtype=np.float32)
    stereo[:, 0] = left
    stereo[:, 1] = right

    import soundfile as sf
    raw_wav = out_wav.replace(".wav", "_raw.wav")
    sf.write(raw_wav, stereo, SR)

    # Master through ffmpeg loudnorm to integrated -16 LUFS
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
    print(f"Mastered audio track to {out_wav} ({duration:.2f}s)")

if __name__ == "__main__":
    os.makedirs("frameforge/agents/glyphcraft/work/audio", exist_ok=True)
    build_soundtrack(42.0, "frameforge/agents/glyphcraft/work/audio/hero_soundtrack.wav")
