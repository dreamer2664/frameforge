#!/usr/bin/env python3
"""PRISM / PROOF — publication to dreamer2664/storagecode (sole primary archive).

1. builds source.zip + evidence.zip + ARCHIVE_SHA256.txt
2. creates GitHub Release  frameforge/prism/r01-<first12 of master sha>
   with assets: master.mp4, master_video.mp4, master_audio.wav, source.zip,
   evidence.zip, ARCHIVE_SHA256.txt
3. prints the exact rows to append to storagecode PUSHES.md / data/INDEX.md
   (the ledger appends happen in publish.sh via a storagecode clone+push)

Token comes from the environment only (R3). Never printed, never in a URL.
"""
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
import zipfile

TOK = os.environ['GITHUB_TOKEN']
REPO = 'dreamer2664/storagecode'
SRC = os.path.dirname(os.path.abspath(__file__))


def api(path, method='GET', body=None, ctype='application/json'):
    req = urllib.request.Request(f'https://api.github.com{path}', method=method)
    req.add_header('Authorization', 'Bearer ' + TOK)
    req.add_header('User-Agent', 'prism-publish')
    req.add_header('Accept', 'application/vnd.github+json')
    if body is not None:
        req.add_header('Content-Type', ctype)
        req.data = body if isinstance(body, bytes) else json.dumps(body).encode()
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.status, json.load(r) if r.headers.get('Content-Type', '').startswith('application/json') else r.read()


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


os.chdir(SRC)
master_sha = sha256('exports/master.mp4')
tag = f'frameforge/prism/r01-{master_sha[:12]}'

# ---- archives
with zipfile.ZipFile('exports/source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in
                   ('node_modules', 'exports', 'frames', 'styleframes', '.git', 'probe')]
        for f in files:
            p = os.path.join(root, f)
            z.write(p, os.path.join('source', p[2:]))
with zipfile.ZipFile('exports/evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir('evidence')):
        p = os.path.join('evidence', f)
        if os.path.isfile(p):
            z.write(p, os.path.join('evidence', f))
members = []
for zp in ('exports/source.zip', 'exports/evidence.zip'):
    with zipfile.ZipFile(zp) as z:
        for i in z.infolist():
            members.append(f'{i.filename}  {i.file_size}')
open('exports/ARCHIVE_MANIFEST.txt', 'w').write('\n'.join(members) + '\n')

archive_sha = sha256('exports/evidence.zip')
with open('exports/ARCHIVE_SHA256.txt', 'w') as f:
    f.write(f'{master_sha}  master.mp4\n{sha256("exports/master_video.mp4")}  master_video.mp4\n'
            f'{sha256("audio/master_audio.wav")}  master_audio.wav\n'
            f'{sha256("exports/source.zip")}  source.zip\n{archive_sha}  evidence.zip\n')

notes = f"""PRISM — PROOF · r01 · 25.00 s three.js motion-design film (env-B)

Specs: 750 frames @ 30 fps = 25.00 s · 1920x1080 · H.264 High yuv420p ·
distribution CRF 18 + AAC 320 kbps 48 kHz stereo · video master CRF 12 ·
audio master 48 kHz stereo 24-bit WAV, I = -13.7 LUFS, TP = -1.1 dBTP.

SHA-256 master.mp4      : {master_sha}
SHA-256 master_video.mp4: {sha256('exports/master_video.mp4')}
SHA-256 master_audio.wav: {sha256('audio/master_audio.wav')}
SHA-256 evidence.zip    : {archive_sha}
SHA-256 source.zip      : {sha256('exports/source.zip')}
(see ARCHIVE_SHA256.txt / ARCHIVE_MANIFEST.txt inside the assets)

Verified by producer (env-B), rung-6 receipts in evidence.zip: ffprobe, full
750-frame decode (0 errors), per-frame SHA-256 manifest, measured flash
luminance deltas, measured text bounding boxes vs the 90% title-safe box,
two-pass loudnorm measurement, determinism re-render sample.

NOT verified: no independent non-owner reviewer has inspected the frames or
listened to the soundtrack at full speed; artistic quality is not
self-assessed.

Independent non-owner acceptance remains PENDING; no self-review/vote.
"""

status, rel = api(f'/repos/{REPO}/releases', 'POST', {
    'tag_name': tag, 'name': 'prism — PROOF · r01 · 25.0 s three.js motion film',
    'body': notes, 'draft': False, 'prerelease': False})
assert status == 201, status
print('release created:', rel['html_url'], rel['tag_name'])

for asset in ['exports/master.mp4', 'exports/master_video.mp4', 'audio/master_audio.wav',
              'exports/source.zip', 'exports/evidence.zip', 'exports/ARCHIVE_SHA256.txt']:
    with open(asset, 'rb') as f:
        data = f.read()
    req = urllib.request.Request(
        f"https://uploads.github.com/repos/{REPO}/releases/{rel['id']}/assets?name={os.path.basename(asset)}",
        method='POST', data=data)
    req.add_header('Authorization', 'Bearer ' + TOK)
    req.add_header('User-Agent', 'prism-publish')
    req.add_header('Content-Type', 'application/octet-stream')
    with urllib.request.urlopen(req, timeout=900) as r:
        print('asset', os.path.basename(asset), r.status, r.headers.get('Content-Length'), 'B')

# readback
status, rel2 = api(f'/repos/{REPO}/releases/tags/{tag}')
print('READBACK tag:', rel2['tag_name'], 'assets:', [a['name'] for a in rel2['assets']])
json.dump({'tag': tag, 'url': rel['html_url'], 'master_sha': master_sha,
           'archive_sha': archive_sha}, open('exports/RELEASE.json', 'w'), indent=1)
print('PUBLISH_OK', tag)
