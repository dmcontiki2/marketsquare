# TrustSquare poster set — 7×A1 category + 1×A1 features + 5×A2 reports
import json
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader, simpleSplit

NAVY=HexColor('#111827'); ACCENT=HexColor('#1E3A5F'); ICE=HexColor('#EEF2F8')
GOLD=HexColor('#C9962E'); GOLDBG=HexColor('#FEF3C7'); RUBY=HexColor('#C0273C')
MUTED=HexColor('#5B6470'); WHITE=HexColor('#FFFFFF'); LINEC=HexColor('#E2E5EA')
DARKSUB=HexColor('#C7D2E3'); BODY=HexColor('#374151'); GREEN=HexColor('#065F46')
BLEED=3*mm
A1W,A1H=594*mm,841*mm; A2W,A2H=420*mm,594*mm
SAMPLE_RUN_MODEL = "claude-sonnet-4-6"  # cost-ok: marketing copy names the model that produced the published sample reports; not a runtime call site
P='/tmp/pitch/photos/'; OUT='/tmp/pitch/out/'
import os; os.makedirs(OUT,exist_ok=True)
import qrcode
q=qrcode.QRCode(border=2,box_size=24); q.add_data('https://trustsquare.co'); q.make()
q.make_image(fill_color='#111827',back_color='white').save('/tmp/pitch/assets/qr_hi.png')
QR=ImageReader('/tmp/pitch/assets/qr_hi.png')

def page(c,W,H):
    c.setFillColor(WHITE); c.rect(-BLEED,-BLEED,W+2*BLEED,H+2*BLEED,fill=1,stroke=0)
def trim(c,W,H):
    c.setStrokeColor(HexColor('#999999')); c.setLineWidth(0.3)
    L=4*mm
    for x,y,dx,dy in ((0,0,-1,-1),(W,0,1,-1),(0,H,-1,1),(W,H,1,1)):
        c.line(x+dx*1*mm,y,x+dx*(1*mm+L),y); c.line(x,y+dy*1*mm,x,y+dy*(1*mm+L))
def diamond(c,cx,cy,r,col=RUBY):
    c.setFillColor(col); p=c.beginPath()
    p.moveTo(cx,cy+r); p.lineTo(cx+r,cy); p.lineTo(cx,cy-r); p.lineTo(cx-r,cy); p.close()
    c.drawPath(p,fill=1,stroke=0)
def wordmark(c,x,y,size):
    c.setFont('Helvetica-Bold',size); c.setFillColor(WHITE); c.drawString(x,y,'TRUST')
    w=c.stringWidth('TRUST','Helvetica-Bold',size); c.setFillColor(GOLD); c.drawString(x+w,y,'SQUARE')
def chip(c,x,y,h,text,fg,bg,size=None):
    size=size or h*0.45
    c.setFont('Helvetica-Bold',size); w=c.stringWidth(text,'Helvetica-Bold',size)+h*0.9
    c.setFillColor(bg); c.roundRect(x,y,w,h,h/2,fill=1,stroke=0)
    c.setFillColor(fg); c.drawCentredString(x+w/2,y+h*0.30,text)
    return w
def trust_chip(c,x,y,h,score):
    if score>=90: return chip(c,x,y,h,f'★ TRUST {score} · HIGHLY TRUSTED',HexColor('#92400E'),GOLDBG)
    if score>=70: return chip(c,x,y,h,f'★ TRUST {score} · TRUSTED',GREEN,HexColor('#D1FAE5'))
    if score>=40: return chip(c,x,y,h,f'★ TRUST {score} · ESTABLISHED',HexColor('#1D4ED8'),HexColor('#DBEAFE'))
    return chip(c,x,y,h,f'★ TRUST {score} · NEW',MUTED,ICE)
def para(c,x,y,w,lines_text,font,size,leading,col,max_lines=99):
    c.setFont(font,size); c.setFillColor(col)
    n=0
    for raw in lines_text.split('\n'):
        for ln in (simpleSplit(raw,font,size,w) or ['']):
            if n>=max_lines: return y
            c.drawString(x,y,ln); y-=leading; n+=1
    return y
def footer(c,W,draft_y=10*mm):
    c.setFillColor(RUBY); c.setFont('Helvetica-Oblique',10)
    c.drawString(14*mm,draft_y,'INTERNAL DRAFT — do not circulate until the provisional patent is filed')
    c.setFillColor(MUTED); c.setFont('Helvetica',10)
    c.drawRightString(W-14*mm,draft_y,'trustsquare.co')

