#!/usr/bin/env python3
"""Detect Engine — gentle verifier (Orchestration v2, Phase 1).
Confirms whether URLs are REALLY dead vs just rate-limited / transient.
Low concurrency + retry, so the detector can't fool itself (the 5 Jun scanner flaw).

Usage:
  python3 detect_verify.py URL [URL ...]
  python3 detect_verify.py --file urls.txt
Prints one line per URL: OK / DEAD / TRANSIENT, then a summary.
"""
import sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

WORKERS = 5            # gentle — never hammer
TIMEOUT = 8
RETRIES = 2
DEAD_CODES = {404, 410}

def probe(url):
    last = None
    for attempt in range(RETRIES + 1):
        try:
            code = urllib.request.urlopen(
                urllib.request.Request(url, method='HEAD',
                    headers={'User-Agent': 'Mozilla/5.0 (detect-verify)'}),
                timeout=TIMEOUT).status
            if code == 200:        return (url, 'OK', code)
            if code in DEAD_CODES: return (url, 'DEAD', code)   # permanent = real
            last = code                                          # 429/5xx → retry
        except urllib.error.HTTPError as e:
            if e.code in DEAD_CODES: return (url, 'DEAD', e.code)   # 404/410 arrive as exceptions
            last = e.code                                          # 429/5xx → retry
        except Exception as e:
            last = e.__class__.__name__                            # timeout / DNS → retry
        time.sleep(0.6 * (attempt + 1))                          # back off, stay gentle
    return (url, 'TRANSIENT', last)   # never a clean 200 or permanent code → NOT counted dead

def main(urls):
    urls = [u.strip() for u in urls if u.strip()]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        rows = list(ex.map(probe, urls))
    dead  = [r for r in rows if r[1] == 'DEAD']
    trans = [r for r in rows if r[1] == 'TRANSIENT']
    for url, status, code in rows:
        print(f"{status:9} {code}  {url}")
    print(f"\n# {len(urls)} checked · {len(dead)} DEAD (real) · {len(trans)} transient (NOT counted as dead)")
    return dead

if __name__ == '__main__':
    a = sys.argv[1:]
    urls = open(a[1]).read().splitlines() if (a and a[0] == '--file') else (a or sys.stdin.read().splitlines())
    main(urls)
