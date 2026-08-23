const pptxgen = require("/tmp/pitch/node_modules/pptxgenjs");

// ── TrustSquare brand ────────────────────────────────────────────────
const NAVY = "111827", ACCENT = "1E3A5F", ICE = "EEF2F8", LINE = "E2E5EA";
const GOLD = "C9962E", GOLDBG = "FEF3C7", RUBY = "C0273C", GREEN = "065F46", GREENBG = "D1FAE5";
const MUTED = "5B6470", WHITE = "FFFFFF";
const HF = "Trebuchet MS", BF = "Calibri";
const QR = "/tmp/pitch/assets/qr.png";

let p = new pptxgen();
p.layout = "LAYOUT_16x9";
p.author = "TrustSquare";
p.title = "TrustSquare — Founding Agency Pitch (MASTER DRAFT)";

const W = 10, H = 5.625;

// helpers ─────────────────────────────────────────────────────────────
function spark(s, x, y, sz, color) {
  s.addShape(p.shapes.DIAMOND, { x, y, w: sz, h: sz, fill: { color: color || RUBY }, line: { type: "none" } });
}
function draftFooter(s, dark) {
  s.addText("INTERNAL DRAFT — do not circulate until the provisional patent is filed", {
    x: 0.5, y: H - 0.32, w: 6.4, h: 0.25, fontFace: BF, fontSize: 8.5, italic: true,
    color: dark ? GOLD : MUTED, align: "left", margin: 0 });
  s.addText("trustsquare.co", { x: W - 2.0, y: H - 0.32, w: 1.5, h: 0.25, fontFace: BF, fontSize: 8.5,
    color: dark ? "8FA3BF" : MUTED, align: "right", margin: 0 });
}
function titleBlock(s, kicker, title, dark) {
  s.addText(kicker.toUpperCase(), { x: 0.55, y: 0.34, w: 8.9, h: 0.3, fontFace: BF, fontSize: 11, bold: true,
    charSpacing: 3, color: dark ? GOLD : ACCENT, margin: 0 });
  s.addText(title, { x: 0.55, y: 0.62, w: 8.9, h: 0.75, fontFace: HF, fontSize: 30, bold: true,
    color: dark ? WHITE : NAVY, margin: 0 });
}
function card(s, x, y, w, h, glyph, glyphBg, glyphColor, head, body, opts = {}) {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.07, fill: { color: opts.bg || WHITE },
    line: { color: opts.line || LINE, width: 1 },
    shadow: { type: "outer", color: "1B2733", blur: 5, offset: 2, angle: 135, opacity: 0.10 } });
  s.addShape(p.shapes.OVAL, { x: x + 0.22, y: y + 0.22, w: 0.46, h: 0.46, fill: { color: glyphBg }, line: { type: "none" } });
  s.addText(glyph, { x: x + 0.22, y: y + 0.22, w: 0.46, h: 0.46, fontSize: 17, align: "center", valign: "middle",
    color: glyphColor, margin: 0, fontFace: BF });
  s.addText(head, { x: x + 0.22, y: y + 0.78, w: w - 0.44, h: 0.32, fontFace: HF, fontSize: 13.5, bold: true,
    color: NAVY, margin: 0 });
  s.addText(body, { x: x + 0.22, y: y + 1.10, w: w - 0.44, h: h - 1.30, fontFace: BF, fontSize: 11,
    color: MUTED, margin: 0, valign: "top" });
}
function stat(s, x, y, w, num, label, color) {
  s.addText(num, { x, y, w, h: 0.75, fontFace: HF, fontSize: 40, bold: true, color: color || ACCENT, align: "center", margin: 0 });
  s.addText(label, { x, y: y + 0.78, w, h: 0.5, fontFace: BF, fontSize: 11, color: MUTED, align: "center", valign: "top", margin: 0 });
}

