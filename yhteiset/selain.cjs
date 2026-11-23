#!/usr/bin/env node
// Avaa HTML-esimerkin Chromiumissa ja tulostaa siitä deterministisen
// raportin, jota testaaja vertaa tiedostoon <nimi>.odotettu.
//
// Käyttö:  node yhteiset/selain.cjs <sivu.html>
//
// Sivu ladataan ilman verkkoa: vain file://-osoitteet sallitaan. Konsolin
// virheet ja varoitukset, sivun poikkeukset ja estetyt pyynnöt kirjoitetaan
// virhetulosteeseen, ja paluuarvo on silloin 1.
//
// Raportti, kullekin leveydelle (oletus 1024 px, muutettavissa
// elementillä <meta name="testi:leveydet" content="360 1024">):
//
//   [leveys 360 px]
//   <nimi>: x=0 y=0 l=360 k=48        elementit, joilla data-mitta="nimi"
//   <nimi>: color=rgb(0, 0, 0)        data-tyyli="color" (laskettu arvo)
//
// Lopuksi [saavutettavuuspuu]: sivun saavutettavuuspuu sellaisena kuin
// ruudunlukija sen näkee (Playwrightin ARIA-tilannekuva). Sen voi jättää
// pois elementillä <meta name="testi:saavutettavuus" content="ei">.
// Sivun console.log-viestit tulostetaan otsikon [konsoli] alle.
//
// Fonttien mitat vaihtelevat koneittain, joten sivun oletusfontiksi
// asetetaan DejaVu Sans. Esimerkkien kannattaa käyttää sitä myös omissa
// tyyleissään, jos niiden korkeuksia mitataan.
//
// Ympäristömuuttuja SELAIN_KUVA=polku tallentaa kustakin leveydestä
// kuvakaappauksen tiedostoon polku-<leveys>.png (kuvitusta varten).

"use strict";

const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");

const OLETUSFONTTI = ':root { font-family: "DejaVu Sans", sans-serif; }';

async function main() {
  const tiedosto = process.argv[2];
  if (!tiedosto) {
    console.error("käyttö: node selain.cjs <sivu.html>");
    return 2;
  }
  const osoite = pathToFileURL(path.resolve(tiedosto)).href;
  const virheet = [];
  const konsoli = [];

  const selain = await chromium.launch({ args: ["--font-render-hinting=none"] });
  try {
    const sivu = await selain.newPage({
      viewport: { width: 1024, height: 768 },
      deviceScaleFactor: 1,
      locale: "fi-FI",
      reducedMotion: "reduce",
    });
    await sivu.route("**/*", (reitti) => {
      const url = reitti.request().url();
      if (url.startsWith("file:") || url.startsWith("data:")) {
        return reitti.continue();
      }
      virheet.push(`estetty verkkopyyntö: ${url}`);
      return reitti.abort();
    });
    sivu.on("console", (viesti) => {
      const tyyppi = viesti.type();
      if (tyyppi === "error" || tyyppi === "warning") {
        virheet.push(`konsoli (${tyyppi}): ${viesti.text()}`);
      } else if (tyyppi === "log" || tyyppi === "info") {
        konsoli.push(viesti.text());
      }
    });
    sivu.on("pageerror", (virhe) => virheet.push(`poikkeus: ${virhe.message}`));
    sivu.on("requestfailed", (pyynto) => {
      if (pyynto.url().startsWith("file:")) {
        virheet.push(`tiedostoa ei löydy: ${pyynto.url()}`);
      }
    });

    await sivu.goto(osoite, { waitUntil: "load" });
    await sivu.addStyleTag({ content: OLETUSFONTTI });
    await sivu.evaluate(() => document.fonts.ready);

    const meta = (nimi) => sivu.evaluate((n) => {
      const e = document.querySelector(`meta[name="${n}"]`);
      return e ? e.getAttribute("content") : null;
    }, nimi);
    const leveydet = ((await meta("testi:leveydet")) ?? "1024")
      .split(/\s+/).filter(Boolean).map(Number);
    const saavutettavuus = (await meta("testi:saavutettavuus")) !== "ei";

    const rivit = [];
    for (const leveys of leveydet) {
      await sivu.setViewportSize({ width: leveys, height: 768 });
      rivit.push(`[leveys ${leveys} px]`);
      rivit.push(...await sivu.evaluate(() => {
        const tulos = [];
        const nimi = (e) => e.dataset.mitta || e.dataset.nimi ||
          e.tagName.toLowerCase() + (e.id ? `#${e.id}` : "");
        for (const e of document.querySelectorAll("[data-mitta], [data-tyyli]")) {
          if (e.dataset.mitta) {
            const r = e.getBoundingClientRect();
            const n = (v) => Math.round(v);
            const nakyva = getComputedStyle(e).display !== "none";
            tulos.push(nakyva
              ? `${nimi(e)}: x=${n(r.x)} y=${n(r.y + scrollY)} ` +
                `l=${n(r.width)} k=${n(r.height)}`
              : `${nimi(e)}: piilossa`);
          }
          if (e.dataset.tyyli) {
            const tyyli = getComputedStyle(e);
            const arvot = e.dataset.tyyli.split(/\s+/).filter(Boolean)
              .map((p) => `${p}=${tyyli.getPropertyValue(p)}`);
            tulos.push(`${nimi(e)}: ${arvot.join("; ")}`);
          }
        }
        return tulos;
      }));
      if (process.env.SELAIN_KUVA) {
        await sivu.screenshot({
          path: `${process.env.SELAIN_KUVA}-${leveys}.png`, fullPage: true,
        });
      }
    }
    if (saavutettavuus) {
      rivit.push("[saavutettavuuspuu]");
      rivit.push(await sivu.locator("body").ariaSnapshot());
    }
    if (konsoli.length > 0) {
      rivit.push("[konsoli]", ...konsoli);
    }
    console.log(rivit.join("\n"));
  } finally {
    await selain.close();
  }
  for (const v of virheet) console.error(v);
  return virheet.length > 0 ? 1 : 0;
}

main().then((koodi) => { process.exitCode = koodi; }, (virhe) => {
  console.error(virhe);
  process.exitCode = 1;
});
