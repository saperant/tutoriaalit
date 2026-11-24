// Pienin mahdollinen CBOR-jäsennin (RFC 8949) WebAuthnin
// attestaatio-olion ja COSE-avaimen lukemiseen. Tuotannossa käytetään
// valmista WebAuthn-kirjastoa, joka tekee myös kaikki tarkistukset.

export type Cbor = number | Buffer | string | Cbor[] | Map<Cbor, Cbor>;

export function cbor(data: Buffer): { arvo: Cbor; loppu: number } {
  let i = 0;
  function pituus(lisa: number): number {
    if (lisa < 24) return lisa;
    const tavuja = { 24: 1, 25: 2, 26: 4 }[lisa];
    if (tavuja === undefined) throw new Error("ei tuettu CBOR-pituus");
    const n = data.readUIntBE(i, tavuja);
    i += tavuja;
    return n;
  }
  function lue(): Cbor {
    const alku = data[i++]!;
    const tyyppi = alku >> 5;
    const n = pituus(alku & 0x1f);
    switch (tyyppi) {
      case 0: return n;                                    // luku
      case 1: return -1 - n;                               // negatiivinen
      case 2: i += n; return data.subarray(i - n, i);      // tavut
      case 3: i += n; return data.toString("utf8", i - n, i);
      case 4: return Array.from({ length: n }, () => lue());
      case 5: {
        const m = new Map<Cbor, Cbor>();
        for (let k = 0; k < n; k++) m.set(lue(), lue());
        return m;
      }
      default: throw new Error(`ei tuettu CBOR-tyyppi ${tyyppi}`);
    }
  }
  const arvo = lue();
  return { arvo, loppu: i };
}
