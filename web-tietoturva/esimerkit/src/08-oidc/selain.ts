// Pieni "selain" ja testiympäristö kaupalle ja tunnistuspalvelulle.
import { kaynnista, type Kasittelija } from "../http.ts";
import { tarjoaja } from "./tarjoaja.ts";
import { kauppa } from "./asiakas.ts";

// Pieni "selain": evästeet osoitteittain ja uudelleenohjausten
// seuraaminen käsin, jotta välivaiheet näkyvät testissä.
export class Selain {
  evasteet = new Map<string, Map<string, string>>();
  constructor(idpKayttaja: string, idp: string) {
    this.evasteet.set(new URL(idp).host,
                      new Map([["idp-kayttaja", idpKayttaja]]));
  }
  async hae(url: string, seuraa = true): Promise<Response> {
    for (;;) {
      const u = new URL(url);
      const purkki = this.evasteet.get(u.host) ?? new Map();
      this.evasteet.set(u.host, purkki);
      const v = await fetch(u, { redirect: "manual", headers: { Cookie:
        [...purkki].map(([k, a]) => `${k}=${a}`).join("; ") } });
      for (const e of v.headers.getSetCookie()) {
        const [pari = ""] = e.split(";");
        const i = pari.indexOf("=");
        purkki.set(pari.slice(0, i), pari.slice(i + 1));
      }
      const kohde = v.headers.get("location");
      if (!seuraa || !kohde || v.status < 300 || v.status >= 400) return v;
      url = new URL(kohde, u).href;
    }
  }
}

export async function ymparisto(korjattu: boolean) {
  // Molemmat tarvitsevat toistensa osoitteet, joten käsittelijät
  // asetetaan vasta, kun portit ovat tiedossa.
  let k: Kasittelija = () => ({});
  let t: Kasittelija = () => ({});
  const kauppaS = await kaynnista((p) => k(p));
  const idp = await kaynnista((p) => t(p));
  t = tarjoaja(idp.url, new Map([["kauppa", `${kauppaS.url}/paluu`]]),
               korjattu);
  k = kauppa(idp.url, kauppaS.url, korjattu);
  return { kauppa: kauppaS.url, idp: idp.url,
           sulje: async () => { await kauppaS.sulje(); await idp.sulje(); } };
}
