#!/usr/bin/env python3
"""Independent PEER REVIEW runner — the second-vendor engineer (GPT-5.6) reads and reports.

ROLE MODEL (David's ruling, 31 Jul 2026, from his QA practice): every design review
carries five mandatory roles — QA, CM, Author (Engineer), Peer (another Engineer),
System Engineer. Mapped onto MarketSquare:

    Author (Engineer)  Claude — wrote the code/design under review
    Peer (Engineer)    GPT-5.6 — THIS RUNNER. Reads and reports; never edits.
    QA                 the executable machinery: regression ledger, BIT, audits
    CM                 STATUS.md / CHANGELOG.md / CHANGE_REGISTER.md + git history
    System Engineer    David — decides, integrates, veto anchor

The Peer breaks the Claude-audits-Claude correlated-blind-spot problem (vendor doc,
11 Jul 2026 — "roving auditor", access READ-ONLY). Findings land in
Records/PEER_REVIEW_<date>.md for David to bring back to the Author for discussion.
This script makes NO edits and holds no write access to anything but its own report.

USAGE
    python3 scripts/peer_review.py FILE [FILE ...]         review these files
    python3 scripts/peer_review.py --dry-run FILE ...      size the request, no call, $0
    python3 scripts/peer_review.py --model gpt-5.6-sol ... deep pass (default: terra)
  python3 scripts/peer_review.py --lens cost FILE ...    pick the review lens:
      design (default) | code | security | privacy | cost | operability |
      performance | maintainability | full
    python3 scripts/peer_review.py --focus "..." FILE ...  point the Peer at a question

KEY   OPENAI_API_KEY — env first, then /var/www/marketsquare/.env, then <repo>/.env.
COST  input capped (120 KB/file, 400 KB total, truncation marked in the report).
      Ballpark per review: Terra ~$0.02-0.06 · Luna ~10x less · Sol ~2.5x more.
Stdlib only — any session or machine can run it, exactly like the regression ledger.
Exit: 0 report written · 2 configuration problem · 3 API error.
"""
import json, os, sys, datetime, urllib.request, urllib.error

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PER_FILE_CAP = 120_000          # chars per file
TOTAL_CAP = 400_000             # chars across all files
DEFAULT_MODEL = "gpt-5.6-terra" # the Peer's default rig; luna = cheap pass, sol = deep pass
MAX_OUT = 16000   # reasoning models burn thinking tokens from this budget first —
                  # 4000 starved Terra to an empty reply (same class as the 17 Jul
                  # qwen3.5 finding on Scaleway). 16k leaves room to think AND answer.
# $/Mtok (in, out) — 30 Jul 2026 prices; used for the report's cost line only
PRICES = {"gpt-5.6-luna": (0.20, 1.20), "gpt-5.6-terra": (2.0, 12.0), "gpt-5.6-sol": (5.0, 30.0)}


