# Johdanto {.runko-johdanto}

Verifiointi on työtä, jolla osoitetaan, että suunnitelma tekee sen,
mitä sen määrittely sanoo. Ohjelmistossa virhe korjataan päivityksellä,
mutta piirissä virhe on valmistettu piiriin: uusi maskisarja maksaa
nykyisillä valmistusprosesseilla miljoonia euroja ja viivästää tuotetta
kuukausia. FPGA:lla virheen voi korjata uudella bittivirralla, mutta
kentälle päässyt laite on silti kallis kutsua takaisin. Siksi
laitteistoprojekteissa verifiointiin käytetään tyypillisesti enemmän
työtä kuin itse suunnitteluun, ja suurissa piireissä verifioijia on
enemmän kuin suunnittelijoita.

Tämä tutoriaali opettaa verifioinnin menetelmät kahden pienen lohkon
avulla: synkronisen FIFOn ja vuorottelevan arbiterin.

## Esitiedot ja rajaus

Esitietoina ovat taidot *RTL-suunnittelu SystemVerilogilla* (moduulit,
kellotettu logiikka, FIFOt, kelvollinen/valmis-kättely, Verilator ja
cocotb:n perusteet) ja *Python työkaluohjelmointiin* (tyyppivihjeet,
ruff, mypy, pytest). Niitä ei kerrata.

Tässä keskitytään lohkotason verifiointiin. Rajauksen ulkopuolelle
jäävät:

- väyläprotokollien tarkistimet ja järjestelmätason testit, joita
  käsitellään taidossa *SoC-integraatio*
- synteesin jälkeinen ekvivalenssitarkistus ja porttitason simulointi,
  joita käsitellään taidossa *ASIC-toteutus*
- regressioiden ajaminen työkaluketjun osana, jota käsitellään
  taidossa *EDA-työkaluketjujen automatisointi*
- emulaattorit ja FPGA-prototyypit.

## Verifiointi, validointi ja testaus

Sanat menevät arkikielessä sekaisin, mutta alalla niillä on omat
merkityksensä:

| Termi | Kysymys | Esimerkki |
|-------|---------|-----------|
| verifiointi | tekeekö suunnitelma sen, mitä määrittely sanoo? | simulointi, väitteet, formaali tarkistus |
| validointi | tekeekö tuote sen, mitä käyttäjä tarvitsee? | prototyyppi, asiakastestaus |
| testaus (valmistustestaus) | onko tämä yksittäinen piiri valmistettu oikein? | testivektorit, skannausketjut |

Verifiointi tehdään ennen valmistusta suunnitelmalle, valmistustestaus
jokaiselle valmistetulle piirille. Tässä tutoriaalissa *testi*
tarkoittaa simulaatiossa ajettavaa verifiointitestiä.

## Menetelmät

Verifioinnin menetelmät jakautuvat kolmeen ryhmään, ja oikeissa
projekteissa käytetään niitä kaikkia:

1. **Simulointi.** Suunnitelmalle syötetään ärsykettä ja sen vastausta
   verrataan odotettuun. Simulointi skaalautuu koko piiriin asti,
   mutta se näkee vain ne tilanteet, jotka ärsyke tuottaa.
2. **Väitteet.** Suunnitelmaan kirjoitetaan ehtoja, joiden on oltava
   aina tosia. Simulaattori tarkistaa ne joka jaksolla, ja samat ehdot
   kelpaavat formaalille työkalulle.
3. **Formaali verifiointi.** Ratkaisija käy läpi *kaikki* syötteet ja
   tilat tiettyyn syvyyteen tai todistaa ominaisuuden kaikille
   syvyyksille. Se löytää kulmatapaukset, joita kukaan ei tullut
   ajatelleeksi, mutta toimii vain kohtuullisen kokoisille lohkoille.

Lisäksi suuria piirejä ajetaan emulaattoreilla ja FPGA-prototyypeillä,
jotta niillä voi ajaa oikeaa ohjelmistoa ennen piirin valmistusta.
Niitä ei käsitellä tässä.

## Esimerkkien lohkot

