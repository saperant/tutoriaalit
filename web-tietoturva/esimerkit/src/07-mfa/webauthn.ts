// Pääsyavaimet (WebAuthn): palvelin tallentaa julkisen avaimen, ja
// kirjautuessa selain allekirjoittaa palvelimen haasteen. Avain on
// sidottu sivuston nimeen (rpId), joten kalastelusivu ei voi käyttää
// sitä. Tarkistukset on kirjoitettu auki opetuksen vuoksi; tuotannossa
// käytetään valmista kirjastoa (esim. SimpleWebAuthn).
import { createHash, createPublicKey, randomBytes, verify, type KeyObject }
  from "node:crypto";
import { type Kasittelija, html, json } from "../http.ts";
import { cbor, type Cbor } from "./cbor.ts";

const b64 = (b: Buffer) => b.toString("base64url");
const sha256 = (b: Buffer | string) =>
  createHash("sha256").update(b).digest();

type Avain = { kayttaja: string; julkinen: KeyObject; laskuri: number };

// @alku authdata
function jasennaAuthData(ad: Buffer) {
  return {
    rpIdHash: ad.subarray(0, 32),
    kayttajaLasna: (ad[32]! & 0x01) !== 0,     // UP: kosketus tms.
    kayttajaVarmistettu: (ad[32]! & 0x04) !== 0, // UV: PIN, biometria
    laskuri: ad.readUInt32BE(33),
    loppu: ad.subarray(37),                     // avaimen tiedot (luonti)
  };
}
// @loppu authdata

function coseAvain(cose: Map<Cbor, Cbor>): KeyObject {
  // COSE EC2 (kty 2), käyrä P-256 (crv 1): x = -2, y = -3.
  if (cose.get(1) !== 2 || cose.get(-1) !== 1) {
    throw new Error("vain ES256-avaimet tuetaan");
  }
  return createPublicKey({ format: "jwk", key: {
    kty: "EC", crv: "P-256",
    x: b64(cose.get(-2) as Buffer), y: b64(cose.get(-3) as Buffer) } });
}

export function palvelu(rpId: string, alkupera: string): Kasittelija {
  const haasteet = new Set<string>();
  const avaimet = new Map<string, Avain>();         // tunniste -> avain

  // @alku asiakastiedot
  function tarkistaClientData(raaka: string, tyyppi: string): void {
    const cd = JSON.parse(Buffer.from(raaka, "base64url").toString("utf8"));
    if (cd.type !== tyyppi) throw new Error("väärä tyyppi");
    if (!haasteet.delete(cd.challenge)) throw new Error("tuntematon haaste");
    if (cd.origin !== alkupera) {
      throw new Error(`väärä alkuperä ${cd.origin}`);
    }
  }
  // @loppu asiakastiedot

  return (p) => {
    const d = p.runko ? JSON.parse(p.runko) : {};
    const haaste = () => {
      const h = b64(randomBytes(32));
      haasteet.add(h);
      return h;
    };
    switch (p.polku) {
      case "/rekisteroi/alku":
        return json({ challenge: haaste(), rpId, kayttaja: d.kayttaja });
      // @alku rekisterointi
      case "/rekisteroi/loppu": {
        tarkistaClientData(d.clientDataJSON, "webauthn.create");
        const att = cbor(Buffer.from(d.attestationObject, "base64url"))
          .arvo as Map<Cbor, Cbor>;
        const ad = jasennaAuthData(att.get("authData") as Buffer);
        if (!ad.rpIdHash.equals(sha256(rpId)) || !ad.kayttajaVarmistettu) {
          throw new Error("rpId tai käyttäjän varmistus ei kelpaa");
        }
        const pituus = ad.loppu.readUInt16BE(16);    // AAGUID ensin
        const tunniste = ad.loppu.subarray(18, 18 + pituus);
        const cose = cbor(ad.loppu.subarray(18 + pituus)).arvo;
        avaimet.set(b64(tunniste), { kayttaja: d.kayttaja,
          julkinen: coseAvain(cose as Map<Cbor, Cbor>),
          laskuri: ad.laskuri });
        return json({ ok: true });
      }
      // @loppu rekisterointi
      case "/kirjaudu/alku":
        return json({ challenge: haaste(), rpId });
      // @alku kirjautuminen
      case "/kirjaudu/loppu": {
        tarkistaClientData(d.clientDataJSON, "webauthn.get");
        const avain = avaimet.get(d.id);
        if (!avain) return json({ virhe: "tuntematon avain" }, 401);
        const authData = Buffer.from(d.authenticatorData, "base64url");
        const ad = jasennaAuthData(authData);
        const allekirjoitettu = Buffer.concat([authData,
          sha256(Buffer.from(d.clientDataJSON, "base64url"))]);
        const ok = ad.rpIdHash.equals(sha256(rpId)) &&
          ad.kayttajaVarmistettu &&
          verify("sha256", allekirjoitettu, avain.julkinen,
                 Buffer.from(d.signature, "base64url"));
        // Laskurin pitää kasvaa, jos laite pitää sitä (kloonattu avain).
        if (!ok || (ad.laskuri !== 0 && ad.laskuri <= avain.laskuri)) {
          return json({ virhe: "allekirjoitus ei kelpaa" }, 401);
        }
        avain.laskuri = ad.laskuri;
        return json({ kayttaja: avain.kayttaja });
      }
      // @loppu kirjautuminen
      default:
        return html(SIVU);
    }
  };
}

// Selaimen puoli: base64url-muunnokset ja WebAuthn-kutsut.
const SIVU = `<!doctype html><title>Pääsyavain</title>
<p id="tila">valmis</p>
<script>
const b64 = (b) => btoa(String.fromCharCode(...new Uint8Array(b)))
  .replace(/\\+/g, "-").replace(/\\//g, "_").replace(/=+$/, "");
const tavut = (s) => Uint8Array.from(
  atob(s.replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0));
const post = async (polku, data) => (await fetch(polku, {
  method: "POST", body: JSON.stringify(data) })).json();

async function rekisteroi(kayttaja) {
  const o = await post("/rekisteroi/alku", { kayttaja });
  const c = await navigator.credentials.create({ publicKey: {
    challenge: tavut(o.challenge), rp: { id: o.rpId, name: "Palvelu" },
    user: { id: new TextEncoder().encode(kayttaja), name: kayttaja,
            displayName: kayttaja },
    pubKeyCredParams: [{ type: "public-key", alg: -7 }],
    authenticatorSelection: { residentKey: "required",
                              userVerification: "required" } } });
  return post("/rekisteroi/loppu", { kayttaja,
    clientDataJSON: b64(c.response.clientDataJSON),
    attestationObject: b64(c.response.attestationObject) });
}

async function kirjaudu() {
  const o = await post("/kirjaudu/alku", {});
  const a = await navigator.credentials.get({ publicKey: {
    challenge: tavut(o.challenge), rpId: o.rpId,
    userVerification: "required" } });
  return post("/kirjaudu/loppu", { id: a.id,
    clientDataJSON: b64(a.response.clientDataJSON),
    authenticatorData: b64(a.response.authenticatorData),
    signature: b64(a.response.signature) });
}
</script>`;
