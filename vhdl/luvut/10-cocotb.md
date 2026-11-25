# Testit Pythonilla: cocotb

Luvun 9 testipenkit ovat VHDL:ää. Se on luonteva valinta pieniin
itsetarkistaviin testeihin, mutta viitemallit, satunnaiset syötteet,
jonot ja raportit ovat VHDL:llä työläitä. *cocotb* (coroutine
cosimulation testbench) kirjoittaa testit Pythonilla ja ajaa VHDL:n
tavallisessa simulaattorissa, tässä GHDL:ssä. Samat Python-testit
toimivat myös Verilog-simulaattoreissa, joten sekakielisessä
projektissa testiympäristö on yhteinen. Tässä luvussa testataan kirjan
omat lohkot: luvun 5 kvadratuuridekooderi ja luvun 6
UART-vastaanotin. Menetelmät syvemmin käsitellään taidossa
*Laitteiston verifiointi*.

## Miten cocotb toimii

cocotb liittyy simulaattoriin sen ohjelmointirajapinnan kautta: GHDL
tarjoaa VPI-rajapinnan, jonka kautta Python näkee entiteetin portit ja
signaalit olioina. `dut.asento.value` on portin arvo ja
`dut.a.value = 1` asettaa syötteen. Testit ovat korutiineja (`async
def`), ja simulaatioaika etenee vain, kun korutiini odottaa
*liipaisinta*: `RisingEdge(dut.clk)`, `FallingEdge(dut.clk)`,
`ClockCycles(dut.clk, n)` tai `Timer(100, unit="ns")`. Kun testi
odottaa, mikään Python-koodi ei suoritu, joten Pythonin ja
simulaattorin välillä ei ole kilpatilanteita.

VHDL:n tyypit näkyvät Pythonissa näin:

| VHDL | Python (`.value`) |
|------------------------------|--------------------------------------|
| `std_logic` | `Logic`: vertautuu lukuihin 0 ja 1 |
| `std_logic_vector`, `unsigned` | `LogicArray`: `int(...)` tai `.to_unsigned()` |
| `signed` | `LogicArray`: `.to_signed()` |
| `integer`, `natural` | `int` |
| generic | `dut.NIMI.value` |

Jos vektorissa on `U`, `X` tai `Z`, kokonaisluvuksi muuntaminen nostaa
poikkeuksen. Alustamaton signaali ei siis mene testistä läpi
huomaamatta, kuten VHDL-testipenkissä `to_integer` varoituksen
kanssa.

## Ajaminen GHDL:llä

cocotb 2:n `cocotb_tools.runner` kääntää lähteet ja ajaa testit
Pythonista. GHDL tallentaa analysoidut yksiköt työhakemistoon, ja
cocotb ajaa simulaation testihakemistossa, joten työhakemisto
annetaan sekä käännökselle että ajolle. Generic-arvot annetaan ajossa
(`parameters`), koska GHDL kiinnittää ne vasta elaboroinnissa:

```{.python tiedosto="esimerkit/cocotb-testit/aja.py" osa="ajaja"}
```

Ubuntun GHDL 4.1 käyttää mcode-taustaosaa, joka tukee VPI:tä, joten
cocotb toimii sellaisenaan. Testit kirjaavat havaintonsa erilliseen
raporttiin, jonka ajaja tulostaa yhteenvedon kanssa; cocotb:n oma loki
kellonaikoineen jää rakennushakemistoon.

## Kvadratuuridekooderi

Kiertoanturi muuttaa kanavia A ja B Gray-järjestyksessä, ja suunta
näkyy siitä, kumpi kanava muuttuu ensin (luku 5). Malli on taulukko
kanavien arvoista ja kokonaisluku, joka kertoo odotetun asennon:

```{.python tiedosto="esimerkit/cocotb-testit/test_kvadratuuri.py" osa="malli"}
```

Testi kiertää anturia satunnaisesti eteen ja taakse ja tarkistaa
asennon jokaisen askeleen jälkeen. Anturi pysyy jokaisessa asennossa
vähintään sen ajan, jonka muutos tarvitsee kulkeakseen tahdistimen
ja reunantunnistuksen läpi; pidempi viive vaihtelee satunnaisesti:

```{.python tiedosto="esimerkit/cocotb-testit/test_kvadratuuri.py" osa="testi"}
```

Toinen testi pyörittää anturia 32 770 askelta taaksepäin ja tarkistaa,
että 16-bittinen `signed`-laskuri kiertää ympäri kuten laitteistossa.
Kolmas testi muuttaa molempia kanavia samalla jaksolla. Suunta ei
silloin selviä, ja dekooderin on jätettävä asento ennalleen:

```{.python tiedosto="esimerkit/cocotb-testit/test_kvadratuuri.py" osa="hyppy"}
```

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/kvadratuuri.odotettu"}
```

### Mutaatio

Testin tehon voi tarkistaa istuttamalla vian: ajaja poistaa
lähteestä yhden siirtymän (`"0100"`) ennen kääntämistä, jolloin
dekooderi ohittaa yhden neljästä myötäpäiväisestä askeleesta.
Satunnainen testi huomaa sen pian:

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/kvadratuuri-vika.odotettu"}
```

