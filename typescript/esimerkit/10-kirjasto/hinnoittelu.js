// Vanha JavaScript-moduli, jota ei kirjoiteta uudelleen. Tyypit
// kuvataan erillisessä esittelytiedostossa hinnoittelu.d.ts.
export const ALV = 0.255;

export function verollinen(hinta, alv = ALV) {
  return Math.round(hinta * (1 + alv) * 100) / 100;
}

export function alennus(hinta, { prosentti = 0, enintaan = Infinity } = {}) {
  return Math.max(hinta - Math.min(hinta * prosentti / 100, enintaan), 0);
}
