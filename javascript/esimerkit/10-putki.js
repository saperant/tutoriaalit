// Asynkroninen iteraattoriputki: lokirivit luetaan virtana, ja jokainen
// vaihe on async-generaattori. Muistissa on kerrallaan vain yksi rivi,
// joten sama koodi toimii myös gigatavujen lokille.
import { createInterface } from "node:readline";
import { Readable } from "node:stream";

/** @typedef {{ aika: string, taso: string, kesto: number }} Tapahtuma */

// @alku vaiheet
/** @param {AsyncIterable<string>} rivit */
async function* jasenna(rivit) {
  for await (const rivi of rivit) {
    const [aika, taso, kesto] = rivi.split(" ");
    if (aika && taso && kesto) yield { aika, taso, kesto: Number(kesto) };
  }
}

/**
 * @param {AsyncIterable<Tapahtuma>} tapahtumat
 * @param {(t: Tapahtuma) => boolean} ehto
 */
async function* suodata(tapahtumat, ehto) {
  for await (const t of tapahtumat) if (ehto(t)) yield t;
}

/** @param {AsyncIterable<Tapahtuma>} tapahtumat */
async function tilasto(tapahtumat) {
  let maara = 0;
  let pisin = 0;
  for await (const t of tapahtumat) {
    maara += 1;
    pisin = Math.max(pisin, t.kesto);
  }
  return { maara, pisin };
}
// @loppu vaiheet

// @alku kaytto
const loki = [
  "08:00:01 INFO 12", "08:00:02 WARN 340", "rikkinäinen rivi",
  "08:00:05 INFO 8", "08:00:09 WARN 1210", "08:00:12 ERROR 15",
].join("\n");
const rivit = createInterface({ input: Readable.from([loki]) });

const tulos = await tilasto(
  suodata(jasenna(rivit), (t) => t.taso !== "INFO"),
);
console.log(tulos);
// @loppu kaytto
