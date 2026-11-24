# Johdanto {.runko-johdanto}

ASIC (application-specific integrated circuit) on yhteen tehtävään
valmistettu mikropiiri. Sama RTL, joka FPGA:ssa ohjelmoidaan valmiiseen
logiikkamatriisiin, muutetaan ASIC-toteutuksessa transistoreiksi ja
metallijohtimiksi, joista valmistaja tekee piikiekolle oman piirin.
Tulos on FPGA:ta moninkertaisesti nopeampi, pienempi ja
energiatehokkaampi, mutta virhettä ei voi korjata ohjelmoimalla
uudelleen: uusi maskisarja maksaa satoja tuhansia tai miljoonia euroja
ja kuukausia.

Tämä taito käy läpi, mitä RTL:lle tapahtuu matkalla piiriksi ja mitä
suunnittelijan on tiedettävä jokaisessa vaiheessa. Esitietona on taito
*RTL-suunnittelu SystemVerilogilla*; synkroninen suunnittelu,
kellotusalueiden ylitys ja synteesikelpoinen koodaustyyli oletetaan
tutuiksi. *Digitaalitekniikka* on käsitellyt portit, ajoitusyhtälöt ja
kriittisen polun; tässä ne viedään oikean solukirjaston ja
työkaluvuon tasolle.

## Toteutusvuo

ASIC-vuo etenee vaiheittain, ja jokainen vaihe tarkistetaan ennen
seuraavaa:

| Vaihe | Tulos | Tarkistus |
|-------|-------|-----------|
| Spesifikaatio ja arkkitehtuuri | lohkot, rajapinnat, PPA-tavoitteet | katselmointi, mallit |
| RTL | Verilog/VHDL | simulointi, lint, formaali verifiointi |
| Synteesi | porttitason netlista | ekvivalenssi, STA |
| DFT | scan-ketjut, BIST, JTAG | vikakattavuus |
| Pohjapiirros | ytimen koko, IO, makrot, tehoverkko | IR-arvio |
| Sijoittelu | solujen paikat | ruuhka, STA |
| Kellopuu (CTS) | puskuroitu kelloverkko | vinous, STA |
| Reititys | metallit ja läpiviennit | DRC, STA |
| Sign-off | lopullinen GDSII | DRC, LVS, STA, IR, EM |
| Tapeout ja valmistus | kiekot, kotelointi | tuotantotesti |

Vuo ei ole suora putki. Kun tarkistus epäonnistuu, palataan
aiempaan vaiheeseen, kuten kuvan katkoviivat näyttävät: ajoitusrike
sijoittelun jälkeen voi vaatia uutta synteesiä tai jopa RTL:n
muutosta, ja jokainen kierros on sitä kalliimpi, mitä myöhemmin se
alkaa.

```{.dot otsikko="ASIC-vuon vaiheet ja tyypilliset paluut taaksepäin"}
digraph {
  rankdir=TB; nodesep=0.3; ranksep=0.35;
  rtl [label="RTL"]; syn [label="synteesi"]; dft [label="DFT"];
  fp [label="pohjapiirros"]; pl [label="sijoittelu"];
  cts [label="kellopuu"]; rt [label="reititys"]; so [label="sign-off"];
  gds [label="GDSII", shape=note, style=""];
  {rank=same; rtl; syn; dft; fp}
  {rank=same; pl; cts; rt; so; gds}
  rtl -> syn -> dft -> fp;
  fp -> pl;
  pl -> cts -> rt -> so -> gds;
  edge [style=dashed, color="#B04848", fontcolor="#B04848"];
  so -> pl [label="ajoitus"];
  pl -> syn [label="ruuhka"];
  syn -> rtl [label="ei ajoitu"];
}
```

Tavoitteet ilmaistaan lyhenteellä PPA: teho (power), suorituskyky
(performance) ja pinta-ala (area). Ne vetävät eri suuntiin: nopeampi
summain on suurempi (luku 3), ja kellon portitus säästää tehoa mutta
lisää logiikkaa (luku 9).

