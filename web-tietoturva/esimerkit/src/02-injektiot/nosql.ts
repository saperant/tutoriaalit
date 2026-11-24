// NoSQL-operaattori-injektio. Dokumenttitietokantojen kyselykielessä
// arvon paikalle voi kirjoittaa operaattorin, kuten {"$ne": null}.
// Esimerkin hakufunktio toimii kuten MongoDB:n suodatin.

type Ehto = string | { $ne?: unknown; $regex?: string };
type Kayttaja = { tunnus: string; salasana: string };

const KAYTTAJAT: Kayttaja[] = [
  { tunnus: "admin", salasana: "Pitka-ja-salainen-1" },
  { tunnus: "aino", salasana: "kissa-ja-koira-2" },
];

function tasmaa(arvo: string, ehto: Ehto): boolean {
  if (typeof ehto === "string") return arvo === ehto;
  if ("$ne" in ehto) return arvo !== ehto.$ne;
  if (ehto.$regex !== undefined) return new RegExp(ehto.$regex).test(arvo);
  return false;
}

function etsi(suodatin: Record<string, Ehto>): Kayttaja | undefined {
  return KAYTTAJAT.find((k) => Object.entries(suodatin).every(
    ([kentta, ehto]) => tasmaa(k[kentta as keyof Kayttaja], ehto)));
}

// @alku haavoittuva
export function kirjauduHaavoittuva(runko: string): string | null {
  const { tunnus, salasana } = JSON.parse(runko);   // mitä tahansa JSONia
  return etsi({ tunnus, salasana })?.tunnus ?? null;
}
// @loppu haavoittuva

// @alku korjattu
export function kirjaudu(runko: string): string | null {
  const data: unknown = JSON.parse(runko);
  if (typeof data !== "object" || data === null) return null;
  const { tunnus, salasana } = data as Record<string, unknown>;
  // Jäsennetään reunalla: vain merkkijonot kelpaavat.
  if (typeof tunnus !== "string" || typeof salasana !== "string") {
    return null;
  }
  return etsi({ tunnus, salasana })?.tunnus ?? null;
}
// @loppu korjattu
