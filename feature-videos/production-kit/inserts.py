import math, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=720,1280; FPS=30
NAVY=(14,31,68); ACC=(91,156,245); YEL=(238,179,59); GRN=(34,181,115); WHT=(255,255,255)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(s,b=True): return ImageFont.truetype(FB if b else FR,s)
def easeio(t): return 3*t*t-2*t*t*t
def cl(x,a=0.0,b=1.0): return max(a,min(b,x))

# screen geometry
PX0,PY0,PX1,PY1=60,80,660,1240          # phone body
SX0,SY0,SX1,SY1=80,100,640,1220         # screen (560x1120)
SW,SH=SX1-SX0,SY1-SY0
SC=2*0.6512  # css px -> final px (form rendered @2x, scaled 860->560)

def make_base(step_label):
    im=Image.new("RGB",(W,H))
    d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H
        d.line([(0,y),(W,y)],fill=(int(10+8*t),int(18+12*t),int(38+18*t)))
    s=4
    big=Image.new("RGBA",(W*s,H*s),(0,0,0,0))
    bd=ImageDraw.Draw(big)
    bd.rounded_rectangle([PX0*s,PY0*s,PX1*s,PY1*s],radius=64*s,fill=(16,22,38,255),outline=(70,86,120,255),width=3*s)
    bd.rounded_rectangle([SX0*s,SY0*s,SX1*s,SY1*s],radius=36*s,fill=(255,255,255,255))
    frame=big.resize((W,H),Image.LANCZOS)
    im.paste(frame,(0,0),frame)
    d=ImageDraw.Draw(im)
    f=font(26)
    tw=d.textlength(step_label,font=f)
    chip_w=tw+44
    d.rounded_rectangle([(W-chip_w)/2,24,(W+chip_w)/2,68],radius=14,fill=(13,26,56))
    d.text((W/2,46),step_label,font=f,fill=(238,200,120),anchor="mm")
    mask=Image.new("L",(SW,SH),0)
    md=ImageDraw.Draw(mask)
    md.rounded_rectangle([0,0,SW-1,SH-1],radius=34,fill=255)
    return im,mask

def paste_screen(base,mask,ui,sy=0):
    crop=ui.crop((0,sy,SW,sy+SH))
    base.paste(crop,(SX0,SY0),mask)

form=Image.open("/tmp/form_full.png").resize((560,int(1344*560/860)),Image.LANCZOS)  # 560x875
FOFF=(SH-form.height)//2  # vertical offset inside screen
rects=json.load(open("/tmp/form_rects.json"))
def fr(k):
    x,y,w,h=rects[k]
    return [SX0+x*SC, SY0+FOFF+y*SC, SX0+(x+w)*SC, SY0+FOFF+(y+h)*SC]

def form_screen(base,mask):
    scr=Image.new("RGB",(SW,SH),(255,255,255))
    scr.paste(form,(0,FOFF))
    base.paste(scr,(SX0,SY0),mask)

FILLS=[("f_items","MtG Veteran Bodyguard (Revised)",1.0,4.0),
       ("f_price","R350",4.6,5.7),
       ("f_city","Pretoria",6.2,7.4),
       ("f_cur","ZAR",8.0,8.9)]
PHOTO_T=0.4

def draw_fill(d,key,txt,active):
    r=fr(key)
    pad=12*SC
    d.rounded_rectangle([r[0]+3,r[1]+3,r[2]-3,r[3]-3],radius=9,fill=NAVY)
    ty=r[1]+(14 if key!="f_items" else 11)*SC
    d.text((r[0]+pad,ty),txt,font=font(16,False),fill=(223,231,245),anchor="lt" if key=="f_items" else "lm" if False else "lt")
    if active:
        d.rounded_rectangle([r[0]-1,r[1]-1,r[2]+1,r[3]+1],radius=11,outline=ACC,width=2)
    return d.textlength(txt,font=font(16,False))

