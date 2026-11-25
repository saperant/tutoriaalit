// Hienojakoinen reaktiivisuus pienoiskoossa (Vuen ref ja computed,
// Angularin ja Solidin signaalit, Svelten riimut): arvo tietää, kuka
// sitä luki, ja ilmoittaa muutoksesta vain lukijoilleen. Näkymää ei
// lasketa uudelleen eikä mitään verrata.

// @alku ydin
type Lukija = () => void;
let kaynnissa: Lukija | null = null;

function signaali<T>(alku: T) {
  let arvo = alku;
  const lukijat = new Set<Lukija>();
  return {
    get(): T {
      if (kaynnissa !== null) lukijat.add(kaynnissa);   // kirjaa lukija
      return arvo;
    },
    set(uusi: T): void {
      if (Object.is(uusi, arvo)) return;      // sama arvo: ei mitään
      arvo = uusi;
      for (const lukija of [...lukijat]) lukija();
    },
  };
}

function efekti(funktio: () => void): void {
  const aja = () => {
    const edellinen = kaynnissa;
    kaynnissa = aja;
    try { funktio(); } finally { kaynnissa = edellinen; }
  };
  aja();
}

/** Johdettu arvo on efekti, joka kirjoittaa tuloksensa signaaliin. */
function johdettu<T>(laske: () => T) {
  const tulos = signaali<T>(undefined as T);
  efekti(() => tulos.set(laske()));
  return { get: tulos.get };
}
// @loppu ydin

// @alku demo
interface Tehtava { nimi: string; valmis: boolean }

const tehtavat = signaali<Tehtava[]>([
  { nimi: "Varaa kokoushuone", valmis: false },
  { nimi: "Lähetä esityslista", valmis: true },
]);
const vainAvoimet = signaali(false);
const avoimia = johdettu(() =>
  tehtavat.get().filter((t) => !t.valmis).length);
const nakyvat = johdettu(() =>
  tehtavat.get().filter((t) => !vainAvoimet.get() || !t.valmis));

// Kumpikin efekti vastaa yhtä DOM:n kohtaa.
efekti(() => console.log(`  [yhteenveto] avoimia ${avoimia.get()}`));
efekti(() => console.log(
  `  [lista] ${nakyvat.get().map((t) => t.nimi).join(", ")}`));

console.log("Suodatin päälle:");
vainAvoimet.set(true);
console.log("Lisätään valmis tehtävä (avoimien määrä ei muutu):");
tehtavat.set([...tehtavat.get(), { nimi: "Tilaa kahvit", valmis: true }]);
console.log("Lisätään avoin tehtävä:");
tehtavat.set([...tehtavat.get(), { nimi: "Kirjoita muistio",
                                   valmis: false }]);
console.log("Asetetaan suodatin samaan arvoon:");
vainAvoimet.set(true);
// @loppu demo
