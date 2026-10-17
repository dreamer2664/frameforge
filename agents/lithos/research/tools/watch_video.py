#!/usr/bin/env python3
"""watch_video.py — fetch any video (URL or file) and produce a full visual
record: every frame extracted, contact sheets, cut detection, audio onsets and
tempo estimate. Built for the KINETIC commission to 'watch' reference films.

Usage:
  python3 watch_video.py --url https://vm.tiktok.com/XXXX/ --out DIR
  python3 watch_video.py --file film.mp4 --out DIR
"""
import argparse, json, subprocess, sys
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url')
    ap.add_argument('--file')
    ap.add_argument('--out', required=True)
    ap.add_argument('--sheet-cols', type=int, default=5)
    ap.add_argument('--sheet-frames', type=int, default=15)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    vid = Path(a.file) if a.file else out / 'source.mp4'
    if a.url:
        run(['yt-dlp', '--no-playlist', '-f', 'mp4/best', '-o', str(vid),
             '--write-info-json', a.url])
        info = out / 'source.info.json'
        for p in out.glob('*.info.json'):
            info = p
        if info.exists():
            d = json.loads(info.read_text())
            print('META', {k: d.get(k) for k in
                  ('title', 'description', 'duration', 'uploader', 'view_count', 'webpage_url')})
    (out / 'frames').mkdir(exist_ok=True)
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(vid), str(out / 'frames' / 'f%04d.png')])
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(vid), '-ac', '1', '-ar', '48000',
         '-f', 'f32le', str(out / 'audio.f32')])
    import numpy as np
    from PIL import Image, ImageDraw
    fs = sorted((out / 'frames').glob('f*.png'))
    imgs = [np.asarray(Image.open(p).convert('L'), dtype=np.float32) / 255.0 for p in fs]
    d = np.array([float(np.abs(imgs[i+1] - imgs[i]).mean()) for i in range(len(imgs)-1)])
    thr = d.mean() + 2.2 * d.std()
    cuts = [round((i+1) / 30, 3) for i, v in enumerate(d) if v > thr]
    print(f'FRAMES {len(fs)}  mean-diff {d.mean():.4f}  cut-candidates {cuts}')
    a_ = np.fromfile(out / 'audio.f32', dtype=np.float32)
    hop = 256; n = len(a_) // hop
    env = np.sqrt((a_[:n*hop].reshape(n, hop)**2).mean(axis=1))
    dd = np.maximum(0, np.diff(env))
    f = dd - dd.mean()
    ac = np.correlate(f, f, 'full')[len(f)-1:]
    lags = np.arange(1, len(ac)); bpm = 60.0 * 48000 / hop / lags
    mask = (bpm > 70) & (bpm < 180)
    best = lags[mask][int(np.argmax(ac[1:][mask]))]
    print(f'AUDIO rms {np.sqrt((a_**2).mean()):.3f}  tempo ~{60.0*48000/hop/best:.1f} BPM')
    sm = np.convolve(dd, np.ones(3)/3, 'same')
    cand = sorted(((sm[i], i) for i in range(8, len(sm)-8) if sm[i] == sm[i-8:i+9].max()), reverse=True)
    onsets = []
    for _, i in sorted(cand[:60]):
        t = round(i * hop / 48000, 2)
        if not onsets or t - onsets[-1] > 0.12:
            onsets.append(t)
    print('ONSETS', sorted(onsets)[:32])
    per, cols = a.sheet_frames, a.sheet_cols
    for si in range(0, len(fs), per):
        chunk = fs[si:si+per]
        rows = (len(chunk) + cols - 1) // cols
        cw, ch, pad, top = 330, 186, 4, 22
        s = Image.new('RGB', (cols*cw + pad*(cols+1), rows*ch + pad*(rows+1) + top), (12, 12, 12))
        dr = ImageDraw.Draw(s)
        dr.text((8, 5), f'frames {si}-{si+len(chunk)-1} (t {si/30:.2f}-{(si+len(chunk)-1)/30:.2f}s)', fill=(255, 230, 120))
        for i, fp in enumerate(chunk):
            r, c = divmod(i, cols)
            th = Image.open(fp).resize((cw, ch), Image.LANCZOS)
            x, y = pad + c*(cw+pad), top + pad + r*(ch+pad)
            s.paste(th, (x, y))
            dr.text((x+3, y+2), f'{int(fp.stem[1:])-1:03d} {(int(fp.stem[1:])-1)/30:.2f}s', fill=(255, 60, 60))
        s.save(out / f'sheet-{si//per:02d}.png')
    (out / 'report.json').write_text(json.dumps({'frames': len(fs), 'cuts': cuts, 'onsets': sorted(onsets)}, indent=1))
    print('WROTE', out)

if __name__ == '__main__':
    main()
