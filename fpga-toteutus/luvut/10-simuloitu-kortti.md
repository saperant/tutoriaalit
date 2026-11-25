# Simuloitu kortti

Tähän asti suunnitelmista on saatu testipenkin tuloste ja työkalujen
raportit. Raportti kertoo, että suunnitelma mahtuu piiriin ja on
tarpeeksi nopea, mutta ei sitä, miltä se näyttää käytössä: syttyvätkö
ledit, vastaako sarjaportti, tuleeko näytölle kuva. Sen näkee kortilla,
ja kortin voi korvata ohjelmalla.

Tässä luvussa rakennetaan **simuloitu kortti**: malli iCEBreakerista
painikkeineen, ledeineen, sarjaportteineen ja näyttöineen. Sillä ajetaan
suunnitelma, joka käyttää niitä kaikkia. RTL on sama, joka syntetisoidaan
kortille, eikä sitä nopeuteta tai yksinkertaisteta simulaatiota varten.
Luvun lopussa valmis bittivirta muunnetaan takaisin Verilogiksi ja
ajetaan samalla mallilla. Oikeaa korttia ei tarvita missään vaiheessa.

## Kortin malli

Aiemmat testipenkit olivat SystemVerilogia. Verilator osaa myös kääntää
suunnitelman C++-luokaksi, jota tavallinen ohjelma ajaa kellojakso
kerrallaan. Kortin malli on tällainen ohjelma: se asettaa suunnitelman
tulot, nostaa kellon ja lukee lähdöt, ja lähtöjen ympärille on
kirjoitettu kortin oheislaitteet.

```{.dot otsikko="Simuloitu kortti: suunnitelma Verilatorin kääntämänä ja sen ympärillä kortin oheislaitteiden mallit"}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.5;
  subgraph cluster_k {
    label="kortin malli (kortti.cpp)"; style="rounded"; color="#5B6B70";
    fontsize=10;
    kello [label="kello\n25,125 MHz"];
    napit [label="painikkeet\n(värähtely)"];
    paate [label="pääte\n(sarjaportti)"];
    ylin [label="kortti_ylin\n(RTL, Verilator)", penwidth=1.6];
    ledit [label="ledit"];
    naytto [label="näyttö\n(VGA)"];
    la [label="logiikka-\nanalysaattori"];
    kello -> ylin; napit -> ylin; paate -> ylin [dir=both];
    ylin -> ledit; ylin -> naytto; ylin -> la;
  }
  loki [label="tapahtumaloki", shape=note, style=""];
  kuvat [label="kehykset\n(kuvat)", shape=note, style=""];
  vcd [label="nastat.vcd", shape=note, style=""];
  ledit -> loki; paate -> loki; naytto -> loki [style=dashed];
  naytto -> kuvat; la -> vcd;
}
```

Malli laskee aikaa kellojaksoina. Kellon taajuus ja sarjaportin
bittiaika ovat samat kuin kortilla:

```{.cpp tiedosto="esimerkit/10-kortti/malli/kortti.cpp" osa="aika"}
```

Pääsilmukka on jokaisen tällaisen mallin runko: käyttäjän toimet,
tulot, kellon nouseva reuna, lähtöjen luku ja kellon laskeva reuna.
Aikaraja lopettaa ajon, jos suunnitelma ei tuota kehyksiä lainkaan.

```{.cpp tiedosto="esimerkit/10-kortti/malli/kortti.cpp" osa="silmukka"}
```

Verilator kääntää suunnitelman ja mallin yhdeksi ohjelmaksi:

```{.makefile tiedosto="esimerkit/Makefile" osa="kortti-sim"}
```

Ohjelma tulostaa tapahtumalokin, ja testi vertaa sitä tallennettuun.
Loki on siis samalla tavalla testattu tulos kuin aiempien lukujen
raportit.

## Esittelysuunnitelma

Suunnitelma käyttää kaikkia kortin osia:

```{.systemverilog tiedosto="esimerkit/10-kortti/rtl/demo.sv" osa="liitanta"}
```

Näyttöä varten tarvitaan 25 MHz:n pikselikello, joten kortin 12 MHz
nostetaan PLL:llä. Ylin taso noudattaa luvun 7 mallia: PLL on
`ifdef SYNTHESIS` -lohkossa, ja nollaus vapautuu vasta lukituksen
jälkeen. Kaikki muu logiikka on moduulissa `demo`, joka ei tiedä
piiristä mitään.