# ── Review lenses — the Peer's charter is BASE + chosen lens. David's environment names
# design/code/config/compliance; the catalogue deliberately adds lenses beyond that list.
LENSES = {
 "design": "LENS: DESIGN. Judge the architecture and state models: can the stated rules be "
   "implemented from the stated state? Failure modes, unstated assumptions, contradictions "
   "between documents and code, simpler alternatives.",
 "code": "LENS: CODE. Line-level correctness: error handling, concurrency and races, resource "
   "leaks, injection and unsafe parsing, silent exception swallowing, API misuse, edge cases.",
 "security": "LENS: SECURITY. AuthN/AuthZ on every endpoint, secrets handling and leakage "
   "paths, input validation, SSRF/injection surfaces, abuse and enumeration, blast radius.",
 "privacy": "LENS: PRIVACY. POPIA/GDPR posture: what personal data flows where, retention, "
   "anonymisation guarantees and their failure modes, third-party exposure, jurisdiction.",
 "cost": "LENS: COST / FinOps. Unit economics in actual currency: cost per call and per 1,000 "
   "calls per provider lane from the supplied prices and token profiles; what each swap "
   "saves or costs; where silent cost drift can enter (retries, fallbacks, probes, verbose "
   "models); pricing risks (intro-price expiries, FX, vendor repricing); whether the cost "
   "rails actually bound worst-case spend; the cheapest SAFE configuration given the "
   "project's stability and golden-set rules. Show your arithmetic.",
 "operability": "LENS: OPERABILITY. One human operates this alone, no on-call team: can a "
   "fault be diagnosed from what is logged/alerted? Runbook completeness, alert fatigue, "
   "recovery steps, observability gaps, what breaks silently.",
 "performance": "LENS: PERFORMANCE. Latency budgets, timeout stacking across fallback chains, "
   "blocking calls in async paths, scalability bottlenecks, degradation under load.",
 "maintainability": "LENS: MAINTAINABILITY. Complexity, duplication, dead code, doc-vs-code "
   "drift, single-file monolith risks, what the next engineer will misunderstand.",
 "legal": "LENS: LEGAL / REGULATORY ASSESSMENT. You are assessing legal RESEARCH and CONTRACT "
   "DRAFTING, not code. Judge: (a) is each statutory citation real, correctly numbered and "
   "still in force as at August 2026 - name any citation you believe is wrong, superseded or "
   "invented; (b) is the consent model stated for each jurisdiction correct, especially the "
   "B2B / corporate-subscriber position; (c) does the extraterritorial analysis hold for a "
   "South African sender with no local establishment; (d) do the drafted contract clauses "
   "actually achieve what they claim under the named local law, and would any be void, "
   "unenforceable or counter-productive; (e) what material legal risk has the Author MISSED "
   "entirely. You are NOT giving legal advice or approval and must say so; you are a second "
   "independent reading whose value is catching what one lineage missed. Where you are "
   "uncertain, say uncertain - a confident wrong answer here is worse than an admitted gap.",
 "full": "LENS: FULL SWEEP. Apply ALL of the above lenses (design, code, security, privacy, "
   "cost, operability, performance, maintainability), prioritize findings by impact, and "
   "say which lens each finding came from.",
}

SYSTEM = """You are the PEER REVIEWER (a second, independent engineer) in a formal design
review. Another engineer (the Author) produced the material below; the System Engineer
(the human owner) will read your report and discuss it with the Author. You are a
different vendor's model than the Author, on purpose: your value is the blind spots a
single engineering lineage cannot see about itself.

Your charter:
- READ ONLY. You change nothing; you report.
- Judge the engineering: correctness, failure modes, unstated assumptions, security and
  cost exposure, simpler alternatives the Author may have missed, and internal
  contradictions between documents.
- Be concrete: cite the file and the passage you mean. No generic advice.
- Severity-tag every finding: BLOCKER / MAJOR / MINOR / QUESTION / PRAISE.
  QUESTIONs are first-class — a sharp question is often the most valuable finding.
- Disagree openly where you disagree, and say why. Do not defer to the Author.
- End with: (1) the three findings the System Engineer should discuss first,
  (2) an honest statement of what you could NOT verify from the material given.
Format the whole report in clean Markdown."""