CAT_ACCENTS={'Property':HexColor('#1E3A5F'),'Collectors':HexColor('#5B21B6'),'Adventures':HexColor('#0F6E56'),
 'Cars':HexColor('#C0273C'),'Tutors':HexColor('#B45309'),'Services':HexColor('#065F46'),'Local Market':HexColor('#1D4ED8')}
CAT_PROMISES={'Property':'Serious buyers pay to meet you. Your listing pauses while you engage — one buyer at a time.',
 'Collectors':'Honest, evidence-based condition language. Buyers with real intent, introduced for $2.',
 'Adventures':'Experiences and stays, sold beside 332 World Heritage sites of native content.',
 'Cars':'No middleman fees. The buyer pays to be introduced — your price stays your price.',
 'Tutors':'Anonymous until accepted. No spam — students who pay to meet their tutor.',
 'Services':'Qualified callouts, not cold leads. You accept who you talk to.',
 'Local Market':'Every seller starts trusted. Verified locals, introduced for $2.'}

def category_poster(spec):
    W,H=A1W,A1H
    c=canvas.Canvas(OUT+spec['file'],pagesize=(W+2*BLEED,H+2*BLEED))
    c.translate(BLEED,BLEED); page(c,W,H)
    acc=CAT_ACCENTS[spec['cat']]
    # header band
    c.setFillColor(NAVY); c.rect(-BLEED,H-205*mm,W+2*BLEED,205*mm+BLEED,fill=1,stroke=0)
    diamond(c,22*mm,H-22*mm,5*mm); wordmark(c,32*mm,H-25*mm,30)
    c.setFillColor(acc); c.rect(-BLEED,H-205*mm,W+2*BLEED,5*mm,fill=1,stroke=0)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold',24)
    c.drawString(22*mm,H-52*mm,spec['cat'].upper()+'  ·  LAUNCH CATEGORY')
    c.setFillColor(WHITE); c.setFont('Helvetica-Bold',110 if len(spec['cat'])<10 else 88)
    c.drawString(20*mm,H-100*mm,spec['cat'])
    para(c,22*mm,H-125*mm,W-44*mm,CAT_PROMISES[spec['cat']],'Helvetica',26,32,DARKSUB,2)
    c.setFillColor(DARKSUB); c.setFont('Helvetica-Bold',18)
    c.drawString(22*mm,H-188*mm,'Pretoria · Johannesburg · London · New York · Sydney   —   one founding window per city')
    # listing card
    cy=70*mm; ch=H-205*mm-cy-18*mm
    c.setFillColor(WHITE); c.roundRect(18*mm,cy,W-36*mm,ch,6*mm,fill=1,stroke=0)
    c.setStrokeColor(LINEC); c.setLineWidth(1.2); c.roundRect(18*mm,cy,W-36*mm,ch,6*mm,fill=0,stroke=1)
    pad=14*mm; x0=18*mm+pad; topy=cy+ch-pad
    if spec.get('photos'):
        main=ImageReader(P+spec['photos'][0])
        iw,ih=main.getSize(); ar=ih/iw
        pw=min(320*mm,(W-36*mm-3*pad)*0.60); ph=pw*ar
        maxh=ch-2*pad
        if ph>maxh: ph=maxh; pw=ph/ar
        c.drawImage(main,x0,topy-ph,pw,ph,preserveAspectRatio=True,anchor='nw')
        if len(spec['photos'])>2:
            sw=(pw-6*mm)/2; sh=sw*0.75
            if topy-ph-8*mm-sh > cy+pad:
                for i,f in enumerate(spec['photos'][1:3]):
                    c.drawImage(ImageReader(P+f),x0+i*(sw+6*mm),topy-ph-8*mm-sh,sw,sh,preserveAspectRatio=True,anchor='nw')
        tx=x0+pw+pad
    else:
        c.setFillColor(ICE); c.roundRect(x0,cy+pad+50*mm,(W-36*mm-3*pad)*0.40,ch-2*pad-50*mm,5*mm,fill=1,stroke=0)
        zx=x0+(W-36*mm-3*pad)*0.20
        c.setFillColor(acc); c.setFont('Helvetica-Bold',260); c.drawCentredString(zx,cy+ch/2+30*mm,spec['glyph'])
        c.setFillColor(MUTED); c.setFont('Helvetica-Bold',15)
        c.drawCentredString(zx,cy+pad+72*mm,'REPRESENTATIVE LISTING')
        c.setFont('Helvetica',12.5)
        c.drawCentredString(zx,cy+pad+64*mm,'founding sellers’ real stock replaces this board')
        tx=x0+(W-36*mm-3*pad)*0.40+pad
    ty=topy-6*mm
    ty=para(c,tx,ty,W-18*mm-pad-tx,spec['title'],'Helvetica-Bold',34,40,NAVY,3)-6*mm
    c.setFillColor(acc); c.setFont('Helvetica-Bold',54); c.drawString(tx,ty-8*mm,spec['price']); ty-=26*mm
    c.setFillColor(MUTED); c.setFont('Helvetica',20); c.drawString(tx,ty,spec['loc']); ty-=16*mm
    w1=trust_chip(c,tx,ty-2*mm,11*mm,spec['trust'])
    w2=chip(c,tx+w1+5*mm,ty-2*mm,11*mm,spec['model'],WHITE,acc)
    chip(c,tx+w1+w2+10*mm,ty-2*mm,11*mm,'ANONYMOUS UNTIL ACCEPT',MUTED,ICE)
    ty-=22*mm
    ty=para(c,tx,ty,W-18*mm-pad-tx,spec['body'],'Helvetica',17,24,BODY,9)
    ty-=10*mm
    c.setFillColor(acc); c.setFont('Helvetica-Bold',19)
    c.drawString(tx,max(ty,cy+pad+52*mm),'Introduced for $2 — paid by the buyer, only when you accept.')
    # how-it-works strip across the card bottom (text column onward)
    sy=cy+pad; sw=(W-36*mm-2*pad)
    steps=[('1','Buyer browses anonymously'),('2','Pays $2 to request the intro'),('3','You accept or decline · 48 h'),('4','Identities revealed on accept')]
    stw=(sw-3*8*mm)/4
    c.setFillColor(MUTED); c.setFont('Helvetica-Bold',13)
    c.drawString(x0,sy+42*mm,'HOW AN INTRODUCTION WORKS')
    for i,(n,t) in enumerate(steps):
        sx=x0+i*(stw+8*mm)
        c.setFillColor(ICE); c.roundRect(sx,sy,stw,38*mm,4*mm,fill=1,stroke=0)
        c.setFillColor(acc); c.circle(sx+12*mm,sy+19*mm,7*mm,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold',17); c.drawCentredString(sx+12*mm,sy+16*mm,n)
        para(c,sx+23*mm,sy+25*mm,stw-28*mm,t,'Helvetica-Bold',14,17,NAVY,3)
        if i<3:
            c.setFillColor(MUTED); c.setFont('Helvetica-Bold',18); c.drawCentredString(sx+stw+4*mm,sy+16*mm,'→')
    if spec.get('credit'):
        c.setFillColor(MUTED); c.setFont('Helvetica',9.5); c.drawString(x0,cy+pad-9*mm,spec['credit'])
    # bottom strip
    c.setFillColor(GOLDBG); c.roundRect(18*mm,26*mm,W-36*mm,32*mm,5*mm,fill=1,stroke=0)
    diamond(c,32*mm,42*mm,4.5*mm)
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold',20)
    c.drawString(42*mm,46*mm,'Founding window — verified agencies & sellers join free; Ruby Spark badge, minted once, never again.')
    c.setFillColor(HexColor('#57534E')); c.setFont('Helvetica',15)
    c.drawString(42*mm,36*mm,'Zero listing fees. Zero commission. We load your existing database for you.')
    c.drawImage(QR,W-52*mm,28*mm,28*mm,28*mm)
    footer(c,W); trim(c,W,H); c.showPage(); c.save()

CATS=[
 dict(file='TrustSquare_A1_Property_DRAFT.pdf',cat='Property',title='Luxury Furnished Apartments — Unit 302 · 2 Bed',
      price='R 27 990 /pm',loc='Waterkloof · Pretoria',trust=75,model='COMMITMENT · pauses on intro',
      photos=['6ec9e891e483457b90afb0ee9fbc1427_IMG-20250710-WA0030.jpg','d289b683818b4cfbbf78b9cf4bc730ba_IMG-20250710-WA0031.jpg','9ffd8c0f8bad44aebce6dd1fe16f82b9_IMG-20250710-WA0032(1).jpg'],
      body='2 Bedrooms · 1 full bathroom · kitchenette/dining · lounge.\nSecure estate — 24-hour manned security booms, separate pedestrian and vehicle entrances.\nServices included: electricity, water, 500Mb/s fibre WiFi.\nReal listing, live on trustsquare.co today — photographed by the agency, privacy-scrubbed by policy.'),
 dict(file='TrustSquare_A1_Collectors_DRAFT.pdf',cat='Collectors',title='Tropical Island — Dual Land · MTG Revised Edition · Reserved List',
      price='R 2 800',loc='Rietvalleirand · Pretoria',trust=45,model='SOFT QUEUE · stays live',
      photos=['c1f78d8c51f44cd2953db3f8b233a66c_card.jpg'],
      body='Green-blue dual land counting as both Forest and Island; illustrated by Jesper Myrfors.\nModerate play wear — edge whitening and light surface aging typical of Revised era.\nA Reserved List staple of Legacy and Vintage play.\nCondition language is evidence-based by canon: an AI visual estimate, never a certified grade — the final grade follows TrustSquare’s assessment.'),
 dict(file='TrustSquare_A1_Adventures_DRAFT.pdf',cat='Adventures',title='Hot Air Balloon Safari · Hartbeespoort',
      price='R 3 200 /pp',loc='Hartbeespoort · Gauteng',trust=72,model='SOFT QUEUE · stays live',
      photos=['np_040_vv_d1d1749e95.jpg'],
      body='Sunrise flight over the Magaliesberg with champagne landing — representative founding-window experience listing.\nAdventures launches beside the World Heritage Content Layer: 332 National Parks and UNESCO sites browsable in-app as native editorial content, linkable from any listing.\nPictured: Blyde River Canyon — one of the 332 heritage sites live today.',
      credit='Photo: Blyde River Canyon · Wikimedia Commons (CC) · part of the TrustSquare World Heritage layer'),
 dict(file='TrustSquare_A1_Cars_DRAFT.pdf',cat='Cars',title='2019 Porsche 911 Carrera S · PDK · 58 000 km',
      price='R 2 850 000',loc='Pretoria East',trust=68,model='COMMITMENT · pauses on intro',glyph='C',
      body='Full service history · PDK · sports chrono.\nDealership-grade presentation without dealership lead fees: the buyer pays $2 to be introduced; you keep every rand of your price.\nVision AI reads condition honestly from your photos — no hype, real features only.'),
 dict(file='TrustSquare_A1_Tutors_DRAFT.pdf',cat='Tutors',title='Mathematics & Physical Science — Matric Specialist',
      price='R 380 /hr',loc='Pretoria East',trust=81,model='SOFT QUEUE · stays live',glyph='T',
      body='IEB & CAPS · Grades 10–12 · exam-prep intensives.\nTutors verify against teaching credentials — the Trust Score puts a tutor’s qualifications on every card.\nStudents pay $2 to be introduced, so every enquiry is a student who means it.'),
 dict(file='TrustSquare_A1_Services_DRAFT.pdf',cat='Services',title='Registered Electrician — Fault Finding & Compliance Certificates',
      price='R 650 callout',loc='Pretoria North',trust=77,model='SOFT QUEUE · stays live',glyph='S',
      body='ECA-registered · CoC issue · 24h emergency line.\nTrade credentials are the quality gate: registration and track record build the public Trust Score.\nNo lead packs, no pay-per-click — a $2 buyer-paid introduction replaces the lead-gen tax.'),
 dict(file='TrustSquare_A1_LocalMarket_DRAFT.pdf',cat='Local Market',title='Rolex Submariner Date · Ref 116610LN · 2019 · Box & Papers',
      price='R 198 000',loc='Centurion',trust=64,model='SOFT QUEUE · stays live',glyph='L',
      body='Full set · service history · honest wear notes.\nEvery Local Market seller starts at Established trust — verified locals, not anonymous classifieds.\nAnonymity protects both sides until a $2 introduction is mutually accepted.'),
]
for s in CATS: category_poster(s)

# ── Features A1 ──────────────────────────────────────────────────────
fns=json.load(open('/tmp/pitch/functions.json'))
W,H=A1W,A1H
c=canvas.Canvas(OUT+'TrustSquare_A1_AI_Features_DRAFT.pdf',pagesize=(W+2*BLEED,H+2*BLEED))
c.translate(BLEED,BLEED)
c.setFillColor(NAVY); c.rect(-BLEED,-BLEED,W+2*BLEED,H+2*BLEED,fill=1,stroke=0)
diamond(c,22*mm,H-22*mm,5*mm); wordmark(c,32*mm,H-25*mm,30)
c.setFillColor(GOLD); c.setFont('Helvetica-Bold',24); c.drawString(22*mm,H-50*mm,'AI FEATURES · IN THE BUYER & SELLER APP')
c.setFillColor(WHITE); c.setFont('Helvetica-Bold',64)
c.drawString(22*mm,H-75*mm,'Free glimpse. Paid deep dive.')
c.setFillColor(DARKSUB); c.setFont('Helvetica',23)
c.drawString(22*mm,H-92*mm,'Ten research features, every one live. Charged in Tuppence (1T = $2) — and only when the report is delivered.')
gx,gy=18*mm,H-110*mm; cw=(W-36*mm-12*mm)/2; chh=118*mm; gap=6*mm
for i,f in enumerate(fns):
    col=i%2; row=i//2
    x=gx+col*(cw+12*mm); y=gy-row*(chh+gap)-chh
    c.setFillColor(HexColor('#1B2A44')); c.roundRect(x,y,cw,chh,5*mm,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont('Helvetica-Bold',25)
    name=f['name'] if c.stringWidth(f['name'],'Helvetica-Bold',25)<cw-95*mm else f['name'][:30]+'…'
    c.drawString(x+10*mm,y+chh-18*mm,name)
    pw=chip(c,x+cw-66*mm,y+chh-21*mm,12*mm,f"{f['price_t']}T · ${f['price_t']*2}",NAVY,GOLDBG.clone() if False else GOLDBG)
    chip(c,x+cw-66*mm+pw+4*mm,y+chh-21*mm,12*mm,'LIVE',WHITE,GREEN)
    chip(c,x+10*mm,y+chh-36*mm,10*mm,('BUYER SIDE' if f['side']=='buyer' else 'SELLER SIDE'),DARKSUB,HexColor('#31415E'))
    bl=f.get('blurb','')
    if len(bl)<150: bl=bl.rstrip('. ')+'. Free Level-1 glimpse answers the first question; the paid level delivers the full researched report.'
    para(c,x+10*mm,y+chh-50*mm,cw-20*mm,bl[:430],'Helvetica',15.5,21,DARKSUB,5)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold',14)
    c.drawString(x+10*mm,y+9*mm,'Free Level-1 glimpse in-app  →  full report on delivery')
c.setFillColor(DARKSUB); c.setFont('Helvetica',16)
c.drawString(22*mm,24*mm,'Price ladder: Free · 2T · 3T · 5T  —  a failed run never charges: the hold is released, by design.')
c.drawImage(QR,W-46*mm,16*mm,28*mm,28*mm)
c.setFillColor(RUBY); c.setFont('Helvetica-Oblique',10)
c.drawString(22*mm,12*mm,'INTERNAL DRAFT — do not circulate until the provisional patent is filed')
trim(c,W,H); c.showPage(); c.save()

# ── Report A2s ───────────────────────────────────────────────────────
def report_poster(r):
    W,H=A2W,A2H
    c=canvas.Canvas(OUT+r['file'],pagesize=(W+2*BLEED,H+2*BLEED))
    c.translate(BLEED,BLEED); page(c,W,H)
    acc=r['accent']
    c.setFillColor(NAVY); c.rect(-BLEED,H-92*mm,W+2*BLEED,92*mm+BLEED,fill=1,stroke=0)
    c.setFillColor(acc); c.rect(-BLEED,H-92*mm,W+2*BLEED,3.5*mm,fill=1,stroke=0)
    diamond(c,16*mm,H-15*mm,3.4*mm); wordmark(c,23*mm,H-17*mm,20)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold',15)
    c.drawString(16*mm,H-33*mm,'AI FEATURE · EXAMPLE REPORT')
    c.setFillColor(WHITE); c.setFont('Helvetica-Bold',33)
    yy=H-46*mm
    for ln in simpleSplit(r['title'],'Helvetica-Bold',33,W-32*mm)[:2]:
        c.drawString(16*mm,yy,ln); yy-=13*mm
    c.setFillColor(DARKSUB); c.setFont('Helvetica',15.5); c.drawString(16*mm,yy-2*mm,r['params'])
    pw=chip(c,16*mm,H-88*mm,10*mm,r['price'],NAVY,GOLDBG)
    chip(c,16*mm+pw+4*mm,H-88*mm,10*mm,r['srcchip'][0],*r['srcchip'][1])
    # callouts
    cy=H-92*mm-34*mm; cwd=(W-32*mm-16*mm)/3
    for i,(num,lab) in enumerate(r['callouts']):
        x=16*mm+i*(cwd+8*mm)
        c.setFillColor(ICE); c.roundRect(x,cy,cwd,26*mm,3.5*mm,fill=1,stroke=0)
        c.setFillColor(acc); c.setFont('Helvetica-Bold',25); c.drawCentredString(x+cwd/2,cy+14*mm,num)
        c.setFillColor(MUTED); c.setFont('Helvetica',10.5); c.drawCentredString(x+cwd/2,cy+6*mm,lab)
    # table
    ty=cy-12*mm
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold',15); c.drawString(16*mm,ty,r['table_title']); ty-=8*mm
    colw=r['colw']; rowh=11.5*mm
    c.setFillColor(acc); c.rect(16*mm,ty-rowh+3*mm,sum(colw),rowh-1*mm,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont('Helvetica-Bold',10.5)
    xx=16*mm
    for wdt,hd in zip(colw,r['headers']): c.drawString(xx+3*mm,ty-4.5*mm,hd); xx+=wdt
    ty-=rowh
    c.setFont('Helvetica',10)
    for ri,row in enumerate(r['rows']):
        if ri%2==0: c.setFillColor(HexColor('#F4F6FA')); c.rect(16*mm,ty-rowh+3*mm,sum(colw),rowh-1*mm,fill=1,stroke=0)
        xx=16*mm
        for wdt,cell in zip(colw,row):
            c.setFillColor(BODY); c.setFont('Helvetica',9.6)
            for k,ln in enumerate(simpleSplit(cell,'Helvetica',9.6,wdt-6*mm)[:2]):
                c.drawString(xx+3*mm,ty-4*mm-k*4.2*mm,ln)
            xx+=wdt
        ty-=rowh
    ty-=6*mm
    # body excerpt
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold',15); c.drawString(16*mm,ty,r['body_title']); ty-=7.5*mm
    ty=para(c,16*mm,ty,W-32*mm,r['body'],'Helvetica',11.5,15.5,BODY,r.get('body_lines',14))
    # highlight box
    if r.get('highlight'):
        hb=30*mm
        c.setFillColor(GOLDBG); c.roundRect(16*mm,38*mm,W-32*mm,hb,4*mm,fill=1,stroke=0)
        c.setFillColor(HexColor('#92400E')); c.setFont('Helvetica-Bold',13)
        c.drawString(22*mm,38*mm+hb-9*mm,r['highlight'][0])
        para(c,22*mm,38*mm+hb-16*mm,W-44*mm,r['highlight'][1],'Helvetica',11,14,HexColor('#57534E'),2)
    # honesty footer
    c.setFillColor(ICE); c.rect(-BLEED,16*mm,W+2*BLEED,16*mm,fill=1,stroke=0)
    c.setFillColor(MUTED); c.setFont('Helvetica',10)
    c.drawString(16*mm,26*mm,r['honesty'])
    c.drawString(16*mm,21*mm,'Extracts shown — the full report is delivered in the app. A failed run never charges; the Tuppence hold is released.')
    c.drawImage(QR,W-30*mm,18*mm,12*mm,12*mm)
    footer(c,W); trim(c,W,H); c.showPage(); c.save()

REPORTS=[
 dict(file='TrustSquare_A2_Report_Collectables_Advert_DRAFT.pdf',accent=HexColor('#5B21B6'),
  title='Collectables Advert + Market Report',params='12-card vintage MTG lot · Pretoria · seller-side · 5T ($10)',
  price='5T · $10',srcchip=('REAL RUN',(WHITE,GREEN)),
  callouts=[('12','cards identified & graded from photos'),('12','live web searches across price sources'),('$0.55','actual API cost of this run')],
  table_title='Market findings (extract — 5 of 12 cards)',
  colw=[52*mm,38*mm,34*mm,98*mm,18*mm],headers=['Card','Intl. range','ZAR est.','Evidence (sourced live)','Conf.'],
  rows=[['Masticore (Urza’s Destiny)','$8–$14','R150–R260','TCGplayer buy $11.03 (EchoMTG); active eBay listings','M'],
        ['Nevinyrral’s Disk (Revised)','$6–$12','R110–R220','eBay LP listings; SCG HP copy; intl. LP–NM ~$10–15','M'],
        ['Zhalfirin Crusader (Visions)','$1.50–$2','R28–R37','Misty Mountain NM/LP $2.00; MTGDecks ~$0.75','M'],
        ['Veteran Bodyguard (Revised)','$2.50–$5','R46–R93','MTGDecks “$300” flagged as data error and disregarded','L'],
        ['Vesuvan Doppelganger (Revised)','$12–$25','R222–R463','MTGStocks avg $21.52 — highest-value card in the lot','M']],
  body_title='The advert it wrote (opening)',
  body='“Vintage MTG Lot: 12 Old-School Rares — Revised, Alliances & More.”\nCalling all old-school Magic collectors and Vintage/Legacy players — a curated batch of 12 genuine MTG rares from the most beloved sets of the 1990s: white-bordered Revised Edition (1994), Homelands (1995), Alliances and Visions (1996–97), into Urza’s Destiny (1999). Every card English-language and sleeve-stored, most showing only light play wear consistent with age.',
  body_lines=8,
  highlight=('The AI caught a pricing-data error','One source listed Veteran Bodyguard at $300; the report flagged it as a data anomaly and priced honestly at R46–R93 — evidence-based by canon, even when a bigger number was available.'),
  honesty=f'REAL RUN · {SAMPLE_RUN_MODEL} · 104k input tokens · 12 web searches · $0.5514 actual cost · delivered 7 Jun 2026.'),
 dict(file='TrustSquare_A2_Report_Heritage_Tour_DRAFT.pdf',accent=HexColor('#0F6E56'),
  title='Heritage Site Tour Planner',params='Kruger National Park road trip · Pretoria · 5 days · 2 adults · 5T ($10)',
  price='5T · $10',srcchip=('REPLAY OF A REAL DELIVERY',(NAVY,GOLDBG)),
  callouts=[('~940 km','full round-trip route, leg by leg'),('5 days','day-by-day schedule with gate times'),('R19k–R41k','transparent cost estimate, all items')],
  table_title='Route overview (as delivered)',
  colw=[58*mm,74*mm,46*mm,62*mm],headers=['Leg','Route','Distance (est.)','Drive time (est.)'],
  rows=[['Day 1 · Pretoria → Graskop','N4 east → R540 north','~380 km','~4 h 30'],
        ['Day 2 · Graskop → Hazyview','Panorama Route scenic (R532)','~80 km scenic','2–3 h incl. stops'],
        ['Day 3–4 · Kruger day drives','R536 to Paul Kruger / Phabeni Gate','14–20 km each way','~20 min to gate'],
        ['Day 5 · Hazyview → Pretoria','R40 → N4 west','~480 km','~5 h 30']],
  body_title='Cost estimate (extract)',
  body='Fuel ~R1,800 · N4 tolls ~R600 · Night 1 Graskop escarpment R4,000–R6,500 · Nights 2–4 Hazyview lodge R9,000–R21,000 · Kruger conservation fees R536 (SA citizens) or R2,408 (international) · Meals R2,100–R4,200 · Panorama Route entries R500–R1,000 · Optional guided game drive R1,500–R4,000.\nEvery figure marked (est.) and sourced; the in-app version renders the full interactive route map with waypoints.',
  body_lines=8,
  highlight=('Map-first by contract','The v1.2 delivery contract requires waypoints with every tour — the app renders the live route map; a map-less delivery is treated as a failed run and never charges.'),
  honesty=f'Replayed from the last REAL delivery (API $0 replay) · model {SAMPLE_RUN_MODEL} · original run server-side with live web search.'),
 dict(file='TrustSquare_A2_Report_Retirement_Planner_DRAFT.pdf',accent=HexColor('#1E3A5F'),
  title='Retirement Relocation Planner',params='UK couple, late 60s → Muizenberg, Cape Town · 5T ($10)',
  price='5T · $10',srcchip=('AUTHORED SAMPLE',(MUTED,ICE)),
  callouts=[('R37,000','/month guaranteed income — SA retired-person visa test'),('FROZEN','UK state pension never inflation-adjusts in SA'),('£250k','Kent house sale buys the Muizenberg home outright')],
  table_title='Visa & legal (UK passport) — as reported',
  colw=[40*mm,118*mm,82*mm],headers=['Item','Detail','Source'],
  rows=[['Visa','Retired Person’s Visa — up to 4 years, renewable','dha.gov.za'],
        ['Income test','R37,000/month guaranteed (pension/annuity only — salary does NOT count)','Gazette threshold — verify current'],
        ['Spouse','Accompanying-spouse visa tied to the main holder','dha.gov.za'],
        ['Alternative','Meet the test via capital structured as an irrevocable annuity','immigration practitioner']],
  body_title='Verdict (extract)',
  body='For a UK couple in their late 60s with a combined pension near £1,800/month plus ~£250,000 from selling a Kent home, retiring to Muizenberg is comfortably feasible — the capital buys the house outright and the pension funds a better lifestyle than it does in Kent. The two hardest constraints, up front: the visa income test, and planning against a flat (frozen) UK state pension figure.\nRisk note carried in the report: informational only — verify with the SA High Commission or a registered immigration practitioner before acting.',
  body_lines=9,
  highlight=('Honest constraints, up front','The report leads with the two hardest blockers — the R37,000/month visa test and the frozen UK pension — before any lifestyle content. Bad news first, by design.'),
  honesty='AUTHORED SAMPLE (development fixture) — illustrative example of the delivered format, clearly labelled; not real research.'),
 dict(file='TrustSquare_A2_Report_Expedition_Dossier_DRAFT.pdf',accent=HexColor('#C0273C'),
  title='Once-in-a-Lifetime Expedition Dossier',params='Lake Baikal in winter · from South Africa · 14 days · 2 adults · 5T ($10)',
  price='5T · $10',srcchip=('AUTHORED SAMPLE',(MUTED,ICE)),
  callouts=[('3 legs','flight connections from ZA, mapped'),('Feb–Mar','the ice season window that makes it'),('R85k–130k','budget for two — 70% flights + guided ice')],
  table_title='Feasibility snapshot — as reported',
  colw=[60*mm,180*mm],headers=['Question','Answer'],
  rows=[['Achievable from ZA?','Yes — 3 connection legs + one specialist local operator'],
        ['When?','February–March: the lake’s metre-thick black-ice season'],
        ['Budget class','R85,000–R130,000 for two (est.)'],
        ['Where the money goes','~70% flights + the guided ice segment']],
  body_title='Why this feature exists',
  body='Adventures isn’t only weekend escapes — the Expedition Dossier turns a bucket-list idea into a researched plan: route, operator class, season physics, budget envelope and risk notes, before a buyer commits to anything. The free Level-1 glimpse answers “is this even possible?”; the paid dossier answers “exactly how.”',
  body_lines=6,
  highlight=('Free glimpse → paid depth','Every research feature ships a free Level-1 answer in-app. The 5T deep dive is bought only when the glimpse earns it.'),
  honesty='AUTHORED SAMPLE (development fixture) — illustrative example of the delivered format, clearly labelled; not real research.'),
 dict(file='TrustSquare_A2_Report_Property_Dossier_DRAFT.pdf',accent=HexColor('#B45309'),
  title='Property Area Dossier',params='Lynnwood, Pretoria · buyer-side · 3T ($6)',
  price='3T · $6',srcchip=('AUTHORED SAMPLE',(MUTED,ICE)),
  callouts=[('R2.45m','median 3-bed sale (12-month area sales)'),('R9.8–12.4k','rand per m² range, comparable transfers'),('62 days','median time on market')],
  table_title='Market position — as reported',
  colw=[68*mm,86*mm,86*mm],headers=['Metric','Value (est., sample)','Basis'],
  rows=[['Median 3-bed sale','R2.45m','12-month area sales'],
        ['R/m² range','R9,800–R12,400','comparable transfers'],
        ['Days on market','62 median','area listings']],
  body_title='The buyer’s companion to every Property introduction',
  body='Before paying for an introduction, a buyer can buy context: what the area actually trades at, how long stock sits, what the rand-per-square-metre band looks like. The Area Snapshot is free; the Investor Dossier (3T) adds yield bands, growth context and comparable evidence — making the $2 introduction a decision, not a gamble.',
  body_lines=6,
  highlight=('Built for the Simpler Model','Property Area Dossier is the first free-glimpse/paid-dive split in the canon price ladder (Free / 2T / 3T / 5T).'),
  honesty='AUTHORED SAMPLE (development fixture) — illustrative example of the delivered format, clearly labelled; not real research.'),
]
for r in REPORTS: report_poster(r)
print('SET DONE:', len(os.listdir(OUT)), 'files')
