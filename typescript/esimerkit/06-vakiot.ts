// enumin korvaajat: literaaliunioni, vakio-olio ja vakiotaulukko.
// 1. Pelkkä unioni riittää useimmiten.
type Taso = "info" | "varoitus" | "virhe";

// 2. Vakio-olio, kun nimille halutaan arvot (vrt. enum).
const HTTP_TILA = {
  ok: 200,
  eiLoydy: 404,
  palvelinvirhe: 500,
} as const;
type HttpTila = (typeof HTTP_TILA)[keyof typeof HTTP_TILA]; // 200|404|500

// 3. Vakiotaulukko, kun arvot pitää myös käydä läpi tai tarkistaa.
const TASOT = ["info", "varoitus", "virhe"] as const satisfies Taso[];

function onTaso(x: string): x is Taso {
  return (TASOT as readonly string[]).includes(x);
}

function kuvaa(tila: HttpTila): string {
  switch (tila) {
    case HTTP_TILA.ok: return "kunnossa";
    case HTTP_TILA.eiLoydy: return "ei löydy";
    case HTTP_TILA.palvelinvirhe: return "palvelinvirhe";
  }
}

for (const syote of ["varoitus", "kriittinen"]) {
  console.log(syote, onTaso(syote) ? "kelpaa" : "ei kelpaa");
}
console.log(TASOT.join(" < "), kuvaa(404), kuvaa(HTTP_TILA.ok));
