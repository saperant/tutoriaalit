// Pieni dynaaminen skanneri (DAST): lähettää pyyntöjä käynnissä olevaan
// sovellukseen ja etsii vastauksista tunnettuja puutteita. Oikeat
// työkalut (OWASP ZAP, Burp) tekevät saman paljon laajemmin; periaate
// on sama: sovellusta testataan ulkoapäin kuin hyökkääjä.

export type Havainto = { kohde: string; ongelma: string };

const MERKKI = `"'<wt${"x".repeat(3)}>`;     // lainausmerkit ja kulmasulut

// @alku skanneri
export async function skannaa(perus: string, polut: string[]):
    Promise<Havainto[]> {
  const havainnot: Havainto[] = [];
  for (const polku of polut) {
    const url = new URL(polku, perus);
    const v = await fetch(url, { redirect: "manual" });
    const o = v.headers;
    const puuttuu = (nimi: string) => havainnot.push(
      { kohde: url.pathname, ongelma: `puuttuu ${nimi}` });

    const csp = o.get("content-security-policy") ?? "";
    if (!csp) puuttuu("Content-Security-Policy");
    if (!csp.includes("frame-ancestors") && !o.get("x-frame-options")) {
      puuttuu("kehystyssuojaus");
    }
    if (o.get("x-content-type-options") !== "nosniff") {
      puuttuu("X-Content-Type-Options");
    }
    for (const e of o.getSetCookie()) {
      for (const lippu of ["HttpOnly", "Secure", "SameSite"]) {
        if (!e.includes(lippu)) puuttuu(`evästeestä ${lippu}`);
      }
    }
    // Heijastuuko parametri sellaisenaan (koodaamatta) sivulle?
    for (const nimi of url.searchParams.keys()) {
      const koe = new URL(url);
      koe.searchParams.set(nimi, MERKKI);
      if ((await (await fetch(koe)).text()).includes(MERKKI)) {
        havainnot.push({ kohde: url.pathname, ongelma:
          `parametri ${nimi} heijastuu koodaamatta` });
      }
    }
  }
  return havainnot;
}
// @loppu skanneri
