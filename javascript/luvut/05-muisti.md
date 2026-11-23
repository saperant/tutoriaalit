# Muisti, viitteet ja suorituskyky {.runko-muisti}

JavaScriptin muistinhallinta on automaattista: oliot varataan keosta, ja
roskienkeruu vapauttaa ne, kun niihin ei enää pääse käsiksi. Ohjelmoija
ei vapauta muistia, mutta vastaa siitä, ettei tarpeettomiin olioihin
jää viitteitä.

## Arvot ja viitteet

Primitiivit kopioituvat sijoituksessa, oliot eivät: muuttuja sisältää
viitteen olioon. Kopion tekotapa ratkaisee, mitä jaetaan:

```{.javascript tiedosto="esimerkit/05-viitteet.js" osa="kopiot"}
```

| Tapa | Mitä kopioituu |
|------|----------------|
| `b = a` | ei mitään: sama olio |
| `{ ...a }`, `[...a]`, `Object.assign({}, a)` | ylin taso; sisäoliot jaetaan |
| `structuredClone(a)` | koko rakenne; säilyttää `Date`-, `Map`- ja `Set`-oliot, ei funktioita eikä luokan prototyyppiä |
| `JSON.parse(JSON.stringify(a))` | vanha tapa; kadottaa `Date`-, `Map`- ja `undefined`-arvot |

## Muuttumattomuus

`const` estää vain muuttujan uudelleensijoituksen. Olion jäädyttää
`Object.freeze`, mutta vain ylimmältä tasolta:

```{.javascript tiedosto="esimerkit/05-viitteet.js" osa="jaadytys"}
```

Syvä jäädytys on lyhyt rekursiivinen funktio:

```{.javascript tiedosto="esimerkit/05-viitteet.js" osa="syvajaadytys"}
```

```{.tuloste tiedosto="esimerkit/05-viitteet.odotettu"}
```

Käytännössä muuttumattomuus on enemmän tapa kuin kielen takuu: uusi
tila luodaan levityksellä (`{ ...tila, maara: 3 }`) ja kopioivilla
taulukkometodeilla (`toSorted`, `toReversed`, `with`, `map`,
`filter`), eikä vanhaa muuteta. Reduxin ja Reactin tilanhallinta
perustuu tähän, koska muutos havaitaan vertaamalla viitteitä (`===`).
Tyyppitarkistimelle muuttumattomuuden voi kertoa tyypeillä `Readonly<T>`
ja `readonly T[]`.

## Roskienkeruu ja vuodot

V8:n roskienkeruu on sukupolvipohjainen: uudet oliot varataan nuoreen
sukupolveen, joka kerätään usein ja nopeasti. Useimmat oliot kuolevat
nuorina, joten lyhytikäiset väliaikaisoliot ovat halpoja. Oliot, jotka
selviävät muutamasta keruusta, siirretään vanhaan sukupolveen, jonka
keruu on harvinaisempaa ja kalliimpaa.

Muistivuoto syntyy, kun tarpeettomaan olioon jää viite. Tavallisimmat
syyt palvelimessa:

- rajaton välimuisti tai taulukko modulin tasolla
- tapahtumankuuntelija tai ajastin, jota ei poisteta ja joka kaappaa
  suuren olion sulkeumaansa
- keskeneräiset lupaukset, jotka eivät koskaan täyty.

Välimuistin koko rajataan. `Map` säilyttää lisäysjärjestyksen, joten
LRU-välimuisti on muutaman rivin luokka:

```{.javascript tiedosto="esimerkit/05-lru.js"}
```

```{.tuloste tiedosto="esimerkit/05-lru.odotettu"}
```

`WeakMap` liittää tietoa olioon pitämättä oliota elossa. Avaimen on
oltava olio, eikä kokoelmaa voi käydä läpi, koska sen sisältö riippuu
roskienkeruusta:

```{.javascript tiedosto="esimerkit/05-weakmap.js"}
```

```{.tuloste tiedosto="esimerkit/05-weakmap.odotettu"}
```

`WeakRef` ja `FinalizationRegistry` antavat vielä hienojakoisemman
hallinnan, mutta niiden ajoitus on määrittelemätön, eikä niitä käytetä
ohjelman logiikkaan.

## Piilotetut luokat

V8 antaa jokaiselle oliolle sisäisen muodon (*hidden class*, *map*),
joka kertoo kenttien nimet, järjestyksen ja sijainnit. Samanmuotoisten
olioiden kenttiin pääsee kiinteällä siirtymällä, ja kutsukohdan
välimuisti (*inline cache*) muistaa muodon. Kun samassa kohdassa näkyy
monta muotoa, kohta muuttuu megamorfiseksi ja hidastuu.

Esimerkki käyttää V8:n diagnostiikkafunktioita, jotka eivät ole osa
kieltä:

```{.javascript tiedosto="esimerkit/05-muodot.js" osa="muodot"}
```

```{.tuloste tiedosto="esimerkit/05-muodot.odotettu"}
```

Muoto riippuu kenttien järjestyksestä, ja jälkikäteen lisätty kenttä
luo uuden muodon. `delete` siirtää olion hitaaseen sanakirjatilaan.
Kentän arvon voi asettaa `undefined`-arvoksi, jolloin muoto säilyy.

## Käytännössä

- **Alusta kaikki kentät konstruktorissa samassa järjestyksessä.**
  Luokan kenttämäärittelyt (luku 7) tekevät tämän automaattisesti.
  Valinnainen kenttä alustetaan arvolla `undefined` tai `null`.
- **Älä käytä `delete`-operaattoria kuumissa olioissa.** Jos avaimia
  lisätään ja poistetaan, rakenne on sanakirja, ja oikea tyyppi on
  `Map`.
- **Rajaa välimuistit** (LRU, aikaraja) ja poista tapahtumankuuntelijat
  ja ajastimet, kun niiden omistaja lopettaa (`AbortSignal` auttaa,
  luku 10).
- **Kopioi rajapinnassa, muuta paikallisesti.** Funktio, joka saa olion,
  ei muuta sitä, ellei se ole funktion tarkoitus ja nimessä (`lajittele`
  vs. `lajiteltu`).
- **Mittaa ennen kuin optimoit.** `node --cpu-prof` ja `--heap-prof`
  sekä Chrome DevToolsin muistikuvat (heap snapshot) näyttävät todelliset
  kuumat kohdat ja vuodot (luku 11).
- **Hinta.** Oliot ja sulkeumat ovat halpoja, `structuredClone` ja
  JSON-muunnos kalliita suurille rakenteille. Numerotaulukko, jossa on
  vain kokonaislukuja tai vain liukulukuja ilman reikiä, tallentuu
  tiiviisti; sekatyyppinen tai reikäinen taulukko ei.

## Itsearviointi

- Osaat selittää viitteen ja kopion eron ja valita matalan kopion,
  `structuredClone`-kopion tai jäädytyksen tilanteen mukaan.
- Osaat kertoa, miten JavaScript-ohjelmaan syntyy muistivuoto, ja
  rajata välimuistin koon.
- Osaat käyttää `WeakMap`-kokoelmaa olioon liitettyyn tietoon.
- Osaat kertoa, mitä piilotetut luokat ovat ja miten `delete` ja
  vaihtuva kenttäjärjestys vaikuttavat suorituskykyyn.
