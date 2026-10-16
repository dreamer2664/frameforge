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

def active_cue(t):
    for c in cues:
        if c['start'] <= t < c['end']:
            return c
    return cues[-1]

def font(path,size):
    return ImageFont.truetype(path,size)
FONTS={
 'chewy': font(BASE+'/fonts/Chewy.ttf', 72),
 'chewy_sm': font(BASE+'/fonts/Chewy.ttf', 54),
 'nunito': font(BASE+'/fonts/Nunito-400.ttf', 36),
 'nunito_b': font(BASE+'/fonts/Nunito-700.ttf', 38),
 'kalam': font(BASE+'/fonts/Kalam.ttf', 42),
}
KEYWORDS={
1:'room',2:'forget',3:'everyone',4:'memory',5:'doorway',
6:'events',7:'boundary',8:'episode',9:'buried',10:'objects',
11:'door',12:'forgot',13:'back',14:'reset',15:'useful',
16:'tidy',17:'aloud',18:'hold',19:'pace',20:'trick',21:'win'
}

random.seed(11)
CREAM=(246,236,210)
INK=(30,26,22)
TEAL=(20,150,140)
GREY=(105,95,80)
WARM=(200,175,140)
RED=(190,70,60)
noise=Image.new('L',(W,H))
nd=noise.load()
for y in range(H):
    for x in range(W):
        nd[x,y]=random.randint(232,248)
noise=noise.filter(ImageFilter.GaussianBlur(1.0))

# precompute vignette + base background once
_vig=Image.new('L',(W,H),0)
_vd=_vig.load()
for y in range(H):
    for x in range(W):
        dx=(x-W/2)/(W/2); dy=(y-H/2)/(H/2)
        r=math.sqrt(dx*dx+dy*dy)
        _vd[x,y]=int(max(0,min(255, (r-0.6)*120)))
_vig=_vig.filter(ImageFilter.GaussianBlur(60))
_BASE_BG=Image.new('RGB',(W,H),CREAM)
_BASE_BG=Image.blend(_BASE_BG, noise.convert('RGB'), 0.25)
_BASE_BG=Image.composite(_BASE_BG, Image.new('RGB',(W,H),(220,205,175)), _vig)

def new_frame():
    return _BASE_BG.copy()

def ease(t):
    t=max(0,min(1,t)); return t*t*(3-2*t)

def scene_for_time(t):
    c=active_cue(t); ci=c['cue']
    if ci<=2: return 1
    if ci<=5: return 2
    if ci<=9: return 3
    if ci<=14: return 4
    if ci<=16: return 5
    if ci<=19: return 6
    return 7

