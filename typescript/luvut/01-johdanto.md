# Johdanto {.runko-johdanto}

TypeScript on JavaScript, johon on lisätty staattiset tyypit. Jokainen
JavaScript-ohjelma on lähes sellaisenaan TypeScriptiä, ja
TypeScript-ohjelmasta saadaan JavaScriptiä poistamalla tyyppimerkinnät.
Kääntäjä tarkistaa ohjelman ennen ajoa: väärän tyyppinen argumentti,
puuttuva kenttä tai käsittelemätön tapaus löytyy editorissa eikä
tuotannossa.

Tämä tutoriaali on tarkoitettu JavaScriptiä osaavalle (taito
*JavaScript*). Kielen ajonaikaiset asiat, kuten sulkeumat, prototyypit,
tapahtumasilmukka ja lupaukset, opetetaan JavaScript-paketissa.
Tässä keskitytään siihen, mitä TypeScript lisää: tyyppijärjestelmään
suunnittelun välineenä.

## Historia ja käyttö

| Vuosi | Tapahtuma |
|-------|-----------|
| 2012 | Microsoft julkaisee TypeScriptin (Anders Hejlsberg) |
| 2016 | TypeScript 2.0: `strictNullChecks`, erotellut unionit |
| 2018 | Ehdolliset tyypit ja `infer` (2.8) |
| 2022 | `satisfies` (4.9) |
| 2025 | Node.js ajaa `.ts`-tiedostoja poistamalla tyypit |
| 2026 | TypeScript 7: kääntäjä uudelleenkirjoitettu Go-kielellä, noin kymmenen kertaa nopeampi |

TypeScript on nykyään web-kehityksen oletuskieli: React-, Angular- ja
Vue-sovellukset, Node.js-palvelut, VS Code ja suurin osa npm:n
suosituista kirjastoista on kirjoitettu TypeScriptillä tai niillä on
tyyppimäärittelyt.

**Mihin TypeScript ei sovellu:** se ei tee JavaScriptistä nopeampaa,
koska tyypit poistetaan ennen ajoa. Se ei myöskään tarkista
ulkomaailmasta tulevaa dataa ajon aikana; se on ohjelmoijan tehtävä
(luku 9). Laskentaintensiiviseen työhön sopii paremmin käännetty kieli
tai WebAssembly.

## Tyyppien tarkistus ja poisto

TypeScript-koodilla on kaksi elämää:

1. **Tarkistus.** Kääntäjä `tsc` lukee koodin ja raportoi tyyppivirheet.
   Se ei aja mitään.
2. **Ajo.** Ajoympäristö poistaa tyyppimerkinnät ja ajaa jäljelle
   jäävän JavaScriptin. Node.js tekee tämän suoraan (*type stripping*);
   selainsovelluksissa poiston tekee rakennustyökalu, kuten esbuild tai
   Vite.

Vaiheet ovat toisistaan riippumattomat: ohjelma ajetaan, vaikka siinä
olisi tyyppivirheitä. Siksi `tsc --noEmit` kuuluu jokaiseen
CI-putkeen. Tämän paketin esimerkit tarkistetaan tsc:llä tiukassa
tilassa ja ajetaan Nodella:

```
tsc --noEmit -p .        # tarkistus (asetukset tsconfig.json:ssa)
node 01-tilaukset.ts     # ajo: Node poistaa tyypit
```

Koska Node vain poistaa tyypit eikä käännä mitään, koodissa saa käyttää
ainoastaan *poistettavaa syntaksia*. TypeScriptin vanhat piirteet, jotka
tuottavat ajonaikaista koodia (`enum`, `namespace`,
parametriominaisuudet), eivät ole sallittuja. Luku 2 perustelee
linjauksen ja näyttää korvaajat.

## Versiot ja työkalut

Esimerkit on testattu TypeScript 7.0:lla ja Node.js 24:llä (kehityskontti
ja CI). Tarvittavat työkalut:

| Työkalu | Tehtävä |
|---------|---------|
| `tsc` (paketti `typescript`) | Tyyppitarkistus, tarvittaessa käännös JavaScriptiksi ja `.d.ts`-tiedostot |
| `node` 22.18+ tai 24 | Ajaa `.ts`-tiedostot poistamalla tyypit |
| `@types/node` | Noden rajapintojen tyypit (`node:fs`, `process`) |
| Editori (VS Code) | Sama kääntäjä taustalla: virheet, täydennys, uudelleennimeäminen |
| typescript-eslint | Tyyppitietoa hyödyntävät lint-säännöt |

Esimerkkien `package.json` merkitsee tiedostot ES-moduleiksi
(`"type": "module"`), ja `tsconfig.json` sisältää samat asetukset, joilla
testaaja tarkistaa esimerkit. Asetukset käydään läpi luvussa 3.

## Ensimmäinen ohjelma

Ohjelma lukee tilausrivejä, jäsentää ne tyypitetyiksi olioiksi ja laskee
tuotekohtaiset summat. Virheelliset rivit raportoidaan, eikä niitä
yritetä arvata.

```{.typescript tiedosto="esimerkit/01-tilaukset.ts"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/01-tilaukset.syote"}
```

```{.tuloste tiedosto="esimerkit/01-tilaukset.odotettu"}
```

Jo tässä näkyy kolme tämän tutoriaalin teemaa:

- **Data on tyypitetty rakenne.** `Tilausrivi` kertoo, mitä kenttiä
  rivillä on, ja `readonly` estää muuttamasta jäsennettyä riviä.
- **Virhe on arvo.** `Jasennys` on *eroteltu unioni*: joko onnistunut
  rivi tai virheviesti. Kääntäjä ei päästä käyttämään kenttää
  `tulos.rivi` ennen kuin `tulos.ok` on tarkistettu.
- **Reunalla jäsennetään, sisällä luotetaan.** Merkkijono muuttuu
  tyypitetyksi riviksi yhdessä paikassa (`jasenna`), ja muu ohjelma
  käsittelee vain kelvollisia rivejä.

Kääntäjä vaatii myös käsittelemään taulukon purun mahdolliset
`undefined`-arvot (`hinta?.replace`), koska `split` voi palauttaa
vähemmän kenttiä kuin kolme. Tämä on asetuksen
`noUncheckedIndexedAccess` ansiota (luku 3).
