#!/usr/bin/env python3
"""build_dossier_pdf.py -- the Study & Work Abroad dossier template (SAW-3, RUL-044).

Renders a dossier dict into the house-style A4 PDF. This script IS the visual
prototype of the P4 dossier generator in STUDYWORK_DOSSIER_SPEC.md: when the live
engine builds a user's dossier, it fills the same structure this file renders.
Both EXAMPLE dossiers (Lerato/Hungary study, Pieter/USA farm work) are generated
from datasets in dossier_examples.py. AI-EXAMPLE honesty labels are structural:
cover band + every-page footer tag (RUL-040 class).
"""
import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, PageBreak, Flowable,
                                KeepTogether)
from reportlab.platypus import Image as RLImage

NAVY  = colors.HexColor("#1F3864"); BLUE  = colors.HexColor("#2F5496")
GOLD  = colors.HexColor("#C9A227"); LBLUE = colors.HexColor("#EAF0FA")
BODY  = colors.HexColor("#262626"); MUTED = colors.HexColor("#595959")
RED   = colors.HexColor("#B91C1C"); AMBER = colors.HexColor("#C55A11")
GREEN = colors.HexColor("#538135"); LINE  = colors.HexColor("#D9D9D9")
DARKRED = colors.HexColor("#7F1D1D")
W,H = A4; M = 18*mm

def S(name, **kw):
    base = dict(fontName="Helvetica", fontSize=9.5, leading=13.5, textColor=BODY,
                spaceAfter=5, alignment=TA_LEFT)
    base.update(kw); return ParagraphStyle(name, **base)
ST = {
 "h1": S("h1", fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=NAVY, spaceBefore=6, spaceAfter=4),
 "h2": S("h2", fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=BLUE, spaceBefore=10, spaceAfter=3),
 "body": S("body"),
 "small": S("small", fontSize=8, leading=11, textColor=MUTED),
 "chip": S("chip", fontName="Helvetica-Bold", fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.white),
 "cell": S("cell", fontSize=8.6, leading=12),
 "cellb": S("cellb", fontName="Helvetica-Bold", fontSize=8.6, leading=12),
 "th": S("th", fontName="Helvetica-Bold", fontSize=8.6, leading=11, textColor=colors.white),
}
def P(t, s="body"): return Paragraph(t, ST[s])
VCOL = {"HIGH":GREEN, "MEDIUM":AMBER, "LOW":RED, "CLOSED":DARKRED, "SEE PANEL":MUTED}

class GoldBar(Flowable):
    def __init__(self, text):
        Flowable.__init__(self); self.text=text; self.height=9*mm
    def wrap(self, aw, ah): self.width=aw; return aw, self.height
    def draw(self):
        c=self.canv
        c.setFillColor(GOLD); c.rect(0, 1.5*mm, 2.2*mm, 6*mm, stroke=0, fill=1)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 13)
        c.drawString(4.5*mm, 3*mm, self.text)

class RoutePanel(Flowable):
    """Stylised journey band: nodes + arcs, no fake geography."""
    def __init__(self, nodes):
        Flowable.__init__(self); self.nodes=nodes; self.height=30*mm
    def wrap(self, aw, ah): self.width=aw; return aw, self.height
    def draw(self):
        c=self.canv; n=len(self.nodes)
        xs=[ self.width*(i+0.5)/n for i in range(n) ]; y=11*mm
        c.setFillColor(colors.HexColor("#F4F7FC"))
        c.roundRect(0,0,self.width,self.height,3*mm,stroke=0,fill=1)
        for i in range(n-1):
            col = VCOL.get(self.nodes[i+1].get("v","HIGH"), BLUE)
            c.setStrokeColor(col); c.setLineWidth(1.1); c.setDash(3,3)
            c.bezier(xs[i], y, (xs[i]+xs[i+1])/2, y+9*mm, (xs[i]+xs[i+1])/2, y+9*mm, xs[i+1], y)
        c.setDash()
        for i,nd in enumerate(self.nodes):
            col = VCOL.get(nd.get("v","HIGH"), NAVY) if i>0 else GOLD
            c.setFillColor(col); c.circle(xs[i], y, 2.3*mm, stroke=0, fill=1)
            c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 7.6)
            c.drawCentredString(xs[i], y-6.5*mm, nd["name"][:26])
            c.setFillColor(MUTED); c.setFont("Helvetica", 6.8)
            c.drawCentredString(xs[i], y-10*mm, nd.get("sub","")[:30])