def envkey(name):
    v = os.getenv(name)
    if v:
        return v
    for envfile in ("/var/www/marketsquare/.env", os.path.join(REPO, ".env")):
        try:
            with open(envfile, encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln.startswith(name + "="):
                        return ln.split("=", 1)[1].strip()
        except OSError:
            pass
    return None


def read_scope(paths):
    blocks, meta, total = [], [], 0
    for p in paths:
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError as e:
            print(f"cannot read {p}: {e}"); sys.exit(2)
        clipped = False
        if len(src) > PER_FILE_CAP:
            src, clipped = src[:PER_FILE_CAP], True
        if total + len(src) > TOTAL_CAP:
            src, clipped = src[: max(0, TOTAL_CAP - total)], True
        total += len(src)
        meta.append((p, len(src), clipped))
        blocks.append(f"===== FILE: {p}{' [TRUNCATED at cap]' if clipped else ''} =====\n{src}")
        if total >= TOTAL_CAP:
            break
    return "\n\n".join(blocks), meta, total


def main():
    args = [a for a in sys.argv[1:]]
    dry = "--dry-run" in args
    model, focus = DEFAULT_MODEL, ""
    lens = "design"
    if "--lens" in args:
        lens = args[args.index("--lens") + 1]
        if lens not in LENSES:
            print("unknown lens %r — choose from: %s" % (lens, ", ".join(LENSES))); sys.exit(2)
        del args[args.index("--lens"): args.index("--lens") + 2]
    if "--model" in args:
        model = args[args.index("--model") + 1]
        del args[args.index("--model"): args.index("--model") + 2]
    if "--focus" in args:
        focus = args[args.index("--focus") + 1]
        del args[args.index("--focus"): args.index("--focus") + 2]
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print(__doc__); sys.exit(2)

    corpus, meta, total = read_scope(paths)
    est_in = total // 4 + 600
    p_in, p_out = PRICES.get(model, PRICES[DEFAULT_MODEL])
    est_cost = est_in / 1e6 * p_in + MAX_OUT / 1e6 * p_out
    scope_lines = "\n".join(f"  - {p} ({n:,} chars{' TRUNCATED' if c else ''})" for p, n, c in meta)
    print(f"Peer review scope ({model} · lens={lens}):\n{scope_lines}\n"
          f"  ~{est_in:,} input tokens · cost ceiling ≈ ${est_cost:.3f}")

    if dry:
        print("--dry-run: no API call made, nothing written."); sys.exit(0)

    key = envkey("OPENAI_API_KEY")
    if not key:
        print("OPENAI_API_KEY not found (env, server .env, repo .env) — the Peer lane "
              "needs its key. See AI_VENDOR_STRATEGY_DECISION Addendum 5/6."); sys.exit(2)

    user = ("Material under review follows. "
            + (f"The Author asks the Peer to focus on: {focus}\n\n" if focus else "")
            + corpus)
    body = {"model": model, "max_completion_tokens": MAX_OUT,
            "messages": [{"role": "system", "content": SYSTEM + "\n\n" + LENSES[lens]},
                         {"role": "user", "content": user}]}
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"API error {e.code}: {e.read().decode()[:400]}"); sys.exit(3)
    except Exception as e:
        print(f"API call failed: {e!r}"); sys.exit(3)

    text = (resp.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
    if not text:
        u = resp.get("usage", {})
        print("Empty reply from the Peer — nothing written. Usage:", u.get("prompt_tokens"),
              "in /", u.get("completion_tokens"), "out — if 'out' is large, the model spent the whole "
              "budget reasoning; raise MAX_OUT."); sys.exit(3)
    u = resp.get("usage", {})
    cost = (u.get("prompt_tokens", 0) / 1e6 * p_in) + (u.get("completion_tokens", 0) / 1e6 * p_out)

    os.makedirs(os.path.join(REPO, "Records"), exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    out_path = os.path.join(REPO, "Records", f"PEER_REVIEW_{stamp}_{lens}.md")
    header = (f"# Independent Peer Review — {stamp}\n\n"
              f"*Peer: {model} (second vendor, read-only) · Lens: {lens} · Author: Claude · "
              f"System Engineer: David*\n\n"
              f"**Scope:**\n{scope_lines}\n\n"
              f"**Usage:** {u.get('prompt_tokens','?')} in / {u.get('completion_tokens','?')} out "
              f"tokens · actual cost ≈ ${cost:.4f}\n\n---\n\n")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(header + text + "\n")
    print(f"Report written: {out_path}  (${cost:.4f})")
    sys.exit(0)


if __name__ == "__main__":
    main()
