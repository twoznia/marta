#!/usr/bin/env python3
"""
Menu Finder - Automatyczne wyszukiwanie linków do menu
Wchodzi na strony restauracji i wyciąga linki do menu
"""

import json
import re
import sys
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("❌ Brakuje Playwright. Zainstaluj: pip install playwright")
    print("   Następnie: playwright install")
    sys.exit(1)

# Konfiguracja
LOCAL_HTML = "restauracje/index.html"
OUTPUT_LINKS = "restauracje/found_menus.json"

# Słowa kluczowe do szukania menu na stronie
MENU_KEYWORDS = [
    'menu', 'jadłospis', 'karta', 'oferta', 'jedzenie',
    'menu-en', 'food', 'our-menu', 'see-menu'
]

# Domeny gdzie może być menu
MENU_DOMAINS = [
    'wolt.com',
    'pyszne.pl',
    'ubereats.com',
    'deliveroo.com',
    'google.com/maps',
]

def extract_restaurants(html, district="Ursynów"):
    """Wyciągnij restauracje z DATA array dla wybranej dzielnicy"""
    data_match = re.search(r'const DATA = \[(.*?)\];', html, re.DOTALL)
    if not data_match:
        return {}

    restaurants = {}
    data_str = data_match.group(1)

    # Szukaj restauracji dla wybranej dzielnicy
    pattern = rf'{{n:"([^"]+)"[^}}]*d:"{re.escape(district)}"[^}}]*p:"([^"]+)"(?:[^}}]*www:"([^"]*)")?'
    for match in re.finditer(pattern, data_str):
        name = match.group(1)
        path = match.group(2)
        www = match.group(3) or ""
        restaurants[path] = {"name": name, "www": www}

    return restaurants

def extract_existing_links(html, district="ursynow"):
    """Wyciągnij istniejące LINKS dla wybranej dzielnicy"""
    links_match = re.search(r'const LINKS = \{(.*?)\};', html, re.DOTALL)
    if not links_match:
        return {}

    links = {}
    links_str = links_match.group(1)
    prefix = f"{district}/"

    for match in re.finditer(r'"([^"]+)":\s*{www:"([^"]*)",menu:"([^"]*)"}', links_str):
        path = match.group(1)
        www = match.group(2)
        menu = match.group(3)
        if path.startswith(prefix):
            links[path] = {"www": www, "menu": menu}

    return links

def find_menu_on_page(browser, url, restaurant_name):
    """Szukaj menu na stronie restauracji"""
    try:
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=15000)

        # Czekaj na załadowanie strony
        time.sleep(2)

        # Pobierz kod strony
        html = page.content()

        # Szukaj linków zawierających słowa kluczowe menu
        links = page.query_selector_all('a')
        menu_link = None

        for link in links:
            href = link.get_attribute('href')
            text = link.inner_text().lower()

            if href and any(kw in href.lower() or kw in text for kw in MENU_KEYWORDS):
                # Pełny URL
                menu_link = urljoin(url, href)
                if menu_link not in [MENU_DOMAINS]:
                    break

        # Jeśli nie znaleziono, szukaj w HTML
        if not menu_link:
            for kw in MENU_KEYWORDS:
                pattern = rf'href=["\']([^"\']*{kw}[^"\']*)["\']'
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    menu_link = urljoin(url, match.group(1))
                    break

        page.close()
        return menu_link

    except PlaywrightTimeoutError:
        print(f"⏱️  Timeout: {restaurant_name}")
        page.close()
        return None
    except Exception as e:
        print(f"❌ Błąd {restaurant_name}: {str(e)[:50]}")
        try:
            page.close()
        except:
            pass
        return None

