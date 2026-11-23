// Taitopuukartan selaintesti.
//
// Käyttö: node testaa.cjs <rakennushakemisto> [kuvakansio]
//
// Testi käynnistää paikallisen palvelimen, avaa sivun Chromiumissa ja
// tarkistaa, että kartta piirtyy, roolin valinta ja taitojen lisäys
// laskevat polun oikein, osoite säilyttää valinnan ja materiaalilinkit
// osoittavat olemassa oleviin tiedostoihin. Odotetut arvot lasketaan
// samasta taitopuu.json-tiedostosta, jota sivu käyttää.

const http = require("http");
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { TaitopuuAsettelu } = require(path.join(__dirname, "asettelu.js"));

const juuri = path.resolve(process.argv[2] || "rakennus");
const kuvat = process.argv[3] ? path.resolve(process.argv[3]) : null;
const data = JSON.parse(fs.readFileSync(path.join(juuri, "taitopuu.json")));
const taidot = new Map(data.taidot.map((t) => [t.id, t]));

const tyypit = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript",
  ".css": "text/css", ".json": "application/json", ".pdf": "application/pdf",
  ".zip": "application/zip",
};

function esitiedot(id, tulos = new Set()) {
  for (const e of taidot.get(id).edellyttaa) {
    if (!tulos.has(e)) {
      tulos.add(e);
      esitiedot(e, tulos);
    }
  }
  return tulos;
}

function roolinPolku(rooli) {
  const polku = new Set();
  for (const t of rooli.tavoitteet) {
    polku.add(t);
    esitiedot(t, polku);
  }
  return polku;
}

const op = (ids) => [...ids].reduce((a, id) => a + taidot.get(id).laajuus, 0);

let virheita = 0;
function tarkista(ehto, viesti) {
  if (ehto) {
    console.log(`  ok: ${viesti}`);
  } else {
    console.log(`  VIRHE: ${viesti}`);
    virheita++;
  }
}

async function laskuri(sivu) {
  const teksti = await sivu.textContent("#laskuri");
  const m = teksti.match(/(\d+) taitoa · (\d+) op/);
  return m ? { taitoja: Number(m[1]), op: Number(m[2]) } : null;
}

// Asettelun ominaisuudet ilman selainta: niput ja taidot eivät ole
// päällekkäin, ja sama data tuottaa aina saman asettelun.
function tarkistaAsettelu(as, otsikko) {
  const sij = [...as.sijainnit.values()];
  let pieninSolmu = Infinity;
  for (let i = 0; i < sij.length; i++) {
    for (let j = i + 1; j < sij.length; j++) {
      pieninSolmu = Math.min(pieninSolmu,
        Math.hypot(sij[i].x - sij[j].x, sij[i].y - sij[j].y));
    }
  }
  const niput = [...as.niput.values()];
  let pieninVali = Infinity;
  for (let i = 0; i < niput.length; i++) {
    for (let j = i + 1; j < niput.length; j++) {
      const a = niput[i];
      const b = niput[j];
      pieninVali = Math.min(pieninVali,
        Math.hypot(a.x - b.x, a.y - b.y) - a.sade - b.sade);
    }
  }
  tarkista(pieninSolmu > 2 * TaitopuuAsettelu.solmunSade(5) + 60,
    `${otsikko}: taitojen pienin etäisyys ${pieninSolmu.toFixed(0)} px`);
  tarkista(pieninVali > 0,
    `${otsikko}: nippujen pienin väli ${pieninVali.toFixed(0)} px`);
  // Johdinnippu ei saa kulkea vieraan nipun radan läpi.
  let lapikulkuja = 0;
  for (const y of as.nippureitit) {
    for (const c of niput) {
      if (c.id === y.a || c.id === y.b) continue;
      for (let i = 0; i <= 40; i++) {
        const p = TaitopuuAsettelu.bezier(y.alku, y.ohjaus, y.loppu, i / 40);
        if (Math.hypot(p.x - c.x, p.y - c.y) < c.radanSade + 30) {
          lapikulkuja++;
          break;
        }
      }
    }
  }
  tarkista(lapikulkuja === 0,
    `${otsikko}: johdinniput eivät kulje vieraiden ratojen läpi ` +
    `(${lapikulkuja})`);
}

