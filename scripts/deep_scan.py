#!/usr/bin/env python3
"""deep_scan.py — the Monday deep static scan, with its own tools.

DW-012 / DW-035 fix, 14 Aug 2026. For weeks the Monday lane reported "pylint and
eslint absent from sandbox and server", so a third of the scan never ran and the
gap was restated every Monday instead of being closed. The cause was that the
scan lived in a session's head: ruff and vulture were pip-installed ad hoc, and
whoever ran it had no way to get pylint or eslint, so those two were simply
skipped and written up as a limitation.

This script owns its own tooling. It bootstraps all four (pip for ruff/vulture/
pylint, a local npm prefix for eslint), runs them, and writes SCAN_REPORT.json.
A tool that cannot be installed is reported as UNAVAILABLE with the reason -- it
is never silently dropped, because a silently missing tool is the DW-024 class.

Usage:  python3 scripts/deep_scan.py [--json] [--no-bootstrap]
"""
import json, os, re, subprocess, sys, datetime, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
NODE_PREFIX = os.path.join(REPO, ".lintenv")
PY_TARGETS = ["bea_main.py", "auth.py", "database.py", "storage.py", "payments.py"]
JS_TARGETS = ["ms.js"]
REPORT = os.path.join(REPO, "SCAN_REPORT.json")

# Staged change-control copies, retired files and vendored trees are NOT live code.
# Scanning them produced 200+ phantom findings on the first run (the same lesson
# _to_delete/ taught the cost sweep in DW-018): a report padded with code that can
# never run teaches you to ignore the report.
EXCLUDE = ["_CCP_STAGED", "_to_delete", ".lintenv", "node_modules", ".git",
           "AUDIT_GLOBAL_QA", "_incoming", "venv", ".venv"]
EXCLUDE_GLOB = ",".join(f"{d}/**" for d in EXCLUDE) + ",**/*.bak-*"


def _excluded(path):
    return any(("/" + d + "/") in ("/" + path.replace(os.sep, "/")) or
               path.replace(os.sep, "/").startswith(d + "/") for d in EXCLUDE) \
           or ".bak-" in path


def run(cmd, timeout=600, cwd=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           cwd=cwd or REPO)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)


def bootstrap():
    """Install every tool. Returns {tool: version-or-None} and a reasons dict."""
    have, why = {}, {}

    for mod, pipname in (("ruff", "ruff"), ("vulture", "vulture"), ("pylint", "pylint")):
        rc, out, err = run([sys.executable, "-m", mod, "--version"], timeout=90)
        if rc != 0:
            run([sys.executable, "-m", "pip", "install", pipname,
                 "--break-system-packages", "-q"], timeout=600)
            rc, out, err = run([sys.executable, "-m", mod, "--version"], timeout=90)
        if rc == 0:
            have[mod] = out.strip().splitlines()[0] if out.strip() else "present"
        else:
            have[mod] = None
            why[mod] = (err or out).strip()[:200] or "pip install failed"

    # eslint: a global npm install is refused in this sandbox (EACCES), so use a
    # repo-local prefix. .lintenv is gitignored; it costs ~10s to rebuild.
    eslint_bin = os.path.join(NODE_PREFIX, "node_modules", ".bin", "eslint")
    if not os.path.exists(eslint_bin):
        if shutil.which("npm") is None:
            have["eslint"] = None; why["eslint"] = "npm not present on this machine"
            return have, why
        os.makedirs(NODE_PREFIX, exist_ok=True)
        run(["npm", "init", "-y"], timeout=180, cwd=NODE_PREFIX)
        run(["npm", "install", "eslint@9", "--no-audit", "--no-fund", "--silent"],
            timeout=900, cwd=NODE_PREFIX)
    if os.path.exists(eslint_bin):
        rc, out, err = run([eslint_bin, "--version"], timeout=90)
        have["eslint"] = out.strip() if rc == 0 else None
        if rc != 0:
            why["eslint"] = (err or out).strip()[:200]
    else:
        have["eslint"] = None
        why["eslint"] = "npm install eslint@9 did not produce node_modules/.bin/eslint"
    return have, why


def scan_ruff(findings):
    rc, out, _ = run([sys.executable, "-m", "ruff", "check", "--select", "F,E9,B",
                      "--exclude", ",".join(EXCLUDE),
                      "--output-format", "json", "."], timeout=600)
    try:
        for d in json.loads(out or "[]"):
            code = (d.get("code") or "?")
            # Crash-class means "this can actually blow up at runtime": syntax/runtime
            # errors (E9xx) and undefined/unbound names (F821/F822/F823). F841 (assigned
            # but unused) and F811 (redefinition) are tidiness, not crashes -- the first
            # cut of this mapping called them HIGH via a lazy startswith("F8") and
            # produced 9 fake crash-class hits. Exactly the vacuous-severity trap
            # RG-0068 exists to catch, so it is spelled out rather than pattern-matched.
            CRASH = {"F821", "F822", "F823"}
            findings.append({
                "tool": "ruff", "code": code,
                "sev": "HIGH" if (code.startswith("E9") or code in CRASH)
                       else ("MEDIUM" if code in ("F811", "F841") else "LOW"),
                "file": d.get("filename", "").replace(REPO + os.sep, ""),
                "line": (d.get("location") or {}).get("row"),
                "msg": d.get("message", ""),
            })
    except Exception as e:
        findings.append({"tool": "ruff", "code": "RUNNER", "sev": "INFO",
                         "file": "-", "line": None, "msg": f"ruff output unparseable: {e}"})


