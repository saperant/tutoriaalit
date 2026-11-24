# Satunnaistettu vertailutestaus

Tietorakenteen testaaminen käsin valituilla tapauksilla on työlästä ja
epävarmaa. Punamustassa puussa on kymmeniä eri tapauksia sen mukaan,
mitkä solmut ovat punaisia ja kummalla puolella. Kirjoittaja, joka ei
huomaa jotakin tapausta, ei myöskään kirjoita sille testiä.
*Satunnaistettu vertailutesti* (engl. *differential testing*,
*model-based testing*) siirtää tapausten keksimisen koneelle.

1. Valitaan **malli**: hidas ja ilmeisen oikea toteutus samasta
   rajapinnasta, kuten `std::set` joukolle, raaka haku merkkijonohaulle
   tai kaikkien osajoukkojen läpikäynti optimointitehtävälle.
2. Tuotetaan satunnainen operaatiosarja kiinteällä siemenellä ja
   ajetaan se sekä toteutukselle että mallille.
3. Verrataan jokaisen operaation tulosta ja lopuksi koko sisältöä.
4. Tarkistetaan toteutuksen sisäiset **invariantit** jokaisen
   operaation jälkeen.

Kohta 4 on tärkeä. Moni virhe ei näy rajapinnan läpi heti. Väärin
väritetty punamusta puu vastaa hakuihin oikein ja on vain hitaampi.
Invarianttien tarkistus paljastaa virheen heti, kun se syntyy, eikä
vasta silloin, kun se tuhoaa jotain.

## Toistettava satunnaisuus

Testi on hyödyllinen vain, jos epäonnistuminen voidaan toistaa.
Siksi satunnaisluvut tulevat omasta generaattorista, jonka tila ja
algoritmi ovat tiedossa. Standardikirjaston `std::mt19937` on myös
määritelty tarkasti. Sen sijaan `std::uniform_int_distribution` ja
muut jakaumat saavat tuottaa eri toteutuksissa eri luvut, eli GCC:n
ja Clangin kirjastoilla sama siemen voisi tuottaa eri testin. Kaikki
tämän tutoriaalin esimerkit käyttävät seuraavaa otsikkotiedostoa:

```{.cpp tiedosto="esimerkit/testaus.hpp"}
```

`vaadi()` on `assert`-makron korvike, joka ei katoa
`NDEBUG`-käännöksessä. Se kirjoittaa viestin virhetulosteeseen ja
kutsuu `abort()`-funktiota. Sanitoijat ja debuggeri näyttävät silloin
pinon kohdasta, jossa ehto rikkoutui.

## Malli ja toteutus

Esimerkin toteutus on *järjestetty taulukko* joukkona ("flat set").
Haku on binäärihaku, ja lisäys ja poisto siirtävät loppuosaa.
Tällainen rakenne on usein nopeampi kuin puu, kun joukko on pieni tai
sitä enimmäkseen luetaan. Esimerkiksi Boostin `flat_set` ja C++23:n
`std::flat_set` ovat tällaisia.

```{.cpp tiedosto="esimerkit/02-vertailu.cpp" osa="toteutus"}
```

Malliksi käy `std::set`. Testi arpoo jokaiselle operaatiolle tyypin ja
avaimen, ajaa operaation molemmille ja vaatii saman tuloksen. Myös
paluuarvoja verrataan: `lisaa()` kertoo, lisättiinkö alkio, ja
`poista()`, poistettiinko se. Juuri paluuarvoissa on usein virheitä,
joita sisällön vertailu ei huomaa.

```{.cpp tiedosto="esimerkit/02-vertailu.cpp" osa="testi"}
```

```{.cpp tiedosto="esimerkit/02-vertailu.cpp" osa="ajot"}
```

```{.tuloste tiedosto="esimerkit/02-vertailu.odotettu"}
```

Avainavaruuden koko ratkaisee, mitä testi tutkii. Neljällä avaimella
joukko on lähes aina tyhjä tai täynnä, ja lähes jokainen lisäys
osuu olemassa olevaan alkioon. Silloin testataan rajatapauksia.
4096 avaimella joukko kasvaa, mutta poisto osuu harvoin olemassa
olevaan alkioon. Silloin taas testataan siirtoja suuressa taulukossa.
Hyvä testi käyttää useita avainavaruuksia, koska yksi ei kata
molempia.

## Virheen löytäminen ja pienentäminen

Seuraava muunnelma sisältää tyypillisen virheen. `poista()` hakee
alarajan mutta unohtaa tarkistaa, että löydetty alkio on etsitty:

```{.cpp tiedosto="esimerkit/02-pienennys.cpp" osa="poista"}
```

