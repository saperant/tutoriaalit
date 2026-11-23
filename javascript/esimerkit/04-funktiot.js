// @alku parametrit
/**
 * Optiot-olio nimettyinä parametreina; oletusarvot purkamisessa.
 * @param {string} osoite
 * @param {{ yrityksia?: number, viive?: number, otsakkeet?: string[] }}
 *   [optiot]
 */
function pyynto(
  osoite,
  { yrityksia = 3, viive = 100, otsakkeet = [] } = {},
) {
  return `${osoite} yrityksia=${yrityksia} viive=${viive} ` +
    `otsakkeita=${otsakkeet.length}`;
}
console.log(pyynto("/api/tilaukset"));
console.log(pyynto("/api/tilaukset", { viive: 500 }));
// @loppu parametrit

// @alku rest
/** @param {...number} luvut */
function keskiarvo(...luvut) {
  if (luvut.length === 0) throw new RangeError("ei lukuja");
  return luvut.reduce((a, b) => a + b, 0) / luvut.length;
}
const mittaukset = [21.5, 22.0, 23.1];
console.log(keskiarvo(...mittaukset).toFixed(2), Math.max(...mittaukset));
// @loppu rest

// @alku arvoina
/**
 * Koostaa funktiot putkeksi vasemmalta oikealle.
 * @template T
 * @param {...((arvo: T) => T)} vaiheet
 * @returns {(arvo: T) => T}
 */
const putki = (...vaiheet) => (arvo) => vaiheet.reduce((a, f) => f(a), arvo);

/** @type {(s: string) => string} */
const siisti = putki(
  (s) => s.trim(),
  (s) => s.replace(/\s+/g, " "),
  (s) => s.toLowerCase(),
);
console.log(JSON.stringify(siisti("  Moi   Maailma \n")));
// @loppu arvoina