def scan_vulture(findings):
    rc, out, _ = run([sys.executable, "-m", "vulture", ".", "--min-confidence", "80",
                      "--exclude", EXCLUDE_GLOB], timeout=600)
    for ln in (out or "").splitlines():
        m = re.match(r"(.+?):(\d+): (.+?) \((\d+)% confidence\)", ln.strip())
        if m:
            findings.append({"tool": "vulture", "code": "DEAD", "sev": "LOW",
                             "file": m.group(1).replace(REPO + os.sep, ""),
                             "line": int(m.group(2)), "msg": m.group(3)})


def scan_pylint(findings):
    targets = [t for t in PY_TARGETS if os.path.exists(os.path.join(REPO, t))]
    if not targets:
        return
    rc, out, _ = run([sys.executable, "-m", "pylint", "--disable=all",
                      "--enable=cyclic-import,undefined-variable",
                      "--output-format=json"] + targets, timeout=900)
    try:
        for d in json.loads(out or "[]"):
            findings.append({"tool": "pylint", "code": d.get("symbol", "?"),
                             "sev": "HIGH" if d.get("type") == "error" else "MEDIUM",
                             "file": d.get("path", ""), "line": d.get("line"),
                             "msg": d.get("message", "")})
    except Exception as e:
        findings.append({"tool": "pylint", "code": "RUNNER", "sev": "INFO",
                         "file": "-", "line": None, "msg": f"pylint output unparseable: {e}"})


def scan_eslint(findings):
    eslint_bin = os.path.join(NODE_PREFIX, "node_modules", ".bin", "eslint")
    cfg = os.path.join(NODE_PREFIX, "eslint.config.mjs")
    # ms.js is browser script (not a module) with no build step: check for real
    # errors only -- undefined vars, unreachable code, duplicate keys, bad regex.
    if not os.path.exists(cfg):
        with open(cfg, "w", encoding="utf-8") as f:
            f.write("export default [{languageOptions:{ecmaVersion:2022,sourceType:'script'},"
                    "rules:{'no-dupe-keys':'error','no-unreachable':'error',"
                    "'no-dupe-args':'error','no-invalid-regexp':'error',"
                    "'no-cond-assign':'error','no-func-assign':'error',"
                    "'no-sparse-arrays':'error','use-isnan':'error'}}];\n")
    for t in JS_TARGETS:
        path = os.path.join(REPO, t)
        if not os.path.exists(path):
            continue
        rc, out, err = run([eslint_bin, "--no-config-lookup", "--config", cfg,
                            "-f", "json", path], timeout=900)
        try:
            for f in json.loads(out or "[]"):
                for m in f.get("messages", []):
                    findings.append({
                        "tool": "eslint", "code": m.get("ruleId") or "parse",
                        "sev": "HIGH" if m.get("severity") == 2 else "LOW",
                        "file": t, "line": m.get("line"), "msg": m.get("message", "")})
        except Exception as e:
            findings.append({"tool": "eslint", "code": "RUNNER", "sev": "INFO",
                             "file": t, "line": None,
                             "msg": f"eslint output unparseable: {e} / {err[:120]}"})


def main():
    as_json = "--json" in sys.argv
    have, why = ({}, {}) if "--no-bootstrap" in sys.argv else bootstrap()
    findings = []
    ran, unavailable = [], []
    for name, fn in (("ruff", scan_ruff), ("vulture", scan_vulture),
                     ("pylint", scan_pylint), ("eslint", scan_eslint)):
        if have.get(name):
            fn(findings); ran.append(f"{name} {have[name]}")
        else:
            unavailable.append({"tool": name, "reason": why.get(name, "not installed")})

    findings[:] = [f for f in findings if not _excluded(f.get("file") or "")]

    prev = {}
    try:
        prev = json.load(open(REPORT, encoding="utf-8"))
    except Exception:
        pass
    prev_keys = {(f.get("tool"), f.get("code"), f.get("file"), f.get("msg"))
                 for f in (prev.get("findings") or [])}
    for f in findings:
        f["new"] = (f["tool"], f["code"], f["file"], f["msg"]) not in prev_keys

    sev = {}
    for f in findings:
        sev[f["sev"]] = sev.get(f["sev"], 0) + 1
    report = {
        "schema_version": 2,
        "report_type": "deep_static_scan",
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
                         .isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generated_by": "scripts/deep_scan.py (DW-012/DW-035 fix, 14 Aug 2026)",
        "scan_scope": {"python": PY_TARGETS, "javascript": JS_TARGETS, "repo_wide": ["ruff", "vulture"]},
        "tools": ran,
        "tools_unavailable": unavailable,
        "totals": {"found": len(findings), "new_since_last": sum(1 for f in findings if f["new"]),
                   "crash_class": sev.get("HIGH", 0)},
        "severity_breakdown": sev,
        "findings": findings,
    }
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)

    if as_json:
        print(json.dumps({"status": "ok", "tools": ran, "unavailable": unavailable,
                          "totals": report["totals"]}))
    else:
        print(f"deep scan — {len(ran)}/4 tools ran: {', '.join(ran) or 'none'}")
        for u in unavailable:
            print(f"  UNAVAILABLE {u['tool']}: {u['reason']}")
        print(f"  {len(findings)} findings ({report['totals']['new_since_last']} new, "
              f"{sev.get('HIGH',0)} crash-class)")
        for f in [x for x in findings if x["new"]][:15]:
            print(f"   NEW [{f['sev']}] {f['tool']} {f['code']} {f['file']}:{f['line']} — {f['msg'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
