#!/usr/bin/env python3
"""Rootless FFmpeg/ffprobe install. Binaries stay in excluded cache, never Git."""
from pathlib import Path
import argparse,hashlib,json,os,platform,shutil,tarfile,urllib.request

def install(cache=None):
    base=Path(cache or os.environ.get('FRAMEFORGE_CACHE',Path.home()/'.cache/frameforge'))
    bindir=base/'bin';bindir.mkdir(parents=True,exist_ok=True)
    if all((bindir/n).is_file() for n in ('ffmpeg','ffprobe')):return bindir
    machine=platform.machine().lower();arch='amd64' if machine in ('x86_64','amd64') else 'arm64' if machine in ('aarch64','arm64') else None
    if platform.system()!='Linux' or not arch:raise RuntimeError('Use installed ffmpeg/ffprobe on this OS; bundled rootless bootstrap supports Linux x86_64/arm64.')
    url=f'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-{arch}-static.tar.xz'
    archive=base/'ffmpeg.tar.xz'
    if not archive.exists():
        with urllib.request.urlopen(url,timeout=120) as src,archive.open('wb') as dest:shutil.copyfileobj(src,dest)
    with tarfile.open(archive,'r:xz') as tar:
        for name in ('ffmpeg','ffprobe'):
            members=[m for m in tar.getmembers() if m.isfile() and Path(m.name).name==name]
            if len(members)!=1:raise RuntimeError(f'Expected one regular {name} binary')
            with tar.extractfile(members[0]) as src,(bindir/name).open('wb') as dest:shutil.copyfileobj(src,dest)
            (bindir/name).chmod(0o755)
    (base/'ffmpeg-source.json').write_text(json.dumps({'url':url,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'license_note':'Read FFmpeg build licensing before redistributing binaries; this helper installs locally, not into the source repo.'},indent=2)+'\n')
    return bindir

def binary(name):
    path=shutil.which(name)
    if path:return path
    return str(install()/name)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache');a=p.parse_args();print(install(a.cache))
