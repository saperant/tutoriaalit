# Johdanto {.runko-johdanto}

RTL-suunnittelija päättää jokaisen rekisterin, multiplekserin ja
tilakoneen tilan itse. Se antaa täyden hallinnan, mutta jokainen
arkkitehtuurin muutos – kaksi kertojaa yhden sijaan, liukuhihnan
syvyys, muistin jakaminen pankkeihin – tarkoittaa RTL:n kirjoittamista
uudelleen ja verifioinnin aloittamista alusta. *Korkean tason synteesi*
(HLS, *high-level synthesis*) siirtää nämä päätökset työkalulle:
suunnittelija kirjoittaa algoritmin C:llä tai C++:lla ja ohjaa
mikroarkkitehtuuria *direktiiveillä* eli pragmoilla, ja työkalu tuottaa
RTL:n. Sama lähde voi tuottaa pienen ja hitaan tai suuren ja nopean
toteutuksen.

HLS ei poista laitteistosuunnittelua vaan muuttaa sen muotoa. Hyvä
HLS-koodi on kirjoitettu laitteistoa ajatellen: suunnittelijan on
tiedettävä, mitä silmukasta, taulukosta ja muuttujasta syntyy, miksi
työkalu ei saavuttanut pyydettyä läpäisyä ja miten tuotettu RTL
todennetaan. Tämä tutoriaali opettaa juuri tämän.

## Käyttökohteet ja rajat

HLS sopii lohkoihin, joiden toiminta on luontevaa kuvata algoritmina:

| Sopii hyvin | Sopii huonosti |
|---------------------------|------------------------------|
| signaalinkäsittely: suotimet, FFT, korrelaattorit | protokollat, joissa jokainen jakso on määritelty (esim. DDR-ohjain) |
| kuvan- ja videonkäsittely | prosessorin liukuhihna ja välimuistiohjain |
| neuroverkkojen kiihdyttimet, matriisilaskenta | kellotoimialueiden ylitykset, asynkroninen logiikka |
| kryptografia ja pakkaus | analogiaa lähellä oleva ohjaus ja kalibrointi |
| algoritmien nopea kokeilu FPGA:lla | piirit, joiden pinta-ala on optimoitava viimeistä porttia myöten |

Rajan syy on sama kaikissa oikean sarakkeen kohdissa: niissä
suunnittelijan on päätettävä, mitä tapahtuu millä jaksolla, eikä
työkalu voi valita sitä vapaasti. Käytännössä piirissä on usein
molempia: ohjaus ja liitännät käsin kirjoitettua RTL:ää, laskenta
HLS:llä tuotettua.

## Historia ja työkalut

Ensimmäiset *käyttäytymistason synteesityökalut* (*behavioral
synthesis*) tehtiin yliopistoissa 1980-luvulla. Niiden algoritmit –
listaajoitus, voimiin perustuva ajoitus (*force-directed scheduling*,
Paulin ja Knight 1989) ja resurssien sidonta – ovat edelleen HLS:n
perusta. Synopsysin Behavioral Compiler (1994) toi menetelmän
kaupallisiin vuohin VHDL:n ja Verilogin päälle, mutta laajempi
käyttö alkoi vasta, kun lähdekieleksi tuli C ja C++.

| Työkalu | Taustaa | Lisenssi |
|----------------------|----------------------------------|--------------|
| Catapult (Siemens) | Mentor Graphics 2004, C++ ja SystemC, ASIC-vuot | kaupallinen |
| Vitis HLS (AMD) | AutoESL:n AutoPilot 2006, Vivado HLS 2012, Xilinxin FPGA:t | kaupallinen, maksuton käyttö |
| Intel HLS Compiler | Intelin FPGA:t, oneAPI | kaupallinen, maksuton käyttö |
| Stratus (Cadence) | SystemC, ASIC | kaupallinen |
| Bambu (PandA) | Politecnico di Milano, C ja C++ LLVM:n tai GCC:n kautta | GPL-3.0 |
| LegUp | Toronton yliopisto 2011, myöhemmin Microchip SmartHLS | kaupallinen |
| XLS | Google 2020, oma kieli DSLX ja C++ (XLS[cc]) | Apache-2.0 |
| Calyx ja CIRCT | välikielet ja kääntäjäinfrastruktuuri (LLVM-projekti) | Apache-2.0 |
| Dynamatic | EPFL, dynaaminen ajoitus kättelyin | Apache-2.0 |

Kaikki työkalut tekevät samat vaiheet, jotka käydään läpi luvuissa 2–4:
lähdekoodi jäsennetään ja muutetaan välikieleksi, operaatiot
*ajoitetaan* kellojaksoille, ne *sidotaan* laitteistoyksiköille ja
lopuksi tuotetaan *ohjaus* eli tilakone. Erot ovat lähdekielessä,
kohdeteknologiassa, optimoinneissa ja käyttöliittymässä.

