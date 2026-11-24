import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdir, mkdtemp, readdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { kaynnista } from "../http.ts";
import { lataukset } from "./lataus.ts";
import { seuraava, seuraavaHaavoittuva, turvaotsakkeet } from "./ohjaus.ts";

const HTML = Buffer.from("<script>alert(document.cookie)</script>");
const PNG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

// @alku lataus
for (const korjattu of [false, true]) {
  test(`lataus, ${korjattu ? "korjattu" : "haavoittuva"}`, async () => {
    const juuri = await mkdtemp(path.join(tmpdir(), "wt-"));
    const hak = path.join(juuri, "julkinen");
    await mkdir(hak);
    const s = await kaynnista(lataukset(hak, korjattu));
    const laheta = (nimi: string, data: Buffer) =>
      fetch(`${s.url}/lataa?nimi=${encodeURIComponent(nimi)}`,
            { method: "POST", body: new Uint8Array(data) });
    try {
      // Skripti ladataan "kuvana" ja jaetaan HTML-sivuna samasta
      // alkuperästä: tallennettu XSS.
      const v = await laheta("kuva.html", HTML);
      assert.equal(v.status, korjattu ? 415 : 201);
      if (!korjattu) {
        const sivu = await fetch(s.url + await v.text());
        assert.equal(sivu.headers.get("content-type"), "text/html");
      }
      // Polku ohittaa hakemiston.
      const ohitus = await laheta("../ohitus.png", PNG);
      assert.equal(ohitus.status, 201);
      assert.equal((await readdir(juuri)).includes("ohitus.png"),
                   !korjattu);

      if (korjattu) {
        const kuva = await fetch(s.url + await (await laheta("a", PNG))
          .text());
        assert.equal(kuva.headers.get("content-type"), "image/png");
        assert.equal(kuva.headers.get("content-disposition"), "attachment");
        assert.deepEqual(Buffer.from(await kuva.arrayBuffer()), PNG);
      }
    } finally {
      await s.sulje();
    }
  });
}
// @loppu lataus

// @alku ohjaus-testi
test("avoin uudelleenohjaus", () => {
  const ansa = "https://pankki-kirjaudu.example/";
  assert.equal(seuraavaHaavoittuva(ansa), ansa);
  for (const hyokkays of [ansa, "//pankki-kirjaudu.example",
                          "/\\pankki-kirjaudu.example",
                          "javascript:alert(1)"]) {
    assert.equal(seuraava(hyokkays), "/", hyokkays);
  }
  assert.equal(seuraava("/tilit?sivu=2#saldo"), "/tilit?sivu=2#saldo");
});
// @loppu ohjaus-testi

test("turvaotsakkeet", () => {
  const o = turvaotsakkeet("abc");
  assert.match(o["Content-Security-Policy"]!, /'nonce-abc'/);
  assert.match(o["Content-Security-Policy"]!, /frame-ancestors 'none'/);
  assert.equal(o["X-Content-Type-Options"], "nosniff");
});
