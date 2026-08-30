// Parsuje pliki maczfit/maczfit_*.html do maczfit/dania.json.
// Obsługuje DWA formaty źródeł (starszy i wrześniowy 2026) i scala je w jedną listę.
// Ignoruje daty — zbiera unikalne dania (po SKU z URL obrazka),
// grupując je wg posiłku (śniadanie, ii śniadanie, obiad, podwieczorek, kolacja).
//
// Obrazki: jeśli w maczfit/img/<SKU>.jpg istnieje lokalna kopia, danie dostaje
// obrazek = "img/<SKU>.jpg" (ścieżka względna dla maczfit/index.html), a oryginalny
// link zdalny jest zachowany w polu "obrazekUrl". Gdy lokalnej kopii nie ma,
// obrazek zostaje oryginalnym URL-em (strona działa online tak jak dotąd).
// Pobranie obrazków: node tools/download-maczfit-images.js
const fs = require("fs");
const path = require("path");

const MACZFIT_DIR = path.join(__dirname, "..", "maczfit");
const IMG_DIR = path.join(MACZFIT_DIR, "img");
const OUT = path.join(MACZFIT_DIR, "dania.json");

// Kolejność ma znaczenie: starsze menu pierwsze, wrzesień dokłada tylko nowości.
const SOURCES = [
  "maczfit_posilki_27lipca-14sierpnia2026.html",
  "maczfit-posilki-wrzesien-2026.html",
];

// Kategorie posiłków (klucz = wielkie litery z pola typu, po normalizacji).
const CAT = {
  "ŚNIADANIE": { slug: "sniadanie", etykieta: "Śniadanie", emoji: "🥣" },
  "II ŚNIADANIE": { slug: "drugie-sniadanie", etykieta: "II śniadanie", emoji: "🍎" },
  "OBIAD": { slug: "obiad", etykieta: "Obiad", emoji: "🍲" },
  "PODWIECZOREK": { slug: "podwieczorek", etykieta: "Podwieczorek", emoji: "🥕" },
  "KOLACJA": { slug: "kolacja", etykieta: "Kolacja", emoji: "🥗" },
};

// Normalizuje etykietę typu posiłku z obu formatów do klucza CAT.
// Starszy: "ŚNIADANIE", "II ŚNIADANIE"...  Wrzesień: "Śniadanie", "2 Śniadanie"...
const normKat = (raw) => {
  const s = raw.toUpperCase().trim();
  if (/^(2|II)\s*ŚNIADANIE$/.test(s)) return "II ŚNIADANIE";
  if (/^ŚNIADANIE$/.test(s)) return "ŚNIADANIE";
  if (/^OBIAD$/.test(s)) return "OBIAD";
  if (/^PODWIECZOREK$/.test(s)) return "PODWIECZOREK";
  if (/^KOLACJA$/.test(s)) return "KOLACJA";
  return s;
};

const decode = (s) =>
  s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
   .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/​/g, "").replace(/\s+/g, " ").trim();

const grab = (block, tag) => {
  const m = block.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, "i"));
  return m ? decode(m[1].replace(/<[^>]+>/g, "")) : "";
};

const grabClass = (block, cls) => {
  const m = block.match(new RegExp(`<div class="${cls}"[^>]*>([\\s\\S]*?)</div>`, "i"));
  return m ? decode(m[1].replace(/<[^>]+>/g, "")) : "";
};

