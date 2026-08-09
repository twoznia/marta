---
name: add-dish
description: Add a new dish to the "marta" Menu / meal-planner (menu/dania). Every dish must be low FODMAP. Use when asked to add, create, or register a new potrawa / danie / posiłek (śniadanie, drugie śniadanie, obiad, podwieczorek, kolacja) with ingredients, gramatura and kalorie, or to regenerate menu/dania.json.
---

# Add a dish to the Menu planner

The Menu tab (`menu/index.html`) is a client-side meal planner. Its **source of
truth** is one Markdown file per dish under `menu/dania/<posilek>/<slug>.md`. A
generator (`tools/build_menu.py`) reads all those files and writes
`menu/dania.json`, which the page fetches. Base calories and gramatura are
**derived from the ingredient list** — you never hand-maintain a total.

To add a dish you do two things: **write the `.md` file**, then **rebuild the JSON**.

## Hard rule: every dish must be LOW FODMAP

The whole Menu is low FODMAP — do not add a dish that isn't. Follow the repo's own
guide (`low-fodmap/README.md`). Practical rules:

- **No lactose:** use *mleko/jogurt bez laktozy*, mature cheeses (ser dojrzewający,
  parmezan, feta w małej porcji). Never plain cow milk, zwykły jogurt, twaróg,
  serek wiejski, śmietana.
- **No wheat/rye/barley:** use *chleb/makaron/panierka bezglutenowa*. No pszenny/żytni
  bread, wheat pasta, kuskus.
- **No onion/garlic** (fruktany): season without them; *oliwa czosnkowa* is fine
  (fructans don't dissolve in fat). Watch ready sauces/broths — say "bez cebuli/czosnku".
- **No honey/agave/HFCS/polioli:** sweeten with cukier (umiar), syrop klonowy, stewia.
- **No** ciecierzyca/soczewica/fasola/hummus, jabłko/gruszka/mango/arbuz.
- **Green-light** staples: jajka, mięso, drób, ryby; ryż, quinoa, kasza gryczana,
  kukurydza; marchew, ogórek, sałata, szpinak, pomidor, ziemniak; banan (niedojrzały),
  truskawki, borówki, winogrona, kiwi, pomarańcza; orzechy włoskie/makadamia/ziemne.
- **Conditional (⚠️) only in their per-serve limit** as the BASE portion (the planner
  may scale up, so keep the base modest): awokado ~30 g, brokuł (różyczki) ~75 g,
  cukinia ~65 g, papryka czerwona ~75 g, feta/mozzarella mała porcja, migdały ~10 szt,
  owies ~50 g. Prefer building dishes mostly from green-light items so scaling is safe.

Keep the `**Low FODMAP:** tak …` note line in the body (the seed uses it).

## 1. Pick the meal (posiłek)

`<posilek>` must be exactly one of these slugs (directory names):

| slug | etykieta |
|---|---|
| `sniadanie` | Śniadanie |
| `drugie-sniadanie` | Drugie śniadanie |
| `obiad` | Obiad |
| `podwieczorek` | Podwieczorek |
| `kolacja` | Kolacja |

## 2. Write `menu/dania/<posilek>/<slug>.md`

`<slug>` is lowercase ASCII, words joined by `-` (no Polish diacritics, no
spaces), e.g. `owsianka-banan-orzechy`. Exact required format:

```markdown
---
nazwa: Owsianka z bananem i orzechami
posilek: sniadanie
skladniki:
  - { nazwa: "Płatki owsiane", gramy: 60, kcal: 228 }
  - { nazwa: "Mleko bez laktozy 2%", gramy: 200, kcal: 100 }
  - { nazwa: "Banan", gramy: 100, kcal: 89 }
  - { nazwa: "Orzechy włoskie", gramy: 15, kcal: 98 }
---

# Owsianka z bananem i orzechami

Jedno zdanie opisu dania (pierwszy akapit trafia do JSON jako "opis").

**Bazowa porcja:** 375 g · **515 kcal** (wartości bazowe; planer skaluje porcję do celu).

## Składniki (porcja bazowa)

- Płatki owsiane — 60 g — 228 kcal
- Mleko 2% — 200 g — 100 kcal
- Banan — 100 g — 89 kcal
- Orzechy włoskie — 15 g — 98 kcal

## Przepis

1. Pierwszy krok.
2. Drugi krok.
```

Rules that the build/planner rely on — do not deviate:

- **Frontmatter** is between `---` lines. `nazwa` and `posilek` are required.
- **`skladniki`** — one item per line, EXACTLY:
  `  - { nazwa: "…", gramy: <liczba>, kcal: <liczba> }` (double quotes around the
  name; `gramy` and `kcal` are numbers). This is what the parser reads; the
  bulleted "## Składniki" list below is for humans only.
- Each ingredient's **`kcal` is for that `gramy` portion**, not per 100 g. Use
  realistic values (per-100g reference × grams ÷ 100). The dish's base kcal is the
  sum — so make the parts add up to a sensible meal.
- Give a dish a base portion that is **typical for that meal** (śniadanie ~400–500,
  drugie śniadanie ~230–300, obiad ~570–750, podwieczorek ~160–250, kolacja
  ~340–500 kcal). The planner scales from there, so a wildly off base makes odd
  portions.
- The `## Przepis` section must use a **numbered list** (`1. …`) — the page pulls
  those lines out as steps.

## 3. Rebuild the index

```bash
python3 tools/build_menu.py          # writes menu/dania.json
python3 tools/build_menu.py --check  # validate only (non-zero exit on error)
```

The build validates every file (frontmatter present, known `posilek`, at least one
ingredient) and prints a per-meal count. **Commit both** the new `.md` file **and**
the regenerated `menu/dania.json`.

## 4. Verify (optional but recommended)

Serve and screenshot with the existing site driver, then look at the Menu page:

```bash
bash .claude/skills/run-marta/smoke.sh   # serves over http:// + screenshots
python3 -m http.server 8000              # or open http://localhost:8000/menu/
```

## Gotchas

- **Regenerate `dania.json`** after any `.md` change — the page reads the JSON, not
  the `.md` files (except the recipe, which it fetches on "Pokaż przepis").
- **`.nojekyll`** at repo root keeps `.md` files fetchable on GitHub Pages — the
  recipe fetch depends on it. Don't remove it.
- **No external YAML library** — the parser is regex-based and only understands the
  exact `skladniki` line format above. Keep the quotes and comma spacing.
- Slug must be unique within its `<posilek>` folder (it's the filename).