// ── 1 · TITLE (dark) ─────────────────────────────────────────────────
let s = p.addSlide();
s.background = { color: NAVY };
spark(s, 0.55, 0.62, 0.30);
s.addText([{ text: "TRUST", options: { color: WHITE, bold: true } }, { text: "SQUARE", options: { color: GOLD, bold: true } }],
  { x: 0.98, y: 0.50, w: 4.5, h: 0.55, fontFace: HF, fontSize: 26, charSpacing: 2, margin: 0 });
s.addText("Your listings. Our buyers.\nZero fees. Forever.", {
  x: 0.55, y: 1.55, w: 8.9, h: 1.9, fontFace: HF, fontSize: 47, bold: true, color: WHITE, lineSpacing: 55, margin: 0 });
s.addText("The introduction marketplace for verified estate agencies", {
  x: 0.55, y: 3.55, w: 8.9, h: 0.4, fontFace: BF, fontSize: 17, color: "C7D2E3", margin: 0 });
const cities = ["Pretoria", "Johannesburg", "London", "New York", "Sydney"];
cities.forEach((c, i) => {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.55 + i * 1.62, y: 4.18, w: 1.48, h: 0.42, rectRadius: 0.21,
    fill: { color: "1B2A44" }, line: { color: "31415E", width: 1 } });
  s.addText(c, { x: 0.55 + i * 1.62, y: 4.18, w: 1.48, h: 0.42, fontFace: BF, fontSize: 11.5, bold: true,
    color: "D8E2F0", align: "center", valign: "middle", margin: 0 });
});
draftFooter(s, true);

// ── 2 · THE PROBLEM (light) ──────────────────────────────────────────
s = p.addSlide(); s.background = { color: WHITE };
titleBlock(s, "The problem", "Property lead-gen taxes the agent three times");
card(s, 0.55, 1.65, 2.9, 2.7, "↗", "FEE2E2", RUBY, "Fees that only climb",
  "Portal subscriptions and premium placements rise every year — whether or not they sell a single mandate.");
card(s, 3.55, 1.65, 2.9, 2.7, "✉", "FEE2E2", RUBY, "Leads that aren't leads",
  "Anyone can click 'enquire'. Your agents burn hours qualifying browsers who were never buyers.");
card(s, 6.55, 1.65, 2.9, 2.7, "⛁", "FEE2E2", RUBY, "Your data, their asset",
  "Your mandates and your buyer interest become the portal's product — sold back to you and your competitors.");
s.addText("TrustSquare was designed from a blank page to remove all three.", {
  x: 0.55, y: 4.6, w: 8.9, h: 0.4, fontFace: HF, fontSize: 15, italic: true, color: ACCENT, margin: 0 });
draftFooter(s);

// ── 3 · THE MODEL (light) ────────────────────────────────────────────
s = p.addSlide(); s.background = { color: WHITE };
titleBlock(s, "The model", "We monetise buyer intent — never your inventory");
stat(s, 0.55, 1.8, 2.9, "$0", "listing fees — every listing, every tier, forever", GREEN);
stat(s, 3.55, 1.8, 2.9, "$0", "commission — your fee stays 100% yours", GREEN);
stat(s, 6.55, 1.8, 2.9, "$2", "paid by the BUYER to be introduced to you", ACCENT);
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 3.45, w: 8.9, h: 1.35, rectRadius: 0.07,
  fill: { color: ICE }, line: { color: LINE, width: 1 } });
s.addText([
  { text: "How the money flows:  ", options: { bold: true, color: NAVY } },
  { text: "a buyer pays a small introduction fee only when an introduction actually happens. The agency pays nothing to list, nothing to be found and nothing on success. Revenue scales with buyer demand for ", options: { color: "374151" } },
  { text: "your", options: { italic: true, color: "374151" } },
  { text: " stock — so our incentive is identical to yours: serious buyers, fast.", options: { color: "374151" } }
], { x: 0.85, y: 3.62, w: 8.3, h: 1.0, fontFace: BF, fontSize: 12.5, margin: 0, valign: "top" });
draftFooter(s);

