#!/usr/bin/env python3
"""
Buduje `menu/dania.json` z plików źródłowych `menu/dania/<posilek>/<slug>.md`.

Każde danie to Markdown z frontmatterem YAML:

    ---
    nazwa: Owsianka z bananem i orzechami
    posilek: sniadanie
    skladniki:
      - { nazwa: "Płatki owsiane", gramy: 60, kcal: 228 }
      - { nazwa: "Mleko 2%", gramy: 200, kcal: 100 }
    ---
    # ... (treść = opis + przepis)

Wynikowy JSON jest tym, co pobiera przeglądarka na `menu/index.html` — dzięki temu
strona nie musi ściągać kilkudziesięciu plików .md przy starcie (analogicznie do
tablicy DATA w `restauracje/index.html`).

Bazowe kcal i gramatura dania są WYLICZANE z sumy składników — nie trzeba ich
utrzymywać ręcznie. Skrypt nie ma zależności zewnętrznych (parser frontmattera
jest dopasowany do powyższego, prostego formatu).

Użycie:
    python tools/build_menu.py            # zapisuje menu/dania.json
    python tools/build_menu.py --check    # tylko waliduje, nic nie zapisuje (exit!=0 przy błędach)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DANIA_DIR = ROOT / "menu" / "dania"
OUT = ROOT / "menu" / "dania.json"

# Kanoniczna kolejność i etykiety posiłków (slug -> etykieta wyświetlana).
POSILKI = {
    "sniadanie": "Śniadanie",
    "drugie-sniadanie": "Drugie śniadanie",
    "obiad": "Obiad",
    "podwieczorek": "Podwieczorek",
    "kolacja": "Kolacja",
}

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
_ING_RE = re.compile(
    r'nazwa:\s*"(?P<nazwa>[^"]+)"\s*,\s*gramy:\s*(?P<gramy>\d+(?:\.\d+)?)\s*,\s*kcal:\s*(?P<kcal>\d+(?:\.\d+)?)'
)


def parse_dish(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        raise ValueError(f"{path}: brak poprawnego frontmattera (--- ... ---)")
    front, body = m.group(1), m.group(2)

    nazwa_m = re.search(r"^nazwa:\s*(.+)$", front, re.MULTILINE)
    posilek_m = re.search(r"^posilek:\s*(.+)$", front, re.MULTILINE)
    if not nazwa_m or not posilek_m:
        raise ValueError(f"{path}: wymagane pola 'nazwa' i 'posilek'")

    nazwa = nazwa_m.group(1).strip()
    posilek = posilek_m.group(1).strip()
    if posilek not in POSILKI:
        raise ValueError(f"{path}: nieznany posilek '{posilek}' (dozwolone: {', '.join(POSILKI)})")

    skladniki = []
    for im in _ING_RE.finditer(front):
        skladniki.append({
            "nazwa": im.group("nazwa"),
            "gramy": float(im.group("gramy")),
            "kcal": float(im.group("kcal")),
        })
    if not skladniki:
        raise ValueError(f"{path}: brak składników (pole 'skladniki')")

    # Opis = pierwszy niepusty akapit treści po nagłówku '# ...'.
    opis = ""
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("**"):
            continue
        opis = s
        break

    bazowe_kcal = round(sum(s["kcal"] for s in skladniki))
    bazowa_gramatura = round(sum(s["gramy"] for s in skladniki))

    rel = path.relative_to(ROOT).as_posix()
    return {
        "slug": path.stem,
        "nazwa": nazwa,
        "posilek": posilek,
        "opis": opis,
        "skladniki": skladniki,
        "bazowe_kcal": bazowe_kcal,
        "bazowa_gramatura": bazowa_gramatura,
        "plik": rel,  # ścieżka do pełnego przepisu (fetch z przeglądarki)
    }


def build() -> dict:
    if not DANIA_DIR.exists():
        raise SystemExit(f"Brak katalogu {DANIA_DIR}")
    dishes: list[dict] = []
    errors: list[str] = []
    for md in sorted(DANIA_DIR.rglob("*.md")):
        try:
            dishes.append(parse_dish(md))
        except ValueError as e:
            errors.append(str(e))
    if errors:
        for e in errors:
            print(f"BŁĄD: {e}", file=sys.stderr)
        raise SystemExit(2)

    # Zlicz dania w każdym posiłku i ostrzeż, jeśli któryś jest pusty.
    per = {p: 0 for p in POSILKI}
    for d in dishes:
        per[d["posilek"]] += 1
    for p, n in per.items():
        if n == 0:
            print(f"OSTRZEŻENIE: posiłek '{p}' nie ma żadnego dania.", file=sys.stderr)

    return {
        "posilki": [{"slug": s, "etykieta": e, "liczba": per[s]} for s, e in POSILKI.items()],
        "dania": dishes,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Buduje menu/dania.json z plików .md.")
    ap.add_argument("--check", action="store_true", help="Tylko waliduj, nie zapisuj.")
    args = ap.parse_args()

    data = build()
    n = len(data["dania"])
    summary = ", ".join(f"{p['etykieta']}: {p['liczba']}" for p in data["posilki"])
    print(f"Wczytano {n} dań ({summary}).", file=sys.stderr)

    if args.check:
        print("OK — walidacja przeszła (nic nie zapisano).", file=sys.stderr)
        return 0

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Zapisano {OUT.relative_to(ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
