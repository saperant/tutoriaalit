// @alku sanakirja
// Tavallinen olio sanakirjana: avaimet muuttuvat merkkijonoiksi, ja
// perityt kentät (esim. "constructor") näyttävät olemassa olevilta.
/** @type {Record<string, number>} */
const olio = {};
olio[1] = 10;
olio["1"] += 5;
console.log(Object.keys(olio), "constructor" in olio);

// Map: mikä tahansa avain, koko, lisäysjärjestys, ei perittyjä avaimia.
/** @type {Map<number | string, number>} */
const kartta = new Map();
kartta.set(1, 10).set("1", 20);
console.log(kartta.size, kartta.get(1), kartta.get("1"));
// @loppu sanakirja

// @alku oliot
const aino = { nimi: "Aino" };
/** @type {Map<{ nimi: string }, string[]>} */
const roolit = new Map([[aino, ["admin"]]]);
console.log(roolit.get(aino), roolit.get({ nimi: "Aino" }));
// @loppu oliot

// @alku joukot
const tilatut = new Set(["kahvi", "tee", "kahvi", "mehu"]);
const varastossa = new Set(["tee", "mehu", "leipä"]);
const puuttuu = [...tilatut].filter((t) => !varastossa.has(t));
const yhteiset = [...tilatut].filter((t) => varastossa.has(t));
console.log(tilatut.size, puuttuu, yhteiset);
// Duplikaattien poisto järjestys säilyttäen:
console.log([...new Set([3, 1, 3, 2, 1])]);
// @loppu joukot

// @alku ryhmittely
const tapahtumat = [
  { kayttaja: aino, toiminto: "kirjautui" },
  { kayttaja: { nimi: "Eero" }, toiminto: "osti" },
  { kayttaja: aino, toiminto: "osti" },
];
const kayttajittain = Map.groupBy(tapahtumat, (t) => t.kayttaja);
for (const [kayttaja, lista] of kayttajittain) {
  console.log(kayttaja.nimi, lista.map((t) => t.toiminto));
}
// @loppu ryhmittely
