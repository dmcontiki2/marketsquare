from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

NAVY=HexColor('#111827'); ACCENT=HexColor('#1E3A5F'); ICE=HexColor('#EEF2F8')
GOLD=HexColor('#C9962E'); GOLDBG=HexColor('#FEF3C7'); RUBY=HexColor('#C0273C')
MUTED=HexColor('#5B6470'); WHITE=HexColor('#FFFFFF'); LINEC=HexColor('#E2E5EA')
DARKSUB=HexColor('#C7D2E3'); BODY=HexColor('#374151')
QR=ImageReader('/tmp/pitch/assets/qr.png')

def diamond(c,cx,cy,r,col):
    c.setFillColor(col); p=c.beginPath()
    p.moveTo(cx,cy+r); p.lineTo(cx+r,cy); p.lineTo(cx,cy-r); p.lineTo(cx-r,cy); p.close()
    c.drawPath(p,fill=1,stroke=0)

def wordmark(c,x,y,size):
    c.setFont('Helvetica-Bold',size)
    c.setFillColor(WHITE); c.drawString(x,y,'TRUST')
    w=c.stringWidth('TRUST','Helvetica-Bold',size)
    c.setFillColor(GOLD); c.drawString(x+w,y,'SQUARE')

def proof_row(c,x,y,w,glyph,head,body,gs,hs,bs,gap):
    c.setFillColor(ICE); c.circle(x+gs/2,y+gs/2,gs/2,fill=1,stroke=0)
    c.setFillColor(ACCENT); c.setFont('Helvetica-Bold',gs*0.5)
    c.drawCentredString(x+gs/2,y+gs/2-gs*0.17,glyph)
    tx=x+gs+gap
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold',hs); c.drawString(tx,y+gs*0.62,head)
    c.setFillColor(MUTED); c.setFont('Helvetica',bs)
    for i,ln in enumerate(body):
        c.drawString(tx,y+gs*0.62-hs*1.15-i*bs*1.25,ln)

# ── A4 leave-behind ──────────────────────────────────────────────────
W,H=A4
c=canvas.Canvas('/tmp/pitch/TrustSquare_Agency_Poster_A4_DRAFT_v1.pdf',pagesize=A4)
c.setFillColor(NAVY); c.rect(0,H-118*mm,W,118*mm,fill=1,stroke=0)
diamond(c,診:=18*mm,H-16*mm,3.2*mm,RUBY) if False else diamond(c,18*mm,H-16*mm,3.2*mm,RUBY)
wordmark(c,24*mm,H-18*mm,15)
c.setFillColor(WHITE); c.setFont('Helvetica-Bold',31)
c.drawString(18*mm,H-42*mm,'Your listings. Our buyers.')
c.drawString(18*mm,H-55*mm,'Zero fees. Forever.')
c.setFillColor(DARKSUB); c.setFont('Helvetica',12.5)
c.drawString(18*mm,H-68*mm,'The introduction marketplace for verified estate agencies.')
c.setFont('Helvetica-Bold',10.5); c.setFillColor(GOLD)
c.drawString(18*mm,H-80*mm,'Pretoria  ·  Johannesburg  ·  London  ·  New York  ·  Sydney')
c.setFillColor(DARKSUB); c.setFont('Helvetica',10)
for i,ln in enumerate(['No commission. No listing fees. Buyers pay a $2 introduction','only when an introduction actually happens — so our incentive','is your incentive: serious buyers, fast.']):
    c.drawString(18*mm,H-93*mm-i*5*mm,ln)
rows=[('$','Zero cost, forever',['$0 listing fees · $0 commission · the buyer pays the $2 introduction.']),
      ('◆','Free verified-agency tier',['Caps rise with trust — 10 to 100 to 500 listings. Never a paywall.']),
      ('▲','We load your database',['White-glove import from your portal feed, privacy-scrubbed by policy.']),
      ('★','Trust Score on every card',['Verification + credentials + track record. 90+ earns gold and priority.'])]
y=H-132*mm
for g,h2,b in rows:
    proof_row(c,18*mm,y,W-36*mm,g,h2,b,9*mm,13,10,4*mm); y-=21*mm
