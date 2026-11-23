import { setTimeout as odota } from "node:timers/promises";

// @alku peruttava
/**
 * Pitkä työ, joka tarkistaa peruutussignaalin jokaisen vaiheen välissä.
 * @param {string} nimi
 * @param {AbortSignal} signaali
 */
async function raportti(nimi, signaali) {
  const vaiheet = [];
  for (const vaihe of ["haku", "laskenta", "muotoilu"]) {
    signaali.throwIfAborted();
    // Myös odotus keskeytyy, kun signaali laukeaa.
    await odota(30, undefined, { signal: signaali });
    vaiheet.push(vaihe);
  }
  return `${nimi}: ${vaiheet.join(", ")}`;
}
// @loppu peruttava

// @alku aikaraja
/**
 * @param {string} nimi
 * @param {AbortSignal} signaali
 */
async function aja(nimi, signaali) {
  try {
    console.log(await raportti(nimi, signaali));
  } catch (virhe) {
    if (!signaali.aborted) throw virhe;   // muu virhe kuin peruutus
    const syy = signaali.reason instanceof Error ? signaali.reason.name : "?";
    console.log(`${nimi}: keskeytyi (${syy})`);
  }
}

await aja("A", AbortSignal.timeout(500));
await aja("B", AbortSignal.timeout(40));

// Käyttäjän peruutus ja aikaraja yhdistettyinä: kumpi tahansa riittää.
const kayttaja = new AbortController();
setTimeout(() => kayttaja.abort(), 10);
await aja("C", AbortSignal.any([kayttaja.signal, AbortSignal.timeout(500)]));
// @loppu aikaraja
