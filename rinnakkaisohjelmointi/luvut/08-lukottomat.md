# Lukottomat tietorakenteet

Lukoton tietorakenne käyttää lukkojen sijaan atomisia operaatioita. Se ei
ole automaattisesti nopeampi kuin lukolla suojattu rakenne, ja se on
paljon vaikeampi tehdä oikein. Sen etu on edistymistakuu: yhden säikeen
viivästys ei pysäytä muita. Tämä luku määrittelee ensin, mitä
lukottomalta rakenteelta vaaditaan, rakentaa sitten kolme klassista
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

## Milloin rinnakkainen rakenne on oikein

Edistymistakuu kertoo, milloin rakenne etenee, mutta ei sitä, milloin
se toimii oikein. Yksisäikeisen pinon oikeellisuus on helppo sanoa:
`ota` palauttaa viimeksi lisätyn alkion. Rinnakkain operaatiot
limittyvät ajassa, eikä "viimeksi" tarkoita enää mitään.

Vakiintunut määritelmä on **linearisoituvuus** (*linearizability*,
Herlihy ja Wing 1990). Rakenne on linearisoituva, jos jokainen operaatio
näyttää tapahtuvan yhdessä hetkessä jossain kutsunsa ja paluunsa
välissä, ja näin järjestettynä operaatiot muodostavat kelvollisen
yksisäikeisen suorituksen. Tuo hetki on operaation
**linearisointipiste**. Kaksi operaatiota, jotka eivät limity ajassa,
pysyvät siis todellisessa järjestyksessään; limittyvät saa järjestää
kummin päin tahansa.

Tämän luvun rakenteissa linearisointipiste on yksi atominen operaatio:
SPSC-renkaassa indeksin release-kirjoitus ja Treiberin pinossa
onnistunut CAS. Epäonnistunut CAS ei muuta mitään, joten sen voi
toistaa. Perustelu "tämän rivin jälkeen operaatio on tapahtunut, sitä
ennen ei" on sama, jolla lukotonta koodia katselmoidaan.

Linearisoituvuutta ei voi testata suoraan, mutta sen seurauksia voi:
jokainen lisätty alkio otetaan täsmälleen kerran, eikä mitään katoa tai
kahdennu. Luvun esimerkit ja luvun *ThreadSanitizer ja virheiden
etsintä* stressitesti tarkistavat juuri tällaisia invariantteja.
Taito *Hajautetut järjestelmät* käyttää samaa käsitettä usean koneen
tietovarastoille.

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

```{.dot otsikko="Rengas, jossa on kolme alkiota. Kumpaakin indeksiä kirjoittaa vain yksi säie, ja toinen lukee sen."}
digraph {
  node [shape=box];
  r [shape=record, label="<p0> 0|<p1> 1|<p2> 2: a|<p3> 3: b|<p4> 4: c|<p5> 5|<p6> 6|<p7> 7"];
  h [label="head_ = 2\nkirjoittaa vain kuluttaja (release),\ntuottaja lukee (acquire)"];
  t [label="tail_ = 5\nkirjoittaa vain tuottaja (release),\nkuluttaja lukee (acquire)"];
  h -> r:p2 [label="seuraava luettava"];
  t -> r:p5 [label="seuraava vapaa"];
}
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
sen voittanut säie. Tunnetuin rajoittamaton lukoton jono on Michaelin
ja Scottin linkitetty jono (1996), jossa solmut varataan
dynaamisesti; se tarvitsee seuraavan luvun takaisinottoa, joten tässä
käytetään rajattua rakennetta:

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

```{.dot otsikko="ABA-lomitus ilman versiolaskuria. Katkoviivalla piirretyt solmut ovat säikeen 2 hallussa. Lopussa pää osoittaa solmuun B, jota säie 2 käyttää, ja A (pisteviiva) on kadonnut pinosta."}
digraph {
  node [shape=box, width=0.5]; ranksep=0.35;
  t1 [shape=plaintext, width=3.3, label="1. Säie 1 lukee: pää = A, seuraaja = B"];
  t2 [shape=plaintext, width=3.3, label="2. Säie 2 ottaa A:n ja B:n"];
  t3 [shape=plaintext, width=3.3, label="3. Säie 2 palauttaa A:n"];
  t4 [shape=plaintext, width=3.3, label="4. Säie 1: CAS(pää: A → B) onnistuu"];
  t1 -> t2 -> t3 -> t4 [style=invis];
  p1 [label="pää", shape=ellipse]; p2 [label="pää", shape=ellipse];
  p3 [label="pää", shape=ellipse]; p4 [label="pää", shape=ellipse];
  a2 [label="A", style="dashed,rounded"]; b2 [label="B", style="dashed,rounded"];
  b3 [label="B", style="dashed,rounded"]; b4 [label="B", style="dashed,rounded"];
  a1 [label="A"]; b1 [label="B"]; c1 [label="C"]; c2 [label="C"];
  a3 [label="A"]; c3 [label="C"]; c4 [label="C"];
  a4 [label="A", style="dotted,rounded"];
  { rank=same; t1 -> p1 [style=invis]; p1 -> a1 -> b1 -> c1; }
  { rank=same; t2 -> p2 [style=invis]; p2 -> c2; c2 -> a2 -> b2 [style=invis]; }
  { rank=same; t3 -> p3 [style=invis]; p3 -> a3 -> c3; c3 -> b3 [style=invis]; }
  { rank=same; t4 -> p4 [style=invis]; p4 -> b4 -> c4; c4 -> a4 [style=invis]; }
}
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
- Osaat selittää linearisoituvuuden ja osoittaa rakenteen operaation
  linearisointipisteen.
- Osaat toteuttaa SPSC-rengaspuskurin ja perustella sen
  muistijärjestykset kahtena julkaisuparina.
- Osaat toteuttaa Treiberin pinon ja kertoa, miksi solmuja ei voi
  vapauttaa heti poiston jälkeen.
- Osaat selittää ABA-ongelman ja kolme tapaa estää se.
