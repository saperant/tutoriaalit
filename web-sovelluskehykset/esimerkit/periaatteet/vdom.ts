// Virtuaalinen DOM pienoiskoossa (Reactin ja Vuen periaate): näkymä on
// funktio tilasta kuvaukseen, ja kehys vertaa uutta kuvausta edelliseen
// ja tekee oikeaan DOM:iin vain erot. Tässä erot tulostetaan.

// @alku solmu
type Lapsi = VSolmu | string;
interface VSolmu {
  tagi: string;
  avain: string | null;
  ominaisuudet: Record<string, string>;
  lapset: Lapsi[];
}

function h(tagi: string, ominaisuudet: Record<string, string> = {},
           ...lapset: Lapsi[]): VSolmu {
  const { avain = null, ...muut } = ominaisuudet;
  return { tagi, avain, ominaisuudet: muut, lapset };
}
// @loppu solmu

// @alku tasmaytys
function tasmayta(vanha: Lapsi | undefined, uusi: Lapsi | undefined,
                  polku: string, erot: string[]): void {
  if (uusi === undefined) { erot.push(`poista ${polku}`); return; }
  if (vanha === undefined) { erot.push(`luo ${polku}`); return; }
  if (typeof vanha === "string" || typeof uusi === "string") {
    if (vanha !== uusi) erot.push(`teksti ${polku} = "${String(uusi)}"`);
    return;
  }
  if (vanha.tagi !== uusi.tagi) { erot.push(`korvaa ${polku}`); return; }
  for (const [nimi, arvo] of Object.entries(uusi.ominaisuudet)) {
    if (vanha.ominaisuudet[nimi] !== arvo) {
      erot.push(`aseta ${polku} ${nimi}="${arvo}"`);
    }
  }
  const avain = (l: Lapsi) => typeof l === "string" ? null : l.avain;
  if (uusi.lapset.every((l) => avain(l) !== null)) {
    // Avaimilla: lapsi tunnistetaan avaimesta, ei järjestysnumerosta.
    const vanhat = new Map(vanha.lapset.map((l) => [avain(l), l]));
    for (const lapsi of uusi.lapset) {
      const nimi = `${polku}/${avain(lapsi)}`;
      tasmayta(vanhat.get(avain(lapsi)), lapsi, nimi, erot);
      vanhat.delete(avain(lapsi));
    }
    for (const a of vanhat.keys()) erot.push(`poista ${polku}/${a}`);
  } else {
    const n = Math.max(vanha.lapset.length, uusi.lapset.length);
    for (let i = 0; i < n; i++) {
      tasmayta(vanha.lapset[i], uusi.lapset[i], `${polku}/${i}`, erot);
    }
  }
}
// @loppu tasmaytys

// @alku demo
interface Tehtava { id: number; nimi: string; valmis: boolean }

/** Näkymä on puhdas funktio: sama tila tuottaa aina saman kuvauksen. */
function nakyma(tehtavat: Tehtava[], avaimet: boolean): VSolmu {
  return h("ul", {}, ...tehtavat.map((t) =>
    h("li", {
      ...(avaimet ? { avain: `li#${t.id}` } : {}),
      class: t.valmis ? "tehtava valmis" : "tehtava",
    }, t.nimi)));
}

const alku: Tehtava[] = [
  { id: 1, nimi: "Varaa kokoushuone", valmis: false },
  { id: 2, nimi: "Lähetä esityslista", valmis: true },
  { id: 3, nimi: "Tilaa kahvit", valmis: false },
];

function nayta(otsikko: string, uusi: Tehtava[], avaimet: boolean): void {
  const erot: string[] = [];
  tasmayta(nakyma(alku, avaimet), nakyma(uusi, avaimet), "ul", erot);
  console.log(`${otsikko}: DOM-operaatioita ${erot.length}`);
  for (const ero of erot) console.log(`  ${ero}`);
}

const merkitty = alku.map((t) => t.id === 3 ? { ...t, valmis: true } : t);
nayta("Merkitään kolmas valmiiksi", merkitty, true);
nayta("Poistetaan ensimmäinen, ilman avaimia", alku.slice(1), false);
nayta("Poistetaan ensimmäinen, avaimilla", alku.slice(1), true);
// @loppu demo
