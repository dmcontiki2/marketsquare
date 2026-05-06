"""
session_dashboard.py
Reads project files, injects live data into session_dashboard.html,
and opens the result in the default browser.
Run by start_marketsquare.bat at session start.
"""

import os, re, json, subprocess, sys, webbrowser
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))

def read(filename, default=""):
    path = os.path.join(ROOT, filename)
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return f.read()

def section(content, heading_re):
    """Extract content under a heading until the next ## heading."""
    m = re.search(heading_re + r'\n(.*?)(?=\n## |\Z)', content, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""

def bullet_list(text):
    """Convert markdown bullet lines to list of strings."""
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- ") or line.startswith("* "):
            lines.append(line[2:].strip())
        elif line.startswith("### "):
            lines.append("__heading__" + line[4:])
        elif line and not line.startswith("#"):
            lines.append(line)
    return lines

# ── Parse STATUS.md ──────────────────────────────────────────
status = read("STATUS.md")
session_m = re.search(r'Session (\d+)', status)
current_session = int(session_m.group(1)) if session_m else 0
next_session = current_session + 1

live_state   = section(status, r'## Live State')
last_done    = section(status, r'## Last Completed[^\n]*')
next_goals   = section(status, r'## Next Session[^\n]*')
known_rules  = section(status, r'## Known Rules[^\n]*')

# ── Parse BACKLOG.md ─────────────────────────────────────────
backlog = read("BACKLOG.md")
blockers = section(backlog, r'## 🔴 Launch Blockers[^\n]*')
high_pri = section(backlog, r'## 🟠 High Priority[^\n]*')
medium   = section(backlog, r'## 🟡 Medium Priority[^\n]*')

# ── Parse CHANGELOG.md — last 2 sessions ─────────────────────
changelog = read("CHANGELOG.md")
cl_sessions = re.split(r'\n(?=## Session)', changelog)
recent_cl = cl_sessions[:2] if len(cl_sessions) >= 2 else cl_sessions

# ── CityLauncher STATUS ──────────────────────────────────────
cl_status = read(os.path.join("..", "CityLauncher", "STATUS.md"), "Not found")
cl_session_m = re.search(r'Session (\d+)', cl_status)
cl_session = cl_session_m.group(1) if cl_session_m else "?"
cl_last = section(cl_status, r'## Last Completed[^\n]*')
cl_next = section(cl_status, r'## Next[^\n]*')

# ── AdvertAgent STATUS ───────────────────────────────────────
aa_status = read(os.path.join("..", "AdvertAgent", "STATUS.md"), "Pre-kickoff")

# ── Build session direction cards ───────────────────────────
# Parse ### Priority items from next_goals
priority_items = []
for line in next_goals.splitlines():
    line = line.strip()
    if re.match(r'\d+\.', line):
        priority_items.append(re.sub(r'^\d+\.\s*', '', line))

directions = []

# ── Helper: plain-text summary of last_done (no markdown) ────
def plain(text, max_chars=300):
    t = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    t = re.sub(r'`([^`]+)`', r'\1', t)
    t = re.sub(r'^#+\s+', '', t, flags=re.MULTILINE)
    t = re.sub(r'\n{2,}', ' ', t)
    t = t.strip()
    return t[:max_chars] + ('…' if len(t) > max_chars else '')

last_done_plain   = plain(last_done)
next_goals_plain  = plain(next_goals, 400)
cl_last_plain     = plain(cl_last)
cl_next_plain     = plain(cl_next, 300)

# Direction 1 — from Next Session priorities
if priority_items:
    directions.append({
        "id": "dir_next",
        "project": "TrustSquare",
        "title": f"Session {next_session} — Priority Queue",
        "colour": "#3b82f6",
        "items": priority_items[:5],
        "prompt": f"Read STATUS.md and AGENT_BRIEFING.md first — they are the source of truth.\n\nState: TrustSquare live at trustsquare.co · BEA v1.3.0 · Session {current_session} complete.\n\nSession {next_session} goal: {priority_items[0] if priority_items else 'Continue from STATUS.md'}\n\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(priority_items[:5])),
        "mobile_prompt": f"You are helping with TrustSquare, a mobile-first local marketplace at trustsquare.co. No file access needed — all context is below.\n\nPLATFORM STATE (Session {current_session} complete):\n{plain(live_state)}\n\nLAST SESSION DONE:\n{last_done_plain}\n\nSESSION {next_session} PRIORITIES:\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(priority_items[:5])) + f"\n\nTask: Help me think through priority 1 — {priority_items[0] if priority_items else 'next steps'}. Ask me questions to clarify approach, flag risks, and suggest a plan."
    })

# Direction 2 — Launch blockers
blocker_items = [l[2:].strip() for l in blockers.splitlines() if l.strip().startswith("|") and "**" in l]
blocker_clean = []
for row in blockers.splitlines():
    if row.strip().startswith("|") and "**" in row:
        m = re.search(r'\*\*([^*]+)\*\*', row)
        if m:
            blocker_clean.append(m.group(1))
if blocker_clean:
    directions.append({
        "id": "dir_blockers",
        "project": "TrustSquare",
        "title": "Launch Blockers",
        "colour": "#ef4444",
        "items": blocker_clean[:4],
        "prompt": f"Read STATUS.md and AGENT_BRIEFING.md first — they are the source of truth.\n\nSession {next_session} goal: Clear launch blockers before public launch.\n\n" + "\n".join(f"- {b}" for b in blocker_clean[:4]),
        "mobile_prompt": f"You are helping with TrustSquare, a mobile-first local marketplace at trustsquare.co. No file access needed — all context is below.\n\nPLATFORM STATE:\n{plain(live_state)}\n\nLAUNCH BLOCKERS (must clear before public launch):\n" + "\n".join(f"- {b}" for b in blocker_clean[:4]) + "\n\nTask: Help me think through how to approach these blockers. Which should I tackle first and why?"
    })

# Direction 3 — CityLauncher
cl_next_items = [l[2:].strip() for l in cl_next.splitlines() if l.strip().startswith("- ")]
directions.append({
    "id": "dir_cl",
    "project": "CityLauncher",
    "title": f"CityLauncher — Session {cl_session}+",
    "colour": "#8b5cf6",
    "items": cl_next_items[:5] if cl_next_items else ["See CityLauncher STATUS.md"],
    "prompt": f"Read C:\\Users\\David\\Projects\\CityLauncher\\STATUS.md and AGENT_BRIEFING.md first.\n\nCityLauncher session goal: {cl_next_items[0] if cl_next_items else 'Continue from STATUS.md'}\n\n" + "\n".join(f"- {i}" for i in cl_next_items[:5]),
    "mobile_prompt": f"You are helping with CityLauncher, an autonomous city-launch pipeline for the TrustSquare marketplace. No file access needed — all context is below.\n\nLAST SESSION:\n{cl_last_plain}\n\nNEXT PRIORITIES:\n{cl_next_plain}\n\nTask: Help me think through the next steps for CityLauncher. Ask me what you need to give good advice."
})

# Direction 4 — AdvertAgent
directions.append({
    "id": "dir_aa",
    "project": "AdvertAgent",
    "title": "AdvertAgent — Kickoff",
    "colour": "#f59e0b",
    "items": ["Read PRINCIPLE_REQUIREMENTS.md Part G", "Define architecture and file map", "Session 1 kickoff — establish agent spec"],
    "prompt": "Read C:\\Users\\David\\Projects\\AdvertAgent\\STATUS.md, PRINCIPLE_REQUIREMENTS.md, and AGENT_BRIEFING.md first.\n\nAdvertAgent Session 1 goal: Kickoff — define architecture, file map, and agent spec based on PRINCIPLE_REQUIREMENTS.md Part G.",
    "mobile_prompt": "You are helping design AdvertAgent, a seller-facing AI assistance feature for TrustSquare marketplace. No file access needed — all context is below.\n\nADVERTAGENT PURPOSE:\nHelps sellers create better listings and manage introductions. Must preserve seller anonymity absolutely. Never calls Claude API without confirming active subscription.\n\nPLATFORM CONTEXT:\nTrustSquare is a mobile-first local marketplace using Tuppence introduction currency. Sellers are anonymous. Listings go through draft → tier picker → EULA → publish flow.\n\nTask: Help me design the AdvertAgent architecture — what components are needed, how it integrates with the platform, and what the Session 1 kickoff should deliver."
})

# Direction 5 — Agentic OS / Infrastructure
directions.append({
    "id": "dir_infra",
    "project": "Infrastructure",
    "title": "Agentic OS — Framework Setup",
    "colour": "#10b981",
    "items": ["Formalise branch structure across all projects", "Automate session end checklist", "Quarterly automation audit baseline", "Prepare GEX44 migration checklist for when volume justifies it"],
    "prompt": f"Read STATUS.md and AGENT_BRIEFING.md first.\n\nInfrastructure session goal: Formalise the Agentic OS framework — branch structure, automated session end checklist, and automation audit.",
    "mobile_prompt": f"You are helping with the Agentic OS framework for a multi-project Claude-powered development setup. No file access needed — all context is below.\n\nPROJECTS ACTIVE:\n- TrustSquare (Session {current_session} complete) — marketplace at trustsquare.co\n- CityLauncher (Session {cl_session}) — autonomous city launch pipeline\n- AdvertAgent — pre-kickoff, seller AI assistance\n\nCURRENT STATE:\n{plain(live_state)}\n\nTask: Help me think through how to formalise the Agentic OS framework — branch structure across projects, automated session end checklist, and quarterly automation audit baseline."
})

# ── Assemble data object ─────────────────────────────────────
data = {
    "generatedAt": datetime.now().strftime("%d %b %Y · %H:%M"),
    "currentSession": current_session,
    "nextSession": next_session,
    "liveState": live_state,
    "lastDone": last_done,
    "nextGoals": next_goals,
    "knownRules": known_rules,
    "recentChangelog": recent_cl[0][:800] if recent_cl else "",
    "blockers": blocker_clean,
    "highPriority": [re.search(r'\*\*([^*]+)\*\*', r).group(1) for r in high_pri.splitlines() if r.strip().startswith("|") and "**" in r][:6],
    "directions": directions,
    "clSession": cl_session,
    "clLast": cl_last[:300],
}

# ── Read template and inject ─────────────────────────────────
template_path = os.path.join(ROOT, "session_dashboard_template.html")
if not os.path.exists(template_path):
    print("ERROR: session_dashboard_template.html not found")
    sys.exit(1)

with open(template_path, encoding="utf-8") as f:
    html = f.read()

json_data = json.dumps(data, ensure_ascii=False)
html = html.replace("/*__DATA__*/null", json_data)

# Write to temp file and open
tmp = os.path.join(ROOT, "session_dashboard_live.html")
with open(tmp, "w", encoding="utf-8") as f:
    f.write(html)

# ── Open locally as file:// (data is fully inlined, no server needed) ──
os.startfile(tmp)
print(f"Dashboard opened — Session {next_session} ready")

# ── Upload to Hetzner so it's accessible from iPhone anywhere ──
SERVER = "root@178.104.73.239"
REMOTE_PATH = "/var/www/marketsquare/dashboard.html"
SSH_KEY = os.path.join(ROOT, "ssh_hetzner_key")

if os.path.exists(SSH_KEY):
    print("Uploading dashboard to server...", end=" ", flush=True)
    result = subprocess.run(
        ["scp", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
         tmp, f"{SERVER}:{REMOTE_PATH}"],
        capture_output=True, text=True, timeout=20
    )
    if result.returncode == 0:
        print("Done → trustsquare.co/dashboard.html")
    else:
        print(f"Upload failed: {result.stderr.strip()}")
else:
    print("SSH key not found — skipping server upload (run setup_sandbox_ssh.ps1 first)")
