# Tyypit, tiukka tila ja syöte {.runko-tyypit}

Tyyppi on joukko arvoja, ja kääntäjän tehtävä on tarkistaa, että
jokainen arvo kuuluu siihen joukkoon, jota sen käyttöpaikka odottaa.
Tässä luvussa käydään läpi perustyypit ja niiden päättely,
tyyppihierarkian ääripäät `unknown` ja `never`, tiukan tilan asetukset
sekä syötteen lukeminen, jossa tyypittämätön data ensi kertaa kohtaa
tyypit.

## Perustyypit ja päättely

TypeScriptin perustyypit vastaavat JavaScriptin arvoja: `number`,
`string`, `boolean`, `bigint`, `symbol`, `null` ja `undefined`. Niiden
lisäksi on *literaalityypit*, joiden ainoa arvo on yksi vakio, kuten
`"EUR"` tai `3`. Literaalityypeistä muodostetaan unioneja, jotka rajaavat
arvojoukon tarkasti.

```{.typescript tiedosto="esimerkit/03-perustyypit.ts"}
```

```{.tuloste tiedosto="esimerkit/03-perustyypit.odotettu"}
```

Päättely toimii näin:

- `const`-muuttujan tyyppi on literaali (`kpl: 3`), `let`-muuttujan
  levennetty (`yhteensa: number`), koska arvo voi muuttua.
- Funktion paluutyyppi päätellään rungosta. Julkisen funktion paluutyyppi
  kannattaa silti kirjoittaa: se dokumentoi sopimuksen, ja virhe
  ilmoitetaan funktiossa eikä kutsujan luona.
- Monikko (`[number, number]`) on taulukko, jonka pituus ja paikkojen
  tyypit ovat kiinteät. Nimetyt paikat (`[leveys: number, ...]`)
  näkyvät editorissa dokumentaationa.
- `number` on 64-bittinen liukuluku kuten JavaScriptissä. Rahamäärät
  käsitellään sentteinä kokonaislukuina tai `bigint`inä.

## unknown, any ja never

| Tyyppi | Merkitys | Käyttö |
|--------|----------|--------|
| `unknown` | Mikä tahansa arvo; käyttö vaatii kavennuksen | Ulkoinen data, `catch`, geneeriset säiliöt |
| `any` | Tarkistukset pois päältä | Siirtymävaiheessa, ei uudessa koodissa |
| `never` | Ei yhtään arvoa | Kattavuustarkistus, mahdottomat haarat |
| `void` | Funktio ei palauta käyttökelpoista arvoa | Paluutyyppinä |

```{.dot otsikko="Tyypit joukkoina. Nuoli osoittaa suppeammasta tyypistä laajempaan: arvon voi sijoittaa nuolen suuntaan ilman tarkistusta, vastasuuntaan vain kaventamalla."}
digraph {
  rankdir=BT; ranksep=0.3; node [shape=box, style=rounded];
  never [label="never\n(tyhjä joukko)"];
  eur [label="\"EUR\""]; sek [label="\"SEK\""];
  unioni [label="\"EUR\" | \"SEK\""];
  string [label="string"]; number [label="number"];
  sn [label="string | number"];
  unknown [label="unknown\n(kaikki arvot)"];
  never -> eur; never -> sek; never -> number;
  eur -> unioni; sek -> unioni; unioni -> string;
  string -> sn; number -> sn; sn -> unknown;
}
```

Literaalityyppi on yhden arvon joukko, unioni joukkojen yhdiste,
`unknown` kaikkien arvojen joukko ja `never` tyhjä joukko. `any` ei
ole kuvassa, koska se ei ole joukko vaan kytkin: se kelpaa kaikkialle
ja kaikki kelpaa siihen. Kavennus (luku 4) ja geneeristen tyyppien
rajoitteet `T extends U` (luku 7) ovat liikkumista tässä hierarkiassa.

`unknown` on turvallinen vastine `any`lle. Kumpaankin voi sijoittaa
minkä tahansa arvon, mutta `unknown`-arvolla ei voi tehdä mitään ennen
kuin sen tyyppi on tarkistettu:

```{.typescript tiedosto="esimerkit/03-unknown.ts"}
```

```{.tuloste tiedosto="esimerkit/03-unknown.odotettu"}
```

`any` on vaarallinen, koska se *leviää*: `data.hinta * 2` on taas
`any`, ja kääntäjä hyväksyy kaiken sen jälkeen. Merkkijono `"12"` muuttui
luvuksi 24 ilman yhtään varoitusta.

## Tiukka tila

Asetus `strict` kytkee päälle joukon tarkistuksia, joita ilman
TypeScript on lähinnä dokumentaatiota. Uusi projekti aloitetaan aina
tiukassa tilassa. Tämän paketin asetukset:

```{.javascript tiedosto="esimerkit/tsconfig.json"}
```