```{.systemverilog tiedosto="esimerkit/10-kortti/rtl/kortti_ylin.sv" osa="ylin"}
```

Rajoitetiedosto kytkee portit iCEBreakerin nastoihin. Painikkeet ja
ledit ovat kortin mukana tulevalla lisäkortilla ja näyttö
VGA-lisäkortilla, jossa on neljän bitin vastusverkko kullekin värille:

```{tiedosto="esimerkit/10-kortti/icebreaker.pcf"}
```

Kortin omat nastat ovat iCEBreakerin julkaistusta rajoitetiedostosta,
ja näytön nastat noudattavat Digilentin Pmod VGA -lisäkortin järjestystä
liittimissä PMOD 1A ja 1B. Simuloitu kortti ei tarkista nastoja, eikä
tätä suunnitelmaa ole ajettu oikealla kortilla. Ennen lataamista
rajoitetiedosto on siksi käytävä läpi oman kortin ja lisäkortin
kytkentäkaavioita vasten (luku 11).

## Painike ja kosketinvärähtely

Mekaaninen painike ei sulkeudu kerralla. Koskettimet pomppivat muutaman
millisekunnin, ja 25 MHz:n kellolla jokainen pomppu näyttää erilliseltä
painallukselta. Lisäksi painike on asynkroninen tulo, joten se on
tahdistettava (luku 8). Moduuli tekee molemmat:

```{.systemverilog tiedosto="esimerkit/10-kortti/rtl/painike.sv" osa="painike"}
```

Jotta suodatusta voi testata, kortin mallin painike värähtelee. Malli
tuottaa värähtelyn kiinteästä siemenestä, joten ajo toistuu aina
samanlaisena:

```{.cpp tiedosto="esimerkit/10-kortti/malli/kortti.cpp" osa="painikkeet"}
```

