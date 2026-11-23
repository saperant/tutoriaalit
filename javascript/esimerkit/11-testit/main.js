import { hinta, valimuistilla } from "./hinnoittelu.js";

let hakuja = 0;
const kurssit = valimuistilla({
  async kurssi(valuutta) {
    hakuja += 1;
    return { SEK: 11.5, NOK: 11.8 }[valuutta] ?? Number.NaN;
  },
}, 60_000);

for (const valuutta of ["EUR", "SEK", "NOK", "SEK"]) {
  console.log(valuutta, await hinta({ sentit: 1250, valuutta }, kurssit));
}
console.log(`kurssihakuja ${hakuja}`);
