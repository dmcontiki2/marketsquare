import math,os,json
from PIL import Image,ImageDraw,ImageFont
W,H,FPS=720,1280,30; DUR=5.5; N=int(DUR*FPS)
GRN=(34,181,115); WHT=(255,255,255); ACC=(91,156,245)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(s): return ImageFont.truetype(FB,s)
def eio(t): return 3*t*t-2*t*t*t
def cl(x,a=0.,b=1.): return max(a,min(b,x))
PX0,PY0,PX1,PY1=60,80,660,1240
SX0,SY0,SX1,SY1=80,100,640,1220
SW,SH=SX1-SX0,SY1-SY0
SC=560/430.0
def make_base(label):
    im=Image.new("RGB",(W,H)); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=(int(10+8*t),int(18+12*t),int(38+18*t)))
    s=4; big=Image.new("RGBA",(W*s,H*s),(0,0,0,0)); bd=ImageDraw.Draw(big)
    bd.rounded_rectangle([PX0*s,PY0*s,PX1*s,PY1*s],radius=64*s,fill=(16,22,38,255),outline=(70,86,120,255),width=3*s)
    bd.rounded_rectangle([SX0*s,SY0*s,SX1*s,SY1*s],radius=36*s,fill=(12,23,48,255))
    fr=big.resize((W,H),Image.LANCZOS); im.paste(fr,(0,0),fr)
    d=ImageDraw.Draw(im); f=font(26); tw=d.textlength(label,font=f); cw=tw+44
    d.rounded_rectangle([(W-cw)/2,24,(W+cw)/2,68],radius=14,fill=(13,26,56))
    d.text((W/2,46),label,font=f,fill=(238,200,120),anchor="mm")
    mask=Image.new("L",(SW,SH),0); md=ImageDraw.Draw(mask); md.rounded_rectangle([0,0,SW-1,SH-1],radius=34,fill=255)
    return im,mask
scr_full=Image.open("/tmp/ractions.png").convert("RGB")
scr=scr_full.resize((SW,int(scr_full.height*SW/scr_full.width)),Image.LANCZOS)
FOFF=(SH-scr.height)//2 if scr.height<SH else 0
rects=json.load(open("/tmp/ractions_rects.json"))
def rr(k):
    x,y,w,h=rects[k]; return [SX0+x*SC,SY0+FOFF+y*SC,SX0+(x+w)*SC,SY0+FOFF+(y+h)*SC]
os.makedirs("/tmp/rins",exist_ok=True)
base,mask=make_base("Step 8 · Save or forward")
def draw_screen(im):
    s=Image.new("RGB",(SW,SH),(12,23,48)); s.paste(scr,(0,FOFF)); im.paste(s,(SX0,SY0),mask)
def tap(d,im,r,t,t0):
    p=cl((t-t0)/0.45)
    if 0<p<1:
        ov=Image.new("RGBA",im.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
        od.rounded_rectangle(r,radius=12,outline=(120,200,255,int(230*(1-p))),width=4)
        bx,by=(r[0]+r[2])/2,(r[1]+r[3])/2; rad=20+70*p
        od.ellipse([bx-rad,by-rad,bx+rad,by+rad],outline=(150,210,255,int(180*(1-p))),width=5)
        im.paste(ov,(0,0),ov)
for f in range(N):
    t=f/FPS; im=base.copy(); draw_screen(im); d=ImageDraw.Draw(im)
    tap(d,im,rr("b_save"),t,1.6)
    tap(d,im,rr("b_fwd"),t,2.9)
    a=cl((t-0.3)/0.5)
    if a>0:
        cw=470; cy=SY1-66
        ov=Image.new("RGBA",im.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
        od.rounded_rectangle([(W-cw)/2,cy-26,(W+cw)/2,cy+26],radius=15,fill=(16,40,48,int(235*a)))
        im.paste(ov,(0,0),ov)
        d.text((W/2,cy),"Save it, or forward it — anytime",font=font(22),fill=(180,235,210),anchor="mm")
    im.save(f"/tmp/rins/{f:04d}.jpg",quality=90)
print("rins frames",N)