def draw_character(draw, cx, cy, scale=1.0, pose='stand', expr='neutral', bob=0, color=INK, t=0.0):
    s=scale
    cy=int(cy+bob)
    head_r=int(42*s)
    # shadow
    draw.ellipse((cx-50*s, cy+95*s, cx+50*s, cy+115*s), fill=(210,195,165))
    # head
    draw.ellipse((cx-head_r, cy-head_r, cx+head_r, cy+head_r), fill=(252,245,225), outline=color, width=5)
    # hair tuft
    draw.arc((cx-head_r-4, cy-head_r-8, cx+head_r+4, cy+head_r), 190, 350, fill=color, width=6)
    # eyes
    eye_y=cy-int(6*s)
    ex=int(12*s)
    for dx in (-ex, ex):
        draw.ellipse((cx+dx-6, eye_y-6, cx+dx+6, eye_y+6), fill=color)
        draw.ellipse((cx+dx-2, eye_y-4, cx+dx+2, eye_y), fill=(252,245,225))
    # brows
    if expr=='happy':
        draw.arc((cx-22*s, eye_y-14*s, cx-4*s, eye_y), 200, 340, fill=color, width=3)
        draw.arc((cx+4*s, eye_y-14*s, cx+22*s, eye_y), 200, 340, fill=color, width=3)
    elif expr=='confused':
        draw.line((cx-20*s, eye_y-8*s, cx-2*s, eye_y-2*s), fill=color, width=3)
        draw.line((cx+2*s, eye_y-2*s, cx+20*s, eye_y-8*s), fill=color, width=3)
    elif expr=='thinking':
        draw.line((cx-20*s, eye_y-6*s, cx-2*s, eye_y-12*s), fill=color, width=3)
        draw.line((cx+2*s, eye_y-12*s, cx+20*s, eye_y-6*s), fill=color, width=3)
    elif expr=='surprised':
        draw.ellipse((cx-20*s, eye_y-12*s, cx-8*s, eye_y), outline=color, width=2)
        draw.ellipse((cx+8*s, eye_y-12*s, cx+20*s, eye_y), outline=color, width=2)
    # mouth
    mouth_y=cy+int(14*s)
    if expr in ('happy','smile'):
        draw.arc((cx-16*s, mouth_y-8*s, cx+16*s, mouth_y+8*s), 20, 160, fill=color, width=4)
    elif expr=='o':
        draw.ellipse((cx-7*s, mouth_y-7*s, cx+7*s, mouth_y+7*s), outline=color, width=3)
    elif expr=='flat':
        draw.line((cx-14*s, mouth_y, cx+14*s, mouth_y), fill=color, width=3)
    else:
        draw.arc((cx-16*s, mouth_y-2*s, cx+16*s, mouth_y+12*s), 200, 340, fill=color, width=3)
    # body (shirt)
    neck_y=cy+head_r
    hip_y=neck_y+int(62*s)
    draw.rounded_rectangle((cx-20*s, neck_y, cx+20*s, hip_y), radius=8, fill=(235,220,195), outline=color, width=4)
    draw.line((cx, neck_y, cx, hip_y), fill=color, width=3)
    # arms
    if pose=='stand':
        draw.line((cx, neck_y+8*s, cx-44*s, neck_y+40*s), fill=color, width=6)
        draw.line((cx, neck_y+8*s, cx+44*s, neck_y+40*s), fill=color, width=6)
    elif pose=='point_right':
        draw.line((cx, neck_y+8*s, cx-26*s, neck_y+36*s), fill=color, width=6)
        draw.line((cx, neck_y+8*s, cx+80*s, neck_y), fill=color, width=6)
    elif pose=='point_up':
        draw.line((cx, neck_y+8*s, cx-26*s, neck_y+36*s), fill=color, width=6)
        draw.line((cx, neck_y+8*s, cx+6*s, neck_y-36*s), fill=color, width=6)
    elif pose=='carry':
        draw.line((cx, neck_y+8*s, cx-50*s, neck_y+46*s), fill=color, width=6)
        draw.line((cx, neck_y+8*s, cx+50*s, neck_y+46*s), fill=color, width=6)
    elif pose=='shrug':
        draw.line((cx, neck_y+8*s, cx-58*s, neck_y), fill=color, width=6)
        draw.line((cx, neck_y+8*s, cx+58*s, neck_y), fill=color, width=6)
    elif pose=='wave':
        draw.line((cx, neck_y+8*s, cx-26*s, neck_y+36*s), fill=color, width=6)
        draw.line((cx, neck_y+8*s, cx+60*s, neck_y-24*s), fill=color, width=6)
    elif pose=='think':
        draw.line((cx, neck_y+8*s, cx-38*s, neck_y+50*s), fill=color, width=6)
        draw.line((cx, neck_y+8*s, cx+26*s, neck_y+10*s), fill=color, width=6)
    elif pose=='walk':
        ph=math.sin(t*8)
        draw.line((cx, neck_y+8*s, cx-40*s, neck_y+42*s+int(8*ph*s)), fill=color, width=6)
        draw.line((cx, neck_y+8*s, cx+40*s, neck_y+42*s-int(8*ph*s)), fill=color, width=6)
    # legs
    if pose=='walk':
        ph=math.sin(t*8)
        draw.line((cx, hip_y, cx-24*s, hip_y+66*s+int(6*ph*s)), fill=color, width=6)
        draw.line((cx, hip_y, cx+24*s, hip_y+66*s-int(6*ph*s)), fill=color, width=6)
        # shoes
        draw.ellipse((cx-34*s+int(6*ph*s), hip_y+128*s+int(6*ph*s), cx-14*s+int(6*ph*s), hip_y+142*s+int(6*ph*s)), fill=color)
        draw.ellipse((cx+14*s-int(6*ph*s), hip_y+128*s-int(6*ph*s), cx+34*s-int(6*ph*s), hip_y+142*s-int(6*ph*s)), fill=color)
    else:
        draw.line((cx, hip_y, cx-22*s, hip_y+68*s), fill=color, width=6)
        draw.line((cx, hip_y, cx+22*s, hip_y+68*s), fill=color, width=6)
        draw.ellipse((cx-32*s, hip_y+128*s, cx-12*s, hip_y+142*s), fill=color)
        draw.ellipse((cx+12*s, hip_y+128*s, cx+32*s, hip_y+142*s), fill=color)

