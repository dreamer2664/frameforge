#!/usr/bin/env python3
"""Decode real output frames with FFmpeg (including AV1/HEVC); make timecoded sheets.
The producer must OPEN these images with its vision tool, not merely generate them.
"""
from pathlib import Path
import argparse,json,math,subprocess
from PIL import Image,ImageDraw
from bootstrap_media import binary

def sample_times(duration,every):
    if duration<=0 or every<=0:raise ValueError('Duration and interval must be positive')
    regular=[round(i*every,3) for i in range(max(1,math.ceil(duration/every))) if i*every<duration]
    return sorted(set(regular+[max(0,round(duration-.1,3))]))

def inspect(video,out,every=2,limit_per_sheet=24):
    video=Path(video).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    meta=json.loads(subprocess.check_output([binary('ffprobe'),'-v','error','-show_format','-show_streams','-of','json',str(video)]))
    duration=float(meta['format']['duration']);stream=next(x for x in meta['streams'] if x.get('codec_type')=='video');portrait=stream['height']>stream['width']
    tw,th,cols=(270,480,4) if portrait else (384,216,3)
    times=sample_times(duration,every)
    paths=[]
    for n in range(0,len(times),limit_per_sheet):
        batch=times[n:n+limit_per_sheet];canvas=Image.new('RGB',(cols*tw,math.ceil(len(batch)/cols)*(th+28)),(22,24,31));draw=ImageDraw.Draw(canvas)
        for i,sec in enumerate(batch):
            path=out/f'frame-{n+i:05d}-{sec:.3f}s.jpg'
            subprocess.run([binary('ffmpeg'),'-v','error','-ss',str(sec),'-i',str(video),'-frames:v','1','-q:v','3','-y',str(path)],check=True,timeout=45)
            with Image.open(path) as frame:
                frame.thumbnail((tw,th));x=i%cols*tw+(tw-frame.width)//2;y=i//cols*(th+28);canvas.paste(frame,(x,y));draw.text((i%cols*tw+6,y+th+6),f'{sec:.3f}s',fill='white')
        sheet=out/f'sheet-{n//limit_per_sheet:03d}.jpg';canvas.save(sheet);paths.append(str(sheet))
    manifest={'video':str(video),'duration':duration,'sampled_at_seconds':times,'sheets':paths,'review_status':'NOT REVIEWED merely because these images were generated. Open them, record observations and fix defects.'}
    (out/'inspection.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--out',required=True);p.add_argument('--every',type=float,default=2);a=p.parse_args()
    if a.every<=0:p.error('--every must be positive')
    print(json.dumps(inspect(a.video,a.out,a.every),indent=2))
