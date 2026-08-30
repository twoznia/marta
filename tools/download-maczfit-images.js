// Pobiera wszystkie obrazki dań Maczfit do maczfit/img/<SKU>.jpg.
// Źródło URL-i: maczfit/dania.json (pole "obrazekUrl").
// Po pobraniu uruchom: node tools/parse-maczfit.js
// — parser przełączy pole "obrazek" na lokalne ścieżki img/<SKU>.jpg.
//
// Uruchomienie: node tools/download-maczfit-images.js
// Pomija pliki już pobrane. Bez zależności zewnętrznych (Node 18+, globalne fetch).
const fs = require("fs");
const path = require("path");

const MACZFIT_DIR = path.join(__dirname, "..", "maczfit");
const IMG_DIR = path.join(MACZFIT_DIR, "img");
const DANIA = path.join(MACZFIT_DIR, "dania.json");

fs.mkdirSync(IMG_DIR, { recursive: true });
const { dania } = JSON.parse(fs.readFileSync(DANIA, "utf8"));

async function download(url, dest) {
  const res = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0" } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(dest, buf);
  return buf.length;
}

(async () => {
  let ok = 0, skip = 0, fail = 0;
  for (const d of dania) {
    const dest = path.join(IMG_DIR, `${d.sku}.jpg`);
    if (fs.existsSync(dest)) { skip++; continue; }
    try {
      const bytes = await download(d.obrazekUrl, dest);
      console.log(`✓ ${d.sku}.jpg (${bytes} B)`);
      ok++;
    } catch (e) {
      console.error(`✗ ${d.sku}: ${e.message}  ${d.obrazekUrl}`);
      fail++;
    }
  }
  console.log(`\nPobrano ${ok}, pominięto ${skip} (już były), błędów ${fail}.`);
  if (ok) console.log("Teraz uruchom: node tools/parse-maczfit.js (przełączy dania.json na lokalne obrazki).");
})();