def chip(text, col):
    t=Table([[P(text,"chip")]], colWidths=[None])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),col),
        ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5)]))
    return t

def styled_table(headers, rows, widths, aligns=None):
    data=[[P(h,"th") for h in headers]]
    for r in rows:
        data.append([x if isinstance(x,(Table,Paragraph)) else P(str(x),"cell") for x in r])
    t=Table(data, colWidths=widths, repeatRows=1)
    style=[("BACKGROUND",(0,0),(-1,0),NAVY),
           ("GRID",(0,0),(-1,-1),0.4,LINE),
           ("VALIGN",(0,0),(-1,-1),"TOP"),
           ("TOPPADDING",(0,0),(-1,-1),3.5),("BOTTOMPADDING",(0,0),(-1,-1),3.5),
           ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5)]
    for i in range(2, len(data), 2):
        style.append(("BACKGROUND",(0,i),(-1,i),LBLUE))
    t.setStyle(TableStyle(style)); return t

def callout(text, fill, border, label=None):
    inner = P(("<b>%s</b>  " % label if label else "") + text, "cell")
    t=Table([[inner]], colWidths=[W-2*M])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),fill),
        ("LINEBEFORE",(0,0),(0,-1),2.6,border),
        ("LINEABOVE",(0,0),(-1,0),0.4,LINE),("LINEBELOW",(0,-1),(-1,-1),0.4,LINE),
        ("LINEAFTER",(-1,0),(-1,-1),0.4,LINE),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8)]))
    return t

def _footer(c, doc, d):
    c.saveState()
    c.setStrokeColor(NAVY); c.setLineWidth(0.7); c.line(M, 14*mm, W-M, 14*mm)
    c.setFont("Helvetica", 7); c.setFillColor(MUTED)
    c.drawString(M, 10*mm, "Study & Work Abroad - Example Dossier  |  TrustSquare / MarketSquare")
    c.drawRightString(W-M, 10*mm, "page %d" % doc.page)
    c.setFillColor(RED); c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(W/2, 6.5*mm, "AI-GENERATED EXAMPLE - NOT A REPORT FOR A REAL USER")
    c.restoreState()

def _cover(c, doc, d):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, H-118*mm, W, 118*mm, stroke=0, fill=1)
    c.setFillColor(GOLD); c.rect(0, H-120*mm, W, 2*mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11); c.drawString(M, H-24*mm, "MARKETSQUARE  |  TRUSTSQUARE.CO")
    c.setFont("Helvetica", 10.5); c.drawString(M, H-33*mm, "Study & Work Abroad - a 5 Tuppence preparation dossier")
    c.setFont("Helvetica-Bold", 26)
    y=H-52*mm
    for ln in d["cover_title"]:
        c.drawString(M, y, ln); y-=11*mm
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 12)
    c.drawString(M, y-2*mm, d["cover_sub"])
    c.setFillColor(colors.white); c.setFont("Helvetica", 9.5); y-=12*mm
    for ln in d["cover_lines"]:
        c.drawString(M, y, ln); y-=5.5*mm
    # contents block in the cover's open space
    y0 = H-158*mm
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 11)
    c.drawString(M, y0, "Inside this dossier")
    c.setStrokeColor(GOLD); c.setLineWidth(1.4); c.line(M, y0-2.2*mm, M+42*mm, y0-2.2*mm)
    c.setFont("Helvetica", 9.2); c.setFillColor(BODY)
    yy = y0-9*mm
    for item in d.get("cover_contents", []):
        c.setFillColor(GOLD); c.circle(M+1.4*mm, yy+1.1*mm, 0.9*mm, stroke=0, fill=1)
        c.setFillColor(BODY); c.drawString(M+5*mm, yy, item)
        yy -= 6.2*mm
    c.setFillColor(RED); c.rect(0, H-134*mm, W, 11*mm, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 9.5)
    c.drawCentredString(W/2, H-130.5*mm, "AI-GENERATED EXAMPLE DOSSIER - NOT A REPORT FOR A REAL USER")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawCentredString(W/2, 22*mm, "An AI-made example of the benchmark for this feature. Facts are real, sourced and dated; volatile figures are")
    c.drawCentredString(W/2, 18*mm, "flagged RE-CHECK. Preparation, not advice: plans and guidance come from the registered agency we introduce you to.")
    _footer(c, doc, d)
    c.restoreState()