Satunnainen sarja löytää virheen nopeasti, mutta 300 operaation sarja
ei kerro syytä. Siksi operaatiot tallennetaan dataksi, jolloin sarjan
voi ajaa uudelleen ja sitä voi muokata:

```{.cpp tiedosto="esimerkit/02-pienennys.cpp" osa="sarja"}
```

*Pienentäminen* (engl. *shrinking*, *delta debugging*) etsii lyhyen
sarjan, joka epäonnistuu yhä. Ahne versio poistaa ensin suuria
paloja ja sitten yhä pienempiä. Lopuksi se pienentää avaimia, koska
pienet luvut on helpompi lukea kuin satunnaiset:

```{.cpp tiedosto="esimerkit/02-pienennys.cpp" osa="pienennys"}
```

```{.cpp tiedosto="esimerkit/02-pienennys.cpp" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/02-pienennys.odotettu"}
```

Kahden operaation sarja kertoo syyn suoraan: puuttuvan avaimen 0 poisto
poisti avaimen 1. Pienentäminen ei takaa lyhintä mahdollista sarjaa,
mutta käytännössä tulos on lähes aina muutaman operaation mittainen.
Ominaisuuspohjaiset testikirjastot, kuten C++:n RapidCheck, Haskellin
QuickCheck ja Pythonin Hypothesis, tekevät saman automaattisesti.

## Mitä vertailutesti ei löydä

Vertailutesti löytää vain virheet, joihin satunnainen sarja osuu.
Kolme asiaa parantaa osumatarkkuutta:

- **Pienet koot.** Useimmat virheet näkyvät jo muutaman alkion
  rakenteessa. Pienillä rakenteilla saman ajan aikana ehtii läpi
  enemmän erilaisia tilanteita.
- **Painotetut operaatiot.** Jos poistoja on yhtä paljon kuin
  lisäyksiä, rakenne pysyy pienenä. Lisäysten ylipaino kasvattaa sitä.
  Hyvä testi vaihtelee painoja ajosta toiseen.
- **Invariantit.** Invariantti, joka tarkistetaan jokaisen operaation
  jälkeen, havaitsee virheen sen syntyhetkellä.

Testi ei myöskään todista, että rakenne on tehokas. Puu, joka ei
tasapainotu, läpäisee vertailun mallin kanssa. Siksi tämän tutoriaalin
esimerkit mittaavat lisäksi korkeuden tai työmäärän laskureilla.

## Käytännössä

- Kirjoita malli ennen toteutusta. Se määrittelee rajapinnan ja on
  usein valmis muutamassa rivissä. Kirjaston säiliö on yleensä hyvä
  malli, koska sen virheet ovat epätodennäköisiä.
- Vertaa paluuarvoja, älä vain lopputilaa. "Lisättiinkö?" ja
  "löytyikö?" ovat rajapinnan osa.
- Kirjoita invarianttien tarkistus rakenteen jäsenfunktioksi.
  Tuotantokoodissa sitä voi kutsua debug-käännöksissä tai harvoin
  ajonaikana.
- Tallenna epäonnistunut siemen ja pienennetty sarja
  regressiotestiksi. Satunnainen testi löytää virheen, mutta
  kiinteä testi pitää sen korjattuna.
- Ajoaika on rajallinen, joten mieluummin monta pientä ajoa eri
  siemenillä kuin yksi suuri. CI-ympäristössä siemeniä voi kiertää
  päivämäärän mukaan, kunhan siemen tulostetaan virheen yhteydessä.
- Sanitoijat kuuluvat samaan ajoon: vertailu löytää väärät tulokset,
  sanitoija löytää muistivirheet, jotka eivät vielä näy tuloksissa.
- Arvo jokainen satunnaisluku omassa lauseessaan. Funktion
  argumenttien laskentajärjestys ei ole C++:ssa määrätty, joten
  `f(s.alle(n), s.alle(n))` voi antaa GCC:llä ja Clangilla eri
  testin. Tämän tutoriaalin testit löysivät tämän virheen omasta
  esimerkistään, kun tulosteet erosivat kääntäjien välillä.

## Itsearviointi

- Osaat kirjoittaa satunnaistetun vertailutestin, joka vertaa
  toteutusta malliin jokaisen operaation jälkeen.
- Osaat perustella, miksi testin satunnaisuuden on oltava toistettavaa
  ja miksi standardikirjaston jakaumat eivät siihen riitä.
- Osaat valita avainavaruuden ja operaatioiden painot niin, että testi
  kattaa sekä rajatapaukset että suuret rakenteet.
- Osaat pienentää epäonnistuneen operaatiosarjan ja tulkita
  pienennetyn sarjan.
- Osaat kertoa, mitä vertailutesti ei löydä ja miten invariantit ja
  työmäärän mittaus täydentävät sitä.
