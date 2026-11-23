// Pieni jäsenninkirjasto: unknown sisään, tyypitetty arvo tai virheet
// ulos. Samaa mallia käyttävät mm. Zod ja Valibot.
export type Tulos<T> =
  | { ok: true; arvo: T }
  | { ok: false; virheet: string[] };

export type Jasennin<T> = (x: unknown, polku?: string) => Tulos<T>;

// Jäsentimen tuottama tyyppi: tyyppi johdetaan skeemasta.
export type Tyyppi<J> = J extends Jasennin<infer T> ? T : never;

const ok = <T>(arvo: T): Tulos<T> => ({ ok: true, arvo });
const vika = (polku: string, viesti: string): Tulos<never> =>
  ({ ok: false, virheet: [`${polku || "juuri"}: ${viesti}`] });

export const merkkijono: Jasennin<string> = (x, polku = "") =>
  typeof x === "string" && x.trim() !== "" ? ok(x.trim())
    : vika(polku, "odotettiin ei-tyhjää merkkijonoa");

export const kokonaisluku: Jasennin<number> = (x, polku = "") =>
  Number.isSafeInteger(x) ? ok(x as number)
    : vika(polku, "odotettiin kokonaislukua");

// Tarkennus: jäsennetty arvo + ehto -> uusi (esim. brändätty) tyyppi.
export function tarkenna<T, U extends T>(
  j: Jasennin<T>, ehto: (x: T) => x is U, viesti: string,
): Jasennin<U> {
  return (x, polku = "") => {
    const t = j(x, polku);
    if (!t.ok) return t;
    return ehto(t.arvo) ? ok(t.arvo) : vika(polku, viesti);
  };
}

export function taulukko<T>(j: Jasennin<T>): Jasennin<T[]> {
  return (x, polku = "") => {
    if (!Array.isArray(x)) return vika(polku, "odotettiin taulukkoa");
    const arvot: T[] = [];
    const virheet: string[] = [];
    x.forEach((alkio: unknown, i) => {
      const t = j(alkio, `${polku}[${i}]`);
      if (t.ok) arvot.push(t.arvo);
      else virheet.push(...t.virheet);
    });
    return virheet.length ? { ok: false, virheet } : ok(arvot);
  };
}

// Kuvattu tyyppi: jokaiselle kentälle oma jäsennin.
export function olio<T>(kentat: { [K in keyof T]: Jasennin<T[K]> }):
    Jasennin<T> {
  return (x, polku = "") => {
    if (typeof x !== "object" || x === null || Array.isArray(x)) {
      return vika(polku, "odotettiin oliota");
    }
    const lahde = x as Record<string, unknown>;
    const tulos: Partial<T> = {};
    const virheet: string[] = [];
    for (const k in kentat) {
      const t = kentat[k](lahde[k], polku ? `${polku}.${k}` : k);
      if (t.ok) tulos[k] = t.arvo;
      else virheet.push(...t.virheet);
    }
    return virheet.length ? { ok: false, virheet } : ok(tulos as T);
  };
}
