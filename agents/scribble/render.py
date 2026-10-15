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
 'chewy': font(BASE+'/fonts/Chewy.ttf', 74),
 'chewy_sm': font(BASE+'/fonts/Chewy.ttf', 56),
 'nunito': font(BASE+'/fonts/Nunito-400.ttf', 38),
 'nunito_b': font(BASE+'/fonts/Nunito-700.ttf', 40),
 'kalam': font(BASE+'/fonts/Kalam.ttf', 44),
}
KEYWORDS={
1:'room',2:'forget',3:'everyone',4:'memory',5:'doorway',
6:'events',7:'boundary',8:'episode',9:'buried',10:'objects',
11:'door',12:'forgot',13:'back',14:'reset',15:'useful',
16:'tidy',17:'aloud',18:'hold',19:'pace',20:'trick',21:'win'
}

random.seed(7)
noise=Image.new('L',(W,H))
nd=noise.load()
for y in range(H):
    for x in range(W):
        nd[x,y]=random.randint(228,246)
noise=noise.filter(ImageFilter.GaussianBlur(0.8))

CREAM=(244,234,208)
INK=(26,22,18)
TEAL=(18,145,135)
GREY=(110,100,85)
PAPER=(248,240,215)

def new_frame():
    img=Image.new('RGB',(W,H),CREAM)
    n=noise.convert('RGB')
    img=Image.blend(img,n,0.3)
    return img, ImageDraw.Draw(img)

def ease(t): 
    t=max(0,min(1,t)); return t*t*(3-2*t)

def draw_text(draw, text, x, y, fnt, color=INK, anchor='left'):
    draw.text((x,y), text, font=fnt, fill=color)

def draw_stick(draw, cx, cy, scale=1.0, pose='stand', expr='neutral', color=INK, lw=7, bob=0):
    s=scale
    cy=cy+int(bob)
    head_r=int(44*s)
    # hair
    draw.arc((cx-head_r-2, cy-head_r-6, cx+head_r+2, cy+head_r), 180, 360, fill=color, width=4)
    draw.ellipse((cx-head_r, cy-head_r, cx+head_r, cy+head_r), outline=color, width=lw)
    eye_y=cy-int(8*s)
    ex=int(13*s)
    for dx in (-ex, ex):
        draw.ellipse((cx+dx-5, eye_y-5, cx+dx+5, eye_y+5), fill=color)
    # brows
    if expr=='happy':
        draw.arc((cx-24*s, eye_y-16*s, cx-4*s, eye_y), 200, 340, fill=color, width=3)
        draw.arc((cx+4*s, eye_y-16*s, cx+24*s, eye_y), 200, 340, fill=color, width=3)
    elif expr=='confused':
        draw.line((cx-22*s, eye_y-10*s, cx-2*s, eye_y-4*s), fill=color, width=3)
        draw.line((cx+2*s, eye_y-4*s, cx+22*s, eye_y-10*s), fill=color, width=3)
    elif expr=='thinking':
        draw.line((cx-22*s, eye_y-8*s, cx-2*s, eye_y-14*s), fill=color, width=3)
        draw.line((cx+2*s, eye_y-14*s, cx+22*s, eye_y-8*s), fill=color, width=3)
    elif expr=='surprised':
        draw.ellipse((cx-22*s, eye_y-12*s, cx-10*s, eye_y), outline=color, width=2)
        draw.ellipse((cx+10*s, eye_y-12*s, cx+22*s, eye_y), outline=color, width=2)
    mouth_y=cy+int(13*s)
    if expr in ('happy','smile'):
        draw.arc((cx-16*s, mouth_y-8*s, cx+16*s, mouth_y+8*s), 20, 160, fill=color, width=3)
    elif expr=='o':
        draw.ellipse((cx-7*s, mouth_y-7*s, cx+7*s, mouth_y+7*s), outline=color, width=3)
    elif expr=='flat':
        draw.line((cx-14*s, mouth_y, cx+14*s, mouth_y), fill=color, width=3)
    else:
        draw.arc((cx-16*s, mouth_y-2*s, cx+16*s, mouth_y+12*s), 200, 340, fill=color, width=3)
    neck_y=cy+head_r
    hip_y=neck_y+int(68*s)
    # shirt (filled torso)
    draw.polygon([(cx-18*s,neck_y),(cx+18*s,neck_y),(cx+22*s,hip_y),(cx-22*s,hip_y)], fill=(230,220,195), outline=color)
    draw.line((cx, neck_y, cx, hip_y), fill=color, width=lw)
    # arms
    if pose=='stand':
        draw.line((cx, neck_y+10*s, cx-42*s, neck_y+42*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+42*s, neck_y+42*s), fill=color, width=lw)
    elif pose=='point_right':
        draw.line((cx, neck_y+10*s, cx-28*s, neck_y+38*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+78*s, neck_y+2*s), fill=color, width=lw)
    elif pose=='point_up':
        draw.line((cx, neck_y+10*s, cx-28*s, neck_y+38*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+8*s, neck_y-34*s), fill=color, width=lw)
    elif pose=='carry':
        draw.line((cx, neck_y+10*s, cx-52*s, neck_y+48*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+52*s, neck_y+48*s), fill=color, width=lw)
    elif pose=='shrug':
        draw.line((cx, neck_y+10*s, cx-58*s, neck_y+2*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+58*s, neck_y+2*s), fill=color, width=lw)
    elif pose=='wave':
        draw.line((cx, neck_y+10*s, cx-28*s, neck_y+38*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+62*s, neck_y-22*s), fill=color, width=lw)
    elif pose=='think':
        draw.line((cx, neck_y+10*s, cx-40*s, neck_y+52*s), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+28*s, neck_y+12*s), fill=color, width=lw)
    elif pose=='walk':
        ph=math.sin(t_global*8)
        draw.line((cx, neck_y+10*s, cx-40*s, neck_y+44*s+int(8*ph)), fill=color, width=lw)
        draw.line((cx, neck_y+10*s, cx+40*s, neck_y+44*s-int(8*ph)), fill=color, width=lw)
    # legs
    if pose=='walk':
        ph=math.sin(t_global*8)
        draw.line((cx, hip_y, cx-24*s, hip_y+66*s+int(6*ph)), fill=color, width=lw)
        draw.line((cx, hip_y, cx+24*s, hip_y+66*s-int(6*ph)), fill=color, width=lw)
    else:
        draw.line((cx, hip_y, cx-22*s, hip_y+68*s), fill=color, width=lw)
        draw.line((cx, hip_y, cx+22*s, hip_y+68*s), fill=color, width=lw)

