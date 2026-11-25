# Työkalut, testaus ja laatu {.runko-tyokalut}

JavaScriptilla ei ole kääntäjää, joka hylkäisi virheellisen ohjelman
ennen ajoa. Laadun varmistavat tyyppitarkistin, lintteri, muotoilija ja
testit, jotka ajetaan editorissa ja CI:ssä.

## Tyyppitarkistus

Tyyppitarkistus on otettu käyttöön luvussa 2: `tsconfig.json` asettaa
`checkJs`- ja `strict`-asetukset, ja tyypit kirjoitetaan
JSDoc-kommentteihin (merkintöjen taulukko on samassa luvussa).
`npm run tarkista` ajaa tarkistuksen koko projektille, ja editori
näyttää samat virheet kirjoitettaessa. Asetus `target` valitsee myös
standardikirjaston tyypit: uudemman version rajapinnat saa käyttöön
asetuksella `lib` tai tiedostokohtaisesti, kuten luvun 6
iteraattoriesimerkissä.

## JSDoc dokumentaationa

JSDoc-kommentti on ensisijaisesti dokumentaatiota, ja tyypit ovat sen
yksi osa. Kommentin ensimmäinen virke on yhteenveto, jonka editori
näyttää vihjeessä kutsupaikalla. Sen jälkeen kerrotaan se, mitä
tyypistä ei näe: yksiköt, sallitut arvot, sivuvaikutukset ja virheet.

| Merkintä | Tarkoitus |
|----------|-----------|
| ensimmäinen virke | yhteenveto editorin vihjeeseen ja luetteloihin |
| `@param {T} nimi kuvaus` | parametrin merkitys, ei vain tyyppi |
| `@throws {RangeError} milloin` | virheet, jotka kutsujan kannattaa tuntea |
| `@example` | lyhyt käyttöesimerkki |
| `@deprecated käytä funktiota x` | editori yliviivaa vanhentuneen kutsun |
| `{@link Nimi}`, `@see` | viittaus toiseen nimeen tai lähteeseen |

Luvun 9 varastomoduli on dokumentoitu näin. Tehdasfunktio saa
yhteenvedon, tarkennuksen ja esimerkin:

```{.javascript tiedosto="esimerkit/09-varasto/varasto.js" alkaen="Saldo, jonka" asti="export function luoVarasto"}
```

Samassa tiedostossa metodi `kirjaa` kertoo `@throws`-merkinnällä,
milloin se heittää `RangeError`-virheen, ja `tilattavat` viittaa
vakioon merkinnällä `{@link TILAUSRAJA}`.

Tyyppitarkistin pitää tyypit ajan tasalla, mutta ei kuvauksia eikä
`@example`-lohkoja: ne vanhenevat, jos niitä ei lueta katselmoinnissa.
Siksi kommenttiin kirjoitetaan sopimus (mitä funktio lupaa), ei
toteutuksen kertausta. Samoista kommenteista tuotetaan
HTML-dokumentaatio TypeDocilla, joka lukee myös tarkistetun
JavaScriptin, tai vanhemmalla `jsdoc`-työkalulla. Lukijat,
dokumenttityypit ja dokumentaation testaus käsitellään taidossa
*Tekninen dokumentaatio*.

## Lintteri ja muotoilija

ESLint löytää virheet, joita tyyppitarkistin ei näe: käyttämättömät
muuttujat, `==`-vertailut, unohtuneet `await`-sanat (typescript-eslint)
ja tyylin poikkeamat. Prettier muotoilee koodin, jolloin muotoilusta ei
keskustella katselmoinnissa. Molemmat ajetaan editorissa tallennettaessa
ja CI:ssä, ja säännöt versioidaan projektiin (`eslint.config.js`,
`.prettierrc`).

## Testaus: node:test

Node sisältää testikehyksen (`node:test`) ja vertailukirjaston
(`node:assert/strict`), joten pieni projekti ei tarvitse
riippuvuuksia. Vitest ja Jest ovat yleisiä vaihtoehtoja, joiden rajapinta
on lähes sama (`describe`, `it`, `expect`).

Testattava moduli ottaa ulkoisen palvelun parametrina (riippuvuuden
injektio), jolloin testi voi korvata sen:

```{.javascript tiedosto="esimerkit/11-testit/hinnoittelu.js"}
```

```{.javascript tiedosto="esimerkit/11-testit/hinnoittelu.test.js"}
```

- **Taulukkotestit**: tapaukset ovat dataa, ja silmukka luo testin
  jokaiselle. Testin nimi kertoo, mikä tapaus epäonnistui.
