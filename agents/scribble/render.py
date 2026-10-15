import json, os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE='/home/user/frameforge/agents/scribble'
WORK=BASE+'/work'
FRAMES=WORK+'/frames'
os.makedirs(FRAMES, exist_ok=True)

W,H=1080,1920
FPS=30
tl=json.load(open(WORK+'/timeline.json'))
cues=tl['cues']
# cue lookup
def active_cue(t):
    for c in cues:
        if c['start'] <= t < c['end']:
            return c
    # after last
    if t >= cues[-1]['end']:
        return cues[-1]
    return None

# fonts
def font(path,size):
    return ImageFont.truetype(path,size)
FONTS={
 'chewy': font(BASE+'/fonts/Chewy.ttf', 78),
 'chewy_sm': font(BASE+'/fonts/Chewy.ttf', 58),
 'nunito': font(BASE+'/fonts/Nunito-400.ttf', 40),
 'nunito_b': font(BASE+'/fonts/Nunito-700.ttf', 40),
 'kalam': font(BASE+'/fonts/Kalam.ttf', 46),
}
# keywords per cue
KEYWORDS={
1:'room',2:'forget',3:'everyone',4:'memory',5:'doorway',
6:'events',7:'boundary',8:'episode',9:'buried',10:'objects',
11:'door',12:'forgot',13:'room',14:'reset',15:'useful',
16:'tidy',17:'loud',18:'need',19:'back',20:'trick',21:'win'
}

# paper texture
random.seed(42)
noise=Image.new('L',(W,H))
nd=noise.load()
for y in range(H):
    for x in range(W):
        nd[x,y]=random.randint(225,245)
# slight grain via blur
noise=noise.filter(ImageFilter.GaussianBlur(0.6))

CREAM=(242,232,205)
INK=(28,24,20)
TEAL=(20,150,140)
GREY=(120,110,95)

def new_frame():
    img=Image.new('RGB',(W,H),CREAM)
    # blend noise
    n=noise.convert('RGB')
    img=Image.blend(img,n,0.35)
    return img, ImageDraw.Draw(img)

def draw_text_centered(draw, text, y, fnt, color=INK, maxw=900):
    # wrap
    words=text.split()
    lines=[]
    cur=''
    for wd in words:
        test=(cur+' '+wd).strip()
        bbox=fnt.getbbox(test)
        if bbox[2]-bbox[0] <= maxw:
            cur=test
        else:
            if cur: lines.append(cur)
            cur=wd
    if cur: lines.append(cur)
    lh=fnt.size+6 if hasattr(fnt,'size') else 40
    # estimate line height
    try:
        lh=fnt.getbbox('Ag')[3]+8
    except Exception:
        lh=40
    total=len(lines)*lh
    yy=y-total//2
    for ln in lines:
        bbox=fnt.getbbox(ln)
        tw=bbox[2]-bbox[0]
        x=(W-tw)//2
        draw.text((x,yy), ln, font=fnt, fill=color)
        yy+=lh
    return lines

def highlight_caption(draw, phrase, y, keyword):
    fnt=FONTS['chewy']
    words=phrase.split()
    space=fnt.getbbox(' ')[2]-fnt.getbbox(' ')[0]
    # wrap into <=2 lines, max width 980
    lines=[]
    cur=[]
    curw=0
    for w in words:
        ww=fnt.getbbox(w)[2]-fnt.getbbox(w)[0]
        if cur and curw+space+ww>980:
            lines.append(cur); cur=[w]; curw=ww
        else:
            cur.append(w); curw = (curw+space+ww) if curw else ww
    if cur: lines.append(cur)
    if len(lines)>2:
        # force split half
        mid=len(words)//2
        lines=[words[:mid], words[mid:]]
    lh=fnt.getbbox('Ag')[3]+10
    totalh=len(lines)*lh
    yy=y-totalh//2
    for ln in lines:
        ws=' '.join(ln)
        # width
        parts=ln
        widths=[fnt.getbbox(w)[2]-fnt.getbbox(w)[0] for w in parts]
        tot=sum(widths)+space*(len(parts)-1)
        x=(W-tot)//2
        for i,w in enumerate(parts):
            col=TEAL if w.strip('.,!?').lower()==keyword.lower() else INK
            draw.text((x,yy), w, font=fnt, fill=col)
            x+=widths[i]+space
        yy+=lh

