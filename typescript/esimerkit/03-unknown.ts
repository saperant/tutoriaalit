// any sammuttaa tarkistukset; unknown vaatii kavennuksen ennen käyttöä.
function pituusAny(x: any): number {
  return x.length; // kääntyy aina, kaatuu ajossa jos x ei ole sopiva
}

function pituus(x: unknown): number {
  if (typeof x === "string" || Array.isArray(x)) return x.length;
  if (x instanceof Map || x instanceof Set) return x.size;
  return 0;
}

console.log(pituusAny("kissa"), pituusAny(42)); // 5 undefined
console.log(pituus("kissa"), pituus([1, 2]), pituus(new Set([1])),
  pituus(42));

// any leviää: tuloksen tyyppi on taas any.
const data: any = JSON.parse('{"hinta": "12"}');
const hinta = data.hinta * 2; // any; merkkijono muuttuu luvuksi
console.log(hinta);
