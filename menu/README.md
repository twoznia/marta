# menu/ — planer posiłków (zakładka „Menu")

Interaktywny planer dnia: ustawiasz **kalorie na dzień**, a strona generuje
propozycję na **śniadanie, drugie śniadanie, obiad, podwieczorek i kolację**,
skalując porcje (gramaturę i kalorie) tak, by suma trafiła w cel. Plan tworzy się
**automatycznie po wejściu na stronę** — bez klikania; przyciski „Losuj od nowa"
i „Zamień danie" dają inne propozycje. Biblioteka liczy **40 dań** (po 8 na posiłek).

**Wszystkie dania są low FODMAP** — składniki i porcje dobrane zgodnie z
przewodnikiem [`low-fodmap/`](../low-fodmap/README.md) (bez laktozy, pieczywo i
makaron bezglutenowy, bez cebuli/czosnku, owoce i warzywa z listy dozwolonej,
produkty warunkowe ⚠️ w limitach porcji).

Otwórz: [`menu/index.html`](index.html).

## Architektura

Ten sam wzorzec, co reszta serwisu: **statyczna strona + dane jako pliki + skrypt
generujący indeks** (bez frameworka i bez builda po stronie przeglądarki).

```
menu/
├── index.html          # strona planera (client-side JS: skalowanie + losowanie)
├── dania.json          # WYGENEROWANY indeks (pobierany przez przeglądarkę)
└── dania/              # ŹRÓDŁO PRAWDY — jedno danie = jeden plik .md
    ├── sniadanie/
    ├── drugie-sniadanie/
    ├── obiad/
    ├── podwieczorek/
    └── kolacja/
tools/build_menu.py     # czyta dania/**/*.md → zapisuje menu/dania.json
```

- **Źródło prawdy** to pliki `menu/dania/<posilek>/<slug>.md` — czytelne dla
  człowieka i łatwe do dodania (patrz skill poniżej). Zawierają frontmatter ze
  składnikami (nazwa, gramy, kcal) oraz przepis w treści.
- **`tools/build_menu.py`** sumuje składniki (bazowe kcal i gramatura są
  wyliczane, nie utrzymywane ręcznie) i zapisuje `menu/dania.json`.
- **`index.html`** pobiera jeden `dania.json` (szybko, zamiast dziesiątek plików —
  analogicznie do tablicy `DATA` w `restauracje/index.html`). Przepis dla danego
  dania dociąga z jego `.md` dopiero po kliknięciu „Pokaż przepis".

## Jak działa generowanie dnia

Domyślny rozkład kalorii między posiłki (wagi, normalizowane po wyłączeniu
posiłków przełącznikami):

| posiłek | udział |
|---|---|
| Śniadanie | 25% |
| Drugie śniadanie | 10% |
| Obiad | 30% |
| Podwieczorek | 10% |
| Kolacja | 25% |

Dla każdego posiłku: `cel_posiłku = cel_dnia × udział`, następnie danie jest
skalowane współczynnikiem `cel_posiłku / bazowe_kcal_dania` — każdy składnik ma
przeskalowaną gramaturę i kalorie. Suma dnia równa się celowi z dokładnością do
zaokrągleń porcji (pokazywana jako różnica ± kcal). Możesz zamienić pojedyncze
danie, wyłączyć posiłek albo wylosować cały dzień od nowa.

## Dodawanie nowych dań

Dwie drogi — obie kończą się regeneracją `dania.json`:

1. **Skill** `add-dish` (`.claude/skills/add-dish/SKILL.md`) — dokładny format pliku
   dania + walidacja + rebuild. Użyj, gdy dodajesz danie sam.
2. **Agent** `dodaj-danie` (`.claude/agents/dodaj-danie.md`) — korzysta z powyższego
   skilla; podajesz nazwę i typ posiłku, agent dobiera realistyczne gramatury/kcal,
   zapisuje plik i przebudowuje indeks.

Ręcznie, w skrócie:

```bash
# 1) dodaj plik menu/dania/<posilek>/<slug>.md (format w skillu add-dish)
# 2) przebuduj indeks:
python3 tools/build_menu.py
# 3) zacommituj plik .md ORAZ zmieniony menu/dania.json
```

## Low FODMAP — zasada dla nowych dań

Każde nowe danie musi być zgodne z dietą low FODMAP: żadnej laktozy (mleko/jogurt
bez laktozy, sery dojrzewające), pieczywo/makaron **bezglutenowy**, bez cebuli i
czosnku (dozwolona oliwa czosnkowa), owoce/warzywa z listy ✅, a produkty warunkowe
⚠️ tylko w bazowych porcjach z limitów. Szczegóły i limity: [`low-fodmap/`](../low-fodmap/README.md).

## Uwaga

Wartości kaloryczne są orientacyjne (typowe wartości produktów). FODMAP-y się
kumulują — mocne zwiększenie porcji dań z produktami ⚠️ może przekroczyć próg
tolerancji. To narzędzie pomocnicze do planowania, nie porada dietetyczna.
