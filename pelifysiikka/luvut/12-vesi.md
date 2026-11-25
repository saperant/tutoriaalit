# Vesi ja hiukkaset

Neste on fysiikkasimulaation kallein kohde. Tarkka virtauslaskenta
ratkaisee nesteen nopeuden ja paineen jokaisessa tilavuuden pisteessä,
eikä siihen ole pelissä aikaa. Pelit valitsevat siksi mallin sen
mukaan, mitä pelaaja näkee. Useimmiten hän näkee pinnan: lammen, johon
heitetty kivi tekee renkaita, ja veneen, joka keinuu aalloilla. Tässä
luvussa vesi on pelkkä pinta, ja roiskeet tehdään hiukkasilla.

## Pinta korkeuskenttänä

*Korkeuskenttä* tallentaa veden pinnan korkeuden jokaisessa ruudukon
ruudussa. Malli ei tunne veden virtausta pinnan alla, murtuvia aaltoja
eikä roiskeita, mutta se riittää aaltoihin, jotka etenevät, heijastuvat
ja vaimenevat.

```{.cpp tiedosto="esimerkit/yhteinen/vesi.hpp" osa="vesi"}
```

Pinnan liikettä kuvaa aaltoyhtälö: ruudun pystykiihtyvyys on
verrannollinen siihen, kuinka paljon sen naapurit ovat keskimäärin sitä
korkeammalla. Kuoppa nousee ja kumpu laskee, ja häiriö leviää
naapureihin.

```{.cpp tiedosto="esimerkit/yhteinen/vesi.hpp" osa="vesiaskel"}
```

Askel on taas puoli-implisiittinen Euler: ensin nopeudet kaikille
ruuduille vanhoista korkeuksista, sitten korkeudet uusista nopeuksista.
Reunalla naapuriksi otetaan ruutu itse, jolloin aalto heijastuu
seinästä.

```{.cpp tiedosto="esimerkit/12-vesi.cpp" osa="aalto"}
```

```{.tuloste tiedosto="esimerkit/12-vesi.odotettu" rivit="1-2"}
```

Kaksi tarkistusta ovat samaa lajia kuin jäykkien kappaleiden
säilymislait. Aallonharja etenee asetetulla nopeudella, ja veden
tilavuus ei muutu: jokainen naapurien välinen ero lisää yhteen ruutuun
saman verran kuin se vähentää toisesta.

## Stabiilisuusraja

Aaltoyhtälön eksplisiittisellä ratkaisulla on sama rajoitus kuin
luvun 11 jousilla: aalto ei saa edetä askeleessa pidemmälle kuin
ruudun verran. Kahdessa ulottuvuudessa ehto on
$c\,\Delta t/\Delta x \le 1/\sqrt2$ (CFL-ehto; taito *Fysikaalinen
mallinnus ja simulointi* johtaa sen).

```{.cpp tiedosto="esimerkit/12-vesi.cpp" osa="raja"}
```

```{.tuloste tiedosto="esimerkit/12-vesi.odotettu" rivit="3-5"}
```

Raja 0,71 jää kahden viimeisen rivin väliin. Pelissä aallonnopeus on
ulkonäköparametri, joten se valitaan rajan alapuolelta sen mukaan,
miltä vesi näyttää.

## Noste

Kelluvaan kappaleeseen vaikuttaa Arkhimedeen laki: noste on
syrjäytetyn veden paino. Pystyssä pysyvälle laatikolle syrjäytetty
tilavuus on pohjan ala kertaa upotussyvyys, ja syvyys mitataan veden
pinnasta laatikon kohdalla, joten laatikko nousee ja laskee aaltojen
mukana.

```{.cpp tiedosto="esimerkit/12-vesi.cpp" osa="noste"}
```

Pelkkä noste panisi kappaleen pomppimaan pinnalla loputtomasti, joten
upoksissa olevaan osaan vaikuttaa myös nopeuteen verrannollinen
vastus.

## Roiske: hiukkasallas

Korkeuskenttä ei voi irrottaa vettä pinnasta. Roiske tehdään siksi
erikseen *hiukkasjärjestelmällä*: joukolla pisaroita, jotka syntyvät
osumakohdassa, lentävät heittoliikettä ja katoavat osuessaan takaisin
veteen. Pisarat eivät vaikuta toisiinsa, mikä tekee niistä halpoja.
Veteen palaava pisara jättää pintaan pienen väreen.

```{.cpp tiedosto="esimerkit/yhteinen/vesi.hpp" osa="allas"}
```

Rakenteessa on kolme tavallista ratkaisua. Hiukkaset ovat *altaassa*
(*pool*), jonka koko on kiinteä: pelin aikana ei varata muistia, ja
kun allas on täynnä, uusia pisaroita ei synny. Kuollut hiukkanen
korvataan taulukon viimeisellä elävällä, jolloin elävät ovat aina
taulukon alussa ilman aukkoja. Ja satunnaisluvut tulevat omasta
generaattorista, jonka tila on osa simulaatiota. Viimeiseen palataan
seuraavassa luvussa.

