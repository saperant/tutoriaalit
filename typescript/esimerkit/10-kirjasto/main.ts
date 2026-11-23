// JavaScript-modulin käyttö tyypitettynä ja tyyppien tuonti.
import { alennus, verollinen, type Alennusehdot } from "./hinnoittelu.js";
import type { Kori, Kuitti } from "./tyypit.ts";

function kuitti(kori: Kori, ehdot: Alennusehdot): Kuitti {
  const yhteensa = kori
    .map((r) => verollinen(alennus(r.hinta, ehdot)))
    .reduce((a, b) => a + b, 0);
  return { rivit: kori.length, yhteensa: Math.round(yhteensa * 100) / 100 };
}

const kori: Kori = [
  { tuote: "kahvi", hinta: 7.95 },
  { tuote: "leipä", hinta: 2.9 },
];
console.log(kuitti(kori, {}));
console.log(kuitti(kori, { prosentti: 20, enintaan: 1 }));