def draw_door(draw, x, y, w=160, h=320, open_angle=0):
    # frame
    draw.rectangle((x-8,y-8,x+w+8,y+h+8), fill=(150,130,105), outline=INK, width=4)
    draw.rectangle((x,y,x+w,y+h), fill=(175,155,125), outline=INK, width=4)
    if open_angle:
        pts=[(x+6,y+6),(x+w-6,y+6),(x+w-6+open_angle,y+h-6),(x+6+open_angle,y+h-6)]
        draw.polygon(pts, fill=(200,180,150), outline=INK)
    # knob
    draw.ellipse((x+w-28, y+h//2-8, x+w-12, y+h//2+8), fill=(90,75,55), outline=INK, width=2)

def draw_bubble(draw, x,y,w,h,text,fnt,color=INK, fill=(255,250,235)):
    draw.rounded_rectangle((x,y,x+w,y+h), radius=28, outline=INK, width=4, fill=fill)
    # tail
    draw.polygon([(x+40,y+h),(x+60,y+h),(x+30,y+h+20)], fill=fill, outline=INK)
    bbox=fnt.getbbox(text); tw=bbox[2]-bbox[0]; th=bbox[3]-bbox[1]
    draw.text((x+(w-tw)//2, y+(h-th)//2-4), text, font=fnt, fill=color)

def draw_room_bg(draw):
    # wall
    draw.rectangle((0,0,W,1300), fill=(242,232,205))
    # floor
    draw.rectangle((0,1300,W,H), fill=(215,195,160))
    # baseboard
    draw.rectangle((0,1285,W,1315), fill=(195,175,140), outline=INK, width=2)
    # subtle panel lines
    for x in range(0,W,220):
        draw.line((x,0,x,1300), fill=(232,222,195), width=2)

def highlight_caption(draw, phrase, y, keyword):
    fnt=FONTS['chewy']
    words=phrase.split()
    space=fnt.getbbox(' ')[2]-fnt.getbbox(' ')[0]
    lines=[]; cur=[]; curw=0
    for w in words:
        ww=fnt.getbbox(w)[2]-fnt.getbbox(w)[0]
        if cur and curw+space+ww>950:
            lines.append(cur); cur=[w]; curw=ww
        else:
            cur.append(w); curw = (curw+space+ww) if curw else ww
    if cur: lines.append(cur)
    if len(lines)>2:
        mid=len(words)//2
        lines=[words[:mid], words[mid:]]
    lh=fnt.getbbox('Ag')[3]+14
    totalh=len(lines)*lh
    yy=y-totalh//2
    for ln in lines:
        widths=[fnt.getbbox(w)[2]-fnt.getbbox(w)[0] for w in ln]
        tot=sum(widths)+space*(len(ln)-1)
        x=(W-tot)//2
        for i,w in enumerate(ln):
            col=TEAL if w.strip('.,!?').lower()==keyword.lower().strip('.,!?') else INK
            draw.text((x,yy), w, font=fnt, fill=col)
            if w.strip('.,!?').lower()==keyword.lower().strip('.,!?'):
                wb=fnt.getbbox(w); draw.line((x,yy+lh-6,x+wb[2]-wb[0],yy+lh-6), fill=TEAL, width=5)
            x+=widths[i]+space
        yy+=lh

def scene_image(t):
    img=new_frame()
    draw=ImageDraw.Draw(img)
    draw_room_bg(draw)
    c=active_cue(t); ci=c['cue']
    scene=scene_for_time(t)
    bob=math.sin(t*2.4)*5
    if scene==1:
        draw_door(draw, 760, 520, 180, 340, open_angle=30)
        px=280+int((t/max(0.1,active_cue(t)['end']))*120) if False else 300+int((t%3)*30)
        px=320+int(math.sin(t*1.5)*20)
        draw_character(draw, px, 1080, scale=1.15, pose='walk', expr='thinking', bob=bob, t=t)
        draw_bubble(draw, px-130, 740, 240, 90, "keys?", FONTS['kalam'], TEAL)
        if t>2.4:
            draw.text((px-90,690), "pop!", font=FONTS['chewy_sm'], fill=TEAL)
    elif scene==2:
        draw_door(draw, 760, 520, 170, 340, open_angle=0)
        draw_character(draw, 420, 1100, scale=1.2, pose='shrug', expr='confused', bob=bob, t=t)
        draw.text((110,460), "not a bad memory", font=FONTS['nunito'], fill=GREY)
        draw.text((110,505), "not age", font=FONTS['nunito'], fill=GREY)
        draw.text((110,585), "it's the DOOR", font=FONTS['chewy_sm'], fill=TEAL)
        # brain icon
        draw.ellipse((880,450,1010,580), fill=(252,245,225), outline=INK, width=4)
        draw.text((915,495), "OK", font=FONTS['nunito_b'], fill=TEAL)
    elif scene==3:
        y=600
        cols=[(255,250,235),(232,245,240),(255,240,225),(240,235,255)]
        for i in range(4):
            x=80+i*240
            draw.rounded_rectangle((x,y,x+215,y+135), radius=18, fill=cols[i], outline=INK, width=4)
            draw.text((x+26,y+48), f"event {i+1}", font=FONTS['nunito'], fill=INK)
        draw_door(draw, 500, 800, 125, 250, open_angle=18)
        draw.text((475,755), "event boundary", font=FONTS['nunito_b'], fill=TEAL)
        prog=ease((t-9.4)/(18.3-9.4))
        bx=280+int(prog*420)
        draw.rounded_rectangle((bx,1320,bx+130,1405), radius=12, fill=WARM, outline=INK, width=3)
        draw.text((bx+20,1348), "filed", font=FONTS['nunito'], fill=INK)
        draw_character(draw, 920, 1120, scale=0.9, pose='point_right', expr='thinking', bob=bob, t=t)
        draw.text((80,1450), "goal gets buried", font=FONTS['chewy_sm'], fill=TEAL)
    elif scene==4:
        draw.text((110,460), "same distance", font=FONTS['nunito_b'], fill=INK)
        draw.text((110,505), "door vs no door", font=FONTS['nunito'], fill=GREY)
        draw.line((110,610,970,610), fill=GREY, width=4)
        draw.text((110,575), "no door: remember", font=FONTS['nunito'], fill=TEAL)
        draw.line((110,750,970,750), fill=GREY, width=4)
        draw_door(draw, 520, 680, 115, 145, open_angle=25)
        draw.text((110,715), "door: forget", font=FONTS['nunito'], fill=RED)
        progress=ease((t-18.6)/(32.0-18.6))
        cx=220+int(progress*560)
        draw_character(draw, cx, 1120, scale=1.05, pose='carry', expr='neutral', bob=bob, t=t)
        draw.rounded_rectangle((cx+46,1092,cx+100,1148), radius=8, fill=WARM, outline=INK, width=4)
        if progress>0.45:
            draw.text((cx-75,995), "forgot!", font=FONTS['chewy_sm'], fill=RED)
        if ci>=13:
            draw.text((110,1320), "going back didn't help", font=FONTS['chewy_sm'], fill=TEAL)
    elif scene==5:
        draw_character(draw, 540, 1080, scale=1.15, pose='stand', expr='happy', bob=bob, t=t)
        for i in range(3):
            x=140+i*270
            draw.rounded_rectangle((x,610,x+230,760), radius=16, fill=(255,250,235), outline=INK, width=4)
            draw.text((x+34,668), f"chunk {i+1}", font=FONTS['nunito'], fill=INK)
        draw.text((140,495), "chunking keeps memories tidy", font=FONTS['chewy_sm'], fill=TEAL)
        draw.rounded_rectangle((140,810,940,895), radius=14, fill=(240,230,200), outline=INK, width=3)
        draw.text((165,835), "organized", font=FONTS['nunito_b'], fill=INK)
    elif scene==6:
        tips=["say it aloud","hold the object","step back"]
        for i,lab in enumerate(tips):
            x=70+i*345
            draw.rounded_rectangle((x,510,x+310,720), radius=22, fill=(255,250,235), outline=INK, width=4)
            draw.text((x+28,565), lab, font=FONTS['nunito_b'], fill=INK)
        draw_character(draw, 230, 1080, scale=1.0, pose='point_up', expr='happy', bob=bob, t=t)
        draw_bubble(draw, 80, 750, 310, 105, "I need keys!", FONTS['kalam'], TEAL)
        draw_character(draw, 540, 1080, scale=1.0, pose='carry', expr='smile', bob=bob, t=t)
        draw.rounded_rectangle((586,1058,640,1112), radius=8, fill=WARM, outline=INK, width=4)
        draw_character(draw, 850, 1080, scale=1.0, pose='stand', expr='happy', bob=bob, t=t)
        if ci>=19:
            draw.text((290,1320), "or step back one pace", font=FONTS['chewy_sm'], fill=TEAL)
    else:
        draw_door(draw, 760, 520, 180, 340, open_angle=30)
        px=320
        draw_character(draw, px, 1080, scale=1.15, pose='walk', expr='happy', bob=bob, t=t)
        draw_bubble(draw, px-130, 740, 240, 90, "keys!", FONTS['kalam'], TEAL)
        draw.text((110,640), "carried through", font=FONTS['nunito_b'], fill=TEAL)
        draw.text((200,1320), "the door won't win", font=FONTS['chewy_sm'], fill=INK)
    return img

TOTAL=tl['total']+1.0
total_frames=int(TOTAL*FPS)

# scene start times for fade
scene_starts={}
for fi in range(total_frames):
    t=fi/FPS
    s=scene_for_time(t)
    if s not in scene_starts:
        scene_starts[s]=t

for fi in range(total_frames):
    t=fi/FPS
    outpath=f'{FRAMES}/frame_{fi:06d}.png'
    if os.path.exists(outpath):
        continue
    img=scene_image(t)
    # fade transition
    s=scene_for_time(t)
    ss=scene_starts[s]
    if t-ss < 0.35 and s>1:
        prev_t=max(0, ss-0.05)
        prev_img=scene_image(prev_t)
        alpha=ease((t-ss)/0.35)
        img=Image.blend(prev_img, img, alpha)
    # caption
    draw=ImageDraw.Draw(img)
    c=active_cue(t); ci=c['cue']
    phrase=open(f'{BASE}/work/cues/cue-{ci:03d}.txt').read().strip()
    kw=KEYWORDS.get(ci,'')
    highlight_caption(draw, phrase, 1520, kw)
    img.save(outpath)

print('rendered', total_frames)
