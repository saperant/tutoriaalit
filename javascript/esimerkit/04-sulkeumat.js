// @alku laskuri
/**
 * Moduulimalli: sulkeuma pitää tilan yksityisenä.
 * @param {number} raja  sallitut pyynnöt aikaikkunassa
 */
function luoRajoitin(raja) {
  let kaytetty = 0;
  return {
    /** @returns {boolean} */
    salli() {
      if (kaytetty >= raja) return false;
      kaytetty += 1;
      return true;
    },
    nollaa() {
      kaytetty = 0;
    },
  };
}

const rajoitin = luoRajoitin(2);
console.log(rajoitin.salli(), rajoitin.salli(), rajoitin.salli());
rajoitin.nollaa();
console.log(rajoitin.salli());
// @loppu laskuri

// @alku silmukka
/** @type {(() => number)[]} */
const vanhat = [];
for (var i = 0; i < 3; i++) vanhat.push(() => i);  // yksi yhteinen i

/** @type {(() => number)[]} */
const uudet = [];
for (let j = 0; j < 3; j++) uudet.push(() => j);   // oma j kierroksittain

console.log(vanhat.map((f) => f()), uudet.map((f) => f()));
// @loppu silmukka

// @alku memo
/**
 * Muistaa puhtaan funktion tulokset (memoisaatio).
 * @template A, T
 * @param {(arg: A) => T} f
 * @returns {(arg: A) => T}
 */
function muista(f) {
  /** @type {Map<A, T>} */
  const tulokset = new Map();
  return (arg) => {
    if (!tulokset.has(arg)) tulokset.set(arg, f(arg));
    return /** @type {T} */ (tulokset.get(arg));
  };
}

let laskentoja = 0;
const nelio = muista((/** @type {number} */ n) => {
  laskentoja += 1;
  return n * n;
});
console.log(nelio(9), nelio(9), nelio(4), `laskentoja ${laskentoja}`);
// @loppu memo