def build(d, out):
    doc=BaseDocTemplate(out, pagesize=A4, leftMargin=M, rightMargin=M,
                        topMargin=16*mm, bottomMargin=20*mm,
                        title=d["cover_sub"], author="MarketSquare - Study & Work Abroad")
    fr=Frame(M, 20*mm, W-2*M, H-38*mm, id="f")
    cover_fr=Frame(M, 140*mm, W-2*M, 10*mm, id="cf")  # cover flowables unused; cover is canvas-drawn
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_fr], onPage=lambda c,dc:_cover(c,dc,d)),
        PageTemplate(id="page",  frames=[fr],       onPage=lambda c,dc:_footer(c,dc,d)),
    ])
    story=[Spacer(1,1)]
    from reportlab.platypus import NextPageTemplate
    story.insert(0, NextPageTemplate("page"))
    story.append(PageBreak())
    for sec in d["sections"]:
        kind=sec[0]
        if kind=="h1": story.append(GoldBar(sec[1]))
        elif kind=="h2": story.append(P(sec[1],"h2"))
        elif kind=="p": story.append(P(sec[1]))
        elif kind=="small": story.append(P(sec[1],"small"))
        elif kind=="spacer": story.append(Spacer(1, sec[1]*mm))
        elif kind=="pagebreak": story.append(PageBreak())
        elif kind=="route": story.append(RoutePanel(sec[1]))
        elif kind=="callout": story.append(callout(sec[1], *sec[2], label=sec[3] if len(sec)>3 else None))
        elif kind=="table":
            story.append(styled_table(sec[1], sec[2], sec[3]))
        elif kind=="photos":
            outdir_l = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "studywork")
            cells=[]; caps=[]
            for fn,cap in sec[1]:
                fp=os.path.join(outdir_l,fn)
                if os.path.exists(fp):
                    cells.append(RLImage(fp, width=(W-2*M-8*mm)/3, height=(W-2*M-8*mm)/3*2/3))
                    caps.append(P(cap,"small"))
            for i in range(0,len(cells),3):
                row_imgs=cells[i:i+3]; row_caps=caps[i:i+3]
                t=Table([row_imgs,row_caps], colWidths=[(W-2*M)/max(len(row_imgs),1)]*len(row_imgs))
                t.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
                                       ("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2),
                                       ("VALIGN",(0,0),(-1,-1),"TOP")]))
                story.append(t)
        elif kind=="mapshot":
            outdir_l = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "studywork")
            fp=os.path.join(outdir_l, sec[1])
            if os.path.exists(fp):
                story.append(RLImage(fp, width=W-2*M, height=(W-2*M)*0.56))
                story.append(P(sec[2],"small"))
        elif kind=="chips":
            row=[]
            for label,v in sec[1]:
                row.append(chip("%s - %s" % (label, v), VCOL.get(v, BLUE)))
            t=Table([row], colWidths=[(W-2*M)/len(row)]*len(row))
            t.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2)]))
            story.append(t)
    doc.build(story)
    return out

if __name__=="__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dossier_examples import DOSSIERS
    outdir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"assets","studywork")
    os.makedirs(outdir, exist_ok=True)
    for fname,data in DOSSIERS.items():
        p=build(data, os.path.join(outdir,fname))
        print("built", p)
