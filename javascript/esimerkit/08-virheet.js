// @alku luokat
/** Sovelluksen virheiden kantaluokka. */
class SovellusVirhe extends Error {
  /**
   * @param {string} viesti
   * @param {ErrorOptions} [optiot]  esim. { cause: alkuperainen }
   */
  constructor(viesti, optiot) {
    super(viesti, optiot);
    this.name = new.target.name;   // aliluokan nimi pinojälkeen
  }
}

class EiLoydy extends SovellusVirhe {
  /** @param {string} tunniste */
  constructor(tunniste) {
    super(`ei löydy: ${tunniste}`);
    this.tunniste = tunniste;
  }
}

class KonfiguraatioVirhe extends SovellusVirhe {}
// @loppu luokat

// @alku ketju
/** @param {string} teksti */
function lueAsetukset(teksti) {
  try {
    return JSON.parse(teksti);
  } catch (virhe) {
    // Kääritään: matalan tason virhe säilyy syynä (cause).
    throw new KonfiguraatioVirhe("asetustiedosto on virheellinen", {
      cause: virhe,
    });
  }
}

try {
  lueAsetukset("{ portti: 80 }");
} catch (virhe) {
  if (virhe instanceof KonfiguraatioVirhe) {
    const syy = virhe.cause instanceof Error ? virhe.cause.name : "?";
    console.log(`${virhe.name}: ${virhe.message} (syy: ${syy})`);
  } else {
    throw virhe;   // tuntematon virhe eteenpäin
  }
}
// @loppu ketju

// @alku kasittely
/** @type {Map<string, string>} */
const kayttajat = new Map([["u1", "Aino"]]);

/** @param {string} id */
function haeKayttaja(id) {
  const nimi = kayttajat.get(id);
  if (nimi === undefined) throw new EiLoydy(id);
  return nimi;
}

for (const id of ["u1", "u2"]) {
  try {
    console.log(haeKayttaja(id));
  } catch (virhe) {
    if (!(virhe instanceof EiLoydy)) throw virhe;
    console.log(`404 ${virhe.tunniste}`, virhe instanceof SovellusVirhe);
  } finally {
    console.log(`haettu ${id}`);
  }
}
// @loppu kasittely
