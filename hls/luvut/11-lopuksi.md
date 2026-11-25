# Lopuksi {.runko-lahteet}

## Työnkulku

Kokenut HLS-suunnittelija etenee samassa järjestyksessä kuin tämän
tutoriaalin luvut, ja jokaisen vaiheen jälkeen ajetaan
yhteissimulaatio:

1. **Oikea C++ ensin.** Ydin ja testipenkki, viitemalli ja sanitoijat.
   Älä lisää pragmoja ennen kuin C-simulaatio menee läpi.
2. **Lähtötaso.** Syntetisoi ilman pragmoja ja kirjaa latenssi ja
   resurssit. Lähtötaso on vertailukohta kaikille muutoksille.
3. **Liukuhihnoita sisimmät silmukat** ja tavoittele II = 1.
4. **Poista II:n esteet** raportin syyn mukaan: muistiportit jakamalla
   taulukoita, takaisinkytkennät kirjoittamalla laskenta uudelleen.
5. **Avaa**, kun muistikaista ja pinta-ala sen sallivat.
6. **Rajapinnat** järjestelmän mukaan, ja testi vastapaineella.
7. **Toteutus** ja ajoitusanalyysi: raportin arviot eivät korvaa
   sijoittelun ja reitityksen tuloksia.

## Nyrkkisäännöt

| Tilanne | Sääntö |
|------------------------------------|------------------------------------|
| II on suurempi kuin pyydettiin | lue syy: resurssi, muistiportti vai takaisinkytkentä |
| syy on muistiportti | jaa taulukko käyttötavan mukaan (`cyclic`, `block`, `complete`) |
| syy on muuttuja | lyhennä ketjua, siirrä laskenta takaisinkytkennän ulkopuolelle |
| syy on taulukko (kirjoitus → luku) | jaa riippuvuus (osahistogrammit, välitys), älä ohita sitä |
| liikaa kertojia | `allocation`, pidempi kellojakso tai vähemmän avausta |
| avaus ei nopeuttanut | muistikaista ei riitä: jaa taulukot |
| latenssi suuri, II = 1 | liukuhihnan täyttö toistuu: litistä silmukat |
| RTL ei vastaa C-simulaatiota | pragma väärin, määrittelemätöntä käytöstä tai työkaluvirhe |
| kellotaajuus ei toteudu | kasvata epävarmuutta, lyhennä ketjutusta |

## Pragmat eri työkaluissa

Käsitteet ovat samat kaikissa työkaluissa, mutta syntaksi vaihtelee.
Taulukko näyttää yleisimmät vastaavuudet; työkalujen käyttöoppaat ovat
lähteissä.

| Käsite | Vitis HLS (ja minihls) | Intel HLS Compiler | Catapult ja XLS[cc] |
|------------------------|----------------------------|----------------------------|----------------------------|
| liukuhihnoitus | `pipeline II=1` | `#pragma ii 1` | `hls_pipeline_init_interval 1` |
| avaus | `unroll factor=4` | `#pragma unroll 4` | `hls_unroll yes` |
| taulukon jako | `array_partition` | attribuutti `hls_numbanks` | direktiivi tai muistiasetus |
| riippuvuus pois | `dependence ... false` | `#pragma ivdep` | direktiivi |
| yksiköiden raja | `allocation` | – | direktiivi |
| silmukoiden litistys | `loop_flatten` | `#pragma loop_coalesce` | direktiivi |
| virta | `hls::stream<T>` | `ihc::stream_in<T>` | `ac_channel<T>` |
| mielivaltainen leveys | `ap_int<W>`, `ap_fixed` | `ac_int<W>`, `ac_fixed` | `ac_int<W>`, `ac_fixed` |

## minihls:n rakenne

Jokaisen vaiheen koodia voi lukea ja muuttaa. Hyviä harjoituksia ovat
uuden operaation lisääminen, rekisterien jakaminen left-edge-
algoritmilla, silmukoiden litistäminen ja ajoitus usean jakson
operaatioille.

