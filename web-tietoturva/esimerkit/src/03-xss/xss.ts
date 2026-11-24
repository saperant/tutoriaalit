// Keskustelupalsta, jossa on kolme XSS-reittiä: heijastettu (haku),
// tallennettu (kommentit) ja DOM-pohjainen (tervehdys URL:n
// fragmentista). Asetukset kytkevät puolustukset päälle yksitellen.
import { randomBytes } from "node:crypto";
import { type Kasittelija, h, html, lomake } from "../http.ts";

export type Puolustus = { escapoi: boolean; csp: boolean };

// @alku csp
function cspOtsake(nonce: string): string {
  return [
    "default-src 'self'",
    `script-src 'nonce-${nonce}' 'strict-dynamic'`,
    "object-src 'none'",
    "base-uri 'none'",
    "require-trusted-types-for 'script'",
  ].join("; ");
}
// @loppu csp

export function palsta(p: Puolustus): Kasittelija {
  const kommentit: string[] = [];
  const e = (t: string) => (p.escapoi ? h(t) : t);

  return (pyynto) => {
    if (pyynto.metodi === "POST" && pyynto.polku === "/kommentit") {
      kommentit.push(lomake(pyynto).get("teksti") ?? "");
      return { tila: 303, otsakkeet: { Location: "/" } };
    }
    const nonce = randomBytes(16).toString("base64");
    const q = pyynto.haku.get("q") ?? "";
    // @alku sivu
    const sivu = `<!doctype html><html lang="fi"><title>Palsta</title>
      <p id="tervehdys"></p>
      <p>Hakusi: ${e(q)}</p>
      <ul>${kommentit.map((k) => `<li>${e(k)}</li>`).join("")}</ul>
      <form method="post" action="/kommentit">
        <input name="teksti"><button>Lähetä</button></form>
      <script nonce="${nonce}">
        const nimi = decodeURIComponent(location.hash.slice(1));
        const kohde = document.getElementById("tervehdys");
        ${p.escapoi
          ? "kohde.textContent = 'Hei ' + nimi;"
          : "kohde.innerHTML = 'Hei ' + nimi;"}
      </script>`;
    // @loppu sivu
    return html(sivu, p.csp ? { "Content-Security-Policy":
                                  cspOtsake(nonce) } : {});
  };
}
