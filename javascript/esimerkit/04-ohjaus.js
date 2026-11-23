/** @type {Record<string, number>} */
const varasto = { kahvi: 7, tee: 0, mehu: 12 };

// @alku silmukat
for (const [tuote, maara] of Object.entries(varasto)) {
  if (maara === 0) continue;
  console.log(`${tuote}: ${maara}`);
}

const taulukko = ["a", "b"];
for (const i in taulukko) console.log(typeof i, i);  // avaimet merkkijonoina
for (const arvo of taulukko) console.log(arvo);       // arvot
// @loppu silmukat

// @alku switch
/** @param {number} koodi */
function luokittele(koodi) {
  switch (true) {
    case koodi >= 500: return "palvelinvirhe";
    case koodi >= 400: return "asiakasvirhe";
    case koodi >= 300: return "uudelleenohjaus";
    default: return "ok";
  }
}
console.log([200, 301, 404, 503].map(luokittele).join(", "));
// @loppu switch

// @alku nimetty
const ruudukko = [[1, 2, 3], [4, -5, 6], [7, 8, -9]];
let ensimmainen = null;
haku: for (const [r, rivi] of ruudukko.entries()) {
  for (const [s, arvo] of rivi.entries()) {
    if (arvo < 0) {
      ensimmainen = { r, s, arvo };
      break haku;
    }
  }
}
console.log(ensimmainen);
// @loppu nimetty
