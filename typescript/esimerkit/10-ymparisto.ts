// Globaalin tyypin täydentäminen: sovellus kertoo, mitä
// ympäristömuuttujia se käyttää. declare-lohko on pelkkä esittely,
// joten se poistetaan ajosta kuten muutkin tyypit.
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      TILA?: "kehitys" | "tuotanto";
      PORTTI?: string;
    }
  }
}

// Esittely ei tarkista arvoja: ne jäsennetään silti reunalla.
function portti(): number {
  const n = Number(process.env.PORTTI ?? "8080");
  if (!Number.isInteger(n) || n < 1 || n > 65535) {
    throw new RangeError(`virheellinen PORTTI: ${process.env.PORTTI}`);
  }
  return n;
}

const tila = process.env.TILA ?? "kehitys";   // tyyppi on unioni
console.log(tila, portti());

export {};   // tekee tiedostosta modulin, jotta declare global on sallittu
