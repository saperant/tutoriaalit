// JWT (RFC 7519): allekirjoitettu JSON-väite. Tarkistus kirjoitetaan
// auki opetuksen vuoksi; tuotannossa käytetään kirjastoa (esim. jose)
// ja annetaan sille kiinteä algoritmi, avaimet ja odotetut väitteet.
import { createHmac, createPublicKey, generateKeyPairSync, sign, verify,
         timingSafeEqual, type KeyObject } from "node:crypto";

export type Vaitteet = Record<string, unknown> & {
  iss?: string; aud?: string; sub?: string; exp?: number; nbf?: number;
  jti?: string; nonce?: string;
};

const koodaa = (o: unknown) => Buffer.from(JSON.stringify(o)).toString(
  "base64url");
const pura = (s: string) => JSON.parse(Buffer.from(s, "base64url")
  .toString("utf8"));

export function allekirjoita(vaitteet: Vaitteet, avain: KeyObject,
                             kid: string): string {
  const alku = `${koodaa({ alg: "RS256", typ: "JWT", kid })}.` +
               koodaa(vaitteet);
  return `${alku}.${sign("sha256", Buffer.from(alku), avain)
    .toString("base64url")}`;
}

// Hyökkääjän työkalu: HMAC-allekirjoitus millä tahansa salaisuudella.
export function allekirjoitaHmac(vaitteet: Vaitteet, salaisuus: string):
    string {
  const alku = `${koodaa({ alg: "HS256", typ: "JWT" })}.${koodaa(vaitteet)}`;
  return `${alku}.${createHmac("sha256", salaisuus).update(alku)
    .digest("base64url")}`;
}

// @alku haavoittuva
// VÄÄRIN: algoritmi luetaan tokenista, ja vanhenemista ei tarkisteta.
export function tarkistaHaavoittuva(token: string,
                                    julkinenPem: string): Vaitteet {
  const [h, v, s = ""] = token.split(".");
  const otsake = pura(h!);
  const alku = Buffer.from(`${h}.${v}`);
  let ok = false;
  if (otsake.alg === "none") ok = true;
  if (otsake.alg === "HS256") {           // "avain" on julkinen PEM!
    const mac = createHmac("sha256", julkinenPem).update(alku).digest();
    ok = mac.length === Buffer.from(s, "base64url").length &&
         timingSafeEqual(mac, Buffer.from(s, "base64url"));
  }
  if (otsake.alg === "RS256") {
    ok = verify("sha256", alku, createPublicKey(julkinenPem),
                Buffer.from(s, "base64url"));
  }
  if (!ok) throw new Error("allekirjoitus ei kelpaa");
  return pura(v!);
}
// @loppu haavoittuva

// @alku korjattu
export type Odotukset = {
  avaimet: Map<string, KeyObject>;      // kid -> julkinen avain
  iss: string; aud: string;
  nyt?: number; marginaali?: number;    // sekunteja
  kumotut?: Set<string>;                // jti-tunnisteet
};

export function tarkista(token: string, o: Odotukset): Vaitteet {
  const [h, v, s] = token.split(".");
  if (!h || !v || !s) throw new Error("väärä muoto");
  const otsake = pura(h);
  if (otsake.alg !== "RS256") throw new Error("väärä algoritmi");
  const avain = o.avaimet.get(otsake.kid);
  if (!avain || !verify("sha256", Buffer.from(`${h}.${v}`), avain,
                        Buffer.from(s, "base64url"))) {
    throw new Error("allekirjoitus ei kelpaa");
  }
  const c: Vaitteet = pura(v);
  const nyt = o.nyt ?? Date.now() / 1000;
  const m = o.marginaali ?? 30;
  if (c.iss !== o.iss || c.aud !== o.aud) throw new Error("väärä iss/aud");
  if (typeof c.exp !== "number" || nyt > c.exp + m) {
    throw new Error("vanhentunut");
  }
  if (typeof c.nbf === "number" && nyt < c.nbf - m) {
    throw new Error("ei vielä voimassa");
  }
  if (c.jti && o.kumotut?.has(c.jti)) throw new Error("kumottu");
  return c;
}
// @loppu korjattu

export function avainpari(): { yksityinen: KeyObject; julkinen: KeyObject } {
  const { privateKey, publicKey } = generateKeyPairSync("rsa", {
    modulusLength: 2048 });
  return { yksityinen: privateKey, julkinen: publicKey };
}
