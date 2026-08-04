#!/usr/bin/env python3
"""
Update Index - Aktualizuje index.html z nowymi linkami do menu
"""

import json
import re
from pathlib import Path

LOCAL_HTML = "restauracje/index.html"
FOUND_MENUS = "restauracje/found_menus.json"
BACKUP_HTML = "restauracje/index.html.backup"

def load_found_menus():
    """Wczytaj znalezione linki"""
    if not Path(FOUND_MENUS).exists():
        print(f"❌ Brakuje {FOUND_MENUS}")
        return {"www": {}, "menu": {}}

    with open(FOUND_MENUS, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_existing_links(html):
    """Wyciągnij istniejące LINKS"""
    links_match = re.search(r'const LINKS = \{(.*?)\};', html, re.DOTALL)
    if not links_match:
        return {}

    links = {}
    links_str = links_match.group(1)

    for match in re.finditer(r'"([^"]+)":\s*\{www:"([^"]*)",menu:"([^"]*)"\}', links_str):
        path = match.group(1)
        www = match.group(2)
        menu = match.group(3)
        links[path] = {"www": www, "menu": menu}

    return links

def get_restaurant_links(html, path):
    """Pobierz www i menu dla restauracji z DATA array"""
    # Szukaj restauracji w DATA
    pattern = rf'{{n:"([^"]+)"[^}}]*p:"{re.escape(path)}"(?:[^}}]*www:"([^"]*)")?[^}}]*}}'
    match = re.search(pattern, html, re.DOTALL)

    if match:
        www = match.group(2) or ""
        return www
    return ""

def build_links_section(links):
    """Zbuduj nową sekcję LINKS"""
    lines = []
    lines.append('const LINKS = {')

    for path in sorted(links.keys()):
        www = links[path]['www']
        menu = links[path]['menu']
        lines.append(f'  "{path}": {{www:"{www}",menu:"{menu}"}},')

    # Usuń ostatni przecinek
    if len(lines) > 1:
        lines[-1] = lines[-1].rstrip(',')

    lines.append('};')
    return '\n      '.join(lines)

def main():
    print("🔄 Update Index - Aktualizowanie index.html\n")

    # Wczytaj pliki
    with open(LOCAL_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    found = load_found_menus()
    existing_links = load_existing_links(html)

    print(f"📊 Istniejące linki: {len(existing_links)}")
    print(f"✅ Nowe www: {len(found['www'])}")
    print(f"✅ Nowe menu: {len(found['menu'])}\n")

    # Aktualizuj existing_links
    updated_count = 0

    for path, www_link in found['www'].items():
        if path not in existing_links:
            existing_links[path] = {"www": "", "menu": ""}
        existing_links[path]['www'] = www_link
        updated_count += 1
        print(f"✅ www: {path.split('/')[-1][:30]}")

    for path, menu_link in found['menu'].items():
        if path not in existing_links:
            existing_links[path] = {"www": "", "menu": ""}
        existing_links[path]['menu'] = menu_link
        print(f"✅ menu: {path.split('/')[-1][:30]}")

    print(f"\n📝 Zmieniono/dodano: {updated_count} linków\n")

    # Zbuduj nową sekcję LINKS
    new_links_section = build_links_section(existing_links)

    # Zastąp starą sekcję LINKS nową
    old_links_pattern = r'const LINKS = \{[^}]*\};'
    updated_html = re.sub(old_links_pattern, new_links_section, html, flags=re.DOTALL)

    # Backup
    with open(BACKUP_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"💾 Backup: {BACKUP_HTML}")

    # Zapisz zaktualizowany HTML
    with open(LOCAL_HTML, 'w', encoding='utf-8') as f:
        f.write(updated_html)

    print(f"✅ Zaktualizowano: {LOCAL_HTML}")
    print(f"✅ Razem linków: {len(existing_links)}")

if __name__ == "__main__":
    main()