Kaikki esimerkit verifioivat kahta lohkoa. Ensimmäinen on synkroninen
FIFO, jonka lukupää näkyy suoraan lähdössä (*first-word
fall-through*). Kirjoitus hyväksytään, kun jono ei ole täynnä, ja luku,
kun jono ei ole tyhjä:

```{.systemverilog tiedosto="esimerkit/rtl/fifo.sv" osa="fifo"}
```

Toinen on neljän pyytäjän vuorotteleva arbiteri (*round-robin
arbiter*). Se myöntää vuoron yhdelle pyytäjälle kerrallaan ja siirtää
etusijan aina viimeksi palvellun pyytäjän seuraajalle, jotta kukaan ei
näänny odottamaan:

```{.systemverilog tiedosto="esimerkit/rtl/arbiteri.sv" osa="arbiteri"}
```

Molemmissa lohkoissa on `ifdef`-makroilla istutettuja vikoja. Ne
edustavat tyypillisiä RTL-virheitä: unohtunut ehto, väärä vertailu ja
väärin käsitelty samanaikainen tapahtuma.

| Makro | Lohko | Vika |
|-------|-------|------|
| `BUGI_TYHJA` | FIFO | luku tyhjästä jonosta sallitaan, määrä alivuotaa |
| `BUGI_SAMANAIKAINEN` | FIFO | samanaikainen kirjoitus ja luku kasvattaa määrää |
| `BUGI_TAYSI` | FIFO | jono ilmoittaa olevansa täynnä yhtä paikkaa liian aikaisin |
| `BUGI_KIINTEA` | arbiteri | etusija ei kierrä, pyytäjä 0 voittaa aina |
| `BUGI_KAKSI` | arbiteri | kun kaikki pyytävät, kaksi saa myönnön |

Jokainen luku näyttää, mitkä viat sen menetelmä löytää ja mitkä jäävät
huomaamatta. Istutetut viat ovat itsessään verifioinnin menetelmä:
jos testi ei löydä tunnettua vikaa, se tuskin löytää tuntemattomiakaan
(luku 2).

## Työkalut

| Tehtävä | Tässä | Kaupallisia ja muita |
|---------|-------|----------------------|
| SystemVerilog-simulointi | Verilator 5.020 | Questa, VCS, Xcelium, Riviera-PRO |
| Simulaattori cocotbille | Icarus Verilog 12 | Verilator, Questa, Xcelium, GHDL |
| Python-testipenkit | cocotb 2.1 | pyuvm, PyVSC |
| Formaali tarkistus | Yosys 0.33, yosys-smtbmc, Z3 | SymbiYosys, Jasper, VC Formal, Questa Formal |
| Kattavuus | Verilator `--coverage`, oma Python-malli | simulaattorien kattavuustietokannat (UCIS) |

Kaikki ovat Ubuntu 24.04:n paketteja, paitsi cocotb, joka asennetaan
pipillä. Kehityskontti (`.devcontainer/verifiointi`) sisältää ne.
Verilator kääntää SystemVerilogin C++:ksi ja on nopea, mutta se tukee
SystemVerilogin verifiointipiirteistä vain osaa: luokkien
satunnaistusrajoitteita ja suurinta osaa sekvenssisyntaksista ei voi
käyttää. Kaupallisilla simulaattoreilla ne toimivat. Tutoriaali kertoo
kunkin rajoituksen kohdalla, miten sen voi kiertää ja miltä täysi
syntaksi näyttäisi.

## Esimerkkien ajaminen

Esimerkit ovat yksi kokonaisuus, jonka `esimerkit/Makefile` ajaa:

```text
make -C esimerkit              # kaikki esimerkit, tulosteet verrataan
make -C esimerkit penkki-taysi # yksi esimerkki
make -C esimerkit siivoa       # poistaa rakennus/-hakemiston
```

Jokainen kohde ajaa simulaation, formaalin tarkistuksen tai työkalun ja
vertaa tulosteen tiedostoon `odotetut/<kohde>.odotettu`
(`tyokalut/vertaa.py`). Kohteet, joiden nimessä on vian nimi, kääntävät
lohkon makrolla `BUGI_*`, ja niiden *on* epäonnistuttava: jos vika
ei löydy, kohde epäonnistuu. Kaikki ajot ovat deterministisiä, koska
satunnaisuus tulee kiinteistä siemenistä. Siksi kirjan tulosteet ovat
täsmälleen ne, jotka `make` tuottaa.

