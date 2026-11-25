import { appendFile, open, readFile, rm, writeFile } from "node:fs/promises";

const polku = "mittaukset.csv";
try {
  // @alku kirjoitus
  // Lupausversiot eivät tuki tapahtumasilmukkaa levyn odotuksen ajaksi.
  await writeFile(polku, "aika;arvo\n08:00;21.5\n08:10;21.9\n", "utf8");
  await appendFile(polku, "08:20;x\n08:30;22.4\n", "utf8");
  // @loppu kirjoitus

  // @alku luku
  // Pieni tiedosto luetaan kerralla, suuri riveittäin virtana.
  const kaikki = await readFile(polku, "utf8");
  console.log(kaikki.split("\n").length - 1, "riviä");

  const kahva = await open(polku);
  try {
    let summa = 0;
    let maara = 0;
    for await (const rivi of kahva.readLines({ encoding: "utf8" })) {
      const arvo = Number(rivi.split(";")[1]);
      if (Number.isFinite(arvo)) {
        summa += arvo;
        maara += 1;
      }
    }
    console.log(`keskiarvo ${(summa / maara).toFixed(2)} (${maara} arvoa)`);
  } finally {
    await kahva.close();
  }
  // @loppu luku

  // @alku virhe
  // Puuttuva tiedosto on virhe, jolla on koodi.
  try {
    await readFile("ei-ole.csv", "utf8");
  } catch (virhe) {
    if (!(virhe instanceof Error) || !("code" in virhe)) throw virhe;
    console.log(virhe.code);
  }
  // @loppu virhe
} finally {
  await rm(polku, { force: true });   // esimerkki siivoaa jälkensä
}