Huomaa, että ylivuoto- ja hyppytesti menevät läpi: ne kulkevat vain
taaksepäin tai eivät liiku lainkaan. Jokainen testi kattaa vain osan
käytöksestä, ja vasta yhdessä ne riittävät.

## UART-vastaanotin

Vastaanottimen testissä on kaksi rinnakkaista osaa. *Ajuri* tuottaa
sarjalinjan bitti bitiltä:

```{.python tiedosto="esimerkit/cocotb-testit/test_uart_rx.py" osa="ajuri"}
```

*Monitori* tarkkailee vastaanottimen ulostuloja koko testin ajan ja
laittaa jokaisen `valmis`- ja `kehysvirhe`-pulssin jonoon. Se on oma
korutiininsa, joka käynnistetään `cocotb.start_soon`-kutsulla:

```{.python tiedosto="esimerkit/cocotb-testit/test_uart_rx.py" osa="monitori"}
```

Testi lähettää kulmatapaukset ja satunnaiset tavut satunnaisin
tauoin ja lukee jonosta yhden tuloksen kutakin tavua kohden. Lopuksi
jonon on oltava tyhjä: ylimääräinen pulssi olisi yhtä lailla virhe
kuin puuttuva.

```{.python tiedosto="esimerkit/cocotb-testit/test_uart_rx.py" osa="testi"}
```

Muut testit kokeilevat virhetilanteita. Lopetusbitti 0 antaa
kehysvirheen, ja seuraavan kehyksen on silti mentävä läpi. Lyhyt
häiriöpiikki linjalla ei saa käynnistää vastaanottoa, koska
vastaanotin tarkistaa aloitusbitin vielä sen keskikohdassa (luku 6):

```{.python tiedosto="esimerkit/cocotb-testit/test_uart_rx.py" osa="hairio"}
```

Testit ajetaan arvolla `KELLOJA_BITTIIN=16`. Oletusarvolla 868 sama
testi kestäisi yli 50 kertaa kauemmin, vaikka logiikka on sama:

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/uart-rx.odotettu"}
```

Mutaatio, jossa siirtorekisteri täyttyy väärästä päästä (eniten
merkitsevä bitti ensin), näkyy heti ensimmäisessä epäsymmetrisessä
tavussa:

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/uart-rx-vika.odotettu"}
```

Kehysvirhetesti menee läpi, koska sen tavu 0xC3 on sama luettuna
kummastakin päästä. Satunnaiset syötteet paljastavat sen, minkä
käsin valitut tapaukset ohittavat.

## cocotb vai VHDL-testipenkki?

| Tilanne | Valinta |
|------------------------------|------------------------------------------|
| pieni itsetarkistava testi | VHDL-testipenkki: ei uutta työkalua |
| viitemalli, data, raportit | cocotb: Pythonin kirjastot ja tietorakenteet |
| sama testi VHDL:lle ja Verilogille | cocotb |
| väyläkomponentit, kattavuus VHDL:llä | OSVVM tai UVVM (luku 9) |
| testien ajo ja raportointi CI:ssä | VUnit tai cocotb:n ajaja ja pytest |

Valinta ei ole joko–tai: VUnit voi ajaa sekä VHDL-testipenkkejä että
cocotb-testejä, ja väittämät (`assert`) kuuluvat RTL:ään kummassakin
tapauksessa.

## Käytännössä

- Erota ajuri, monitori ja tarkistus. Monitori, joka kerää kaikki
  tapahtumat jonoon, löytää myös ylimääräiset tapahtumat, joita
  pelkkä odotetun arvon tarkistus ei huomaa.
- Lue ulostulot ja aseta syötteet reunojen välissä (laskeva reuna).
  Muuten testi ja VHDL-prosessi kilpailevat samasta deltasyklistä.
- Pienennä generic-arvoilla jakajia ja laskureita, jotta simulaatio
  pysyy nopeana. Hyvin parametroitu lohko toimii samoin pienillä
  ja suurilla arvoilla (luku 7).
- Anna jokaiselle testille oma satunnaislukugeneraattori kiinteästä
  siemenestä ja kirjaa siemen raporttiin.
- Tarkista testisi mutaatiolla. Testi, joka ei koskaan kaadu, ei
  testaa mitään.
- GHDL:n työhakemisto ja VHDL-standardi (`--std=08`) on annettava
  samoina sekä käännökselle että ajolle.

## Itsearviointi

- Osaat ajaa cocotb-testejä GHDL:llä ja antaa generic-arvot ajossa.
- Osaat lukea ja asettaa `std_logic`-, `std_logic_vector`- ja
  `signed`-portteja Pythonista ja tiedät, mitä tapahtuu, jos arvossa
  on `U` tai `X`.
- Osaat kirjoittaa sarjalinjan ajurin ja rinnakkaisen monitorin, joka
  kerää tapahtumat jonoon.
- Osaat testata virhetilanteet (kehysvirhe, häiriöpiikki) ja tarkistaa
  testin tehon mutaatiolla.
