# 🍽️ Menu Tools - Automatyzacja wyszukiwania menu

Narzędzia do automatycznego znajdowania i aktualizowania linków do menu restauracji.

## Narzędzia

### 1. menu_scraper.py
**Cel:** Znajdowanie restauracji bez linków do menu

```bash
python3 menu_scraper.py
```

**Wyjście:**
- `searches.txt` - Google search queries
- `missing_menus.json` - JSON restauracji bez menu

### 2. menu_finder.py
**Cel:** Automatyczne wyszukiwanie menu na stronach restauracji

```bash
# Instalacja zależności (tylko raz)
pip install playwright
playwright install

# Uruchomienie
python3 menu_finder.py
```

**Działanie:**
1. Wchodzi na www restauracji
2. Szuka linków do menu
3. Dla restauracji bez www - szuka przez Google
4. Zapisuje wyniki do `found_menus.json`

**Czas:** ~30-60 minut dla 194 restauracji

### 3. update_index.py
**Cel:** Aktualizowanie index.html znalezionymi linkami

```bash
python3 update_index.py
```

**Działanie:**
1. Czyta `found_menus.json`
2. Aktualizuje sekcję LINKS w index.html
3. Tworzy backup: `index.html.backup`
4. Zapisuje zaktualizowany index.html

## Workflow

```bash
# 1. Znajdź brakujące menu (opcjonalnie - przed update)
python3 menu_scraper.py

# 2. Szukaj menu automatycznie
python3 menu_finder.py
# ⏱️  czeka ~30-60 min

# 3. Aktualizuj index.html
python3 update_index.py

# 4. Sprawdź zmiany
git diff restauracje/index.html

# 5. Commit i push
git add restauracje/index.html
git commit -m "Add found menu links"
git push
```

## Instalacja Playwright (Windows)

```powershell
# Zainstaluj pakiet
pip install playwright

# Pobierz przeglądarkę (ważne!)
python -m playwright install
```

## Struktura danych

### found_menus.json
```json
{
  "www": {
    "ursynow/category/restaurant.md": "https://restaurant.pl"
  },
  "menu": {
    "ursynow/category/restaurant.md": "https://restaurant.pl/menu"
  }
}
```

### index.html - LINKS
```javascript
const LINKS = {
  "ursynow/category/restaurant.md": {www:"https://...",menu:"https://..."},
  ...
};
```

## Notatki

- ✅ Scraper respektuje robots.txt
- ✅ Timeout 15 sekund na stronę
- ⚠️ Google Search może wymagać CAPTCHA
- 💡 Najlepiej uruchamiać wieczorem (mniej obciążenia)

## Troubleshooting

**Błąd: Playwright nie znaleziony**
```bash
pip install playwright
python -m playwright install
```

**Błąd: Timeout**
- Zwiększ timeout w menu_finder.py (linia: `timeout=15000`)
- Lub uruchom w godzinach szczytu

**Google CAPTCHA**
- Google może zablokować automatyczne wyszukiwania
- Rozwiązanie: Ręczne dodanie niektórych linków lub użycie VPN

## Przyszłe ulepszenia

- [ ] Cache znalezionych linków
- [ ] Logowanie do pliku
- [ ] Retry dla failed entries
- [ ] Support dla Instagram/Facebook linków
- [ ] Integracja z API dostawców (pyszne, wolt)
