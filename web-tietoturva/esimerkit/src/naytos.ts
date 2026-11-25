// Näytösajo: ajaa lukujen hyökkäykset haavoittuvaa ja korjattua
// versiota vastaan ja tulostaa, mitä kumpikin vastasi. Testit
// (*.test.ts) väittävät samat asiat; tämä näyttää ne.
//
//   node src/naytos.ts 02-sql  yksi näytös
//   make naytos                kaikki, ja vertailu tallennettuun
//
// Kaikki palvelimet käynnistyvät tämän prosessin sisällä osoitteeseen
// 127.0.0.1 satunnaiseen porttiin ja sammuvat ajon lopussa.
import { mkdtemp, readdir, writeFile, mkdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { BlockList } from "node:net";
import { kaynnista } from "./http.ts";
import { taulu as muotoile, yrita } from "./taulu.ts";
import { tietokanta, tilauksetHaavoittuva, tilaukset }
  from "./02-injektiot/sql.ts";
import { kirjauduHaavoittuva, kirjaudu } from "./02-injektiot/nosql.ts";
import { kokoHaavoittuva, koko } from "./02-injektiot/komento.ts";
import { esikatseluHaavoittuva, esikatselu } from "./02-injektiot/ssrf.ts";
import { corsHaavoittuva, cors } from "./04-csrf/cors.ts";
import { palvelu as istuntopalvelu, EVASTE } from "./05-istunnot/istunnot.ts";
import { arvioi } from "./06-salasanat/salasanat.ts";
import { Kirjautuminen, Rajoitin } from "./06-salasanat/kirjautuminen.ts";
import { Palautus } from "./06-salasanat/palautus.ts";
import { totp, TotpTarkistin } from "./07-mfa/totp.ts";
import { Selain, ymparisto } from "./08-oidc/selain.ts";
import { tarjoaja } from "./08-oidc/tarjoaja.ts";
import { allekirjoita, allekirjoitaHmac, avainpari, tarkista,
         tarkistaHaavoittuva, type Odotukset, type Vaitteet }
  from "./09-jwt/jwt.ts";
import { api } from "./10-valtuutus/api.ts";
import { lataukset } from "./11-tiedostot/lataus.ts";
import { seuraava, seuraavaHaavoittuva } from "./11-tiedostot/ohjaus.ts";
import { palsta } from "./03-xss/xss.ts";
import { skannaa } from "./12-testaus/skanneri.ts";


const OTSIKOT = ["hyökkäys", "haavoittuva", "korjattu"];

function taulu(otsikot: string[], rivit: string[][]): void {
  process.stdout.write(muotoile(otsikot, rivit));
}

function sql(): void {
  const db = tietokanta();
  const hyokkays = "x' OR '1'='1";
  taulu(["asiakas", "haavoittuva", "korjattu"], ["aino", hyokkays].map((a) =>
    [a, `${tilauksetHaavoittuva(db, a).length} tilausta`,
     `${tilaukset(db, a).length} tilausta`]));
}

function nosql(): void {
  const tulos = (k: string | null) => k ? `kirjautui: ${k}` : "hylätty";
  taulu(["tunnus", "salasana", "haavoittuva", "korjattu"], [
    ["aino", '"kissa-ja-koira-2"'], ["admin", '{"$ne": null}'],
  ].map(([t, s]) => {
    const runko = `{"tunnus": "${t}", "salasana": ${s}}`;
    return [t!, s!, tulos(kirjauduHaavoittuva(runko)), tulos(kirjaudu(runko))];
  }));
}

async function komento(): Promise<void> {
  const rivit: string[][] = [];
  for (const nimi of ["raportti.txt", "raportti.txt; touch PWNED", "-rf"]) {
    const tulokset: string[] = [];
    for (const f of [kokoHaavoittuva, koko]) {
      const hak = await mkdtemp(path.join(tmpdir(), "wt-"));
      await writeFile(path.join(hak, "raportti.txt"), "12345");
      const t = (await yrita(() => f(hak, nimi)))
        .replace(/^virhe: Command failed[^]*/, "virhe (wc)");
      tulokset.push((await readdir(hak)).includes("PWNED")
        ? "PWNED syntyi" : t);
    }
    rivit.push([nimi, ...tulokset]);
  }
  taulu(["nimi", "haavoittuva", "korjattu"], rivit);
}

async function ssrf(): Promise<void> {
  const sisainen = await kaynnista(() => ({ runko: "salainen-avain" }));
  const julkinen = await kaynnista(() => ({
    tila: 302, otsakkeet: { Location: `${sisainen.url}/` } }), "127.0.0.2");
  const estetyt = new BlockList();
  estetyt.addAddress("127.0.0.1");
  estetyt.addAddress("::1", "ipv6");
  const portti = new URL(sisainen.url).port;
  // Portit vaihtuvat ajosta toiseen, joten tulosteessa ne ovat P ja Q.
  const kohteet: [string, string][] = [
    ["http://127.0.0.1:P/", sisainen.url],
    ["http://2130706433:P/", `http://2130706433:${portti}/`],
    ["http://127.0.0.2:Q/ (ohjaa)", julkinen.url],
    ["file:///etc/passwd", "file:///etc/passwd"],
  ];
  const rivit: string[][] = [];
  for (const [nimi, kohde] of kohteet) {
    rivit.push([nimi,
      (await yrita(() => esikatseluHaavoittuva(kohde)))
        .replace(/^virhe: .*/, "virhe"),
      await yrita(() => esikatselu(kohde, estetyt))]);
  }
  await sisainen.sulje();
  await julkinen.sulje();
  taulu(["osoite", "haavoittuva", "korjattu"], rivit);
}

function cors04(): void {
  const sallitut = new Set(["https://app.example"]);
  const nayta = (o: Record<string, string>) =>
    o["Access-Control-Allow-Origin"] ?? "–";
  taulu(["Origin", "haavoittuva sallii", "korjattu sallii"],
    ["https://app.example", "https://vieras.example", "null"].map((o) =>
      [o, nayta(corsHaavoittuva(o)), nayta(cors(o, sallitut))]));
}

async function istunnot(): Promise<void> {
  const rivit: string[][] = [];
  const tulos: Record<string, string[]> = { kiinnitys: [], sama: [],
                                            ulos: [] };
  for (const korjattu of [false, true]) {
    const s = await kaynnista(istuntopalvelu(korjattu));
    const evasteesta = (v: Response) => {
      const o = v.headers.get("set-cookie") ?? "";
      return o.slice(`${EVASTE}=`.length, o.indexOf(";"));
    };
    // Hyökkääjä hankkii tunnisteen, uhri kirjautuu sillä.
    const sid = await (await fetch(`${s.url}/uusi`)).text();
    const v = await fetch(`${s.url}/kirjaudu?sid=${sid}`, {
      method: "POST", body: "tunnus=aino" });
    const uhrin = evasteesta(v);
    const h = await fetch(`${s.url}/?sid=${sid}`);
    tulos.kiinnitys!.push(`${h.status} ${await h.text()}`);
    tulos.sama!.push(uhrin === sid ? "sama kuin ennen" : "uusi");
    // Uloskirjautumisen jälkeen vanha eväste ei saa kelvata.
    const pyynto = { headers: { Cookie: `${EVASTE}=${uhrin}` } };
    await fetch(`${s.url}/ulos`, { method: "POST", ...pyynto });
    const j = await fetch(s.url, pyynto);
    tulos.ulos!.push(`${j.status} ${await j.text()}`);
    await s.sulje();
  }
  rivit.push(["uhrin tunniste kirjautumisen jälkeen", ...tulos.sama!]);
  rivit.push(["hyökkääjän pyyntö omalla tunnisteellaan",
              ...tulos.kiinnitys!]);
  rivit.push(["vanha eväste uloskirjautumisen jälkeen", ...tulos.ulos!]);
  taulu(["vaihe", "haavoittuva", "korjattu"], rivit);
}

function kaytanto(): void {
  const estetyt = new Set(["salasana123456789"]);
  taulu(["salasana", "arvio"], ["Kesä2026!", "salasana123456789",
      "aino-sanoo-hyvää-huomenta", "lumi sataa hiljaa pihalle"]
    .map((s) => [s, arvioi(s, "aino", estetyt).join(", ") || "kelpaa"]));
}

function arvailu(): void {
  const k = new Kirjautuminen({ aino: "lumi sataa hiljaa pihalle" });
  taulu(["tunnus / salasana", "haavoittuva", "korjattu"],
    [["ville", "x"], ["aino", "x"]].map(([t, s]) =>
      [`${t} / ${s}`, k.haavoittuva(t!, s!).viesti,
       k.kirjaudu(t!, s!, "10.0.0.1").viesti]));
}

function rajoitus(): void {
  let nyt = 0;
  const r = new Rajoitin(5, 1 / 60, () => nyt);
  const rivit: string[][] = [];
  const yritys = (i: number) =>
    rivit.push([`${i}.`, `${nyt / 1000} s`,
                r.salli("aino") ? "sallittu" : "estetty"]);
  for (let i = 1; i <= 7; i++) yritys(i);
  nyt += 60_000;
  yritys(8);
  yritys(9);
  taulu(["yritys", "aika", "tulos"], rivit);
}

function palautus(): void {
  let nyt = 0;
  const p = new Palautus(["aino"], () => nyt);
  const lahti = (t: string | undefined) => t ? "token sähköpostiin" : "–";
  const kaytto = (t: string) => p.kayta(t) ?? "hylätty";
  const eka = p.pyyda("aino")!;
  const rivit = [
    ["pyyntö tunnukselle aino", lahti(eka)],
    ["pyyntö tuntemattomalle tunnukselle", lahti(p.pyyda("tuntematon"))],
    ["arvattu token", kaytto("x".repeat(43))],
    ["oikea token", `salasanan saa vaihtaa: ${kaytto(eka)}`],
    ["sama token uudelleen", kaytto(eka)],
  ];
  const toka = p.pyyda("aino")!;
  nyt += 31 * 60_000;
  rivit.push(["uusi token 31 minuutin kuluttua", kaytto(toka)]);
  taulu(["vaihe", "tulos"], rivit);
}

function totpNaytos(): void {
  const salaisuus = Buffer.from("12345678901234567890");
  const t = new TotpTarkistin(salaisuus);
  const T = 1_000_000;
  const koodi = totp(salaisuus, T);
  taulu(["koodi", "laskettu", "tarkistus", "tulos"], [
    [koodi, "T", "T + 25 s", String(t.tarkista(koodi, T + 25))],
    [koodi, "T", "T + 25 s (uudelleen)", String(t.tarkista(koodi, T + 25))],
    [totp(salaisuus, T - 90), "T − 90 s", "T",
     String(t.tarkista(totp(salaisuus, T - 90), T))],
    ["000000", "arvaus", "T", String(t.tarkista("000000", T))],
  ].map((r) => [r[0]!, r[1]!, r[2]!,
                r[3] === "true" ? "hyväksytty" : "hylätty"]));
}

async function kirjautumisCsrf(): Promise<void> {
  const tulokset: string[] = [];
  for (const korjattu of [false, true]) {
    const y = await ymparisto(korjattu);
    const h = new Selain("hyokkaaja", y.idp);
    const ohjaus = await h.hae(`${y.kauppa}/kirjaudu`, false);
    const ansa = (await h.hae(ohjaus.headers.get("location")!, false))
      .headers.get("location")!;
    const tulos = await new Selain("uhri", y.idp).hae(ansa);
    tulokset.push(tulos.status === 200
      ? `kirjautui tilille ${(await tulos.json()).kayttaja}`
      : `${tulos.status} ${await tulos.text()}`);
    await y.sulje();
  }
  taulu(OTSIKOT, [["uhri avaa ansalinkin", ...tulokset]]);
}

async function pkce(): Promise<void> {
  const tulokset: string[] = [];
  for (const korjattu of [false, true]) {
    const y = await ymparisto(korjattu);
    const uhri = new Selain("aino", y.idp);
    const ohjaus = await uhri.hae(`${y.kauppa}/kirjaudu`, false);
    const paluu = new URL((await uhri.hae(ohjaus.headers.get("location")!,
                                          false)).headers.get("location")!);
    const v = await fetch(`${y.idp}/token`, { method: "POST",
      body: new URLSearchParams({ grant_type: "authorization_code",
        client_id: "kauppa", redirect_uri: `${y.kauppa}/paluu`,
        code: paluu.searchParams.get("code")! }) });
    const runko = await v.json() as Record<string, unknown>;
    tulokset.push(v.status === 200 && "id_token" in runko
      ? "200, tokenit" : `${v.status} ${Object.values(runko).join(", ")}`);
    await y.sulje();
  }
  taulu(OTSIKOT, [["kaapattu koodi ilman code_verifier-arvoa",
                   ...tulokset]]);
}

async function paluuosoite(): Promise<void> {
  const rivit: string[][] = [];
  for (const osoite of ["https://kauppa.example",
                        "https://kauppa.example.hyokkaaja.example/"]) {
    const tulokset: string[] = [];
    for (const korjattu of [false, true]) {
      const s = await kaynnista(tarjoaja("x",
        new Map([["kauppa", "https://kauppa.example"]]), korjattu));
      const u = new URL(`${s.url}/authorize`);
      u.search = new URLSearchParams({ client_id: "kauppa",
        redirect_uri: osoite, response_type: "code", state: "s",
        code_challenge: "x".repeat(43), code_challenge_method: "S256" })
        .toString();
      const v = await fetch(u, { redirect: "manual" });
      tulokset.push(v.status === 302 ? "302 ja koodi" : `${v.status}`);
      await s.sulje();
    }
    rivit.push([osoite, ...tulokset]);
  }
  taulu(["redirect_uri", "haavoittuva", "korjattu"], rivit);
}

async function jwt(): Promise<void> {
  const { yksityinen, julkinen } = avainpari();
  const pem = julkinen.export({ type: "spki", format: "pem" }).toString();
  const NYT = 1_800_000_000;
  const odotukset: Odotukset = {
    avaimet: new Map([["k1", julkinen]]), iss: "https://tunnistus.example",
    aud: "kauppa", nyt: NYT, kumotut: new Set(["kumottu-1"]) };
  const perus: Vaitteet = { iss: "https://tunnistus.example",
    aud: "kauppa", sub: "aino", exp: NYT + 300, jti: "t-1" };
  const b64 = (s: string) => Buffer.from(s).toString("base64url");
  const tokenit: [string, string][] = [
    ["alg: none",
     `${b64('{"alg":"none"}')}.${b64(JSON.stringify(
       { ...perus, sub: "admin" }))}.`],
    ["HS256 julkisella avaimella",
     allekirjoitaHmac({ ...perus, sub: "admin" }, pem)],
    ["vanhentunut tunti sitten",
     allekirjoita({ ...perus, exp: NYT - 3600 }, yksityinen, "k1")],
    ["aud: toinen",
     allekirjoita({ ...perus, aud: "toinen" }, yksityinen, "k1")],
    ["kumottu (jti)",
     allekirjoita({ ...perus, jti: "kumottu-1" }, yksityinen, "k1")],
    ["oikea token", allekirjoita(perus, yksityinen, "k1")],
  ];
  const rivit: string[][] = [];
  for (const [nimi, token] of tokenit) {
    rivit.push([nimi,
      await yrita(() => `kelpaa, sub: ${tarkistaHaavoittuva(token, pem).sub}`),
      await yrita(() => `kelpaa, sub: ${tarkista(token, odotukset).sub}`)]);
  }
  taulu(["token", "haavoittuva", "korjattu"], rivit);
}

async function valtuutus(): Promise<void> {
  const pyynnot: [string, string, string, unknown?][] = [
    ["aino", "GET", "/tilaukset/1"],
    ["aino", "GET", "/tilaukset/2"],
    ["aino", "PATCH", "/oma", { sahkoposti: "uusi@x.fi",
                                rooli: "yllapitaja" }],
    ["paula", "GET", "/tilaukset/2"],
    ["ville", "DELETE", "/tilaukset/2"],
  ];
  const sarakkeet: string[][] = [];
  for (const korjattu of [false, true]) {
    const s = await kaynnista(api(korjattu));
    const sarake: string[] = [];
    for (const [kayttaja, metodi, polku, runko] of pyynnot) {
      const v = await fetch(`${s.url}${polku}`, { method: metodi,
        headers: { Authorization: `Bearer ${kayttaja}` },
        body: runko === undefined ? undefined : JSON.stringify(runko) });
      const teksti = await v.text();
      sarake.push(metodi === "PATCH"
        ? `${v.status}, rooli: ${JSON.parse(teksti).rooli}`
        : `${v.status}`);
    }
    sarakkeet.push(sarake);
    await s.sulje();
  }
  taulu(["käyttäjä", "pyyntö", "haavoittuva", "korjattu"],
    pyynnot.map(([k, m, p], i) =>
      [k, `${m} ${p}`, sarakkeet[0]![i]!, sarakkeet[1]![i]!]));
}

async function lataus(): Promise<void> {
  const HTML = Buffer.from("<script>alert(document.cookie)</script>");
  const PNG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  const sarakkeet: string[][] = [];
  for (const korjattu of [false, true]) {
    const juuri = await mkdtemp(path.join(tmpdir(), "wt-"));
    const hak = path.join(juuri, "julkinen");
    await mkdir(hak);
    const s = await kaynnista(lataukset(hak, korjattu));
    const laheta = (nimi: string, data: Buffer) =>
      fetch(`${s.url}/lataa?nimi=${encodeURIComponent(nimi)}`,
            { method: "POST", body: new Uint8Array(data) });
    const sarake: string[] = [];
    const v = await laheta("kuva.html", HTML);
    sarake.push(v.status === 201
      ? `201, jaetaan ${(await fetch(s.url + await v.text()))
          .headers.get("content-type")}`
      : `${v.status}`);
    await laheta("../ohitus.png", PNG);
    sarake.push((await readdir(juuri)).includes("ohitus.png")
      ? "ulos hakemistosta" : "palvelimen nimellä");
    const kuva = await fetch(s.url + await (await laheta("a.png", PNG))
      .text());
    for (const o of ["content-disposition", "x-content-type-options",
                     "content-security-policy"]) {
      sarake.push(kuva.headers.get(o) ?? "–");
    }
    sarakkeet.push(sarake);
    await s.sulje();
  }
  const rivit = ["kuva.html (skripti)", "../ohitus.png",
                 "Content-Disposition", "X-Content-Type-Options",
                 "Content-Security-Policy"]
    .map((n, i) => [n, sarakkeet[0]![i]!, sarakkeet[1]![i]!]);
  taulu(["lataus", "haavoittuva", "korjattu"], rivit.slice(0, 2));
  console.log();
  taulu(["kuvan a.png jakelu", "haavoittuva", "korjattu"], rivit.slice(2));
}

function ohjaus(): void {
  taulu(["?seuraava=", "haavoittuva", "korjattu"],
    ["https://ansa.example/", "//ansa.example",
     "/\\ansa.example", "javascript:alert(1)",
     "/tilit?sivu=2#saldo"].map((a) =>
      [a, seuraavaHaavoittuva(a), seuraava(a)]));
}

async function skanneri(): Promise<void> {
  for (const [nimi, puolustus] of [
    ["haavoittuva palsta", { escapoi: false, csp: false }],
    ["korjattu palsta", { escapoi: true, csp: true }]] as const) {
    const s = await kaynnista(palsta(puolustus));
    console.log(`${nimi}:`);
    for (const h of await skannaa(s.url, ["/?q=kahvi"])) {
      console.log(`  ${h.kohde}  ${h.ongelma}`);
    }
    await s.sulje();
  }
}

const NAYTOKSET: Record<string, () => void | Promise<void>> = {
  "02-sql": sql, "02-nosql": nosql, "02-komento": komento, "02-ssrf": ssrf,
  "04-cors": cors04, "05-istunnot": istunnot,
  "06-kaytanto": kaytanto, "06-arvailu": arvailu, "06-rajoitus": rajoitus,
  "06-palautus": palautus, "07-totp": totpNaytos,
  "08-kirjautumis-csrf": kirjautumisCsrf, "08-pkce": pkce,
  "08-paluuosoite": paluuosoite, "09-jwt": jwt, "10-valtuutus": valtuutus,
  "11-lataus": lataus, "11-ohjaus": ohjaus, "12-skanneri": skanneri,
};

const valinta = process.argv[2] ?? "";
if (valinta === "--lista") {
  console.log(Object.keys(NAYTOKSET).join("\n"));
} else if (NAYTOKSET[valinta]) {
  await NAYTOKSET[valinta]();
} else {
  console.error("käyttö: node src/naytos.ts --lista | <näytös>");
  process.exit(2);
}
