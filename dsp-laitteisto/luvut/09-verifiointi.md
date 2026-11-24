# Verifiointi

Signaalinkäsittelylohkon voi testata kahdella tavalla. *Toiminnallinen*
testi mittaa, tekeekö lohko sen, mitä signaalinkäsittelyn kannalta
pitää: taajuusvaste, vaimennus, SNR. *Bittitarkka* testi vertaa
jokaista ulostulonäytettä malliin. Molempia tarvitaan, mutta ne
löytävät eri vikoja. Tässä luvussa rakennetaan testipenkki, joka tekee
molemmat, ja nähdään istutetulla vialla, miksi toiminnallinen testi
yksin ei riitä.

Taito *Laitteiston verifiointi* esitteli testipenkin osat (ajuri,
monitori, malli, tulostaulu) ja cocotb:n. Tässä samat osat
sovitetaan virtaliitäntään ja signaalinkäsittelyyn.

## Ajuri ja vastaanottaja

Ajuri syöttää näytteet liitäntään ja pitää satunnaisia taukoja.
Tulot asetetaan laskevalla reunalla, ja kättely tarkistetaan
nousevalla reunalla ennen kuin rekisterit päivittyvät:

```{.python tiedosto="esimerkit/penkit/virta.py" osa="ajuri"}
```

Vastaanottaja kerää ulostulot ja pitää satunnaista vastapainetta.
Ajurin tauot ja vastaanottajan vastapaine tulevat samasta siemenestä,
joten epäonnistunut ajo toistuu täsmälleen samana:

```{.python tiedosto="esimerkit/penkit/virta.py" osa="vastaanottaja"}
```

Satunnaiset tauot ja vastapaine testaavat liitännän ohjauksen: jos
liukuhihna hukkaa tai monistaa näytteen pysähdyksessä, ulostulojono
siirtyy ja vertailu epäonnistuu heti. Testipenkki ei oleta mitään
latenssista. Se vertaa jonoja, joten sama testi kelpaa yhden jakson
transponoidulle FIR-suotimelle ja yhdeksän jakson jaetulle.

## Bittitarkka vertailu

Vertailu on yksinkertainen: jokaisen näytteen on oltava sama.
Raportti kertoo erojen määrän ja ensimmäisen eron, koska ensimmäinen
ero on lähin vian syytä:

```{.python tiedosto="esimerkit/penkit/virta.py" osa="vertaa"}
```

Testisarja on yhteinen kaikille suotimille. Ympäristömuuttuja `SUODIN`
valitsee mallin, ja ajaja valitsee RTL:n:

```{.python tiedosto="esimerkit/penkit/test_suodin.py" osa="asetukset"}
```

```{.python tiedosto="esimerkit/penkit/test_suodin.py" osa="aja"}
```

Jokainen testi raportoi myös, *kokeileeko* se rajoja. Saturoivalle
suotimelle lasketaan malli toiseen kertaan niin, että ylivuoto
kiertää, ja eroavien näytteiden määrä kertoo, moneenko näytteeseen
saturaatio vaikuttaa. Jos luku on nolla, testi ei olisi huomannut
puuttuvaa saturaatiota. CIC-suotimelle raportoidaan vastaavasti
integraattorien ylivuodot. Tämä on toiminnallisen kattavuuden mittari,
joka on kirjoitettu suoraan testin raporttiin.

## Suunnatut ja satunnaiset testit

Suunnatut testit valitaan sen mukaan, mitä halutaan nähdä:

```{.python tiedosto="esimerkit/penkit/test_suodin.py" osa="suunnatut"}
```

- **Impulssi** näyttää kertoimet. Jos kertoimet ovat väärässä
  järjestyksessä tai yksi puuttuu, ero on ensimmäisissä näytteissä.
- **Askel** näyttää tasavirtavahvistuksen ja ylityksen. Täysi
  positiivinen ja negatiivinen askel vievät ulostulon molempiin
  rajoihin.
