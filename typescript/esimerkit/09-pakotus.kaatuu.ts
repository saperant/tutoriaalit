// as-pakotus siirtää virheen käännösajasta ajoon ja kauas syystä.
type Asiakas = { nimi: string; osoite: { katu: string; kunta: string } };

const vastaus = '{"nimi": "Aino"}'; // osoite puuttuu
const asiakas = JSON.parse(vastaus) as Asiakas;

console.log(asiakas.nimi);
console.log(asiakas.osoite.kunta.toUpperCase());
