// @alku tyypit
/**
 * Eroteltu unioni (tagged union): kenttä `laji` kertoo muodon.
 * @typedef {{ laji: "ympyra", r: number }} Ympyra
 * @typedef {{ laji: "suorakaide", leveys: number, korkeus: number }}
 *   Suorakaide
 * @typedef {{ laji: "kolmio", kanta: number, korkeus: number }} Kolmio
 * @typedef {Ympyra | Suorakaide | Kolmio} Muoto
 */
// @loppu tyypit

// @alku kattava
/**
 * Tarkistin varmistaa, että jokainen laji käsitellään: jos uusi laji
 * lisätään unioniin, `default`-haaran sijoitus tyyppiin never
 * epäonnistuu.
 * @param {Muoto} m
 * @returns {number}
 */
function pinta(m) {
  switch (m.laji) {
    case "ympyra":
      return Math.PI * m.r ** 2;
    case "suorakaide":
      return m.leveys * m.korkeus;
    case "kolmio":
      return (m.kanta * m.korkeus) / 2;
    default: {
      /** @type {never} */
      const kasittelematon = m;
      throw new TypeError(`tuntematon: ${JSON.stringify(kasittelematon)}`);
    }
  }
}
// @loppu kattava

/** @type {Muoto[]} */
const muodot = [
  { laji: "ympyra", r: 1 },
  { laji: "suorakaide", leveys: 2, korkeus: 3 },
  { laji: "kolmio", kanta: 4, korkeus: 5 },
];
for (const m of muodot) {
  console.log(m.laji.padEnd(11), pinta(m).toFixed(2));
}
