# Johdanto {.runko-johdanto}

Digitaalinen piiri koostuu porteista ja kiikuista, mutta kukaan ei
piirrä nykyaikaista piiriä portti kerrallaan. Piiri kuvataan
*laitteistonkuvauskielellä* (hardware description language, HDL), ja
synteesityökalu muuttaa kuvauksen porttitason verkoksi. Kuvaustaso, jolla
lähes kaikki digitaalisuunnittelu tehdään, on *rekisterinsiirtotaso*
(register transfer level, RTL): suunnittelija kertoo, mitkä rekisterit
piirissä on ja millainen kombinaatiologiikka laskee niiden seuraavan
arvon. Kellon reuna siirtää arvot rekistereihin, tästä nimi.

Tämä tutoriaali opettaa RTL-suunnittelua SystemVerilogilla: miten
portit, kiikut ja tilakoneet kuvataan niin, että kuvaus on
synteesikelpoinen, luettava ja toimii samoin simulaattorissa ja
piirissä.

## Esitiedot ja rajaus

Esitietona on taito *Digitaalitekniikka*: Boolen algebra, kombinaatio-
ja sekvenssilogiikka, kiikut, tilakoneet ja lukujärjestelmät oletetaan
tutuiksi. Ohjelmointikokemus auttaa testipenkkien lukemisessa, mutta
sitä ei edellytetä. Poikkeus on luku 13, jonka testit on kirjoitettu
Pythonilla (*Ohjelmoinnin perusteet (Python)* riittää); sen voi ohittaa.

Tutoriaali rajautuu synteesikelpoiseen kuvaukseen ja yksinkertaisiin
itsetarkistaviin testipenkkeihin. Muu käsitellään omissa taidoissaan:

- verifiointimenetelmät (satunnaistus, kattavuus, väittämät, formaali
  verifiointi): *Laitteiston verifiointi*
- synteesi, sijoittelu, ajoitusrajoitteet ja piirin näkyvä toiminta
  simuloidulla kortilla: *FPGA-toteutus*; ASIC-vuo: *ASIC-toteutus*
- väylät, keskeytykset ja järjestelmän kokoaminen lohkoista:
  *SoC-integraatio*
- samat käsitteet VHDL:llä: *RTL-suunnittelu VHDL:llä*.

## HDL ei ole ohjelmointikieli

SystemVerilog näyttää C:ltä, mutta sen merkitys on toinen. Ohjelma on
jono käskyjä, jotka suoritetaan peräkkäin. RTL-kuvaus on joukko
rinnakkaisia laitteistolohkoja, jotka ovat olemassa yhtä aikaa ja
toimivat jatkuvasti. Jokainen `always`-lohko ja jokainen `assign`-lause
on oma piirinsä, ja niiden kirjoitusjärjestyksellä ei ole merkitystä.

Hyvä RTL-suunnittelija ajattelee ensin laitteistoa ja kirjoittaa sitten
koodin, joka kuvaa sen. Hyödyllinen kysymys jokaisen rivin kohdalla on:
*mikä portti, kiikku tai multiplekseri tästä syntyy?* Jos siihen ei
osaa vastata, synteesityökalu vastaa puolesta, eikä vastaus aina miellytä.

Kieli on myös kaksijakoinen. SystemVerilogissa on synteesikelpoinen
osajoukko, jolla kuvataan laitteisto, ja paljon laajempi
verifiointikieli testipenkkejä varten: jonot, merkkijonot, luokat,
satunnaistus, väittämät ja viiveet. Tämä tutoriaali käyttää
testipenkeissä vain perusasioita. Verifiointi on oma taitonsa
(*Laitteiston verifiointi*).

## Historia ja standardit

| Vuosi | Standardi | Keskeistä |
|-------|-----------|-----------|
| 1984 | Verilog (Gateway Design Automation) | simulointikieli, myöhemmin myös synteesiin |
| 1995 | IEEE 1364-1995 | ensimmäinen standardi |
| 2001 | IEEE 1364-2001 | ANSI-tyyliset portit, `generate`, `always @*`, etumerkilliset tyypit |
| 2005 | IEEE 1364-2005 | viimeinen erillinen Verilog-standardi |
| 2005 | IEEE 1800-2005 | SystemVerilog: Verilogin laajennus |
| 2009 | IEEE 1800-2009 | Verilog ja SystemVerilog yhdistettiin |
| 2017 | IEEE 1800-2017 | korjauksia ja selvennyksiä |
| 2023 | IEEE 1800-2023 | nykyinen standardi |

