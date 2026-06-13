import math, os, json, sys
from PIL import Image, ImageDraw, ImageFont
W,H=720,1280; FPS=30
GRN=(34,181,115); WHT=(255,255,255)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(s,b=True): return ImageFont.truetype(FB if b else FR,s)
def eio(t): return 3*t*t-2*t*t*t
def cl(x,a=0.0,b=1.0): return max(a,min(b,x))
PX0,PY0,PX1,PY1=60,80,660,1240
SX0,SY0,SX1,SY1=80,100,640,1220
SW,SH=SX1-SX0,SY1-SY0
SC=560/430.0

def make_base(label):
    im=Image.new("RGB",(W,H))
    d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=(int(10+8*t),int(18+12*t),int(38+18*t)))
    s=4
    big=Image.new("RGBA",(W*s,H*s),(0,0,0,0)); bd=ImageDraw.Draw(big)
    bd.rounded_rectangle([PX0*s,PY0*s,PX1*s,PY1*s],radius=64*s,fill=(16,22,38,255),outline=(70,86,120,255),width=3*s)
    bd.rounded_rectangle([SX0*s,SY0*s,SX1*s,SY1*s],radius=36*s,fill=(255,255,255,255))
    frame=big.resize((W,H),Image.LANCZOS)
    im.paste(frame,(0,0),frame)
    d=ImageDraw.Draw(im); f=font(26)
    tw=d.textlength(label,font=f); cw=tw+44
    d.rounded_rectangle([(W-cw)/2,24,(W+cw)/2,68],radius=14,fill=(13,26,56))
    d.text((W/2,46),label,font=f,fill=(238,200,120),anchor="mm")
    mask=Image.new("L",(SW,SH),0); md=ImageDraw.Draw(mask)
    md.rounded_rectangle([0,0,SW-1,SH-1],radius=34,fill=255)
    return im,mask

# filled form: 654 css tall -> 560 wide image
form=Image.open("/tmp/hform_filled.png").convert("RGB")
form=form.resize((SW,int(form.height*SW/form.width)),Image.LANCZOS)  # 560 x ~852
FOFF=(SH-form.height)//2 if form.height<SH else 0
meta=json.load(open("/tmp/hfilled_meta.json"))
rx,ry,rw,rh=meta["f_run"]
def run_rect():
    return [SX0+rx*SC, SY0+FOFF+ry*SC, SX0+(rx+rw)*SC, SY0+FOFF+(ry+rh)*SC]

def form_screen(base,mask):
    scr=Image.new("RGB",(SW,SH),(255,255,255))
    scr.paste(form,(0,FOFF))
    base.paste(scr,(SX0,SY0),mask)

def render1(out):  # filled form reveal w/ highlight sweep, 6s
    os.makedirs(out,exist_ok=True); dur=6.0; N=int(dur*FPS)
    base0,mask=make_base("Steps 1-2 · Plan your tour")
    fields_y=[ry*SC+SY0+FOFF for ry in [80,210,300,300,380,380,470]]  # approx css rows*SC
    for f in range(N):
        fp=f"{out}/{f:04d}.jpg"
        if os.path.exists(fp): continue
        im=base0.copy(); form_screen(im,mask)
        t=f/FPS
        # green highlight bar sweeping down the form to imply completion
        p=cl(t/4.5)
        yy=SY0+FOFF+ (form.height)*eio(p)
        if 0.05<p<0.98:
            ov=Image.new("RGBA",im.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
            od.rectangle([SX0,yy-3,SX1,yy+3],fill=(34,181,115,120))
            im.paste(ov,(0,0),ov)
        im.save(fp,quality=90)
    return dur

def render2(out):  # run press + toast, 3.2s
    os.makedirs(out,exist_ok=True); dur=3.2; N=int(dur*FPS)
    base0,mask=make_base("Step 3 · Run — holds 5T")
    r=run_rect(); bx=(r[0]+r[2])/2; by=(r[1]+r[3])/2
    for f in range(N):
        fp=f"{out}/{f:04d}.jpg"
        if os.path.exists(fp): continue
        t=f/FPS; im=base0.copy(); form_screen(im,mask); d=ImageDraw.Draw(im)
        press=cl((t-1.0)/0.18)
        if 0<press<=1:
            ov=Image.new("RGBA",im.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
            od.rounded_rectangle(r,radius=12,fill=(0,0,0,int(70*(1-abs(press*2-1)))))
            im.paste(ov,(0,0),ov)
        rp=cl((t-1.05)/0.5)
        if 0<rp<1:
            ov=Image.new("RGBA",im.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
            rad=14+90*rp; od.ellipse([bx-rad,by-rad,bx+rad,by+rad],outline=(255,255,255,int(200*(1-rp))),width=6)
            im.paste(ov,(0,0),ov)
        tp=cl((t-1.5)/0.3)
        if tp>0:
            d=ImageDraw.Draw(im); cw=330; cy=r[1]-46+int(14*(1-eio(tp)))
            d.rounded_rectangle([(W-cw)/2,cy-22,(W+cw)/2,cy+22],radius=14,fill=GRN)
            d.text((W/2,cy),"5T reserved · planning…",font=font(19),fill=WHT,anchor="mm")
        im.save(fp,quality=90)
    return dur

def render3(out):  # report scroll, 12s
    os.makedirs(out,exist_ok=True); dur=12.0; N=int(dur*FPS)
    rep=Image.open("/tmp/hreport_full.png").convert("RGB")
    rep=rep.resize((SW,int(rep.height*SW/rep.width)),Image.LANCZOS)
    maxs=max(1,rep.height-SH)
    base0,mask=make_base("Step 4 · Your Tour Plan")
    for f in range(N):
        fp=f"{out}/{f:04d}.jpg"
        if os.path.exists(fp): continue
        t=f/FPS; p=cl((t-0.8)/(dur-1.8)); sy=int(maxs*eio(p))
        im=base0.copy()
        crop=rep.crop((0,sy,SW,sy+SH)); im.paste(crop,(SX0,SY0),mask)
        d=ImageDraw.Draw(im)
        bh=max(40,int(SH*SH/rep.height)); bt=SY0+int((SH-bh)*sy/maxs)
        d.rounded_rectangle([SX1-8,bt,SX1-3,bt+bh],radius=3,fill=(120,140,180))
        im.save(fp,quality=90)
    return dur

w=sys.argv[1] if len(sys.argv)>1 else "all"
if w in ("1","all"): render1("/tmp/hi1")
if w in ("2","all"): render2("/tmp/hi2")
if w in ("3","all"): render3("/tmp/hi3")
print("HINSERTS DONE",w)
