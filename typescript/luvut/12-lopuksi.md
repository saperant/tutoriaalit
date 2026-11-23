# Lopuksi {.runko-kaytannot .runko-lahteet}

## Nyrkkisäännöt

1. **Tiukka tila ja `noUncheckedIndexedAccess`** jokaisessa
   projektissa. `tsc --noEmit` CI:ssä.
2. **Vain poistettava syntaksi.** Ei `enum`ia, `namespace`a eikä
   parametriominaisuuksia; tilalle literaaliunionit, `as const` ja
   tavalliset kentät.
3. **`unknown` rajalle, jäsennys reunalla.** Ulkoinen data muutetaan
   tyypitetyksi yhdessä paikassa, ja tyyppi johdetaan skeemasta.
4. **Ei `as`-pakotusta sovelluskoodissa.** Pakotus kuuluu pieniin,
   testattuihin apufunktioihin heti tarkistuksen jälkeen.
5. **Erotellut unionit tiloille ja virheille.** Mahdottomat tilat eivät
   ole esitettävissä, ja jokainen `switch` tarkistaa kattavuuden.
6. **Yksi totuuden lähde.** Johda tyypit mallista (`Omit`, `Pick`) tai
   datasta (`typeof`, `satisfies`) äläkä ylläpidä rinnakkaisia tyyppejä.
7. **Merkitse rajapinnat, päättele sisältö.** Parametrit ja julkiset
   paluuarvot merkitään, paikalliset muuttujat päätellään.
8. **`readonly` ja kopiointi oletuksena.** Muutokset tehdään uusiin
   olioihin.
9. **Brändi invariantille.** Tarkistettu sähköposti, sentit tai tunniste
   ei sekoitu tavalliseen arvoon.
10. **Tyyppitaso kohtuudella.** Monimutkainen tyyppi kannattaa vain, jos
    se poistaa paljon toistoa.

## Mallit

| Malli | Ongelma | Luku |
|-------|---------|------|
| Eroteltu unioni ja kattavuustarkistus | Tilat, viestit, virhelajit | 4, 6 |
| Tilakoneen siirtymäfunktio | Sallitut tilasiirtymät yhdessä paikassa | 6 |
| `as const` -olio tai -taulukko | `enum`in korvaaja | 6 |
| Geneerinen rajoite (`T extends …`) | Tarkka tyyppi säilyy | 7 |
| Johdetut tyypit (`Omit`, `Partial`) | Uusi, muutos ja esikatselu yhdestä mallista | 7 |
| `satisfies` | Muodon tarkistus ilman levennystä | 8 |
| `Tulos<T, E>` | Odotetut virheet näkyviksi | 9 |
| Jäsennys reunalla, tyyppi skeemasta | Ulkoinen data | 9 |
| Brändätty tyyppi | Samanmuotoiset arvot eivät sekoitu | 9 |
| Tehdasmetodi ja `#`-kentät | Luokan invariantti | 5 |
| Tyyppitesti | Kirjaston tyyppien regressiot | 11 |

## Jatko taitopuussa

- **Web-sovellukset** jatkaa suoraan tästä: TypeScript selaimessa,
  käyttöliittymäkehykset ja HTTP-rajapintojen kutsuminen.
- **Taustapalvelut** käsittelee palvelinpuolen suunnittelua; sen mallit
  (jäsennys reunalla, virheet arvoina) siirtyvät Node-palveluihin.
- **Kääntäjätekniikka** syventää tyyppijärjestelmiä ja tyyppipäättelyä.
- **Rust** ja **Kotlin** tarjoavat samat mallit (summatyypit,
  null-turvallisuus) kielen ytimessä ja ajonaikaisin takuin.

## Lähteet ja lisälukemista

Dokumentaatio:

- TypeScript-käsikirja ja asetusten viite:
  <https://www.typescriptlang.org/docs/>
- tsconfig-viite: <https://www.typescriptlang.org/tsconfig/>
- Node.js: TypeScript-tuki ja node:test:
  <https://nodejs.org/api/typescript.html>,
  <https://nodejs.org/api/test.html>
- typescript-eslint: <https://typescript-eslint.io/>

Kirjat ja oppaat:

- Dan Vanderkam: *Effective TypeScript*, 2. painos. O'Reilly, 2024.
- Boris Cherny: *Programming TypeScript*. O'Reilly, 2019.
- Basarat Ali Syed: *TypeScript Deep Dive* (verkossa, avoin):
  <https://basarat.gitbook.io/typescript/>
- type-challenges, harjoituksia tyyppitason ohjelmointiin:
  <https://github.com/type-challenges/type-challenges>

Kirjastot:

- Zod, Valibot ja ArkType: skeemat ja jäsennys, tyypit skeemasta.
- DefinitelyTyped (`@types/…`): JavaScript-kirjastojen tyypit.
- expect-type ja tsd: tyyppitestit.

Tämän tutoriaalin teksti ja esimerkit on kirjoitettu tätä pakettia
varten. Teos on lisensoitu CC BY-SA 4.0 -lisenssillä.