def draw_stick(draw, cx, cy, scale=1.0, pose='stand', expr='neutral', color=INK, lw=6):
    s=scale
    head_r=int(46*s)
    # head
    draw.ellipse((cx-head_r, cy-head_r, cx+head_r, cy+head_r), outline=color, width=lw)
    # eyes
    eye_y=cy-int(8*s)
    ex=int(14*s)
    for dx in (-ex, ex):
        draw.ellipse((cx+dx-4, eye_y-4, cx+dx+4, eye_y+4), fill=color)
    # brows
    if expr=='happy':
        draw.arc((cx-22*s, eye_y-18*s, cx-2*s, eye_y-2*s), 200, 340, fill=color, width=3)
        draw.arc((cx+2*s, eye_y-18*s, cx+22*s, eye_y-2*s), 200, 340, fill=color, width=3)
    elif expr=='confused':
        draw.line((cx-22*s, eye_y-12*s, cx-2*s, eye_y-6*s), fill=color, width=3)
        draw.line((cx+2*s, eye_y-6*s, cx+22*s, eye_y-12*s), fill=color, width=3)
    elif expr=='thinking':
        draw.line((cx-22*s, eye_y-10*s, cx-2*s, eye_y-14*s), fill=color, width=3)
        draw.line((cx+2*s, eye_y-14*s, cx+22*s, eye_y-10*s), fill=color, width=3)
    # mouth
    mouth_y=cy+int(12*s)
    if expr in ('happy','smile'):
        draw.arc((cx-16*s, mouth_y-8*s, cx+16*s, mouth_y+8*s), 20, 160, fill=color, width=3)
    elif expr=='o':
        draw.ellipse((cx-6*s, mouth_y-6*s, cx+6*s, mouth_y+6*s), outline=color, width=3)
    elif expr=='flat':
        draw.line((cx-14*s, mouth_y, cx+14*s, mouth_y), fill=color, width=3)
    else:
        draw.arc((cx-16*s, mouth_y-4*s, cx+16*s, mouth_y+12*s), 200, 340, fill=color, width=3)
    # body
    neck_y=cy+head_r
    hip_y=neck_y+int(70*s)
    draw.line((cx, neck_y, cx, hip_y), fill=color, width=lw)
    # arms
    if pose=='stand':
        draw.line((cx, neck_y+10*s, cx-40*s, neck_y+40*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+40*s, neck_y+40*s), fill=color, width=lw)
    elif pose=='point_right':
        draw.line((cx, neck_y+10*s, cx-30*s, neck_y+35*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+70*s, neck_y+5*s), fill=color, width=lw)
    elif pose=='point_up':
        draw.line((cx, neck_y+10*s, cx-30*s, neck_y+35*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+10*s, neck_y-30*s), fill=color, width=lw)
    elif pose=='carry':
        draw.line((cx, neck_y+10*s, cx-50*s, neck_y+45*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+50*s, neck_y+45*s), fill=color, width=lw)
    elif pose=='shrug':
        draw.line((cx, neck_y+10*s, cx-55*s, neck_y+5*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+55*s, neck_y+5*s), fill=color, width=lw)
    elif pose=='wave':
        draw.line((cx, neck_y+10*s, cx-30*s, neck_y+35*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+60*s, neck_y-20*s), fill=color, width=lw)
    elif pose=='think':
        draw.line((cx, neck_y+10*s, cx-40*s, neck_y+50*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+30*s, neck_y+10*s), fill=color, width=lw) # hand on chin approx
    # legs
    if pose=='walk':
        draw.line((cx, hip_y, cx-25*s, hip_y+60*s), fill=color, width=lw)
        draw.line((cx, hip_y, cx+35*s, hip_y+55*s), fill=color, width=lw)
    else:
        draw.line((cx, hip_y, cx-20*s, hip_y+65*s), fill=color, width=lw)
        draw.line((cx, hip_y, cx+20*s, hip_y+65*s), fill=color, width=lw)

