#!/usr/bin/env python3
"""
Menu Scraper dla bazy restauracji Ursynów
Szuka linków do menu dla restauracji bez nich
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin
import urllib.request
import urllib.error

# Konfiguracja
GITHUB_RAW = "https://raw.githubusercontent.com/twoznia/marta/main/restauracje/index.html"
LOCAL_HTML = "restauracje/index.html"  # Szukaj w folderze restauracje

# Delivery platforms do sprawdzenia
PLATFORMS = {
    "pyszne": "https://www.pyszne.pl/menu/",
    "wolt": "https://wolt.com/en/pol/warsaw/restaurant/",
    "ubereats": "https://www.ubereats.com/pl/store/",
}

def load_index_html(use_local=True):
    """Wczytaj index.html"""
    if use_local and Path(LOCAL_HTML).exists():
        print(f"📖 Czytam {LOCAL_HTML} z dysku...")
        with open(LOCAL_HTML, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"📡 Pobieranie index.html z GitHub...")
        try:
            with urllib.request.urlopen(GITHUB_RAW) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"❌ Błąd pobierania: {e}")
            sys.exit(1)

def extract_restaurants(html):
    """Wyciągnij restauracje z DATA array"""
    data_match = re.search(r'const DATA = \[(.*?)\];', html, re.DOTALL)
    if not data_match:
        print("❌ Nie znaleziono DATA array")
        return {}

    restaurants = {}
    data_str = data_match.group(1)

    # Szukaj Ursynów restauracji
    for match in re.finditer(r'{n:"([^"]+)"[^}]*d:"Ursynów"[^}]*p:"([^"]+)"', data_str):
        name = match.group(1)
        path = match.group(2)
        restaurants[path] = {"name": name, "www": "", "menu": ""}

    return restaurants

def extract_links(html):
    """Wyciągnij istniejące LINKS"""
    links_match = re.search(r'const LINKS = \{(.*?)\};', html, re.DOTALL)
    if not links_match:
        return {}

    links = {}
    links_str = links_match.group(1)

    for match in re.finditer(r'"([^"]+)":\s*{([^}]*)}}', links_str):
        path = match.group(1)
        attrs = match.group(2)

        www = ""
        menu = ""

        www_m = re.search(r'www:"([^"]*)"', attrs)
        if www_m:
            www = www_m.group(1)

        menu_m = re.search(r'menu:"([^"]*)"', attrs)
        if menu_m:
            menu = menu_m.group(1)

        if path.startswith("ursynow/"):
            links[path] = {"www": www, "menu": menu}

    return links

def find_missing_menus(restaurants, links):
    """Znajdź restauracje bez menu linków"""
    missing = {}

    for path, rest in restaurants.items():
        has_menu = path in links and links[path].get("menu")
        if not has_menu:
            missing[path] = rest

    return missing

def generate_search_queries(missing):
    """Generuj query do Google dla brakujących"""
    queries = {}
    for path, rest in missing.items():
        name = rest["name"]
        # Query: "Restauracja Ursynów menu pyszne wolt"
        query = f'"{name}" Ursynów menu pyszne wolt ubereats'
        queries[path] = query
    return queries

def print_report(restaurants, links, missing):
    """Wydrukuj raport"""
    total = len(restaurants)
    with_menu = sum(1 for p in restaurants if p in links and links[p].get("menu"))

    print(f"\n{'='*60}")
    print(f"📊 RAPORT MENU LINKÓW URSYNÓW")
    print(f"{'='*60}")
    print(f"Razem restauracji: {total}")
    if total > 0:
        print(f"Z menu linkami: {with_menu}/{total} ({100*with_menu//total}%)")
    else:
        print(f"Z menu linkami: 0/0 (0%)")
    print(f"Brakujące: {len(missing)}")
    print(f"{'='*60}\n")

def save_search_queries(queries, output_file="searches.txt"):
    """Zapisz query do pliku"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Google Search Queries dla brakujących menu linków\n")
        f.write("# Skopiuj i wklej do Google\n\n")

        for path, query in sorted(queries.items()):
            restaurant = path.split('/')[-1].replace('-', ' ').title()
            f.write(f"# {restaurant}\n")
            f.write(f"{query}\n\n")

    print(f"✅ Zapisano {len(queries)} query do {output_file}")

def save_missing_json(missing, output_file="missing_menus.json"):
    """Zapisz brakujące do JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(missing, f, indent=2, ensure_ascii=False)

    print(f"✅ Zapisano {len(missing)} brakujących do {output_file}")

def main():
    print("🚀 Menu Scraper - Ursynów\n")

    # Wczytaj HTML
    html = load_index_html(use_local=True)

    # Ekstrahuj dane
    print("🔍 Czytam restauracje...")
    restaurants = extract_restaurants(html)
    print(f"✅ Znaleziono {len(restaurants)} restauracji")

    print("🔗 Czytam istniejące linki...")
    links = extract_links(html)
    print(f"✅ Znaleziono {len(links)} linków")

    # Znajdź brakujące
    missing = find_missing_menus(restaurants, links)
    print(f"⚠️  Brakuje {len(missing)} menu linków")

    # Wydrukuj raport
    print_report(restaurants, links, missing)

    if missing:
        # Generuj search queries
        print("📝 Generuję search queries...")
        queries = generate_search_queries(missing)
        save_search_queries(queries)
        save_missing_json(missing)

        print("\n💡 INSTRUKCJA:")
        print("1. Otwórz searches.txt")
        print("2. Dla każdego query wklej do Google")
        print("3. Szukaj 'pyszne.pl/menu' lub 'wolt.com' linków")
        print("4. Zapisz znalezione linki w formacie JSON")
        print("5. Wyślij mi JSON - dopiszę do bazy\n")
    else:
        print("✨ Wszystkie restauracje mają menu linki!")

if __name__ == "__main__":
    main()
