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

# Składniki warunkowe (⚠️ „żółte") wg low-fodmap/README.md — bezpieczne tylko
# w limicie porcji, a FODMAP-y się kumulują. Danie z takim składnikiem oznaczamy
# jako „żółte"; danie wyłącznie z produktów zielonych → „zielone".
_WARUNKOWE_KEYWORDS = (
    "awokado", "brokuł", "brokul", "batat", "cukini", "malin",
    "papryk", "feta", "mozzarell", "owsian", "owies", "orkisz",
    "laskow", "gorzka czekolad", "czekolada gorzk", "kukurydza",
)


def _skladnik_warunkowy(nazwa: str) -> bool:
    """Czy dany składnik jest warunkowy (⚠️)?"""
    n = nazwa.lower()
    # „mleko migdałowe" jest zielone, ale migdały (orzechy) już warunkowe.
    if "migdał" in n and "mleko" not in n:
        return True
    # „kukurydza" (ziarna/kolba) jest warunkowa, ale „produkty kukurydziane"
    # (tortilla, wafle, mąka kukurydziana) są zielone — te nie zawierają
    # podłańcucha „kukurydza" (mają „kukurydzian…"), więc obsługuje to keyword.
    return any(k in n for k in _WARUNKOWE_KEYWORDS)


def klasyfikuj(skladniki: list[dict]) -> tuple[str, list[str]]:
    """Zwraca ('zielony'|'zolty', [nazwy składników warunkowych])."""
    warunkowe = [s["nazwa"] for s in skladniki if _skladnik_warunkowy(s["nazwa"])]
    return ("zolty" if warunkowe else "zielony"), warunkowe


# ── Jednostki na listach zakupów / w tabelach dań ────────────────────────────
# Dla każdego składnika wyliczamy, jak pokazywać ilość: na sztuki (typ "szt",
# `na_sztuke` g/szt.), płynny (typ "ml", `gestosc` g/ml) albo domyślnie w gramach
# (brak pola `jednostka`). Reguły są TU centralnie — nowe dania z build-u dostają
# jednostki automatycznie. Dodając nowy składnik na sztuki/płyn, dopisz regułę
# poniżej (i przegeneruj dania.json).
#
# `grupa`/`nazwa_grupy` scala różne nazwy tego samego produktu na liście zakupów
# (np. wszystkie warianty jajek → „Jajka", pieczywo/chleb → „Pieczywo bezglutenowe").
def jednostka_dla(nazwa: str) -> dict | None:
    n = nazwa.lower()
    if re.search(r"jaj(ka|ko|a|ek)", n) and "jajeczn" not in n:
        return {"typ": "szt", "na_sztuke": 55, "etykieta": "szt.", "grupa": "jajka", "nazwa_grupy": "Jajka"}
    if n.startswith("banan"):
        return {"typ": "szt", "na_sztuke": 120, "etykieta": "szt."}
    if n.startswith("kiwi"):
        return {"typ": "szt", "na_sztuke": 75, "etykieta": "szt."}
    if n.startswith("pomarańcza"):
        return {"typ": "szt", "na_sztuke": 130, "etykieta": "szt."}
    if re.fullmatch(r"pomidor", n):
        return {"typ": "szt", "na_sztuke": 120, "etykieta": "szt."}
    if n.startswith("tortilla"):
        return {"typ": "szt", "na_sztuke": 30, "etykieta": "szt."}
    if n.startswith("wafle"):
        return {"typ": "szt", "na_sztuke": 8, "etykieta": "szt."}
    if re.match(r"(chleb|pieczywo) bezglutenow", n):
        return {"typ": "szt", "na_sztuke": 30, "etykieta": "kromka",
                "grupa": "pieczywo-bg", "nazwa_grupy": "Pieczywo bezglutenowe"}
    for pref, dens in (("mleko", 1.0), ("jogurt", 1.0), ("bulion", 1.0),
                       ("passata", 1.0), ("syrop", 1.32), ("majonez", 0.91)):
        if n.startswith(pref):
            return {"typ": "ml", "gestosc": dens, "etykieta": "ml"}
    if re.match(r"(oliwa|olej)", n):
        return {"typ": "ml", "gestosc": 0.92, "etykieta": "ml"}
    return None


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
        nazwa_sk = im.group("nazwa")
        s = {
            "nazwa": nazwa_sk,
            "gramy": float(im.group("gramy")),
            "kcal": float(im.group("kcal")),
        }
        jed = jednostka_dla(nazwa_sk)
        if jed:
            s["jednostka"] = jed
        skladniki.append(s)
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
    fodmap, warunkowe = klasyfikuj(skladniki)

    rel = path.relative_to(ROOT).as_posix()
    return {
        "slug": path.stem,
        "nazwa": nazwa,
        "posilek": posilek,
        "opis": opis,
        "skladniki": skladniki,
        "bazowe_kcal": bazowe_kcal,
        "bazowa_gramatura": bazowa_gramatura,
        "fodmap": fodmap,          # 'zielony' | 'zolty'
        "warunkowe": warunkowe,    # nazwy składników warunkowych (⚠️)
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
    zolte = sum(1 for d in data["dania"] if d["fodmap"] == "zolty")
    print(f"Wczytano {n} dań ({summary}).", file=sys.stderr)
    print(f"FODMAP: zielone {n - zolte}, żółte {zolte}.", file=sys.stderr)

    if args.check:
        print("OK — walidacja przeszła (nic nie zapisano).", file=sys.stderr)
        return 0

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Zapisano {OUT.relative_to(ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
