"""Three autonomous art-direction studies; never sent as a creative poll."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
BASE=os.path.dirname(os.path.abspath(__file__))
FD=os.path.join(BASE,'fonts')
OUT=os.path.join(BASE,'evidence','concept-boards.png')
W,H=900,650

def ft(name,size,weight=None):
    p=os.path.join(FD,name)
    f=ImageFont.truetype(p,size)
    if weight is not None and name=='Fraunces.ttf':
        f.set_variation_by_axes([min(144,max(9,size)),weight,0,0])
    if weight is not None and name=='PlayfairDisplay.ttf':
        f.set_variation_by_axes([weight])
    return f

def centered(draw,text,xy,font,fill):
    x,y=xy
    box=draw.textbbox((0,0),text,font=font)
    draw.text((x-(box[2]-box[0])/2,y-(box[3]-box[1])/2-box[1]),text,font=font,fill=fill)

def glow_line(img,pts,color=(232,164,97),width=3):
    g=Image.new('RGBA',img.size,(0,0,0,0)); gd=ImageDraw.Draw(g)
    gd.line(pts,fill=(*color,80),width=width+14,joint='curve')
    g=g.filter(ImageFilter.GaussianBlur(13)); img.alpha_composite(g)
    d=ImageDraw.Draw(img); d.line(pts,fill=(*color,255),width=width,joint='curve')

def panel1():
    im=Image.new('RGBA',(W,H),(9,11,16,255)); d=ImageDraw.Draw(im)
    # restrained amber pool
    g=Image.new('RGBA',im.size,(0,0,0,0)); gd=ImageDraw.Draw(g)
    gd.ellipse((30,370,460,800),fill=(215,126,62,32)); g=g.filter(ImageFilter.GaussianBlur(70)); im.alpha_composite(g)
    d=ImageDraw.Draw(im)
    d.text((70,48),'01  /  SINGLE POINT → LIVING WORLD',font=ft('Inter-Medium.ttf',22),fill=(230,163,97))
    d.line((70,88,830,88),fill=(66,63,62),width=1)
    d.text((70,155),'A thought',font=ft('Fraunces.ttf',94,600),fill=(243,238,229))
    d.text((70,270),'becomes a world.',font=ft('Fraunces.ttf',78,520),fill=(243,238,229))
    glow_line(im,[(80,410),(220,410),(330,376),(430,414),(610,414),(800,340)],(231,164,97),3)
    d=ImageDraw.Draw(im)
    d.ellipse((789,329,811,351),fill=(255,224,182))
    d.text((72,500),'Fraunces  +  Inter  /  ember, ink, cool glass',font=ft('Inter-Medium.ttf',23),fill=(177,185,193))
    # quiet corner mark
    d.line((760,560,760,610),fill=(231,164,97),width=3); d.line((760,585,792,560),fill=(231,164,97),width=3); d.line((760,585,795,612),fill=(231,164,97),width=3)
    d.text((70,596),'A line carries the idea from word to world.',font=ft('Inter-Regular.ttf',21),fill=(201,200,194))
    return im.convert('RGB')

def panel2():
    im=Image.new('RGB',(W,H),(241,237,228)); d=ImageDraw.Draw(im)
    d.text((70,48),'02  /  PAPER ENGINE',font=ft('Inter-Medium.ttf',22),fill=(64,91,121))
    d.line((70,88,830,88),fill=(176,177,170),width=1)
    # modular grid, blue rules
    d.rectangle((70,143,830,487),outline=(53,68,83),width=1)
    d.line((100,180,800,180),fill=(72,108,142),width=2)
    d.text((106,207),'Make room',font=ft('PlayfairDisplay.ttf',91,600),fill=(32,39,49))
    d.text((106,306),'for what moves.',font=ft('PlayfairDisplay.ttf',74,520),fill=(32,39,49))
    d.rectangle((106,411,383,418),fill=(76,123,160))
    d.text((70,520),'Playfair Display  +  Inter  /  paper, ink, mineral blue',font=ft('Inter-Medium.ttf',22),fill=(55,65,77))
    d.text((70,588),'Modular, editorial, composed like a page.',font=ft('Inter-Regular.ttf',21),fill=(80,87,94))
    return im

def panel3():
    im=Image.new('RGB',(W,H),(15,17,23)); d=ImageDraw.Draw(im)
    d.text((70,48),'03  /  SIGNAL / ECHO',font=ft('Inter-Medium.ttf',22),fill=(153,218,205))
    d.line((70,88,830,88),fill=(64,69,78),width=1)
    # stepped echo bars
    for i in range(7):
        x=70+i*100
        d.rectangle((x,148,x+2,470),fill=(40+i*3,52+i*2,62+i*3))
    d.text((74,178),'MOVE',font=ft('Inter-Bold.ttf',104),fill=(245,241,231))
    d.text((104,285),'TO',font=ft('Inter-Bold.ttf',78),fill=(129,210,195))
    d.text((72,360),'MEAN.',font=ft('Inter-Bold.ttf',96),fill=(245,241,231))
    for i,c in enumerate([(129,210,195),(241,162,112),(198,178,255)]):
        x=600+i*58
        d.ellipse((x,226,x+24,250),fill=c)
    d.text((70,520),'Inter  /  hard cut, fast pulse, electric mint',font=ft('Inter-Medium.ttf',22),fill=(181,191,198))
    d.text((70,588),'High energy; risks becoming generic tech shorthand.',font=ft('Inter-Regular.ttf',21),fill=(181,191,198))
    return im

def main():
    canvas=Image.new('RGB',(3*W+80, H+90),(5,6,9))
    for i,im in enumerate([panel1(),panel2(),panel3()]):
        canvas.paste(im,(20+i*(W+20),45))
    d=ImageDraw.Draw(canvas)
    d.text((24,14),'KINETIC  /  PRIVATE ART-DIRECTION STUDY   •   THREE DIFFERENT VISUAL GRAMMARS',font=ft('Inter-SemiBold.ttf',20),fill=(222,219,211))
    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    canvas.save(OUT)
    print(OUT, canvas.size)
if __name__=='__main__': main()
