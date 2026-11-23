# Funktiot, kavennus ja asynkronisuus {.runko-ohjaus}

Ohjausrakenteet ovat samat kuin JavaScriptissä. TypeScript lisää niihin
*kavennuksen* (*narrowing*): kääntäjä seuraa ohjausvuota ja tietää
jokaisessa haarassa, mitä tyyppejä muuttuja voi vielä olla.

## Kavennus

```{.typescript tiedosto="esimerkit/04-kavennus.ts"}
```

```{.tuloste tiedosto="esimerkit/04-kavennus.odotettu"}
```

Kavennuksen keinot:

| Keino | Kaventaa |
|-------|----------|
| `typeof x === "string"` | Primitiivit ja funktiot |
| `x instanceof Date` | Luokat (ei rajapintoja eikä tyyppialiaksia) |
| `"viite" in x` | Olioiden unionit kentän olemassaolon perusteella |
| `x.laji === "ympyra"` | Erotellut unionit (luku 6) |
| `x == null`, `x !== undefined` | Puuttuvat arvot |
| `Array.isArray(x)` | Taulukot |
| Oma vartija `x is T` | Mikä tahansa ehto |

Totuusarvokavennus (`if (x)`) poistaa `undefined`in mutta myös arvot
`0`, `""` ja `NaN`. Esimerkin `alennusVaarin(0)` tulostaa "ei alennusta",
vaikka nollan prosentin alennus on annettu. Kun `0` tai tyhjä merkkijono
on kelvollinen arvo, vertaa suoraan `undefined`iin.

## Tyyppivartijat ja varmistusfunktiot

Kun kääntäjä ei osaa kaventaa itse, kavennuksen voi kirjoittaa
funktioksi. Paluutyyppi `x is T` kertoo, että tosi tulos takaa tyypin;
`asserts ehto` kertoo, että funktio palaa vain, jos ehto on tosi.

```{.typescript tiedosto="esimerkit/04-vartijat.ts"}
```

```{.tuloste tiedosto="esimerkit/04-vartijat.odotettu"}
```

Vartija on lupaus, jota kääntäjä ei tarkista: jos `onTuote` palauttaa
`true` väärälle arvolle, virhe siirtyy ajoon. Vartija kirjoitetaan siksi
huolellisesti ja testataan, tai se johdetaan skeemasta (luku 9).
TypeScript 5.5:stä alkaen yksinkertaisten suodattimien vartija
päätellään itse (`hinnat: number[]`).

## Kattavuustarkistus

Kun `switch` käsittelee unionin kaikki vaihtoehdot, `default`-haarassa
muuttujan tyyppi on `never`. Antamalla sen funktiolle, joka hyväksyy vain
`never`in, käsittelemätön uusi vaihtoehto muuttuu käännösvirheeksi:

```{.typescript tiedosto="esimerkit/04-kattavuus.ei-kaanny.ts"}
```

```
04-kattavuus.ei-kaanny.ts(15,33): error TS2345: Argument of type
  '{ laji: "kolmio"; kanta: number; korkeus: number; }' is not
  assignable to parameter of type 'never'.
```

```{.tuloste tiedosto="esimerkit/04-kattavuus.odotettu"}
```

Virhe osoittaa täsmälleen paikan, joka on päivitettävä. Ilman
tarkistusta uusi muoto palauttaisi hiljaa `undefined`in. `eiKasitelty`
heittää lisäksi poikkeuksen ajossa, jos data ei vastaa tyyppiä.

## Funktioiden tyypit

```{.typescript tiedosto="esimerkit/04-funktiot.ts"}
```

```{.tuloste tiedosto="esimerkit/04-funktiot.odotettu"}
```

- **Funktiotyyppi** `(euroa: number) => string` kuvaa takaisinkutsut ja
  strategiat. Nuolifunktion parametrien tyypit päätellään kontekstista.
- **Oletusparametri** (`alv = 0.255`) päättelee tyypin oletuksesta ja
  tekee parametrista valinnaisen.
- **Ylikuormitus** antaa eri syötteille eri paluutyypin. Toteutuksen
  allekirjoitus ei näy kutsujalle. Usein unioni tai geneerinen funktio
  (luku 7) on yksinkertaisempi.
- **Jäännösparametri** `...osat: unknown[]` ottaa vastaan vaihtelevan
  määrän argumentteja.

## Asynkronisen koodin tyypit

Async-funktio palauttaa aina `Promise<T>`-tyypin. `Promise.all`
säilyttää paikkakohtaiset tyypit, ja `Awaited<T>` purkaa lupauksen
tyypin:

```{.typescript tiedosto="esimerkit/04-async.ts"}
```

```{.tuloste tiedosto="esimerkit/04-async.odotettu"}
```

Lupauksen hylkäyksen syy on tyypiltään `any`, koska `throw` voi heittää
mitä tahansa. Käsittele se kuin `unknown`. Unohtunut `await` on yleinen
virhe: `if (haeSaldo(x))` on aina tosi, koska lupaus on olio.
typescript-eslintin säännöt `no-floating-promises` ja
`no-misused-promises` löytävät nämä.

## Käytännössä

- **Anna kääntäjän kaventaa.** Kirjoita ehdot niin, että kavennus
  onnistuu (`in`, erotin, `typeof`), äläkä pakota tyyppiä `as`illa.
- **Kattavuustarkistus jokaiseen unionin `switch`iin.** Se muuttaa
  "unohdin päivittää tämän kohdan" -virheet käännösvirheiksi. Saman
  tekee typescript-eslintin sääntö `switch-exhaustiveness-check`.
- **Totuusarvokavennus vain olioille.** Luvuille ja merkkijonoille
  vertaa `undefined`iin tai käytä `??`-operaattoria, joka ohittaa vain
  `null`in ja `undefined`in, toisin kuin `||`.
- **Vartijat ovat kriittistä koodia.** Ne ovat paikka, jossa kääntäjä
  luottaa ohjelmoijaan; testaa ne tai johda ne skeemasta.
- **Julkisille funktioille paluutyyppi.** Se pitää muutokset
  paikallisina ja nopeuttaa tarkistusta suurissa projekteissa.

## Itsearviointi

- Osaat kaventaa unionin `typeof`-, `in`-, `instanceof`- ja
  erotinvertailuilla ja tunnet totuusarvokavennuksen sudenkuopat.
- Osaat kirjoittaa tyyppivartijan (`x is T`) ja varmistusfunktion
  (`asserts`) ja kertoa niiden riskit.
- Osaat tehdä kattavuustarkistuksen `never`-tyypillä.
- Osaat tyypittää async-funktiot, `Promise.all`-yhdistelmät ja
  hylkäyksen käsittelyn.