// ── 4 · QUALIFIED LEADS (light) ──────────────────────────────────────
s = p.addSlide(); s.background = { color: WHITE };
titleBlock(s, "Lead quality", "A buyer who pays to meet you is a buyer");
const steps = [
  ["1", "Buyer browses anonymously", "No contact details exposed — yours or theirs."],
  ["2", "Buyer pays $2 to request an introduction", "Payment is the qualification filter."],
  ["3", "You accept or decline", "You stay in control — a 48-hour response window keeps the market moving."],
  ["4", "Identities revealed on mutual accept", "Two parties who both chose the conversation."],
];
steps.forEach((t, i) => {
  const y = 1.62 + i * 0.82;
  s.addShape(p.shapes.OVAL, { x: 0.55, y: y + 0.06, w: 0.5, h: 0.5, fill: { color: ACCENT }, line: { type: "none" } });
  s.addText(t[0], { x: 0.55, y: y + 0.06, w: 0.5, h: 0.5, fontFace: HF, fontSize: 16, bold: true, color: WHITE,
    align: "center", valign: "middle", margin: 0 });
  s.addText([{ text: t[1] + "   ", options: { bold: true, color: NAVY, fontSize: 14 } },
             { text: t[2], options: { color: MUTED, fontSize: 12 } }],
    { x: 1.25, y, w: 5.6, h: 0.68, fontFace: BF, valign: "middle", margin: 0 });
});
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 7.15, y: 1.62, w: 2.3, h: 3.2, rectRadius: 0.07, fill: { color: NAVY }, line: { type: "none" } });
s.addText("No spam.\nNo tyre-kickers.\nNo cold lists.", { x: 7.35, y: 2.0, w: 1.9, h: 1.5, fontFace: HF, fontSize: 16,
  bold: true, color: WHITE, lineSpacing: 24, margin: 0 });
s.addText("Anonymity until mutual acceptance means nobody can scrape, spam or shortcut your pipeline.", {
  x: 7.35, y: 3.45, w: 1.9, h: 1.25, fontFace: BF, fontSize: 10.5, color: "C7D2E3", margin: 0, valign: "top" });
draftFooter(s);

// ── 5 · FREE AGENCY TIER (light) ─────────────────────────────────────
s = p.addSlide(); s.background = { color: WHITE };
titleBlock(s, "The agency tier", "Free for verified agencies — caps rise with trust, never with payment");
const ladder = [["10", "New agency", "verification in progress", 1.05, "B9C5D6"],
                ["100", "Verified", "identity + vertical credentials confirmed", 1.75, "6E87A8"],
                ["500", "Established", "verified + strong Trust Score · raised further on review", 2.45, ACCENT]];
ladder.forEach((L, i) => {
  const bw = 1.9, x = 0.7 + i * 2.15, bh = L[3], y = 4.45 - bh;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, rectRadius: 0.06, fill: { color: L[4] }, line: { type: "none" } });
  s.addText(L[0] + " listings", { x, y: y + 0.08, w: bw, h: 0.4, fontFace: HF, fontSize: 15, bold: true, color: WHITE, align: "center", margin: 0 });
  s.addText([{ text: L[1] + "\n", options: { bold: true, fontSize: 11.5, color: NAVY } },
             { text: L[2], options: { fontSize: 9.5, color: MUTED } }],
    { x: x - 0.1, y: 4.55, w: bw + 0.2, h: 0.62, fontFace: BF, align: "center", valign: "top", margin: 0 });
});
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 7.0, y: 1.62, w: 2.45, h: 3.0, rectRadius: 0.07, fill: { color: GOLDBG }, line: { color: "EAD9A8", width: 1 } });
s.addText("★", { x: 7.2, y: 1.8, w: 0.45, h: 0.45, fontSize: 20, color: GOLD, margin: 0 });
s.addText([{ text: "Trust Score on every card\n", options: { bold: true, fontSize: 12.5, color: NAVY } },
  { text: "Verification, credentials and track record build a 0–100 public score. 90+ earns the gold badge and featured priority — credibility your brand carries into every search result.", options: { fontSize: 10.5, color: "57534E" } }],
  { x: 7.2, y: 2.3, w: 2.05, h: 2.2, fontFace: BF, margin: 0, valign: "top" });
