#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_ria_discussion.py -- RIA-DISCUSSION-1 (14 Sep 2026).

Builds the discussion paper David asked for after the launch post-mortem: Claude's
suggestions as INPUT to the Council discussion on designing redundancy, independence
and accountability into TrustSquare. Professional Navy house style.

Regenerate rather than hand-edit the .docx, so the source of the argument stays in git.
"""
import os
from docx import Document
from docx.shared import RGBColor, Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY  = RGBColor(0x1F, 0x38, 0x64)
BLUE  = RGBColor(0x2F, 0x54, 0x96)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BODY  = RGBColor(0x26, 0x26, 0x26)
MUTED = RGBColor(0x59, 0x59, 0x59)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "Baseline Readiness - Redundancy, Independence, Accountability - "
                          "Discussion Input 2026-09-14 - nice.docx")


def shade(props, fill_hex):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), fill_hex)
    props.append(shd)


def divider(doc, color="BFBFBF", sz="6"):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr'); bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), sz)
    bottom.set(qn('w:space'), '1'); bottom.set(qn('w:color'), color)
    pbdr.append(bottom); pPr.append(pbdr)
    return p


def callout(doc, label, text, fill="EAF0FA", border="2F5496"):
    tbl = doc.add_table(rows=1, cols=1)
    cell = tbl.cell(0, 0)
    tcPr = cell._tc.get_or_add_tcPr()
    shade(tcPr, fill)
    borders = OxmlElement('w:tcBorders')
    for edge in ('top', 'bottom', 'right'):
        e = OxmlElement('w:%s' % edge)
        e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4'); e.set(qn('w:color'), 'D9D9D9')
        borders.append(e)
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single'); left.set(qn('w:sz'), '24'); left.set(qn('w:color'), border)
    borders.append(left); tcPr.append(borders)
    p = cell.paragraphs[0]
    r = p.add_run(label + "  "); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(11)
    b = p.add_run(text); b.font.name = "Calibri"; b.font.size = Pt(11); b.font.color.rgb = BODY
    doc.add_paragraph()
    return tbl


def body(doc, text, size=11, color=BODY, italic=False, space_after=8):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_after = Pt(space_after)
    r = p.add_run(text)
    r.font.name = "Calibri"; r.font.size = Pt(size); r.font.color.rgb = color; r.italic = italic
    return p


def bullets(doc, items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.space_after = Pt(4)
        if isinstance(it, tuple):
            r = p.add_run(it[0] + " "); r.bold = True; r.font.name = "Calibri"
            r.font.size = Pt(11); r.font.color.rgb = NAVY
            r2 = p.add_run(it[1]); r2.font.name = "Calibri"; r2.font.size = Pt(11)
            r2.font.color.rgb = BODY
        else:
            r = p.add_run(it); r.font.name = "Calibri"; r.font.size = Pt(11)
            r.font.color.rgb = BODY


def h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    r.font.name = "Calibri"; r.bold = True; r.font.size = Pt(24); r.font.color.rgb = NAVY
    divider(doc, color="1F3864", sz="24")


def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(6)
    r = p.add_run("▍ " + text)
    r.font.name = "Calibri"; r.bold = True; r.font.size = Pt(16); r.font.color.rgb = BLUE


def h3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.font.name = "Calibri"; r.bold = True; r.font.size = Pt(13); r.font.color.rgb = NAVY


def table(doc, headers, rows, widths=None):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.autofit = True
    for i, htxt in enumerate(headers):
        c = tbl.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(htxt)
        r.bold = True; r.font.color.rgb = WHITE; r.font.name = "Calibri"; r.font.size = Pt(10.5)
        shade(c._tc.get_or_add_tcPr(), "1F3864")
    for ri, row in enumerate(rows, start=1):
        cells = tbl.add_row().cells
        for ci, val in enumerate(row):
            cells[ci].text = ""
            p = cells[ci].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(str(val))
            r.font.name = "Calibri"; r.font.size = Pt(10); r.font.color.rgb = BODY
            if ci == 0:
                r.bold = True
        if ri % 2 == 0:
            for c in cells:
                shade(c._tc.get_or_add_tcPr(), "EAF0FA")
    # thin gray borders everywhere
    for row in tbl.rows:
        for c in row.cells:
            tcPr = c._tc.get_or_add_tcPr()
            borders = OxmlElement('w:tcBorders')
            for edge in ('top', 'bottom', 'left', 'right'):
                e = OxmlElement('w:%s' % edge)
                e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4')
                e.set(qn('w:color'), 'D9D9D9')
                borders.append(e)
            tcPr.append(borders)
    doc.add_paragraph()
    return tbl


def build():
    doc = Document()
    for s in doc.sections:
        s.left_margin = Inches(0.9); s.right_margin = Inches(0.9)
        s.top_margin = Inches(0.8); s.bottom_margin = Inches(0.8)

    h1(doc, "Baseline Readiness")
    body(doc, "Designing redundancy, independence and accountability into TrustSquare",
         size=13, color=BLUE)
    body(doc, "Claude's input to the Council discussion  ·  14 September 2026  ·  "
              "Discussion paper, not a decision", size=9.5, color=MUTED, italic=True)

    callout(doc, "★ The one sentence",
            "Every instrument we built measured our own machinery rather than a stranger's "
            "experience — a test our code passes proves the code ran, it never proves a "
            "stranger succeeded, and that is why a green board and a blocked launch were both "
            "true at the same time.")

    body(doc, "This paper is input, not a design. It sets out what the evidence actually shows, "
              "proposes testable meanings for your three words, and ends with the decisions that "
              "are yours rather than mine. Nothing here is a requirement until you make it one.")

    # 1 -----------------------------------------------------------------
    divider(doc)
    h2(doc, "1.  What actually happened")
    body(doc, "Eight findings, all probed on 14 September or recorded in the project's own "
              "registers. They are listed not as a complaint but because the pattern only "
              "becomes visible when they sit together.")
    table(doc,
          ["Finding", "What the board said", "What was true"],
          [
            ["Test accounts scored as customers",
             "5 onboarded, 2 published",
             "All five were our own end-to-end fixtures; none was ever emailed; zero real "
             "conversions, for six weeks"],
            ["Two dashboards disagreed",
             "1,569 emailed / 1,671 emailed",
             "Two correct answers to different questions, and neither surface knew the other "
             "existed"],
            ["Liveness check called a live agent dead",
             "“pending 125 min, task not registered or stopped”",
             "The agent had ticked 8 minutes earlier; the check was reading the wrong file"],
            ["Fact board depends on where it runs",
             "52 regressions from a clone",
             "Every one was “I cannot see this file” printed as “this fix has "
             "come back”"],
            ["Status panel blank by construction",
             "Heading fresh, compiler ran, fold succeeded",
             "The panel had been empty since 11 September; the block's own first line ended the "
             "section"],
            ["Agreement document self-contradicting",
             "Sync tool green for three weeks",
             "Header read v1.14 while the footer read v1.15 — the tool compared the copies "
             "to each other, never the header to the footer"],
            ["Outreach decayed in silence",
             "The wave ran every night",
             "398 sends a night fell to 87 with 3,941 people in the pool and no instrument "
             "reported the slope"],
            ["718 people unreachable by accident",
             "“Nobody to send to” in 15 cities",
             "Their category was never typed into their city's list; fifth instance of a fault "
             "class four earlier fixes had each closed by hand"],
          ])

    # 2 -----------------------------------------------------------------
    divider(doc)
    h2(doc, "2.  The diagnosis — three patterns, not eight bugs")
    bullets(doc, [
        ("Self-reference.", "Every check measured our own machinery: our fixtures, our "
         "documents, our logs — never a stranger completing a journey."),
        ("Shared assumption.", "A checker and the thing it checks inherited the same blind spot: "
         "the agreement tool compared three copies to each other, the freshness check compared a "
         "heading to a date, the liveness check read the work log."),
        ("Absence read as health.", "A blank panel, a missing file and a quiet log each rendered "
         "as green or as zero, and none of them could be told apart from the real thing."),
    ])
    callout(doc, "⚠️ Why more auditing would not have helped",
            "The audits and end-to-end reports existed and were run. They failed because they "
            "shared the three patterns above, not because there were too few of them. Adding a "
            "fourth audit of the same kind buys a fourth confirmation of the same blind spot.",
            fill="FFF4E5", border="C55A11")

    # 3 -----------------------------------------------------------------
    divider(doc)
    h2(doc, "3.  The three words, made testable")
    body(doc, "Redundancy, independence and accountability are not three names for reliability. "
              "They answer three different questions, and today the project fails each one in a "
              "different way.")

    h3(doc, "Redundancy — is there a second path, and has it been driven?")
    bullets(doc, [
        "A second path that has never been exercised is a belief, not a redundancy.",
        "Today with no second path: one outreach category with five nights of supply, one "
        "server, one sending provider, one payment provider, one deploy lane, one founder.",
        "Proposed test: every load-bearing capability has a named second path, a drill, a drill "
        "date and a recorded drill result — undrilled counts as absent.",
    ])

    h3(doc, "Independence — does the second opinion share any input with the first?")
    bullets(doc, [
        "This is the hard one, and the one most likely to be got wrong in practice.",
        "An auditor that reads our status files inherits our blind spot exactly: those documents "
        "were green throughout the bad launch.",
        "Proposed test: the Peer Auditor forms its readiness verdict using only what a stranger "
        "could obtain — the live site, a fresh account, the public interface — and is "
        "barred from our registers, our reports and our test data while forming it.",
        "Corollary: the auditor creates its own test data, because using ours reproduces exactly "
        "the fault that hid the zero.",
    ])

    h3(doc, "Accountability — whose name is on the verdict, and what happens when it is wrong?")
    bullets(doc, [
        "The reports that said “ready” had no author, no date of evidence and no cost "
        "when they turned out wrong.",
        "Proposed test: every readiness verdict carries who said it, on what evidence and on "
        "what date.",
        "Proposed consequence, and it is the important half: when a blocker appears after a green "
        "verdict, the instrument that missed it gets a fix in the same session — the rule "
        "the project already applies to bugs, raised to apply to verdicts.",
    ])

    # 4 -----------------------------------------------------------------
    divider(doc)
    h2(doc, "4.  A proposed gate — what “baseline ready” would have to mean")
    body(doc, "Six conditions. The common property is that none of them can be satisfied by our "
              "own machinery agreeing with itself.")
    table(doc,
          ["#", "Condition", "Would it pass today?"],
          [
            ["1", "A stranger completes the journey end to end on the live site, with data we "
                  "did not seed, and is not us.", "No — zero real signups from 1,671 emails"],
            ["2", "Every single point of failure has a named second path, drilled within an "
                  "agreed window.", "No — no register exists yet"],
            ["3", "The independent auditor returns green without reading our documents.",
             "Untested — the auditor has always read our documents"],
            ["4", "The adversarial pass finds nothing unmitigated above an agreed severity.",
             "Untested — no adversarial pass is defined"],
            ["5", "Every instrument that must fire has been proven to fire against a "
                  "deliberately broken case.", "Partly — done on a few checks, never "
                  "required"],
            ["6", "No number on the readiness board counts our own test data.",
             "Yes, since today — this was the six-week lie"],
          ])
    callout(doc, "★ Key takeaway",
            "Condition 5 already exists in the project's own practice — one check was "
            "deliberately broken first and proven red before it was believed green. Making that "
            "universal is the cheapest single change in this paper, and it is the one that would "
            "have caught most of section 1.")

    # 5 -----------------------------------------------------------------
    divider(doc)
    h2(doc, "5.  The Council — who does what, and why it is separable")
    body(doc, "Four opinions that all read the same repository is a chorus, not independence. "
              "The roles below are separated by what each one is ALLOWED to see, which is what "
              "makes them genuinely different voices.")
    table(doc,
          ["Member", "Role", "What it may see"],
          [
            ["Deepseek Harness", "Worker APIs — the repetitive verification labour: run the "
             "drills, repeat journeys from clean accounts, diff the outputs.",
             "Only the task and the live product; never our conclusions"],
            ["Design team", "Owns the stranger's experience and defines the journeys the gate is "
             "tested against.", "The product as a user meets it"],
            ["OpenAI — Peer Auditor", "Forms the independent readiness verdict.",
             "Outside evidence only — live site, fresh account, public interface"],
            ["Grok — Risk & Security", "Adversarial pass: tries to break it, not to confirm "
             "it.", "Full access, because attack needs it"],
            ["Claude — CTO", "The specification, the instruments, the registers and the "
             "memory that carries all of it between sessions.",
             "Everything — which is exactly why Claude may not also be the auditor"],
            ["David — +1", "Decides. Sets what the three words mean and what a red verdict "
             "does.", "Everything"],
          ])

    # 6 -----------------------------------------------------------------
    divider(doc)
    h2(doc, "6.  Honest risks in this design")
    bullets(doc, [
        ("Coordination cost is real.", "More members means more to maintain, and a solo founder "
         "pays that cost personally."),
        ("Independence is easy to lose quietly.", "The moment the auditor is handed our summary "
         "“to save time”, it stops being a second opinion and nobody will notice."),
        ("The auditor will look less productive.", "It will find fewer issues than an insider "
         "and they will be the ones that matter — judge it on blockers missed, never on "
         "volume."),
        ("Consumption-based worker APIs need a ceiling first.", "Rule B7 exists because of the "
         "Google billing incident; the ceiling is set before the first key is issued, not after "
         "the first invoice."),
        ("The largest single point of failure is not technical.", "It is one person, and an "
         "honest register has to say so even though the remedy is not a script."),
    ])

    # 7 -----------------------------------------------------------------
    divider(doc)
    h2(doc, "7.  Decisions reserved to you — the discussion agenda")
    body(doc, "These are the questions I have deliberately not answered. They set the "
              "specification that delegates technical authority, so answering them myself would "
              "put my guess into canon.")
    bullets(doc, [
        ("Scope.", "Does the gate apply to every deploy, or only to a baseline or major "
         "release?"),
        ("Force.", "Does a red verdict from the auditor STOP a release, or advise against it?"),
        ("Drill window.", "How recently must a second path have been exercised to count, and "
         "which failures are we content to leave undrilled?"),
        ("Budget.", "What hard monthly ceiling do the worker APIs get, and who is told when it "
         "is reached?"),
        ("The human stranger.", "My view is that at least one real person outside the project "
         "must complete the journey per baseline, because that is the only fully independent "
         "evidence — but that is a cost decision and therefore yours."),
    ])

    callout(doc, "→ Next step",
            "Bring this paper to the Council as the opening position, let the Peer Auditor and "
            "Risk attack it before it is refined, and make section 7 the agenda. Once you settle "
            "section 7, the rest becomes a build and the instruments can be written against it.",
            fill="E7F2E3", border="538135")

    body(doc, "Prepared by Claude as CTO input. Every figure in section 1 was measured on "
              "14 September 2026 against the live system, not recalled.",
         size=9.5, color=MUTED, italic=True)

    doc.save(OUT)
    print("written:", OUT)
    return OUT


if __name__ == "__main__":
    build()
