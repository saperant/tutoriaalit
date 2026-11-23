// @alku kopiot
const tilaus = {
  asiakas: "Aino",
  rivit: [{ tuote: "kahvi", maara: 2 }],
  luotu: new Date(Date.UTC(2026, 0, 15)),
};

const viite = tilaus;                    // sama olio
const matala = { ...tilaus };            // uusi olio, samat sisäoliot
const syva = structuredClone(tilaus);    // kaikki kopioitu, Date säilyy

tilaus.rivit[0].maara = 5;
console.log(viite.rivit[0].maara, matala.rivit[0].maara,
  syva.rivit[0].maara);
console.log(syva.luotu instanceof Date, syva.luotu.toISOString());
// @loppu kopiot

// @alku jaadytys
// ES-moduli on aina tiukassa tilassa: kirjoitus jäädytettyyn heittää.
const asetukset = Object.freeze({
  portti: 8080,
  sallitut: ["localhost"],
});
try {
  // @ts-expect-error: kenttä on vain luku -tyyppiä
  asetukset.portti = 80;
} catch (virhe) {
  console.log(virhe instanceof TypeError);
}
asetukset.sallitut.push("0.0.0.0");   // Object.freeze on matala
console.log(asetukset.portti, asetukset.sallitut);
// @loppu jaadytys

// @alku syvajaadytys
/**
 * Jäädyttää olion ja kaikki sen sisäoliot.
 * @template {object} T
 * @param {T} olio
 * @returns {Readonly<T>}
 */
function syvaJaadyta(olio) {
  for (const arvo of Object.values(olio)) {
    if (typeof arvo === "object" && arvo !== null) syvaJaadyta(arvo);
  }
  return Object.freeze(olio);
}
const vakio = syvaJaadyta({ verot: { ruoka: 0.135, yleinen: 0.255 } });
console.log(Object.isFrozen(vakio.verot));
// @loppu syvajaadytys