## Työnkulku

HLS-projektin vaiheet ovat samat työkalusta riippumatta:

1. **C-simulaatio** (*C simulation*, csim): ydin käännetään tavallisella
   kääntäjällä ja ajetaan C++-testipenkillä. Tämä todentaa algoritmin
   ja on nopea, koska kyse on tavallisesta ohjelmasta.
2. **Synteesi**: HLS-työkalu tuottaa RTL:n ja raportin, joka kertoo
   latenssin, aloitusvälin ja resurssiarviot.
3. **C/RTL-yhteissimulaatio** (*co-simulation*, cosim): samat
   testivektorit ajetaan tuotetulle RTL:lle, ja tuloksia verrataan.
   Tämä todentaa, että työkalu ja suunnittelijan pragmat säilyttivät
   merkityksen.
4. **Toteutus**: RTL syntetisoidaan logiikaksi, sijoitellaan ja
   reititetään (taito *FPGA-toteutus* tai *ASIC-toteutus*), ja
   ajoitusanalyysi kertoo, saavutettiinko kellotaajuus.

## Tutoriaalin työkalu: minihls

Ubuntun pakettivarastossa ei ole HLS-työkalua, ja avoimet työkalut ovat
suuria: esimerkiksi Bambu jaetaan satojen megatavujen AppImage-pakettina,
ja sen sisäiset vaiheet ovat vaikeita seurata. Siksi esimerkit käyttävät tätä tutoriaalia varten
kirjoitettua opetustyökalua **minihls**, joka on alle 3 000 riviä
Pythonia hakemistossa `esimerkit/minihls/`. Jokainen vaihe on luettavissa
ja kokeiltavissa, ja tutoriaali näyttää vaiheiden koodia sitä mukaa,
kun aiheet tulevat vastaan.

minihls jäljittelee Vitis HLS:ää kahdessa asiassa, jotta käsitteet ja
merkinnät ovat tuttuja oikeassa työkalussa: pragmojen syntaksi on sama
(esimerkiksi
`#pragma HLS pipeline II=1`), ja tuotetun RTL:n porttien nimet ja
protokollat ovat samat (`ap_start`, `ap_done`, `a_address0`,
`x_TVALID`). Muuten minihls on tarkoituksella pieni:

| Lähdekieli | minihls | Oikeat työkalut |
|------------------------|------------------------------|------------------------------|
| tietotyypit | vain 32-bittinen `int` | mielivaltaiset leveydet (`ap_int<W>`, `ac_fixed`) |
| silmukat | `for`, vakiokierrosmäärä | myös muuttuva kierrosmäärä ja `while` |
| ehtolauseet | `if`, `?:` | myös `switch` |
| taulukot | yksiulotteiset, vakiokoko | moniulotteiset, rakenteet |
| funktiot | yksi ylin funktio | aliohjelmat, `inline`, tietovuo (`dataflow`) |
| operaatiot | yhteen-, vähennys- ja kertolasku, bittioperaatiot, siirrot, vertailut | myös jako, liukuluvut, matematiikkakirjasto |
| osoittimet | ei | rajoitetusti |

minihls ei tee liukulukuja, ajoitusta usean kellojakson operaatioille
eikä tietovuo-optimointia. Sen raportoimat viiveet ovat suuntaa-antavia
FPGA:n luokkaa, eivät minkään piirin mittauksia.

## Ensimmäinen ydin

HLS:ssä syntetisoitavaa funktiota kutsutaan *ytimeksi* (*kernel*) tai
ylimmäksi funktioksi (*top function*). Pistetulo on lyhyt mutta
sisältää jo silmukan, kaksi muistia ja kertolaskun:

```{.cpp tiedosto="esimerkit/01-mac/mac.cpp" osa="ydin"}
```

Silmukan nimiö `kertolasku:` on C++:ssa tavallinen hyppynimiö, jota
ei käytetä. HLS-työkalut nimeävät sillä silmukan raportissa, joten
kääntäjän varoitus käyttämättömästä nimiöstä kytketään pois.

Ydin testataan ensin tavallisena C++-ohjelmana. Testipenkki vertaa
ydintä standardikirjaston viitetoteutukseen ja kirjaa syötteet ja
tulokset testivektoreiksi:

```{.cpp tiedosto="esimerkit/01-mac/testi.cpp" osa="testi"}
```

Testipenkki ottaa ytimen mukaan makrolla `YDIN`, jonka vuo asettaa
lähteen nimeksi; näin sama testipenkki kelpaa saman ytimen
muunnelmille. Luokat `Tallennin` ja `Satunnainen` ovat tiedostossa
`esimerkit/yhteinen/vektorit.hpp`. Satunnaisluvut tuottaa oma
xorshift-generaattori, koska standardikirjaston jakaumat voivat antaa eri
lukuja eri toteutuksissa, eikä testivektorien saa muuttua koneen mukana.

