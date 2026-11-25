# JavaScript kokeneelle {.runko-kokeneelle}

Tämä luku on tarkoitettu kehittäjälle, joka osaa Pythonia, Javaa, C#:a
tai C++:aa ja haluaa päästä JavaScriptissa nopeasti tuottavaksi.

## Ajattelutapa

- **Dynaaminen tyypitys, olioita kaikkialla.** Arvoilla on tyyppi,
  muuttujilla ei. Olio on avain–arvo-kokoelma, jonka kenttiä voi lisätä
  ja poistaa. Luokat ovat syntaksia prototyyppiketjun päällä (luku 7).
- **Funktiot ovat arvoja.** Sulkeumat, takaisinkutsut ja funktioita
  palauttavat funktiot ovat arkea. Moni malli, joka Javassa vaatii
  luokan (strategia, tehdas, komento), on JavaScriptissa funktio.
- **Yksi säie ja tapahtumasilmukka.** JavaScript-koodia ajetaan
  kerrallaan yhdessä säikeessä. I/O ei tukkeudu, vaan tulos saapuu
  myöhemmin lupauksena (`Promise`). Lukkoja ei tarvita, koska vuoro
  vaihtuu vain `await`-kohdissa, mutta pitkä laskenta pysäyttää kaiken
  (luku 10).
- **Ympäristö ratkaisee rajapinnat.** Kieli on pieni; tiedostot, verkko
  ja ajastimet tulevat selaimelta tai Nodelta.
- **Taaksepäin yhteensopivuus on ehdoton.** Kielestä ei poisteta mitään.
  Huonot osat (`var`, `==`, `arguments`, `with`) jätetään käyttämättä,
  ja tiukka tila (aina päällä ES-moduleissa) poistaa pahimmat.

## Tyypit tarkistetaan JSDocilla

Tämä tutoriaali kirjoittaa tyypit JSDoc-kommentteihin ja tarkistaa ne
TypeScript-kääntäjällä (`tsc`, `checkJs` ja tiukka tila `strict`). Koodi
pysyy tavallisena JavaScriptina eikä vaadi käännösvaihetta, mutta
tarkistin löytää kirjoitusvirheet, puuttuvat tarkistukset ja väärät
argumentit ennen ajoa. Sama tapa on käytössä esimerkiksi webpackin ja
Svelten lähdekoodissa. Suuremmissa sovelluksissa siirrytään usein
TypeScriptiin, jossa tyypit kirjoitetaan koodiin (taito *TypeScript*).

```{.javascript tiedosto="esimerkit/02-tarkistus.ei-kaanny.js"}
```

```text
02-tarkistus.ei-kaanny.js(11,22): error TS2551: Property 'mara' does
not exist on type 'Tilausrivi'. Did you mean 'maara'?
```

Ilman tarkistinta virheellinen rivi lisäisi summaan `undefined`-arvon,
ja tulos olisi `NaN`. Tämän kirjan `.ei-kaanny`-esimerkeissä virheellinen
rivi on merkitty kommentilla `@virhe`. Testit varmistavat, että
tiedosto ei läpäise tyyppitarkistusta sellaisenaan mutta läpäisee, kun
merkityt rivit poistetaan.

Tarkistus otetaan käyttöön koko projektissa tiedostolla
`tsconfig.json`:

```{.json tiedosto="esimerkit/tsconfig.json"}
```

`checkJs` tarkistaa `.js`-tiedostot, `strict` ottaa käyttöön tiukat
tarkistukset (`null` ja `undefined` erikseen, ei implisiittistä `any`-
tyyppiä, `unknown` catch-muuttujissa), ja `noEmit` jättää tiedostot
ennalleen. Yksittäisen tiedoston voi ottaa mukaan kommentilla
`// @ts-check` ilman asetustiedostoa.

Tyyppi kirjoitetaan `/** … */`-kommenttiin määrittelyn yläpuolelle.
Esimerkeissä käytetyt merkinnät:

| Merkintä | Tarkoitus |
|----------|-----------|
| `@param {string} nimi`, `@returns {number}` | funktion tyyppi |
| `@param {number} [raja]` | valinnainen parametri |
| `@type {Map<string, number>}` | muuttujan tai kentän tyyppi |
| `@typedef {{ x: number }} Piste` | uusi tyyppinimi |
| `@template T` | geneerinen tyyppiparametri |
| `@import { Tyyppi } from "./m.js"` | tyypin tuonti |
| `/** @type {T} */ (lauseke)` | tyyppimuunnos (cast) |
| `// @ts-expect-error: syy` | tarkoituksellinen virhe kuitataan |

Paluutyyppi jätetään usein pois, koska tarkistin päättelee sen. Samat
kommentit toimivat myös dokumentaationa (luku 11).

## Vastaavuudet

