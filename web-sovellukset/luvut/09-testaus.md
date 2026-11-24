# Testaus

Sovelluksen testit on kirjoitettu lukujen yhteydessä. Tämä luku kokoaa
ne strategiaksi: mitä testataan millä tasolla, ja miten testit pysyvät
nopeina ja luotettavina.

## Testitasot

| Taso | Työkalu | Testaa | Nopeus |
|------|---------|--------|--------|
| yksikkö | Vitest | puhtaat funktiot: reducer, validointi, jäsennys | ms |
| komponentti | Vitest, Testing Library, happy-dom | komponentti tai hook käyttäjän näkökulmasta | kymmeniä ms |
| integraatio | Vitest, oikea palvelin | asiakas ja rajapinta yhdessä | satoja ms |
| päästä päähän | Playwright, Chromium | koko sovellus oikeassa selaimessa | sekunteja |

Klassinen *testipyramidi* suosittelee eniten yksikkötestejä.
Käyttöliittymissä painopiste on usein komponentti- ja integraatiotesteissä
(*testing trophy*), koska ne vastaavat parhaiten kysymykseen "toimiiko
tämä käyttäjälle", mutta ovat silti nopeita. Päästä päähän -testejä on
vähän: ne kattavat tärkeimmät polut, kuten varauksen tekemisen.

Vitest käyttää samaa asetustiedostoa kuin Vite, joten testit kääntyvät
samoin kuin sovellus:

```{.typescript tiedosto="esimerkit/vite.config.ts"}
```

## Komponenttitestit

Hyvä komponenttitesti toimii kuten käyttäjä: löytää elementin roolin ja
nimen perusteella, kirjoittaa ja klikkaa `user-event`-kirjastolla ja
tarkistaa näkyvän tuloksen. Se ei tarkista komponentin sisäistä tilaa,
propsien välitystä tai CSS-luokkia, joten rakennetta voi muuttaa
rikkomatta testejä.

Testing Libraryn hakujen suositusjärjestys on `getByRole`,
`getByLabelText`, `getByText` ja vasta viimeisenä `getByTestId`.
Kyselyn muoto kertoo odotuksen: `getBy` heittää, jos elementtiä ei ole,
`queryBy` palauttaa `null` (poissaolon tarkistus), ja `findBy` odottaa
asynkronista ilmestymistä. Esimerkkejä on luvuissa 4, 5 ja 7.

Hookeja testataan `renderHook`-funktiolla (luvut 6 ja 7), ja aikaa
hallitaan valeajastimilla. Asynkronisten lupausten järjestystä
hallitaan lupauksilla, jotka testi ratkaisee itse (luku 7). Näin
kilpatilanne, joka tuotannossa tapahtuu kerran sadasta, toistuu testissä
joka kerta.

## Päästä päähän Playwrightilla

Playwright ohjaa oikeaa selainta. Testit ajetaan tuotantokäännöstä
vastaan, joten ne kattavat myös käännöksen, koodin pilkkomisen ja
tietoturvaotsakkeet (luku 10):

```{.typescript tiedosto="esimerkit/playwright.config.ts" osa="asetukset"}
```

Rajapinta mokataan `page.route`-kutsulla. Testi päättää vastaukset,
joten se on toistettava eikä tarvitse palvelinta tai tietokantaa.
Mokki tallentaa lähetetyt varaukset, jotta testi voi tarkistaa myös
pyynnön sisällön:

```{.typescript tiedosto="esimerkit/e2e/api.ts" osa="mokki"}
```

```{.typescript tiedosto="esimerkit/e2e/varaus.spec.ts" osa="varaus"}
```

Playwrightin lokaattorit (`getByRole`, `getByLabel`) ovat samat kuin
Testing Libraryssä, ja `expect`-tarkistukset odottavat automaattisesti,
kunnes ehto täyttyy tai aika loppuu. Siksi testeissä ei ole
`sleep`-kutsuja, jotka olisivat joko hitaita tai epäluotettavia.
Virhepolut testataan samalla tavalla:

```{.typescript tiedosto="esimerkit/e2e/virheet.spec.ts" osa="virheet"}
```

## Käytännössä

- **Testaa käyttäytymistä, ei toteutusta.** Testi kertoo, mitä käyttäjä
  tekee ja näkee. Jos refaktorointi rikkoo testin ilman
  toiminnallista muutosta, testi on liian lähellä toteutusta.
- **Roolihaku on myös saavutettavuustesti.** Jos elementtiä ei löydy
  roolilla ja nimellä, se on todennäköisesti saavutettavuusvirhe.
  Automaattiseen tarkistukseen lisätään axe-core (`@axe-core/playwright`).
- **Mokkaa verkko, ei omaa koodia.** `page.route` ja valefetch
  korvaavat verkon; komponentit ja hookit testataan oikeina. Laajempaan
  mokkaukseen sekä testeissä että kehityksessä sopii MSW (*Mock
  Service Worker*).
- **Ei odotusaikoja.** Valeajastimet, hallitut lupaukset ja Playwrightin
  automaattinen odotus. Satunnaisesti epäonnistuva (*flaky*) testi
  korjataan heti tai poistetaan; muuten kukaan ei luota testeihin.
- **Hinnat.** Komponenttitesti happy-domissa vie kymmeniä millisekunteja,
  päästä päähän -testi sekunteja. Satoja komponenttitestejä ja
  kymmenkunta päästä päähän -testiä on tavallinen tasapaino.
- **CI ajaa kaiken.** Tyypit, testit, käännös ja päästä päähän -testit
  jokaisessa muutoksessa, kuten tämän tutoriaalin esimerkeissä.

## Itsearviointi

- Osaat valita testitason tarkistettavalle asialle ja perustella
  valinnan.
- Osaat kirjoittaa komponenttitestin, joka käyttää rooleja ja nimiä ja
  `user-event`-kirjastoa.
- Osaat kirjoittaa Playwright-testin, joka mokkaa rajapinnan
  `page.route`-kutsulla ja tarkistaa lähetetyn pyynnön.
- Osaat tehdä asynkronisista testeistä deterministisiä valeajastimilla
  ja hallituilla lupauksilla.
