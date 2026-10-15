"""Sample-free procedural score and authored punctuation for the Kinetic film."""
from __future__ import annotations
import argparse, json, math, os, wave
import numpy as np

BASE=os.path.dirname(os.path.abspath(__file__))
CUES=json.load(open(os.path.join(BASE,'audio_cues.json'),encoding='utf-8'))
SR=48000


def smooth_arr(x):
    x=np.clip(x,0.0,1.0)
    return x*x*(3.0-2.0*x)

def write_wav(path, stereo, sample_rate=SR):
    os.makedirs(os.path.dirname(os.path.abspath(path)),exist_ok=True)
    x=np.asarray(stereo,dtype=np.float64)
    x=np.nan_to_num(x,nan=0.0,posinf=0.0,neginf=0.0)
    x=np.clip(x,-0.98,0.98)
    pcm=np.round(x*32767).astype('<i2')
    with wave.open(path,'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sample_rate); wf.writeframes(pcm.tobytes())
    print(f'wrote {path}: {len(x)} stereo samples, {len(x)/sample_rate:.6f}s at {sample_rate} Hz')

def timebase(start,duration): return start + np.arange(int(round(duration*SR)),dtype=np.float64)/SR

def hero_audio(path,start=0.0,duration=None):
    if duration is None: duration=float(CUES['hero']['duration_seconds'])
    t=timebase(start,duration)
    mix=np.zeros_like(t)
    # Five slow harmonic beds; attack/release envelopes avoid clicks at each chord change.
    points=CUES['hero']['progression_seconds']
    chords=CUES['hero']['chords_hz']
    for seg in range(len(chords)):
        a=float(points[seg]); b=float(points[seg+1]); length=b-a
        rel=t-a
        attack=smooth_arr(rel/1.15)
        release=1.0-smooth_arr((rel-(length-1.25))/1.25)
        env=attack*release
        env*=((t>=a)&(t<b))
        swell=.84+.16*(.5+.5*np.sin(2*np.pi*t/12.0+seg*.55))
        for j,f in enumerate(chords[seg]):
            phase=2*np.pi*f*rel
            voice=(np.sin(phase)+.18*np.sin(2*phase+.3)+.06*np.sin(3*phase+.7))
            level=[.021,.017,.014,.010][j]
            mix += level*env*swell*voice
    # Sparse soft plucks at editorial joints; each has a gentle onset and measured decay.
    cues=CUES['hero']['punctuations_seconds']
    notes=[659.25,523.25,587.33,440.00,493.88,392.00,523.25,659.25,587.33,440.00,523.25]
    for idx,(at,f) in enumerate(zip(cues,notes)):
        dt=t-at
        valid=(dt>=0)&(dt<1.55)
        u=np.maximum(dt[valid],0.0)
        env=(1-np.exp(-u*42.0))*np.exp(-u*(2.8+0.12*(idx%3)))
        tone=np.sin(2*np.pi*f*u)+.20*np.sin(2*np.pi*f*2.01*u+.2)
        mix[valid] += .041*env*tone
    # A short, airy, interpolated-noise breath and a descending sine sweep punctuate major transitions.
    rng=np.random.default_rng(20261015)
    major=[0.05,3.00,6.10,9.18,12.48,16.48,20.48,23.32]
    for idx,at in enumerate(major):
        dur=.74 if idx not in (0,7) else .55
        dt=t-at
        valid=(dt>=0)&(dt<dur)
        if not np.any(valid): continue
        u=dt[valid]/dur
        env=np.sin(np.pi*u)**1.5
        # Band-limited noise is interpolated from a fixed 3 kHz stream to keep the timbre soft.
        count=max(4,int(dur*3000))
        coarse=rng.standard_normal(count)
        noise=np.interp(u*dur,np.linspace(0,dur,count),coarse)
        f0=420+idx*23; f1=155+idx*9
        phase=2*np.pi*(f0*(u*dur)+(f1-f0)*(u*dur)**2/(2*dur))
        sweep=np.sin(phase)
        mix[valid] += env*(.008*noise+.018*sweep)
        # soft low pulse as the line lands, never a sharp click
        lowenv=(1-np.exp(-u*dur*55))*np.exp(-u*dur*7)
        lowfreq=74+idx*2
        mix[valid] += .022*lowenv*np.sin(2*np.pi*lowfreq*u*dur)
    # Very low moving air, two-second periodic amplitude so it does not become a constant hiss.
    drift=.0028*(.5+.5*np.sin(2*np.pi*t/8.0))
    mix += drift*np.sin(2*np.pi*37.0*t+.4)
    # Slight short stereo room reflection; the mix remains centered and phase-safe.
    delay=int(.018*SR)
    right=np.roll(mix,delay)*.075
    right[:delay]=0.0
    left=mix*.985
    stereo=np.column_stack((left+right,mix*.95+np.roll(mix,int(.011*SR))*.06))
    stereo[:int(.018*SR),1]=mix[:int(.018*SR)]*.95
    write_wav(path,stereo)

def loop_audio(path,start=0.0,duration=10.0):
    t=timebase(start,duration)
    phase=2*np.pi*t
    # Integer-cycle tones at 55/65/82.5 Hz return to identical phase every ten seconds.
    bed=(.035*np.sin(phase*55.0)+.026*np.sin(phase*65.0+.35)+
         .020*np.sin(phase*82.5+.8)+.012*np.sin(phase*110.0+.5)+
         .008*np.sin(phase*165.0+1.0)+.005*np.sin(phase*220.0+.2))
    breathe=.88+.12*(.5+.5*np.sin(phase)) # exactly one envelope cycle per 10 s
    shimmer=.006*np.sin(phase*330.0+np.sin(phase)*.08)
    mono=bed*breathe+shimmer
    # Identical channels avoid unintended phase width and give a reliably repeatable seam.
    write_wav(path,np.column_stack((mono,mono)))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--kind',choices=['hero','loop'],required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--start',type=float,default=0.0)
    ap.add_argument('--duration',type=float,default=None)
    a=ap.parse_args()
    if a.kind=='hero': hero_audio(a.out,a.start,a.duration)
    else: loop_audio(a.out,a.start,a.duration or 10.0)
if __name__=='__main__': main()