ticks=[]
def render_insert1(out):
    os.makedirs(out,exist_ok=True)
    dur=12.0; N=int(dur*FPS)
    base0,mask=make_base("Steps 2-5 · Fill in the details")
    for f in range(N):
        fp=f"{out}/{f:04d}.jpg"
        if os.path.exists(fp): continue
        t=f/FPS
        im=base0.copy()
        form_screen(im,mask)
        d=ImageDraw.Draw(im)
        if t>=PHOTO_T:
            r=fr("f_photos_t") if "f_photos_t" in rects else None
            if r:
                d.rectangle([r[0]-2,r[1]-2,r[2]+60,r[3]+4],fill=NAVY)
                d.text((r[0],(r[1]+r[3])/2),"card_photo_1.jpg",font=font(13,False),fill=(223,231,245),anchor="lm")
        for key,txt,t0,t1 in FILLS:
            if t<t0: continue
            k=int(len(txt)*cl((t-t0)/(t1-t0)))
            shown=txt[:k]
            active = t0<=t<t1+0.45
            tw=draw_fill(d,key,shown,active)
            if active and (t%0.66)<0.4 and k<len(txt) or (active and k==len(txt) and (t%0.66)<0.33):
                r=fr(key); pad=12*SC
                cx=r[0]+pad+tw+2; cy=r[1]+11*SC
                d.rectangle([cx,cy,cx+2,cy+20],fill=ACC)
            if f>0 and k>int(len(txt)*cl((t-1/FPS-t0)/(t1-t0))):
                ticks.append(round(t,3))
        im.save(fp,quality=90)
    return dur

def render_insert2(out):
    os.makedirs(out,exist_ok=True)
    dur=3.2; N=int(dur*FPS)
    base0,mask=make_base("Step 6 · Run — holds 5T")
    for f in range(N):
        fp=f"{out}/{f:04d}.jpg"
        if os.path.exists(fp): continue
        t=f/FPS
        im=base0.copy()
        form_screen(im,mask)
        d=ImageDraw.Draw(im)
        for key,txt,_,_ in FILLS: draw_fill(d,key,txt,False)
        rp2=fr("f_photos_t")
        d.rectangle([rp2[0]-2,rp2[1]-2,rp2[2]+70,rp2[3]+4],fill=(14,31,68))
        d.text((rp2[0],(rp2[1]+rp2[3])/2),"card_photo_1.jpg",font=font(13,False),fill=(223,231,245),anchor="lm")
        r=fr("f_run"); bx=(r[0]+r[2])/2; by=(r[1]+r[3])/2
        press=cl((t-1.0)/0.18)
        if 0<press<=1:
            ov=Image.new("RGBA",im.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
            od.rounded_rectangle(r,radius=12,fill=(0,0,0,int(70*(1-abs(press*2-1)))))
            im.paste(ov,(0,0),ov)
        rp=cl((t-1.05)/0.5)
        if 0<rp<1:
            ov=Image.new("RGBA",im.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
            rad=14+90*rp
            od.ellipse([bx-rad,by-rad,bx+rad,by+rad],outline=(255,255,255,int(200*(1-rp))),width=6)
            im.paste(ov,(0,0),ov)
        tp=cl((t-1.5)/0.3)
        if tp>0:
            d=ImageDraw.Draw(im)
            cw=320; cy=r[1]-46+int(14*(1-easeio(tp)))
            d.rounded_rectangle([(W-cw)/2,cy-22,(W+cw)/2,cy+22],radius=14,fill=GRN)
            d.text((W/2,cy),"5T reserved · running…",font=font(19),fill=WHT,anchor="mm")
        im.save(fp,quality=90)
    return dur

def render_insert3(out):
    os.makedirs(out,exist_ok=True)
    dur=10.0; N=int(dur*FPS)
    rep=Image.open("/tmp/report_full.png")
    rep=rep.resize((SW,int(rep.height*SW/rep.width)),Image.LANCZOS)
    maxs=rep.height-SH
    base0,mask=make_base("Step 7 · Your Market Report")
    for f in range(N):
        fp=f"{out}/{f:04d}.jpg"
        if os.path.exists(fp): continue
        t=f/FPS
        p=cl((t-0.8)/(dur-1.6))
        sy=int(maxs*easeio(p))
        im=base0.copy()
        paste_screen(im,mask,rep,sy)
        d=ImageDraw.Draw(im)
        bh=max(40,int(SH*SH/rep.height))
        bt=SY0+int((SH-bh)*sy/maxs)
        d.rounded_rectangle([SX1-8,bt,SX1-3,bt+bh],radius=3,fill=(120,140,180))
        im.save(fp,quality=90)
    return dur

import sys
which=sys.argv[1] if len(sys.argv)>1 else "all"
if which in ("1","all"): render_insert1("/tmp/ins1")
if which in ("2","all"): render_insert2("/tmp/ins2")
if which in ("3","all"): render_insert3("/tmp/ins3")
json.dump(ticks,open("/tmp/ticks.json","w"))
print("INSERTS DONE",which,"ticks",len(ticks))
