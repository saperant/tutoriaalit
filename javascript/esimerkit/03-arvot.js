// @alku typeof
import { inspect } from "node:util";

const arvot = [42, 4.2, 10n, "teksti", true, undefined, null,
  Symbol("id"), { a: 1 }, [1, 2], () => 0];
for (const arvo of arvot) {
  console.log(`${inspect(arvo).padEnd(23)} ${typeof arvo}`);
}
// @loppu typeof

// @alku luvut
console.log(0.1 + 0.2, 0.1 + 0.2 === 0.3);
console.log(Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON);
console.log(Number.MAX_SAFE_INTEGER, 2 ** 53 === 2 ** 53 + 1);
console.log(9007199254740993n * 2n);
console.log(7 / 2, Math.trunc(7 / 2), 7 % 3, -7 % 3);
console.log(1 / 0, -1 / 0, 0 / 0);
// @loppu luvut

// @alku muunnokset
console.log(Number("42"), Number(" 4.5 "), Number(""), Number("4x"));
console.log(Number.parseInt("42px", 10), Number.parseFloat("3.5e2"));
console.log(String(12), (255).toString(16), Boolean(""), Boolean("0"));
// Implisiittiset muunnokset: + suosii merkkijonoja, muut operaattorit
// lukuja. Tyyppitarkistin hylkää jälkimmäiset, joten ne on kuitattu.
// @ts-expect-error: merkkijono aritmetiikassa
const erotus = "5" - 1;
// @ts-expect-error: totuusarvo aritmetiikassa
const summa = true + 1;
console.log("5" + 1, erotus, summa);
// @loppu muunnokset
