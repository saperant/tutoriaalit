# Lukot

Lukko on rinnakkaisohjelmoinnin perustyökalu: se tekee koodialueesta
yksinoikeudellisen ja tuo mukanaan tapahtumisjärjestyksen. Kaikki lukon
alla tehdyt kirjoitukset näkyvät seuraavalle lukon ottajalle. *Moderni
C++* esitteli `std::mutex`in ja `std::scoped_lock`in, ja
*Käyttöjärjestelmät* kertoi, miten lukko toteutetaan futexilla ja miksi
lukkojärjestys estää lukkiutumisen. Tämä luku käsittelee lukkojen
suunnittelua: monta lukkoa yhtä aikaa, lukijoiden ja kirjoittajan
erottaminen, lukituksen karkeus ja lukkojen tyypilliset ongelmat.

## Lukot ja niiden omistajat

| Tyyppi | Käyttö |
|---------------|-----------------------------------|
| `std::mutex` | Peruslukko; ei rekursiivinen |
| `std::timed_mutex` | Lisäksi `try_lock_for`, `try_lock_until` |
| `std::recursive_mutex` | Sama säie voi lukita monta kertaa; yleensä suunnitteluvirheen oire |
| `std::shared_mutex` | Jaettu (lukijat) ja yksinomainen (kirjoittaja) lukitus |
| `std::scoped_lock` | RAII: yksi tai useampi lukko, ei lukkiutumista |
| `std::unique_lock` | RAII, siirrettävä, voi vapauttaa ja ottaa uudelleen; ehtomuuttujille |
| `std::shared_lock` | RAII jaetulle lukitukselle |
| `std::lock_guard` | Vanhempi yhden lukon RAII; `scoped_lock` korvaa sen |

Lukkoa ei käsitellä kutsuilla `lock` ja `unlock` vaan aina RAII-olion
kautta, jotta poikkeus tai varhainen paluu ei jätä lukkoa päälle.

## Monta lukkoa kerralla

Tilisiirto tarvitsee kaksi tiliä yhtä aikaa. Jos säie A lukitsee ensin
tilin 1 ja sitten tilin 2 ja säie B päinvastoin, ne voivat lukkiutua.
`std::scoped_lock` ottaa useita lukkoja algoritmilla, joka ei lukkiudu
(`std::lock`: ota yksi, yritä muita, vapauta kaikki ja aloita toisesta,
jos jokin on varattu):

```{.cpp tiedosto="esimerkit/06-tilisiirto.cpp" osa="tili"}
```

```{.cpp tiedosto="esimerkit/06-tilisiirto.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-tilisiirto.odotettu"}
```

Testi tarkistaa invariantin, ei yksittäisiä saldoja: rahan kokonaismäärä
pysyy samana ja yksikään saldo ei mene negatiiviseksi. Yksittäiset saldot
ja hylättyjen siirtojen määrä riippuvat lomituksesta, ja ne vaihtelevat
ajosta toiseen. Tämä on rinnakkaisen ohjelman testaamisen perusmalli.

Tarkistus `&mista == &minne` on tarpeen, koska saman mutexin lukitseminen
kahdesti samassa säikeessä on määrittelemätöntä käyttäytymistä. Toinen
tapa välttää lukkiutuminen on **kiinteä lukkojärjestys**, esimerkiksi
aina pienempi osoite tai tunniste ensin. Se on tarpeen, kun lukkoja ei
oteta yhdessä kohdassa vaan peräkkäisissä funktiokutsuissa.

## Lukijat ja kirjoittaja

Jos dataa luetaan paljon ja kirjoitetaan harvoin, lukijat voivat toimia
rinnakkain. `std::shared_mutex` antaa jaetun lukituksen lukijoille ja
yksinomaisen kirjoittajalle:

```{.cpp tiedosto="esimerkit/06-asetukset.cpp" osa="asetukset"}
```

```{.cpp tiedosto="esimerkit/06-asetukset.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-asetukset.odotettu"}
```

Lukija–kirjoittaja-lukko on kalliimpi kuin tavallinen: jaettu lukitus
päivittää lukijalaskuria, joka on itsessään kilpailtu välimuistirivi.
Lyhyillä lukualueilla tavallinen `std::mutex` on usein nopeampi. Jaettu
lukko kannattaa, kun lukeminen kestää kauan (esimerkiksi haku suuresta
rakenteesta) ja lukijoita on monta. Toteutukset eroavat myös siinä,
pääseekö odottava kirjoittaja lukijoiden ohi; huono yhdistelmä voi
nääntyttää kirjoittajan. Jos data on pieni ja vaihtuu kokonaan, luvun
*Muistin takaisinotto* kopioi ja vaihda -malli on parempi: lukijat eivät
lukitse lainkaan.

