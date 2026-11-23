// @alku muotoilu
const rivit = [
  { tuote: "Kahvi, tumma paahto", maara: 2, hinta: 6.5 },
  { tuote: "Tee", maara: 12, hinta: 4.25 },
  { tuote: "Kaurakeksi", maara: 1, hinta: 1234.5 },
];

// Intl-oliot luodaan kerran ja käytetään uudelleen.
const euro = new Intl.NumberFormat("fi-FI", {
  style: "currency",
  currency: "EUR",
});
const pvm = new Intl.DateTimeFormat("fi-FI", {
  dateStyle: "long",
  timeZone: "Europe/Helsinki",
});

console.log(`Lasku ${pvm.format(new Date(Date.UTC(2026, 10, 23)))}`);
for (const { tuote, maara, hinta } of rivit) {
  const nimi = tuote.length > 14 ? `${tuote.slice(0, 13)}…` : tuote;
  console.log(
    `${nimi.padEnd(15)}${String(maara).padStart(4)} kpl` +
      `${euro.format(maara * hinta).padStart(14)}`,
  );
}
const yhteensa = rivit.reduce((s, r) => s + r.maara * r.hinta, 0);
console.log(`${"Yhteensä".padEnd(23)}${euro.format(yhteensa).padStart(14)}`);
// @loppu muotoilu

// @alku perus
console.log((2 / 3).toFixed(2), (1234.5).toLocaleString("en-US"));
// 1.005 on binäärisenä hieman alle 1.005, joten se pyöristyy alaspäin.
console.log((1.005).toFixed(2), Math.round(1.005 * 100) / 100);
// Rahasummat lasketaan kokonaislukuina sentteinä.
const sentit = 2 * 650 + 12 * 425;
console.log(sentit, (sentit / 100).toFixed(2));
// @loppu perus
