// Taulukon kovarianssi on tyyppijärjestelmän tunnetuin aukko.
type Elain = { nimi: string };
type Koira = Elain & { hauku(): string };

const koirat: Koira[] = [{ nimi: "Musti", hauku: () => "hau" }];
const elaimet: Elain[] = koirat;   // sallittu: Koira kelpaa Elaimeksi
elaimet.push({ nimi: "Mirri" });   // sama taulukko: kissa koirien joukkoon

try {
  for (const koira of koirat) console.log(koira.nimi, koira.hauku());
} catch (virhe) {
  console.log(virhe instanceof TypeError ? "TypeError ajossa" : virhe);
}

// Korjaus: lukija saa vain luku -näkymän, johon ei voi lisätä.
function nimet(lista: readonly Elain[]): string {
  return lista.map((e) => e.nimi).join(", ");
}
console.log(nimet(koirat));

// Metodisyntaksilla esitellyn jäsenen parametreja ei tarkisteta
// tiukasti: käsittelijä, joka vaatii koiran, kelpaa eläinten kuuntelijaksi.
interface Kuuntelija {
  kasittele(e: Elain): void;
}
const vainKoirille = (k: Koira): void => console.log(k.hauku());
const kuuntelija: Kuuntelija = { kasittele: vainKoirille };
try {
  kuuntelija.kasittele({ nimi: "Mirri" });
} catch (virhe) {
  console.log(virhe instanceof TypeError ? "TypeError ajossa" : virhe);
}
