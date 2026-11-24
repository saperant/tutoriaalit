// Verkkokaupan kirjautuminen OpenID Connectilla BFF-mallilla
// (backend for frontend): palvelin hoitaa koko virran ja säilyttää
// tokenit, ja selain saa vain HttpOnly-istuntoevästeen.
import { createHash, createPublicKey, randomBytes, type JsonWebKey,
         type KeyObject } from "node:crypto";
import { type Kasittelija, json } from "../http.ts";
import { tarkista } from "../09-jwt/jwt.ts";

type Odottava = { state: string; nonce: string; tarkiste: string };
const satunnainen = () => randomBytes(32).toString("base64url");

export function kauppa(idp: string, oma: string, korjattu: boolean):
    Kasittelija {
  const paluu = `${oma}/paluu`;
  const odottavat = new Map<string, Odottava>();   // esi-istunto -> virta
  const istunnot = new Map<string, string>();      // istunto -> käyttäjä

  async function avaimet(): Promise<Map<string, KeyObject>> {
    const { keys } = await (await fetch(`${idp}/jwks`)).json();
    return new Map(keys.map((k: JsonWebKey & { kid: string }) =>
      [k.kid, createPublicKey({ format: "jwk", key: k })]));
  }

  return async (p) => {
    // @alku aloitus
    if (p.polku === "/kirjaudu") {
      const esi = satunnainen();
      const o = { state: satunnainen(), nonce: satunnainen(),
                  tarkiste: satunnainen() };          // PKCE code_verifier
      odottavat.set(esi, o);
      const u = new URL(`${idp}/authorize`);
      u.search = new URLSearchParams({
        response_type: "code", client_id: "kauppa", redirect_uri: paluu,
        scope: "openid", state: o.state, nonce: o.nonce,
        ...(korjattu ? {
          code_challenge: createHash("sha256").update(o.tarkiste)
            .digest("base64url"),
          code_challenge_method: "S256" } : {}),
      }).toString();
      return { tila: 302, otsakkeet: { Location: u.href, "Set-Cookie":
        `esi=${esi}; Path=/; HttpOnly; SameSite=Lax; Max-Age=600` } };
    }
    // @loppu aloitus
    // @alku paluu
    if (p.polku === "/paluu") {
      const o = odottavat.get(p.evasteet.get("esi") ?? "");
      odottavat.delete(p.evasteet.get("esi") ?? "");
      if (korjattu && (!o || p.haku.get("state") !== o.state)) {
        return { tila: 400, runko: "state ei täsmää" };
      }
      const vastaus = await fetch(`${idp}/token`, { method: "POST",
        body: new URLSearchParams({
          grant_type: "authorization_code", client_id: "kauppa",
          code: p.haku.get("code") ?? "", redirect_uri: paluu,
          ...(korjattu && o ? { code_verifier: o.tarkiste } : {}) }) });
      if (!vastaus.ok) return { tila: 400, runko: "koodi ei kelpaa" };
      const { id_token } = await vastaus.json();
      const v = tarkista(id_token, { avaimet: await avaimet(),
                                     iss: idp, aud: "kauppa" });
      if (korjattu && v.nonce !== o?.nonce) {
        return { tila: 400, runko: "nonce ei täsmää" };
      }
      const sid = satunnainen();
      istunnot.set(sid, String(v.sub));
      return { tila: 302, otsakkeet: { Location: "/", "Set-Cookie":
        `sid=${sid}; Path=/; HttpOnly; SameSite=Lax` } };
    }
    // @loppu paluu
    const kayttaja = istunnot.get(p.evasteet.get("sid") ?? "");
    return kayttaja ? json({ kayttaja }) : { tila: 401 };
  };
}
