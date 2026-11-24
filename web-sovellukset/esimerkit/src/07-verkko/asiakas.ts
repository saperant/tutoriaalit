import type { Luonnos } from "../05-lomakkeet/varaus.ts";
import type { Tila } from "../tilat.ts";
import { jasennaTila, jasennaTilat, jasennaVarausId } from "./skeema.ts";

// @alku virhe
/** Palvelimen virhevastaus. Tila erottaa käyttäjän virheet (4xx)
 *  palvelimen virheistä (5xx), joita voi yrittää uudelleen. */
export class ApiVirhe extends Error {
  readonly status: number;
  constructor(status: number, viesti: string) {
    super(viesti);
    this.status = status;
  }
  get uudelleenyritettava(): boolean { return this.status >= 500; }
}
// @loppu virhe

type Fetch = typeof fetch;

// @alku asiakas
export function luoAsiakas(perus: string, hae: Fetch = fetch) {
  async function pyynto<T>(polku: string, jasenna: (x: unknown) => T,
                           init: RequestInit = {}): Promise<T> {
    // Aikakatkaisu ja kutsujan peruutus samaan signaaliin.
    const signaalit = [AbortSignal.timeout(10_000)];
    if (init.signal) signaalit.push(init.signal);
    const vastaus = await hae(`${perus}${polku}`, {
      ...init,
      signal: AbortSignal.any(signaalit),
      headers: { "Accept": "application/json", ...init.headers },
    });
    const runko: unknown = await vastaus.json().catch(() => null);
    if (!vastaus.ok) {
      const viesti = typeof runko === "object" && runko !== null &&
        "virhe" in runko && typeof runko.virhe === "string"
        ? runko.virhe : `Palvelin vastasi ${vastaus.status}`;
      throw new ApiVirhe(vastaus.status, viesti);
    }
    return jasenna(runko);
  }

  return {
    haeTilat: (signal?: AbortSignal): Promise<Tila[]> =>
      pyynto("/api/tilat", jasennaTilat, signal ? { signal } : {}),
    haeTila: (id: string, signal?: AbortSignal): Promise<Tila> =>
      pyynto(`/api/tilat/${encodeURIComponent(id)}`, (x) => jasennaTila(x),
             signal ? { signal } : {}),
    varaa: (luonnos: Luonnos): Promise<string> =>
      pyynto("/api/varaukset", jasennaVarausId, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(luonnos),
      }),
  };
}

export type Asiakas = ReturnType<typeof luoAsiakas>;
// @loppu asiakas
