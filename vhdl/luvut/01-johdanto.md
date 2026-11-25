# Johdanto {.runko-johdanto}

VHDL (*VHSIC Hardware Description Language*) on laitteistonkuvauskieli,
jolla digitaalinen piiri kuvataan rekisterinsiirtotasolla (RTL) ja
simuloidaan ennen kuin siitä tehdään FPGA-konfiguraatio tai
mikropiiri. Tämä tutoriaali opettaa synteesikelpoisen VHDL:n ja
itsetarkistavat testipenkit VHDL-2008-standardin mukaisesti.

## Esitiedot ja rajaus

Esitietona on taito *Digitaalitekniikka*: Boolen algebra, kiikut,
tilakoneet ja lukujärjestelmät oletetaan tutuiksi. Luku 10 olettaa
lisäksi Pythonin perusteet (*Ohjelmoinnin perusteet (Python)*); sen
voi ohittaa.

Tämä tutoriaali keskittyy siihen, mikä on VHDL:lle ominaista: vahvaan
tyypitykseen, signaalien ja muuttujien eroon, deltasykleihin,
paketteihin, muistien kuvaamiseen ja kielen omiin sudenkuoppiin.
Laitteistoperusteet kerrotaan vain sen verran, että esimerkit ovat
ymmärrettäviä. Muu käsitellään omissa taidoissaan:

- kieliriippumaton RTL-ajattelu, kuten synkroninen suunnittelu,
  ajoitus, liukuhihnat ja vastapaine, nollausstrategiat ja
  kellotusalueiden ylitys: *RTL-suunnittelu SystemVerilogilla*
- verifiointimenetelmät (satunnaistus, kattavuus, väittämät, formaali
  verifiointi): *Laitteiston verifiointi*
- synteesi, sijoittelu ja ajoitusanalyysi: *FPGA-toteutus*.

## Historia ja standardit

VHDL syntyi Yhdysvaltain puolustusministeriön VHSIC-ohjelmassa
1980-luvun alussa. Tarkoitus oli dokumentoida hankittujen piirien
toiminta yksiselitteisesti, ja simuloinnista ja synteesistä tuli
kielen pääkäyttö vasta myöhemmin. Kielen syntaksi on lainattu Adasta,
mikä näkyy vahvana tyypityksenä, paketteina ja pitkinä avainsanoina.

| Vuosi | Standardi | Keskeistä |
|-------|-----------|-----------|
| 1987 | IEEE 1076-1987 | ensimmäinen standardi |
| 1993 | IEEE 1076-1993 | nykyisen syntaksin perusta, `std_logic_1164` (IEEE 1164) |
| 1997 | IEEE 1076.3 | `numeric_std`: `signed` ja `unsigned` |
| 2002 | IEEE 1076-2002 | suojatut tyypit (`protected`) |
| 2008 | IEEE 1076-2008 | `process (all)`, geneeriset tyypit ja paketit, `std.env`, `to_string`, rajoittamattomat tietueet ja taulukot, PSL |
| 2019 | IEEE 1076-2019 | liitäntänäkymät (`view`), parannuksia rajapintoihin ja testipenkkeihin |

Työkalujen tuki VHDL-2008:lle on nykyään hyvä: GHDL, nvc, Questa,
Riviera-PRO, Vivado ja Quartus Pro tukevat sen keskeiset piirteet.
VHDL-2019:n tuki on vielä osittaista, joten tämä tutoriaali käyttää
VHDL-2008:aa ja mainitsee 2019:n parannukset erikseen.

## Mihin VHDL:ää käytetään

VHDL ja SystemVerilog ovat kaksi rinnakkaista teollisuusstandardia.
VHDL on vahvoilla

- Euroopassa, myös Suomessa, sekä teollisuudessa että opetuksessa
- ilmailu- ja avaruuselektroniikassa sekä puolustusteollisuudessa,
  joissa sertifiointi (esim. DO-254) suosii kieltä, jonka tyypitys
  estää virheitä jo käännösvaiheessa
- FPGA-suunnittelussa: valmistajien IP-lohkoissa ja esimerkeissä
  VHDL on yhtä yleinen kuin Verilog.

SystemVerilog on yleisempi ASIC-suunnittelussa ja erityisesti
verifioinnissa (UVM). Moni organisaatio käyttää molempia: RTL on
VHDL:ää ja verifiointi SystemVerilogia tai Pythonia (cocotb).
Työkalut simuloivat sekakielisiä malleja. Kielten erot ja
vastaavuudet on koottu lukuun 11.

VHDL ei sovellu algoritmien nopeaan mallinnukseen tai suuriin
verifiointiympäristöihin sellaisenaan. Korkean tason mallit
kirjoitetaan C++:lla, SystemC:llä tai Pythonilla (taito *Korkean tason
mallinnus*), ja testipenkkien apuna käytetään avoimia kirjastoja kuten
OSVVM, UVVM ja VUnit (luku 9).

## Työkalut

| Työkalu | Tyyppi | Huomioita |
|---------|--------|-----------|
| GHDL | avoin simulaattori | tämän tutoriaalin työkalu; myös synteesi (`--synth`) ja Yosys-liitäntä |
| nvc | avoin simulaattori | nopea, hyvä VHDL-2008/2019-tuki |
| Questa, Riviera-PRO | kaupalliset simulaattorit | teollisuuden vakiotyökalut, sekakielisimulointi |
| Vivado, Quartus | FPGA-valmistajien ympäristöt | synteesi, sijoittelu, ajoitusanalyysi, oma simulaattori |
| VUnit, OSVVM, UVVM | testikehykset | testien ajo, tarkistukset, satunnaistus, kattavuus |
| VSG, vhdl-ls | tyylitarkistin, kielipalvelin | koodin muotoilu ja editorin tuki |
| GTKWave, Surfer | aaltomuotojen katselu | `ghdl -r ... --wave=aallot.ghw` |