c.setFillColor(GOLDBG); c.roundRect(18*mm,52*mm,W-36*mm,22*mm,3*mm,fill=1,stroke=0)
diamond(c,26*mm,63*mm,2.6*mm,RUBY)
c.setFillColor(NAVY); c.setFont('Helvetica-Bold',11.5)
c.drawString(32*mm,65*mm,'The founding window — the Ruby Spark')
c.setFillColor(HexColor('#57534E')); c.setFont('Helvetica',9.5)
c.drawString(32*mm,59*mm,'Join inside your city’s window: founding badge + founders’ terms for life. Minted once, never again.')
c.drawImage(QR,18*mm,16*mm,26*mm,26*mm)
c.setFillColor(NAVY); c.setFont('Helvetica-Bold',13)
c.drawString(50*mm,32*mm,'trustsquare.co')
c.setFillColor(MUTED); c.setFont('Helvetica',9.5)
c.drawString(50*mm,26*mm,'Become a founding agency: 30 minutes + your listings export.')
c.setFillColor(RUBY); c.setFont('Helvetica-Oblique',7.5)
c.drawString(18*mm,9*mm,'INTERNAL DRAFT — do not circulate until the provisional patent is filed')
c.showPage(); c.save()

# ── Pull-up banner 850 × 2000 mm ─────────────────────────────────────
BW,BH=850*mm,2000*mm
c=canvas.Canvas('/tmp/pitch/TrustSquare_Agency_Banner_850x2000_DRAFT_v1.pdf',pagesize=(BW,BH))
c.setFillColor(NAVY); c.rect(0,BH-760*mm,BW,760*mm,fill=1,stroke=0)
diamond(c,80*mm,BH-95*mm,16*mm,RUBY)
wordmark(c,108*mm,BH-105*mm,72)
c.setFillColor(WHITE); c.setFont('Helvetica-Bold',150)
c.drawString(70*mm,BH-280*mm,'Your listings.')
c.drawString(70*mm,BH-340*mm,'Our buyers.')
c.setFillColor(GOLD)
c.drawString(70*mm,BH-430*mm,'Zero fees.')
c.drawString(70*mm,BH-490*mm,'Forever.')
c.setFillColor(DARKSUB); c.setFont('Helvetica',52)
c.drawString(70*mm,BH-580*mm,'The introduction marketplace')
c.drawString(70*mm,BH-605*mm,'for verified estate agencies.')
c.setFillColor(GOLD); c.setFont('Helvetica-Bold',38)
c.drawString(70*mm,BH-700*mm,'Pretoria · Johannesburg · London · New York · Sydney')
rows=[('$','Zero cost, forever','$0 listing fees, $0 commission — buyers pay the $2 introduction.'),
      ('◆','Free verified-agency tier','Caps rise with trust: 10 → 100 → 500 listings. Never a paywall.'),
      ('▲','We load your database','White-glove import from your portal feed, privacy-scrubbed.'),
      ('★','Trust Score on every card','Verification, credentials, track record — 90+ earns gold.')]
y=BH-880*mm
for g,h2,b in rows:
    c.setFillColor(ICE); c.circle(110*mm,y+30*mm,34*mm,fill=1,stroke=0)
    c.setFillColor(ACCENT); c.setFont('Helvetica-Bold',60); c.drawCentredString(110*mm,y+12*mm,g)
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold',56); c.drawString(170*mm,y+38*mm,h2)
    c.setFillColor(MUTED); c.setFont('Helvetica',34); c.drawString(170*mm,y-6*mm,b)
    y-=190*mm
c.setFillColor(GOLDBG); c.roundRect(60*mm,260*mm,BW-120*mm,150*mm,16*mm,fill=1,stroke=0)
diamond(c,110*mm,335*mm,18*mm,RUBY)
c.setFillColor(NAVY); c.setFont('Helvetica-Bold',52)
c.drawString(150*mm,350*mm,'The founding window — the Ruby Spark')
c.setFillColor(HexColor('#57534E')); c.setFont('Helvetica',36)
c.drawString(150*mm,300*mm,'Founding badge + founders’ terms for life. Minted at launch, never again.')
c.drawImage(QR,60*mm,60*mm,150*mm,150*mm)
c.setFillColor(NAVY); c.setFont('Helvetica-Bold',64)
c.drawString(240*mm,150*mm,'trustsquare.co')
c.setFillColor(MUTED); c.setFont('Helvetica',34)
c.drawString(240*mm,100*mm,'Become a founding agency — 30 minutes + your listings export.')
c.setFillColor(RUBY); c.setFont('Helvetica-Oblique',26)
c.drawString(60*mm,25*mm,'INTERNAL DRAFT — do not circulate until the provisional patent is filed')
c.showPage(); c.save()
print('posters written')