s.addText("The cap is the quality gate — it is never a paywall.", {
  x: 0.7, y: 4.92, w: 6.0, h: 0.32, fontFace: HF, fontSize: 13, italic: true, color: ACCENT, margin: 0 });
draftFooter(s);

// ── 6 · ZERO DATA ENTRY (light) ──────────────────────────────────────
s = p.addSlide(); s.background = { color: WHITE };
titleBlock(s, "Onboarding", "Bring your database. We do the rest.");
const flow = [["⇪", "Export", "The portal feed you already produce — Rightmove/Zoopla, MLS, REA-style XML or a simple spreadsheet."],
              ["⚙", "We load & format", "White-glove import by our team — titles, categories, pricing and photos structured for you."],
              ["♦", "Privacy scrub", "Location-revealing exteriors and identifying shots are removed by policy — vendor privacy by design."],
              ["✓", "You review · go live", "Nothing publishes until your team signs it off in the agency dashboard."]];
flow.forEach((f, i) => {
  const x = 0.55 + i * 2.28;
  card(s, x, 1.7, 2.08, 2.55, f[0], ICE, ACCENT, f[1], f[2]);
  if (i < 3) s.addText("→", { x: x + 2.06, y: 2.7, w: 0.26, h: 0.4, fontSize: 18, bold: true, color: "9AA7B8", align: "center", margin: 0 });
});
s.addText("Founding agencies get the full import service free — your stock live in week one, zero hours from your staff.", {
  x: 0.55, y: 4.5, w: 8.9, h: 0.5, fontFace: HF, fontSize: 14, italic: true, color: ACCENT, margin: 0 });
draftFooter(s);

// ── 7 · DAY-ONE WORLD (light) ────────────────────────────────────────
s = p.addSlide(); s.background = { color: WHITE };
titleBlock(s, "Launch footprint", "Five cities, four countries, one founding window each");
stat(s, 0.55, 1.7, 2.23, "5", "launch cities across ZA · UK · US · AU");
stat(s, 2.78, 1.7, 2.23, "332", "World Heritage sites as native browse content");
stat(s, 5.01, 1.7, 2.23, "11,679", "suburbs mapped in South Africa alone");
stat(s, 7.24, 1.7, 2.23, "7", "listing categories, Property first among equals");
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 3.35, w: 8.9, h: 1.5, rectRadius: 0.07, fill: { color: NAVY }, line: { type: "none" } });
spark(s, 0.85, 3.62, 0.32);
s.addText([{ text: "The founding window — the Ruby Spark.  ", options: { bold: true, color: WHITE, fontSize: 14 } },
  { text: "Each city opens one founding window. Verified agencies that join inside it mint the Ruby Spark badge — minted at launch, never minted again — plus founders' preferential terms for life. Early isn't a risk here; it's the prize.", options: { color: "C7D2E3", fontSize: 12 } }],
  { x: 1.35, y: 3.55, w: 7.9, h: 1.15, fontFace: BF, margin: 0, valign: "top" });
draftFooter(s);

// ── 8 · THE ASK (dark) ───────────────────────────────────────────────
s = p.addSlide(); s.background = { color: NAVY };
titleBlock(s, "The ask", "Become a founding agency", true);
const asks = [["30 minutes", "one working session with your listings lead"],
              ["Your export", "any feed or spreadsheet your system already produces"],
              ["Verification", "identity + your vertical's credentials — the quality gate"]];