t_global=0.0

def draw_door(draw, x, y, w=150, h=300, open_angle=0, color=INK):
    draw.rectangle((x,y,x+w,y+h), outline=color, width=6, fill=(170,150,120))
    if open_angle:
        # door ajar
        pts=[(x+6,y+6),(x+w-6,y+6),(x+w-6+open_angle,y+h-6),(x+6+open_angle,y+h-6)]
        draw.polygon(pts, fill=(195,175,145), outline=color)
    draw.ellipse((x+w-26, y+h//2-6, x+w-14, y+h//2+6), fill=color)

def draw_bubble(draw, x,y,w,h,text,fnt,color=INK, fill=(255,250,235)):
    draw.rounded_rectangle((x,y,x+w,y+h), radius=26, outline=INK, width=4, fill=fill)
    bbox=fnt.getbbox(text); tw=bbox[2]-bbox[0]; th=bbox[3]-bbox[1]
    draw.text((x+(w-tw)//2, y+(h-th)//2-4), text, font=fnt, fill=color)

def draw_room_bg(draw, t):
    # floor line
    draw.line((0,1280,W,1280), fill=(180,165,135), width=4)
    # wall texture: subtle vertical panels
    for x in range(0,W,180):
        draw.line((x,0,x,1280), fill=(235,225,200), width=2)

def highlight_caption(draw, phrase, y, keyword):
    fnt=FONTS['chewy']
    words=phrase.split()
    space=fnt.getbbox(' ')[2]-fnt.getbbox(' ')[0]
    lines=[]; cur=[]; curw=0
    for w in words:
        ww=fnt.getbbox(w)[2]-fnt.getbbox(w)[0]
        if cur and curw+space+ww>960:
            lines.append(cur); cur=[w]; curw=ww
        else:
            cur.append(w); curw = (curw+space+ww) if curw else ww
    if cur: lines.append(cur)
    if len(lines)>2:
        mid=len(words)//2
        lines=[words[:mid], words[mid:]]
    lh=fnt.getbbox('Ag')[3]+12
    totalh=len(lines)*lh
    yy=y-totalh//2
    for ln in lines:
        widths=[fnt.getbbox(w)[2]-fnt.getbbox(w)[0] for w in ln]
        tot=sum(widths)+space*(len(ln)-1)
        x=(W-tot)//2
        for i,w in enumerate(ln):
            col=TEAL if w.strip('.,!?').lower()==keyword.lower().strip('.,!?') else INK
            # slight scale for keyword via bold? draw twice offset
            draw.text((x,yy), w, font=fnt, fill=col)
            if w.strip('.,!?').lower()==keyword.lower().strip('.,!?'):
                # underline
                wb=fnt.getbbox(w); draw.line((x,yy+lh-4,x+wb[2]-wb[0],yy+lh-4), fill=TEAL, width=4)
            x+=widths[i]+space
        yy+=lh

TOTAL=tl['total']+1.0
total_frames=int(TOTAL*FPS)

for fi in range(total_frames):
    t=fi/FPS
    t_global=t
    outpath=f'{FRAMES}/frame_{fi:06d}.png'
    if os.path.exists(outpath):
        continue
    img,draw=new_frame()
    c=active_cue(t)
    ci=c['cue']
    scene = 1 if ci<=2 else 2 if ci<=5 else 3 if ci<=9 else 4 if ci<=14 else 5 if ci<=16 else 6 if ci<=19 else 7
    bob=math.sin(t*2.2)*4
    # background room
    draw_room_bg(draw,t)
    if scene==1:
        # hallway + door
        draw_door(draw, 760, 560, 180, 360, open_angle=35)
        # character walking
        px=260+int((t/3.2)*180)
        draw_stick(draw, px, 1080, scale=1.15, pose='walk', expr='thinking', bob=bob)
        draw_bubble(draw, px-120, 760, 230, 86, "keys?", FONTS['kalam'], TEAL)
        if t>2.4:
            draw.text((px-80,700), "pop!", font=FONTS['chewy_sm'], fill=TEAL)
        # floor shadow
        draw.ellipse((px-60,1180,px+60,1210), fill=(200,185,155))
    elif scene==2:
        draw_door(draw, 760, 560, 170, 350, open_angle=0)
        draw_stick(draw, 420, 1100, scale=1.25, pose='shrug', expr='confused', bob=bob)
        draw.text((120,470), "not a bad memory", font=FONTS['nunito'], fill=GREY)
        draw.text((120,520), "not age", font=FONTS['nunito'], fill=GREY)
        draw.text((120,600), "it's the DOOR", font=FONTS['chewy_sm'], fill=TEAL)
        # brain icon
        draw.ellipse((900,470,1020,590), outline=INK, width=4)
        draw.text((925,510), "OK", font=FONTS['nunito_b'], fill=TEAL)
    elif scene==3:
        # event blocks
        y=620
        colors=[(255,250,235),(230,245,240),(255,240,225),(240,235,255)]
        for i in range(4):
            x=90+i*235
            draw.rounded_rectangle((x,y,x+210,y+130), radius=18, outline=INK, width=4, fill=colors[i])
            draw.text((x+24,y+46), f"event {i+1}", font=FONTS['nunito'], fill=INK)
        # door boundary between 2 and 3
        draw_door(draw, 500, 820, 120, 240, open_angle=18)
        draw.text((470,770), "event boundary", font=FONTS['nunito_b'], fill=TEAL)
        # files away animation: block sliding into folder
        prog=ease((t-9.4)/(18.3-9.4))
        bx=300+int(prog*400)
        draw.rounded_rectangle((bx,1320,bx+120,1400), radius=12, outline=INK, width=3, fill=(200,180,150))
        draw.text((bx+18,1345), "filed", font=FONTS['nunito'], fill=INK)
        draw_stick(draw, 920, 1120, scale=0.95, pose='point_right', expr='thinking', bob=bob)
        draw.text((90,1450), "goal gets buried", font=FONTS['chewy_sm'], fill=TEAL)
    elif scene==4:
        # split diagram: with/without door
        draw.text((120,470), "same distance", font=FONTS['nunito_b'], fill=INK)
        draw.text((120,515), "door vs no door", font=FONTS['nunito'], fill=GREY)
        # no-door path top
        draw.line((120,620,960,620), fill=GREY, width=4)
        draw.text((120,585), "no door: remember", font=FONTS['nunito'], fill=TEAL)
        # door path bottom
        draw.line((120,760,960,760), fill=GREY, width=4)
        draw_door(draw, 520, 690, 110, 140, open_angle=25)
        draw.text((120,725), "door: forget", font=FONTS['nunito'], fill=(180,60,60))
        # character carrying box
        progress=ease((t-18.6)/(32.0-18.6))
        cx=220+int(progress*560)
        draw_stick(draw, cx, 1120, scale=1.1, pose='carry', expr='neutral', bob=bob)
        draw.rectangle((cx+44,1095,cx+96,1145), outline=INK, width=4, fill=(200,180,150))
        if progress>0.45:
            draw.text((cx-70,1000), "forgot!", font=FONTS['chewy_sm'], fill=(180,60,60))
        if ci>=13:
            draw.text((120,1320), "going back didn't help", font=FONTS['chewy_sm'], fill=TEAL)
    elif scene==5:
        draw_stick(draw, 540, 1080, scale=1.2, pose='stand', expr='happy', bob=bob)
        for i in range(3):
            x=150+i*260
            draw.rounded_rectangle((x,620,x+220,760), radius=16, outline=INK, width=4, fill=(255,250,235))
            draw.text((x+30,670), f"chunk {i+1}", font=FONTS['nunito'], fill=INK)
        draw.text((150,500), "chunking keeps memories tidy", font=FONTS['chewy_sm'], fill=TEAL)
        # folder icon
        draw.rounded_rectangle((150,820,930,900), radius=12, outline=INK, width=3, fill=(240,230,200))
        draw.text((170,840), "organized", font=FONTS['nunito_b'], fill=INK)
    elif scene==6:
        # three tip panels
        tips=[("say it aloud","speech"),("hold the object","carry"),("step back","pace")]
        for i,(lab,_) in enumerate(tips):
            x=80+i*340
            draw.rounded_rectangle((x,520,x+300,720), radius=20, outline=INK, width=4, fill=(255,250,235))
            draw.text((x+30,560), lab, font=FONTS['nunito_b'], fill=INK)
        # characters
        draw_stick(draw, 230, 1080, scale=1.05, pose='point_up', expr='happy', bob=bob)
        draw_bubble(draw, 90, 760, 300, 100, "I need keys!", FONTS['kalam'], TEAL)
        draw_stick(draw, 540, 1080, scale=1.05, pose='carry', expr='smile', bob=bob)
        draw.rectangle((584,1060,636,1110), outline=INK, width=4, fill=(200,180,150))
        draw_stick(draw, 850, 1080, scale=1.05, pose='stand', expr='happy', bob=bob)
        if ci>=19:
            draw.text((300,1320), "or step back one pace", font=FONTS['chewy_sm'], fill=TEAL)
    else:
        draw_door(draw, 760, 560, 180, 360, open_angle=35)
        px=320
        draw_stick(draw, px, 1080, scale=1.15, pose='walk', expr='happy', bob=bob)
        draw_bubble(draw, px-120, 760, 230, 86, "keys!", FONTS['kalam'], TEAL)
        draw.text((120,640), "carried through", font=FONTS['nunito_b'], fill=TEAL)
        draw.text((200,1320), "the door won't win", font=FONTS['chewy_sm'], fill=INK)
        draw.ellipse((px-60,1180,px+60,1210), fill=(200,185,155))

    # caption
    phrase=open(f'{BASE}/work/cues/cue-{ci:03d}.txt').read().strip()
    kw=KEYWORDS.get(ci,'')
    highlight_caption(draw, phrase, 1520, kw)

    img.save(outpath)

print('rendered', total_frames)
