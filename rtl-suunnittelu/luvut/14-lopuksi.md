# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. Ajattele ensin laitteistoa: mitkä rekisterit, mikä logiikka niiden
   välissä, mikä kello. Kirjoita sitten koodi, joka kuvaa sen.
2. `always_ff` ja `<=` kiikuille, `always_comb` ja `=`
   kombinaatiologiikalle. Ei poikkeuksia.
3. Jokainen `always_comb`-lohko alkaa oletussijoituksilla.
4. Yksi kello niin pitkälle kuin mahdollista. Hidas toiminta
   tehdään sallinnalla, ei jaetulla kellolla.
5. Jokainen asynkroninen syöte ja jokainen kellotusalueen ylitys kulkee
   tunnetun tahdistusrakenteen kautta.
6. Nollaus vapautetaan tahdistettuna. Vain ohjaus nollataan, ei dataa.
7. Rajapinnat rekisteröidään ja kuvataan kättelyllä, ja latenssi
   dokumentoidaan.
8. Muistit kirjoitetaan päättelykuvioina, ja synteesiraportista
   tarkistetaan, mihin ne päätyivät.
9. Lint ilman varoituksia. Poikkeus vaiennetaan paikallisesti ja
   perustellaan.
10. Jokaisella moduulilla on itsetarkistava testipenkki ja viitemalli,
    joka on kirjoitettu eri tavalla kuin suunnitelma.

## Mallit

Tutoriaalissa esitellyt mallit ovat RTL-suunnittelijoiden yhteistä
sanastoa:

| Malli | Ongelma, jonka se ratkaisee | Luku |
|--------------------------------------|------------------------------------------|------|
| Paketti ja `function automatic` | jaetut tyypit ja toistuva kombinaatiologiikka | 3 |
| Oletussijoitukset ensin | salvat ja puutteelliset haarat | 4 |
| Viivästetyn kopion reunantunnistus | tapahtumaan reagointi ilman uutta kelloa | 5 |
| Kaksiprosessitilakone (`_d`/`_q`) | selkeä seuraavan tilan logiikka | 6 |
| FSMD | ohjauksen ja datapolun erottaminen | 6 |
| Kelvollinen/valmis-kättely | vuonohjaus lohkojen välillä | 6, 7 |
| Kellon sallinta ja tahtigeneraattori | hidas toiminta yhdellä kellolla | 7 |
| Varjorekisteri | ohjausarvon vaihto jakson rajalla | 7 |
| Liukuhihna ja kelvollisuusbitti | kellotaajuus ja läpäisy | 7 |
| Tulostaulu | latenssista riippumaton tarkistus | 7 |
| Kättelyvaihe ja skid-puskuri | vastapaine ja `valmis`-polun katkaisu | 7 |
| Ylimääräisen bitin FIFO-osoitin | täysi ja tyhjä ilman laskuria | 8 |
| W1C-rekisteri | keskeytysten kuittaus ilman kilpailua | 8 |
| Nollauksen tahdistin | turvallinen nollauksen vapautus | 9 |
| Kahden kiikun tahdistin | yksittäisen bitin ylitys | 10 |
| Pulssi tasonvaihdoksena | tapahtuman ylitys | 10 |
| Nelivaiheinen kättely | monibittisen arvon ylitys | 10 |
| Gray-koodattu osoitin | asynkroninen FIFO | 10 |
| Viitemalli ja satunnaiset syötteet | kulmatapaukset ilman käsin kirjoitettuja testejä | 13 |
| Ajuri ja monitori | rajapinnan protokolla testistä erillään | 13 |
| Mutaatio | testin tehon tarkistus | 13 |

## Jatkotaidot

- *Laitteiston verifiointi*: testipenkkien rakenne, rajoitettu
  satunnaistus, toiminnallinen kattavuus, SystemVerilog-väittämät,
  cocotb-ympäristö kerroksittain ja formaali verifiointi. Tämän
  tutoriaalin testipenkit ovat tarkoituksella yksinkertaisia.
- *FPGA-toteutus*: synteesi, sijoittelu, ajoitusrajoitteet ja
  -analyysi. Siellä nähdään, mitä tämän tutoriaalin koodista syntyy,
  ja suunnitelma ajetaan simuloidulla kortilla, jossa on ledit,
  painikkeet, sarjaportti ja näyttö.
- *SoC-integraatio*: väylät, keskeytykset ja rekisterirajapinnat, kun
  lohkoista kootaan järjestelmä.
- *RTL-suunnittelu VHDL:llä*: samat käsitteet toisella kielellä.
- *EDA-työkaluketjujen automatisointi*: työkaluvuon ohjaus Tcl- ja
  Python-skripteillä.
- *ASIC-toteutus*: sama RTL piitehtaan vuossa.

## Lähteet

Standardit ja dokumentaatio:

- IEEE 1800-2023, *IEEE Standard for SystemVerilog – Unified Hardware
  Design, Specification, and Verification Language*. Saatavilla
  maksutta IEEE GET -ohjelman kautta.
- IEEE 1364-2005, *IEEE Standard for Verilog Hardware Description
  Language*.
- Verilatorin käyttöopas ja varoitusten kuvaukset:
  <https://verilator.org/guide/latest/>
- Yosys: <https://yosyshq.net/yosys/>
- Verible-työkalut (muotoilu ja lint):
  <https://github.com/chipsalliance/verible>
- cocotb: <https://docs.cocotb.org/>
- Icarus Verilog: <https://steveicarus.github.io/iverilog/>
- sv2v (SystemVerilogista Verilog-2005:ksi):
  <https://github.com/zachjs/sv2v>

Tyylioppaat ja artikkelit:

- lowRISC, *Verilog Coding Style Guide*:
  <https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md>
- Clifford E. Cummings, *Nonblocking Assignments in Verilog
  Synthesis, Coding Styles That Kill!* SNUG 2000.
- Clifford E. Cummings, *Synthesis and Scripting Techniques for
  Designing Multi-Asynchronous Clock Designs* ja *Clock Domain
  Crossing (CDC) Design & Verification Techniques Using
  SystemVerilog*. SNUG 2001 ja 2008.
- Clifford E. Cummings, *Simulation and Synthesis Techniques for
  Asynchronous FIFO Design*. SNUG 2002.
- Clifford E. Cummings, *The Fundamentals of Efficient Synthesizable
  Finite State Machine Design using NC-Verilog and BuildGates*.
  ICU 2002.
- Clifford E. Cummings ja Don Mills, *Synchronous Resets? Asynchronous
  Resets? I am so confused! How will I ever know which to use?*
  SNUG 2002.
- Cummingsin artikkelit ovat saatavilla osoitteessa
  <http://www.sunburst-design.com/papers/>.

Kirjat:

- Stuart Sutherland, *RTL Modeling with SystemVerilog for Simulation
  and Synthesis*. Sutherland HDL, 2017. Synteesikelpoisen
  SystemVerilogin perusteos; korvaa saman tekijän vanhemman kirjan
  *SystemVerilog for Design* (2006).
- Stuart Sutherland ja Don Mills, *Verilog and SystemVerilog Gotchas*.
  Springer, 2007. Sudenkuopat esimerkkeineen.
- Sarah L. Harris ja David Money Harris, *Digital Design and Computer
  Architecture, RISC-V Edition*. Morgan Kaufmann, 2021.
  Digitaalitekniikka ja HDL rinnakkain.
- Pong P. Chu, *FPGA Prototyping by SystemVerilog Examples*.
  Wiley, 2018. Käytännön FPGA-lohkoja: UART, ajastimet, näytönohjain.
