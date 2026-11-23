// Kuvatut ja ehdolliset tyypit: kohtuudella, kun ne poistavat toistoa.
type Asiakas = { nimi: string; ika: number; uutiskirje: boolean };

// Kuvattu tyyppi: jokaiselle kentälle lomakkeen tila.
type Lomake<T> = {
  [K in keyof T]: { arvo: T[K]; virhe?: string };
};

// Avainten uudelleennimeäminen mallimerkkijonolla.
type Kasittelijat<T> = {
  [K in keyof T as `muuta${Capitalize<string & K>}`]: (uusi: T[K]) => void;
};

// Ehdollinen tyyppi ja infer: taulukon alkion tyyppi.
type Alkio<T> = T extends readonly (infer A)[] ? A : T;
type Rivi = Alkio<{ tuote: string }[]>; // { tuote: string }

const lomake: Lomake<Asiakas> = {
  nimi: { arvo: "Aino" },
  ika: { arvo: -3, virhe: "iän on oltava positiivinen" },
  uutiskirje: { arvo: true },
};

const muutokset: string[] = [];
const kasittelijat: Kasittelijat<Asiakas> = {
  muutaNimi: (n) => muutokset.push(`nimi=${n}`),
  muutaIka: (i) => muutokset.push(`ikä=${i.toFixed(0)}`),
  muutaUutiskirje: (u) => muutokset.push(`uutiskirje=${u}`),
};
kasittelijat.muutaIka(42);
kasittelijat.muutaNimi("Aino K.");

const virheet = Object.entries(lomake)
  .filter(([, kentta]) => kentta.virhe !== undefined)
  .map(([nimi, kentta]) => `${nimi}: ${kentta.virhe}`);
const r: Rivi = { tuote: "omena" };
console.log(virheet, muutokset, r.tuote);
