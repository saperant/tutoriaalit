// Odotettavissa olevat virheet arvoina: Tulos<T, E>.
type Tulos<T, E> = { ok: true; arvo: T } | { ok: false; virhe: E };

const ok = <T>(arvo: T): Tulos<T, never> => ({ ok: true, arvo });
const virhe = <E>(v: E): Tulos<never, E> => ({ ok: false, virhe: v });

type Varausvirhe =
  | { laji: "loppu"; tuote: string }
  | { laji: "liian-iso"; enintaan: number };

const saldot = new Map([["omena", 12], ["leipä", 0]]);

function varaa(tuote: string, maara: number): Tulos<number, Varausvirhe> {
  const saldo = saldot.get(tuote) ?? 0;
  if (saldo === 0) return virhe({ laji: "loppu", tuote });
  if (maara > saldo) return virhe({ laji: "liian-iso", enintaan: saldo });
  saldot.set(tuote, saldo - maara);
  return ok(saldo - maara);
}

const pyynnot = [["omena", 5], ["omena", 10], ["leipä", 1]] as const;
for (const [tuote, maara] of pyynnot) {
  const t = varaa(tuote, maara);
  if (t.ok) {
    console.log(`${tuote}: varattu ${maara}, jäljellä ${t.arvo}`);
    continue;
  }
  switch (t.virhe.laji) { // kutsujan on käsiteltävä jokainen laji
    case "loppu": console.log(`${t.virhe.tuote} on loppu`); break;
    case "liian-iso": console.log(`enintään ${t.virhe.enintaan}`); break;
  }
}
