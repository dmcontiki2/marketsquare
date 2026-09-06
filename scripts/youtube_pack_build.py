#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
youtube_pack_build.py -- build the YouTube upload package for each finished
feature film (the /youtube-pack skill, made repeatable).

WHY THIS EXISTS: film 01's package was hand-built on 6 Sep 2026 and the other
nine were not, so a weekly posting cadence would have stalled on the first
Tuesday. One script, ten packages, same shape every time.

EVERY link it writes carries ?src=yt-NN-name so GET /onboard/funnel?src=...
answers "did that film send anyone" -- RUL-096(b) scores the goal by probes,
never by guesses (CAMPAIGN-SRC-1 makes the app record it).

Run:  python3 scripts/youtube_pack_build.py [--only 05-car]
Writes: feature-videos/<folder>/<cut>_youtube/{metadata.md,thumbnail.jpg,frames/}
Reads nothing it does not own; never touches the film itself.
"""
import os, sys, json, subprocess, textwrap

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FV   = os.path.join(REPO, "feature-videos")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_I = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"

BOILER = (
"TrustSquare is a global marketplace where the seller stays anonymous until they accept an\n"
"introduction. Buyers see the item, the price and the seller's trust score — never a name, address\n"
"or phone number. Listing is free; the only fee is a small introduction fee paid by the person who\n"
"asks to be put in touch.")

# Everything below is READ OFF THE FILM (frame strip + the on-screen form) or off its
# script/VO on disk. No claim here that the film does not make.
FILMS = [
 # 01 was hand-packaged 6 Sep before this script existed; folded in here so all ten rebuild
 # from one place. Its report insert ALREADY shows both currencies (R42,500 · ~$2,574, and
 # per card R24,860 / $1,505) with the rate it used -- the app's own dual-currency report --
 # so the dollar figures below are the film's own, not a conversion invented here.
 dict(n="01", folder="01-collectables", cut="collectables-FINAL-4K-v3-03jul.mp4", dur=43.38,
   feature="Collectables Advert + Market Report", hold="5T", thumb_t=6.0,
   t1="SIX CARDS.", t2="$2,574.", t3="priced and listed in a minute",
   titles=[("Benefit-led","Six old Magic cards. $2,574. Priced and listed in a minute"),
           ("Curiosity-led","He thought they were worth nothing. One card was $1,505"),
           ("Search-led","Sell trading cards — real market prices, no guesswork")],
   hook=("Six real Magic: The Gathering cards, photographed on a phone, priced against the real market and\n"
         "listed as one collection — $2,574, with Gaea's Cradle alone at $1,505."),
   beats=["six cards to sell — “I need real prices, not guesses”","each card snapped on the phone",
          "the report: every card identified and valued","the top card, valued on its own",
          "listed as one collection","live, waiting for introductions"],
   tags=["trustsquare","sell trading cards","magic the gathering value","mtg card prices",
         "sell collectables online","online marketplace","vintage cards worth","gaea's cradle price",
         "collectors marketplace","anonymous selling","trusted sellers","how much are my cards worth",
         "sell mtg collection","card collection valuation"],
   pinned="What is the one collectable you have kept \"just in case it is worth something\"? Tell us what it is and we will tell you what the market says.",
   hashtags="#TrustSquare #MagicTheGathering #Collectables #SellOnline #TradingCards"),

 dict(n="02", folder="02-heritage", cut="heritage-FINAL-4K-v3-03jul.mp4", dur=48.77,
   feature="Heritage Site Tour Planner", hold="5T", thumb_t=3.0,
   t1="A PROPER TOUR.", t2="$1,600 · 7 DAYS", t3="route, stays and costs, planned",
   titles=[("Benefit-led","Cape Town to Kruger, planned in one go — stays and all"),
           ("Curiosity-led","“I want to see Kruger. Properly, this time.”"),
           ("Search-led","Plan a Kruger trip from Cape Town — route, stops, costs")],
   hook=("A Cape Town couple wanted Kruger done properly. The planner mapped the whole route via\n"
         "Graskop — every overnight stop, every lodging link, the whole trip costed."),
   beats=["the ask — “we need a proper tour”","he opens the Heritage Tour Planner",
          "sites, dates, travellers, budget — $1,600 for two, 7 days","the route: Cape Town → Kruger via Graskop",
          "every stay arranged, full cost estimate","“that was easy”"],
   tags=["trustsquare","kruger national park trip","how to plan a trip","panorama route graskop",
         "cape town to kruger","road trip planner","heritage sites south africa",
         "holiday planning app","travel itinerary planner","online marketplace",
         "trip cost estimate","self drive kruger","tour planning ai","trusted sellers"],
   pinned="Which South African heritage site have you always meant to see properly and never got to?",
   hashtags="#TrustSquare #Kruger #SouthAfrica #TravelPlanning #RoadTrip"),

 dict(n="03", folder="03-expedition", cut="expedition-FINAL-4K-v5-04jul.mp4", dur=45.40,
   feature="Expedition Dossier", hold="5T", thumb_t=2.7,
   t1="SIBERIA. FROM PRETORIA.", t2="$5,000 · 2 WEEKS", t3="visas, agencies, routes, real costs",
   titles=[("Benefit-led","The trip of a lifetime, planned like you have done it before"),
           ("Curiosity-led","“Siberia. Visas, agencies, costs — where do I even start?”"),
           ("Search-led","Siberia on a South African passport — visas, routes, costs")],
   hook=("Lake Baikal in February on a South African passport. The dossier came back with the visa rules for\n"
         "that passport, vetted agencies, the route through Istanbul to Irkutsk, and what it really costs."),
   beats=["the dream on the wall map","he opens the Expedition Dossier",
          "destination, month, passport, budget — $5,000","the route map: Pretoria → Irkutsk, legs pinned",
          "visas, agencies, kit, safety, medical — the things you would never think to ask","“sorted”"],
   tags=["trustsquare","travel dossier","siberia travel","lake baikal trip","south african passport visa",
         "expedition planning","adventure travel","visa requirements south africans",
         "trip planning ai","travel research tool","once in a lifetime trip","independent travel planning",
         "travel to russia","travel costs breakdown"],
   pinned="What is the one trip you keep putting off because the planning looks impossible?",
   hashtags="#TrustSquare #Travel #Expedition #SouthAfrica #Baikal"),

 dict(n="04", folder="04-property", cut="property-FINAL-4K-v5-04jul.mp4", dur=45.33,
   feature="Property Area Dossier", hold="3T", thumb_t=2.5,
   t1="BEFORE YOU BUY.", t2="SCHOOLS · COMMUTE · COMPS", t3="know more than the agent",
   titles=[("Benefit-led","Know more than the agent before you view the house"),
           ("Curiosity-led","“The house looks perfect — but what is the area like?”"),
           ("Search-led","Check a Centurion house before you buy — area and price")],
   hook=("A young couple found a house in Centurion. Before viewing it they ran the area — sales comps,\n"
         "school ratings, the commute to work — and the report found two similar homes for less."),
   beats=["“is the price even fair?”","she opens the Property Area Dossier",
          "the listing, her work address, what matters — schools and fibre","area comps and whether the asking price holds up",
          "matching TrustSquare listings alongside it","“we know more than the agent now”"],
   tags=["trustsquare","buying a house","centurion property","property area research",
         "is the asking price fair","neighbourhood report","school ratings suburb","commute times pretoria",
         "first time home buyer","property comps","house hunting tips","property marketplace",
         "area dossier","before you buy checklist"],
   pinned="What would you most want to know about a suburb before you put in an offer?",
   hashtags="#TrustSquare #Property #Centurion #HouseHunting #SouthAfrica"),

 dict(n="05", folder="05-car", cut="car-FINAL-4K-v3-03jul.mp4", dur=42.47,
   feature="Car Purchase Dossier", hold="3T", thumb_t=2.5,
   t1="2019 HILUX.", t2="$26,000 ASKING", t3="is that a fair price?",
   titles=[("Benefit-led","Check the price and known faults before you view it"),
           ("Curiosity-led","“$26,000 for a 2019 Hilux — is that right?”"),
           ("Search-led","2019 Toyota Hilux 2.8 GD-6 — fair price and known faults")],
   hook=("A 2019 Hilux 2.8 GD-6 on 120,000 km, asking $26,000. The dossier gave the market band for exactly\n"
         "that spec, the known faults for that model-year, and a test-drive checklist written for that car."),
   beats=["“is the price right? what goes wrong with these?”","he opens the Car Purchase Dossier",
          "model, year, mileage, their asking price","the market band for exactly this spec",
          "known faults and a checklist for this car","“I am walking in prepared”"],
   tags=["trustsquare","2019 toyota hilux","hilux 2.8 gd6 problems","used car price check",
         "buying a used pickup","car inspection checklist","what is my car worth",
         "second hand car","test drive checklist","used car buying tips","car dossier",
         "vehicle marketplace","hilux review","avoid a bad used car"],
   pinned="What is the one thing you always check first on a used bakkie?",
   hashtags="#TrustSquare #Hilux #UsedCars #SouthAfrica #CarBuying"),

 dict(n="06", folder="06-retirement", cut="retirement-FINAL-4K-v3-03jul.mp4", dur=47.40,
   feature="Retirement Relocation Planner", hold="5T", thumb_t=35.0,
   t1="RETIRE TO PORTUGAL?", t2="THE D7 VISA PATH", t3="pension, healthcare, what it really costs",
   titles=[("Benefit-led","Retiring to Portugal: the visa, pension and real costs"),
           ("Curiosity-led","“What if we actually do it — retire to Portugal?”"),
           ("Search-led","D7 visa for South Africans — pension, healthcare, property")],
   hook=("A couple in their sixties asked whether Portugal is actually possible. The planner came back with the\n"
         "D7 passive income visa, what their pension is worth in euros, healthcare, and homes on the coast."),
   beats=["“pensions, visas, healthcare — it is a maze”","he opens the Retirement Relocation Planner",
          "citizenship, pension, capital, what they want — coast and healthcare","verdict: can this retirement work?",
          "the D7 visa, what the pension is worth in euros, property rules","the two of them, sea view, decided"],
   tags=["trustsquare","retire to portugal","d7 visa south africans","emigrate from south africa",
         "portugal retirement visa","pension abroad","cost of living portugal",
         "algarve retirement","healthcare portugal expats","retirement planning",
         "relocation planner","pension exchange rate","retire abroad","cascais living"],
   pinned="If you could retire anywhere tomorrow, where would it be — and what is stopping you?",
   hashtags="#TrustSquare #Portugal #Retirement #D7Visa #SouthAfrica"),

 dict(n="07", folder="07-liquidation", cut="liquidation-FINAL-4K-v5-04jul.mp4", dur=69.24,
   feature="Collection Liquidation Plan", hold="5T", thumb_t=3.0,
   t1="DAD'S WHOLE COLLECTION.", t2="INVENTORIED & VALUED", t3="what sells as a lot, what sells alone",
   titles=[("Benefit-led","An inherited collection, inventoried, valued and listed"),
           ("Curiosity-led","“I do not know what is here, never mind what it is worth”"),
           ("Search-led","Sell an inherited stamp and coin collection — South Africa")],
   hook=("A study full of a father's stamps and coins. Photograph the lot and the plan comes back: an inventory,\n"
         "honest valuations, what to sell as lots versus singly, and a drafted advert for every lot."),
   beats=["“I do not even know what is here”","he photographs the albums and loose lots",
          "the plan: inventory and valuations against the catalogues","sell strategy — lot splits, in order",
          "drafted adverts, one per lot","months of work, done"],
   tags=["trustsquare","selling inherited collection","stamp collection value",
         "coin collection valuation","union of south africa coins","first day covers value",
         "deceased estate collection","how to sell a collection","selling collectables",
         "estate clearance","stamp albums worth","selling collectables online","lot splitting",
         "collectors marketplace"],
   pinned="Has a collection ever landed in your lap with no idea what it was worth? What was in it?",
   hashtags="#TrustSquare #Collectables #Stamps #Coins #SouthAfrica"),

 dict(n="08", folder="08-weekend", cut="weekend-FINAL-4K-v3-03jul.mp4", dur=42.49,
   feature="Weekend Adventure Itinerary", hold="3T", thumb_t=2.5,
   t1="FRIDAY. NO PLAN.", t2="UNDER $60 FOR TWO", t3="a whole weekend, built in minutes",
   titles=[("Benefit-led","A whole Pretoria weekend planned for under $60 for two"),
           ("Curiosity-led","“It is Friday night and we have no plan. Again.”"),
           ("Search-led","Things to do in Pretoria this weekend — under $60 for two")],
   hook=("Friday night, no plan, under sixty dollars for two. The itinerary came back built from real\n"
         "Adventures listings in Pretoria — every stop one introduction away."),
   beats=["“no plan for the weekend. again.”","she opens the Weekend Adventure planner",
          "city, vibe, budget — outdoorsy, two of us, under $60","Saturday: hike and market, timed and costed",
          "the rest of the weekend, from real listings","daypacks on, out the door"],
   tags=["trustsquare","things to do in pretoria","weekend ideas","cheap weekend pretoria",
         "hiking near pretoria","weekend itinerary planner","budget weekend",
         "adventures pretoria","what to do this weekend","day trips gauteng","local experiences",
         "affordable outings","weekend plans","pretoria markets"],
   pinned="Best thing you have ever done in your city for under $30? Drop it below — we are collecting.",
   hashtags="#TrustSquare #Pretoria #WeekendPlans #SouthAfrica #ThingsToDo"),

 dict(n="09", folder="09-exam", cut="exam-study-plan-FINAL-4K-v4-03jul.mp4", dur=49.51,
   feature="Exam Study Plan", hold="3T", thumb_t=3.0,
   t1="FINALS IN SIX WEEKS.", t2="WEEK BY WEEK, WEIGHTED", t3="CAPS Maths and Physical Science",
   titles=[("Benefit-led","Six weeks to finals: a plan weighted like the real exam"),
           ("Curiosity-led","“Finals in six weeks, Ma. I do not know where to start.”"),
           ("Search-led","Matric study plan — CAPS Maths and Physical Science, 6 weeks")],
   hook=("Six weeks to matric finals and no idea where to start. The plan came back weighted the way the real\n"
         "exam is weighted — week by week, with official past papers and a trig tutor slotted into week three."),
   beats=["“six weeks. I do not know where to START.”","Mum: let TrustSquare build the plan",
          "curriculum, grade, subjects, exam date, city","the exam profile — how the papers are actually built",
          "diagnostics, week-by-week schedule, free past papers","a tutor pinned where it helps most"],
   tags=["trustsquare","matric study plan","caps maths grade 12","physical sciences matric",
         "nsc exam preparation","matric finals 2026","past papers south africa","study timetable",
         "matric tutor south africa","exam study tips","grade 12 revision","how to study for finals",
         "topic weightings caps","maths tutor pretoria"],
   pinned="Matrics — which subject is the one keeping you up at night? We will point you at the right help.",
   hashtags="#TrustSquare #Matric #StudyPlan #CAPS #SouthAfrica"),

 dict(n="10", folder="10-offer", cut="offer-FINAL-4K-v5-04jul.mp4", dur=43.10,
   feature="Offer Strategy Advisor", hold="2T", thumb_t=2.5,
   t1="SHOULD YOU PAY $280?", t2="OPENING · TARGET · WALK-AWAY", t3="know the play before you message",
   titles=[("Benefit-led","Price checked and an opening offer, before you message"),
           ("Curiosity-led","“Is $280 fair — and what do I even open with?”"),
           ("Search-led","Is $280 fair? A value check and a negotiation brief")],
   hook=("A guitar amp listed at $280. Before committing to an introduction he got a fair-value verdict and\n"
         "a negotiation brief: opening offer, target, walk-away number."),
   beats=["“is $280 fair? what do I open with?”","he points it at the listing",
          "the item and the question — fair price?","the fair-value verdict on that asking price",
          "opening offer, target, walk-away","now he requests the introduction"],
   tags=["trustsquare","negotiation tips","is this a fair price","guitar amp price","how to negotiate a price",
         "buying second hand","fair value check","opening offer strategy","haggling tips",
         "online marketplace","price check tool","second hand deals","walk away price","buyer tips"],
   pinned="What is the best deal you have ever talked someone down to? Opening offer and final price — go.",
   hashtags="#TrustSquare #Negotiation #SecondHand #SouthAfrica #BuyingTips"),
]

def mmss(sec):
    sec = int(round(sec)); return "%d:%02d" % (sec // 60, sec % 60)

def esc(t):
    return (t.replace("\\", r"\\\\").replace(":", r"\:").replace("'", r"’")
             .replace("%", r"\%"))

def _fit(draw, text, path, box_w, start_px, min_px=34):
    """Largest point size at or below start_px whose rendered width fits box_w.
    drawtext has no measuring, which is exactly how the first build cropped five
    covers -- so the cover is drawn with PIL, which can measure."""
    from PIL import ImageFont
    size = start_px
    while size > min_px:
        f = ImageFont.truetype(path, size)
        if draw.textlength(text, font=f) <= box_w:
            return f
        size -= 2
    return ImageFont.truetype(path, min_px)


def build_thumb(film, srcvid, outdir):
    """1080x1920 vertical cover: a frame from the film under a navy band with three
    lines, the same shape as film 01's hand-built cover. Text is auto-fitted."""
    from PIL import Image, ImageDraw
    tmp = os.path.join(outdir, "_frame.jpg")
    subprocess.run(["ffmpeg","-v","error","-ss",str(film["thumb_t"]),"-i",srcvid,"-frames:v","1",
                    "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                    "-q:v","2",tmp,"-y"], check=True)
    im = Image.open(tmp).convert("RGB")
    band_y, band_h, pad = 1440, 480, 44
    band = Image.new("RGB", (1080, band_h), (14, 32, 56))
    im.paste(Image.blend(im.crop((0, band_y, 1080, band_y + band_h)), band, 0.90), (0, band_y))
    d = ImageDraw.Draw(im)
    box = 1080 - 2 * pad
    rows = [(film["t1"], FONT_B, 78, (255, 255, 255), band_y + 62),
            (film["t2"], FONT_B, 78, (245, 197, 24), band_y + 178),
            (film["t3"], FONT_I, 50, (235, 240, 246), band_y + 312)]
    for text, fontpath, px, colour, y in rows:
        f = _fit(d, text, fontpath, box, px)
        d.text(((1080 - d.textlength(text, font=f)) / 2, y), text, font=f, fill=colour)
    out = os.path.join(outdir, "thumbnail.jpg")
    im.save(out, "JPEG", quality=88)
    os.rename(tmp, os.path.join(outdir, "frames", "cover_source.jpg"))
    return out


def build_frames(srcvid, dur, outdir):
    fr = os.path.join(outdir, "frames"); os.makedirs(fr, exist_ok=True)
    for frac in (0.06, 0.23, 0.40, 0.57, 0.74, 0.91):
        t = round(dur * frac, 2)
        subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",srcvid,"-frames:v","1",
                        "-vf","scale=540:-2","-q:v","4",
                        os.path.join(fr, "f%05.1f.jpg" % t),"-y"], check=True)

