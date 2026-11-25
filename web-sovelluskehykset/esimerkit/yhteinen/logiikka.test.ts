// Logiikan yksikkötestit Noden omalla testiajurilla: node --test.
import assert from "node:assert/strict";
import { test } from "node:test";
import {
  haeTehtavat, laske, lisaa, lueTallennetut, otsikko, poista,
  poistaValmiit, suodata, tallenna, vaihda, validoi, yhteenveto,
  type Tehtava,
} from "./logiikka.ts";

const lista: Tehtava[] = [
  { id: 1, nimi: "Varaa huone", kiire: "kiireellinen", valmis: false },
  { id: 2, nimi: "Tilaa kahvit", kiire: "tavallinen", valmis: true },
];

function muisti(alku: Record<string, string> = {}) {
  const data = new Map(Object.entries(alku));
  return {
    getItem: (k: string) => data.get(k) ?? null,
    setItem: (k: string, v: string) => { data.set(k, v); },
  };
}

// @alku muutokset
test("muutokset eivät muuta alkuperäistä listaa", () => {
  const kopio = structuredClone(lista);
  const uusi = lisaa(lista, "  Kirjoita muistio ", "tavallinen");
  assert.deepEqual(uusi.at(-1),
    { id: 3, nimi: "Kirjoita muistio", kiire: "tavallinen", valmis: false });
  assert.equal(vaihda(lista, 1)[0]?.valmis, true);
  assert.deepEqual(poista(lista, 1).map((t) => t.id), [2]);
  assert.deepEqual(poistaValmiit(lista).map((t) => t.id), [1]);
  assert.deepEqual(lista, kopio);
});
// @loppu muutokset

test("johdetut arvot lasketaan tilasta", () => {
  assert.deepEqual(laske(lista), { avoimia: 1, valmiita: 1 });
  assert.equal(yhteenveto(lista), "1 avoin, 1 valmis");
  assert.equal(yhteenveto([]), "0 avointa, 0 valmista");
  assert.equal(otsikko(lista), "Tehtävät (1)");
  assert.deepEqual(suodata(lista, "avoimet").map((t) => t.id), [1]);
  assert.deepEqual(suodata(lista, "valmiit").map((t) => t.id), [2]);
  assert.equal(suodata(lista, "kaikki"), lista);
});

test("validointi", () => {
  assert.match(validoi(" ab ", lista) ?? "", /vähintään 3/);
  assert.match(validoi("x".repeat(41), lista) ?? "", /enintään 40/);
  assert.match(validoi("tilaa KAHVIT", lista) ?? "", /jo listalla/);
  assert.equal(validoi("Kirjoita muistio", lista), null);
});

test("tallennus ja lataus", async () => {
  const varasto = muisti();
  assert.equal(lueTallennetut(varasto), null);
  tallenna(varasto, lista);
  assert.deepEqual(lueTallennetut(varasto), lista);
  assert.equal(lueTallennetut(muisti({ tehtavat: "[{}]" })), null);

  // Tallennettu lista ohittaa verkon.
  const eiVerkkoa = () => Promise.reject(new Error("ei pitäisi hakea"));
  assert.deepEqual(await haeTehtavat(varasto, eiVerkkoa), lista);

  const palvelin = (tila: number) => () =>
    Promise.resolve(new Response(JSON.stringify(lista), { status: tila }));
  assert.deepEqual(await haeTehtavat(muisti(), palvelin(200)), lista);
  await assert.rejects(haeTehtavat(muisti(), palvelin(500)), /HTTP 500/);
});
