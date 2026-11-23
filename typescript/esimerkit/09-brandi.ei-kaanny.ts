// Brändätty tyyppi: rakenteeltaan string, mutta ei vaihdettavissa.
type Sahkoposti = string & { readonly __brandi: "Sahkoposti" };

function sahkoposti(x: string): Sahkoposti | undefined {
  const s = x.trim().toLowerCase();
  return /^[^@\s]+@[^@\s]+\.[a-z]{2,}$/.test(s) ? s as Sahkoposti
    : undefined;
}

function laheta(vastaanottaja: Sahkoposti, aihe: string): string {
  return `${vastaanottaja}: ${aihe}`;
}

console.log(laheta("aino@example.com", "kuitti")); // @virhe: ei tarkistettu
const osoite = sahkoposti(" Aino@Example.com ");
if (osoite) console.log(laheta(osoite, "kuitti"));
