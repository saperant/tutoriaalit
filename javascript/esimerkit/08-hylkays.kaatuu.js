/**
 * @param {string} tuote
 * @returns {Promise<number>}
 */
async function haeHinta(tuote) {
  await new Promise((valmis) => setTimeout(valmis, 5));
  throw new Error(`hintaa ei löydy: ${tuote}`);
}

// Lupaus jää käsittelemättä: ei awaitia eikä catchia. Node lopettaa
// prosessin käsittelemättömään hylkäykseen (unhandled rejection).
haeHinta("kahvi");
setTimeout(() => console.log("tätä ei tulosteta"), 50);
