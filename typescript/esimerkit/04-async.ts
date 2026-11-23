// Asynkronisen koodin tyypit: Promise<T>, Promise.all ja Awaited.
import { setTimeout as odota } from "node:timers/promises";

type Varasto = { tuote: string; saldo: number };

async function haeSaldo(tuote: string): Promise<Varasto> {
  await odota(5); // simuloitu verkkokutsu
  if (tuote === "") throw new Error("tyhjä tuotenimi");
  return { tuote, saldo: tuote.length * 10 };
}

async function haeHinta(tuote: string): Promise<number> {
  await odota(1);
  return tuote === "omena" ? 0.45 : 2.9;
}

// Promise.all säilyttää paikkakohtaiset tyypit: [Varasto, number].
const [saldo, hinta] = await Promise.all([haeSaldo("omena"),
  haeHinta("omena")]);
console.log(saldo.saldo, hinta);

type Tulos = Awaited<ReturnType<typeof haeSaldo>>; // Varasto
const tulokset = await Promise.allSettled(["leipä", ""].map(haeSaldo));
for (const t of tulokset) {
  if (t.status === "fulfilled") {
    const v: Tulos = t.value;
    console.log("ok", v.tuote, v.saldo);
  } else {
    // Hylkäyksen syy on any: käsitellään kuin unknown.
    const syy: unknown = t.reason;
    console.log("virhe", syy instanceof Error ? syy.message : syy);
  }
}
