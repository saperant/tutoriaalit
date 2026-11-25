const rivi = "Tilaus 1042: kahvi 6,50 €, tee 4,25 €, toimitus 4,90 €";

// @alku haku
// g-lippu hakee kaikki osumat, ja matchAll antaa niiden ryhmät.
const hinta = /(?<nimi>\p{L}+) (?<eurot>\d+),(?<sentit>\d{2}) €/gu;
for (const osuma of rivi.matchAll(hinta)) {
  const { nimi, eurot, sentit } = osuma.groups ?? {};
  console.log(nimi, Number(eurot) * 100 + Number(sentit), osuma.index);
}
// @loppu haku

// @alku korvaus
// Korvaaja voi olla funktio, joka saa osuman ja sen ryhmät.
const pisteilla = rivi.replace(/(\d+),(\d{2})/g, (_, e, s) => `${e}.${s}`);
console.log(pisteilla);
// i = kirjainkoosta riippumaton, m = ^ ja $ joka rivillä.
console.log(/^tee/im.test("Kahvi\nTEE"), "a1b22".split(/\d+/));
// @loppu korvaus

// @alku ansa
// g-lipullinen lauseke muistaa kohdan (lastIndex), josta seuraava haku
// alkaa. Sama olio antaa siksi samalle syötteelle vuorotellen eri tuloksen.
const numero = /\d+/g;
console.log(numero.test("a1"), numero.lastIndex, numero.test("a1"));
// Korjaus: ei g-lippua test-kutsuun tai uusi lauseke joka kerralla.
console.log(/\d+/.test("a1"), /\d+/.test("a1"));
// @loppu ansa
