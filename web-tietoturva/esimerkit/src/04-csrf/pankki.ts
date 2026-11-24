// Verkkopankki, jonka tilisiirto-lomake on CSRF-hyökkäyksen kohde.
// Haavoittuva versio luottaa pelkkään istuntoevästeeseen.
import { randomBytes, timingSafeEqual } from "node:crypto";
import { type Kasittelija, type Pyynto, h, html, lomake }
  from "../http.ts";

type Istunto = { kayttaja: string; csrf: string };

export function pankki(korjattu: boolean, alkupera: string): Kasittelija {
  const saldot = new Map([["aino", 1000], ["hyokkaaja", 0]]);
  const istunnot = new Map<string, Istunto>();
  const nimi = korjattu ? "__Host-istunto" : "istunto";

  // @alku eväste
  function luoIstunto(kayttaja: string): string {
    const id = randomBytes(32).toString("base64url");
    istunnot.set(id, { kayttaja,
                       csrf: randomBytes(32).toString("base64url") });
    return korjattu
      ? `${nimi}=${id}; Path=/; Secure; HttpOnly; SameSite=Lax`
      : `${nimi}=${id}; Path=/; Secure; SameSite=None`;
  }
  // @loppu eväste

  // @alku tarkistus
  function sallittu(p: Pyynto, istunto: Istunto): boolean {
    if (!korjattu) return true;
    // 1) Pyyntö tulee omalta sivulta (Origin-otsake).
    if (p.otsakkeet.origin !== alkupera) return false;
    // 2) Lomakkeen piilotettu tunniste vastaa istunnon tunnistetta.
    const annettu = Buffer.from(lomake(p).get("csrf") ?? "");
    const odotettu = Buffer.from(istunto.csrf);
    return annettu.length === odotettu.length &&
      timingSafeEqual(annettu, odotettu);
  }
  // @loppu tarkistus

  return (p) => {
    if (p.polku === "/kirjaudu") {
      return { tila: 303, otsakkeet: {
        "Set-Cookie": luoIstunto("aino"), Location: "/" } };
    }
    const istunto = istunnot.get(p.evasteet.get(nimi) ?? "");
    if (!istunto) return { tila: 401, runko: "Kirjaudu ensin" };
    // @alku kehys
    const kehys: Record<string, string> = korjattu
      ? { "Content-Security-Policy": "frame-ancestors 'none'",
          "X-Frame-Options": "DENY" }
      : {};
    // @loppu kehys
    if (p.metodi === "POST" && p.polku === "/siirto") {
      if (!sallittu(p, istunto)) return { tila: 403, runko: "Estetty" };
      const l = lomake(p);
      const summa = Number(l.get("summa"));
      const saaja = l.get("saaja") ?? "";
      if (!Number.isInteger(summa) || summa <= 0 || !saldot.has(saaja)) {
        return { tila: 400, runko: "Virheellinen siirto" };
      }
      saldot.set(istunto.kayttaja, saldot.get(istunto.kayttaja)! - summa);
      saldot.set(saaja, saldot.get(saaja)! + summa);
      return { tila: 303, otsakkeet: { Location: "/" } };
    }
    return html(`<!doctype html><title>Pankki</title>
      <p>Saldo: ${saldot.get(istunto.kayttaja)} €</p>
      <form method="post" action="/siirto">
        <input type="hidden" name="csrf" value="${h(istunto.csrf)}">
        <input name="saaja"><input name="summa">
        <button>Siirrä</button></form>`, kehys);
  };
}

// @alku hyokkaaja
// Hyökkääjän sivu toisella sivustolla: näkymätön lomake lähettää
// tilisiirron heti, kun uhri avaa sivun. Kehys yrittää upottaa pankin
// läpinäkyvänä (clickjacking).
export function hyokkaajanSivu(pankinOsoite: string): Kasittelija {
  return () => html(`<!doctype html><title>Voitit!</title>
    <form id="f" method="post" action="${pankinOsoite}/siirto">
      <input type="hidden" name="saaja" value="hyokkaaja">
      <input type="hidden" name="summa" value="500"></form>
    <iframe id="k" src="${pankinOsoite}/" style="opacity:0.01"></iframe>
    <script>
      if (location.hash === "#csrf") document.getElementById("f").submit();
    </script>`);
}
// @loppu hyokkaaja