GHDL käsittelee mallin kolmessa vaiheessa, joita kaikki simulaattorit
noudattavat jossain muodossa:

```text
ghdl -a --std=08 summain.vhd testipenkki.vhd   # analyysi kirjastoon
ghdl -e --std=08 testipenkki                   # elaborointi
ghdl -r --std=08 testipenkki --wave=aallot.ghw # simulointi
```

*Analyysi* tarkistaa syntaksin ja tyypit ja tallentaa suunnitteluyksiköt
(entiteetit, arkkitehtuurit, paketit) kirjastoon, oletuksena `work`.
Tiedostot on analysoitava riippuvuusjärjestyksessä: paketti ennen sen
käyttäjiä. *Elaborointi* kokoaa hierarkian ylimmästä entiteetistä
alkaen, kiinnittää generic-parametrit ja tarkistaa esimerkiksi
signaalien ajurit. *Simulointi* ajaa mallia, kunnes tapahtumia ei enää
ole, aikaraja täyttyy tai testipenkki lopettaa sen.

## Ensimmäinen malli

Ensimmäinen esimerkki muuntaa binääriluvun Gray-koodiksi ja takaisin.
Gray-koodissa peräkkäiset arvot eroavat vain yhdellä bitillä, minkä
vuoksi sitä käytetään kiertoantureissa ja kellotusalueita ylittävissä
osoitelaskureissa.

```{.vhdl tiedosto="esimerkit/01-gray.vhd" osa="muunnin"}
```

Mallissa näkyvät VHDL:n peruspalat. `library` ja `use` tuovat
näkyviin IEEE:n standardipaketin `std_logic_1164`, jossa on
logiikkatyyppi `std_logic`. *Entiteetti* (`entity`) on piirin
ulkoinen rajapinta: generic-parametrit ja portit. *Arkkitehtuuri*
(`architecture`) on sen toteutus. Arkkitehtuurin sisällä on
*rinnakkaisia lauseita*: ensimmäinen on yksinkertainen sijoitus, toinen
prosessi, jonka sisällä lauseet suoritetaan peräkkäin. Molemmat
kuvaavat kombinaatiologiikkaa.

Testipenkki on entiteetti, jolla ei ole portteja. Se luo
testattavan yksikön (*device under test*, DUT), syöttää sille kaikki 16
arvoa ja tarkistaa jokaisen tuloksen `assert`-lauseella:

```{.vhdl tiedosto="esimerkit/01-gray.vhd" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/01-gray.odotettu"}
```

Testipenkki ei tulosta pelkkiä arvoja ihmisen tarkistettaviksi, vaan
tarkistaa ne itse. Jos `assert`-ehto ei päde, simulointi pysähtyy
virheeseen (`severity failure`), ja virhe näkyy myös
jatkuvan integraation (CI) ajossa. Tämä *itsetarkistava testipenkki*
on kaikkien tämän tutoriaalin esimerkkien malli.

## Esimerkkien testaus

Kaikki tutoriaalin koodi on peräisin hakemiston `esimerkit`
tiedostoista. Jokainen esimerkki analysoidaan ja elaboroidaan GHDL
4.1:llä valitsimilla `--std=08 --warn-error`, eli varoitukset ovat
virheitä, ja simuloidaan ylimmästä entiteetistä `testipenkki`
alkaen. Tulostetta verrataan tiedostoon, josta tekstin tulosteet on
poimittu. Esimerkit, joiden on tarkoitus olla virheellisiä, testataan
kahdella tavalla: `.ei-kaanny`-esimerkin on kaaduttava analyysissä tai
elaboroinnissa ja toimittava, kun `@virhe`-merkityt rivit poistetaan;
`.kaatuu`-esimerkin simuloinnin on päätyttävä odotettuun virheeseen.

Kehityskontti (`.devcontainer/vhdl`) sisältää GHDL:n ja makefilen.
Esimerkkejä voi ajaa myös EDA Playgroundissa tai FPGA-valmistajan
simulaattorissa, kunhan VHDL-2008 on valittuna.

## Tutoriaalin rakenne

| Luku | Sisältö |
|------|---------|
| 2 | Entiteetit, arkkitehtuurit ja hierarkia |
| 3 | Tyypit: `std_logic`, `numeric_std`, omat tyypit ja muunnokset |
| 4 | Kombinaatiologiikka: rinnakkaiset lauseet ja `process (all)` |
| 5 | Sekvenssilogiikka, signaalit, muuttujat ja deltasyklit |
| 6 | Tilakoneet |
| 7 | Generic-parametrit, `generate` ja muistit (RAM, ROM, FIFO) |
| 8 | Paketit, funktiot ja proseduurit |
| 9 | Testipenkit VHDL:llä |
| 10 | Testit Pythonilla: cocotb |
| 11 | VHDL ja SystemVerilog rinnakkain |
| 12 | Nyrkkisäännöt, jatkotaidot ja lähteet |

Kokenut SystemVerilog-suunnittelija voi aloittaa luvusta 11 ja
palata sieltä lukuihin 3 ja 5, joissa VHDL eroaa eniten.
