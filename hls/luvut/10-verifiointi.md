# Verifiointi

HLS:n suurin etu verifioinnissa on, että sama C++-koodi on sekä
toteutuksen lähde että sen malli. Mutta se, että C++-ohjelma toimii, ei
vielä kerro, että tuotettu RTL toimii: välissä ovat työkalu, sen pragmat
ja C++:n ja laitteiston erilainen semantiikka. Tämä luku kokoaa
esimerkkien vuon verifiointimenetelmäksi. Taito *Laitteiston
verifiointi* käsittelee kattavuuden, satunnaistuksen ja formaalit
menetelmät yleisesti.

| Vaihe | Todentaa | Ei todenna |
|----------------------------|------------------------------|------------------------------|
| C-simulaatio viitemallia vastaan | algoritmin | laitteistoa |
| C-simulaatio sanitoijin | määrittelemättömän käytöksen puuttumisen testatuilla syötteillä | muita syötteitä |
| RTL:n lint (Verilator) | rakenteelliset virheet tuotetussa RTL:ssä | toimintaa |
| C/RTL-yhteissimulaatio | RTL:n vastaavuuden testivektoreilla | muita syötteitä, ajoitusta |
| vastapaine yhteissimulaatiossa | rajapintaprotokollan | protokollan kaikkia tiloja |
| mallitiedoston vertailu | ettei RTL muuttunut huomaamatta | oikeellisuutta |
| formaali ekvivalenssi | vastaavuuden kaikilla syötteillä | algoritmin oikeellisuutta |
| toteutuksen ajoitusanalyysi | kellotaajuuden | toimintaa |

## C-testipenkki

C-testipenkki on tavallinen C++-ohjelma, jolla on kolme tehtävää:

1. **Viitemalli.** Ydin verrataan toiseen toteutukseen, joka on
   kirjoitettu selkeyttä eikä laitteistoa ajatellen: standardikirjaston
   `std::inner_product` pistetulolle, suora konvoluutio FIR-suotimelle ja
   kolme sisäkkäistä silmukkaa matriisitulolle. Jos viitemalli on sama
   koodi kuin ydin, vertailu ei todenna mitään. Bittitarkka malli
   (taito *Korkean tason mallinnus (SystemC/TLM)*) on hyvä viitemalli.
2. **Testivektorit.** Testipenkki kirjaa jokaisen tapauksen syötteet ja
   ytimen tulokset. Samoilla vektoreilla ajetaan myöhemmin RTL.
3. **Pahimmat tapaukset.** Satunnaiset syötteet kiinteällä siemenellä,
   ääriarvot ja tapaukset, jotka laukaisevat riippuvuudet (luvun 8
   toistuvat luokat).

minihls:n testipenkit kirjaavat vektorit luokalla `Tallennin`:

```{.cpp tiedosto="esimerkit/yhteinen/vektorit.hpp" osa="tallennin"}
```

Virtoja varten testipenkki käyttää luokkaa `virta`, joka keskeyttää
ohjelman, jos tyhjästä virrasta luetaan. Laitteistossa sama tilanne
olisi lukkiutuminen, joka on paljon vaikeampi löytää:

```{.cpp tiedosto="esimerkit/yhteinen/virta.hpp" osa="virta"}
```

## Sanitoijat ja määrittelemätön käytös

C++:ssa etumerkillisen kokonaisluvun ylivuoto on määrittelemätöntä
käytöstä (*undefined behavior*). Laitteisto laskee kahden komplementin
kierrolla, mutta kääntäjä – myös HLS-työkalun etupää – saa olettaa,
ettei ylivuotoa tapahdu, ja optimoida sen mukaan. C-simulaatio voi
silloin antaa eri tuloksen kuin RTL, vaikka kumpikaan ei ole "väärin".
Siksi esimerkkien C-simulaatio käännetään GCC:n sanitoijilla
(`-fsanitize=address,undefined -fno-sanitize-recover=all`), jotka
pysäyttävät ohjelman ensimmäiseen virheeseen.

Pistetulo suurilla syötteillä:

```{.tuloste tiedosto="esimerkit/10-verifiointi/odotettu"}
```

Sanitoija löysi ylivuodon summassa. Korjaus on suunnittelupäätös:
leveämpi summa (`long long` tai `ap_int<48>`), syötteiden rajaaminen
tai saturoiva laskenta (taito *Lukujen esitys ja kiinteän pilkun
aritmetiikka*).
AddressSanitizer löytää samalla tavalla taulukon rajojen ylitykset,
jotka laitteistossa lukisivat hiljaa väärää muistia.

## C/RTL-yhteissimulaatio

minihls tuottaa RTL:n lisäksi testipenkin, joka mallintaa ytimen
ympäristön: muistit, virtojen lähettäjät ja vastaanottajat sekä
lohkotason ohjauksen. Muistimalli on synkroninen RAM, jonka data tulee
seuraavalla jaksolla, kuten `ap_memory` olettaa:

```{.verilog tiedosto="esimerkit/01-mac/mac.tb.sv" osa="muistit"}
```

Jokaista testitapausta kohden testipenkki lataa syötteet muisteihin,
käynnistää ytimen, laskee jaksot `ap_done`:en asti ja vertaa tulokset
C-simulaation tuloksiin:

```{.verilog tiedosto="esimerkit/01-mac/mac.tb.sv" osa="ajo"}
```

Testipenkki ajetaan Verilatorilla (`--binary --timing`), joka kääntää
sekä ytimen että testipenkin C++-ohjelmaksi. Ennen sitä tuotettu RTL
tarkistetaan Verilatorin lintillä (`-Wall`), joka löytää esimerkiksi
leveyksien epäsuhdat ja ajurittomat signaalit. Käyttämättömien bittien
varoitus kytketään pois, koska tuotetussa koodissa 32-bittisistä
arvoista käytetään usein vain osoitteen verran bittejä, ja synteesi
poistaa loput.

Yhteissimulaatio mittaa myös latenssin. Kun mitattu latenssi on sama
kuin raportin arvio, raportti ja RTL ovat sopusoinnussa. Oikeissa
työkaluissa ero on tavallinen, kun silmukan kierrosmäärä riippuu
datasta tai rajapinta pysähtyy, ja yhteissimulaation latenssi on silloin
luotettavampi.

## Mitä yhteissimulaatio löytää

Esimerkeissä yhteissimulaatio on jo löytänyt kaksi virhetyyppiä:

- **Väärä pragma** (luku 8): `dependence false` teki histogrammista
  nopean ja väärän. C-simulaatio ei voi löytää tällaista virhettä, koska
  kääntäjä ei tunne pragmaa.
- **Protokollavirheet** (luku 9): testi vastapaineella todentaa, että
  ydin pysähtyy oikein. Ilman vastapainetta väärin kytketty
  `TREADY` voisi jäädä huomaamatta.

Kolmas virhetyyppi ovat työkalun omat virheet. Niitä on harvoin, mutta
niitä on: jokainen suuri HLS-työkalu on joskus tuottanut väärää RTL:ää
jollekin rakenteelle. Yhteissimulaatio on ainoa tavallinen menetelmä,
joka löytää ne.

## Regressio ja mallitiedostot

Esimerkkien vuo vertaa muutaman ytimen tuotettua RTL:ää ja testipenkkiä
mallitiedostoihin (`mac.v`, `mac.tb.sv`). Vertailu ei todenna
oikeellisuutta, mutta se kertoo heti, jos työkalun muutos tai pragman
lisäys muutti RTL:ää, ja pakottaa tarkistamaan muutoksen. Oikeissa
projekteissa sama tehdään raporteille: jos II, latenssi tai resurssit
muuttuvat työkalun versiopäivityksessä, regressio pysähtyy. Taito
*EDA-työkaluketjujen automatisointi* käsittelee tällaiset laatuportit.

## Formaali ekvivalenssi

Yhteissimulaatio todentaa vastaavuuden vain testatuilla syötteillä.
*Sekventiaalinen ekvivalenssitarkistus* (*sequential logic equivalence
checking*, SLEC) todistaa, että C++-malli ja RTL tuottavat saman
tuloksen kaikilla syötteillä: työkalu muuntaa molemmat logiikaksi ja
etsii SAT- tai SMT-ratkaisijalla syötettä, jolla tulokset eroavat.
Kaupalliset työkalut (esimerkiksi Siemensin SLEC ja Cadencen Jasper
C2RTL) tekevät tämän HLS-vuon osana; avoimista työkaluista Yosysin
SymbiYosys ja EBMC tekevät vastaavaa RTL-tasolla. Menetelmä skaalautuu
huonosti suuriin kertojiin ja pitkiin silmukoihin, joten käytännössä
sitä käytetään ohjauslogiikalle ja pienille lohkoille.

## Käytännössä

- **Viitemalli ei ole ydin.** Kirjoita viite eri tavalla kuin ydin, tai
  käytä standardikirjastoa tai bittitarkkaa mallia.
- **Sanitoijat aina.** Määrittelemätön käytös C-simulaatiossa tarkoittaa,
  että C ja RTL voivat erota.
- **Yhteissimulaatio jokaisen pragman jälkeen.** Pragmat eivät muuta
  C-simulaatiota, joten vain yhteissimulaatio todentaa ne.
- **Testivektorit kattamaan riippuvuudet ja protokollat.** Toistuvat
  arvot, ääriarvot ja satunnainen vastapaine.
- **Mittaa latenssi simulaatiosta** ja vertaa raporttiin. Ero kertoo
  yleensä datasta riippuvasta ohjauksesta tai rajapinnan pysähdyksistä.

## Itsearviointi

- Osaat kirjoittaa C-testipenkin, joka vertaa ydintä riippumattomaan
  viitemalliin ja tuottaa testivektorit.
- Osaat selittää, miksi määrittelemätön käytös voi erottaa C-simulaation
  ja RTL:n, ja käyttää sanitoijia sen löytämiseen.
- Osaat kuvata, mitä C/RTL-yhteissimulaation testipenkki tekee ja mitä
  se todentaa.
- Osaat luetella virhetyypit, jotka löytyvät vain yhteissimulaatiossa,
  ja suunnitella testivektorit niiden löytämiseksi.
- Osaat kertoa, mitä formaali ekvivalenssitarkistus lisää simulointiin
  ja missä se on käytännöllinen.