async function main() {
  console.log("Asettelu:");
  const as1 = TaitopuuAsettelu.laske(data);
  const as2 = TaitopuuAsettelu.laske(data);
  tarkistaAsettelu(as1, "oletusasettelu");
  tarkista([...as1.sijainnit].every(([id, p]) =>
    p.x === as2.sijainnit.get(id).x && p.y === as2.sijainnit.get(id).y),
  "asettelu on deterministinen");
  const yhteyksiaYht = data.taidot.reduce((a, t) => a + t.edellyttaa.length, 0);
  tarkista(as1.reitit.length === yhteyksiaYht,
    `jokaiselle yhteydelle on reitti (${as1.reitit.length})`);
  // Nipun siirto: kiinnitetty nippu pysyy paikallaan ja muut väistävät.
  const siirretty = [...as1.niput.values()][3];
  const aiempi = new Map([...as1.niput].map(([id, n]) => [id, { x: n.x, y: n.y }]));
  aiempi.set(siirretty.id, { x: 0, y: 0 });
  const as3 = TaitopuuAsettelu.laske(data, aiempi, new Set([siirretty.id]));
  tarkistaAsettelu(as3, "nippu siirretty keskelle");
  // Valinnainen nippu-kenttä jakaa alueen kahteen nippuun.
  const jaettu = JSON.parse(JSON.stringify(data));
  const alue = jaettu.taidot[jaettu.taidot.length - 1].alue;
  jaettu.taidot.filter((t) => t.alue === alue).slice(0, 2)
    .forEach((t) => { t.nippu = "erillinen"; });
  const as4 = TaitopuuAsettelu.laske(jaettu);
  tarkista(as4.niput.size === as1.niput.size + 1,
    `nippu-kenttä luo oman nipun (${as4.niput.size})`);
  tarkistaAsettelu(as4, "jaettu alue");


  const palvelin = http.createServer((pyynto, vastaus) => {
    const osoite = decodeURIComponent(new URL(pyynto.url, "http://x").pathname);
    const tiedosto = path.join(juuri, osoite === "/" ? "index.html" : osoite);
    if (!tiedosto.startsWith(juuri) || !fs.existsSync(tiedosto)) {
      vastaus.writeHead(404);
      vastaus.end();
      return;
    }
    vastaus.writeHead(200, {
      "Content-Type": tyypit[path.extname(tiedosto)] || "application/octet-stream",
    });
    fs.createReadStream(tiedosto).pipe(vastaus);
  });
  await new Promise((ok) => palvelin.listen(0, "127.0.0.1", ok));
  const osoite = `http://127.0.0.1:${palvelin.address().port}/`;

  const selain = await chromium.launch();
  const sivu = await selain.newPage({ viewport: { width: 1400, height: 900 } });
  const konsolivirheet = [];
  sivu.on("console", (v) => {
    if (v.type() === "error") konsolivirheet.push(v.text());
  });
  sivu.on("pageerror", (v) => konsolivirheet.push(String(v)));
  // Testi ei riipu ulkoisista fonteista.
  const tyhjaFontti = (r) => r.fulfill({ status: 200, body: "" });
  await sivu.route(/fonts\.(googleapis|gstatic)\.com/, tyhjaFontti);

  console.log("Taitopuukartta:");
  await sivu.goto(osoite);
  await sivu.waitForSelector("html[data-valmis='true']");

  const solmuja = await sivu.locator(".solmu").count();
  tarkista(solmuja === data.taidot.length,
    `kartalla ${solmuja} taitoa (odotettu ${data.taidot.length})`);
  const reitteja = await sivu.locator(".reitti").count();
  const yhteyksia = data.taidot.reduce((a, t) => a + t.edellyttaa.length, 0);
  tarkista(reitteja === yhteyksia,
    `kartalla ${reitteja} yhteyttä (odotettu ${yhteyksia})`);

  // Ensimmäisellä käynnillä ensimmäinen rooli on valittuna.
  const eka = data.roolit[0];
  let l = await laskuri(sivu);
  const ekaPolku = roolinPolku(eka);
  tarkista(l && l.taitoja === ekaPolku.size && l.op === op(ekaPolku),
    `oletusrooli ${eka.nimi}: ${l && l.taitoja} taitoa, ${l && l.op} op`);
  if (kuvat) {
    await sivu.emulateMedia({ colorScheme: "dark" });
    await sivu.screenshot({ path: path.join(kuvat, "tumma.png") });
    await sivu.click("#lahenna");
    await sivu.click("#lahenna");
    await sivu.screenshot({ path: path.join(kuvat, "tumma-lahi.png") });
    await sivu.click("#sovita");
    await sivu.emulateMedia({ colorScheme: "light" });
  }

  // Jokainen rooli.
  for (const rooli of data.roolit) {
    await sivu.click(`.rooli-nappi[data-id='${rooli.id}']`);
    if (rooli.id === eka.id) {
      // Valitun roolin uudelleenklikkaus poistaa roolikorostuksen,
      // valinta säilyy.
      await sivu.click(`.rooli-nappi[data-id='${rooli.id}']`);
    }
    l = await laskuri(sivu);
    const polku = roolinPolku(rooli);
    tarkista(l.taitoja === polku.size && l.op === op(polku),
      `rooli ${rooli.nimi}: ${l.taitoja} taitoa, ${l.op} op`);
    const hash = await sivu.evaluate(() => location.hash);
    tarkista(hash === `#rooli-${rooli.id}`, `osoite ${hash}`);
  }

  // Tyhjennys ja yksittäisen taidon lisääminen paneelin napilla.
  await sivu.click("#tyhjenna");
  l = await laskuri(sivu);
  tarkista(l.taitoja === 0, "tyhjennys poistaa kaikki valinnat");

  const kohde = data.taidot.reduce((a, b) => (b.taso > a.taso ? b : a));
  await sivu.locator(`.solmu[data-id='${kohde.id}']`).dispatchEvent("click");
  const otsikko = await sivu.textContent("#paneeli h2");
  tarkista(otsikko === kohde.nimi, `paneeli näyttää taidon ${otsikko}`);
  await sivu.click("#paneeli .nappi.ensisijainen");
  const odotettu = esitiedot(kohde.id);
  odotettu.add(kohde.id);
  l = await laskuri(sivu);
  tarkista(l.taitoja === odotettu.size && l.op === op(odotettu),
    `${kohde.nimi} esitietoineen: ${l.taitoja} taitoa, ${l.op} op`);

  // Esitiedon poistaminen poistaa myös sen varaan rakentuvat taidot.
  const pohja = [...odotettu].find((id) => taidot.get(id).taso === 1);
  await sivu.locator(`.solmu[data-id='${pohja}']`).dblclick();
  l = await laskuri(sivu);
  const jaljella = [...odotettu].filter(
    (id) => id !== pohja && !esitiedot(id).has(pohja));
  tarkista(l.taitoja === jaljella.length,
    `esitiedon poisto jättää ${l.taitoja} taitoa (odotettu ${jaljella.length})`);

  // Osoite säilyttää valinnan uudelleenlatauksessa.
  const ennen = await laskuri(sivu);
  await sivu.reload();
  await sivu.waitForSelector("html[data-valmis='true']");
  l = await laskuri(sivu);
  tarkista(l.taitoja === ennen.taitoja && l.op === ennen.op,
    "valinta säilyy uudelleenlatauksessa");

  // Nipun raahaaminen siirtää nippua, eikä nippuja jää päällekkäin.
  const nippu = sivu.locator(".nippu").nth(4);
  const ennenX = Number(await nippu.getAttribute("data-x"));
  const laatikko = await nippu.locator(".nippu-alusta").boundingBox();
  const lx = laatikko.x + laatikko.width / 2;
  const ly = laatikko.y + laatikko.height * 0.12;
  await sivu.mouse.move(lx, ly);
  await sivu.mouse.down();
  for (let i = 1; i <= 10; i++) await sivu.mouse.move(lx + 12 * i, ly + 6 * i);
  await sivu.mouse.up();
  const jalkeenX = Number(await nippu.getAttribute("data-x"));
  tarkista(Math.abs(jalkeenX - ennenX) > 20,
    `nippu siirtyi raahattaessa (${ennenX.toFixed(0)} → ${jalkeenX.toFixed(0)})`);
  const niputDom = await sivu.$$eval(".nippu", (gs) => gs.map((g) => ({
    x: Number(g.dataset.x), y: Number(g.dataset.y), r: Number(g.dataset.r),
  })));
  let pienin = Infinity;
  for (let i = 0; i < niputDom.length; i++) {
    for (let j = i + 1; j < niputDom.length; j++) {
      const a = niputDom[i];
      const b = niputDom[j];
      pienin = Math.min(pienin, Math.hypot(a.x - b.x, a.y - b.y) - a.r - b.r);
    }
  }
  tarkista(pienin > 0, `raahauksen jälkeen niput eivät ole päällekkäin (${pienin.toFixed(0)} px)`);
  await sivu.click("#jarjesta");
  const palautettuX = Number(await nippu.getAttribute("data-x"));
  tarkista(Math.abs(palautettuX - ennenX) < 0.5, "asettelun palautus");

  // Haku korostaa osumat.
  await sivu.fill("#haku", "verilator");
  const osumat = await sivu.locator(".solmu.osuma").count();
  const odotetut = data.taidot.filter((t) =>
    [t.nimi, t.kuvaus, t.testaus, ...t.aiheet]
      .join(" ").toLowerCase().includes("verilator")).length;
  tarkista(osumat === odotetut && osumat > 0,
    `haku "verilator": ${osumat} osumaa`);
  await sivu.fill("#haku", "");

  // Valmiin taidon materiaalilinkit osoittavat olemassa oleviin tiedostoihin.
  for (const t of data.taidot.filter((x) => x.materiaalit)) {
    for (const avain of ["pdf", "esimerkit"]) {
      const polku = t.materiaalit[avain];
      tarkista(polku && fs.existsSync(path.join(juuri, polku)),
        `${t.nimi}: ${avain} ${polku}`);
    }
  }

  if (kuvat) {
    await sivu.goto(osoite + "#rooli-" + data.roolit[1].id);
    await sivu.waitForSelector("html[data-valmis='true']");
    const valmis = data.taidot.find((x) => x.materiaalit);
    await sivu.locator(`.solmu[data-id='${valmis.id}']`).dispatchEvent("click");
    await sivu.emulateMedia({ colorScheme: "light" });
    await sivu.screenshot({ path: path.join(kuvat, "vaalea.png") });
    const puhelin = await selain.newPage({
      viewport: { width: 390, height: 844 }, deviceScaleFactor: 1,
    });
    await puhelin.route(/fonts\.(googleapis|gstatic)\.com/, tyhjaFontti);
    await puhelin.goto(osoite + "#rooli-" + data.roolit[0].id);
    await puhelin.waitForSelector("html[data-valmis='true']");
    await puhelin.screenshot({ path: path.join(kuvat, "puhelin.png") });
    const leveys = await puhelin.evaluate(
      () => document.documentElement.scrollWidth);
    tarkista(leveys <= 390, `puhelinnäkymä ei vieritä sivusuunnassa (${leveys}px)`);
  }

  tarkista(konsolivirheet.length === 0,
    `ei konsolivirheitä${konsolivirheet.length ? ": " + konsolivirheet.join("; ") : ""}`);

  await selain.close();
  palvelin.close();
  if (virheita) {
    console.log(`VIRHEITÄ: ${virheita}`);
    process.exit(1);
  }
  console.log("OK: taitopuukartta toimii.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
