import math, os
from PIL import Image, ImageDraw, ImageFont
W,H=720,1280; FPS=30
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(s,b=True): return ImageFont.truetype(FB if b else FR,s)
def eio(t): return 3*t*t-2*t*t*t
def cl(x,a=0.,b=1.): return max(a,min(b,x))
# phone frame
PX0,PY0,PX1,PY1=60,80,660,1240
SX0,SY0,SX1,SY1=80,100,640,1220
SW,SH=SX1-SX0,SY1-SY0
def make_base(label):
    im=Image.new("RGB",(W,H)); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=(int(10+8*t),int(18+12*t),int(38+18*t)))
    s=4; big=Image.new("RGBA",(W*s,H*s),(0,0,0,0)); bd=ImageDraw.Draw(big)
    bd.rounded_rectangle([PX0*s,PY0*s,PX1*s,PY1*s],radius=64*s,fill=(16,22,38,255),outline=(70,86,120,255),width=3*s)
    bd.rounded_rectangle([SX0*s,SY0*s,SX1*s,SY1*s],radius=36*s,fill=(13,32,40,255))
    frame=big.resize((W,H),Image.LANCZOS); im.paste(frame,(0,0),frame)
    d=ImageDraw.Draw(im); f=font(26); tw=d.textlength(label,font=f); cw=tw+44
    d.rounded_rectangle([(W-cw)/2,24,(W+cw)/2,68],radius=14,fill=(13,26,56))
    d.text((W/2,46),label,font=f,fill=(238,200,120),anchor="mm")
    return im
# route stops in screen coords (stylised SA: CT bottom-left, Kruger top-right)
STOPS=[("Cape Town",150,1080,False),("Colesberg",330,860,False),
       ("Dullstroom",470,560,False),("Graskop",545,430,True),
       ("Kruger",600,300,False)]
def catmull(pts,n=24):
    out=[]
    P=[pts[0]]+pts+[pts[-1]]
    for i in range(1,len(P)-2):
        p0,p1,p2,p3=P[i-1],P[i],P[i+1],P[i+2]
        for j in range(n):
            t=j/n
            x=0.5*((2*p1[0])+(-p0[0]+p2[0])*t+(2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t*t+(-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t**3)
            y=0.5*((2*p1[1])+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t*t+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t**3)
            out.append((x,y))
    out.append(pts[-1]); return out
PATH=catmull([(x,y) for _,x,y,_ in STOPS])

def render(out):
    os.makedirs(out,exist_ok=True); dur=6.5; N=int(dur*FPS)
    base=make_base("Your route, mapped")
    # faint grid inside screen
    g=base.copy(); gd=ImageDraw.Draw(g)
    for gx in range(SX0,SX1,46): gd.line([(gx,SY0),(gx,SY1)],fill=(22,52,62))
    for gy in range(SY0,SY1,46): gd.line([(SX0,gy),(SX1,gy)],fill=(22,52,62))
    base=Image.blend(base,g,0.5)
    for f in range(N):
        fp=f"{out}/{f:04d}.jpg"
        if os.path.exists(fp): continue
        t=f/FPS; im=base.copy(); d=ImageDraw.Draw(im)
        p=cl((t-0.5)/4.0); k=int(len(PATH)*eio(p))
        if k>=2:
            d.line(PATH[:k],fill=(91,200,160),width=6,joint="curve")
        # head dot
        if 1<=k<len(PATH):
            hx,hy=PATH[k-1]; d.ellipse([hx-8,hy-8,hx+8,hy+8],fill=(180,255,220))
        for i,(nm,x,y,way) in enumerate(STOPS):
            reach=p*len(STOPS)
            if reach>=i:
                col=(238,179,59) if way else (255,255,255)
                d.ellipse([x-9,y-9,x+9,y+9],fill=col,outline=(13,32,40),width=3)
                lab=nm+(" • waypoint" if way else "")
                anc="lm"; tx=x+16
                if x>460: anc="rm"; tx=x-16
                d.text((tx,y),lab,font=font(20),fill=(225,236,250),anchor=anc)
        # title strip bottom
        if t>4.2:
            a=cl((t-4.2)/0.5)
            d.rounded_rectangle([SX0+20,SY1-90,SX1-20,SY1-30],radius=14,fill=(16,40,48))
            d.text((W/2,SY1-60),"Cape Town → Kruger · 7 days · R28,420",font=font(19),fill=(180,235,210),anchor="mm")
        im.save(fp,quality=90)
    return dur
render("/tmp/hmap")
print("MAP DONE")