Toinen yleinen laitteistonkuvauskieli on VHDL (IEEE 1076), jota
käytetään paljon Euroopassa, ilmailussa ja puolustusteollisuudessa.
Käsitteet ovat samat, ja ne opetetaan VHDL:llä taidossa
*RTL-suunnittelu VHDL:llä*.

Uusi suunnittelu kirjoitetaan nykyään SystemVerilogilla. Vanhaa
Verilog-2005-koodia on kuitenkin paljon, ja jotkin työkalut tukevat
vain sitä, joten luku 12 kertoo, miten kirjoitetaan yhteensopivaa
koodia.

## Käyttökohteet

RTL-kuvauksesta tehdään joko FPGA-piirin konfiguraatio tai ASIC-piiri:

- **FPGA** (field-programmable gate array) on uudelleenohjelmoitava
  piiri, jossa on hakutauluja (LUT), kiikkuja, muistilohkoja ja
  kertojia. Sitä käytetään prototyypeissä, tietoliikenteessä,
  signaalinkäsittelyssä, ohjausjärjestelmissä ja kiihdyttimissä.
- **ASIC** (application-specific integrated circuit) valmistetaan
  piitehtaassa. Suunnittelu on kallista ja hidasta, mutta piiri on
  pienempi, nopeampi ja sarjatuotannossa halvempi.

RTL ei sovellu kaikkeen. Monimutkaista algoritmia, jonka suorituskyky
riittää prosessorilla, ei kannata toteuttaa laitteistona: ohjelmiston
kehittäminen ja muuttaminen on moninkertaisesti halvempaa.
Algoritmipainotteisessa laskennassa korkean tason synteesi (HLS) C++:sta
voi olla tuottavampi kuin käsin kirjoitettu RTL. RTL on oikea valinta,
kun tarvitaan tarkka hallinta jaksoista, rinnakkaisuudesta, liitännöistä
ja resursseista.

## Työkalut

| Tehtävä | Avoimet | Kaupalliset |
|---------|---------|-------------|
| Lint ja simulointi | Verilator, Icarus Verilog | Questa, VCS, Xcelium, Vivado Simulator |
| Synteesi | Yosys | Vivado, Quartus, Design Compiler, Genus |
| Sijoittelu ja reititys | nextpnr, OpenROAD | Vivado, Quartus, Innovus |
| Muotoilu ja lint | Verible, Slang | Spyglass |

Tutoriaalin esimerkit käännetään ja ajetaan **Verilator 5.020**:llä.
Verilator kääntää SystemVerilogin C++:ksi ja siitä nopean
simulaattorin. Se on myös tiukka lint-työkalu: valitsimella `-Wall`
se varoittaa leveyseroista, käyttämättömistä signaaleista, salvoista ja
monesta muusta. Tämän tutoriaalin esimerkeissä jokainen varoitus on
virhe.

Verilator simuloi kaksitilaista logiikkaa: signaalin arvo on aina 0 tai
1, ei koskaan tuntematon `X` tai korkeaimpedanssinen `Z`. Nelitilaiset
simulaattorit, kuten Questa ja Icarus, näyttävät alustamattoman
rekisterin `X`:nä. Kumpikaan ei vastaa täysin oikeaa piiriä, ja ero
käsitellään luvussa 11.

## Ensimmäinen suunnitelma

Laskuri on yksinkertaisin hyödyllinen sekvenssipiiri. Tässä laskurissa
on parametroitava leveys, asynkroninen nollaus ja sallintasignaali:

```{.systemverilog tiedosto="esimerkit/01-laskuri.sv" osa="moduuli"}
```

