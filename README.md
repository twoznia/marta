# marta

Strona dla Marty pod GitHub Pages (`github.io`). Strona główna to list oraz
**menu z kafelkami wyboru** — na razie z jednym kafelkiem: **Restauracje**.

## Struktura repozytorium

- `index.html` – strona główna (hero, list, powody, menu z kafelkami)
- `style.css` – styl strony
- `hearts.js` – animowane serduszka w tle + animacja listy powodów
- `restauracje/` – baza restauracji (Wilanów i Ursynów) z menu i oznaczeniami low FODMAP
  - `restauracje/index.html` – interaktywna przeglądarka: filtry (dzielnica, low FODMAP),
    wyszukiwarka i podgląd menu każdej restauracji
  - `restauracje/INDEX.md` – ta sama lista jako tabela (czytelna wprost na GitHubie)
- `.nojekyll` – wyłącza przetwarzanie Jekyllem, dzięki czemu GitHub Pages serwuje pliki
  `.md` bez zmian (przeglądarka restauracji wczytuje je na żywo)

## Kafelki menu

Kafelki znajdują się w `index.html` w sekcji `#menu`. Aby dodać kolejny wybór,
skopiuj blok `<a class="tile" …>` i podmień emoji, tytuł, opis oraz `href`.

Obecne kafelki:

- 🍽️ **Restauracje** → [`restauracje/index.html`](restauracje/index.html) —
  interaktywna przeglądarka restauracji w Wilanowie i Ursynowie: menu, adresy, godziny
  otwarcia, typ kuchni oraz dania, które można zjeść na diecie low FODMAP.

## Jak opublikować na GitHub Pages (`github.io`)

1. Wejdź w repozytorium na GitHub.
2. `Settings` → `Pages`.
3. W sekcji **Build and deployment** ustaw:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main`, folder `/ (root)`
4. Zapisz ustawienia.
5. Po chwili strona będzie dostępna pod adresem:
   - `https://twoznia.github.io/marta/` (dla tego repozytorium)
