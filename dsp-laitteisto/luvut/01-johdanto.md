# Johdanto {.runko-johdanto}

Taito *Digitaalinen signaalinkäsittely* suunnitteli suotimia SciPyllä
ja toteutti ne C:llä. Prosessori laskee näytteen kerrallaan, ja jos se
ei ehdi, valitaan nopeampi prosessori. Laitteistossa raja tulee
vastaan eri tavalla: 100 MHz:n näytetaajuudella yhdelle näytteelle
jää 10 ns, eikä mikään prosessori laske siinä ajassa 64 kertoimen
suodinta. FPGA tai ASIC laskee sen, koska kertolaskut tehdään
rinnakkain omilla kertojillaan ja jokainen välitulos on juuri niin
leveä kuin tarvitaan.

Tämä tutoriaali kääntää algoritmin laitteistoksi. Työ ei ole
käännöstä samassa mielessä kuin C:stä konekieleksi. Suunnittelija
päättää jokaisen bitin: kuinka leveä on kerroin, kuinka monta bittiä
summa kasvaa, missä pyöristetään ja mitä tapahtuu ylivuodossa. Hän
päättää myös rakenteen: kuinka monta kertojaa on ja kuinka monta
kellojaksoa näytteeseen saa kulua. Samat päätökset tehdään jokaiselle
lohkolle, joten luvut etenevät lohko kerrallaan: FIR, IIR, CORDIC,
numeerisesti ohjattu oskillaattori, CIC ja polyfaasisuodin.

## Työnkulku

Jokainen lohko kulkee saman polun:

| Vaihe | Väline | Tulos |
|-------|--------|-------|
| suunnittelu | SciPy, liukuluvut | kertoimet ja vaatimukset |
| kvantisointi | Python, kokonaisluvut | kertoimet ja sanaleveydet |
| bittitarkka malli | Python, kokonaisluvut | referenssi jokaiselle bitille |
| RTL | SystemVerilog | rakenne: kertojat, rekisterit, ohjaus |
| verifiointi | cocotb ja Icarus, Verilator | RTL = malli bitilleen |
| toteutus | Yosys, nextpnr | resurssit ja kellotaajuus |

Tärkein välivaihe on **bittitarkka malli**. Se laskee
kokonaisluvuilla täsmälleen saman kuin RTL, jokaista pyöristystä ja
saturaatiota myöten. Mallin avulla sanaleveydet valitaan ennen RTL:n
kirjoittamista, ja RTL:n testaus muuttuu yksinkertaiseksi: jokaisen
ulostulon on oltava sama kuin mallin, ei vain "lähellä". Lähellä
oleminen ei riitä, koska väärä pyöristys tai unohtunut saturaatio
näkyy usein vain virheenä viimeisessä bitissä tai harvinaisella
sisääntulolla. Luvussa 9 nähdään, että taajuusvastemittaus ei
huomaa väärää pyöristystä lainkaan, mutta bittitarkka vertailu
huomaa sen ensimmäisessä näytteessä.

## Esitiedot ja rajaus

Tutoriaali olettaa seuraavat taidot:

- *Digitaalinen signaalinkäsittely*: FIR- ja IIR-suunnittelu,
  toisen asteen lohkot, polyfaasihajotelma, Q15-laskenta C:llä.
  Suunnittelumenetelmiä ei toisteta.
- *Lukujen esitys ja kiinteän pilkun aritmetiikka*: Q-merkintä, bittikasvu,
  pyöristystavat, saturaatio ja SQNR. Tässä käytetään samaa
  merkintää: **Qm.n** on etumerkillinen luku, jossa on $m$
  kokonaisbittiä etumerkki mukaan lukien ja $n$ murtobittiä.
- *Laitteiston verifiointi*: testipenkin rakenne, cocotb,
  satunnaistus ja siemenet.
- *FPGA-toteutus*: Yosys, nextpnr, ajoitusraportit ja
  resurssien jakaminen. Siellä jaettiin yksi kertoja neljän kertoimen
  suotimessa; tässä aihe viedään pidemmälle.

Läheisiä taitoja ovat *RTL-suunnittelu SystemVerilogilla*
(valid/ready-kättely ja liukuhihnat), *Korkean tason synteesi* (sama
työ tehtynä C++:sta työkalun avulla) ja *Korkean tason mallinnus
(SystemC/TLM)* (SystemC:n `sc_fixed`-tyypit vastaavat tämän tutoriaalin
Python-malleja).

Tutoriaali rajautuu yksittäisiin lohkoihin, joista vastaanottimen
datapolku kootaan. Lohkoja ei kytketä tässä kokonaiseksi ketjuksi
(digitaalinen alassekoitin on taidon *Ohjelmistoradio* aihe
ohjelmistona), eikä FFT:tä käsitellä: sen rakenteet (iteratiivinen ja
liukuhihnoitettu perhonen, vaiheittainen skaalaus) ansaitsisivat oman
lukunsa, ja samat periaatteet (bittikasvu, liukuhihna vastaan jaettu
kertoja, lohko-RAM) opitaan tämän tutoriaalin lohkoista.