Moduulin otsikko kertoo rajapinnan: parametrit `#(...)` ja portit
`(...)`. Lohko `always_ff` kuvaa kiikut: kellon nousevalla reunalla tai
nollauksen laskevalla reunalla rekisteri `arvo` saa uuden arvon.
Sijoitus `<=` on *ei-estävä*, ja se on kellotetun logiikan oikea
sijoitus (luku 5). Synteesi tekee tästä neljä kiikkua, neljän bitin
summaimen ja multiplekserin, joka valitsee vanhan ja kasvatetun arvon
välillä.

Laitteistoa ei ajeta, vaan se simuloidaan *testipenkissä*. Testipenkki
on moduuli ilman portteja. Se tuottaa kellon ja syötteet, kytkee
testattavan moduulin (device under test, `dut`) ja tarkistaa tulokset:

```{.systemverilog tiedosto="esimerkit/01-laskuri.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/01-laskuri.odotettu"}
```

Testipenkki ei ole synteesikelpoista koodia. Viiveet `#5`,
`$display`-tulostus ja `initial`-lohkon peräkkäinen suoritus kuuluvat
simulointiin. Ne ovat sallittuja testipenkissä, mutta eivät
suunnitelmassa.

Esimerkki käännetään ja ajetaan näin:

```text
verilator --binary --assert -Wall --top-module testipenkki 01-laskuri.sv
./obj_dir/Vtestipenkki
```

`--binary` tuottaa suoraan ajettavan simulaattorin. `--top-module`
kertoo ylimmän tason moduulin, kun tiedostossa on useita.
Moniosaisissa esimerkeissä luetellaan kaikki tiedostot. Esimerkkien
testaaja lisää valitsimen `-Wno-DECLFILENAME`, koska yhdessä
tiedostossa on usein useita moduuleja, eikä tiedostonimi vastaa
moduulin nimeä.

## Esimerkkien käytännöt

Kaikki esimerkit on testattu. Testipenkit noudattavat samoja sääntöjä:

- Ylin moduuli on `testipenkki`, ja se tarkistaa tuloksensa itse.
  Virhe pysäyttää simuloinnin kutsulla `$fatal`, ja onnistunut ajo
  tulostaa tiiviin yhteenvedon, jota verrataan odotettuun tulosteeseen.
- Kello tuotetaan silmukalla `initial while (kaynnissa) #5 clk = ~clk;`.
  Kun testi on valmis, `kaynnissa = 1'b0` pysäyttää kellon, tapahtumat
  loppuvat ja simulointi päättyy.
- Syötteet muutetaan hieman kellon reunan jälkeen (`@(posedge clk); #1;`)
  ja tulokset luetaan samoin. Näin testipenkki ei kilpaile
  suunnitelman kiikkujen kanssa samasta reunasta.
- Tiedostot `*.ei-kaanny.sv` näyttävät yleisen virheen: Verilator
  hylkää ne. Rivit, joilla on merkintä `// @virhe`, ovat virheellisiä,
  ja ilman niitä esimerkki kääntyy ja toimii.
- Tiedosto `*.kaatuu.sv` näyttää virheen, joka havaitaan simuloinnin
  aikana.

Esimerkit löytyvät hakemistosta `esimerkit/`, ja paketin kehityskontti
sisältää Verilatorin.

## Lukuohje

Luvut 2–5 ovat perusta: niiden jälkeen osaa kuvata minkä tahansa
synkronisen piirin. Luvut 6–8 käsittelevät suunnittelun
rakennuspalikoita: tilakoneet, datapolut ja muistit. Luvut 9–11
kertovat, miten suunnitelma toimii oikeassa piirissä: kellot, nollaukset,
kellotusalueiden ylitykset ja synteesikelpoisuus. Luku 12 on
Verilog-2005-koodin ylläpitäjille. Luku 13 on ensikosketus cocotbiin:
samat moduulit testataan Pythonilla kirjoitetuilla testeillä.

Kokenut lukija voi lukea kunkin luvun lopussa olevan itsearvioinnin ja
ohittaa luvun, jos hallitsee sen kaikki väitteet. Lisäksi on tarjolla
muutaman sivun pikaopas.

Jatkotaidot on lueteltu viimeisessä luvussa.