- **`mock.fn`** luo funktion, joka kirjaa kutsunsa
  (`mock.callCount()`, `mock.calls`).
- **`mock.timers`** korvaa `Date`- ja ajastinfunktiot, joten aikaan
  sidottu logiikka testataan ilman odottamista. Node 22 merkitsee sen
  vielä kokeelliseksi ja tulostaa siitä varoituksen; Node 24:ssä
  varoitusta ei enää tule.
- **`assert.rejects`** testaa asynkronisen virheen; `assert.throws`
  synkronisen. Toinen argumentti on virheluokka tai säännöllinen
  lauseke.

```text
$ node --test --test-reporter=tap
TAP version 13
# Subtest: hinta
    # Subtest: 1000 snt -> EUR
    ok 1 - 1000 snt -> EUR
...
# tests 6
# pass 6
# fail 0
```

`node --test` etsii testitiedostot (`*.test.js` ja `test`-hakemistot),
ajaa jokaisen omassa prosessissaan ja raportoi tulokset.
`--test-reporter` vaihtaa raportin muodon (esim. `junit` CI:lle), ja
`--experimental-test-coverage` mittaa kattavuuden. Ohjelma, joka käyttää
modulia:

```{.javascript tiedosto="esimerkit/11-testit/main.js"}
```

```{.tuloste tiedosto="esimerkit/11-testit.odotettu"}
```

## Debuggaus ja profilointi

| Komento | Tehtävä |
|---------|---------|
| `node --inspect-brk ohjelma.js` | debuggeri: Chrome `chrome://inspect` tai VS Code |
| `node --watch ohjelma.js` | ajaa uudelleen, kun tiedosto muuttuu |
| `node --cpu-prof ohjelma.js` | CPU-profiili tiedostoon `.cpuprofile` |
| `node --heap-prof`, heap snapshot | muistin käyttö ja vuodot |
| `node --trace-warnings` | varoitusten pinojäljet |
| `NODE_OPTIONS=--enable-source-maps` | pinojäljet alkuperäiseen lähdekoodiin |

`performance.now()` mittaa aikaa mikrosekuntien tarkkuudella, mutta
mikrovertailuja tulkitaan varoen: JIT optimoi koodin vasta
lämpenemisen jälkeen ja voi poistaa koodin, jonka tulosta ei käytetä.
Luotettavampi on profiili todellisesta kuormasta.

## Loki

`console.log` sopii skripteihin. Palvelin kirjoittaa rakenteista lokia
(JSON-rivit, joissa on aika, taso, viesti ja konteksti), jonka
lokijärjestelmä voi hakea ja suodattaa. Tavallisia kirjastoja ovat pino
ja winston. Virhe kirjataan kerran, ylimmällä tasolla, syyketjuineen.

## Käytännössä

- **Dokumentoi julkinen rajapinta, älä toteutusta.** Viety funktio saa
  yhteenvedon ja tiedon virheistä; yksityinen apufunktio selittää
  itsensä nimellään ja tyypeillään.
- **Tyyppitarkistus, lintteri, muotoilija ja testit CI:ssä**, ja samat
  työkalut editorissa, jotta virheet näkyvät heti.
- **Testaa julkista rajapintaa**, ei toteutusta. Ulkoiset palvelut
  (verkko, kello, satunnaisuus) annetaan parametrina, jolloin testit
  ovat nopeita ja deterministisiä.
- **Taulukkotestit** rajatapauksille: tyhjä, nolla, negatiivinen, suuri,
  virheellinen tyyppi.
- **Ei testejä, jotka odottavat oikeaa aikaa.** `mock.timers` tai
  injektoitu kello.
- **Profiili ennen optimointia.** Useimmiten pullonkaula on I/O tai
  algoritmi, ei kielen piirre.
- **Hinta.** Tyyppitarkistus ja lintteri eivät maksa ajon aikana mitään;
  JSDoc-kommentit ovat pelkkiä kommentteja. Paketoija poistaa ne
  selaimeen lähetettävästä koodista.

## Itsearviointi

- Osaat ottaa käyttöön JSDoc-tyyppien tarkistuksen ja kirjoittaa
  tavallisimmat tyyppimerkinnät.
- Osaat dokumentoida funktion rajapinnan JSDoc-kommentilla:
  yhteenveto, parametrien merkitys, virheet ja esimerkki.
- Osaat kirjoittaa testejä `node:test`-kehyksellä: taulukkotestit,
  asynkroniset virheet, mock-funktiot ja ajan korvaamisen.
- Osaat suunnitella modulin testattavaksi riippuvuuden injektiolla.
- Osaat käynnistää debuggerin ja ottaa CPU-profiilin Node-ohjelmasta.
