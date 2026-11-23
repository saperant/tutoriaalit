import { setTimeout as odota } from "node:timers/promises";

// @alku perus
const nimi = "Aino";                  // const oletuksena, let jos muuttuu
const ika = Number("42");             // NaN, jos ei luku
const tervehdys = `Hei ${nimi}, ${ika + 1} v`;
const raja = process.env.RAJA ?? "5000";  // vain null/undefined -> oletus
/** @type {{ katu?: string } | undefined} */
const asiakas = JSON.parse('{"katu": "Hämeenk. 1"}');
const osoite = asiakas?.katu ?? "ei osoitetta";
console.log(tervehdys, raja, osoite, 0.1 + 0.2 === 0.3);
// @loppu perus

// @alku funktiot
/**
 * @param {string} polku
 * @param {{ yrityksia?: number }} [optiot]
 */
function hae(polku, { yrityksia = 3 } = {}) {
  return `${polku} x${yrityksia}`;
}
/** @param {...number} xs */
const summa = (...xs) => xs.reduce((a, b) => a + b, 0);
console.log(hae("/api"), summa(...[1, 2, 3]));
// @loppu funktiot

// @alku oliot
class Tili {
  #saldo = 0;
  static avaa() { return new Tili(); }
  get saldo() { return this.#saldo; }
  /** @param {number} s */
  talleta(s) {
    if (!(s > 0)) throw new RangeError(`summa ${s}`);
    this.#saldo += s;
    return this;
  }
}
const { saldo } = Tili.avaa().talleta(100);
const kopio = structuredClone({ a: [1], d: new Date(0) });
console.log(saldo, { ...kopio, b: 2 });
// @loppu oliot

// @alku kokoelmat
const luvut = [10, 9, 1];
console.log(luvut.toSorted((a, b) => a - b), luvut.at(-1));
const kartta = new Map([["kahvi", 2]]);
kartta.set("tee", (kartta.get("tee") ?? 0) + 1);
const ryhmat = Object.groupBy(["aa", "b", "cc"], (s) => String(s.length));
console.log([...kartta], [...new Set([1, 1, 2])]);
console.log(JSON.stringify(ryhmat));
// @loppu kokoelmat

// @alku async
/** @param {number} ms */
async function viive(ms) {
  await odota(ms);
  return ms;
}
const tulokset = await Promise.allSettled([viive(5), viive(1)]);
const signaali = AbortSignal.timeout(1000);
try {
  await odota(1, undefined, { signal: signaali });
} catch (virhe) {
  if (!(virhe instanceof Error) || virhe.name !== "AbortError") throw virhe;
}
console.log(tulokset.map((t) => t.status));
// @loppu async