- **Pahin tapaus** on täysi arvo jokaisen kertoimen etumerkillä.
  Se tuottaa suurimman mahdollisen summan ja on ainoa testi, joka
  saa luvun 2 suotimen ylittämään alueen 11 %.

Satunnainen testi syöttää tasajakautuneita näytteitä koko alueelta:

```{.python tiedosto="esimerkit/penkit/test_suodin.py" osa="satunnainen"}
```

Se löytää kaiken, mikä näkyy tavallisilla arvoilla, mutta ei
rajatapauksia. Tasajakautuneen kohinan teho jakautuu tasaisesti
kaikille taajuuksille, ja alipäästö vaimentaa siitä suurimman osan,
joten ulostulo ei koskaan lähesty rajaa. Luvun 1 tulosteessa
satunnaisen testin rivillä lukee "saturaatio vaikuttaa 0".

## Taajuusvaste RTL:stä

Toiminnallinen testi syöttää siniaaltoja ja mittaa vahvistuksen
RTL:n ulostulosta. Jokainen taajuus valitaan mittausikkunan
DFT-lokeroon, jolloin amplitudi saadaan yhdestä DFT-kertoimesta ilman
vuotoa, ja jokaiselle taajuudelle annetaan ensin aikaa asettua:

```{.python tiedosto="esimerkit/penkit/test_suodin.py" osa="taajuusvaste"}
```

Mitattua vahvistusta verrataan kertoimista laskettuun vasteeseen
toleranssilla 0,004 eli noin 0,03 dB päästökaistalla. Ero syntyy
ulostulon kvantisoinnista. Vasta lopuksi tarkistetaan sama jono
bitilleen.

## Väärä pyöristys

Istutettu vika `BUGI_KATKAISU` unohtaa pyöristyksen puolikkaan, eli
ulostulo katkaistaan. Vika on tyypillinen: se syntyy, kun yhteinen
kavennusfunktio kirjoitetaan kiireessä tai kun yksi lohko kopioidaan
toisesta, jossa katkaisu oli tarkoituksellinen.

```text
make -C esimerkit cocotb-fir-suora-katkaisu
```

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fir-suora-katkaisu.odotettu"}
```

Taajuusvaste on toleranssin sisällä kaikilla neljällä taajuudella:
katkaisu tuottaa vain puolen LSB:n tasavirtapoikkeaman, ja yksi
DFT-lokero ei näe tasavirtaa. Toiminnallinen testi päästäisi vian
läpi. Bittitarkka vertailu löytää sen jokaisesta testistä, ja
ensimmäinen ero on impulssitestin ensimmäinen näyte.

Vika ei ole harmiton. Puolen LSB:n poikkeama kertautuu jokaisessa
seuraavassa lohkossa, ja kun signaali myöhemmin vahvistetaan, siitä
tulee näkyvä tasavirtakomponentti. Luvun 2 analyysin mukaan katkaisu
myös huonontaa SNR:ää 6 dB. Toiminnallinen testi mittaa sen, mitä sen
kirjoittaja ajatteli mitata; bittitarkka testi löytää myös sen, mitä
kukaan ei ajatellut.

## Verilator pitkiin ajoihin

cocotb ja Icarus Verilog ovat joustavia mutta hitaita: jokainen
kellojakso kulkee Pythonin kautta. Pitkät regressiot ajetaan
Verilatorilla, joka kääntää RTL:n C++:ksi. Testipenkki on lyhyt
C++-ohjelma, joka lukee sisääntulon ja mallin ulostulon tiedostoista:

```{.cpp tiedosto="esimerkit/verilator/paa.cpp" osa="paa"}
```

```{.makefile tiedosto="esimerkit/Makefile" osa="verilator"}
```

```{.tuloste tiedosto="esimerkit/odotetut/verilator-fir.odotettu"}
```

Sata tuhatta näytettä kestää sekunnin murto-osan; cocotb:llä samaan
menisi noin minuutti. Sisääntulosta puolet on ääriarvoja, joten
saturaatio tulee testatuksi. Sama vika löytyy samalla tavalla:

```{.tuloste tiedosto="esimerkit/odotetut/verilator-fir-katkaisu.odotettu"}
```

Noin joka toinen näyte eroaa, koska katkaisu ja pyöristys antavat
eri tuloksen aina, kun pudotettavien bittien ylin bitti on yksi.

Verilator tarkistaa lisäksi koodin tiukimmilla varoituksilla. Jokainen
leveysero on varoitus, ja varoitus on virhe:

```{.makefile tiedosto="esimerkit/Makefile" osa="lint"}
```

Leveysvaroitukset ovat signaalinkäsittelyssä erityisen arvokkaita.
Luvun 3 summat kirjoitettiin muodossa `summa + AW'(p[i])`, koska ilman
eksplisiittistä levennystä Verilator varoittaa, että 28-bittinen tulo
lisätään 31-bittiseen summaan. Tässä tapauksessa SystemVerilogin
etumerkkilaajennus olisi tehnyt oikein, mutta lukija ei näe sitä, ja
toisessa lausekkeessa sama luottamus katkaisisi tuloksen.