| Tiedosto | Vaihe | Luku |
|------------------------|------------------------------|------|
| `jasennin.py`, `puu.py` | sanasto, jäsennys, jäsennyspuu | 2 |
| `muunnokset.py` | silmukoiden avaus, alueet | 5 |
| `dfg.py` | tietovuograafi, if-conversion, riippuvuudet | 2, 8 |
| `ajoitus.py` | ASAP, ALAP, listaajoitus, modulo-ajoitus | 3, 6 |
| `sidonta.py` | kertojien jakaminen, vaiherekisterit | 4, 6 |
| `verilog.py` | tilakone, datapolku, rajapinnat | 4, 6, 9 |
| `testipenkki.py` | yhteissimulaation testipenkki | 10 |
| `raportti.py`, `__main__.py` | raportti, vuo | 1 |

## Jatkotaidot

Taitopuussa tämä taito on polun päässä, mutta luontevia seuraavia
taitoja on useita:

- *DSP-algoritmien laitteistototeutus*: samat suotimet ja rakenteet
  käsin kirjoitettuna RTL:nä; vertailukohta sille, mitä HLS tuottaa.
- *SoC-integraatio*: HLS:n tuottaman ytimen liittäminen väylään ja
  rekisterirajapintaan.
- *ASIC-toteutus*: sama RTL piirinä, jossa pinta-ala ja ajoitus
  mitataan toteutuksesta eikä työkalun arviosta.
- *Laitteiston verifiointi*: yhteissimulaation jälkeen tulevat
  kattavuus ja formaalit menetelmät.

## Lähteet

Työkalujen dokumentaatio:

- AMD: *Vitis High-Level Synthesis User Guide* (UG1399). Pragmojen,
  rajapintojen ja raporttien täydellinen kuvaus.
  <https://docs.amd.com/r/en-US/ug1399-vitis-hls>.
- Intel: *Intel High Level Synthesis Compiler Pro Edition: Reference
  Manual*. <https://www.intel.com/content/www/us/en/docs/programmable/>.
- Siemens EDA: *Catapult High-Level Synthesis* ja Algorithmic C
  -tietotyypit (`ac_int`, `ac_fixed`, `ac_channel`, Apache-2.0).
  <https://github.com/hlslibs/ac_types>.
- PandA-Bambu: avoin HLS-työkalu. <https://panda.dei.polimi.it/>.
- XLS: Accelerated HW Synthesis. <https://google.github.io/xls/>.
- Calyx ja CIRCT: <https://calyxir.org/>, <https://circt.llvm.org/>.
- Dynamatic: <https://github.com/EPFL-LAP/dynamatic>.
- Arm: *AMBA AXI-Stream Protocol Specification* (IHI 0051) ja *AMBA
  AXI Protocol Specification* (IHI 0022).
  <https://developer.arm.com/documentation/>.
- Verilator ja Yosys: <https://verilator.org/guide/latest/>,
  <https://yosyshq.readthedocs.io/>.

Kirjat:

- Kastner, R., Matai, J. ja Neuendorffer, S.: *Parallel Programming
  for FPGAs*. 2018. Vapaasti saatavilla:
  <https://kastner.ucsd.edu/hlsbook/>.
- Coussy, P. ja Morawiec, A. (toim.): *High-Level Synthesis: From
  Algorithm to Digital Circuit*. Springer, 2008.
- De Micheli, G.: *Synthesis and Optimization of Digital Circuits*.
  McGraw-Hill, 1994. Ajoituksen ja sidonnan klassinen oppikirja.
- Gajski, D., Dutt, N., Wu, A. ja Lin, S.: *High-Level Synthesis:
  Introduction to Chip and System Design*. Kluwer, 1992.

Artikkelit:

- Paulin, P. G. ja Knight, J. P.: Force-directed scheduling for the
  behavioral synthesis of ASICs. *IEEE Transactions on Computer-Aided
  Design* 8(6), 1989.
- Rau, B. R.: Iterative modulo scheduling: an algorithm for software
  pipelining loops. *MICRO-27*, 1994.
- Cong, J. ja Zhang, Z.: An efficient and versatile scheduling
  algorithm based on SDC formulation. *DAC*, 2006.
- Nane, R. et al.: A survey and evaluation of FPGA high-level synthesis
  tools. *IEEE Transactions on Computer-Aided Design* 35(10), 2016.
- Nigam, R. et al.: A compiler infrastructure for accelerator generators
  (Calyx). *ASPLOS*, 2021.

Tämä tutoriaali on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
-lisenssillä (CC BY-SA 4.0). Esimerkkikoodit ja minihls ovat saman
lisenssin alaisia.
