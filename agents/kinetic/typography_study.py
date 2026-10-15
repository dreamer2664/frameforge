"""Optical/phone-scale comparison of three licensed type directions."""
import os
from PIL import Image,ImageDraw,ImageFont,ImageFilter
BASE=os.path.dirname(os.path.abspath(__file__)); FD=os.path.join(BASE,'fonts')
OUT=os.path.join(BASE,'evidence','type-comparison.png')
W,H=1940,980; PW=620; GAP=20

def face(name,size,w=None,opsz=None):
 f=ImageFont.truetype(os.path.join(FD,name),size)
 if name=='Fraunces.ttf': f.set_variation_by_axes([opsz or min(144,size),w or 600,0,0])
 elif name=='PlayfairDisplay.ttf': f.set_variation_by_axes([w or 600])
 return f

def fitdraw(d,text,x,y,f,fill): d.text((x,y),text,font=f,fill=fill)
def line(d,coords,fill,w=1): d.line(coords,fill=fill,width=w)

def make_panel(kind):
 dark=kind!='Playfair Display'
 bg=(9,11,16) if kind!='Playfair Display' else (241,237,228)
 ink=(242,238,229) if dark else (34,40,49)
 muted=(172,183,191) if dark else (83,91,99)
 accent=(231,164,97) if kind!='Playfair Display' else (81,125,161)
 im=Image.new('RGB',(PW,760),bg); d=ImageDraw.Draw(im)
 d.text((42,34),kind.upper()+(' + INTER' if kind!='INTER' else ' ONLY'),font=face('Inter-SemiBold.ttf',18),fill=accent)
 line(d,(42,76,PW-42,76),(70,75,82) if dark else (183,182,174),1)
 if kind=='Fraunces':
  f1=face('Fraunces.ttf',76,580,opsz=76); f2=face('Fraunces.ttf',70,540,opsz=70)
  fitdraw(d,'A thought',42,125,f1,ink); fitdraw(d,'becomes a world.',42,207,f2,ink)
 elif kind=='Playfair Display':
  f1=face('PlayfairDisplay.ttf',76,600); f2=face('PlayfairDisplay.ttf',70,520)
  fitdraw(d,'A thought',42,125,f1,ink); fitdraw(d,'becomes a world.',42,207,f2,ink)
 else:
  f1=face('Inter-Bold.ttf',67); f2=face('Inter-SemiBold.ttf',50)
  fitdraw(d,'A THOUGHT',42,135,f1,ink); fitdraw(d,'BECOMES A WORLD.',42,222,f2,accent)
 line(d,(42,330,PW-42,330),accent,3)
 d.text((42,365),'Give it a shape, a rhythm, and room.',font=face('Inter-Regular.ttf',23),fill=muted)
 d.text((42,407),'Aa  AV  fi  Æ  —  0123456789',font=face('Inter-Medium.ttf',23),fill=ink)
 # tracking label / monospaced-style spacing via separate characters
 label='02 / TYPE, PATH, LIGHT'
 f=face('Inter-Medium.ttf',19)
 x=42
 for ch in label:
  d.text((x,467),ch,font=f,fill=accent); x+=f.getlength(ch)+1.2
 # phone-size viewing window at 1/3 of an HD output: scale a selected composition to 640x360.
 # This is deliberately an actual downsample, not an assertion about a specific device.
 crop=im.crop((0,110,PW,470)).resize((320,180),Image.Resampling.LANCZOS)
 # border and label
 d.rectangle((41,510,383,716),outline=accent,width=1)
 d.text((42,485),'TYPE SAMPLE / HALF-SCALE CHECK',font=face('Inter-Medium.ttf',15),fill=muted)
 im.paste(crop,(52,523))
 # mark small-glyph contrast test
 d.text((410,530),'READ AT A GLANCE',font=face('Inter-SemiBold.ttf',17),fill=accent)
 d.text((410,568),'• glyphs render',font=face('Inter-Regular.ttf',17),fill=muted)
 d.text((410,598),'• line break holds',font=face('Inter-Regular.ttf',17),fill=muted)
 d.text((410,628),'• display stays clear',font=face('Inter-Regular.ttf',17),fill=muted)
 d.text((410,658),'• UI stays secondary',font=face('Inter-Regular.ttf',17),fill=muted)
 return im

def main():
 canvas=Image.new('RGB',(1940,820),(5,6,9))
 d=ImageDraw.Draw(canvas)
 d.text((30,10),'KINETIC  /  TYPE CANDIDATES  /  SAME COPY, THREE HIERARCHIES',font=face('Inter-SemiBold.ttf',20),fill=(224,220,211))
 for i,k in enumerate(['Fraunces','Playfair Display','INTER']):
  p=make_panel(k); canvas.paste(p,(20+i*(PW+20),42))
 os.makedirs(os.path.dirname(OUT),exist_ok=True); canvas.save(OUT)
 print(OUT,canvas.size)
if __name__=='__main__':main()