asks.forEach((a, i) => {
  const x = 0.55 + i * 2.6;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.7, w: 2.4, h: 1.5, rectRadius: 0.07, fill: { color: "1B2A44" }, line: { color: "31415E", width: 1 } });
  s.addText(a[0], { x: x + 0.2, y: 1.88, w: 2.0, h: 0.4, fontFace: HF, fontSize: 16, bold: true, color: GOLD, margin: 0 });
  s.addText(a[1], { x: x + 0.2, y: 2.3, w: 2.0, h: 0.8, fontFace: BF, fontSize: 11, color: "C7D2E3", margin: 0, valign: "top" });
});
s.addText([{ text: "In return: ", options: { bold: true, color: WHITE } },
  { text: "day-one presence in your city, the Ruby Spark founding badge, white-glove import of your full book — at zero cost, on the tier that stays free forever.", options: { color: "C7D2E3" } }],
  { x: 0.55, y: 3.45, w: 6.3, h: 1.2, fontFace: BF, fontSize: 13.5, margin: 0, valign: "top" });
s.addImage({ path: QR, x: 8.35, y: 3.45, w: 1.35, h: 1.35 });
s.addText("trustsquare.co", { x: 8.2, y: 4.75, w: 1.65, h: 0.3, fontFace: BF, fontSize: 10.5, color: "C7D2E3", align: "center", margin: 0 });
draftFooter(s, true);

// ── 9–12 · CITY SLIDES (swappable) ───────────────────────────────────
const citySlides = [
  ["Gauteng — Pretoria & Johannesburg", "South Africa · launch wave 1 (twin cities)",
   "Our home market and deepest build: full national geo down to 11,679 suburbs, launch operations on the ground, and the founding wave running both metros as one corridor.",
   "Founding window opens: [DATE — Gauteng]"],
  ["London", "United Kingdom · launch wave 1",
   "Full UK geo live in-app. Founding agencies define the London launch book — first verified agencies anchor their boroughs before public open.",
   "Founding window opens: [DATE — London]"],
  ["New York", "United States · launch wave 1",
   "US geo live in-app. The founding window anchors Manhattan and the boroughs ahead of public open — Ruby Spark status is citywide and permanent.",
   "Founding window opens: [DATE — New York]"],
  ["Sydney", "Australia · launch wave 1",
   "AU geo live in-app. Founding agencies set the Sydney standard — verified, badged and loaded before the city opens to buyers.",
   "Founding window opens: [DATE — Sydney]"],
];
citySlides.forEach(C => {
  s = p.addSlide(); s.background = { color: WHITE };
  titleBlock(s, "Your city", C[0]);
  s.addText(C[1], { x: 0.55, y: 1.42, w: 8.9, h: 0.35, fontFace: BF, fontSize: 14, bold: true, color: GOLD, margin: 0 });
  s.addText(C[2], { x: 0.55, y: 1.95, w: 5.4, h: 1.35, fontFace: BF, fontSize: 13.5, color: "374151", margin: 0, valign: "top" });
  s.addText("Categories live day one: Property · Tutors · Services · Adventures · Collectors · Cars · Local Market — your vertical's aggregator seat is the Agency tier.", {
    x: 0.55, y: 3.35, w: 5.4, h: 0.85, fontFace: BF, fontSize: 11, color: MUTED, margin: 0, valign: "top" });
  s.addText("One founding window per city — it opens once, closes hard at the city's end date, and is never minted again.", {
    x: 0.55, y: 4.3, w: 5.4, h: 0.65, fontFace: HF, fontSize: 12.5, italic: true, color: ACCENT, margin: 0, valign: "top" });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 6.25, y: 1.95, w: 3.2, h: 2.95, rectRadius: 0.07, fill: { color: ICE }, line: { color: LINE, width: 1 } });
  spark(s, 6.5, 2.2, 0.28);
  s.addText([{ text: "Founding terms\n", options: { bold: true, fontSize: 13, color: NAVY } },
    { text: "Free agency tier — never a paywall\nRuby Spark founding badge\nFounders' preferential terms for life\nFull white-glove import included", options: { fontSize: 11, color: MUTED, lineSpacing: 17 } }],
    { x: 6.95, y: 2.12, w: 2.35, h: 1.95, fontFace: BF, margin: 0, valign: "top" });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 6.5, y: 4.18, w: 2.7, h: 0.5, rectRadius: 0.07, fill: { color: "DBE4F0" }, line: { type: "none" } });
  s.addText(C[3], { x: 6.62, y: 4.18, w: 2.5, h: 0.5, fontFace: HF, fontSize: 11.5, bold: true, color: ACCENT, margin: 0, valign: "middle" });
  draftFooter(s);
});