Alla on mallin logiikka-analysaattorin tallenne ensimmäisestä
painalluksesta: painikkeen nasta `btn1` ja suodatettu tila, jonka
suunnitelma näyttää ledillä 5. Nasta käy alhaalla kolmesti ennen
asettumistaan. Ledi syttyy vasta, kun nasta on pysynyt ylhäällä
5,2 ms, ja laskuri kasvaa täsmälleen yhdellä.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/varahtely.json" otsikko="Kosketinvärähtely ja suodatettu tila simuloidun kortin nastoista, näyteväli 0,25 ms"}
```

Suodatusaika on kompromissi: liian lyhyt päästää värähtelyn läpi, liian
pitkä tuntuu viiveeltä. Muutama millisekunti riittää useimmille
painikkeille, ja alle 20 ms:n viivettä ihminen ei huomaa.

## Näyttö

VGA-näyttö piirtää kuvan rivi kerrallaan vasemmalta oikealle ja ylhäältä
alas. Lähde antaa kolme analogista värisignaalia ja kaksi
tahdistuspulssia: vaakatahdistus päättää rivin ja pystytahdistus
kehyksen. Pulssien ympärillä on *kuistit*, joiden aikana värien on
oltava mustat. Tilassa 640 × 480, 60 Hz ajoitus on:

| Osa | Rivillä (pikseliä) | Kehyksessä (riviä) |
|-----|-----|-----|
| Näkyvä kuva | 640 | 480 |
| Etukuisti | 16 | 10 |
| Tahdistuspulssi | 96 | 2 |
| Takakuisti | 48 | 33 |
| Yhteensä | 800 | 525 |

Pikselikello on $800 \cdot 525 \cdot 60 \approx 25{,}2$ MHz. Standardin
arvo on 25,175 MHz; PLL tuottaa 25,125 MHz, jonka 0,2 %:n ero ei haittaa
näyttöjä. Ajoitus on kaksi sisäkkäistä laskuria:

```{.systemverilog tiedosto="esimerkit/10-kortti/rtl/vga_ajoitus.sv" osa="ajoitus"}
```

Kuvan sisältö on kombinaatiologiikkaa: pikselin väri lasketaan sen
paikasta. Kuvamuistia ei tarvita.

```{.systemverilog tiedosto="esimerkit/10-kortti/rtl/kuva.sv" osa="kuva"}
```

Merkkien pistematriisi on vakiotaulukko moduulissa `fontti`, ja pallon
paikka päivittyy kerran kehyksessä moduulissa `pallo`. Ennen nastoja
värit ja tahdistus kulkevat saman rekisterin läpi:

```{.systemverilog tiedosto="esimerkit/10-kortti/rtl/demo.sv" osa="lahto"}
```

Mallin näyttö ei tiedä suunnitelman laskureista mitään. Se näkee vain
nastat ja laskee kuvan paikan tahdistuspulsseista, kuten oikea näyttö:

```{.cpp tiedosto="esimerkit/10-kortti/malli/kortti.cpp" osa="naytto"}
```

Tämän takia malli löytää ajoitusvirheet, jotka näkyisivät oikealla
näytöllä. Kaksi kokeilua samalla suunnitelmalla:

- Kun pimennys jätetään pois (`rgb <= vari_nyt`), malli ilmoittaa lähes
  sata tuhatta värillistä pikseliä kehyksessä kuva-alueen ulkopuolella.
  Oikea näyttö mittaa mustan tason kuistien aikana, ja kuva vääristyisi.
- Kun vaakatahdistus viedään nastaan ilman rekisteriä, se on jakson
  edellä värejä. Kuva siirtyy pikselin, ja malli löytää 480 värillistä
  pikseliä kehyksessä kuva-alueen ulkopuolelta: oikeanpuoleisen reunuksen.

Kuvassa on kolme mallin tallentamaa kehystä. Pallo liikkuu ja vaihtaa
väriä sarjaportin komennosta, ja laskuri näyttää painallukset.

![Simuloidun kortin näytön kehykset 2, 14 ja 26](kuvat/kehykset.png){width=100%}

Alla on kehys 26 täydessä 640 × 480 pikselin tarkkuudessa, täsmälleen
sellaisena kuin malli sen nastoista kokosi: yhden pikselin reunus,
väripalkit, pallo ja painallusten määrä.

![Kehys 26 pikseli pikseliltä](kuvat/kehys.png){width=70%}

## Sarjaportti

iCEBreakerin USB-liitin näkyy tietokoneelle sarjaporttina. Suunnitelmassa
on UART-vastaanotin ja -lähetin (8 databittiä, ei pariteettia, yksi
lopetusbitti). Vastaanotin tahdistaa linjan kahdella kiikulla, odottaa
aloitusbitin reunaa ja näytteistää bitit bittiajan keskeltä:

```{.systemverilog tiedosto="esimerkit/10-uart-debug/uart_rx.sv"}
```

Lähetin siirtää kehyksen ulos bitti kerrallaan. Ajastin laskee bittiajan
kellojaksoja, ja kehys siirtyy vain, kun ajastin on nollassa: tämä on
luvussa 7 kuvattu sallinta johdetun kellon sijaan.

```{.systemverilog tiedosto="esimerkit/10-uart-debug/uart_tx.sv"}
```

Bittiaika on 25,125 MHz / 115 200 ≈ 218 kellojaksoa. Pyöristyksen virhe
on 0,05 %; UART sietää muutaman prosentin, koska vastaanotin tahdistuu
uudelleen jokaisen tavun alussa. Esittelysuunnitelma lähettää rivin
jokaisesta painalluksesta ja kuittaa vastaanottamansa merkin:

```{.systemverilog tiedosto="esimerkit/10-kortti/rtl/demo.sv" osa="viestit"}
```

Mallin pääte on sarjaportin toinen pää. Se tekee ohjelmallisesti saman
kuin vastaanotin ja lähetin, toisesta suunnasta:

```{.cpp tiedosto="esimerkit/10-kortti/malli/kortti.cpp" osa="paate"}
```

## Ajo

Käyttäjän toimet on kirjoitettu malliin taulukoksi:

```{.cpp tiedosto="esimerkit/10-kortti/malli/kortti.cpp" osa="skenaario"}
```

Ajo kattaa puoli sekuntia kortin aikaa, 12,6 miljoonaa kellojaksoa, ja
kestää noin sekunnin. Loki:

```{.tuloste tiedosto="esimerkit/10-kortti/kortti.odotettu"}
```

Lokista voi lukea koko suunnitelman toiminnan:

- Ledi 5 syttyy 8 ms painalluksen jälkeen: 3 ms värähtelyä ja 5 ms
  suodatusta. Samalla hetkellä sarjaporttiin tulee rivi `N=01`.
- Juokseva valo etenee 50 ms:n välein ja kääntyy, kun painiketta 2
  painetaan.
- Merkki `3` vaihtaa pallon värin ja kuittautuu itsellään, tuntematon
  merkki kysymysmerkillä.
- Näyttö tahdistuu: rivillä on 800 jaksoa ja kehyksessä 525 riviä,
  tahdistuspulssit ovat oikean pituiset, ja kuistit ovat mustat.
- Painike 3 pysäyttää pallon, joten kaksi viimeistä kehystä ovat
  pikselilleen samat.

Kehysten tarkisteet sitovat luvun kuvat tähän ajoon: jos suunnitelma
muuttuu niin, että kuva muuttuu, testi huomaa sen. Sama ajo ledien
näkökulmasta, 25 ms:n välein näytteistettynä:

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/ledit.json" otsikko="Juokseva valo, painikkeet ja ledi 5 simuloidun kortin nastoista, näyteväli 25 ms"}
```

