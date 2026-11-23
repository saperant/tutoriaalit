// Luokat: yksityiset kentät (#), readonly, implements ja tehdasmetodi.
interface Tili {
  readonly numero: string;
  saldo(): number;
  pane(sentit: number): void;
}

class Pankkitili implements Tili {
  readonly numero: string;
  #saldo = 0; // aidosti yksityinen myös ajossa
  #tapahtumat: number[] = [];

  private constructor(numero: string) { // vain tehdasmetodin kautta
    this.numero = numero;
  }

  static avaa(numero: string): Pankkitili {
    if (!/^FI\d{16}$/.test(numero)) {
      throw new RangeError(`virheellinen tilinumero ${numero}`);
    }
    return new Pankkitili(numero);
  }

  saldo(): number { return this.#saldo; }

  pane(sentit: number): void {
    if (!Number.isInteger(sentit) || sentit <= 0) {
      throw new RangeError("talletuksen on oltava positiivinen");
    }
    this.#saldo += sentit;
    this.#tapahtumat.push(sentit);
  }

  get tapahtumia(): number { return this.#tapahtumat.length; }
}

const tili = Pankkitili.avaa("FI2112345600000785");
tili.pane(12_50);
tili.pane(7_25);
console.log(tili.numero, tili.saldo(), tili.tapahtumia);
try {
  Pankkitili.avaa("12345");
} catch (e) {
  console.log(e instanceof RangeError ? e.message : e);
}
// Rakenteellisesti mikä tahansa samanmuotoinen olio kelpaa Tiliksi:
const vale: Tili = { numero: "x", saldo: () => 0, pane: () => {} };
console.log(vale.saldo());