## Mallin testaus

Bittitarkka testi on niin hyvä kuin malli. Jos malli on väärin, RTL
testataan väärää vastaan, ja vika on molemmissa. Mallilla on siksi omat
testinsä, jotka vertaavat sitä liukulukulaskentaan ja tunnettuihin
ominaisuuksiin:

```{.python tiedosto="esimerkit/testit/test_malli.py" osa="perus"}
```

```{.python tiedosto="esimerkit/testit/test_malli.py" osa="fir"}
```

```{.python tiedosto="esimerkit/testit/test_malli.py" osa="cordic"}
```

Mallin testit ovat nopeita (alle sekunti) ja ajetaan ensimmäisinä.
Ne eivät vaadi simulaattoria, joten ne voi ajaa myös
algoritmisuunnittelijan koneella, jolla RTL-työkaluja ei ole.

## Käytännössä

- Vertaa jokaista ulostulonäytettä malliin. Toleranssivertailu
  piilottaa juuri ne viat, jotka kiinteän pilkun toteutuksessa ovat
  yleisimpiä: väärä pyöristys, puuttuva saturaatio ja bitin siirtymä.
- Lisää toiminnallinen testi (taajuusvaste, SNR) bittitarkan rinnalle.
  Se tarkistaa, että malli itse täyttää vaatimukset.
- Testaa liitäntä satunnaisilla tauoilla ja vastapaineella. Sama
  siemen tuottaa saman ajon.
- Raportoi, kokeileeko testi rajoja. Testi, joka ei koskaan
  saturoidu, ei testaa saturaatiota.
- Aja lyhyet testit cocotb:llä ja pitkät Verilatorilla. Lintaa
  kaikki moduulit `-Wall`-tasolla ja käsittele leveysvaroitukset
  virheinä.
- Testaa malli erikseen ennen kuin RTL testataan sitä vastaan.

## Itsearviointi

- Osaat rakentaa virtaliitännän ajurin ja vastaanottajan, jotka
  pitävät satunnaisia taukoja ja vastapainetta toistettavasti.
- Osaat valita suotimelle suunnatut testit, jotka vievät sen rajoille,
  ja selittää, miksi satunnainen testi ei tee sitä.
- Osaat mitata taajuusvasteen RTL:n ulostulosta ja verrata sitä
  kertoimista laskettuun.
- Osaat selittää istutetun pyöristysvian avulla, miksi toiminnallinen
  testi ei riitä ja bittitarkka testi tarvitaan.
- Osaat ajaa saman vertailun Verilatorin C++-testipenkillä ja tiedät,
  milloin se kannattaa.
