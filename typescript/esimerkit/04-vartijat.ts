// Omat tyyppivartijat (x is T) ja varmistusfunktiot (asserts).
type Tuote = { nimi: string; hinta: number };

function onTuote(x: unknown): x is Tuote {
  return typeof x === "object" && x !== null
    && "nimi" in x && typeof x.nimi === "string"
    && "hinta" in x && typeof x.hinta === "number";
}

function varmista(ehto: unknown, viesti: string): asserts ehto {
  if (!ehto) throw new Error(viesti);
}

const data: unknown = JSON.parse(
  '[{"nimi": "omena", "hinta": 0.45}, {"nimi": "leipä"}]');
varmista(Array.isArray(data), "odotettiin taulukkoa");
// Tästä eteenpäin data on any[]: rajataan heti tarkemmin.
const tuotteet = data.filter(onTuote); // Tuote[] (vartija suodattimena)
console.log(tuotteet.map((t) => `${t.nimi} ${t.hinta}`).join(", "));
console.log(`${data.length - tuotteet.length} virheellinen`);

// Myös ilman omaa vartijaa TypeScript päättelee suodattimen tyypin,
// kun ehto on yksinkertainen:
const hinnat = [1.2, undefined, 3.4].filter((h) => h !== undefined);
console.log(hinnat.reduce((a, b) => a + b, 0)); // hinnat: number[]
