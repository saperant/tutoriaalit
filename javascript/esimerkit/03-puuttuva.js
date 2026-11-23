/**
 * @typedef {object} Asetukset
 * @property {number} [aikaraja]  millisekunteina, puuttuu = oletus
 * @property {{ osoite?: string } | null} [valityspalvelin]
 */

const OLETUSRAJA = 5000;

// @alku kasittely
/** @param {Asetukset} asetukset */
function kuvaa(asetukset) {
  const raja1 = asetukset.aikaraja || OLETUSRAJA;  // väärin: 0 hylätään
  const raja2 = asetukset.aikaraja ?? OLETUSRAJA;  // oikein
  const osoite = asetukset.valityspalvelin?.osoite ?? "suora yhteys";
  console.log(`${raja1} ${raja2} ${osoite}`);
}

kuvaa({});
kuvaa({ aikaraja: 0, valityspalvelin: null });
kuvaa({ aikaraja: 200, valityspalvelin: { osoite: "proxy:3128" } });
// @loppu kasittely

// @alku ero
/** @type {Record<string, number | undefined>} */
const varasto = { kahvi: 0, tee: undefined };
console.log(varasto.kahvi, varasto.tee, varasto.mehu);
console.log("tee" in varasto, "mehu" in varasto);
console.log(Object.hasOwn(varasto, "tee"), JSON.stringify(varasto));
// @loppu ero
