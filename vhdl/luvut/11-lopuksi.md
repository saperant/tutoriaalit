# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

Tutoriaalin tärkeimmät käytännöt koottuina. Perustelut ovat
luvuissa, joihin suluissa viitataan.

1. VHDL-2008, `numeric_std`, ei Synopsysin paketteja (3).
2. Tyyppi kertoo merkityksen: `std_logic_vector` bitteinä,
   `unsigned`/`signed` lukuina, `natural range` laskureina ja
   indekseinä (3).
3. Leveydet lasketaan auki: kanto `resize`-laajennuksella, tulo
   leveyksien summana, kavennus vasta kun arvo mahtuu (3).
4. Yksi ajuri signaalille; `'Z'` vain piirin nastoissa (2, 3).
5. Kombinaatiologiikka `process (all)` -prosessilla tai rinnakkaisella
   sijoituksella; oletussijoitukset prosessin alkuun (4).
6. Kellotettu prosessi aina samalla mallilla: `process (clk)`,
   `rising_edge(clk)`, nollaus ensimmäisenä ehtona (5).
7. Rekisterit signaaleina, välitulokset muuttujina; muuttujaan
   sijoitetaan ennen lukemista (5).
8. Kelloon ei sijoiteta eikä siihen tehdä logiikkaa (5).
9. Asynkroniset tulot kahden kiikun tahdistimen kautta (5).
10. Tilat luettelotyyppinä ilman `when others` -haaraa, lähdöt
    rekistereinä (6).
11. Parametrit yhdestä lähteestä; rajoitukset tarkistetaan
    `assert`-lauseella (7).
12. Yhteiset tyypit, vakiot ja algoritmit paketteihin; funktiot
    puhtaina (8).
13. Testipenkki tarkistaa itse, mallintaa eri tavalla, satunnaistaa
    toistettavasti ja käyttää aikarajoja (9).
14. Suora entiteetti-instanssi ja nimetyt liitokset; komponentti vain
    Verilog-moduuleille ja IP-lohkoille (2).
15. Synteesin varoitukset luetaan; salvat ovat virheitä (4).

## Lähteet ja jatkolukeminen

- **IEEE 1076-2019, *IEEE Standard for VHDL Language Reference
  Manual*.** Kielen määritelmä. IEEE:n *Open Source* -ohjelma julkaisee
  standardin paketit (`numeric_std`, `fixed_pkg` ym.) avoimena
  lähdekoodina: <https://opensource.ieee.org/vasg/Packages>.
- **GHDL:n dokumentaatio** (<https://ghdl.github.io/ghdl/>) kertoo
  simulaattorin valitsimet, synteesin ja VHDL-2008:n tuen.
- **nvc** (<https://www.nickg.me.uk/nvc/>) on toinen avoin VHDL-
  simulaattori, jonka tuki VHDL-2019:lle on laajin.
- **Kirjat:** Peter Ashendenin *The Designer's Guide to VHDL* on kielen
  kattava käsikirja ja hänen ja Jim Lewisin *VHDL-2008: Just the New
  Stuff* standardin uudistusten esittely. Ricardo Jasinskin *Effective
  Coding with VHDL* käsittelee koodin laatua, tyyliä ja testattavuutta.
  Pong P. Chun *FPGA Prototyping by VHDL Examples* on käytännönläheinen
  FPGA-oppikirja.
- **VHDL-tyylioppaat:** VSG (VHDL Style Guide,
  <https://github.com/jeremiah-c-leary/vhdl-style-guide>) on
  konfiguroitava tyylitarkistin, jonka säännöt toimivat myös
  tyylioppaana.

### Testikehykset

- **VUnit** (<https://vunit.github.io>): testien ajo ja tarkistuskirjasto.
- **OSVVM** (<https://osvvm.org>): tulostaulut, väyläkomponentit,
  satunnaistus ja kattavuus.
- **UVVM** (<https://github.com/UVVM/UVVM>): verifiointikomponentit ja
  lokitus.
- **cocotb** (<https://www.cocotb.org>): testipenkit Pythonilla.

### Työkalut

- **GHDL** ja **nvc** simulointiin, **GTKWave** ja **Surfer**
  aaltomuotojen katseluun.
- **Yosys** ja **ghdl-yosys-plugin**: avoin synteesi VHDL:stä, myös
  avoimiin FPGA-työkaluketjuihin.
- **vhdl-ls** (rust_hdl): kielipalvelin editoreille.
- FPGA-valmistajien ympäristöt: AMD Vivado, Altera Quartus, Lattice
  Radiant, Microchip Libero.

### Mihin tästä eteenpäin

Taitopuussa VHDL:n rinnalla on *RTL-suunnittelu SystemVerilogilla*,
joka käsittelee laajemmin datapolut, muistit, kellot ja
kellotusalueiden ylityksen. Sieltä polku jatkuu taitoihin *Laitteiston
verifiointi*, *FPGA-toteutus* ja *EDA-työkaluketjujen automatisointi*,
jossa simulointi, synteesi ja testit ajetaan skripteillä. Kiinteän
pilkun laskenta VHDL:n `fixed_pkg`-paketilla liittyy taitoon *Lukujen
esitys ja kiinteän pilkun aritmetiikka*.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
