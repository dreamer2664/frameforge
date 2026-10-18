import sys
sys.path.insert(0, '/home/user/work/frameforge/agents/lithos/reel')
from acts2 import screen_frame
bad = []
for fr in range(384):
    try:
        screen_frame(fr / 30)
    except Exception as e:
        bad.append((fr, repr(e)[:150]))
        if len(bad) > 6:
            break
print('BAD_FRAMES', bad)
