// Pieni reaktiivinen tila: signaali, johdettu arvo ja efekti. Sama
// periaate on Vuen ref/computed/watchEffect-rajapinnoissa, SolidJS:ssä
// ja Angularin signaaleissa. Ei tuotantokäyttöön: ei eräajoa eikä
// syklien tunnistusta.

type Efekti = { aja: () => void; riippuvuudet: Set<Set<Efekti>> };
let kaynnissa: Efekti | null = null;

// @alku signaali
export function signaali<T>(alku: T) {
  let arvo = alku;
  const tilaajat = new Set<Efekti>();
  return {
    get(): T {
      if (kaynnissa) {                 // kirjataan, kuka arvoa luki
        tilaajat.add(kaynnissa);
        kaynnissa.riippuvuudet.add(tilaajat);
      }
      return arvo;
    },
    set(uusi: T): void {
      if (Object.is(uusi, arvo)) return;
      arvo = uusi;
      for (const e of [...tilaajat]) e.aja();   // vain lukijat päivittyvät
    },
  };
}
// @loppu signaali

// @alku efekti
export function efekti(funktio: () => void): () => void {
  const e: Efekti = {
    riippuvuudet: new Set(),
    aja() {
      for (const t of e.riippuvuudet) t.delete(e);   // vanhat pois
      e.riippuvuudet.clear();
      const edellinen = kaynnissa;
      kaynnissa = e;
      try { funktio(); } finally { kaynnissa = edellinen; }
    },
  };
  e.aja();
  return () => { for (const t of e.riippuvuudet) t.delete(e); };
}

export function johdettu<T>(laske: () => T) {
  const tulos = signaali<T>(undefined as T);
  efekti(() => tulos.set(laske()));
  return { get: tulos.get };
}
// @loppu efekti
