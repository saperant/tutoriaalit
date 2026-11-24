# Simulointitestaus

Kaikissa edellisissä luvuissa testi oli samaa muotoa: rakenna
järjestelmä simulaattoriin, arvo vikoja siemenestä, aja ja tarkista
invariantti. Tämä luku kokoaa menetelmän: miten invariantit kirjoitetaan,
miten löydetty virhe pienennetään ymmärrettäväksi ja mitä satunnainen
simulointi ei löydä.

## Menetelmä

Deterministinen simulointitestaus (*deterministic simulation testing*,
DST) vaatii kolme asiaa:

1. **Determinismi.** Kaikki epädeterminismin lähteet, eli verkko, kello,
   levy, säikeiden ajoitus ja satunnaisluvut, kulkevat simulaattorin
   kautta ja johdetaan siemenestä. Yksikin piilotettu lähde, kuten
   järjestämätön hajautustaulu, säikeen ajoitus tai `time()`-kutsu,
   tekee siemenestä hyödyttömän.
2. **Vikojen ruiskutus.** Simulaattori tuottaa ne viat, joita vikamalli
   sallii: katoamiset, viiveet, monistumiset, kaatumiset, jaot ja
   kellon ajautumisen. Usein kannattaa liioitella, eli tuottaa vikoja
   paljon useammin kuin tuotannossa, jotta harvinaiset yhdistelmät
   tulevat vastaan.
3. **Oraakkeli.** Testin on tiedettävä, mikä on virhe. Hyvät invariantit
   ovat turvallisuusominaisuuksia, jotka voi tarkistaa jokaisessa
   tilassa: kaksi johtajaa samalla termillä, eri merkintä samassa
   indeksissä, linearisoitumaton historia, laskurin summa, jonka pitäisi
   täsmätä. Etenemisen voi tarkistaa ajon lopussa: kun viat ovat ohi,
   järjestelmän on toivuttava.

Invariantit kannattaa kirjoittaa järjestelmän tilasta, ei sen
tulosteista. Raft-testin tarkkailija sai tiedon jokaisesta sovelletusta
merkinnästä suoraan solmulta, ja lokien tarkistus luki solmujen lokit.
Tällaista pääsyä ei ole oikeassa verkossa, ja se on yksi simuloinnin
suurimmista eduista.

## Siemenhaku ja pienentäminen

Kun testi kaatuu, siemen toistaa virheen, mutta jälki voi olla
tuhansien tapahtumien mittainen ja täynnä merkityksettömiä vikoja.
*Delta-debuggaus* (Zeller ja Hildebrandt 2002) pienentää syötettä
järjestelmällisesti: se kokeilee poistaa vikaohjelmasta osan kerrallaan
ja pitää poiston, jos virhe säilyy. Lopputulos on *1-minimaalinen*:
minkä tahansa jäljelle jääneen vian poistaminen korjaisi virheen.

```{.cpp tiedosto="esimerkit/11-minimointi.cpp" osa="ddmin"}
```

Verkon siemen pysyy samana, joten jokainen koe on yhtä deterministinen
kuin alkuperäinen. Esimerkki etsii ensimmäisen siemenen, jolla luvun 8
virheellinen Raft rikkoo turvallisuuden 30 vian ohjelmalla, ja pienentää
sen:

```{.cpp tiedosto="esimerkit/11-minimointi.cpp" osa="haku"}
```

```{.cpp tiedosto="esimerkit/11-minimointi.cpp" osa="jalki"}
```

```{.tuloste tiedosto="esimerkit/11-minimointi.odotettu"}
```

Kolmestakymmenestä viasta jäi yksi, ja siihen tarvittiin kahdeksan
koeajoa. Jälki kertoo virheen syyn lähes sellaisenaan. Solmu 2 oli
johtaja termillä 1, ja klusteri sitoutti yli 80 merkintää. Verkko jakautui,
ja vähemmistö {1, 3} aloitti vaaleja toistuvasti termeillä 2, 3 ja 4
(häiritsevä solmu, ks. luku 7). Kun verkko palasi, solmu 1 aloitti termin 5,
ja koska äänestäjät eivät tarkistaneet sen lokia, se voitti, vaikka siltä
puuttuivat jakautumisen aikana sitoutetut merkinnät. Tarkkailija
huomasi rikkeen 5 ms myöhemmin.

Sama periaate pätee muihinkin syötteisiin: viestisekvenssiin,
asiakasoperaatioihin ja verkon asetuksiin. Ominaisuuspohjaisen testauksen
kirjastot (QuickCheck, Hypothesis, RapidCheck) tekevät pienentämisen
automaattisesti.

## Mitä satunnainen simulointi ei löydä

Luvussa 8 mainittiin Raftin hienovaraisin sääntö: edellisen termin
merkintää ei saa sitouttaa pelkän enemmistön perusteella. Makro
`RAFT_BUGI_SITOUTUS` rikkoo säännön, ja tarkkailija laskee, kuinka usein
virheellinen haara suoritettiin:

```{.cpp tiedosto="esimerkit/11-kattavuus.cpp" osa="kattavuus"}
```

