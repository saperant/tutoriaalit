// @alku metatieto
/**
 * Pyyntökohtainen metatieto ilman, että pyyntöolioon lisätään kenttiä.
 * WeakMap ei pidä avainta elossa: kun pyyntö vapautuu, tietokin vapautuu.
 * @type {WeakMap<object, { alku: number, kayttaja: string }>}
 */
const metatiedot = new WeakMap();

/** @param {object} pyynto */
function tunnista(pyynto) {
  metatiedot.set(pyynto, { alku: 1000, kayttaja: "aino" });
}

/** @param {object} pyynto */
function kirjaa(pyynto) {
  const tieto = metatiedot.get(pyynto);
  return tieto ? `${tieto.kayttaja} @ ${tieto.alku}` : "tuntematon";
}

const pyynto = { polku: "/tilaukset" };
tunnista(pyynto);
console.log(kirjaa(pyynto), kirjaa({ polku: "/muu" }));
console.log(Object.keys(pyynto));    // olio on ennallaan
// @loppu metatieto

// @alku avaimet
try {
  // @ts-expect-error: WeakMapin avain ei voi olla primitiivi
  metatiedot.set("teksti", { alku: 0, kayttaja: "" });
} catch (virhe) {
  console.log(virhe instanceof TypeError);
}
// @loppu avaimet
