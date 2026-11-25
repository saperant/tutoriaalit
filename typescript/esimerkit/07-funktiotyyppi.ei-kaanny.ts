// Funktio-ominaisuutena esitellyn jäsenen parametrit tarkistetaan
// (strictFunctionTypes): koiran vaativa käsittelijä ei kelpaa.
type Elain = { nimi: string };
type Koira = Elain & { hauku(): string };

interface Kuuntelija {
  kasittele: (e: Elain) => void;
}
const vainKoirille = (k: Koira): void => console.log(k.hauku());
const kaikille = (e: Elain): void => console.log(e.nimi);

const kuuntelijat: Kuuntelija[] = [
  { kasittele: kaikille },
  { kasittele: vainKoirille },   // @virhe
];
for (const k of kuuntelijat) k.kasittele({ nimi: "Mirri" });
