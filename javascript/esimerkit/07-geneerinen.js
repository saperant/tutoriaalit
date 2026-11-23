// @alku tulos
/**
 * Tulos-tyyppi odotetuille epäonnistumisille.
 * @template T
 * @typedef {{ ok: true, arvo: T } | { ok: false, virhe: string }} Tulos
 */

/**
 * @template T
 * @param {T} arvo
 * @returns {Tulos<T>}
 */
const onnistui = (arvo) => ({ ok: true, arvo });

/**
 * @param {string} virhe
 * @returns {Tulos<never>}
 */
const epaonnistui = (virhe) => ({ ok: false, virhe });
// @loppu tulos

// @alku kaytto
/**
 * @param {string} teksti
 * @returns {Tulos<number>}
 */
function luePostinumero(teksti) {
  return /^\d{5}$/.test(teksti)
    ? onnistui(Number(teksti))
    : epaonnistui(`ei postinumero: ${JSON.stringify(teksti)}`);
}

for (const syote of ["00100", "1234", "33720"]) {
  const tulos = luePostinumero(syote);
  // Tarkistin kaventaa tyypin ok-kentän perusteella.
  console.log(tulos.ok ? `ok ${tulos.arvo}` : `virhe: ${tulos.virhe}`);
}
// @loppu kaytto

// @alku rajoite
/**
 * Geneerinen funktio rajoitteella: avain on T:n kenttä.
 * @template T
 * @template {keyof T} K
 * @param {readonly T[]} lista
 * @param {K} kentta
 * @returns {Map<T[K], T[]>}
 */
function ryhmittele(lista, kentta) {
  /** @type {Map<T[K], T[]>} */
  const tulos = new Map();
  for (const alkio of lista) {
    const avain = alkio[kentta];
    tulos.set(avain, [...(tulos.get(avain) ?? []), alkio]);
  }
  return tulos;
}

const henkilot = [
  { nimi: "Aino", kunta: "Tampere" },
  { nimi: "Eero", kunta: "Oulu" },
  { nimi: "Iida", kunta: "Tampere" },
];
const kunnittain = ryhmittele(henkilot, "kunta");
console.log([...kunnittain].map(([k, h]) => `${k}: ${h.length}`));
// ryhmittele(henkilot, "ika") olisi tyyppivirhe: ei kenttää "ika".
// @loppu rajoite
