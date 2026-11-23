// @alku protokolla
/** Puoliavoin väli [alku, loppu) askeleella. */
class Vali {
  /**
   * @param {number} alku
   * @param {number} loppu
   * @param {number} [askel]
   */
  constructor(alku, loppu, askel = 1) {
    this.alku = alku;
    this.loppu = loppu;
    this.askel = askel;
  }

  // Generaattorimetodi toteuttaa iteraattoriprotokollan.
  *[Symbol.iterator]() {
    for (let i = this.alku; i < this.loppu; i += this.askel) yield i;
  }
}

const vali = new Vali(0, 10, 3);
console.log([...vali], Math.max(...vali));
for (const x of new Vali(1, 3)) console.log(x);
// @loppu protokolla

// @alku laiska
/**
 * @template T
 * @param {Iterable<T>} lahde
 * @param {(arvo: T) => boolean} ehto
 */
function* suodata(lahde, ehto) {
  for (const arvo of lahde) if (ehto(arvo)) yield arvo;
}

/**
 * @template T
 * @param {Iterable<T>} lahde
 * @param {number} n
 */
function* ota(lahde, n) {
  if (n <= 0) return;
  for (const arvo of lahde) {
    yield arvo;
    if (--n === 0) return;
  }
}

function* luonnolliset() {
  for (let n = 1; ; n++) yield n;   // ääretön, mutta laiska
}

/** @param {number} n */
const onAlkuluku = (n) => {
  if (n < 2) return false;
  for (let d = 2; d * d <= n; d++) if (n % d === 0) return false;
  return true;
};
console.log([...ota(suodata(luonnolliset(), onAlkuluku), 8)].join(" "));
// @loppu laiska

// @alku kasin
const iter = new Vali(0, 2)[Symbol.iterator]();
for (let i = 0; i < 3; i++) console.log(iter.next());
// @loppu kasin
