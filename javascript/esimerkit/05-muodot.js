// V8:n sisäiset diagnostiikkafunktiot (%-alkuiset) eivät ole osa
// JavaScriptia. Ne otetaan tässä käyttöön vain havainnollistamiseen.
import { setFlagsFromString } from "node:v8";

setFlagsFromString("--allow-natives-syntax");
const samaMuoto = new Function("a", "b", "return %HaveSameMap(a, b)");
const nopeat = new Function("o", "return %HasFastProperties(o)");

// @alku muodot
/**
 * @param {number} x
 * @param {number} y
 */
function piste(x, y) {
  return { x, y };   // kentät aina samassa järjestyksessä
}

const a = piste(1, 2);
const b = piste(3, 4);
const c = { y: 1, x: 2 };          // eri järjestys = eri muoto
/** @type {{ x: number, y: number, z?: number }} */
const d = piste(5, 6);
d.z = 7;                          // kenttä lisätty jälkikäteen
console.log(samaMuoto(a, b), samaMuoto(a, c), samaMuoto(a, d));

/** @type {{ x: number, y?: number }} */
const e = piste(8, 9);
delete e.y;                       // olio siirtyy hitaaseen sanakirjatilaan
const f = { ...piste(8, 9), y: undefined };   // muoto säilyy
console.log(nopeat(a), nopeat(e), nopeat(f));
// @loppu muodot
