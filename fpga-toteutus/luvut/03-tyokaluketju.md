# Avoin työkaluketju

Luvussa käydään läpi vaiheet RTL:stä bittivirtaan ja tehdään niistä
toistettava, skriptattu vuo. Graafiset työkalut ovat hyviä
tutkimiseen, mutta tuotannossa ja CI:ssä vuo ajetaan komentoriviltä.

## Vaiheet

1. **Synteesi** (Yosys). `synth_ice40` lukee RTL:n, optimoi logiikan ja
   kuvaa sen iCE40:n primitiiveihin: `SB_LUT4`, `SB_CARRY`, kiikut
   (`SB_DFF`, `SB_DFFE`, `SB_DFFSR` …), `SB_RAM40_4K` ja valinnalla
   `-dsp` myös `SB_MAC16`. Tuloksena on netlista JSON-muodossa.
2. **Sijoittelu ja reititys** (nextpnr). Primitiivit pakataan
   logiikkasoluihin, sijoitetaan piirin paikkoihin ja kytketään
   reititysverkolla. nextpnr laskee ajoituksen ja yrittää saavuttaa
   tavoitetaajuuden (`--freq`). Tuloksena on piirin tila tekstimuodossa
   (ASC) ja raportti.
3. **Bittivirta** (`icepack`). ASC muunnetaan binääriseksi
   bittivirraksi.
4. **Lataus** (`iceprog`). Bittivirta kirjoitetaan kortin
   SPI-flashiin tai suoraan piirille.

Kuvassa on sama vuo tiedostoina: jokainen vaihe lukee edellisen
tuloksen ja kirjoittaa omansa, joten Make voi ajaa vain ne vaiheet,
joiden syötteet ovat muuttuneet.

```{.dot otsikko="iCE40:n avoin työkaluketju tiedostoineen"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.35;
  sv [label="vilkku.sv", shape=note]; pcf [label="icebreaker.pcf", shape=note];
  yosys [label="Yosys\nsynth_ice40"]; nextpnr [label="nextpnr-ice40"];
  icepack; iceprog; kortti [label="kortti", shape=box3d, style=""];
  raportti [label="raportti", shape=note, style=""];
  sv -> yosys; yosys -> nextpnr [label="vilkku.json"];
  pcf -> nextpnr; nextpnr -> icepack [label="vilkku.asc"];
  icepack -> iceprog [label="vilkku.bin"]; iceprog -> kortti;
  nextpnr -> raportti [style=dashed];
}
```

## Bittivirta Makella

Vaiheet ovat tiedostomuunnoksia, joten Make sopii niiden ajamiseen:
jokainen vaihe ajetaan uudelleen vain, jos sen lähteet muuttuvat.

```{.makefile tiedosto="esimerkit/Makefile" osa="bittivirta"}
```

nextpnr:n valinnat kertovat piirin (`--up5k`), kotelon
(`--package sg48`) ja tavoitetaajuuden. `--pcf` antaa
rajoitetiedoston, joka kytkee ylimmän tason portit nastoihin. Jos
rajoite puuttuu, nextpnr ei sijoittele suunnitelmaa: väärään nastaan
kytketty lähtö voi rikkoa kortin. Esimerkkien raporttiajoissa
käytetään valintaa `--pcf-allow-unconstrained`, joka sallii vapaan
sijoittelun, koska niitä ei ladata kortille.

Kortilla bittivirta ladattaisiin näin (iCEBreakerin FTDI-silta näkyy
USB-laitteena):

```text
iceprog rakennus/vilkku.bin
```

## Raportit

Kumpikin työkalu kertoo, mitä teki. Synteesin tilastot (`stat`)
luettelevat solutyypit, ja nextpnr:n raportti kertoo käyttöasteen ja
jokaisen kellon saavutetun maksimitaajuuden. Esimerkkien vuo ajaa
molemmat ja tallentaa raportit JSON-tiedostoina:

```{.bash tiedosto="esimerkit/tyokalut/vuo.sh" osa="vuo"}
```

