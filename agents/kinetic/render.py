"""Deterministic 30fps Kinetic film renderer. Draws original 1280x720 frames; FFmpeg upsamples to 1920x1080 H.264."""
from __future__ import annotations
import argparse, math, os, shutil, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE, 'fonts')
W, H = 1280, 720
FPS = 30
DURATION = 27.0
SCALE = 2
LW, LH = W // SCALE, H // SCALE

# Art direction: ink / ember / paper / cool glass. Colors are deliberately limited.
INK_TOP = (17, 19, 25)
INK_BOTTOM = (7, 9, 14)
PAPER_TOP = (243, 240, 233)
PAPER_BOTTOM = (231, 227, 219)
IVORY = (243, 238, 229)
WARM = (231, 164, 97)
WARM_HI = (255, 224, 182)
COOL = (112, 147, 174)
COOL_DARK = (67, 107, 139)
DARK_TYPE = (32, 39, 48)
MUTED_LIGHT = (173, 181, 188)
MUTED_DARK = (89, 96, 102)


def clamp(v, lo=0.0, hi=1.0): return max(lo, min(hi, v))
def lerp(a, b, p): return a + (b - a) * p
def smooth(a, b, v):
    if b == a: return 1.0 if v >= b else 0.0
    x = clamp((v-a)/(b-a))
    return x*x*(3.0-2.0*x)
def ease_out(v):
    x = clamp(v)
    return 1.0-(1.0-x)**3

def mixc(a, b, p): return tuple(int(lerp(a[i], b[i], p)) for i in range(3))

@lru_cache(maxsize=192)
def font(kind: str, size: int, weight: int = 500):
    size = max(8, int(size))
    if kind == 'display':
        f = ImageFont.truetype(os.path.join(FONT_DIR, 'Fraunces.ttf'), size)
        # Fraunces axes: optical size, weight, softness, wonk.
        f.set_variation_by_axes([min(144, max(9, size)), min(900, max(100, int(weight))), 0, 0])
        return f
    if kind == 'playfair':
        f = ImageFont.truetype(os.path.join(FONT_DIR, 'PlayfairDisplay.ttf'), size)
        f.set_variation_by_axes([min(900, max(400, int(weight)))])
        return f
    face = 'Inter-Regular.ttf'
    if weight >= 700: face = 'Inter-Bold.ttf'
    elif weight >= 600: face = 'Inter-SemiBold.ttf'
    elif weight >= 500: face = 'Inter-Medium.ttf'
    return ImageFont.truetype(os.path.join(FONT_DIR, face), size)


def make_gradient(top, bottom):
    im = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        p = y / max(1, H-1)
        c = tuple(int(top[i]*(1-p) + bottom[i]*p) for i in range(3))
        d.line((0, y, W, y), fill=c)
    return im


def add_static_glow(base, cx, cy, radius, color, alpha, blur=None):
    layer = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = radius / SCALE
    d.ellipse((cx/SCALE-r, cy/SCALE-r, cx/SCALE+r, cy/SCALE+r), fill=(*color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur if blur is not None else radius/(SCALE*2.2)))
    base = base.convert('RGBA')
    base.alpha_composite(layer.resize((W,H), Image.Resampling.BICUBIC))
    return base.convert('RGB')


def make_base(top, bottom, glows):
    im = make_gradient(top, bottom)
    for cx, cy, rad, color, alpha in glows:
        im = add_static_glow(im, cx, cy, rad, color, alpha)
    return im

DARK_BG = make_base(INK_TOP, INK_BOTTOM, [
    (75, 600, 350, (170, 82, 36), 34),
    (1140, 150, 300, (56, 89, 117), 22),
])
PAPER_BG = make_base(PAPER_TOP, PAPER_BOTTOM, [
    (1030, 190, 400, (111, 153, 179), 25),
    (140, 600, 250, (204, 155, 97), 17),
])


