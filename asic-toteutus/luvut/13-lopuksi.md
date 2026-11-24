# Lopuksi {.runko-kaytannot .runko-lahteet}

## Nyrkkisäännöt

1. **Arkkitehtuuri ja pohjapiirros ratkaisevat.** Myöhemmät vaiheet
   hiovat, mutta eivät korjaa väärää rakennetta tai huonoa
   pohjapiirrosta.
2. **Rajoitteet ovat osa suunnittelua.** SDC versioidaan, katselmoidaan
   ja testataan; rajoittamaton polku on näkymätön.
3. **Jokainen muunnos todistetaan.** Ekvivalenssi RTL:n ja jokaisen
   netlistan välillä, STA jokaisen fyysisen vaiheen jälkeen.
4. **Asetus hitaassa, pito nopeassa kulmassa – kaikki kulmat.**
   Pitorikkeet korjataan kellopuun jälkeen.
5. **Testattavuus alusta asti.** Scan, BIST ja JTAG suunnitellaan
   RTL:ään, ei lisätä viime viikolla.
6. **Kello on suurin kuluttaja.** Portita kello salpapohjaisella
   ICG:llä, ei koskaan JA-portilla.
7. **Sign-off vahvistaa, ei korjaa.** DRC-, IR- ja ajoitusongelmat
   ratkaistaan aikaisin.

## Avoin RTL-to-GDS-vuo

Tämän tutoriaalin opetustoteutukset näyttävät jokaisen vaiheen
algoritmin. Oikea avoin vuo kokoaa samat vaiheet: OpenLane (uudempi
versio LibreLane) ajaa Yosysin, OpenROADin (sijoittelu, CTS,
reititys, STA), Magicin ja KLayoutin (DRC) sekä Netgenin (LVS)
SkyWater SKY130- tai GF180MCU-PDK:lla. Vuo ohjataan asetustiedostolla;
tämä esimerkki näyttää rakenteen, mutta sitä ei ajeta tässä
tutoriaalissa, koska PDK ja työkalut ovat useita gigatavuja:

```text
{
  "DESIGN_NAME": "laskuri",
  "VERILOG_FILES": "dir::laskuri.v",
  "CLOCK_PORT": "clk",
  "CLOCK_PERIOD": 10.0,
  "FP_CORE_UTIL": 50,
  "PL_TARGET_DENSITY_PCT": 60
}
```

```text
openlane config.json      # synteesi → sijoittelu → CTS → reititys
                          # → STA, DRC, LVS, antenni → GDSII
```

Tiny Tapeout -projekti tarjoaa valmiin pohjan, jolla pienen piirin voi
lähettää valmistukseen jaetulla kiekolla ja saada fyysisen piirin
testattavaksi.

## Mallit

| Malli | Luku | Tarkoitus |
|-------|------|-----------|
| NLDM-taulukko | 2 | viive tulon siirtymäajan ja kuorman funktiona |
| Miter + SAT | 3 | muodollinen ekvivalenssi |
| Saapumis- ja vaadittu aika | 4 | ajoitusmarginaali |
| Monisykli- ja väärä polku | 5 | ajoituspoikkeukset |
| PVT-kulma ja OCV | 5 | vaihtelun huomiointi |
| Scan-ketju | 6 | sisäisen tilan ohjaus ja havainnointi |
| LFSR + MISR | 6 | itsetestaus |
| HPWL ja jäähdytys | 7 | sijoittelu |
| H-puu ja Elmore-viive | 8 | kellopuu |
| Leen sokkeloreititin | 8 | reititys |
| ICG | 9 | kellon portitus |
| UPF | 9 | tehoalueet |
| Vastusverkko | 10 | IR-pudotus |
| Poisson ja Murphy | 11 | saanto |
| C-elementti | 12 | asynkroninen kättely |

## Mihin tästä

- **Verifiointi**: testipenkit, kattavuus ja formaalit menetelmät
  piirin oikeellisuuden varmistamiseen ennen tapeoutia.
- **SoC-integraatio**: väylät, IP-lohkot ja järjestelmäpiirin
  kokoaminen.
- **FPGA-toteutus**: sama vuo ohjelmoitavalle logiikalle, josta
  prototyyppi syntyy usein ennen ASICia.
- **EDA-skriptaus**: vuon automatisointi Pythonilla ja Tcl:llä.
- **Tietokonearkkitehtuuri ja arkkitehtuurin tutkiminen**: PPA-
  arviot jo ennen RTL:ää.

## Lähteet ja lisälukemista

- N. Weste, D. Harris: *CMOS VLSI Design: A Circuits and Systems
  Perspective*. Pearson. Kattava CMOS-suunnittelun oppikirja.
- J. Rabaey, A. Chandrakasan, B. Nikolić: *Digital Integrated
  Circuits*. Pearson. Viive- ja tehomallit.
- A. Kahng, J. Lienig, I. Markov, J. Hu: *VLSI Physical Design: From
  Graph Partitioning to Timing Closure*. Springer. Pohjapiirros,
  sijoittelu, CTS ja reititys algoritmeina.
- J. Bhasker, R. Chadha: *Static Timing Analysis for Nanometer
  Designs*. Springer.
- M. Bushnell, V. Agrawal: *Essentials of Electronic Testing for
  Digital, Memory and Mixed-Signal VLSI Circuits*. Springer.
- J. Sparsø: *Introduction to Asynchronous Circuit Design*. DTU,
  vapaasti saatavilla.
- Yosys-käsikirja: <https://yosyshq.readthedocs.io/>
- OpenROAD-dokumentaatio: <https://openroad.readthedocs.io/>
- SkyWater SKY130 -PDK (Apache 2.0):
  <https://skywater-pdk.readthedocs.io/>
- OpenLane/LibreLane: <https://librelane.readthedocs.io/>
- Tiny Tapeout: <https://tinytapeout.com/>
- IEEE 1801 (UPF) ja IEEE 1149.1 (JTAG) -standardit.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Opetuskirjasto `opetus.lib`
on kirjoitettu tätä tutoriaalia varten, eikä se perustu minkään
valmistajan dataan.