def search_www_on_google(browser, restaurant_name):
    """Szukaj www restauracji na Google"""
    try:
        page = browser.new_page()
        search_query = f'"{restaurant_name}" Ursynów website'
        page.goto(f"https://www.google.com/search?q={search_query}", timeout=15000)

        time.sleep(2)

        # Szukaj linków w wynikach
        links = page.query_selector_all('a')
        for link in links:
            href = link.get_attribute('href')
            if href and 'url?q=' in href:
                # Wyciągnij URL z Google search
                match = re.search(r'url\?q=([^&]+)', href)
                if match:
                    www_link = match.group(1)
                    if not any(x in www_link for x in ['google', 'pyszne', 'wolt']):
                        page.close()
                        return www_link

        page.close()
        return None

    except Exception as e:
        try:
            page.close()
        except:
            pass
        return None

def process_district(html, district_name, district_lower):
    """Przetwórz jedną dzielnicę"""
    restaurants = extract_restaurants(html, district=district_name)
    existing_links = extract_existing_links(html, district=district_lower)

    print(f"📊 Znaleziono {len(restaurants)} restauracji w {district_name}")

    # Restauracje do przetworzenia
    to_process = []
    for path, rest in restaurants.items():
        needs_www = not rest.get('www')
        needs_menu = path not in existing_links or not existing_links[path].get('menu')

        if needs_www or needs_menu:
            to_process.append((path, rest, needs_www, needs_menu))

    print(f"⚠️  {len(to_process)} restauracji do przetworzenia")
    print(f"   - Bez www: {sum(1 for _, _, nw, _ in to_process if nw)}")
    print(f"   - Bez menu: {sum(1 for _, _, _, nm in to_process if nm)}\n")

    found = {"www": {}, "menu": {}}

    # Otwórz przeglądarkę
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for i, (path, rest, needs_www, needs_menu) in enumerate(to_process, 1):
            name = rest['name']
            www = rest.get('www', '')

            print(f"[{i}/{len(to_process)}] {name[:40]:40} ", end='', flush=True)

            # Szukaj www jeśli brakuje
            if needs_www:
                print("🔍www ", end='', flush=True)
                www = search_www_on_google(browser, name)
                if www:
                    found['www'][path] = www
                    print(f"✅www ", end='', flush=True)
                else:
                    print("❌www ", end='', flush=True)
                time.sleep(1)

            # Szukaj menu na stronie
            if needs_menu and www:
                print("🔍menu ", end='', flush=True)
                menu = find_menu_on_page(browser, www, name)
                if menu:
                    found['menu'][path] = menu
                    print("✅menu")
                else:
                    print("❌menu")
                time.sleep(1)
            else:
                print()

        browser.close()

    return found

def main():
    # Argumenty command line
    parser = argparse.ArgumentParser(
        description='Automatyczne wyszukiwanie linków do menu restauracji'
    )
    parser.add_argument(
        '--district',
        choices=['ursynow', 'wilanow', 'all'],
        default='ursynow',
        help='Dzielnica: ursynow, wilanow, lub all (default: ursynow)'
    )
    args = parser.parse_args()

    # Wybór dzielnic do przetworzenia
    if args.district == 'all':
        districts = [('ursynow', 'Ursynów'), ('wilanow', 'Wilanów')]
    else:
        districts = [(args.district, args.district.title())]

    print(f"🚀 Menu Finder - Automatyczne wyszukiwanie menu")
    print(f"📍 Dzielnice: {', '.join([d[1] for d in districts])}\n")

    # Wczytaj HTML
    with open(LOCAL_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    # Przetwórz każdą dzielnicę
    all_found = {"www": {}, "menu": {}}

    for district_lower, district_title in districts:
        print(f"\n{'='*60}")
        print(f"Przetwarzanie: {district_title}")
        print(f"{'='*60}")

        found = process_district(html, district_title, district_lower)
        all_found['www'].update(found['www'])
        all_found['menu'].update(found['menu'])

    # Zapisz wyniki
    with open(OUTPUT_LINKS, 'w', encoding='utf-8') as f:
        json.dump(all_found, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"✅ Znaleziono www: {len(all_found['www'])}")
    print(f"✅ Znaleziono menu: {len(all_found['menu'])}")
    print(f"📁 Zapisano do: {OUTPUT_LINKS}")
    print(f"{'='*60}")
    print("\n💡 Następnie: Uruchom update_index.py żeby dodać linki do index.html")

if __name__ == "__main__":
    main()