// ── 13 · APPENDIX: ECONOMICS ─────────────────────────────────────────
s = p.addSlide(); s.background = { color: WHITE };
titleBlock(s, "Appendix · economics", "Small fee, real intent — and only on delivery");
card(s, 0.55, 1.65, 4.3, 2.8, "T", "DBEAFE", "1D4ED8", "The introduction fee",
  "Buyers pay in Tuppence — 1T = $2. One introduction = 1T. Buyers are only charged when an introduction actually happens; a request that you decline costs them nothing and costs you nothing.");
card(s, 5.15, 1.65, 4.3, 2.8, "⌂", "DBEAFE", "1D4ED8", "Property gets exclusivity",
  "A property introduction pauses the listing while you engage — one serious buyer at a time, a 48-hour window, no parallel-bidding chaos. Service categories run a soft queue instead.");
s.addText("Buyer-side subscriptions and feature credits exist on the buyer side of the market — agencies never need them.", {
  x: 0.55, y: 4.65, w: 8.9, h: 0.4, fontFace: BF, fontSize: 11.5, italic: true, color: MUTED, margin: 0 });
draftFooter(s);

// ── 14 · APPENDIX: TRUST SCORE ───────────────────────────────────────
s = p.addSlide(); s.background = { color: WHITE };
titleBlock(s, "Appendix · trust", "The Trust Score — credibility, earned and visible");
const tiers = [["0–39", "New", "visible, building", "EEF2F8", NAVY],
               ["40–69", "Established", "blue badge", "DBEAFE", "1D4ED8"],
               ["70–89", "Trusted", "green badge", GREENBG, GREEN],
               ["90–100", "Highly Trusted", "gold badge + featured priority", GOLDBG, GOLD]];
tiers.forEach((t, i) => {
  const x = 0.55 + i * 2.28;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.7, w: 2.08, h: 1.7, rectRadius: 0.07, fill: { color: t[3] }, line: { color: LINE, width: 1 } });
  s.addText(t[0], { x: x + 0.18, y: 1.86, w: 1.75, h: 0.4, fontFace: HF, fontSize: 17, bold: true, color: t[4], margin: 0 });
  s.addText([{ text: t[1] + "\n", options: { bold: true, fontSize: 12.5, color: NAVY } },
             { text: t[2], options: { fontSize: 10.5, color: "4B5563" } }],
    { x: x + 0.18, y: 2.3, w: 1.75, h: 0.95, fontFace: BF, margin: 0, valign: "top" });
});
s.addText([{ text: "Three pillars: ", options: { bold: true, color: NAVY } },
  { text: "universal verification (identity, profile, referrals) · category credentials (your vertical's qualifications and registrations) · platform track record (introductions honoured, reliability, tenure). Agencies verify against their own vertical's credentials — an estate agency's gate looks nothing like a tutor college's, by design.", options: { color: "374151" } }],
  { x: 0.55, y: 3.7, w: 8.9, h: 1.1, fontFace: BF, fontSize: 12.5, margin: 0, valign: "top" });
draftFooter(s);

// ── 15 · APPENDIX: ONBOARDING TIMELINE ───────────────────────────────
s = p.addSlide(); s.background = { color: WHITE };
titleBlock(s, "Appendix · onboarding", "Mandate to market in one week");
const tl = [["Day 0", "Working session — we take your export"], ["Day 1–2", "Import, format & privacy scrub"],
            ["Day 3", "Your team reviews in the dashboard"], ["Day 4–5", "Verification completes — badge minted"], ["LIVE", "Your book is live for the founding window"]];
