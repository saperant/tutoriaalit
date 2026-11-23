// noUncheckedIndexedAccess: indeksointi voi palauttaa undefined.
const rivit: string[] = [];
const ensimmainen = rivit[0]; // tyyppi string | undefined

console.log(ensimmainen.toUpperCase()); // @virhe: voi olla undefined
console.log(ensimmainen?.toUpperCase() ?? "(ei rivejä)");

const hinnat: Record<string, number> = { omena: 0.45 };
const hinta = hinnat["päärynä"]; // number | undefined
console.log(hinta === undefined ? "ei hintaa" : hinta.toFixed(2));
