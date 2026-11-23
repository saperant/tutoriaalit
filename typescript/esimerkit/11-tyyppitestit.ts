// Tyyppitestit: väitteet, jotka tarkistetaan käännöksessä.
type Yhtasuuri<A, B> =
  (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2)
    ? true : false;
function odota<T extends true>(): T | undefined { return undefined; }

type Tila = "auki" | "kiinni";
type Seuraava<T extends Tila> = T extends "auki" ? "kiinni" : "auki";

odota<Yhtasuuri<Seuraava<"auki">, "kiinni">>();
odota<Yhtasuuri<Parameters<(a: string, b?: number) => void>,
  [a: string, b?: number]>>();

// @ts-expect-error: väärä tila ei saa kelvata
const virheellinen: Tila = "raollaan";

// Jos virhettä ei tulekaan, @ts-expect-error itse on käännösvirhe.
console.log("tyyppitestit kääntyivät", virheellinen);