| Asetus | Mitä tekee |
|--------|------------|
| `strict` | Mm. `strictNullChecks` (`null` ja `undefined` eivät kuulu muihin tyyppeihin), `noImplicitAny`, `strictFunctionTypes`, `useUnknownInCatchVariables` |
| `noUncheckedIndexedAccess` | Taulukon ja indeksiallekirjoituksen indeksointi palauttaa myös `undefined`in |
| `erasableSyntaxOnly` | Vain poistettavaa syntaksia (luku 2) |
| `verbatimModuleSyntax` | Tyyppituonnit merkitään `import type` -sanoin (luku 10) |
| `allowImportingTsExtensions` | Tuonnit `./x.ts`-päätteellä, kuten Node vaatii |
| `module: nodenext` | Noden moduliresoluutio; `package.json` ratkaisee ESM:n |
| `target: es2024` | Kielitaso ja standardikirjaston tyypit (esim. `Object.groupBy`) |

`noImplicitAny` vaatii merkitsemään parametrien tyypit, kun niitä ei
voi päätellä:

```{.typescript tiedosto="esimerkit/03-implisiittinen.ei-kaanny.ts"}
```

```
03-implisiittinen.ei-kaanny.ts(2,14): error TS7006: Parameter 'hinta'
  implicitly has an 'any' type.
```

`noUncheckedIndexedAccess` ei kuulu `strict`-joukkoon, mutta se on
tärkeimpiä yksittäisiä asetuksia. Se pakottaa huomaamaan tyhjän
taulukon ja puuttuvan avaimen:

```{.typescript tiedosto="esimerkit/03-indeksointi.ei-kaanny.ts"}
```

```
03-indeksointi.ei-kaanny.ts(5,13): error TS18048: 'ensimmainen' is
  possibly 'undefined'.
```

```{.tuloste tiedosto="esimerkit/03-indeksointi.odotettu"}
```

Kun tiedät taulukon olevan epätyhjä, voit käyttää
ei-null-väitettä `xs[0]!`. Se on samanlainen väite kuin `as`, joten
käytä sitä vain, kun ehto on tarkistettu samassa kohdassa.

## Syöte ja muotoilu

Syöte luetaan Noden rajapinnoilla, ja kaikki siitä jäsennetty on aluksi
merkkijonoa. Luvuksi muuttaminen tarkistetaan: `Number("abc")` on
`NaN`, ei virhe. Lukujen ja rahamäärien muotoiluun käytetään
`Intl.NumberFormat`-oliota, joka noudattaa kielialueen sääntöjä
(desimaalipilkku, sitova välilyönti ennen €-merkkiä).

```{.typescript tiedosto="esimerkit/03-syote.ts"}
```

```{.tuloste tiedosto="esimerkit/03-syote.syote"}
```

```{.tuloste tiedosto="esimerkit/03-syote.odotettu"}
```

Ylätason `await` (`for await`) on sallittu ES-moduleissa. Virheet ja
ohitetut rivit kirjoitetaan `console.error`illa virhevirtaan, jotta ne
eivät sekoitu varsinaiseen tulosteeseen.

## Käytännössä

- **Tiukka tila ja `noUncheckedIndexedAccess` aina.** Ne löytävät
  suurimman osan virheistä, joita TypeScriptillä halutaan estää. Vanhaan
  projektiin ne otetaan käyttöön asetus kerrallaan.
- **Merkitse rajapinnat, päättele sisältö.** Parametrit, julkiset
  paluuarvot ja datatyypit merkitään; paikalliset muuttujat jätetään
  päättelyn varaan. Turhat merkinnät (`const n: number = 3`) vain
  leventävät tyyppiä.
- **`unknown` rajalle, ei `any`ä.** `JSON.parse`, `catch` ja
  kolmannen osapuolen data otetaan vastaan `unknown`-tyyppisinä ja
  jäsennetään (luku 9). Jos `any` on pakko käyttää, se rajataan yhteen
  funktioon.
- **Literaaliunionit ennen merkkijonoja.** `"EUR" | "SEK"` on parempi
  kuin `string`, kun arvojoukko on tunnettu: kääntäjä tarkistaa
  kirjoitusasun ja editori täydentää.
- **Raha kokonaislukuina.** `0.1 + 0.2 !== 0.3` koskee myös
  TypeScriptiä.

## Itsearviointi

- Osaat selittää literaalityypit ja `const`- ja `let`-päättelyn eron.
- Osaat valita `unknown`in, `any`n ja `never`in välillä ja perustella
  valinnan.
- Osaat kertoa, mitä `strict` ja `noUncheckedIndexedAccess` tarkistavat,
  ja korjata niiden ilmoittamat virheet ilman `as`-pakotusta.
- Osaat lukea ja jäsentää syötettä ja muotoilla rahamäärät
  `Intl.NumberFormat`illa.
