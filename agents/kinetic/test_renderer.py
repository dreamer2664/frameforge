"""Offline checks for deterministic timing, type assets, and loop phase geometry."""
import json, os, sys, unittest
from pathlib import Path
from PIL import ImageChops
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import render

class KineticRenderTests(unittest.TestCase):
    def test_hero_timeline_is_27s_and_all_beats_are_ordered(self):
        data=json.loads((ROOT/'storyboard.json').read_text())
        self.assertEqual(data['format']['duration_seconds'],27.0)
        beats=data['beats']
        self.assertEqual(len(beats),8)
        self.assertEqual(beats[0]['in'],0.0)
        self.assertEqual(beats[-1]['out'],27.0)
        self.assertTrue(all(a['out']==b['in'] for a,b in zip(beats,beats[1:])))

    def test_hero_critical_frames_are_rgb_full_work_size(self):
        for t in [0.0,0.5,3.0,6.1,9.2,10.6,12.5,13.1,16.5,20.5,23.4,26.9]:
            im=render.draw_hero_frame(t)
            self.assertEqual(im.size,(1280,720),f't={t}')
            self.assertEqual(im.mode,'RGB',f't={t}')

    def test_loop_phase_closes_pixel_exactly(self):
        first=render.draw_loop_frame(0.0)
        wrapped=render.draw_loop_frame(render.LOOP_DURATION)
        self.assertIsNone(ImageChops.difference(first,wrapped).getbbox())

    def test_loop_wrap_frame_step_matches_normal_step(self):
        fps=render.LOOP_FPS; period=render.LOOP_DURATION
        last=render.draw_loop_frame(period-1/fps)
        first=render.draw_loop_frame(0.0)
        next_frame=render.draw_loop_frame(1/fps)
        a=last.convert('RGB'); b=first.convert('RGB'); c=next_frame.convert('RGB')
        def mean_delta(x,y):
            import numpy as np
            q=np.asarray(x,dtype=np.int16)-np.asarray(y,dtype=np.int16)
            return float(np.abs(q).mean())
        seam=mean_delta(a,b); ordinary=mean_delta(b,c)
        self.assertLess(seam,ordinary*1.15)

    def test_loop_audio_packets_land_exactly(self):
        data=json.loads((ROOT/'audio_cues.json').read_text())['loop']
        samples=round(data['duration_seconds']*data['sample_rate'])
        self.assertEqual(samples,491520)
        self.assertEqual(samples%data['aac_frame_samples'],0)
        self.assertEqual(data['duration_seconds']*data['fps'],data['frames'])
        for f in data['harmonic_frequencies_hz']:
            self.assertAlmostEqual(f*data['period_seconds'],round(f*data['period_seconds']),places=8)

    def test_font_notices_are_retained(self):
        for rel in ['fonts/Fraunces.ttf','fonts/Inter-Regular.ttf','fonts/Inter-Medium.ttf',
                    'fonts/licenses/Fraunces-OFL.txt','fonts/licenses/Inter-OFL.txt']:
            self.assertTrue((ROOT/rel).is_file(),rel)

if __name__=='__main__': unittest.main(verbosity=2)
