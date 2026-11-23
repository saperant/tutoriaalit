// @alku vertailu
/**
 * Tulostaa vertailujen tulokset. Parametrit ovat tyyppiä unknown, koska
 * tarkistin hylkäisi vertailut, joiden tyypit eivät voi olla samat.
 * @param {string} kuvaus
 * @param {unknown} a
 * @param {unknown} b
 */
function vertaa(kuvaus, a, b) {
  const tulokset = [a == b, a === b, Object.is(a, b)];
  const sarakkeet = tulokset.map((t) => String(t).padEnd(7)).join("");
  console.log(`${kuvaus.padEnd(19)}${sarakkeet}`.trimEnd());
}

console.log(`${"".padEnd(19)}==     ===    Object.is`);
vertaa('0 ja ""', 0, "");
vertaa('"1" ja 1', "1", 1);
vertaa("null ja undefined", null, undefined);
vertaa("NaN ja NaN", NaN, NaN);
vertaa("0 ja -0", 0, -0);
vertaa("[1] ja 1", [1], 1);
// @loppu vertailu

// @alku viitteet
const a = { tuote: "kahvi" };
const b = { tuote: "kahvi" };
const c = a;
console.log(a === b, a === c);
console.log([NaN].includes(NaN), [NaN].indexOf(NaN));
// Rakenteellinen vertailu tehdään itse tai kirjastolla:
// node:assert tarjoaa deepStrictEqual-funktion.
console.log(JSON.stringify(a) === JSON.stringify(b));
// @loppu viitteet