## ASIC vai FPGA

Valinta on lähes aina taloudellinen. ASIC-projektin kertakustannus
(non-recurring engineering, NRE) on suuri, mutta kappalehinta pieni:

```{.python tiedosto="esimerkit/01-kustannus.py" osa="malli"}
```

```{.python tiedosto="esimerkit/01-kustannus.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/01-kustannus.odotettu"}
```

Luvut ovat havainnollisia, mutta mittasuhteet ovat todellisia. Pienissä
sarjoissa FPGA voittaa aina; ASIC kannattaa suurissa sarjoissa tai kun
tehonkulutus, koko tai suorituskyky on muuten mahdoton saavuttaa.
Avoimet monikäyttökiekot (multi-project wafer, MPW), kuten Tiny
Tapeout ja yliopistojen shuttle-ohjelmat, laskevat prototyypin hinnan
satoihin euroihin jakamalla kiekon kymmenien projektien kesken.

## Työkalut ja mitä tässä ajetaan

Kaupalliset vuot (Synopsys, Cadence, Siemens) ovat alan standardi,
mutta niitä ei voi jakaa avoimessa oppimateriaalissa. Tämä tutoriaali
käyttää avoimia työkaluja ja omia opetustoteutuksia:

| Vaihe | Tässä tutoriaalissa | Tuotannossa |
|-------|---------------------|-------------|
| Synteesi | Yosys + ABC, **ajetaan** | Design Compiler, Genus, Yosys |
| Solukirjasto | oma `opetus.lib`, **ajetaan** | valmistajan PDK (esim. SKY130) |
| Ekvivalenssi | Icarus Verilog, Yosys SAT, **ajetaan** | Formality, Conformal |
| STA | Python-opetustoteutus, **ajetaan** | PrimeTime, Tempus, OpenSTA |
| DFT | Python-vikasimulointi, scan-simulointi, **ajetaan** | Tessent, DFT Compiler |
| Sijoittelu, CTS, reititys | Python-opetusmallit, **ajetaan** | Innovus, ICC2, OpenROAD |
| Teho | VCD-aktiivisuus + kuormat, **ajetaan** | PrimePower, Voltus |
| Sign-off | DRC- ja IR-opetusmallit, **ajetaan** | Calibre, Pegasus, Magic, KLayout |
| Koko vuo | kuvataan tekstinä (luku 13) | OpenLane/LibreLane, kaupalliset vuot |

Opetustoteutukset ovat tarkoituksella pieniä, jotta algoritmit näkyvät.
Ne käyttävät samoja tietomuotoja kuin oikeat työkalut: Liberty-
solukirjastoa, Yosysin netlistaa, SDC-rajoitteita ja VCD-aktiivisuutta.

Solukirjasto `opetus.lib` on tätä tutoriaalia varten kirjoitettu
keksitty kirjasto, jonka arvot muistuttavat 130 nm:n prosessia. Oikean
PDK:n (esim. SkyWater SKY130, Apache 2.0) kirjastot ovat satoja
megatavuja ja sisältävät satoja soluja kymmenissä kulmissa; pieni
kirjasto pitää esimerkit luettavina ja tulokset toistettavina.

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Python-ohjelmat tarkistetaan
ruffilla ja mypyllä (`--strict`), ja ne käyttävät Yosysia ja Icarus
Verilogia aliprosesseina. SystemVerilog-esimerkit simuloidaan
Verilatorilla. Kehityskontissa ovat kaikki työkalut valmiina:

```text
make -C asic-toteutus testaa
cd asic-toteutus/esimerkit && python3 sta.py
```

## Lukuohje

Luvut 2–5 muodostavat ytimen: solukirjasto, synteesi ja ajoitus. Luvut
6–11 seuraavat vuota fyysiseen toteutukseen ja valmistukseen, ja ne
voi lukea itsenäisesti. Luku 12 esittelee asynkroniset piirit
vaihtoehtona kellolle.
