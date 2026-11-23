# TypeScript kokeneelle {.runko-kokeneelle}

Tämä luku on tarkoitettu kehittäjälle, joka osaa JavaScriptin ja
jonkin staattisesti tyypitetyn kielen, kuten Javan, C#:n, Kotlinin tai
Rustin. Luku kokoaa TypeScriptin ajattelutavan, vastaavuudet, hinnat ja
sudenkuopat. Kokenut lukija voi lukea tämän luvun ja kunkin luvun
itsearvioinnin ja ohittaa luvut, joiden asiat jo hallitsee.

## Ajattelutapa

**Tyypit ovat vain käännösaikaisia.** Ajossa ei ole tyyppejä,
rajapintoja eikä geneerisiä parametreja. `instanceof Tuote` toimii vain
luokille, ei rajapinnoille eikä tyyppialiaksille. Tyyppimerkintä tai
`as`-pakotus ei tarkista dataa:

```{.typescript tiedosto="esimerkit/02-poisto.ts"}
```

```{.tuloste tiedosto="esimerkit/02-poisto.odotettu"}
```

**Tyypitys on rakenteellista.** Tyyppi on yhteensopiva, jos sillä on
vaaditut kentät oikean tyyppisinä. Nimellä ei ole väliä (vrt. Javan ja
C#:n nimellinen tyypitys). Jos samanmuotoiset arvot eivät saa sekoittua,
käytetään brändättyä tyyppiä (luku 9).

```{.typescript tiedosto="esimerkit/02-rakenteellinen.ts"}
```

```{.tuloste tiedosto="esimerkit/02-rakenteellinen.odotettu"}
```

Muut periaatteet:

- **Tyypit kuvaavat JavaScriptiä, eivät päinvastoin.** Tyyppijärjestelmä
  on suunniteltu kuvaamaan olemassa olevia JavaScript-malleja, kuten
  merkkijonoliteraaleja, olioita kenttien kokoelmina ja funktioita, jotka
  palauttavat eri tyyppejä eri syötteillä. Siksi siinä on unionit,
  leikkaukset, literaalityypit ja tyyppitason ohjelmointi.
- **Tyypit päätellään.** Muuttujien ja paluuarvojen tyypit päätellään
  yleensä itse. Merkintöjä kirjoitetaan rajapintoihin: funktioiden
  parametreihin, julkisiin paluuarvoihin ja datatyyppeihin.
- **Tyyppijärjestelmä on tarkoituksella epätäydellinen** (*unsound*).
  Esimerkiksi `as`, `any`, taulukon kovarianssi ja metodiparametrien
  kaksisuuntaisuus päästävät läpi virheitä, joita kääntäjä ei huomaa.
  Tiukka tila ja muutama käytäntö sulkevat suurimmat aukot.

## Vastaavuudet

| Asia | TypeScript | Java / C# | Rust |
|------|------------|-----------|------|
| Tietue | `type T = { … }` tai `interface` | `record` | `struct` |
| Summatyyppi | eroteltu unioni | `sealed` + `record` | `enum` |
| Luettelotyyppi | literaaliunioni, `as const` | `enum` | `enum` |
| Puuttuva arvo | unioni `undefined`in kanssa, `?.`, `??` | `Optional<T>`, `null` | `Option<T>` |
| Virhe arvona | oma `Tulos<T, E>` -unioni | (poikkeukset) | `Result<T, E>` |
| Geneerisyys | rakenteellinen, poistetaan | poistetaan / säilyy | monomorfisoidaan |
| Rajapinnan toteutus | rakenteellinen, `implements` vapaaehtoinen | nimellinen | `impl Trait` |
| Tyypin tarkistus ajossa | `typeof`, `in`, oma vartija | `instanceof` | `match` |
| Moduli | ES-moduli, `import type` | paketti / nimiavaruus | `mod`, `use` |

## Hinnat

TypeScript ei maksa ajossa mitään: poistettu tyyppi ei tuota koodia.
Kustannukset ovat kehityksen puolella.

| Mikä | Hinta | Vastatoimi |
|------|-------|------------|
| Tyyppitarkistus | Suuressa projektissa sekunteja; TS 7 on nopea | Projektiviittaukset, inkrementaalinen käännös |
| Monimutkaiset tyypit | Hidas tarkistus ja vaikeat virheilmoitukset | Yksinkertaiset tyypit, apuvälinetyypit |
| `any` ja `as` | Virhe siirtyy ajoon, kauas syystä | `unknown` ja ajonaikainen jäsennys |
| Kirjastojen tyypit | Voivat olla vanhentuneita tai liian väljiä | Jäsennä rajapinnassa |
| Ajonaikainen validointi | Koodia, jota tyypit eivät korvaa | Skeemasta johdetut tyypit (luku 9) |

## Vain poistettava syntaksi

Tässä paketissa käytetään asetusta `erasableSyntaxOnly`. Se kieltää
TypeScriptin piirteet, jotka tuottavat ajonaikaista koodia: `enum`,
`namespace`, parametriominaisuudet (`constructor(private x: T)`) ja
`import x = require()`. Perusteet:

1. **Node ja muut ajoympäristöt ajavat TypeScriptiä poistamalla
   tyypit.** Poistettava syntaksi toimii kaikkialla ilman käännösvaihetta.
2. **Koodi on aina JavaScriptiä plus tyypit.** Lukija näkee, mitä ajossa
   tapahtuu, ja JavaScript-osaaminen siirtyy sellaisenaan.
3. **Korvaajat ovat parempia.** Literaaliunioni ja `as const` -olio
   toimivat rakenteellisen tyypityksen kanssa, eikä niissä ole numeeristen
   `enum`-arvojen sudenkuoppia.

```{.typescript tiedosto="esimerkit/02-enum.ei-kaanny.ts"}
```

```
02-enum.ei-kaanny.ts(2,6): error TS1294: This syntax is not allowed
  when 'erasableSyntaxOnly' is enabled.
```

```{.tuloste tiedosto="esimerkit/02-enum.odotettu"}
```

## Muisti ja rinnakkaisuus

Kielipakettien rungossa on luvut muistimallista ja rinnakkaisuudesta.
Ne eivät sovellu tähän pakettiin, koska TypeScript ei muuta
JavaScriptin ajonaikaista mallia: muistinhallinta on roskienkeruuta,
ja rinnakkaisuus on tapahtumasilmukka, lupaukset ja Worker-säikeet.
Nämä opetetaan JavaScript-paketissa. Asynkronisen koodin *tyypit*
(`Promise<T>`, `Awaited`) käsitellään luvussa 4.

## Sudenkuopat

1. **`as` on väite, ei muunnos.** Se ei tarkista eikä muuta mitään
   (luku 9).
2. **`any` leviää.** `any`-arvon kentät ja kutsujen tulokset ovat
   `any`-tyyppisiä. `JSON.parse` ja `fetch`-vastauksen `json()`
   palauttavat `any`n; ota tulos vastaan `unknown`-tyyppisenä.
3. **Indeksointi voi palauttaa `undefined`.** Ilman
   `noUncheckedIndexedAccess`-asetusta `xs[0]` on tyyppiä `T`, vaikka
   taulukko olisi tyhjä.
4. **Ylimääräiset kentät tarkistetaan vain olioliteraaleista.** Muuttujan
   kautta kirjoitusvirhe kentän nimessä menee läpi (luku 5).
5. **`Object.keys` palauttaa `string[]`,** ei `keyof T`, koska olio voi
   sisältää muitakin kenttiä (luku 8).
6. **Tyyppivirhe ei estä ajoa.** Ilman `tsc`-tarkistusta CI:ssä
   virheellinen koodi päätyy tuotantoon.

## Lukuohje

| Tarve | Luvut |
|-------|-------|
| Tiukka tila ja perustyypit | 3 |
| Kavennus, tyyppivartijat, async-tyypit | 4 |
| Datan mallintaminen | 5, 6 |
| Geneerisyys ja tyyppien johtaminen | 7, 8 |
| Ulkoisen datan käsittely turvallisesti | 9 |
| Modulit, `.d.ts`, testaus | 10, 11 |
| Kaikki säännöt koottuna | 12 |