def metadata(film, src_tag):
    d = film["dur"]
    marks = [0.0, 0.20*d, 0.38*d, 0.55*d, 0.72*d, 0.88*d]
    beats = "\n".join("%s %s" % (mmss(m), b) for m, b in zip(marks, film["beats"]))
    titles = "\n".join("%d. %-13s `%s`  (%d)" % (i+1, k+":", t, len(t))
                       for i, (k, t) in enumerate(film["titles"]))
    link = "https://trustsquare.co/?src=%s" % src_tag
    return u"""# YouTube upload package — {n} · {feature} (Short)

Upload this file: `{upload}` · {dursec} s · 2160×3840 vertical · h264 + aac
Format: **YouTube Short** (vertical). Shorts take their cover from a frame you pick in the upload
screen on the phone; `thumbnail.jpg` (1080×1920) is that frame with the overlay, for use where a
custom cover is accepted (Shorts on mobile, X, Instagram).
Built {built} by `scripts/youtube_pack_build.py`. Beats read off a frame strip of the finished cut;
every figure below is one the film puts on screen. WHICH film goes first and the channel's
positioning are David's (RUL-103f).

**The link is tracked on purpose.** `?src={src}` is how GET /onboard/funnel?src={src} answers
"did this film send anyone" — the goal is scored by probes, never by guesses (RUL-096b). Do not
paste a bare trustsquare.co link in its place.

## Title — pick one (all ≤ 60 characters)

{titles}

## Description (first two lines are the only part most people see)

{hook}

{beats}

List free at {link}

{boiler}

{hashtags}

## Tags (comma-separated, {ntags})

{tags}

## Pinned comment  (post it, then pin it — a link here is far more visible than one in the description)

{pinned}

List yours free: {link}

## End-screen / closing line

On-screen text over the last 3 seconds: **trustsquare.co — list it free**.

## Publish slot

Shorts are discovered, not scheduled, so the slot matters less than for long-form; if a slot is
wanted: Tuesday 18:00 SAST (evening phone time in ZA; Tuesday morning in the US eastern time).
""".format(n=film["n"], feature=film["feature"], upload=film.get("upload_name", film["cut"]),
           dursec=int(round(film["dur"])),
           built="6 Sep 2026", src=src_tag, titles=titles, hook=film["hook"], beats=beats,
           link=link, boiler=BOILER, hashtags=film["hashtags"],
           ntags=len(film["tags"]), tags=", ".join(film["tags"]), pinned=film["pinned"])