def draw_door(draw, x, y, w=120, h=260, open_angle=0):
    # door frame
    draw.rectangle((x,y,x+w,y+h), outline=INK, width=6)
    # door panel
    if open_angle==0:
        draw.rectangle((x+6,y+6,x+w-6,y+h-6), fill=(180,160,130), outline=INK, width=3)
    else:
        # open door skewed
        draw.polygon([(x+6,y+6),(x+w-6,y+6),(x+w-6+open_angle,y+h-6),(x+6+open_angle,y+h-6)], fill=(180,160,130), outline=INK)
    # knob
    draw.ellipse((x+w-24, y+h//2-6, x+w-12, y+h//2+6), fill=INK)

def draw_bubble(draw, x,y,w,h,text,fnt,color=INK):
    draw.rounded_rectangle((x,y,x+w,y+h), radius=24, outline=INK, width=4, fill=(255,250,235))
    # text centered
    bbox=fnt.getbbox(text)
    tw=bbox[2]-bbox[0]; th=bbox[3]-bbox[1]
    draw.text((x+(w-tw)//2, y+(h-th)//2-4), text, font=fnt, fill=color)

def scene_for_time(t):
    # returns scene id based on cue
    c=active_cue(t)
    ci=c['cue'] if c else 1
    if ci<=2: return 1
    if ci<=5: return 2
    if ci<=9: return 3
    if ci<=14: return 4
    if ci<=16: return 5
    if ci<=19: return 6
    return 7

TOTAL=tl['total']+1.0
total_frames=int(TOTAL*FPS)

for fi in range(total_frames):
    outpath=f'{FRAMES}/frame_{fi:06d}.png'
    if os.path.exists(outpath):
        continue
    t=fi/FPS
    img,draw=new_frame()
    scene=scene_for_time(t)
    c=active_cue(t)
    ci=c['cue'] if c else 1
    # scene visuals
    if scene==1:
        # hook: character walks into room
        # door on right
        draw_door(draw, 760, 600, 160, 340, open_angle=40 if t>0.5 else 0)
        # character
        walk_phase=math.sin(t*6)*0.3
        draw_stick(draw, 300+int(t*40)%200, 1050, scale=1.1, pose='walk', expr='thinking')
        # thought bubble
        draw_bubble(draw, 180, 720, 260, 90, "keys?", FONTS['kalam'], TEAL)
        # pop at end of cue2
        if t>2.8:
            draw.text((200,740), "POP!", font=FONTS['chewy_sm'], fill=TEAL)
    elif scene==2:
        # "It happens to everyone. not memory failing. it's doorway."
        draw_stick(draw, 540, 1100, scale=1.2, pose='shrug', expr='confused')
        # door behind
        draw_door(draw, 760, 620, 150, 320, open_angle=0)
        # labels
        draw.text((120,520), "not dementia", font=FONTS['nunito'], fill=GREY)
        draw.text((120,570), "not age", font=FONTS['nunito'], fill=GREY)
        draw.text((120,640), "it's the DOOR", font=FONTS['chewy_sm'], fill=TEAL)
    elif scene==3:
        # mechanism diagram
        # timeline events
        y=700
        for i in range(4):
            x=120+i*230
            draw.rounded_rectangle((x,y,x+200,y+120), radius=16, outline=INK, width=4, fill=(255,250,235))
            draw.text((x+20,y+40), f"event {i+1}", font=FONTS['nunito'], fill=INK)
        # door between event2 and3
        draw_door(draw, 540, 920, 110, 220, open_angle=20)
        draw.text((520,870), "event boundary", font=FONTS['nunito_b'], fill=TEAL)
        # character small
        draw_stick(draw, 900, 1150, scale=0.9, pose='think', expr='thinking')
        # "files away"
        draw.text((120,1320), "files away last episode", font=FONTS['chewy_sm'], fill=INK)
        draw.text((120,1400), "goal gets buried", font=FONTS['chewy_sm'], fill=TEAL)
    elif scene==4:
        # experiments
        # character carrying box across
        progress=min(1.0, (t-18.6)/ (32.0-18.6))
        cx=200+int(progress*600)
        draw_stick(draw, cx, 1100, scale=1.1, pose='carry', expr='neutral')
        # box
        draw.rectangle((cx+40,1080,cx+90,1130), outline=INK, width=4, fill=(200,180,150))
        # door at middle
        draw_door(draw, 500, 620, 150, 320, open_angle=30 if progress>0.4 else 0)
        # same distance label
        draw.text((120,520), "same distance", font=FONTS['nunito_b'], fill=INK)
        draw.text((120,570), "with or without door", font=FONTS['nunito'], fill=GREY)
        if progress>0.5:
            draw.text((cx-60,980), "forgot!", font=FONTS['chewy_sm'], fill=TEAL)
        # returning room note
        if ci>=13:
            draw.text((120,1320), "returning did not help", font=FONTS['chewy_sm'], fill=TEAL)
    elif scene==5:
        # chunking useful
        draw_stick(draw, 540, 1050, scale=1.2, pose='stand', expr='happy')
        # organized boxes
        for i in range(3):
            draw.rectangle((200+i*220, 700, 380+i*220, 820), outline=INK, width=4, fill=(255,250,235))
            draw.text((220+i*220,745), f"chunk {i+1}", font=FONTS['nunito'], fill=INK)
        draw.text((200,520), "chunking keeps memories tidy", font=FONTS['chewy_sm'], fill=TEAL)
    elif scene==6:
        # tips
        # say plan aloud
        draw_stick(draw, 300, 1080, scale=1.1, pose='point_up', expr='happy')
        draw_bubble(draw, 120, 760, 360, 110, "I need keys!", FONTS['kalam'], TEAL)
        # carry object
        draw_stick(draw, 780, 1080, scale=1.1, pose='carry', expr='smile')
        draw.rectangle((820,1060,870,1110), outline=INK, width=4, fill=(200,180,150))
        draw.text((680,760), "carry it", font=FONTS['nunito_b'], fill=INK)
        # step back
        if ci>=19:
            draw.text((300,1320), "or step back", font=FONTS['chewy_sm'], fill=TEAL)
    else:
        # payoff/callback
        draw_door(draw, 760, 600, 160, 340, open_angle=40)
        draw_stick(draw, 320, 1050, scale=1.1, pose='walk', expr='happy')
        # thought bubble stays
        draw_bubble(draw, 180, 720, 260, 90, "keys!", FONTS['kalam'], TEAL)
        draw.text((180,640), "carried through", font=FONTS['nunito_b'], fill=TEAL)
        draw.text((200,1320), "doorway will not win", font=FONTS['chewy_sm'], fill=INK)

    # caption (burned-in) near bottom but above overlay risk: bottom 300px risk, so place around y=1500? Actually bottom 300px risk -> keep text above bottom 300, so y ~1480-1600. Let's place at 1500.
    if c:
        phrase=c['text'] if 'text' in c else None
    # get phrase from cues file
    phrase=open(f'{BASE}/work/cues/cue-{ci:03d}.txt').read().strip()
    kw=KEYWORDS.get(ci,'')
    # caption at y=1500
    highlight_caption(draw, phrase, 1500, kw)

    # small progress? no
    img.save(outpath)

print('rendered', total_frames)