Mallin logiikka-analysaattori kirjoittaa nastat VCD-tiedostoon, jonka
voi avata aaltomuotokatselimessa (esimerkiksi GTKWave):

```text
rakennus/kortti-sim/kortti --vcd nastat.vcd --vali-us 1000 \
    --naytteita 500
```

Valinta `--kuvat hakemisto` tallentaa kehykset PPM-kuvatiedostoiksi,
jotka useimmat kuvankatselimet avaavat. Skenaariota
muuttamalla voi kokeilla omia tilanteitaan: kaksi painiketta yhtä aikaa,
merkki kesken painalluksen tai pidempi värähtely kuin suodatusaika.

## Synteesi ja sijoittelu

Sama RTL viedään kortille luvun 3 vuolla, nyt 25,125 MHz:n tavoitteella:

```{.tuloste tiedosto="esimerkit/raportit/kortti.odotettu"}
```

Suunnitelma vie 835 logiikkasolua, 16 % piiristä, ja saavuttaa 33 MHz.
Kantoketjun soluja on paljon, koska jokainen laskuri ja jokainen
vertailu pikselin paikkaan on kantoketju. Kuvassa on nextpnr:n
sijoittelu. PLL on IO-solujen rivissä piirin reunassa. Kriittinen polku
alkaa pikselilaskurista, kulkee pallon paikan vertailun läpi ja päättyy
värirekisteriin.

![Esittelysuunnitelman sijoittelu iCE40 UP5K -piirillä](kuvat/sijoittelu.png){width=52%}

Taajuus ylittää vaaditun 30 %:lla, joten tulos ei ole siemenen varassa
(luku 5).
Jos marginaali loppuisi, ensimmäinen keino olisi liukuhihnavaihe värin
laskentaan (luku 6): näytöllä yhden jakson viive ei näy, kunhan
tahdistusta viivästetään saman verran.

## Bittivirrasta takaisin Verilogiksi

Simulaatio testasi RTL:n. Kortille menee kuitenkin bittivirta, ja
välissä ovat synteesi, sijoittelu ja reititys. IceStormin `icebox_vlog`
tekee matkan toiseen suuntaan: se lukee sijoitellun piirin tilan
(ASC-tiedoston, jossa on bittivirran sisältö tekstinä) ja kirjoittaa
Verilog-moduulin, jossa on piirin jokainen käytetty LUT ja kiikku.

```{.makefile tiedosto="esimerkit/Makefile" osa="takaisin"}
```

Palautetussa moduulissa ei ole enää signaalien nimiä eikä hierarkiaa,
vain satoja hakutauluja ja kiikkuja, joiden nimet ovat numeroita.
Nastoilla on rajoitetiedoston nimet, joten pieni kääre antaa moduulille
saman liitännän kuin RTL:n ylimmällä tasolla:

```{.systemverilog tiedosto="esimerkit/10-kortti/bittivirta/kaare.sv" osa="kaare"}
```

