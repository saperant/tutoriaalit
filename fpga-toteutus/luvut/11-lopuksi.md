# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Ajattele palikoina.** LUT ja kiikku, kantoketju, lohko-RAM, DSP.
   Kuvaus, joka ei osu palikkaan, rakentuu kalliisti logiikkasoluista.
2. **Simulaatio ennen synteesiä, synteesi ennen korttia.** Jokainen
   vaihe on hitaampi ja näkee vähemmän kuin edellinen.
3. **Skriptattu, toistettava vuo.** Kiinteät työkaluversiot ja siemen,
   raportit tarkistetaan automaattisesti.
4. **Lue raportit.** Solutyypit kertovat, osuiko kuvaus palikkaan;
   Fmax ja kriittinen polku kertovat, riittääkö nopeus ja miksi ei.
5. **Ajoitusvirhe on suunnitteluvirhe.** `FAIL` ei ole varoitus.
   Marginaalia vähintään 10 %.
6. **Liukuhihnoita datapolku.** Lisärekisteri on FPGA:lla lähes
   ilmainen; takaisinkytkentä lyhennetään muulla tavoin.
7. **Yksi kello, jos mahdollista.** Hidas tahti sallinnalla; jokainen
   uusi kello on uusi kellotusalue.
8. **Ylitykset vain tunnetuilla rakenteilla.** Tahdistin, kättely,
   asynkroninen FIFO, ja lista jokaisesta ylityksestä.
9. **Rajoitetiedosto on lähdekoodia.** Väärä nasta voi rikkoa kortin.

## Mallit

| Malli | Luku | Tarkoitus |
|-------|------|-----------|
| Rekisteröity muistin luku | 4 | lohko-RAMin päättely |
| Rekisteröity kertoja `-dsp`-valinnalla | 4 | DSP-lohkon päättely |
| Rekisteröity tulo ja lähtö | 6 | IO-polut pois kriittiseltä polulta |
| Liukuhihnavaihe | 6 | lyhyempi kriittinen polku |
| PLL `ifdef SYNTHESIS` -lohkossa | 7 | simuloitava ja syntetisoitava ylin taso |
| Nollauksen tahdistin `LOCK`-signaalista | 7 | turvallinen käynnistys |
| Kellon sallinta | 7 | hidas tahti ilman uutta kelloa |
| Asynkroninen FIFO | 8 | tieto kellotusalueiden välillä |
| Jaettu laskentayksikkö | 9 | vähemmän erikoislohkoja |
| UART-virheenjäljitysydin | 10 | sisäinen tila näkyviin kortilla |

## Mihin tästä

- **Suuremmat piirit.** Latticen ECP5 toimii samalla avoimella
  ketjulla (`nextpnr-ecp5`, Project Trellis) ja tuo enemmän
  logiikkaa, SERDES-lähetin-vastaanottimet ja DDR-muistiliitännät.
  AMD:n ja Intelin piireille käytetään valmistajan työkaluja (Vivado,
  Quartus); tämän tutoriaalin käsitteet siirtyvät niihin suoraan.
- **Järjestelmät FPGA:lla.** Suoritin, väylä ja oheislaitteet samalle
  piirille: LiteX kokoaa ne valmiista osista, ja RISC-V-ydin mahtuu
  iCE40UP5K:hon. Taito *SoC-integraatio* käsittelee väylät ja
  osien liittämisen.
- **ASIC.** FPGA on usein piirin prototyyppi. Taito *ASIC-toteutus*
  vie saman RTL:n standardisoluiksi ja valmistukseen.
- **Muut kuvauskielet.** Amaranth (Python), Chisel (Scala) ja
  SpinalHDL tuottavat Verilogia, joka kulkee saman vuon läpi.

## Lähteet ja lisälukemista

- Lattice Semiconductor: *iCE40 UltraPlus Family Data Sheet*
  (FPGA-DS-02008). Piirin resurssit, PLL:n rajat ja IO-ominaisuudet.
- Lattice Semiconductor: *iCE40 sysCLOCK PLL Design and Usage Guide*
  ja *Memory Usage Guide for iCE40 Devices*. PLL:n ja lohko-RAMin
  käyttö.
- Lattice Semiconductor: *iCE Technology Library*. Primitiivit
  `SB_LUT4`, `SB_CARRY`, `SB_RAM40_4K`, `SB_MAC16`, `SB_PLL40_*`.
- Project IceStorm: <https://prjicestorm.readthedocs.io/>. iCE40:n
  bittivirran dokumentaatio ja työkalut `icepack`, `iceprog`,
  `icepll`.
- Yosys-käsikirja: <https://yosyshq.readthedocs.io/>. Synteesin
  komennot, `synth_ice40` ja sen vaiheet.
- nextpnr: <https://github.com/YosysHQ/nextpnr>. Sijoittelijan ja
  reitittimen dokumentaatio ja algoritmit.
- iCEBreaker: <https://github.com/icebreaker-fpga/icebreaker>.
  Kortin kytkentäkaavio ja esimerkit.
- P. Chu: *FPGA Prototyping by SystemVerilog Examples*. Wiley.
  Käytännön FPGA-suunnittelu esimerkkien kautta.
- C. Cummings: *Clock Domain Crossing (CDC) Design & Verification
  Techniques Using SystemVerilog*. SNUG 2008. Tahdistimet ja
  asynkroninen FIFO.
- AMD: *UltraFast Design Methodology Guide for FPGAs and SoCs*
  (UG949). Koodaustyyli, rajoitteet ja ajoituksen sulkeminen suurissa
  FPGA:issa.
- L. McMurchie, C. Ebeling: *PathFinder: A Negotiation-Based
  Performance-Driven Router for FPGAs*. FPGA '95. Luvun 5
  reititysalgoritmi.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0).
