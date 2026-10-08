#!/bin/bash
# make_min.sh -- MINIFY-1 (David, 8 Oct 2026: "Please proceed" on the 6 Oct audit's F6, the app's first load).
#
#   bash ops/minify/make_min.sh <live_dir> <src_dir>
#
# Writes <live>/static/ms.min.js from <live>/static/ms.js: the same code with its comments and whitespace removed --
# no renaming, no rewriting -- about 367 KB over the wire instead of about 530 KB. The app's own page asks for it as
# /static/ms.js?v=N&m=1 (an nginx rule, migration 071); every other request still gets the readable ms.js, so drift
# checks, the FEA sensor and anyone reading the code see exactly the repo's file.
#
# The minifier is esbuild 0.24.0 linux-x64 from the npm registry (tarball integrity checked), vendored gzipped next to
# this script and verified against its SHA-256 before it runs. If anything fails, ms.min.js becomes a plain COPY of
# ms.js -- never a stale or broken file -- so the page always gets the code that was just placed.
set -u
LIVE="${1:?live dir}"; SRC="${2:?src dir}"
f="$LIVE/static/ms.js"; dst="$LIVE/static/ms.min.js"; tmp="$dst.tmp.$$"
[ -f "$f" ] || { echo "make_min: $f not found -- nothing written"; exit 1; }
mode=copy
BIN="$(mktemp /tmp/ms-esbuild.XXXXXX)"
SHA="$(awk '{print $1; exit}' "$SRC/ops/minify/esbuild-linux-x64.sha256" 2>/dev/null)"
if [ "${MS_MINIFY:-1}" = "1" ] && [ -n "$SHA" ] && gzip -dc "$SRC/ops/minify/esbuild-linux-x64.gz" > "$BIN" 2>/dev/null \
   && [ "$(sha256sum "$BIN" | awk '{print $1}')" = "$SHA" ]; then
    chmod 700 "$BIN"
    if "$BIN" "$f" --minify-whitespace --legal-comments=none --charset=utf8 --log-level=error > "$tmp" 2>/dev/null && [ -s "$tmp" ]; then
        b0=$(wc -c < "$f"); b1=$(wc -c < "$tmp")
        if [ "$b1" -lt "$b0" ] && [ "$b1" -gt $(( b0 / 4 )) ]; then mode=min; fi
    fi
else
    echo "make_min: minifier missing or failed its checksum -- serving a copy"
fi
rm -f "$BIN"
[ "$mode" = "min" ] || cp -f "$f" "$tmp" || { rm -f "$tmp"; echo "make_min: copy failed"; exit 1; }
chmod --reference="$f" "$tmp" 2>/dev/null; chown --reference="$f" "$tmp" 2>/dev/null
mv -f "$tmp" "$dst" || { rm -f "$tmp"; echo "make_min: could not place $dst"; exit 1; }
echo "make_min: $mode static/ms.js $(wc -c < "$f") -> static/ms.min.js $(wc -c < "$dst") bytes"
