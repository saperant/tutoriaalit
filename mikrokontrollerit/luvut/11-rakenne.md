# Bare-metal-ohjelman rakenne

Edellisten lukujen palaset (käynnistys, rekisterit, keskeytykset,
ajastimet, jonot ja uni) kootaan tässä luvussa ohjelmaksi. Ilman
käyttöjärjestelmää ohjelman rakenne on kokonaan kehittäjän päätettävä,
ja muutama vakiintunut malli kattaa lähes kaikki tarpeet.

## Mallit

| Malli | Rakenne | Sopii, kun |
|----------------|----------------------------------------|------------------------------|
| pääsilmukka (super loop) | `for (;;)` kysyy kaikkien laitteiden tilan vuorotellen | toimintoja on vähän ja aikavaatimukset väljiä |
| etu- ja taustataso | keskeytykset asettavat lippuja, pääsilmukka käsittelee | tapahtumia on harvoin ja niiden käsittely on lyhyt |
| tapahtumajono ja tilakone | keskeytykset lisäävät tapahtumia jonoon, pääsilmukka jakaa ne tilakoneille ja nukkuu | useita tapahtumalähteitä ja virransäästö |
| ajastettu tehtävätaulu | tikki ajaa kiinteällä jaksolla funktioita, jotka eivät odota | säätösilmukat ja jaksolliset mittaukset |
| RTOS | säikeet, joilla oma pino ja jotka voivat odottaa | monta toisistaan riippumatonta tehtävää, verkkopino |

Kaikissa ilman käyttöjärjestelmää toimivissa malleissa on sama sääntö:
**mikään funktio ei saa odottaa**. Jos tehtävä joutuu odottamaan
(tavun saapumista, ajastinta, toisen laitteen vastausta), se palaa ja
jatkaa, kun odotettu tapahtuma tulee. Tilakone on tapa kirjoittaa
tällainen jatkuva tehtävä: tila muistaa, mihin jäätiin.

Pääsilmukan pahin viive on koko silmukan kierroksen kesto, ja yksi
hidas toiminto hidastaa kaikkia. Tapahtumajonossa viive määräytyy
jonossa edellä olevista tapahtumista, ja kiireelliset asiat hoidetaan
keskeytyksessä. RTOS ratkaisee saman ongelman antamalla jokaiselle
tehtävälle oman pinon ja prioriteetin, mikä maksaa RAMia, ja tuo
mukanaan uudet virheluokat: lukot, prioriteetti-inversion ja pinojen
mitoituksen. Taito *Reaaliaikakäyttöjärjestelmät* käsittelee ne.

## Laitteesta riippumaton logiikka

Hyvin jäsennellyssä ohjelmassa on kaksi kerrosta. *Ajurit* tuntevat
rekisterit ja keskeytykset, mutta eivät sovelluksen sääntöjä.
*Sovelluslogiikka* tuntee säännöt, mutta ei yhtään rekisteriä: se saa
tapahtumia ja aikaleimoja ja palauttaa päätöksiä. Erottelusta on kaksi
hyötyä. Logiikan voi siirtää toiseen piiriin muuttamatta sitä, ja sen
voi testata isäntäkoneella tavallisella C-kääntäjällä
millisekunneissa ilman laitetta, emulaattoria tai odottamista.

Esimerkissä on valo, jota ohjataan yhdellä painikkeella. Lyhyt
painallus vaihtaa tilaa järjestyksessä pois, päällä ja vilkku; yli
sekunnin painallus sammuttaa valon heti. Painikkeen kosketin värähtelee,
joten raakanäytteet suodatetaan ensin.

```{.c tiedosto="esimerkit/11-tilakone/tila.h" osa="suodin"}
```

```{.c tiedosto="esimerkit/11-tilakone/tila.c" osa="suodin"}
```

Suodin hyväksyy uuden tilan vasta, kun kolme peräkkäistä näytettä
kymmenen millisekunnin välein ovat samat. Mekaanisen kytkimen
värähtely kestää tyypillisesti alle 10 millisekuntia, joten 30
millisekuntia riittää, eikä ihminen huomaa viivettä.

```{.c tiedosto="esimerkit/11-tilakone/tila.h" osa="valo"}
```

```{.c tiedosto="esimerkit/11-tilakone/tila.c" osa="kasittele"}
```

Alla oleva kuva näyttää tilakoneen siirtymät.

```{.dot otsikko="Valon tilakone"}
digraph {
  rankdir=LR; nodesep=0.5; ranksep=0.8;
  node [shape=circle, width=0.95, fixedsize=true];
  alku [shape=point, width=0.08, style=filled, fillcolor="#1F2A2E"];
  POIS; PAALLA; VILKKU;
  alku -> POIS;
  POIS -> PAALLA [label="lyhyt"];
  PAALLA -> VILKKU [label="lyhyt"];
  VILKKU -> POIS [label="lyhyt"];
  PAALLA -> POIS [label="pitkä", style=dashed];
  VILKKU -> POIS [label="pitkä", style=dashed];
  VILKKU -> VILKKU [label="tikki: LED\nvaihtuu"];
}
```

Tilakoneella ei ole omaa kelloa. Aika tulee tapahtuman mukana
parametrina `nyt`, ja sekin vertaillaan etumerkittömällä erotuksella.
Siksi testi voi syöttää tilakoneelle minkä tahansa aikasarjan.

