// Oliotyypit: interface ja type, valinnaiset ja readonly-kentät.
interface Asiakas {
  readonly id: string;
  nimi: string;
  sahkoposti?: string; // valinnainen: string | undefined
}

// interface voi laajentaa; type yhdistää leikkauksella (&).
interface Yritysasiakas extends Asiakas {
  ytunnus: string;
}
type Aikaleimattu = { luotu: Date };
type Tallennettu = Yritysasiakas & Aikaleimattu;

const a: Tallennettu = {
  id: "A-17", nimi: "Oy Esimerkki Ab", ytunnus: "1234567-8",
  luotu: new Date(Date.UTC(2026, 0, 2)),
};
a.nimi = "Esimerkki Oyj"; // sallittu
// a.id = "A-18";         // virhe: id on readonly

function yhteystieto(x: Asiakas): string {
  return x.sahkoposti ?? "(ei sähköpostia)";
}
console.log(a.nimi, a.ytunnus, yhteystieto(a), a.luotu.getUTCFullYear());

// Indeksiallekirjoitus: vapaat avaimet, samantyyppiset arvot.
interface Varasto { [tuote: string]: number }
const varasto: Varasto = { omena: 12, leipa: 3 };
varasto["maito"] = 8;
console.log(Object.keys(varasto).length);

// readonly on vain käännösaikainen; Object.freeze estää myös ajossa.
const asetukset: Readonly<{ alv: number }> = Object.freeze({ alv: 0.255 });
console.log(asetukset.alv);