`--seed` valitsee sijoittelun satunnaissiemenen (luku 5). Kiinteä
siemen tekee ajosta toistettavan. Parametrit annetaan Yosysin
komennolla `chparam`, joten samasta RTL:stä voi ajaa useita versioita
ilman lähdekoodin muutoksia.

Raportit ovat koneluettavia, joten niiden tarkistamisen voi
automatisoida. Esimerkkien apuohjelma tiivistää ne riveiksi, joita
verrataan odotettuun:

```{.python tiedosto="esimerkit/tyokalut/raportti.py"}
```

Ohjelma tulostaa tarkasti vain solutyypit, joiden määrä ei riipu
työkaluversiosta (kantoketjut, lohko-RAMit, DSP-lohkot, PLL:t).
Logiikkasolujen määrä ja Fmax tarkistetaan raja-arvoja vasten: ne
muuttuvat työkalun pienissäkin versiopäivityksissä.

## Raportin lukeminen

nextpnr:n lokissa käyttöaste näyttää tältä (vilkun vuo):

```text
Info: Device utilisation:
Info:          ICESTORM_LC:    28/ 5280     0%
Info:         ICESTORM_RAM:     0/   30     0%
Info:                SB_IO:     2/   96     2%
Info:                SB_GB:     1/    8    12%
Info:         ICESTORM_PLL:     0/    1     0%
Info:         ICESTORM_DSP:     0/    8     0%
```

ja ajoitus näin:

```text
Info: Max frequency for clock 'clk$SB_IO_IN_$glb_clk': 79.76 MHz
      (PASS at 12.00 MHz)
```

Kellon nimi kertoo, että kello tulee nastasta (`SB_IO_IN`) ja kulkee
globaalia verkkoa (`glb_clk`). Rivi `PASS` tarkoittaa, että
tavoitetaajuus saavutettiin. `FAIL` ei estä bittivirran tekemistä,
mutta piiri ei silloin toimi luotettavasti tavoitetaajuudella:
ajoitusvirhe on suunnitteluvirhe, ei varoitus.

## Simulointi vuon osana

Synteesi ei tarkista toimintaa, ja kortilla vian etsiminen on hidasta.
Siksi jokainen esimerkki simuloidaan Verilatorilla ennen synteesiä, ja
simuloinnin on mentävä läpi ennen kuin vuo ajetaan. Synteesiä varten
kirjoitettu RTL on samaa koodia, jota simuloidaan; erot (esimerkiksi
PLL, jota simulaattori ei tunne) rajataan selvästi `ifdef SYNTHESIS`
-lohkoihin (luku 7).

## Käytännössä

- **Skriptaa vuo.** Make tai skripti, ei graafisen työkalun napit.
  Skriptattu vuo on toistettava, versionhallittava ja ajettavissa
  CI:ssä.
- **Kiinnitä työkaluversiot.** Sama RTL voi tuottaa eri tuloksen eri
  versioilla. Kehityskontti tai versioitu työkalupaketti pitää vuon
  samana koneesta riippumatta.
- **Tarkista raportit automaattisesti.** Vuo, joka päättyy
  bittivirtaan mutta jonka ajoitus on rikki, on vaarallisempi kuin vuo,
  joka kaatuu. Testaa ainakin, että ajoitus täyttyy ja että tärkeät
  resurssit (RAM, DSP) päätyivät sinne, minne tarkoitit.
- **Rajoitetiedosto lähdekoodina.** PCF on yhtä tärkeä kuin RTL:
  väärä nasta voi rikkoa laitteen. Pidä se versionhallinnassa ja
  korttikohtaisena.

## Itsearviointi

- Osaat kertoa synteesin, sijoittelun, reitityksen ja bittivirran
  vaiheet ja niiden tuotokset.
- Osaat ajaa Yosysin ja nextpnr:n komentoriviltä ja tehdä niistä
  Make-vuon.
- Osaat lukea käyttöasteen ja Fmax:n nextpnr:n raportista.
- Osaat kirjoittaa PCF-rajoitteet ja kertoa, miksi ne ovat tarpeen.