## Testaus isäntäkoneella

Testi kuvaa painikkeen raakanäytteet merkkijonona, yksi merkki
kymmentä millisekuntia kohden. Sama suodin ja tilakone, jotka ajetaan
laitteessa, käännetään tässä isäntäkoneen `cc`:llä.

```{.c tiedosto="esimerkit/11-tilakone/isanta/testi.c" osa="testit"}
```

```{.tuloste tiedosto="esimerkit/testit/11-isanta.odotettu"}
```

Testi löysi tätä kirjoitettaessa virheen: ensimmäisessä versiossa
kolmannen painalluksen jälkeen oli vain kaksi nollanäytettä, jolloin
suodin ei vielä hyväksynyt vapautusta ja tila jäi vilkkuun. Testi oli
väärin eikä tilakone, mutta sellaisen havaitseminen laitteella olisi
vaatinut painikkeen, oskilloskoopin ja kärsivällisyyttä.

Isäntätestit eivät korvaa laitetestejä: ne eivät löydä virheitä
rekistereistä, ajoituksesta tai keskeytyksistä. Tavallinen jako on
kolmitasoinen. Logiikka testataan isäntäkoneella, ajurit ja niiden
yhteispeli emulaattorissa (QEMU, Renode) tai laitteessa, ja koko laite
testipenkissä (*hardware-in-the-loop*), jossa toinen laite syöttää
tulot ja mittaa lähdöt.

## Laitteen pääsilmukka

Laitteessa SysTick-käsittelijä ajetaan kymmenen millisekunnin välein.
Se lukee painikkeen raakatason (tässä simuloituna aikataulusta),
syöttää sen suotimeen ja lisää jonoon painallus- ja vapautustapahtumat
sekä joka tikillä tikkitapahtuman.

```{.c tiedosto="esimerkit/11-tilakone/main.c" osa="painike"}
```

```{.c tiedosto="esimerkit/11-tilakone/main.c" osa="isr"}
```

Jono on sama yhden tuottajan ja yhden kuluttajan rengas kuin luvussa
7, mutta alkiot ovat tapahtumia aikaleimoineen. Aikaleima otetaan
keskeytyksessä, joten pääsilmukan viive ei vääristä sitä.

```{.c tiedosto="esimerkit/11-tilakone/main.c" osa="jono"}
```

Pääsilmukka ottaa tapahtuman jonosta, antaa sen tilakoneelle ja
toteuttaa tilakoneen päätöksen ajurin kautta. Kun jono on tyhjä, se
nukkuu luvun 8 kaavalla.

```{.c tiedosto="esimerkit/11-tilakone/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/11-tilakone.odotettu"}
```

Ensimmäinen painallus 200 millisekunnin kohdalla värähtelee, mutta
tilakone näkee yhden painalluksen. Tila vaihtuu vapautuksessa, kun
suodin on hyväksynyt sen (400 + 20 ms). Vilkkutilassa LED vaihtuu 250
millisekunnin välein. Viimeinen painallus kestää 1,3 sekuntia, ja
valo sammuu jo sekunnin kohdalla eikä vapautus enää vaihda tilaa.
Jono ei vuotanut kertaakaan yli.

## Ajastettu tehtävätaulu

Kun ohjelma koostuu jaksollisista tehtävistä (lue anturi 100 ms
välein, päivitä säädin 10 ms välein, lähetä tila sekunnin välein),
yksinkertaisin rakenne on taulukko, jossa on kunkin tehtävän funktio,
jakso ja seuraava suoritushetki. Pääsilmukka käy taulukon läpi
jokaisen tikin jälkeen ja kutsuu ne tehtävät, joiden hetki on
koittanut. Rakenne on deterministinen ja helppo analysoida, kunhan
jokainen tehtävä on lyhyt: tehtävien yhteenlaskettu pahin kesto on
mahduttava lyhimpään jaksoon.

## Käytännössä

- **Valitse rakenne ennen kuin kirjoitat ensimmäisen ajurin.**
  Pääsilmukasta tapahtumajonoon siirtyminen myöhemmin on uudelleenkirjoitus.
- **Älä odota missään funktiossa**, jota pääsilmukka kutsuu; kirjoita
  odottava toiminta tilakoneeksi.
- **Erota logiikka rekistereistä** ja testaa se isäntäkoneella. Anna
  aika parametrina, älä lue sitä globaalista laskurista.
- **Aikaleimaa tapahtumat keskeytyksessä.**
- **Siirry RTOS:ään, kun tehtäviä on monta ja niiden aikavaatimukset
  ovat erilaiset**, tai kun tarvitset valmiin verkkopinon. Älä
  kirjoita omaa käyttöjärjestelmää.

## Itsearviointi

- Osaat vertailla pääsilmukkaa, etu- ja taustatasoa, tapahtumajonoa,
  tehtävätaulua ja RTOS:ää ja valita niistä sopivan.
- Osaat kirjoittaa tilakoneen, joka ei odota, ja syöttää sille ajan
  parametrina.
- Osaat suodattaa painikkeen kosketinvärähtelyn.
- Osaat erottaa ajurit ja sovelluslogiikan ja testata logiikan
  isäntäkoneella.
- Osaat koota keskeytyksistä, jonosta, tilakoneesta ja nukkuvasta
  pääsilmukasta tapahtumaohjatun ohjelman.
