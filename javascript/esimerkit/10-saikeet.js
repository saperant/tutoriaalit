// Prosessoriintensiivinen työ säikeisiin. Tapahtumasilmukka ei
// tukkeudu, kun pääsäie vain odottaa tuloksia.
import { Worker, isMainThread, parentPort, workerData }
  from "node:worker_threads";

/**
 * Laskee alkuluvut puoliavoimelta väliltä [alku, loppu).
 * @param {number} alku
 * @param {number} loppu
 */
function alkulukuja(alku, loppu) {
  let maara = 0;
  for (let n = Math.max(alku, 2); n < loppu; n++) {
    let alkuluku = true;
    for (let d = 2; d * d <= n; d++) {
      if (n % d === 0) {
        alkuluku = false;
        break;
      }
    }
    if (alkuluku) maara += 1;
  }
  return maara;
}

// @alku saikeet
if (isMainThread) {
  const RAJA = 2_000_000;
  const SAIKEITA = 4;
  const pala = Math.ceil(RAJA / SAIKEITA);

  /** @type {Promise<number>[]} */
  const osat = [];
  for (let i = 0; i < SAIKEITA; i++) {
    const vali = [i * pala, Math.min((i + 1) * pala, RAJA)];
    // Sama tiedosto ajetaan säikeessä; data kopioidaan viestinä.
    const saie = new Worker(new URL(import.meta.url), { workerData: vali });
    osat.push(new Promise((valmis, virhe) => {
      saie.once("message", valmis);
      saie.once("error", virhe);
    }));
  }
  const maarat = await Promise.all(osat);
  console.log(maarat.reduce((a, b) => a + b, 0), "alkulukua");
} else {
  const [alku, loppu] = /** @type {[number, number]} */ (workerData);
  parentPort?.postMessage(alkulukuja(alku, loppu));
}
// @loppu saikeet
