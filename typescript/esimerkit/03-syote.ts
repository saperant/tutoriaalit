// Syötteen luku ja tulosteen muotoilu suomalaisittain.
import { createInterface } from "node:readline";

const euro = new Intl.NumberFormat("fi-FI", {
  style: "currency", currency: "EUR",
});
const prosentti = new Intl.NumberFormat("fi-FI", {
  style: "percent", maximumFractionDigits: 1,
});

const lukija = createInterface({ input: process.stdin });
const summat: number[] = [];
for await (const rivi of lukija) {
  const arvo = Number(rivi.trim().replace(",", "."));
  if (rivi.trim() === "" || !Number.isFinite(arvo)) {
    console.error(`ohitetaan: '${rivi}'`);
    continue;
  }
  summat.push(arvo);
}

const yhteensa = summat.reduce((a, b) => a + b, 0);
const suurin = Math.max(...summat);
console.log(`yhteensä ${euro.format(yhteensa)}`);
console.log(`suurin ${euro.format(suurin)}, ` +
  `osuus ${prosentti.format(suurin / yhteensa)}`);
