#!/usr/bin/env python3
"""
Export Restaurants - Eksportuje listę restauracji do CSV
"""

import re
import sys
from pathlib import Path

LOCAL_HTML = "restauracje/index.html"
OUTPUT_FILE = "lista.md"

def extract_restaurants(html):
    """Wyciągnij wszystkie restauracje z DATA array"""
    data_match = re.search(r'const DATA = \[(.*?)\];', html, re.DOTALL)
    if not data_match:
        print("❌ Nie znaleziono DATA array")
        return []

    restaurants = []
    data_str = data_match.group(1)

    # Szukaj wszystkich restauracji (Wilanów i Ursynów)
    for match in re.finditer(r'{n:"([^"]+)"[^}]*d:"([^"]+)"[^}]*a:"([^"]+)"', data_str):
        name = match.group(1)
        district = match.group(2)
        address = match.group(3)
        restaurants.append({
            'district': district,
            'name': name,
            'address': address
        })

    return restaurants

def main():
    print("📋 Export Restaurants\n")

    # Wczytaj HTML
    if not Path(LOCAL_HTML).exists():
        print(f"❌ Plik nie znaleziony: {LOCAL_HTML}")
        sys.exit(1)

    with open(LOCAL_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    restaurants = extract_restaurants(html)
    print(f"✅ Znaleziono {len(restaurants)} restauracji\n")

    # Grupuj po dzielnicach
    by_district = {}
    for rest in restaurants:
        district = rest['district']
        if district not in by_district:
            by_district[district] = []
        by_district[district].append(rest)

    # Zapisz do pliku
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Lista Restauracji\n\n")

        for district in sorted(by_district.keys()):
            rest_list = by_district[district]
            f.write(f"## {district} ({len(rest_list)})\n\n")
            f.write("Dzielnica, Restauracja, Adres\n")
            f.write("---|---|---\n")

            for rest in sorted(rest_list, key=lambda x: x['name']):
                # CSV format: dzielnica, nazwa, adres
                line = f"{rest['district']}, {rest['name']}, {rest['address']}\n"
                f.write(line)

            f.write("\n")

    print(f"✅ Zapisano do: {OUTPUT_FILE}")
    print(f"📊 Razem restauracji: {len(restaurants)}")
    for district in sorted(by_district.keys()):
        print(f"   - {district}: {len(by_district[district])}")

if __name__ == "__main__":
    main()