```{.tuloste tiedosto="esimerkit/11-kattavuus.odotettu"}
```

Virheellistä haaraa ei suoritettu kertaakaan. Syy on tyhjä merkintä,
jonka johtaja lisää termin alussa: se lähtee samassa viestissä kuin
edellisen termin merkinnät, joten enemmistöllä oleva suurin indeksi on
lähes aina oman termin merkintä. Virhe on olemassa mutta piilossa.
Kun tyhjä merkintä poistetaan makrolla `RAFT_ILMAN_TYHJAA`, haara
suoritetaan:

```{.cpp tiedosto="esimerkit/11-ilman-tyhjaa.cpp" osa="ilman"}
```

```{.tuloste tiedosto="esimerkit/11-ilman-tyhjaa.odotettu"}
```

Virheellinen sitoutus tehtiin 271 kertaa 98 ajossa sadasta, eikä
turvallisuus silti rikkoutunut. Rike vaatii tarkan sarjan: johtaja
sitouttaa vanhan merkinnän ja kaatuu, toinen solmu, jolla on uudempi termi
lokin lopussa mutta ei merkintää, voittaa vaalin ja ehtii korvata
merkinnän enemmistöltä ennen kuin kukaan soveltaa sitä. Kirjoittajan
2 000 lisäajossa optimoituna sitä ei tullut vastaan.

Opetuksia on kolme. *Koodikattavuus ei ole tilakattavuus*: rivi, joka
suoritetaan tuhansia kertoja, voi silti olla väärin. *Satunnaisuus
kattaa leveyttä, ei syvyyttä*: harvinainen viiden tapahtuman sarja vaatii
joko kohdennetun skenaarion tai paljon enemmän ajoja ja vikoja. Ja
*mallintarkistus täydentää simulointia*: TLA+-määrittely ja TLC tai
Apalache käyvät läpi kaikki pienen mallin tilat, myös juuri tällaiset
harvinaiset järjestykset. Raftin kirjoittajat laativat algoritmista
TLA+-määrittelyn, ja Amazon ja Microsoft ovat raportoineet
löytäneensä TLA+:lla suunnitteluvirheitä, joita testit eivät olleet
löytäneet.

## Testausta tehostavia keinoja

- **Parveilu** (*swarm testing*, Groce ym. 2012): jokainen ajo käyttää
  satunnaista osajoukkoa vikatyypeistä ja asetuksista. Kun jokaisessa
  ajossa on kaikkea vähän, harvinaiset vuorovaikutukset jäävät
  piiloon.
- **Ohjattu ajoitus**: vikojen arvontaa painotetaan kiinnostaviin
  hetkiin, kuten juuri vaalin jälkeen tai levykirjoituksen ja vastauksen
  väliin. Hyvät simulaattorit antavat koodin merkitä tällaisia
  kohtia (*buggify*-makrot FoundationDB:ssä).
- **Kattavuusmittarit**: lasketaan, kuinka usein kiinnostavat tilat
  toteutuvat, kuten tämän luvun laskuri. Jos tilaa ei koskaan nähdä,
  sitä ei myöskään testata.
- **Regressiosiemenet**: jokainen virheen paljastanut siemen lisätään
  pysyvään testijoukkoon.
- **Jepsen oikeille järjestelmille**: kun koodia ei voi ajaa
  simulaattorissa, oikeassa verkossa ajettu testi ja historian
  tarkistin ovat seuraavaksi paras vaihtoehto.

## Käytännössä

- **Rakenna simulointi alusta asti.** Determinismin lisääminen
  valmiiseen järjestelmään on vaikeaa, koska epädeterminismin lähteitä on
  kaikkialla. FoundationDB ja TigerBeetle suunniteltiin simulaattorin
  ympärille.
- **Tarkista turvallisuus jokaisessa tilassa.** Ajon lopussa tehty
  tarkistus ohittaa väliaikaiset rikkeet.
- **Pienennä ennen kuin tutkit.** Yhden vian jälki on luettavissa,
  kolmenkymmenen ei.
- **Mittaa, mitä testi näkee.** Laske kiinnostavien tilojen esiintymät;
  nolla kertoo puuttuvasta testistä, ei virheettömyydestä.
- **Yhdistä menetelmiä.** Simulointi löytää toteutuksen virheet,
  mallintarkistus suunnittelun virheet ja Jepsen ympäristön virheet.

## Itsearviointi

- Osaat luetella deterministisen simulointitestauksen kolme vaatimusta
  ja tunnistaa piilotettuja epädeterminismin lähteitä.
- Osaat kirjoittaa turvallisuusinvariantteja järjestelmän tilasta ja
  erottaa ne etenemisen tarkistuksista.
- Osaat pienentää kaatuvan vikaohjelman delta-debuggauksella ja tulkita
  tuloksena saadun jäljen.
- Osaat selittää, miksi koodikattavuus ei takaa, että virhe löytyy,
  ja mitä mallintarkistus tuo lisää.
- Osaat kuvata parveilun, ohjatun ajoituksen ja regressiosiementen
  käytön.
