---
name: run-marta
description: Run, serve, preview, screenshot or smoke-test the "marta" static site (GitHub Pages) — the restaurant/low-FODMAP browser. Use when asked to run, start, launch, serve, preview, screenshot, or verify the marta site or its restauracje / low-fodmap pages.
---

# Run marta

`marta` is a **static, client-side site** (no build, no framework) published on
GitHub Pages. Three pages:

- `index.html` — landing with two tiles (Restauracje, Low FODMAP).
- `restauracje/index.html` — restaurant browser. JS embeds a `DATA` array of 224
  restaurants and renders cards; clicking a card **fetches the matching `.md`**
  menu file and renders it. Filters + search are pure client-side JS.
- `low-fodmap/index.html` — Low FODMAP guide with a JS-rendered food finder (115 items).

Because pages render their data with JavaScript and fetch `.md` files over HTTP,
you must serve the repo over `http://` (not open `file://`) and let JS run before
screenshotting. The driver below does exactly that.

All paths are relative to the repo root (the unit dir).

## Prerequisites

Everything is preinstalled in this container — **no `apt-get` needed**:

- `python3` (static file server)
- headless Chromium at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`
- `curl`

If Chromium lives elsewhere, pass `CHROME=/path/to/chrome`.

## Run (agent path) — the driver

```bash
bash .claude/skills/run-marta/smoke.sh
```

What it does: starts `python3 -m http.server` at the repo root, screenshots all
three pages with headless Chromium, and asserts the client-side JS rendered its
data (224 restaurant cards, the "z 224 restauracji" count, food-finder items) and
that a menu `.md` is served (the modal fetch dependency). Exits non-zero on any
failed assertion.

Screenshots + DOM dumps land in `./.smoke-out/` by default (override with `OUT=`):

```bash
OUT=/tmp/marta-shots bash .claude/skills/run-marta/smoke.sh
# -> /tmp/marta-shots/{home,restauracje,low-fodmap}.png  (+ *.dom.html)
```

Then **look at** `.smoke-out/restauracje.png` — you should see the sticky nav with
the LOW FODMAP filter chips, "Znaleziono: 132 z 224 restauracji", and a grid of
cards each with a 🟢/🟡/🔴 badge.

Screenshot one page manually (same technique the driver uses):

```bash
python3 -m http.server 8000 --directory "$PWD" & SRV=$!; sleep 1.5
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless=new --no-sandbox \
  --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=1280,1700 \
  --screenshot=/tmp/one.png http://localhost:8000/restauracje/index.html
kill $SRV
```

## Run (human path)

Serve and open in a browser (useless headless — for a real desktop only):

```bash
python3 -m http.server 8000 --directory "$PWD"
# then open http://localhost:8000/  and Ctrl-C to stop
```

## Test

There is no unit-test suite — the smoke driver **is** the test. Run it and check
the exit code / screenshots.

## Gotchas

- **Serve over HTTP, never `file://`.** The restaurant modal does
  `fetch('<path>.md')`; `file://` blocks that (CORS) and the menu preview shows an
  error. `python3 -m http.server` at the repo root is the fix.
- **`.nojekyll` is load-bearing on GitHub Pages.** It stops Jekyll from converting
  the `.md` menu files to HTML, so they stay fetchable by the browser. Don't delete
  it. Locally it doesn't matter (http.server serves raw), but the driver curls a
  `.md` to catch a regression that would only bite on Pages.
- **Let JS run before the screenshot.** Without `--virtual-time-budget=6000` the
  screenshot fires before the `DATA`/`FOODS` arrays render and you get an empty
  grid. The DOM dump has the same requirement.
- **Chromium path is version-pinned** (`chromium-1194`). If the container image
  bumps the version this path changes — override with `CHROME=` or
  `find /opt/pw-browsers -name chrome -type f`.
- **`--no-sandbox` is required** (running as root in the container).
- **Counts are asserted from the DOM.** If you add/remove restaurants, update the
  `z 224 restauracji` count assertion (or rely on the `>=100 cards` check) —
  `DATA` in `restauracje/index.html`, the `INDEX.md` rows, and the `.md` files must
  stay in sync (224 = 86 Wilanów + 138 Ursynów).

## Troubleshooting

- **Screenshot is blank / grid empty** → JS didn't finish; increase
  `--virtual-time-budget`, and confirm you loaded `http://localhost:...` not a
  `file://` path.
- **`FAIL: menu .md not served`** → the http.server isn't running at the repo root,
  or the sample path moved. Check `.smoke-out/httpd.log`.
- **`chromium not found`** → set `CHROME=` to the real binary
  (`find /opt/pw-browsers -name chrome -type f`).
- **Port 8000 busy** → `PORT=8081 bash .claude/skills/run-marta/smoke.sh`.