## Esimerkit

Kaikki koodi on hakemistossa `esimerkit/`, ja `make` ajaa sen:

| Hakemisto | Sisältö |
|-----------|---------|
| `malli/` | bittitarkat mallit Pythonilla ja kertoimet |
| `rtl/` | SystemVerilog-toteutukset ja generoidut vakiot |
| `penkit/` | cocotb-testipenkit ja niiden ajaja |
| `verilator/` | Verilatorin C++-testipenkki pitkille ajoille |
| `testit/` | mallin omat pytest-testit |
| `analyysit/` | sanaleveyksien ja tarkkuuden analyysit |
| `synteesi/`, `tyokalut/` | synteesikääre, synteesivuo ja raportit |
| `odotetut/`, `raportit/` | tulosteet, joihin ajoja verrataan |

Lohkoilla on sama liitäntä: sisääntulo ja ulostulo ovat virtoja,
joissa näyte siirtyy, kun `valid` ja `ready` ovat molemmat ykkösiä
kellon nousevalla reunalla. Liitäntä esitellään luvussa 3 ja
vastapaineen käsittely luvussa 8.

## Ensimmäinen ajo

Kahdeksan kertoimen alipäästösuotimen RTL ajetaan cocotb-testipenkissä
ja jokainen ulostulo verrataan malliin:

```text
make -C esimerkit cocotb-fir-suora
```

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fir-suora.odotettu"}
```

Testisarjassa on viisi testiä: impulssi, täysi askel, pahin
mahdollinen sisääntulo, satunnainen sisääntulo ja taajuusvaste.
Jokaisessa näytteet syötetään satunnaisin tauoin ja ulostulon
vastaanottaja pitää satunnaista vastapainetta, joten myös liitännän
ohjaus tulee testatuksi. Rivi "saturaatio vaikuttaa 30" kertoo, että
testi todella vie suotimen ylivuotoon: 30 ulostulossa saturoiva ja
kiertävä toteutus antaisivat eri tuloksen. Taajuusvasteen rivit
näyttävät mallin ja RTL:n vahvistuksen neljällä taajuudella.

Sama tulostemuoto toistuu jokaisen lohkon kohdalla luvuissa 3–8, ja
sen lukemiseen riittää tämä kuvaus: "bittitarkasti" tarkoittaa, että
jokainen RTL:n ulostulo oli sama kokonaisluku kuin mallin. Testipenkin
rakenne (ajuri, vastaanottaja ja vertailu) avataan luvussa 9.

## Työkalut

Esimerkit käyttävät Ubuntu 24.04:n paketteja: Icarus Verilog 12,
Verilator 5.020, Yosys 0.33 ja nextpnr-ice40. Pythonin paketeista
tarvitaan cocotb 2.1, NumPy, SciPy 1.18, pytest, ruff ja mypy.
Kehityskontti `.devcontainer/dsp-laitteisto` sisältää ne.

cocotb-testit ajetaan Icarus Verilogilla, koska cocotb 2 tukee
Verilatoria vasta versiosta 5.036 alkaen. Verilatoria käytetään
lintiin ja nopeaan C++-testipenkkiin, joka ajaa 100 000 näytettä
sekunnin murto-osassa. FPGA-esimerkit syntetisoidaan Lattice iCE40
UP5K -piirille, jossa on kahdeksan 16 × 16 -bitin kertojalohkoa.

Kuvaajat (spektrit, taajuusvasteet ja askelvasteet) piirtää
`kuvat/piirra.py` samoilla malleilla ja analyyseillä, joihin testit
vertaavat RTL:n ulostulon. Komento `make kuvat` tuottaa ne uudelleen,
joten parametreja voi muuttaa ja katsoa, mitä kuvalle tapahtuu.

## Lukuohje

Luku 2 rakentaa bittitarkan mallin ja valitsee sanaleveydet. Luvut
3 ja 4 toteuttavat FIR- ja IIR-suotimet, luvut 5 ja 6 CORDICin ja
oskillaattorin, ja luku 7 monitaajuusrakenteet. Luku 8 käsittelee
liukuhihnoitusta, vastapainetta ja resurssien jakamista, luku 9
verifiointia ja luku 10 FPGA-toteutuksen resursseja ja ajoitusta.
Luku 11 kokoaa nyrkkisäännöt ja lähteet.

Kokenut lukija voi aloittaa luvuista 2 ja 9 ja lukea lohkoluvuista
ne, joita tarvitsee. Jokaisen luvun lopussa on itsearviointi.
