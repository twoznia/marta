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
python3 menu_finder.py [--district DISTRICT]
```

**Parametry:**
- `--district ursynow` - szukaj tylko Ursynów (domyślnie)
- `--district wilanow` - szukaj tylko Wilanów
- `--district all` - szukaj Ursynów + Wilanów

**Działanie:**
1. Wchodzi na www restauracji
2. Szuka linków do menu
3. Dla restauracji bez www - szuka przez Google
4. Zapisuje wyniki do `found_menus.json`

**Czas:** 
- ~30-60 min dla Ursynów (194 restauracji)
- ~60-90 min dla Wilanowa (280+ restauracji)
- ~120+ min dla obu (all)

### 3. update_index.py
**Cel:** Aktualizowanie index.html znalezionymi linkami

```bash
python3 update_index.py [--test|--apply]
```

**Parametry:**
- `--test` (domyślnie) - Tryb testowy
  - Zapisuje do `index_updated.html` (nie zmienia oryginalnego)
  - Pozwala sprawdzić zmiany przed aplikacją
  
- `--apply` - Tryb aplikacji
  - Modyfikuje `index.html`
  - Tworzy backup: `index.html.backup`

**Działanie:**
1. Czyta `found_menus.json`
2. Aktualizuje sekcję LINKS
3. W trybie test: zapisuje do `index_updated.html`
4. W trybie apply: backup i update `index.html`

## Workflow

### Opcja 1: Pojedyncza dzielnica (Ursynów)

```bash
# 1. Szukaj menu (domyślnie Ursynów)
python3 tools/menu_finder.py
# czeka ~30-60 min

# 2. TEST - sprawdź zmiany bez modyfikacji
python3 tools/update_index.py --test
# sprawdź: restauracje/index_updated.html

# 3. APPLY - zastosuj zmiany
python3 tools/update_index.py --apply
# backup: restauracje/index.html.backup
# zaktualizowany: restauracje/index.html

# 4. Commit i push
git add restauracje/index.html
git commit -m "Add Ursynów menu links"
git push
```

### Opcja 2: Obie dzielnice (Ursynów + Wilanów)

```bash
# 1. Szukaj menu w obu dzielnicach
python3 tools/menu_finder.py --district all
# czeka ~120+ min

# 2. TEST
python3 tools/update_index.py --test

# 3. APPLY
python3 tools/update_index.py --apply

# 4. Commit
git add restauracje/index.html
git commit -m "Add menu links for Ursynów and Wilanów"
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