## Ensimmäinen testi

Yksinkertaisin testipenkki on *ohjattu testi* (directed test):
käsin kirjoitettu ärsykesarja ja tarkistukset. Apuaskare kirjaa
epäonnistuneen tarkistuksen:

```{.systemverilog tiedosto="esimerkit/01-ohjattu/testipenkki.sv" osa="tarkista"}
```

Testi täyttää FIFOn neljällä arvolla, tarkistaa liput ja lukee arvot
takaisin. Ärsyke vaihdetaan kellon laskevalla reunalla, jotta se on
vakaa nousevalla reunalla, jolla FIFO sen näkee:

```{.systemverilog tiedosto="esimerkit/01-ohjattu/testipenkki.sv" osa="testi"}
```

Ehjä FIFO läpäisee testin:

```{.tuloste tiedosto="esimerkit/odotetut/ohjattu.odotettu"}
```

Alla oleva ajoituskaavio on piirretty saman ajon aaltomuodosta (`make
kaavio-ohjattu`). Kukin sarake on yksi kellojakso, ja arvot näkyvät
sellaisina kuin ne ovat nousevan reunan jälkeen. Siksi `maara` kasvaa
samassa sarakkeessa, jossa `push` on ylhäällä: kirjoitus hyväksyttiin
sarakkeen alun reunalla. `dout` näyttää jonon ensimmäisen arvon heti,
koska lukupää näkyy suoraan lähdössä.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/ohjattu.json" otsikko="Ohjattu testi simulaatiosta: neljä kirjoitusta ja neljä lukua"}
```

Kun FIFO käännetään makrolla `BUGI_TAYSI`, testi löytää vian kahdesta
kohdasta: määrä jää kolmeen, koska neljäs kirjoitus hylättiin, ja
neljäs luettu arvo on väärä. Lopun `$error` saa Verilatorin
lopettamaan simulaation virhekoodilla, jonka `make` tunnistaa:

```{.tuloste tiedosto="esimerkit/odotetut/ohjattu-taysi.odotettu"}
```

Sama testi ei kuitenkaan löydä vikaa `BUGI_SAMANAIKAINEN`, koska se ei
koskaan kirjoita ja lue samalla jaksolla:

```{.tuloste tiedosto="esimerkit/odotetut/ohjattu-samanaikainen.odotettu"}
```

Tämä on koko tutoriaalin lähtökohta. Ohjattu testi tarkistaa vain ne
tilanteet, jotka sen kirjoittaja keksi. Seuraavat luvut rakentavat
menetelmiä, jotka tuottavat tilanteita automaattisesti (satunnaistus),
mittaavat, mitä on tarkistettu (kattavuus), valvovat sääntöjä joka
jaksolla (väitteet) ja käyvät läpi kaikki mahdollisuudet (formaali
tarkistus).

## Lukuohje

Luku 2 kertoo, miten verifiointi suunnitellaan. Luvut 3–6 rakentavat
simulointiin perustuvan testipenkin: rakenne SystemVerilogilla
(luku 3), sama ympäristö Pythonilla cocotb:n avulla (luku 4),
satunnaistus (luku 5) ja kattavuus (luku 6). Luvut 5 ja 6 käyttävät
luvun 4 Python-ympäristöä, joten ne luetaan tässä järjestyksessä.
Luku 7 esittelee SystemVerilogin väitteet ja luku 8 formaalin
verifioinnin. Luku 9 käy läpi alan standardimenetelmän UVM:n käsitteet
ja luku 10 regressiot ja epäonnistumisten luokittelun. Luku 11 kokoaa
nyrkkisäännöt ja lähteet.

Kokenut lukija voi aloittaa luvuista 7 ja 8, jos testipenkkien rakenne
on tuttu, ja lukea muiden lukujen lopussa olevat itsearvioinnit.
