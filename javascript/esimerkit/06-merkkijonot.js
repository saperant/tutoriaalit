// @alku unicode
// Emojit kirjoitetaan koodipisteinä, koska PDF:n fontissa niitä ei ole.
const sanat = [
  ["kissa", "kissa"],
  ["äiti", "äiti"],
  ["peukku", "\u{1F44D}"],                 // yksi koodipiste
  ["peukku + sävy", "\u{1F44D}\u{1F3FD}"],   // kaksi koodipistettä
  ["Suomen lippu", "\u{1F1EB}\u{1F1EE}"],    // aluemerkkipari
];
const graafit = new Intl.Segmenter("fi", { granularity: "grapheme" });
console.log("merkkijono       length  koodipisteet  merkit");
for (const [kuvaus, s] of sanat) {
  const nakyvat = [...graafit.segment(s)].length;
  console.log(kuvaus.padEnd(16), String(s.length).padEnd(7),
    String([...s].length).padEnd(13), nakyvat);
}
// @loppu unicode

// @alku normalisointi
/** @type {string} */
const yhdistetty = "a\u0308iti";   // a + yhdistyvä treema
console.log(yhdistetty === "äiti", yhdistetty.normalize("NFC") === "äiti");
// @loppu normalisointi

// @alku kasittely
const loki = "2026-11-23T08:15:02Z WARN levy 91 % täynnä (/var)";
const malli =
  /^(?<aika>\S+) (?<taso>[A-Z]+) (?<viesti>.*?)(?: \((?<polku>.+)\))?$/;
const osat = loki.match(malli)?.groups;
console.log(osat?.taso, osat?.polku, JSON.stringify(osat?.viesti));
console.log("a-b-c".replaceAll("-", "/"), "  x ".trim().padStart(3, "."));
console.log("Tilaus".startsWith("Til"), "kahvi,tee,,".split(","));
// @loppu kasittely

// @alku rakentaminen
// Merkkijonot ovat muuttumattomia. Moottorit optimoivat += -ketjut
// (köysirakenne), mutta taulukko ja join ovat selkeä tapa koota
// osista ja lisätä erottimet.
const rivit = [];
for (let i = 1; i <= 3; i++) rivit.push(`rivi ${i}`);
console.log(rivit.join(" | "));
// @loppu rakentaminen
