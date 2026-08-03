#!/usr/bin/env bash
# Smoke driver for the "marta" static site (GitHub Pages).
# Serves the repo over HTTP, screenshots each page with headless Chromium,
# and asserts the client-side JS rendered its data. Exits non-zero on failure.
#
# Usage:  bash .claude/skills/run-marta/smoke.sh
# Screenshots + DOM dumps land in $OUT (default: ./.smoke-out).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"   # repo root (unit dir)
PORT="${PORT:-8000}"
OUT="${OUT:-$ROOT/.smoke-out}"
CHROME="${CHROME:-/opt/pw-browsers/chromium-1194/chrome-linux/chrome}"
mkdir -p "$OUT"

[ -x "$CHROME" ] || { echo "FAIL: chromium not found at $CHROME (set \$CHROME)"; exit 1; }

python3 -m http.server "$PORT" --directory "$ROOT" >"$OUT/httpd.log" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 1.5

shot() { # url slug -> screenshot + dom dump
  local url="$1" slug="$2"
  "$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
    --virtual-time-budget=6000 --window-size=1280,1700 \
    --screenshot="$OUT/$slug.png" "$url" 2>/dev/null
  "$CHROME" --headless=new --no-sandbox --disable-gpu --virtual-time-budget=6000 \
    --dump-dom "$url" 2>/dev/null > "$OUT/$slug.dom.html"
}

assert() { # needle file label
  if grep -q "$1" "$2"; then echo "  ok: $3"; else echo "  FAIL: $3 ($1 not in $2)"; exit 1; fi
}

BASE="http://localhost:$PORT"

echo "[1/3] home (tiles)"
shot "$BASE/index.html" home
assert 'href="restauracje/index.html"' "$OUT/home.dom.html" "Restauracje tile"
assert 'href="low-fodmap/index.html"'  "$OUT/home.dom.html" "Low FODMAP tile"

echo "[2/3] restauracje browser (JS-rendered cards)"
shot "$BASE/restauracje/index.html" restauracje
assert 'z 224 restauracji' "$OUT/restauracje.dom.html" "restaurant count text"
N=$(grep -o 'class="r-card"' "$OUT/restauracje.dom.html" | wc -l)
[ "$N" -ge 100 ] && echo "  ok: $N restaurant cards rendered" || { echo "  FAIL: only $N cards"; exit 1; }
# menu fetch dependency: .md must be served raw (needs .nojekyll on Pages)
curl -fs "$BASE/restauracje/wilanow/kuchnia-polska/restauracja-wilanow.md" | grep -q 'Low FODMAP\|low FODMAP\|Menu' \
  && echo "  ok: menu .md served (modal fetch works)" || { echo "  FAIL: menu .md not served"; exit 1; }

echo "[3/3] low-fodmap (JS-rendered food finder)"
shot "$BASE/low-fodmap/index.html" low-fodmap
assert 'class="food ' "$OUT/low-fodmap.dom.html" "food items rendered"

echo "PASS — screenshots in $OUT"