s.addShape(p.shapes.LINE, { x: 0.93, y: 2.8, w: 8.0, h: 0, line: { color: LINE, width: 2.5 } });
tl.forEach((t, i) => {
  const x = 1.0 + i * 1.95;
  s.addShape(p.shapes.OVAL, { x: x - 0.14, y: 2.66, w: 0.28, h: 0.28, fill: { color: i === 4 ? RUBY : ACCENT }, line: { color: WHITE, width: 2 } });
  s.addText(t[0], { x: x - 0.85, y: 2.05, w: 1.7, h: 0.4, fontFace: HF, fontSize: 14, bold: true, color: i === 4 ? RUBY : NAVY, align: "center", margin: 0 });
  s.addText(t[1], { x: x - 0.92, y: 3.1, w: 1.84, h: 1.0, fontFace: BF, fontSize: 10.5, color: MUTED, align: "center", valign: "top", margin: 0 });
});
s.addText("Zero hours from your staff beyond the review click.", {
  x: 0.55, y: 4.55, w: 8.9, h: 0.4, fontFace: HF, fontSize: 14, italic: true, color: ACCENT, align: "center", margin: 0 });
draftFooter(s);

// ── 16 · APPENDIX: PRIVACY & COMPLIANCE ──────────────────────────────
s = p.addSlide(); s.background = { color: WHITE };
titleBlock(s, "Appendix · privacy", "Privacy and compliance, by architecture");
card(s, 0.55, 1.65, 2.9, 2.75, "◎", GREENBG, GREEN, "Anonymity by design",
  "Buyer and seller identities are hidden until both sides accept an introduction. Nobody harvests your agents or your vendors.");
card(s, 3.55, 1.65, 2.9, 2.75, "♦", GREENBG, GREEN, "Vendor-safe media",
  "Location-revealing exteriors, entrances and signage are removed from imported photo sets by policy before anything publishes.");
card(s, 6.55, 1.65, 2.9, 2.75, "§", GREENBG, GREEN, "Per-market legal review",
  "POPIA/GDPR-aware data handling, and each market's outreach and category rules are reviewed with counsel before that market opens.");
draftFooter(s);

// ── 17 · CLOSE (dark) ────────────────────────────────────────────────
s = p.addSlide(); s.background = { color: NAVY };
spark(s, 0.55, 0.62, 0.30);
s.addText([{ text: "TRUST", options: { color: WHITE, bold: true } }, { text: "SQUARE", options: { color: GOLD, bold: true } }],
  { x: 0.98, y: 0.50, w: 4.5, h: 0.55, fontFace: HF, fontSize: 26, charSpacing: 2, margin: 0 });
s.addText("The market where your stock\nmeets buyers who mean it.", {
  x: 0.55, y: 1.7, w: 8.9, h: 1.6, fontFace: HF, fontSize: 38, bold: true, color: WHITE, lineSpacing: 46, margin: 0 });
s.addText("Founding windows: Pretoria · Johannesburg · London · New York · Sydney", {
  x: 0.55, y: 3.45, w: 8.9, h: 0.4, fontFace: BF, fontSize: 14, color: "C7D2E3", margin: 0 });
s.addImage({ path: QR, x: 0.55, y: 4.0, w: 1.1, h: 1.1 });
s.addText("trustsquare.co  ·  [contact — David]", { x: 1.8, y: 4.42, w: 5.5, h: 0.35, fontFace: BF, fontSize: 13, color: "C7D2E3", margin: 0 });
draftFooter(s, true);

p.writeFile({ fileName: "/tmp/pitch/TrustSquare_Agency_Pitch_MASTER_DRAFT_v1.pptx" })
  .then(() => console.log("DECK WRITTEN"));