def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only")+1]
    made = []
    for film in FILMS:
        if only and film["folder"] != only:
            continue
        srcvid = os.path.join(FV, film["folder"], film["cut"])
        if not os.path.isfile(srcvid):
            print("MISSING film: %s" % srcvid); continue
        # DUAL-CURRENCY CUT (6 Sep 2026): where a -USD cut exists it IS the film we post --
        # same picture with the dollar figures added (scripts/usd_dual_patch.py). Package the
        # file that will actually be uploaded, so the cover frame comes from the real thing.
        usd = srcvid.replace(".mp4", "-USD.mp4")
        upload_name = os.path.basename(srcvid)
        if os.path.isfile(usd):
            srcvid = usd
            upload_name = os.path.basename(usd)
        film = dict(film, upload_name=upload_name)
        outdir = os.path.join(FV, film["folder"], film["cut"].replace(".mp4", "") + "_youtube")
        os.makedirs(os.path.join(outdir, "frames"), exist_ok=True)
        build_frames(srcvid, film["dur"], outdir)
        build_thumb(film, srcvid, outdir)
        tag = "yt-%s-%s" % (film["n"], film["folder"].split("-", 1)[1])
        md = metadata(film, tag)
        with open(os.path.join(outdir, "metadata.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(md)
        made.append((film["folder"], outdir, tag, len(md)))
        print("built %-14s -> %s (%d bytes md)" % (film["folder"], os.path.basename(outdir), len(md)))
    print("\n%d package(s) built" % len(made))

if __name__ == "__main__":
    main()
