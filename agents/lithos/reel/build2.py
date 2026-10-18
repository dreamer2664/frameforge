"""Final mux: graded frames + gain-fitted score -> out/kinetic-reel.mp4 + poster.
python3 build2.py
"""
import subprocess, re
from pathlib import Path

ROOT = Path('/home/user/work/frameforge/agents/lithos/reel')
FF = str(Path.home() / '.cache/frameforge/bin/ffmpeg')
FP = str(Path.home() / '.cache/frameforge/bin/ffprobe')
OUT = ROOT / 'out'
OUT.mkdir(exist_ok=True)

# 1) measure score loudness
r = subprocess.run([FF, '-hide_banner', '-nostats', '-i', '/tmp/reel-score.wav',
                    '-af', 'loudnorm=I=-16:TP=-1.5:print_format=summary', '-f', 'null', '-'],
                   capture_output=True, text=True)
m = re.search(r'Input Integrated:\s+(-?[\d.]+) LUFS', r.stderr)
tp = re.search(r'Input True Peak:\s+(-?[\d.]+) dBTP', r.stderr)
lufs = float(m.group(1))
gain = -16.0 - lufs
print(f'score: {lufs} LUFS / {tp.group(1)} dBTP -> gain {gain:+.2f} dB')

# 2) encode
cmd = [FF, '-y', '-hide_banner', '-loglevel', 'error',
       '-framerate', '30', '-i', str(ROOT / '/tmp/reel-graded/%04d.jpg'),
       '-i', '/tmp/reel-score.wav',
       '-af', f'volume={gain:.2f}dB',
       '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
       '-c:a', 'aac', '-b:a', '192k', '-ar', '44100',
       '-movflags', '+faststart', '-shortest',
       str(OUT / 'kinetic-reel.mp4')]
subprocess.run(cmd, check=True)

# 3) poster
subprocess.run([FF, '-y', '-hide_banner', '-loglevel', 'error', '-ss', '10.5',
                '-i', str(OUT / 'kinetic-reel.mp4'), '-frames:v', '1',
                str(OUT / 'poster.png')], check=True)

# 4) QC
r = subprocess.run([FP, '-v', 'error', '-show_entries',
                    'stream=codec_name,width,height,r_frame_rate:format=duration,size',
                    '-of', 'default=nw=1', str(OUT / 'kinetic-reel.mp4')], capture_output=True, text=True)
print(r.stdout)
r = subprocess.run([FF, '-hide_banner', '-nostats', '-i', str(OUT / 'kinetic-reel.mp4'),
                    '-af', 'loudnorm=I=-16:TP=-1.5:print_format=summary', '-f', 'null', '-'],
                   capture_output=True, text=True)
for line in r.stderr.splitlines():
    if 'Input Integrated' in line or 'Input True Peak' in line:
        print(line.strip())
print('BUILD2_OK')
