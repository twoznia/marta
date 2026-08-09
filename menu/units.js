// Wspólne formatowanie jednostek dla stron Menu (planer dnia, tydzień, propozycje).
// Reguły jednostek są w tools/build_menu.py i trafiają do dania.json jako pole
// `jednostka` przy każdym składniku — tutaj tylko je formatujemy.
(function () {
  function fmtQty(g) {
    if (g >= 1000) { const kg = g / 1000; return (Number.isInteger(kg) ? kg : kg.toFixed(2)) + " kg"; }
    return g + " g";
  }
  // Polska odmiana „kromka/kromki/kromek".
  function kromkaForm(n) {
    if (n === 1) return "kromka";
    const t = n % 10, h = n % 100;
    return (t >= 2 && t <= 4 && !(h >= 12 && h <= 14)) ? "kromki" : "kromek";
  }
  // Etykieta ilości dla podanych gramów i (opcjonalnie) danych `jednostka`:
  //  • typ "szt"  → „N szt./kromki (X g)"
  //  • typ "ml"   → „N ml (X g)"
  //  • brak/typ inny → same gramy/kg
  function qtyLabel(gramy, jednostka) {
    if (jednostka && jednostka.typ === "szt") {
      const n = Math.max(1, Math.round(gramy / jednostka.na_sztuke));
      const unit = jednostka.etykieta === "kromka" ? kromkaForm(n) : jednostka.etykieta;
      return `${n} ${unit} (${fmtQty(gramy)})`;
    }
    if (jednostka && jednostka.typ === "ml") {
      return `${Math.round(gramy / jednostka.gestosc)} ml (${fmtQty(gramy)})`;
    }
    return fmtQty(gramy);
  }
  window.MenuUnits = { fmtQty, kromkaForm, qtyLabel };
})();