def local_text_layer(text, f, color, alpha=255):
    box = f.getbbox(text)
    ww = max(1, box[2]-box[0])
    hh = max(1, box[3]-box[1])
    layer = Image.new('RGBA', (ww+4, hh+4), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.text((2-box[0], 2-box[1]), text, font=f, fill=(*color, int(clamp(alpha/255)*255)))
    return layer


def draw_text(img, text, x, y, f, color, alpha=255, reveal=1.0, feather=2):
    if not text: return
    layer = local_text_layer(text, f, color, alpha)
    reveal = clamp(reveal)
    if reveal < 0.999:
        mask = Image.new('L', layer.size, 0)
        md = ImageDraw.Draw(mask)
        edge = int((layer.width-3) * reveal)
        md.rectangle((0,0,edge,layer.height), fill=255)
        if feather > 0:
            mask = mask.filter(ImageFilter.GaussianBlur(feather))
        layer.putalpha(ImageChops.multiply(layer.getchannel('A'), mask))
    img.alpha_composite(layer, (int(x), int(y)))


def centered_x(text, f, cx):
    b = f.getbbox(text)
    return int(cx - (b[2]-b[0])/2 - b[0])

def draw_center(img, text, cx, y, f, color, alpha=255, reveal=1.0):
    draw_text(img, text, centered_x(text, f, cx), y, f, color, alpha, reveal)

def draw_tracking(img, text, x, y, f, color, spacing=2, alpha=255):
    xx = x
    for ch in text:
        draw_text(img, ch, xx, y, f, color, alpha)
        xx += f.getlength(ch) + spacing
    return xx-x


def cubic(p0,p1,p2,p3,u):
    v=1.0-u
    return (v*v*v*p0[0]+3*v*v*u*p1[0]+3*v*u*u*p2[0]+u*u*u*p3[0],
            v*v*v*p0[1]+3*v*v*u*p1[1]+3*v*u*u*p2[1]+u*u*u*p3[1])

def bezier(p0,p1,p2,p3,n=90): return [cubic(p0,p1,p2,p3,i/(n-1)) for i in range(n)]

def poly_partial(points, progress):
    if not points: return []
    progress = clamp(progress)
    if progress <= 0: return [points[0]]
    lengths=[]; total=0.0
    for a,b in zip(points,points[1:]):
        d=math.hypot(b[0]-a[0],b[1]-a[1]); lengths.append(d); total+=d
    if total <= 0: return [points[0]]
    target=progress*total; out=[points[0]]; sofar=0.0
    for i,d in enumerate(lengths):
        a,b=points[i],points[i+1]
        if sofar+d <= target:
            out.append(b); sofar+=d; continue
        u=(target-sofar)/max(1e-9,d)
        out.append((lerp(a[0],b[0],u),lerp(a[1],b[1],u)))
        break
    return out

def point_along(points, progress):
    part=poly_partial(points,progress)
    return part[-1] if part else points[0]


def draw_path(img, points, progress=1.0, color=WARM, width=2, glow=12, alpha=255):
    pts=poly_partial(points,progress)
    if len(pts) < 2: return
    # broad, low-opacity aura on a half-resolution layer; crisp core remains at full resolution
    if glow > 0 and alpha > 1:
        aura=Image.new('RGBA',(LW,LH),(0,0,0,0)); ad=ImageDraw.Draw(aura)
        q=[(int(x/SCALE),int(y/SCALE)) for x,y in pts]
        ad.line(q,fill=(*color,int(alpha*0.22)),width=max(2,int(width/SCALE)+5),joint='curve')
        aura=aura.filter(ImageFilter.GaussianBlur(max(2,int(glow/SCALE))))
        img.alpha_composite(aura.resize((W,H),Image.Resampling.BICUBIC))
    d=ImageDraw.Draw(img)
    d.line([(int(x),int(y)) for x,y in pts],fill=(*color,int(alpha)),width=max(1,int(width)),joint='curve')
    # rounded bright tip for a designed drawing action
    if alpha>10:
        x,y=pts[-1]; r=max(2,width*1.15)
        d.ellipse((int(x-r),int(y-r),int(x+r),int(y+r)),fill=(*color,int(alpha)))


def draw_dot(img, xy, color=WARM_HI, radius=4, alpha=255, glow=36):
    x,y=xy
    if alpha>1 and glow>0:
        aura=Image.new('RGBA',(LW,LH),(0,0,0,0)); d=ImageDraw.Draw(aura)
        r=glow/SCALE
        d.ellipse((x/SCALE-r,y/SCALE-r,x/SCALE+r,y/SCALE+r),fill=(*color,int(alpha*0.42)))
        aura=aura.filter(ImageFilter.GaussianBlur(max(2,glow/SCALE*0.48)))
        img.alpha_composite(aura.resize((W,H),Image.Resampling.BICUBIC))
    d=ImageDraw.Draw(img); r=radius
    d.ellipse((int(x-r),int(y-r),int(x+r),int(y+r)),fill=(*color,int(alpha)))
    d.ellipse((int(x-r*.4),int(y-r*.4),int(x+r*.4),int(y+r*.4)),fill=(255,249,235,int(alpha)))


def draw_rule(img, x1,y1,x2,y2, color, width=1, alpha=130):
    ImageDraw.Draw(img).line((int(x1),int(y1),int(x2),int(y2)),fill=(*color,int(alpha)),width=max(1,int(width)))

def draw_label(img, text, x=138, y=112, light=True, accent=None):
    color = accent or (WARM if light else COOL_DARK)
    f=font('ui',20,500)
    draw_tracking(img,text,x,y,f,color,spacing=1.6,alpha=235)
    rulecol=(103,107,112) if light else (174,177,178)
    draw_rule(img,x,y+34,W-138,y+34,rulecol,1,70)


def draw_morph_center(img, old, new, cx, y, f, color, p):
    p=clamp(p)
    if p <= 0.001:
        draw_center(img,old,cx,y,f,color); return
    if p >= 0.999:
        draw_center(img,new,cx,y,f,color); return
    old_layer=local_text_layer(old,f,color,255)
    new_layer=local_text_layer(new,f,color,255)
    old_x=centered_x(old,f,cx); new_x=centered_x(new,f,cx)
    old_full=Image.new('RGBA',(W,H),(0,0,0,0)); new_full=Image.new('RGBA',(W,H),(0,0,0,0))
    old_full.alpha_composite(old_layer,(old_x,y))
    new_full.alpha_composite(new_layer,(new_x,y))
    # The wipe spans the actual glyph silhouettes, not an arbitrary screen-width mask.
    left=min(old_x+2,new_x+2)-8
    right=max(old_x+old_layer.width-2,new_x+new_layer.width-2)+8
    edge=int(lerp(left,right,p))
    mask=Image.new('L',(W,H),0); md=ImageDraw.Draw(mask)
    md.rectangle((0,0,edge,H),fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(3))
    new_full.putalpha(ImageChops.multiply(new_full.getchannel('A'),mask))
    inv=ImageChops.invert(mask)
    old_full.putalpha(ImageChops.multiply(old_full.getchannel('A'),inv))
    img.alpha_composite(old_full); img.alpha_composite(new_full)
    # A thin warm seam makes the word replacement visibly caused by the moving line.
    seam_alpha=int(210*math.sin(math.pi*p))
    if seam_alpha>3:
        aura=Image.new('RGBA',(LW,LH),(0,0,0,0)); ad=ImageDraw.Draw(aura)
        ad.line((edge/SCALE,(y-10)/SCALE,edge/SCALE,(y+100)/SCALE),fill=(*WARM,seam_alpha//2),width=5)
        aura=aura.filter(ImageFilter.GaussianBlur(7))
        img.alpha_composite(aura.resize((W,H),Image.Resampling.BICUBIC))
        ImageDraw.Draw(img).line((edge,y-8,edge,y+96),fill=(*WARM_HI,seam_alpha),width=2)


def draw_periodic_bg_light(img,t,intensity=1.0):
    # Slow, low-amplitude warm breath. Same phase every 5 seconds; never floods text.
    a=22+int(5*(0.5+0.5*math.sin(2*math.pi*t/5.0)))
    add=Image.new('RGBA',(LW,LH),(0,0,0,0)); d=ImageDraw.Draw(add)
    d.ellipse((70,500/SCALE,360,650/SCALE),fill=(231,164,97,int(a*intensity)))
    add=add.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(add.resize((W,H),Image.Resampling.BICUBIC))


def draw_logo_mark(img, x, y, size=100, progress=1.0, alpha=255, warm=WARM, cool=COOL):
    # Original asymmetric K monogram, drawn from three independent tapered paths.
    h=size; w=size*0.68
    spine=[(x+w*.24,y),(x+w*.24,y+h)]
    upper=bezier((x+w*.24,y+h*.5),(x+w*.37,y+h*.43),(x+w*.55,y+h*.18),(x+w,y+h*.05),36)
    lower=bezier((x+w*.24,y+h*.5),(x+w*.37,y+h*.58),(x+w*.57,y+h*.87),(x+w,y+h*.98),36)
    if progress <= .24:
        draw_path(img,spine,progress/.24,warm,3,9,alpha)
    else:
        draw_path(img,spine,1,warm,3,9,alpha)
    p2=clamp((progress-.20)/.43)
    if p2>0: draw_path(img,upper,p2,warm,3,10,alpha)
    p3=clamp((progress-.57)/.43)
    if p3>0: draw_path(img,lower,p3,cool,3,10,alpha)


def draw_hero_frame(t: float) -> Image.Image:
    t=clamp(t,0.0,DURATION)
    # A single editorial palette inversion at each transition avoids a long muddy gray dissolve.
    # The filament and frame carry continuity across the deliberate hard color-state cut.
    paper=1.0 if 9.40 <= t < 16.50 else 0.0
    img=Image.blend(DARK_BG,PAPER_BG,paper).convert('RGBA')
    draw_periodic_bg_light(img,t,1.0-paper)

    if t < 3.0:
        # 01 — One thought appears as a point; the line writes its underline.
        draw_label(img,'01  /  SPARK',light=True)
        path=bezier((110,435),(215,435),(305,408),(500,430),72)
        u=clamp(t/1.48)
        draw_path(img,path,u,WARM,2,15,alpha=int(255*ease_out(u)))
        p= smooth(0.03,0.80,t)
        display=font('display',112,590)
        draw_text(img,'A thought',145,258,display,IVORY,alpha=255,reveal=p,feather=3)
        support=font('ui',27,400)
        draw_text(img,'starts with one point.',151,397,support,MUTED_LIGHT,alpha=int(235*smooth(.35,1.05,t)),reveal=smooth(.32,.94,t))
        q=point_along(path,u)
        draw_dot(img,q,WARM_HI,4,int(255*smooth(0,.15,t)),42)
        # a compact, readable echo of the first point
        d=ImageDraw.Draw(img)
        d.ellipse((116,430,124,438),outline=(*WARM,145),width=1)

    elif t < 6.1:
        # 02 — The same filament takes a chosen direction and writes the new phrase.
        draw_label(img,'02  /  DIRECTION',light=True)
        path=bezier((500,430),(610,470),(655,368),(780,395),65)+bezier((780,395),(890,420),(1010,472),(1142,316),65)[1:]
        u=clamp((t-3.0)/2.72)
        draw_path(img,path,ease_out(u),WARM,2,15,alpha=int(255*smooth(3.02,3.35,t)))
        display=font('display',97,570)
        p=smooth(3.08,4.20,t)
        draw_text(img,'Give it a line.',145,267,display,IVORY,alpha=255,reveal=p,feather=3)
        body=font('ui',26,400)
        draw_text(img,'A direction is a decision.',151,394,body,MUTED_LIGHT,alpha=int(225*smooth(3.85,4.55,t)),reveal=smooth(3.82,4.6,t))
        q=point_along(path,ease_out(u))
        draw_dot(img,q,WARM_HI,4,255,40)
        # end node makes the line feel deliberate, not a cursor wandering at random
        if t>5.0:
            d=ImageDraw.Draw(img); xx,yy=path[-1]
            d.ellipse((xx-10,yy-10,xx+10,yy+10),outline=(*WARM,100),width=1)

    elif t < 9.2:
        # 03 — One drawn line branches into a three-part tempo.
        draw_label(img,'03  /  FIND THE RHYTHM',light=True)
        centers=[230,640,1050]
        words=['pause','pulse','repeat']
        # incoming line continues from the direction beat into a single baseline
        connector=bezier((1142,316),(1150,430),(1030,438),(centers[0],444),74)
        draw_path(img,connector,smooth(6.10,6.55,t),WARM,2,13,alpha=int(245*smooth(6.12,6.32,t)))
        draw_rule(img,centers[0],444,centers[2],444,(149,136,119),1,110)
        travel=smooth(6.48,8.75,t)
        route=bezier((centers[0],444),(430,432),(775,456),(centers[2],444),80)
        draw_path(img,route,travel,WARM,2,12,alpha=230)
        q=point_along(route,travel)
        draw_dot(img,q,WARM_HI,4,255,32)
        f=font('display',70,560)
        small=font('ui',20,500)
        thresholds=[6.48,7.28,8.08]
        for i,(cx,word,at) in enumerate(zip(centers,words,thresholds)):
            a=smooth(at,at+.48,t)
            # active word turns warm-white as the travelling pulse reaches its node
            active=smooth(at+.12,at+.56,t)
            col=mixc(MUTED_LIGHT,IVORY,active)
            draw_center(img,word,cx,324,f,col,alpha=int(255*a))
            d=ImageDraw.Draw(img)
            rr=4+int(2*math.sin(max(0,t-at)*5)) if t>=at else 4
            d.ellipse((cx-rr,444-rr,cx+rr,444+rr),fill=(*WARM_HI,int(230*a)))
            draw_center(img,f'0{i+1}',cx,478,small,(135,132,126),alpha=int(210*a))

    elif t < 12.5:
        # 04 — The baseline folds into an open frame. A seam changes a word, not the scene.
        draw_label(img,'04  /  GIVE IT FORM',light=False,accent=COOL_DARK)
        p=smooth(9.18,10.55,t)
        start=(1050,444)
        polygon=[start,(988,520),(286,505),(258,230),(1008,208),(1050,444)]
        outline=poly_partial(polygon,p)
        draw_path(img,outline,1,COOL_DARK,2,9,alpha=int(210*smooth(9.25,9.7,t)))
        # one copper anchor remains at the end of the route
        q=point_along(polygon,p)
        draw_dot(img,q,WARM,3,int(230*smooth(9.2,9.45,t)),30)
        display=font('display',91,610)
        morph=smooth(10.52,10.68,t)
        draw_morph_center(img,'A thought','A world',640,317,display,DARK_TYPE,morph)
        body=font('ui',25,400)
        draw_center(img,'becomes a place to go.',640,430,body,(74,82,88),alpha=int(238*smooth(11.24,11.58,t)))
        # fine registration ticks are part of the frame, not tiny interface controls
        if t>10.1:
            d=ImageDraw.Draw(img)
            for xx,yy in [(258,230),(1008,208),(1050,444),(286,505)]:
                d.ellipse((xx-3,yy-3,xx+3,yy+3),fill=(*COOL_DARK,180))

    elif t < 16.5:
        # 05 — The frame opens past its margins; the copy remains in clear negative space.
        draw_label(img,'05  /  OPEN THE FRAME',light=False,accent=COOL_DARK)
        p=smooth(12.48,14.25,t)
        old=[(258,230),(1008,208),(1050,444),(286,505)]
        new=[(28,80),(1240,64),(1264,635),(22,638)]
        corners=[(lerp(old[i][0],new[i][0],p),lerp(old[i][1],new[i][1],p)) for i in range(4)]
        draw_path(img,corners+[corners[0]],1,mixc(COOL_DARK,(151,169,178),p),2,7,alpha=int(150*(1-.25*p)))
        # The seam leaves the frame as an underline; it traverses to the sentence's end.
        line=bezier((1050,444),(1030,493),(930,520),(812,520),60)
        line2=bezier((812,520),(690,520),(570,520),(180,520),70)
        allpath=line+line2[1:]
        u=clamp((t-12.5)/3.55)
        draw_path(img,allpath,ease_out(u),COOL_DARK,2,10,alpha=185)
        q=point_along(allpath,ease_out(u)); draw_dot(img,q,COOL,3,230,32)
        display=font('display',112,600)
        # Keep complete words inside the evolving frame, then let the frame outrun them.
        text_x=int(lerp(300,172,p))
        make_p=ease_out(smooth(12.76,13.08,t))
        room_p=ease_out(smooth(13.04,13.36,t))
        make_y=257+int(9*(1-make_p)); room_y=257+int(9*(1-room_p))
        draw_text(img,'Make',text_x,make_y,display,DARK_TYPE,alpha=int(255*make_p))
        room_x=text_x+display.getlength('Make ')
        draw_text(img,'room.',room_x,room_y,display,DARK_TYPE,alpha=int(255*room_p))
        body=font('ui',27,400)
        draw_text(img,'for the unexpected.',text_x+8,396,body,MUTED_DARK,alpha=int(230*smooth(13.35,14.12,t)),reveal=smooth(13.35,14.1,t))

    elif t < 20.5:
        # 06 — The paper recedes; the moving point lands in the punctuation.
        draw_label(img,'06  /  MEANING',light=True)
        p=ease_out(smooth(16.52,17.24,t))
        display=font('display',105,590)
        display2=font('ui',76,550)
        draw_text(img,'Meaning,',170,262,display,IVORY,alpha=255,reveal=p,feather=3)
        p2=ease_out(smooth(17.05,18.0,t))
        draw_text(img,'in motion.',180,389,display2,IVORY,alpha=int(255*p2),reveal=p2,feather=2)
        # same seam continues under the statement and finds its terminal point
        payoff=bezier((180,520),(390,520),(770,540),(980,520),64)
        u=smooth(16.5,19.2,t)
        draw_path(img,payoff,u,WARM,2,13,alpha=240)
        q=point_along(payoff,u); draw_dot(img,q,WARM_HI,4,255,38)
        # a soft cool echo, separated from the copy
        if t>18.4:
            d=ImageDraw.Draw(img)
            d.ellipse((1000,506,1028,534),outline=(*COOL,100),width=1)

    elif t < 23.4:
        # 07 — The writing stroke becomes a new K monogram.
        draw_label(img,'07  /  SIGNATURE',light=True)
        connector=bezier((980,520),(900,485),(720,420),(518,360),56)
        cp=clamp((t-20.5)/.78)
        connector_alpha=int(230*(1-smooth(21.02,21.52,t)))
        if connector_alpha>2:
            draw_path(img,connector,ease_out(cp),WARM,2,14,alpha=connector_alpha)
        q=point_along(connector,ease_out(cp))
        if t<21.52: draw_dot(img,q,WARM_HI,4,int(250*smooth(20.5,20.68,t)*(1-smooth(21.02,21.52,t))),36)
        kp=clamp((t-21.0)/1.58)
        draw_logo_mark(img,486,305,100,kp,alpha=int(255*smooth(20.82,21.08,t)))
        if t>21.72:
            a=smooth(21.72,22.45,t)
            word=font('ui',48,600)
            w=draw_tracking(img,'KINETIC',592,326,word,IVORY,spacing=5.0,alpha=int(255*a))
        # signature group drifts into its final centered position by a few pixels
        if t>22.35:
            b=smooth(22.35,23.35,t)
            draw_center(img,'Ideas, in motion.',640,445,font('ui',25,400),MUTED_LIGHT,alpha=int(235*b))

    else:
        # 08 — Deliberate, readable end lock-up. Only the small light phase breathes.
        breath=.94+.06*(.5+.5*math.sin(2*math.pi*t/5.0))
        img=add_static_glow(img,520,360,92*breath,WARM,18).convert('RGBA')
        draw_logo_mark(img,486,305,100,1.0,255)
        word=font('ui',48,600)
        draw_tracking(img,'KINETIC',592,326,word,IVORY,spacing=5.0,alpha=255)
        draw_center(img,'Ideas, in motion.',640,445,font('ui',25,400),MUTED_LIGHT)
        draw_rule(img,486,486,794,486,(87,93,99),1,90)

    return img.convert('RGB')


def draw_loop_frame(t: float) -> Image.Image:
    # Exact 10-second periodic composition: all animated values are functions of phase only.
    t=t % 10.0
    phase=2*math.pi*t/10.0
    img=DARK_BG.copy().convert('RGBA')
    draw_periodic_bg_light(img,t,0.85)
    # Quiet orbit rings, not radial spokes; the moving point is the only bright cursor.
    cx,cy=640,360
    d=ImageDraw.Draw(img)
    d.ellipse((cx-360,cy-185,cx+360,cy+185),outline=(100,113,124,48),width=1)
    d.ellipse((cx-306,cy-143,cx+306,cy+143),outline=(87,99,110,34),width=1)
    # Two smooth ellipses with a trail of variable opacity; each has one 10s period.
    for track,(rx,ry,offset,color,width) in enumerate([(360,185,phase,WARM,2),(306,143,-phase+.6,COOL,1)]):
        span=1.20 if track==0 else .85
        pts=[]
        steps=36
        for i in range(steps+1):
            a=offset-span*(1-i/steps)
            pts.append((cx+rx*math.cos(a),cy+ry*math.sin(a)))
        for i in range(1,len(pts)):
            age=i/(len(pts)-1)
            col=color
            alpha=int((40+150*age)*(0.75+0.25*math.sin(phase+track)))
            d.line((pts[i-1],pts[i]),fill=(*col,alpha),width=width+1 if age>.8 else width)
    # Orbiting point: position, light breath and sound phase all close on exactly 10.0 s.
    px=cx+360*math.cos(phase); py=cy+185*math.sin(phase)
    draw_dot(img,(px,py),WARM_HI,4,255,35)
    # One counter-moving, quieter glass point.
    sx=cx+306*math.cos(-phase+.6); sy=cy+143*math.sin(-phase+.6)
    draw_dot(img,(sx,sy),COOL,2,175,22)
    draw_tracking(img,'KINETIC',138,110,font('ui',18,600),MUTED_LIGHT,spacing=2.4,alpha=225)
    draw_center(img,'Ideas,',640,278,font('display',92,600),IVORY)
    draw_center(img,'in motion.',640,388,font('ui',29,500),MUTED_LIGHT)
    d=ImageDraw.Draw(img)
    d.line((560,465,720,465),fill=(*WARM,155),width=1)
    return img.convert('RGB')


def encode_video(kind, out, start=0.0, duration=None, fps=FPS, ffmpeg=None):
    if duration is None:
        duration=DURATION if kind=='hero' else 10.0
    total=int(round(duration*fps))
    ffmpeg=ffmpeg or os.environ.get('FFMPEG_BIN') or shutil.which('ffmpeg')
    if not ffmpeg:
        candidate=os.path.expanduser('~/.cache/frameforge/bin/ffmpeg')
        if os.path.exists(candidate): ffmpeg=candidate
    if not ffmpeg: raise RuntimeError('ffmpeg not found; run python3 ops/bootstrap_media.py')
    os.makedirs(os.path.dirname(os.path.abspath(out)),exist_ok=True)
    cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-preset','slow','-crf','17','-profile:v','high','-pix_fmt','yuv420p','-r',str(fps),'-movflags','+faststart','-metadata','title=Kinetic — A thought becomes a world',out]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i in range(total):
            t=start+i/fps
            frame=draw_hero_frame(t) if kind=='hero' else draw_loop_frame(t)
            proc.stdin.write(frame.tobytes())
            if i % fps == 0: print(f'{kind}: rendered frame {i}/{total} at t={t:.3f}s',flush=True)
        proc.stdin.close()
        err=proc.stderr.read().decode('utf-8','replace')
        rc=proc.wait()
        if rc: raise RuntimeError(f'ffmpeg exit {rc}: {err[-1200:]}')
    except Exception:
        try: proc.stdin.close()
        except Exception: pass
        proc.kill(); proc.wait(); raise
    print(f'{kind}: wrote {out} ({total} frames; {duration:.3f}s at {fps} fps)',flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--kind',choices=['hero','loop'],default='hero')
    ap.add_argument('--out',required=True)
    ap.add_argument('--start',type=float,default=0.0)
    ap.add_argument('--duration',type=float,default=None)
    ap.add_argument('--fps',type=int,default=FPS)
    ap.add_argument('--ffmpeg',default=None)
    args=ap.parse_args()
    encode_video(args.kind,args.out,args.start,args.duration,args.fps,args.ffmpeg)

if __name__=='__main__': main()
