#!/usr/bin/env python3
"""Measured technical gate. Passing this is NOT artistic/full-watch approval."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
from bootstrap_media import binary

RANGES={'kinetic':(20,45),'scribble':(45,90),'axiom':(840,1080),'parallax':(35,55),'glyphcraft':(35,55),'lithos':(35,55)}

def probe(video):
    return json.loads(subprocess.check_output([binary('ffprobe'),'-v','error','-show_format','-show_streams','-of','json',str(video)]))

def check(video,agent,*,decode=True,audio_scan=True,allow_test_duration=False):
    path=Path(video);meta=probe(path);issues=[];streams=meta['streams'];v=next((s for s in streams if s.get('codec_type')=='video'),None);a=next((s for s in streams if s.get('codec_type')=='audio'),None)
    d=float(meta['format']['duration']);lo,hi=RANGES[agent]
    if not allow_test_duration and not lo<=d<=hi:issues.append(f'Duration {d:.3f}s outside {lo}-{hi}s')
    if not v:issues.append('Missing video track')
    else:
        size=(v.get('width'),v.get('height'));wanted=(1080,1920) if agent=='scribble' else (1920,1080)
        if size!=wanted:issues.append(f'Picture {size}, expected {wanted}')
        if v.get('codec_name')!='h264' or v.get('pix_fmt')!='yuv420p':issues.append('Final must be H.264 / yuv420p')
        rate=v.get('avg_frame_rate','0/1');n,den=map(float,rate.split('/'));fps=n/den if den else 0
        if not any(abs(fps-f)<.02 for f in (24,25,30)):issues.append(f'Unsupported frame rate {rate}')
    if not a:issues.append('Missing audio: narration for explainers, deliberate soundtrack/SFX for kinetic')
    else:
        if a.get('codec_name')!='aac' or a.get('sample_rate')!='48000':issues.append('Final audio must be AAC / 48kHz')
        if int(a.get('bit_rate') or 0)<128000:issues.append('AAC bitrate below 128 kbps; target at least 160 kbps')
        if v:
            try:
                delta=abs(float(v['duration'])-float(a['duration']))
                if delta>.25:issues.append(f'Audio/picture end mismatch {delta:.3f}s; do not leave a frozen/black tail')
            except (KeyError,ValueError):issues.append('Could not measure both stream durations')
    if decode:
        p=subprocess.run([binary('ffmpeg'),'-v','error','-xerror','-i',str(path),'-f','null','-'],capture_output=True,text=True)
        if p.returncode:issues.append('Full decode failed: '+p.stderr[-600:])
    loudness=None;silence_log=''
    if a and audio_scan:
        p=subprocess.run([binary('ffmpeg'),'-hide_banner','-nostats','-i',str(path),'-vn','-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True)
        chunks=re.findall(r'\{[^{}]*"input_i"[^{}]*\}',p.stderr,re.S)
        if chunks:
            loudness=json.loads(chunks[-1]);i=float(loudness['input_i']);tp=float(loudness['input_tp'])
            if not -17.5<=i<=-14.5:issues.append(f'Integrated loudness {i} LUFS outside -16 ±1.5')
            if tp> -1:issues.append(f'True peak {tp} dBTP exceeds -1')
        else:issues.append('Could not measure loudness')
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return {'file':path.name,'agent':agent,'sha256':h.hexdigest(),'bytes':path.stat().st_size,'duration_seconds':d,'streams':streams,'loudness':loudness,'technical_pass':not issues,'violations':issues,'grading':'TECHNICAL ONLY. Requires actual visual self-review, story/source/rights review; no fake listening or audience-performance claims.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('agent',choices=RANGES);p.add_argument('video');p.add_argument('--out',required=True);p.add_argument('--skip-decode',action='store_true');p.add_argument('--skip-loudness',action='store_true');a=p.parse_args()
    result=check(a.video,a.agent,decode=not a.skip_decode,audio_scan=not a.skip_loudness);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'technical_pass':result['technical_pass'],'violations':result['violations']},indent=2));sys.exit(0 if result['technical_pass'] else 2)