## Lukituksen karkeus

Yksi lukko koko rakenteelle on yksinkertainen ja helppo todistaa
oikeaksi, mutta kaikki säikeet jonottavat sitä. Hienojakoisempi lukitus
sallii rinnakkaisuuden, mutta lukkoja on enemmän, ja niiden väliset
invariantit ovat vaikeampia. **Raidoitus** (*lock striping*) on
käytännöllinen välimuoto: hajautustaulu jaetaan osiin, joilla on omat
lukkonsa:

```{.cpp tiedosto="esimerkit/06-raidat.cpp" osa="raidat"}
```

```{.cpp tiedosto="esimerkit/06-raidat.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-raidat.odotettu"}
```

Kaksi saman raidan avainta kilpailee edelleen, mutta 16 raidalla ja
neljällä säikeellä kilpailu harvenee. Koko taulun operaatio `koko` ottaa
raidat yksi kerrallaan, joten sen tulos ei ole hetkellinen tilannekuva:
toinen säie voi lisätä avaimen jo lasketulle raidalle. Jos tarvitaan
yhtenäinen tilannekuva, kaikki lukot otetaan aina samassa järjestyksessä.

## Lukkojen ongelmat

- **Lukkiutuminen** (*deadlock*): säikeet odottavat toistensa lukkoja.
  Estetään ottamalla lukot yhdellä `scoped_lock`illa tai kiinteässä
  järjestyksessä. ThreadSanitizer löytää järjestysvirheet, vaikka
  lukkiutuminen ei tapahtuisi testiajossa (luku *ThreadSanitizer ja
  virheiden etsintä*).
- **Elolukko** (*livelock*): säikeet perääntyvät toistensa tieltä
  loputtomasti. Satunnainen odotus ennen uutta yritystä purkaa sen.
- **Jonoutuminen** (*convoying*): kun lukkoa pitävä säie vuorontuu pois tai
  odottaa I/O:ta, kaikki muut jonottavat. Lukon alla ei tehdä I/O:ta eikä
  kutsuta tuntematonta koodia, kuten takaisinkutsuja.
- **Prioriteetin inversio**: matalan prioriteetin säie pitää lukkoa,
  korkea odottaa, ja keskitason säie vie suorittimen. Mars Pathfinder
  -luotain käynnistyi tästä syystä toistuvasti uudelleen vuonna 1997.
  Ratkaisu on prioriteetin periytyminen (`PTHREAD_PRIO_INHERIT`), jota
  reaaliaikakäyttöjärjestelmät käyttävät (taito *Reaaliaikakäyttöjärjestelmät*).
- **Kilpailu itse**: kun lukkoa pyytää moni ydin, sen välimuistirivi
  liikkuu ytimeltä toiselle ja odottajat nukkuvat ja heräävät. Lukon
  hinta on pieni ilman kilpailua ja suuri sen kanssa.

## Käytännössä

- **Yksi lukko ensin.** Aloita karkealla lukituksella, mittaa ja jaa
  hienommaksi vain kilpailluimmat kohdat. Oikea karkea ratkaisu on parempi
  kuin nopea väärä.
- **Lukko ja data yhdessä.** Lukko on samassa luokassa kuin data, jota se
  suojaa, ja dataan pääsee vain lukon kautta. Clangin
  *Thread Safety Analysis* (`-Wthread-safety` ja merkinnät kuten
  `GUARDED_BY`) tarkistaa tämän käännösaikana.
- **Usea lukko yhdellä `scoped_lock`illa**, ja muuten aina samassa
  dokumentoidussa järjestyksessä.
- **Ei odotusta lukon alla.** Ei I/O:ta, ei takaisinkutsuja, ei toisen
  säikeen odottamista. Lukko pidetään mikrosekunteja, ei millisekunteja.
- **Testaa invariantteja.** Rinnakkaisen ohjelman testi tarkistaa
  säilymislait ja ehdot, jotka eivät riipu lomituksesta.

## Itsearviointi

- Osaat lukita kaksi oliota yhtä aikaa ilman lukkiutumista ja tunnistat
  saman lukon kaksoislukituksen vaaran.
- Osaat käyttää `std::shared_mutex`ia ja arvioida, milloin se on
  tavallista lukkoa parempi.
- Osaat jakaa rakenteen raitoihin ja kertoa, mitä se maksaa koko
  rakennetta koskevissa operaatioissa.
- Osaat nimetä lukkiutumisen, elolukon, jonoutumisen ja prioriteetin
  inversion sekä niiden torjuntakeinot.
