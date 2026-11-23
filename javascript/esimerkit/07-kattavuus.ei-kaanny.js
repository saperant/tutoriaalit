/**
 * @typedef {{ tila: "odottaa" }
 *   | { tila: "maksettu", summa: number }
 *   | { tila: "palautettu", syy: string } // @virhe
 * } Tilaus
 */

/**
 * @param {Tilaus} t
 * @returns {string}
 */
function kuvaa(t) {
  switch (t.tila) {
    case "odottaa":
      return "odottaa maksua";
    case "maksettu":
      return `maksettu ${t.summa} snt`;
    default: {
      /** @type {never} */
      const muu = t;
      throw new TypeError(`tuntematon tila: ${JSON.stringify(muu)}`);
    }
  }
}

console.log(kuvaa({ tila: "maksettu", summa: 1250 }));
