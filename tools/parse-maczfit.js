// Parsuje maczfit/maczfit_*.html do maczfit/dania.json.
// Ignoruje daty — zbiera unikalne dania (po SKU z URL obrazka),
// grupując je wg posiłku (śniadanie, ii śniadanie, obiad, podwieczorek, kolacja).
const fs = require("fs");
const path = require("path");

const SRC = path.join(__dirname, "..", "maczfit", "maczfit_posilki_27lipca-14sierpnia2026.html");
const OUT = path.join(__dirname, "..", "maczfit", "dania.json");

const CAT = {
  "ŚNIADANIE": { slug: "sniadanie", etykieta: "Śniadanie", emoji: "🥣" },
  "II ŚNIADANIE": { slug: "drugie-sniadanie", etykieta: "II śniadanie", emoji: "🍎" },
  "OBIAD": { slug: "obiad", etykieta: "Obiad", emoji: "🍲" },
  "PODWIECZOREK": { slug: "podwieczorek", etykieta: "Podwieczorek", emoji: "🥕" },
  "KOLACJA": { slug: "kolacja", etykieta: "Kolacja", emoji: "🥗" },
};

const html = fs.readFileSync(SRC, "utf8");

const decode = (s) =>
  s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
   .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/​/g, "").trim();

// Wyciąga zawartość jednej etykiety (pierwsze wystąpienie).
const grab = (block, tag) => {
  const m = block.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, "i"));
  return m ? decode(m[1].replace(/<[^>]+>/g, "")) : "";
};

const meals = [];
const re = /<div class="meal">([\s\S]*?)<\/div>\s*<\/div>/g;
let m;
while ((m = re.exec(html))) {
  const block = m[1];
  const imgM = block.match(/<img\s+src="([^"]+)"[^>]*alt="([^"]*)"/i);
  if (!imgM) continue;
  const img = imgM[1];
  const skuM = img.match(/SKU\/(\d+)\.jpg/i);
  const sku = skuM ? skuM[1] : img;
  const kat = grab(block, "h3");
  const nazwa = grab(block, "h4") || decode(imgM[2]);
  // Składniki: <p><strong>Składniki:</strong> ...</p>
  const skM = block.match(/<strong>Składniki:<\/strong>([\s\S]*?)<\/p>/i);
  const skladniki = skM ? decode(skM[1]) : "";
  const alM = block.match(/<strong>Alergeny:<\/strong>([\s\S]*?)<\/p>/i);
  const alergeny = alM ? decode(alM[1]) : "";
  meals.push({ sku, img, kat, nazwa, skladniki, alergeny });
}

// Dedupe po SKU, zachowując kolejność.
const seen = new Map();
for (const meal of meals) {
  if (!seen.has(meal.sku)) seen.set(meal.sku, meal);
}
const unique = [...seen.values()];

const posilki = Object.values(CAT).map((c) => ({ slug: c.slug, etykieta: c.etykieta, emoji: c.emoji }));

const dania = unique.map((meal) => {
  const cat = CAT[meal.kat];
  return {
    sku: meal.sku,
    posilek: cat ? cat.slug : "inne",
    nazwa: meal.nazwa,
    obrazek: meal.img,
    skladniki: meal.skladniki,
    alergeny: meal.alergeny
      ? meal.alergeny.split(",").map((s) => s.trim()).filter(Boolean)
      : [],
  };
});

const byCat = {};
for (const d of dania) (byCat[d.posilek] ||= []).push(d);

fs.writeFileSync(OUT, JSON.stringify({ zrodlo: "Maczfit", posilki, dania }, null, 2), "utf8");

console.log(`Zapisano ${dania.length} unikalnych dań (z ${meals.length} pozycji).`);
for (const p of posilki) console.log(`  ${p.etykieta}: ${(byCat[p.slug] || []).length}`);
