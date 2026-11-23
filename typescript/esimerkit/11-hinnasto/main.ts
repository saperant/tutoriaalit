import { rivihinta, type Hintasaanto } from "./hinnasto.ts";

const kahvi: Hintasaanto = {
  laji: "maara",
  rajat: [{ alkaen: 1, sentit: 795 }, { alkaen: 6, sentit: 690 }],
};
for (const maara of [1, 6, 12]) {
  console.log(maara, (rivihinta(kahvi, maara) / 100).toFixed(2));
}
