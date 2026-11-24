// Pieni OpenID Connect -palveluntarjoaja testejä varten: valtuutus-
// koodivirta (authorization code) ja PKCE. Kirjautuminen tarjoajalle
// on yksinkertaistettu evästeeksi, joka kertoo käyttäjän.
import { createHash, randomBytes } from "node:crypto";
import { type Kasittelija, json, lomake } from "../http.ts";
import { allekirjoita, avainpari } from "../09-jwt/jwt.ts";

type Koodi = { asiakas: string; paluu: string; kayttaja: string;
               nonce: string; haaste?: string; vanhenee: number };

export function tarjoaja(iss: string, asiakkaat: Map<string, string>,
                         tiukka: boolean): Kasittelija {
  const { yksityinen, julkinen } = avainpari();
  const koodit = new Map<string, Koodi>();

  // @alku paluuosoite
  function sallittuPaluu(rekisteroity: string, annettu: string): boolean {
    // Tiukka: täsmälleen sama merkkijono. Löysä (VÄÄRIN): alkuosa.
    return tiukka ? annettu === rekisteroity
                  : annettu.startsWith(rekisteroity);
  }
  // @loppu paluuosoite

  return (p) => {
    if (p.polku === "/authorize") {
      const q = p.haku;
      const asiakas = q.get("client_id") ?? "";
      const paluu = q.get("redirect_uri") ?? "";
      const rekisteroity = asiakkaat.get(asiakas);
      // Virheellistä paluuosoitetta ei koskaan seurata: muuten koodi
      // vuotaisi hyökkääjälle.
      if (!rekisteroity || !sallittuPaluu(rekisteroity, paluu)) {
        return { tila: 400, runko: "virheellinen redirect_uri" };
      }
      // @alku pkce-vaatimus
      const haaste = q.get("code_challenge") ?? undefined;
      if (tiukka && (!haaste || q.get("code_challenge_method") !== "S256")) {
        return { tila: 400, runko: "PKCE (S256) vaaditaan" };
      }
      // @loppu pkce-vaatimus
      const koodi = randomBytes(24).toString("base64url");
      koodit.set(koodi, { asiakas, paluu, haaste,
        kayttaja: p.evasteet.get("idp-kayttaja") ?? "",
        nonce: q.get("nonce") ?? "", vanhenee: Date.now() + 60_000 });
      const kohde = new URL(paluu);
      kohde.searchParams.set("code", koodi);
      kohde.searchParams.set("state", q.get("state") ?? "");
      return { tila: 302, otsakkeet: { Location: kohde.href } };
    }
    if (p.polku === "/token" && p.metodi === "POST") {
      const l = lomake(p);
      const k = koodit.get(l.get("code") ?? "");
      koodit.delete(l.get("code") ?? "");            // kertakäyttöinen
      if (!k || k.vanhenee < Date.now() ||
          k.asiakas !== l.get("client_id") ||
          k.paluu !== l.get("redirect_uri")) {
        return json({ error: "invalid_grant" }, 400);
      }
      // @alku pkce-tarkistus
      if (k.haaste !== undefined || tiukka) {
        const v = l.get("code_verifier") ?? "";
        const laskettu = createHash("sha256").update(v).digest("base64url");
        if (laskettu !== k.haaste) {
          return json({ error: "invalid_grant" }, 400);
        }
      }
      // @loppu pkce-tarkistus
      const nyt = Math.floor(Date.now() / 1000);
      return json({
        token_type: "Bearer", expires_in: 300,
        access_token: randomBytes(24).toString("base64url"),
        id_token: allekirjoita({ iss, aud: k.asiakas, sub: k.kayttaja,
          nonce: k.nonce, iat: nyt, exp: nyt + 300 }, yksityinen, "k1"),
      });
    }
    if (p.polku === "/jwks") {
      return json({ keys: [{ ...julkinen.export({ format: "jwk" }),
                             kid: "k1", alg: "RS256", use: "sig" }] });
    }
    return { tila: 404 };
  };
}
