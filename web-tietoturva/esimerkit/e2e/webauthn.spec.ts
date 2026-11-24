import { test, expect } from "@playwright/test";
import { kaynnista, type Kasittelija } from "../src/http.ts";
import { palvelu } from "../src/07-mfa/webauthn.ts";

// @alku testi
test("pääsyavain: rekisteröinti, kirjautuminen ja kalastelu", async ({
  page,
}) => {
  let k: Kasittelija = () => ({});
  const s = await kaynnista((p) => k(p));
  const oikea = s.url.replace("127.0.0.1", "localhost");
  k = palvelu("localhost", oikea);
  // Virtuaalinen todennin: kuin puhelimen tai kannettavan sisäinen
  // pääsyavain, jossa käyttäjä on aina varmistettu.
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("WebAuthn.enable");
  await cdp.send("WebAuthn.addVirtualAuthenticator", { options: {
    protocol: "ctap2", transport: "internal", hasResidentKey: true,
    hasUserVerification: true, isUserVerified: true } });
  try {
    await page.goto(oikea);
    expect(await page.evaluate(() => rekisteroi("aino")))
      .toEqual({ ok: true });
    expect(await page.evaluate(() => kirjaudu()))
      .toEqual({ kayttaja: "aino" });

    // Sama sivu eri alkuperästä (127.0.0.1), kuten kalastelusivu:
    // selain ei anna käyttää localhostin avainta.
    await page.goto(s.url);
    const virhe = await page.evaluate(() =>
      kirjaudu().then(() => "onnistui", (e: Error) => e.name));
    expect(virhe).toBe("SecurityError");
  } finally {
    await s.sulje();
  }
});
// @loppu testi

declare global {
  function rekisteroi(kayttaja: string): Promise<unknown>;
  function kirjaudu(): Promise<unknown>;
}
