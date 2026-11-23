// Ylimääräisten kenttien tarkistus koskee vain tuoreita olioliteraaleja.
type Asetukset = { kieli: string; tumma?: boolean };

function kayta(a: Asetukset): string {
  return `${a.kieli}${a.tumma ? ", tumma" : ""}`;
}

console.log(kayta({ kieli: "fi", tumme: true })); // @virhe: kirjoitusvirhe
console.log(kayta({ kieli: "fi", tumma: true }));

// Sama kirjoitusvirhe muuttujan kautta menee läpi huomaamatta:
const luettu = { kieli: "sv", tumme: true };
console.log(kayta(luettu));