// Wyciąga jeden posiłek z bloku HTML, niezależnie od formatu.
function parseBlock(block) {
  const imgM = block.match(/<img\s+src="([^"]+)"[^>]*alt="([^"]*)"/i);
  if (!imgM) return null;
  const img = imgM[1];
  const skuM = img.match(/SKU\/(\d+)\.jpg/i);
  if (!skuM) return null; // pomija placeholdery (emptyMealImage.png) — brak SKU
  const sku = skuM[1];

  // Format starszy: <h3>KAT</h3><h4>nazwa</h4><p><strong>Składniki:</strong>...</p>
  let kat = grab(block, "h3");
  let nazwa = grab(block, "h4");
  let skladniki = "";
  let alergeny = "";

  if (kat || nazwa) {
    const skM = block.match(/<strong>Składniki:<\/strong>([\s\S]*?)<\/p>/i);
    skladniki = skM ? decode(skM[1]) : "";
    const alM = block.match(/<strong>Alergeny:<\/strong>([\s\S]*?)<\/p>/i);
    alergeny = alM ? decode(alM[1]) : "";
  } else {
    // Format wrześniowy: .meal-type / .meal-name / <details><summary>Składniki</summary><p>...</p>
    kat = grabClass(block, "meal-type");
    nazwa = grabClass(block, "meal-name");
    const skM = block.match(/<summary>Składniki<\/summary>\s*<p>([\s\S]*?)<\/p>/i);
    let full = skM ? decode(skM[1]) : "";
    // "Może zawierać: ..." pełni rolę pola Alergeny (śladowe).
    const mz = full.split(/Może zawierać:/i);
    skladniki = mz[0].replace(/[.\s]+$/, "").trim();
    alergeny = mz[1] ? mz[1].replace(/\.\s*$/, "").trim() : "";
  }

  if (!nazwa) nazwa = decode(imgM[2]);
  return { sku, img, kat: normKat(kat), nazwa, skladniki, alergeny };
}

// Zbiera pozycje ze wszystkich źródeł.
const items = [];
for (const file of SOURCES) {
  const html = fs.readFileSync(path.join(MACZFIT_DIR, file), "utf8");
  const blocks = html.split(/(?=<div class="meal">)/).filter((b) => b.startsWith('<div class="meal">'));
  let n = 0;
  for (const b of blocks) {
    const meal = parseBlock(b);
    if (meal) { meal.zrodlo = file; items.push(meal); n++; }
  }
  console.log(`Źródło ${file}: ${n} pozycji (z ${blocks.length} bloków).`);
}

// Dedupe po SKU, zachowując pierwsze wystąpienie (starsze menu ma priorytet).
const seen = new Map();
let duplikaty = 0;
for (const meal of items) {
  if (seen.has(meal.sku)) { duplikaty++; continue; }
  seen.set(meal.sku, meal);
}
const unique = [...seen.values()];

const hasLocalImg = (sku) => fs.existsSync(path.join(IMG_DIR, `${sku}.jpg`));

const posilki = Object.values(CAT).map((c) => ({ slug: c.slug, etykieta: c.etykieta, emoji: c.emoji }));

const dania = unique.map((meal) => {
  const cat = CAT[meal.kat];
  const local = hasLocalImg(meal.sku);
  return {
    sku: meal.sku,
    posilek: cat ? cat.slug : "inne",
    nazwa: meal.nazwa,
    obrazek: local ? `img/${meal.sku}.jpg` : meal.img, // lokalna kopia jeśli jest
    obrazekUrl: meal.img, // oryginalny link (zawsze zachowany)
    skladniki: meal.skladniki,
    alergeny: meal.alergeny
      ? meal.alergeny.split(",").map((s) => s.trim()).filter(Boolean)
      : [],
  };
});

const byCat = {};
for (const d of dania) (byCat[d.posilek] ||= []).push(d);

fs.writeFileSync(OUT, JSON.stringify({ zrodlo: "Maczfit", posilki, dania }, null, 2), "utf8");

const zLokalnymi = dania.filter((d) => d.obrazek.startsWith("img/")).length;
console.log(`\nZapisano ${dania.length} unikalnych dań (z ${items.length} pozycji, pominięto ${duplikaty} duplikatów po SKU).`);
for (const p of posilki) console.log(`  ${p.etykieta}: ${(byCat[p.slug] || []).length}`);
console.log(`Obrazki: ${zLokalnymi}/${dania.length} z lokalną kopią (reszta zdalny URL).`);
