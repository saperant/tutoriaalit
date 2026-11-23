/** @typedef {{ tuote: string, maara: number }} Tilausrivi */

/**
 * @param {Tilausrivi[]} rivit
 * @returns {number}
 */
function kappaleet(rivit) {
  let yhteensa = 0;
  for (const rivi of rivit) {
    yhteensa += rivi.maara;
    yhteensa += rivi.mara; // @virhe
  }
  return yhteensa;
}

console.log(kappaleet([{ tuote: "omena", maara: 3 }]));
