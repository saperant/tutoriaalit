// Tyypit datasta: as const, satisfies, typeof ja keyof typeof.
type Reitti = { polku: `/${string}`; metodi: "GET" | "POST" };

// Annotaatio leventää: avaimet ovat pelkkä string.
const reititA: Record<string, Reitti> = {
  tuotteet: { polku: "/tuotteet", metodi: "GET" },
};
// satisfies tarkistaa muodon mutta säilyttää tarkat tyypit.
const reitit = {
  tuotteet: { polku: "/tuotteet", metodi: "GET" },
  tilaa: { polku: "/tilaukset", metodi: "POST" },
} as const satisfies Record<string, Reitti>;

type ReitinNimi = keyof typeof reitit; // "tuotteet" | "tilaa"
type TilaaPolku = (typeof reitit)["tilaa"]["polku"]; // "/tilaukset"

function osoite(nimi: ReitinNimi): string {
  const r = reitit[nimi];
  return `${r.metodi} ${r.polku}`;
}

const p: TilaaPolku = "/tilaukset";
console.log(osoite("tilaa"), p, Object.keys(reititA).length);
// reititA.tuotteet on Reitti | undefined (noUncheckedIndexedAccess),
// reitit.tuotteet on aina olemassa:
console.log(reititA["tuotteet"]?.polku, reitit.tuotteet.polku);

// Kaksisuuntainen yhteys: tyyppi datasta, data tyypillä tarkistettuna.
const OLETUKSET = { kieli: "fi", sivukoko: 20, tumma: false };
type Asetukset = typeof OLETUKSET;
function lue(muutokset: Partial<Asetukset>): Asetukset {
  return { ...OLETUKSET, ...muutokset };
}
console.log(lue({ sivukoko: 50 }));
