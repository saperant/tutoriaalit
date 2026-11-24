# Lukottomat tietorakenteet

Lukoton tietorakenne käyttää lukkojen sijaan atomisia operaatioita. Se ei
ole automaattisesti nopeampi kuin lukolla suojattu rakenne, ja se on
paljon vaikeampi tehdä oikein. Sen etu on edistymistakuu: yhden säikeen
viivästys ei pysäytä muita. Tämä luku rakentaa kolme klassista lukotonta
rakennetta ja näyttää niiden tyypillisimmän virheen, ABA-ongelman.

## Edistymistakuut

| Takuu | Merkitys |
|---------------|-----------------------------------|
| Estävä (*blocking*) | Säie voi joutua odottamaan toista, esimerkiksi lukkoa |
| Esteetön (*obstruction-free*) | Yksin suoritettava säie valmistuu äärellisessä ajassa |
| Lukoton (*lock-free*) | Jokin säie edistyy aina, vaikka muut pysähtyisivät |
| Odotukseton (*wait-free*) | Jokainen säie valmistuu äärellisessä ajassa |

Lukottomuus tarkoittaa, että käyttöjärjestelmän vuorontaja ei voi
pysäyttää koko rakennetta keskeyttämällä yhden säikeen kriittisessä
kohdassa. Siksi lukottomia rakenteita käytetään reaaliaikajärjestelmissä,
signaalinkäsittelijöissä ja äänen tai verkon käsittelyssä, joissa lukon
odotus on sallittua pidempi. Keskimääräisessä läpäisyssä hyvä lukko voittaa
usein lukottoman rakenteen, koska kilpailtu CAS on kallis ja epäonnistunut
yritys toistetaan.

## SPSC-rengaspuskuri

Yksinkertaisin ja käytännössä hyödyllisin lukoton rakenne on rengaspuskuri
yhdelle tuottajalle ja yhdelle kuluttajalle (*single producer, single
consumer*). Kumpikin indeksi on vain yhden säikeen kirjoittama, joten
CAS-operaatioita ei tarvita lainkaan:

```{.cpp tiedosto="esimerkit/08-spsc.cpp" osa="rengas"}
```

```{.cpp tiedosto="esimerkit/08-spsc.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-spsc.odotettu"}
```

Muistijärjestykset muodostavat kaksi julkaisuparia:

- Tuottaja kirjoittaa alkion ja julkaisee sen `tail_`-indeksin
  release-kirjoituksella. Kuluttaja lukee `tail_`in acquirella ennen kuin
  lukee alkion.
- Kuluttaja lukee alkion ja vapauttaa paikan `head_`-indeksin
  release-kirjoituksella. Tuottaja lukee `head_`in acquirella ennen kuin
  kirjoittaa paikkaan uudelleen. Ilman tätä tuottaja voisi kirjoittaa
  paikan yli ennen kuin kuluttaja on lukenut sen.

Oman indeksin luku on `relaxed`, koska säie on itse sen ainoa
kirjoittaja. Indeksit kasvavat ylivuotoon asti (`size_t` kiertää
hallitusti), ja paikka saadaan maskilla. Siksi koon on oltava kahden
potenssi. Indeksit ovat eri välimuistiriveillä, jotta tuottajan ja
kuluttajan kirjoitukset eivät kilpaile samasta rivistä. Tuotantokäyttöön
tarkoitetut toteutukset tallentavat lisäksi toisen osapuolen indeksin
paikalliseen välimuistiin ja lukevat jaetun indeksin vasta, kun
paikallinen arvo ei riitä.

## Treiberin pino

Treiberin pino (1986) on lukoton pino, jonka koko tila on yksi atominen
osoitin päähän. Lisäys ja poisto ovat CAS-silmukoita:

```{.cpp tiedosto="esimerkit/08-treiber.cpp" osa="pino"}
```

Lisäys valmistelee solmun, joka ei ole vielä muiden nähtävissä, ja
julkaisee sen release-CAS:lla. Poisto lukee pään ja sen seuraajan ja
yrittää vaihtaa pään seuraajaan. Jos joku ehti väliin, CAS epäonnistuu ja
poisto aloittaa alusta päivitetyllä päällä.

```{.cpp tiedosto="esimerkit/08-treiber.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-treiber.odotettu"}
```

Pinossa on kaksi piilotettua ongelmaa. Ensinnäkin poisto lukee
`vanha->seuraava`n, vaikka toinen säie on ehkä jo poistanut solmun
`vanha`. Jos se olisi myös vapauttanut solmun, luku osuisi vapautettuun
muistiin. Siksi esimerkki ei vapauta otettuja solmuja ennen kuin kaikki
säikeet ovat valmiita. Toinen ongelma, ABA, syntyy, kun solmuja
kierrätetään. Seuraava luku ratkaisee vapauttamisen; ABA käsitellään
tämän luvun lopussa.

## MPMC-jono

Monen tuottajan ja kuluttajan (*multiple producer, multiple consumer*)
rajattu jono on lukottomista rakenteista käytetyimpiä. Dmitry Vjukovin
rakenteessa jokaisella paikalla on järjestysnumero, joka kertoo, kenen
vuoro paikkaan on. Tuottajat kilpailevat kirjoitusindeksistä ja
kuluttajat lukuindeksistä CAS:lla, mutta itse paikan käsittelee vain
sen voittanut säie:

```{.cpp tiedosto="esimerkit/08-mpmc.cpp" osa="jono"}
```

Paikan järjestysnumero kulkee kierroksittain. Kun järjestysnumero on sama
kuin kirjoitusindeksi, paikka on vapaa; kirjoittaja varaa indeksin CAS:lla,
kirjoittaa arvon ja julkaisee sen asettamalla järjestysnumeroksi `pos +
1`. Lukija odottaa samaa arvoa, lukee ja asettaa numeroksi `pos + N`,
jolloin paikka vapautuu seuraavan kierroksen kirjoittajalle. Jos
järjestysnumero on jäljessä, jono on täynnä (tai lukijalle tyhjä).

```{.cpp tiedosto="esimerkit/08-mpmc.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-mpmc.odotettu"}
```

Rakenne ei ole tiukasti lukoton: jos kirjoittaja pysähtyy varattuaan
paikan mutta ennen julkaisua, lukijat eivät pääse sen ohi. Käytännössä
tämä hyväksytään, koska rakenne on nopea ja yksinkertainen. Esimerkki
näyttää, ettei "lukoton" ole kaksiarvoinen ominaisuus; takuu on
perusteltava rakenne kerrallaan.

## ABA-ongelma

Poiston CAS tarkistaa, että pää on sama kuin luettaessa. Se ei tarkista,
onko pää *pysynyt* samana: jos solmu A poistetaan ja lisätään takaisin,
CAS ei erota uutta A:ta vanhasta. Tämä on **ABA-ongelma**. Seuraava
esimerkki ajaa pahimman lomituksen käsin yhdessä säikeessä, joten
lopputulos on aina sama. Pino käyttää indeksejä osoittimien sijaan, jotta
solmut voi kierrättää ja pään viereen mahtuu versiolaskuri:

```{.cpp tiedosto="esimerkit/08-aba.cpp" osa="pino"}
```

```{.cpp tiedosto="esimerkit/08-aba.cpp" osa="lomitus"}
```

```{.tuloste tiedosto="esimerkit/08-aba.odotettu"}
```

Ilman versiota säikeen 1 CAS onnistuu, ja pään paikalle tulee B, joka on
jo säikeen 2 hallussa. Pinossa on nyt solmu, jota toinen säie käyttää, ja
säikeen 2 palauttama A on kadonnut pinosta. Versiolaskuri muuttuu jokaisella
onnistuneella vaihdolla, joten säikeen 1 vanha havainto ei enää kelpaa.

Ratkaisuja on kolme:

- **Versiolaskuri** päätä vastaavassa sanassa, kuten esimerkissä.
  Osoittimien kanssa se vaatii 16 tavun CAS:n (`cmpxchg16b`) tai
  osoittimen käyttämättömät bitit.
- **LL/SC-käskyt** (ARM, POWER, RISC-V) epäonnistuvat, jos muistipaikkaan
  on kirjoitettu välissä lainkaan, joten niillä ABA ei synny. C++:n CAS
  ei kuitenkaan paljasta tätä ominaisuutta.
- **Turvallinen takaisinotto**: jos solmua ei kierrätetä, kun joku vielä
  saattaa käyttää sitä, samaa osoitetta ei voi tulla takaisin. Seuraavan
  luvun vaaraosoittimet ratkaisevat näin sekä vapautuksen että ABA:n.

## Käytännössä

- **Lukoton rakenne on viimeinen keino.** Lukolla suojattu rakenne on
  helpompi tehdä oikein ja usein yhtä nopea. Lukoton rakenne on perusteltu,
  kun edistymistakuu on vaatimus tai lukko on mitattu pullonkaulaksi.
- **Käytä valmista.** Boost.Lockfree, Folly (`ProducerConsumerQueue`,
  `MPMCQueue`), moodycamel::ConcurrentQueue ja liburcu ovat
  laajasti testattuja.
- **SPSC on helpointa.** Kun rakenteen voi järjestää niin, että jokaisella
  muuttujalla on yksi kirjoittaja, CAS-operaatioita ei tarvita, ja
  oikeellisuus seuraa kahdesta julkaisuparista.
- **Kirjoita jokaiselle muistijärjestykselle perustelu.** Kommentti kertoo,
  minkä kirjoituksen kanssa acquire pariutuu. Ilman perustelua järjestystä
  ei voi tarkistaa katselmoinnissa.
- **Testaa monella tavalla.** ThreadSanitizer, stressitestit,
  AArch64-kone ja mallintarkastimet (CDSChecker, GenMC, Relacy) löytävät
  eri virheitä.

## Itsearviointi

- Osaat erottaa estävän, lukottoman ja odotuksettoman rakenteen ja kertoa,
  mitä lukottomuus takaa ja mitä ei.
- Osaat toteuttaa SPSC-rengaspuskurin ja perustella sen
  muistijärjestykset kahtena julkaisuparina.
- Osaat toteuttaa Treiberin pinon ja kertoa, miksi solmuja ei voi
  vapauttaa heti poiston jälkeen.
- Osaat selittää ABA-ongelman ja kolme tapaa estää se.
