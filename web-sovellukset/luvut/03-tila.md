# Tila ja näkymä

Edellisen luvun koodi muutti DOM:ia suoraan: "lisää tämä rivi, poista
tuo nappi". Kun sovellus kasvaa, käskyjä on satoja, ja niiden on
pidettävä näkymä yhtäpitävänä datan kanssa jokaisessa järjestyksessä.
Kehykset ratkaisevat tämän yhdellä ajatuksella: **näkymä on tilan
funktio**. Kehittäjä kertoo, miltä näkymä näyttää annetulla tilalla, ja
kehys hoitaa muutokset DOM:iin.

## Näkymä tilan funktiona

Yksinkertaisin toteutus rakentaa koko näkymän uudelleen joka
muutoksella. Tila on yksi tavallinen olio, jota ei muuteta vaan joka
korvataan uudella (muuttumaton päivitys):

```{.typescript tiedosto="esimerkit/src/03-tila/nakyma.ts" osa="nakyma"}
```

Malli on selkeä: tila on yhdessä paikassa (*single source of truth*),
näkymää ei voi päivittää väärin, ja hakutulokset johdetaan tilasta
eikä niitä tallenneta erikseen. Testi kuitenkin paljastaa ongelman:

```{.typescript tiedosto="esimerkit/src/03-tila/nakyma.test.ts" osa="testi"}
```

Jokainen näppäily luo uuden hakukentän, joten fokus, kursorin paikka,
tekstin valinta, vierityskohta ja ruudunlukijan sijainti katoavat.
Lisäksi koko näkymän uudelleenrakennus on hidas, kun elementtejä on
tuhansia. Ratkaisuja on kaksi, ja nykyiset kehykset käyttävät jompaakumpaa.

**Sovitus** (*reconciliation*): näkymäfunktio tuottaa kevyen kuvauksen
puusta (*virtuaali-DOM*), kehys vertaa sitä edelliseen ja tekee DOM:iin
vain erot. Olemassa oleva hakukenttä säilyy, ja vain sen arvo
päivitetään. Tämä on Reactin malli (luku 4).

**Hienojakoinen reaktiivisuus** (*fine-grained reactivity*): tila
koostuu *signaaleista*, ja jokainen DOM:n kohta tilaa vain ne signaalit,
joita se lukee. Muutos päivittää suoraan oikeat kohdat ilman vertailua.
Tämä on Vuen, SolidJS:n, Sveltin ja Angularin signaalien malli.

## Signaalit

Signaalin periaate mahtuu muutamaan riviin. Signaali muistaa, mitkä
efektit lukivat sen arvon, ja ajaa ne uudelleen arvon muuttuessa:

```{.typescript tiedosto="esimerkit/src/03-tila/signaali.ts" osa="signaali"}
```

Efekti asettaa itsensä käynnissä olevaksi ennen funktion ajoa, joten
jokainen `get`-kutsu kirjaa riippuvuuden automaattisesti. Riippuvuudet
kerätään uudelleen joka ajolla, koska ehtolauseen haara voi lukea eri
signaaleja eri kerroilla:

```{.typescript tiedosto="esimerkit/src/03-tila/signaali.ts" osa="efekti"}
```

```{.typescript tiedosto="esimerkit/src/03-tila/signaali-demo.ts" osa="demo"}
```

```{.tuloste tiedosto="esimerkit/src/03-tila/signaali-demo.odotettu"}
```

```{.dot otsikko="Esimerkin riippuvuudet. Efekti lukee signaalia osallistujia sekä suoraan että johdetun arvon kautta, joten muutos tavoittaa sen kahta reittiä."}
digraph {
  rankdir=LR; nodesep=0.4;
  p [label="paikkoja\n(signaali)", shape=ellipse];
  o [label="osallistujia\n(signaali)", shape=ellipse, style=bold];
  m [label="mahtuu\n(johdettu)"];
  e [label="efekti:\ntulostaa rivin"];
  o -> m [label="1."]; m -> e [label="2. ajo"];
  o -> e [label="3. ajo"];
  p -> m; p -> e;
}
```

Tuloste paljastaa yksinkertaisen toteutuksen heikkouden: rivi `5/4`
tulostuu kahdesti. Muutos `osallistujia`-signaaliin ajaa ensin johdetun
arvon, joka ajaa efektin, ja sitten efektin suoraan. Tätä kutsutaan
*häiriöksi* (*glitch*): välitila näkyy ulos ja työtä tehdään turhaan.
Oikeat toteutukset järjestävät päivitykset riippuvuusjärjestykseen ja
niputtavat ne (*batching*), jolloin jokainen efekti ajetaan kerran
johdonmukaisella tilalla. Niiden lisäksi ne käsittelevät syklit ja
siivoavat efektit, joita kukaan ei enää tarvitse. Tämän vuoksi
reaktiivisuus otetaan kirjastosta eikä tehdä itse.

## Käytännössä

- **Yksi totuuden lähde.** Jokainen tieto on tallessa yhdessä paikassa.
  Kaikki, mikä voidaan laskea tilasta (suodatettu lista, summa,
  "mahtuuko"), johdetaan eikä tallenneta. Tallennettu johdettu tieto
  joutuu ennen pitkää ristiriitaan lähteensä kanssa.
- **Muuttumattomat päivitykset.** Uusi tila luodaan levittämällä
  (`{ ...tila, haku }`) eikä vanhaa muuteta. Muutoksen huomaa
  viitevertailulla (`!==`), mihin sekä React että useimmat
  tilakirjastot nojaavat.
- **Tilan muodot.** *Paikallinen tila* (kentän arvo, avattu valikko)
  kuuluu komponentille, *jaettu tila* (kirjautunut käyttäjä) yhteiselle
  esivanhemmalle tai kontekstille, *palvelimen tila* (tilat, varaukset)
  välimuistiin, joka tietää datan iän (luku 7), ja *URL-tila* (haku,
  valittu tila) osoitteeseen (luku 8). Suurin osa "tilanhallinnan"
  ongelmista johtuu siitä, että nämä sekoitetaan.
- **Hinnat.** Sovitus maksaa näkymäfunktion ajon ja vertailun joka
  muutoksella, mutta malli on yksinkertainen. Signaalit maksavat
  riippuvuuksien kirjanpidon muistissa, mutta päivitys on suora.
  Molemmat ovat tavalliselle sovellukselle riittävän nopeita; ero näkyy
  vasta tuhansien rivien taulukoissa ja animaatioissa.

## Itsearviointi

- Osaat selittää, miksi näkymä kannattaa kuvata tilan funktiona ja
  miksi johdettua tietoa ei tallenneta.
- Osaat kertoa, miksi koko näkymän uudelleenrakennus hävittää fokuksen,
  ja kuvata sovituksen ja signaalien erot.
- Osaat toteuttaa signaalin, johdetun arvon ja efektin periaatteen
  tasolla ja selittää häiriön ja niputuksen.
- Osaat luokitella sovelluksen tilan paikalliseen, jaettuun,
  palvelimen ja URL-tilaan.