PLL on analoginen lohko, jota bittivirta vain konfiguroi, joten
palautetussa piirissä se on yhä primitiivi `SB_PLL40_PAD`. Samassa
tiedostossa on sille simulointimalli, joka tekee saman kuin
RTL-simulaation suora kytkentä: kello kulkee läpi ja lukitus on päällä.

Sama kortin malli ajaa nyt bittivirrasta palautettua piiriä, ja testi
vaatii, että loki on merkilleen sama kuin RTL:llä: samat ledit samoilla
hetkillä, samat rivit sarjaportissa ja samat kehysten tarkisteet.
Bittivirta piirtää siis saman kuvan. Ajo on hitaampi, noin viisi
sekuntia, koska simulaattori laskee jokaisen hakutaulun erikseen.

Tämä on vahvempi tarkistus kuin raporttien lukeminen: synteesi,
sijoittelu ja bittivirran kokoaminen eivät muuttaneet toimintaa tässä
ajossa. Ajoitusta se ei todista. Palautetussa piirissä ei ole
viiveitä, joten nopeus varmistetaan edelleen ajoitusraportista. nextpnr
osaa kirjoittaa viiveet SDF-tiedostoon (`--sdf`) viiveellistä
porttitason simulointia varten, mutta staattinen ajoitusanalyysi kattaa
kaikki polut ja simulaatio vain ne, joita testi sattuu käyttämään.

## Mitä simuloitu kortti ei kerro

Malli on yhtä hyvä kuin sen oletukset. Simulaation ulkopuolelle jäävät

- **nastat**: rajoitetiedoston numerot ja lisäkorttien kytkennät,
- **sähköiset ominaisuudet**: jännitetasot, nousuajat, kaapelit ja
  näytön todellinen toleranssi,
- **PLL**: lukittumisaika ja se, ovatko parametrit sallituissa rajoissa
  (tämän kertoo `icepll` ja synteesin loki),
- **ajoitus**: mallin kello on ideaalinen, ja
- **metastabiilius**: tahdistin on mukana, mutta simulaatiossa
  asynkroninen tulo osuu aina siististi kellon reunojen väliin.

Näitä varten on oikea kortti. Simuloitu kortti muuttaa kuitenkin sen,
mitä kortilla etsitään: logiikkaviat on jo löydetty, joten jäljelle
jäävät luvun 11 taulukon viat simuloinnin ulkopuolelta.

## Käytännössä

- **Tee kortista malli.** Jo pieni malli (kello, sarjaportti ja ledit)
  nopeuttaa työtä, koska suunnitelman voi ajaa sekunneissa ja jokainen
  signaali on näkyvissä. Avoimia valmiita malleja on myös, mutta oman
  mallin oletukset tunnet.
- **Malli nastojen takaa.** Oheislaitteen malli saa käyttää vain
  nastoja, ei suunnitelman sisäisiä signaaleja. Näyttö, joka laskee
  kuvan paikan tahdistuksesta, löytää virheet, joita sisäisiä laskureita
  lukeva malli ei löytäisi.
- **Sama RTL kortille ja simulaatioon.** Simulaatiota varten
  lyhennetyt laskurit ja ohitetut lohkot ovat paikkoja, joissa kortti ja
  simulaatio eroavat. Kun simulaattori on nopea, niitä ei tarvita.
- **Tee tuloksesta testi.** Loki ja kehysten tarkisteet verrataan
  tallennettuihin, joten kuva ei voi muuttua huomaamatta.
- **Aja bittivirta takaisin.** Jos työkaluketjusi osaa palauttaa
  bittivirran tai sijoitellun netlistan simuloitavaksi, sama testi
  kannattaa ajaa sitä vasten ennen kortille menoa.

## Itsearviointi

- Osaat kertoa, miten Verilatorin kääntämää suunnitelmaa ajetaan
  C++-ohjelmasta kellojakso kerrallaan.
- Osaat suodattaa painikkeen kosketinvärähtelyn ja testata suodatuksen
  simulaatiossa.
- Osaat laskea VGA-tilan pikselikellon ja selittää tahdistuspulssit ja
  kuistit.
- Osaat perustella, miksi oheislaitteen malli käyttää vain nastoja.
- Osaat muuntaa bittivirran takaisin Verilogiksi ja kertoa, mitä sen
  simulointi todistaa ja mitä ei.
