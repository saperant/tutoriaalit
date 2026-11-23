// Ohjausvuon analyysi kaventaa tyyppiä haara kerrallaan.
type Syote = string | number | Date | null | undefined;

function kuvaa(x: Syote): string {
  if (x == null) return "puuttuu"; // null tai undefined
  if (typeof x === "string") return `teksti (${x.length} merkkiä)`;
  if (typeof x === "number") return `luku ${x.toFixed(1)}`;
  return `päivä ${x.toISOString().slice(0, 10)}`; // jäljellä Date
}

for (const x of ["omena", 4.25, new Date(Date.UTC(2026, 10, 23)), null]) {
  console.log(kuvaa(x));
}

// Totuusarvokavennus ohittaa myös 0:n ja tyhjän merkkijonon.
function alennusVaarin(prosentti?: number): string {
  return prosentti ? `${prosentti} %` : "ei alennusta";
}
function alennus(prosentti?: number): string {
  return prosentti !== undefined ? `${prosentti} %` : "ei alennusta";
}
console.log(alennusVaarin(0), "|", alennus(0));

// in-operaattori kaventaa olioiden unionia.
type Kortti = { kortinNumero: string };
type Lasku = { viite: string; erapaiva: string };
function maksutapa(m: Kortti | Lasku): string {
  return "viite" in m ? `lasku, viite ${m.viite}` : "kortti";
}
console.log(maksutapa({ viite: "1232", erapaiva: "2026-12-01" }));
