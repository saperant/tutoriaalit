// Tyypit poistetaan ennen ajoa: `as` ei tarkista mitään.
type Tilaus = { tuote: string; maara: number };

const json = '{"tuote": "omena", "maara": "3"}'; // määrä merkkijonona
const tilaus = JSON.parse(json) as Tilaus; // kääntäjä uskoo väitteen

console.log(tilaus.maara + 1); // ei 4 vaan merkkijonojen liitos
console.log(typeof tilaus.maara);

// Ajonaikainen tarkistus kertoo totuuden:
function onTilaus(x: unknown): x is Tilaus {
  return typeof x === "object" && x !== null
    && "tuote" in x && typeof x.tuote === "string"
    && "maara" in x && typeof x.maara === "number";
}
console.log(onTilaus(JSON.parse(json)));