| Asia | Python | Java | JavaScript |
|---------------|---------------|---------------|---------------|
| Dynaaminen taulukko | `list` | `ArrayList` | `Array` |
| Sanakirja | `dict` | `HashMap` | `Map` (tai olio) |
| Joukko | `set` | `HashSet` | `Set` |
| Tietue | `dataclass` | `record` | olioliteraali, `@typedef` |
| Luokka | `class` | `class` | `class` (prototyypit) |
| Yksityinen kenttä | `_nimi` | `private` | `#nimi` |
| Lambda | `lambda x: x` | `x -> x` | `(x) => x` |
| Puuttuva arvo | `None` | `null` | `undefined`, `null` |
| Poikkeus | `raise` | `throw` | `throw` (mikä tahansa arvo) |
| Siivous | `with` | try-with-resources | `try`–`finally`, `using` |
| Asynkronisuus | `asyncio` | `CompletableFuture` | `Promise`, `async`/`await` |
| Rinnakkaisuus | `multiprocessing` | säikeet | Worker-säikeet |
| Generaattori | `yield` | – | `function*`, `yield` |
| Paketit | pip, PyPI | Maven | npm |
| Testit | pytest | JUnit | `node:test` |

Esimerkki näyttää purkamisen, levityksen, kokoelmat ja asynkronisen
kutsun:

```{.javascript tiedosto="esimerkit/02-vastaavuudet.js" osa="tietue"}
```

```{.javascript tiedosto="esimerkit/02-vastaavuudet.js" osa="kokoelmat"}
```

```{.javascript tiedosto="esimerkit/02-vastaavuudet.js" osa="async"}
```

```{.tuloste tiedosto="esimerkit/02-vastaavuudet.odotettu"}
```

`Promise.all` käynnistää kolme hakua samanaikaisesti ja odottaa kaikki.
Silmukka, jossa on `await`, tekisi ne peräkkäin.

## Hinnat

Mikä JavaScriptissa (V8) on halpaa ja mikä kallista:

| Halpaa | Kallista |
|--------|----------|
| funktiokutsu, sulkeuma, olioliteraali | kentän poisto `delete`, olion muodon vaihtelu |
| samanmuotoiset oliot (piilotetut luokat) | samassa kohdassa monta eri muotoista oliota |
| lyhytikäiset oliot (nuoren polven roskienkeruu) | suuret, pitkäikäiset rakenteet ja vuodot |
| `Map` ja `Set` suurillekin kokoelmille | taulukon reiät, `arguments`, `eval` |
| poikkeus, jota ei heitetä | `JSON.parse` ja `structuredClone` suurille datoille |
| `await` I/O:lle | raskas synkroninen laskenta: tukkii tapahtumasilmukan |

Moottori kääntää usein ajetun koodin konekieleksi (JIT) olettaen, että
tyypit ja olioiden muodot pysyvät samoina. Kun oletus pettää, koodi
palaa hitaampaan tulkkiin. Siksi tasainen, ennustettava koodi on
nopeaa (luku 5).

## Sudenkuopat

- **`==` muuntaa tyyppejä**: `0 == ""` on tosi. Käytä aina `===`.
- **`this` riippuu kutsutavasta**, ei määrittelypaikasta (esimerkki
  alla).
- **`||` hylkää kaikki epätodet arvot** (`0`, `""`, `false`). Oletusarvo
  annetaan `??`-operaattorilla.
- **Luvut ovat liukulukuja**: `0.1 + 0.2 !== 0.3`. Rahat lasketaan
  kokonaislukuina sentteinä.
- **`sort()` lajittelee merkkijonoina**: `[10, 9, 1].sort()` antaa
  `[1, 10, 9]`. Anna aina vertailufunktio.
- **Unohtunut `await`** palauttaa lupauksen arvon sijaan, ja
  käsittelemätön hylkäys kaataa Node-prosessin.
- **Oliot ja taulukot välitetään viitteinä**: `const` estää vain
  uudelleensijoituksen, ei muutoksia.
- **Merkkijonon `length` laskee UTF-16-yksiköitä**, ei merkkejä.

Irrotettu metodi menettää olionsa, koska `this` määräytyy kutsuhetkellä:

```{.javascript tiedosto="esimerkit/02-this.kaatuu.js"}
```

```text
TypeError: Cannot read properties of undefined (reading 'arvo')
```

Tyyppitarkistin ei huomaa virhettä. Korjaus on nuolifunktio
(`() => laskuri.kasvata()`) tai sidottu metodi `bind` (luku 4).

## Lukuohje kokeneelle

Lue ensin luvut 3 (yhtäsuuruus ja puuttuvat arvot), 4 (`this` ja
sulkeumat) ja 10 (tapahtumasilmukka), koska ne poikkeavat eniten muista
kielistä. Muista luvuista riittää itsearvioinnin läpikäynti ja
pikaopas. Luku 12 kokoaa mallit ja nyrkkisäännöt.
