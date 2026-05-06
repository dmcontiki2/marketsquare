"""
session_dashboard.py
Reads project files, injects live data into session_dashboard.html,
and opens the result in the default browser.
Run by start_marketsquare.bat at session start.
"""

import os, re, json, subprocess, sys, webbrowser, tempfile
from datetime import datetime
import threading, http.server, socketserver

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

# Direction 1 — from Next Session priorities
if priority_items:
    directions.append({
        "id": "dir_next",
        "project": "TrustSquare",
        "title": f"Session {next_session} — Priority Queue",
        "colour": "#3b82f6",
        "items": priority_items[:5],
        "prompt": f"Read STATUS.md and AGENT_BRIEFING.md first — they are the source of truth.\n\nState: TrustSquare live at trustsquare.co · BEA v1.3.0 · Session {current_session} complete.\n\nSession {next_session} goal: {priority_items[0] if priority_items else 'Continue from STATUS.md'}\n\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(priority_items[:5]))
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
        "prompt": f"Read STATUS.md and AGENT_BRIEFING.md first — they are the source of truth.\n\nSession {next_session} goal: Clear launch blockers before public launch.\n\n" + "\n".join(f"- {b}" for b in blocker_clean[:4])
    })

# Direction 3 — CityLauncher
cl_next_items = [l[2:].strip() for l in cl_next.splitlines() if l.strip().startswith("- ")]
directions.append({
    "id": "dir_cl",
    "project": "CityLauncher",
    "title": f"CityLauncher — Session {cl_session}+",
    "colour": "#8b5cf6",
    "items": cl_next_items[:5] if cl_next_items else ["See CityLauncher STATUS.md"],
    "prompt": f"Read C:\\Users\\David\\Projects\\CityLauncher\\STATUS.md and AGENT_BRIEFING.md first.\n\nCityLauncher session goal: {cl_next_items[0] if cl_next_items else 'Continue from STATUS.md'}\n\n" + "\n".join(f"- {i}" for i in cl_next_items[:5])
})

# Direction 4 — AdvertAgent
directions.append({
    "id": "dir_aa",
    "project": "AdvertAgent",
    "title": "AdvertAgent — Kickoff",
    "colour": "#f59e0b",
    "items": ["Read PRINCIPLE_REQUIREMENTS.md Part G", "Define architecture and file map", "Session 1 kickoff — establish agent spec"],
    "prompt": "Read C:\\Users\\David\\Projects\\AdvertAgent\\STATUS.md, PRINCIPLE_REQUIREMENTS.md, and AGENT_BRIEFING.md first.\n\nAdvertAgent Session 1 goal: Kickoff — define architecture, file map, and agent spec based on PRINCIPLE_REQUIREMENTS.md Part G."
})

# Direction 5 — Agentic OS / Infrastructure
directions.append({
    "id": "dir_infra",
    "project": "Infrastructure",
    "title": "Agentic OS — Framework Setup",
    "colour": "#10b981",
    "items": ["Formalise branch structure across all projects", "Automate session end checklist", "Quarterly automation audit baseline", "Prepare GEX44 migration checklist for when volume justifies it"],
    "prompt": f"Read STATUS.md and AGENT_BRIEFING.md first.\n\nInfrastructure session goal: Formalise the Agentic OS framework — branch structure, automated session end checklist, and automation audit."
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

# Serve via local HTTP to avoid Chrome blocking file:// JavaScript
PORT = 7474
os.chdir(ROOT)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass  # suppress request logs

def start_server():
    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        httpd.serve_forever()

thread = threading.Thread(target=start_server, daemon=True)
thread.start()

import time; time.sleep(0.5)
url = f"http://localhost:{PORT}/session_dashboard_live.html"
webbrowser.open(url)
print(f"Dashboard opened — Session {next_session} ready → {url}")
time.sleep(2)  # keep process alive long enough for browser to fetch the file
