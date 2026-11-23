// @alku sarjallistus
const tilaus = {
  id: 17,
  luotu: new Date(Date.UTC(2026, 10, 23, 8, 30)),
  tuotteet: new Map([["kahvi", 2]]),
  tagit: new Set(["kiire"]),
  muistiinpano: undefined,
  summa: () => 0,
};
console.log(JSON.stringify(tilaus));

// Muunnos kerralla: replacer-funktio käsittelee Mapin ja Setin.
const teksti = JSON.stringify(tilaus, (_avain, arvo) =>
  arvo instanceof Map ? Object.fromEntries(arvo)
    : arvo instanceof Set ? [...arvo]
    : arvo, 2);
console.log(teksti);
// @loppu sarjallistus

// @alku jasennys
/**
 * Jäsentää ja validoi tilauksen. JSON.parse palauttaa tyypin any, joten
 * tyyppi on ansaittava tarkistuksilla rajapinnassa.
 * @param {string} json
 * @returns {{ id: number, luotu: Date }}
 */
function lueTilaus(json) {
  /** @type {unknown} */
  const data = JSON.parse(json);
  if (typeof data !== "object" || data === null) {
    throw new TypeError("tilaus ei ole olio");
  }
  if (!("id" in data) || !Number.isInteger(data.id)) {
    throw new TypeError("id puuttuu tai ei ole kokonaisluku");
  }
  if (!("luotu" in data) || typeof data.luotu !== "string") {
    throw new TypeError("luotu puuttuu");
  }
  const luotu = new Date(data.luotu);
  if (Number.isNaN(luotu.getTime())) throw new TypeError("virheellinen aika");
  return { id: /** @type {number} */ (data.id), luotu };
}

const luettu = lueTilaus(teksti);
console.log(luettu.id, luettu.luotu.getUTCHours());
try {
  lueTilaus('{"id": "17"}');
} catch (virhe) {
  console.log(virhe instanceof Error ? virhe.message : virhe);
}
// @loppu jasennys
