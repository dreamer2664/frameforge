#!/usr/bin/env python3
"""Noninteractive neural English TTS: NEVER auditions voices to the Director.
Downloads open-source runtime/model locally; no speech-service API key required.
Voice is the producer's decision. This tool does not clone a person's voice.
"""
from pathlib import Path
import argparse,json,os,subprocess,sys,urllib.request,hashlib,shutil

CACHE=Path(os.environ.get('FRAMEFORGE_CACHE',Path.home()/'.cache/frameforge'))
MODELS={'kokoro-v1.0.onnx':'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx','voices-v1.0.bin':'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin'}

def bootstrap():
    v=CACHE/'voice-venv';python=v/'bin/python'
    env={k:v for k,v in os.environ.items() if k not in ('CHATCODE_TOKEN','GITHUB_TOKEN','GH_TOKEN')}
    if not python.exists():subprocess.run([sys.executable,'-m','venv',str(v)],check=True,env=env)
    marker=v/'frameforge-ready'
    if not marker.exists():
        subprocess.run([str(python),'-m','pip','install','--disable-pip-version-check','kokoro-onnx==0.6.1','soundfile==0.14.0'],check=True,env=env)
        marker.write_text('runtime installed; first synthesis is the real access test\n')
    return python,env

def download_models():
    folder=CACHE/'voice-models';folder.mkdir(parents=True,exist_ok=True);receipts={}
    for name,url in MODELS.items():
        target=folder/name
        if not target.exists():
            tmp=target.with_suffix(target.suffix+'.part')
            with urllib.request.urlopen(url,timeout=180) as src,tmp.open('wb') as dest:shutil.copyfileobj(src,dest)
            tmp.replace(target)
        h=hashlib.sha256()
        with target.open('rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
        receipts[name]={'url':url,'sha256':h.hexdigest(),'bytes':target.stat().st_size}
    (folder/'source-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n');return folder

def main():
    p=argparse.ArgumentParser();p.add_argument('--text-file',required=True);p.add_argument('--out',required=True);p.add_argument('--voice',default='af_heart');p.add_argument('--speed',type=float,default=1.0);p.add_argument('--lang',choices=('en-us','en-gb'),default='en-us');p.add_argument('--child',action='store_true');a=p.parse_args()
    if not a.child:
        python,env=bootstrap();args=[str(python),str(Path(__file__).resolve()),'--child','--text-file',str(Path(a.text_file).resolve()),'--out',str(Path(a.out).resolve()),'--voice',a.voice,'--speed',str(a.speed),'--lang',a.lang]
        return subprocess.call(args,env=env)
    import soundfile as sf
    from kokoro_onnx import Kokoro
    folder=download_models();model=Kokoro(str(folder/'kokoro-v1.0.onnx'),str(folder/'voices-v1.0.bin'))
    text=Path(a.text_file).read_text().strip()
    if not text:raise ValueError('Empty narration cue')
    # Generate short cue files independently and cache them for long-form work.
    samples,sr=model.create(text,voice=a.voice,speed=a.speed,lang=a.lang)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);sf.write(out,samples,sr)
    report={'engine':'kokoro-onnx','voice':a.voice,'language':a.lang,'synthetic':True,'sample_rate':sr,'duration_seconds':len(samples)/sr,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'user_audition_requested':False}
    out.with_suffix('.voice.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return 0
if __name__=='__main__':sys.exit(main())