Esimerkkien vuo on skriptissä `esimerkit/testaa.sh`. Se ajaa minihls:n,
kääntää C-testipenkin GCC:llä sanitoijien kanssa, tarkistaa tuotetun
RTL:n Verilatorin lintillä ja ajaa yhteissimulaation:

```{.bash tiedosto="esimerkit/testaa.sh" osa="asetukset"}
```

Pistetulon vuon tuloste:

```{.tuloste tiedosto="esimerkit/01-mac/odotettu"}
```

Raportin taulukossa on rivi kullekin *alueelle*. minihls jakaa funktion
alueisiin: silmukan runko on oma alueensa ja silmukoiden väliin jäävä
suoraviivainen koodi omansa (`lohko1` alustaa summan, `lohko3`
palauttaa sen). Silmukan kierros vie kaksi jaksoa (*pituus*), ja uusi
kierros alkaa kahden jakson välein (*II*, aloitusväli). Kahdeksan
kierrosta vievät siis 16 jaksoa, ja koko funktion latenssi on 19
jaksoa. Yhteissimulaatio mittasi saman latenssin, ja tulokset olivat
samat kuin C-simulaatiossa.

Luvuissa 5–7 sama ydin nopeutetaan lähes nelinkertaiseksi pragmoilla,
eikä algoritmin riviäkään muuteta.

## Rakentaminen

| Komento | Tekee |
|---------------------------|----------------------------------------|
| `make testaa` | tarkistaa tekstin viittaukset ja ajaa kaikki esimerkit |
| `make pdf` | rakentaa tämän dokumentin ja pikaoppaan |
| `make -C esimerkit 07-matriisi` | ajaa yhden esimerkin |
| `cd esimerkit; python3 -m minihls 01-mac/mac.cpp --top mac --ajoitus` | minihls käsin |

Esimerkit tarvitsevat Python 3.12:n, GCC 14:n, Verilator 5:n, Yosysin
ja ShellCheckin sekä minihls:n omaan tarkistukseen ruffin ja mypyn.
Kehityskontti on hakemistossa `.devcontainer/hls`.

## Mitä tutoriaali kattaa

| Luku | Aihe | Esimerkit |
|------|------|-----------|
| 2 | Työkalun etupää ja välikieli | jäsennys, tietovuograafi, rajoitukset |
| 3 | Ajoitus | ASAP, ALAP, listaajoitus, ketjutus |
| 4 | Sidonta ja ohjaus | yksiköiden jakaminen, tuotettu Verilog |
| 5 | Silmukat ja avaaminen | latenssi, osittainen ja täysi avaus |
| 6 | Liukuhihnoitus | aloitusväli, vaiherekisterit, takaisinkytkentä |
| 7 | Muistit ja taulukoiden jako | portit, syklinen ja lohkojako |
| 8 | Riippuvuudet muistin kautta | histogrammi, `dependence` |
| 9 | Rajapintaprotokollat | `ap_ctrl_hs`, `ap_memory`, AXI-Stream |
| 10 | Verifiointi | C-simulaatio, yhteissimulaatio, sanitoijat |
| 11 | Lopuksi | nyrkkisäännöt, työkalujen vastaavuudet, lähteet |

## Esitiedot ja rajaus

Tutoriaali olettaa taidot *Korkean tason mallinnus (SystemC/TLM)*
(C++-mallit ja bittitarkat tyypit) ja *FPGA-toteutus* (synteesi,
resurssit ja ajoitus). *RTL-suunnittelu SystemVerilogilla* opetti
tilakoneen ja datapolun sekä valid/ready-kättelyn, jotka HLS-työkalu
tuottaa tässä automaattisesti.

Rajaus seuraa työkalusta. Yhtään esimerkkiä ei ajeta kaupallisella
HLS-työkalulla, joten oikean työkalun raportteja, varoituksia ja
laatua ei tässä nähdä; ajoituksen, sidonnan, liukuhihnoituksen ja
rajapintojen periaatteet ovat samat, yksityiskohdat luetaan työkalun
ohjeesta. Kaksi oikeassa työssä keskeistä asiaa jää maininnan
varaan: mielivaltaiset bittileveydet (`ap_int`, `ap_fixed`), jotka
määräävät kertojien koon ja ketjutuksen pituuden (leveyksien valinta
on taidossa *Lukujen esitys ja kiinteän pilkun aritmetiikka*), ja
tietovuo-optimointi (`dataflow`), jossa useita ytimiä ketjutetaan
virroilla.
