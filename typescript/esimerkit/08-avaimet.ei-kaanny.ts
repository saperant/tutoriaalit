// Object.keys palauttaa string[], ei keyof T: olio voi sisältää
// rakenteellisesti muitakin kenttiä kuin tyyppi kertoo.
type Hinnat = { omena: number; leipa: number };
const hinnat: Hinnat = { omena: 0.45, leipa: 2.9 };

let summa = 0;
for (const k of Object.keys(hinnat)) summa += hinnat[k]; // @virhe
for (const h of Object.values(hinnat)) summa += h; // oikea tapa tähän
for (const [tuote, h] of Object.entries(hinnat)) {
  console.log(`${tuote}: ${h}`);
}
console.log(summa.toFixed(2));
