// Primitiivit, literaalityypit ja tyyppipäättely.
const kpl = 3; // tyyppi 3 (vakio: literaalityyppi)
let yhteensa = 0; // tyyppi number (muuttuja: levennetty)
yhteensa += kpl * 0.45;

const isot = 2n ** 64n; // bigint on oma tyyppinsä
const nimi: string = "omena";
const alennus: boolean = yhteensa > 1;

// Literaaliunioni rajaa arvojoukon.
type Valuutta = "EUR" | "SEK" | "USD";
const valuutta: Valuutta = "EUR";

// Mallimerkkijonotyypit (template literal types).
type Tunnus = `${Valuutta}-${number}`;
const tilinro: Tunnus = "EUR-1042";

// Monikko: kiinteä pituus ja paikkakohtaiset tyypit.
const sijainti: readonly [leveys: number, pituus: number] = [60.17, 24.94];

console.log(nimi, yhteensa.toFixed(2), alennus, valuutta, tilinro);
console.log(isot, sijainti[0]);
console.log(0.1 + 0.2 === 0.3, Number.MAX_SAFE_INTEGER);