Esimerkki yhdistää osat. Puulaatikko pudotetaan altaaseen, osuma
synnyttää roiskeen ja aallon, ja laatikko jää kellumaan:

```{.cpp tiedosto="esimerkit/12-vesi.cpp" osa="kellunta"}
```

```{.tuloste tiedosto="esimerkit/12-vesi.odotettu" alkaen="laatikko kelluu"}
```

![Laatikko putoaa altaaseen: pudotus, osuma, roiske ja lopuksi
leviävä aalto kelluvan laatikon ympärillä.](kuvat/vesi.png){width=85%}

Laatikon tiheys on 0,6 kertaa veden tiheys, joten sen 30 senttimetrin
korkeudesta jää veden alle 18 senttimetriä. Simulaatio päätyy samaan
lukuun, kun aallot ovat vaimenneet.

Osuman vaikutus veteen on tehty käsin: ruudut laatikon alla saavat
nopeuden alas ja niiden ympärillä ylös niin, että summa on nolla.
Pisaran väre on tehty samoin, joten altaan tilavuus on lopussa sama
kuin alussa. Kytkentä on taiteilijan valinta eikä fysiikkaa, ja se on
korkeuskenttäveden tavallinen käyttötapa: mallin säilymislaki pidetään
voimassa, mutta voimien suuruus säädetään silmällä.

## Kun pinta ei riitä

Kun veden pitää virrata, kaatua astiasta tai täyttää huone, tarvitaan
tilavuutta kuvaava malli. Peleissä käytetään kahta pääsuuntaa.

- **Hiukkasneste.** Vesi on joukko hiukkasia, jotka vaikuttavat
  toisiinsa. *SPH* (*smoothed particle hydrodynamics*) laskee
  tiheyden ja paineen naapurihiukkasista, ja sen sijaintipohjainen
  muunnos (*position based fluids*) pakottaa tiheyden vakioksi
  rajoitteena samassa ratkaisijassa kuin luvun 11 kangas.
  Naapurihaku tehdään ruudukolla, ja laskenta tehdään tavallisesti
  näytönohjaimella (taito *GPU-laskenta*).
- **Ruudukkoneste.** Nopeus ja paine tallennetaan kiinteään
  ruudukkoon, ja kokoonpuristumattomuus pakotetaan projektiolla.
  Savu ja tuli tehdään usein näin. Menetelmä on sama kuin
  insinöörien virtauslaskennassa, mutta karkealla ruudukolla ja
  ehdottoman stabiileilla, tarkkuudesta tinkivillä askelilla.

Molemmissa tavoite on sama kuin koko tutoriaalissa: uskottava liike,
joka ei räjähdä ja mahtuu aikabudjettiin.

## Käytännössä

- **Malli sen mukaan, mitä näkyy.** Lampi ja meri ovat pintoja, sade
  ja roiskeet hiukkasia, ja vain harvoin tarvitaan tilavuusneste.
  Avomeren aallot tehdään usein ilman simulaatiota summaamalla
  valmiita aaltomuotoja.
- **Hiukkaset eivät ole pelitilaa.** Roiskeet, kipinät ja pöly ovat
  koristetta. Ne eivät vaikuta pelin kulkuun, joten ne voi simuloida
  karkeammin, eri tahtiin ja eri koneilla eri tavoin.
- **Kiinteä allas.** Hiukkasten enimmäismäärä päätetään etukäteen, ja
  ylivuoto käsitellään jättämällä uudet syntymättä tai korvaamalla
  vanhimmat.
- **Noste useasta pisteestä.** Tässä laatikko pysyi pystyssä. Kun
  noste lasketaan kappaleen useassa pisteessä erikseen, se tuottaa
  myös vääntömomentin, ja vene kallistuu aallon mukana.
- **Stabiilisuusraja pätee ruudukoille aina.** Eksplisiittisessä
  ruudukkosimulaatiossa tieto saa edetä askeleessa enintään ruudun
  verran. Tiheämpi ruudukko vaatii lyhyemmän askeleen.

## Itsearviointi

- Osaat selittää, mitä korkeuskenttävesi mallintaa ja mitä se ei voi
  esittää.
- Osaat kertoa, miksi veden tilavuus säilyy korkeuskentän askeleessa
  ja mikä ehto rajoittaa aallonnopeutta.
- Osaat laskea kelluvan laatikon nosteen ja tarkistaa tuloksen
  Arkhimedeen lailla.
- Osaat toteuttaa hiukkasaltaan, joka ei varaa muistia pelin aikana.
- Osaat nimetä tilavuusnesteen kaksi päämenetelmää ja niiden
  perusajatuksen.
