// @alku aikaleima
// Date on aikaleima: millisekunteja hetkestä 1970-01-01T00:00:00Z.
// Kuukaudet numeroidaan nollasta: 10 on marraskuu.
const julkaisu = new Date(Date.UTC(2026, 10, 23, 8, 15));
console.log(julkaisu.getTime(), julkaisu.toISOString());

// ISO 8601 -merkkijono, jossa on Z tai siirtymä, on yksiselitteinen.
const sama = new Date("2026-11-23T10:15:00+02:00");
console.log(sama.getTime() === julkaisu.getTime());
// @loppu aikaleima

// @alku ansat
// Pelkkä päivämäärä jäsennetään UTC-aikana. Jos mukana on kellonaika
// ilman vyöhykettä, se tulkitaan koneen paikalliseksi ajaksi.
console.log(new Date("2026-11-23").toISOString());

// Date on muuttuva olio: set-metodit muuttavat sitä itseään, joten
// laskentaa varten tehdään kopio. Ylivuoto siirtyy seuraavaan kuuhun.
const erapaiva = new Date(julkaisu);
erapaiva.setUTCDate(erapaiva.getUTCDate() + 14);
console.log(erapaiva.toISOString().slice(0, 10));

// Virheellinen syöte ei heitä poikkeusta, vaan tulos on Invalid Date.
const rikki = new Date("23.11.2026");
console.log(Number.isNaN(rikki.getTime()));
// @loppu ansat

// @alku muotoilu
/** @param {string} vyohyke */
const muotoilija = (vyohyke) =>
  new Intl.DateTimeFormat("fi-FI", {
    dateStyle: "full",
    timeStyle: "short",
    timeZone: vyohyke,
  });
console.log(muotoilija("Europe/Helsinki").format(julkaisu));
console.log(muotoilija("Asia/Tokyo").format(julkaisu));

// Kesto on aikaleimojen erotus.
const PAIVA_MS = 24 * 60 * 60 * 1000;
console.log((erapaiva.getTime() - julkaisu.getTime()) / PAIVA_MS);
// @loppu muotoilu
