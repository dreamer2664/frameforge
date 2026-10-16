import numpy as np, soundfile as sf, subprocess
SR = 48000
DUR = 10.0
total = int(DUR * SR)
t = np.linspace(0, DUR, total, endpoint=False)
theta = 2.0 * np.pi * t / DUR

# Cyclic breathing drone
drone = 0.3 * np.sin(2 * np.pi * 50 * t) * (0.7 + 0.3 * np.cos(theta))
pad = 0.15 * (np.sin(2 * np.pi * 196.0 * t) + np.sin(2 * np.pi * 293.66 * t)) * (0.7 + 0.3 * np.sin(theta))
left = drone + pad
right = drone + pad

# Interleave
stereo = np.empty((total, 2), dtype=np.float32)
stereo[:, 0] = left
stereo[:, 1] = right

sf.write("frameforge/agents/glyphcraft/work/audio/loop_raw.wav", stereo, SR)
subprocess.run([
    "/home/user/.cache/frameforge/bin/ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
    "-i", "frameforge/agents/glyphcraft/work/audio/loop_raw.wav",
    "-af", "loudnorm=I=-16:LRA=7:TP=-1.5",
    "-ar", "48000",
    "frameforge/agents/glyphcraft/work/audio/loop_soundtrack.wav"
], check=True)
print("Synthesized loop soundtrack.")
