# Testit Pythonilla: cocotb

Tähän asti jokaisella moduulilla on ollut SystemVerilog-testipenkki.
Se riittää pieniin tarkistuksiin, mutta viitemallit, satunnaiset
syötteet ja raportit ovat SystemVerilogilla työläitä. *cocotb*
(coroutine cosimulation testbench) kirjoittaa testit Pythonilla ja
ajaa RTL:n tavallisessa simulaattorissa. Tässä luvussa kirjan omat
moduulit testataan sillä: luvun 1 laskuri, luvun 8 FIFO ja luvun 6
UART-lähetin. Testausmenetelmät syvemmin (kattavuus, tulostaulut,
UVM-käsitteet) käsitellään taidossa *Laitteiston verifiointi*.

## Miten cocotb toimii

Simulaattori ajaa RTL:ää ja pysähtyy aina, kun Python-testi odottaa
jotakin. cocotb liittyy simulaattoriin sen ohjelmointirajapinnan
kautta (Verilogissa VPI, VHDL:ssä VHPI). Testi näkee DUT:n olioina:
`dut.arvo` on kahva signaaliin, `dut.arvo.value` sen arvo ja
`dut.sallittu.value = 1` asettaa syötteen.

Testit ovat korutiineja (`async def`). Simulaattorin aika etenee vain,
kun korutiini odottaa *liipaisinta* (trigger):

| Liipaisin | Odottaa |
|-----------------------------------|-------------------------------------|
| `RisingEdge(dut.clk)` | kellon nousevaa reunaa |
| `FallingEdge(dut.clk)` | laskevaa reunaa: syötteet asettuneet |
| `ClockCycles(dut.clk, n)` | n nousevaa reunaa |
| `Timer(100, unit="ns")` | simulaatioaikaa |
| `ReadOnly()` | aika-askeleen loppua |

Kun testi on odottamassa, mikään Python-koodi ei suoritu, joten
Pythonin ja simulaattorin välillä ei synny kilpatilanteita. Kaksi
korutiinia voi kuitenkin olla käynnissä yhtä aikaa: ajuri syöttää
dataa ja monitori tarkkailee ulostuloa.

## Ensimmäinen testi

Testi on funktio, jolla on koriste `@cocotb.test()`. Kello on
oma korutiininsa, joka käynnistetään `start()`-kutsulla:

```{.python tiedosto="esimerkit/cocotb-testit/test_laskuri.py" osa="testi"}
```

Ajoitus kannattaa ajatella samoin kuin SystemVerilog-testipenkissä
(luku 1). Syötteet asetetaan ja ulostulot luetaan *reunojen välissä*:
laskevalla reunalla rekisterit ovat päivittyneet eivätkä syötteiden
muutokset kilpaile nousevan reunan kanssa. Signaalin arvo on
`LogicArray`-olio, joka vertautuu kokonaislukuun; jos arvossa on `X`
tai `Z`, `int()` nostaa poikkeuksen, joten alustamaton signaali ei
mene huomaamatta läpi.

Parametrit näkyvät testille porttien leveyksinä ja kahvoina
(`dut.SYVYYS.value`). Sama testi toimii siksi jokaisella
parametroinnilla:

```{.python tiedosto="esimerkit/cocotb-testit/test_laskuri.py" osa="ylivuoto"}
```

## Ajaminen

cocotb 2:n `cocotb_tools.runner` kääntää lähteet ja ajaa testit
Pythonista. Tämän luvun ajaja käyttää Icarus Verilogia, koska
Ubuntun Verilator 5.020 on cocotb 2:lle liian vanha (vaatimus on
5.036). Icarus ei tue kaikkea SystemVerilogia: kirjan moduuleista
esimerkiksi luvun 6 vaimennin ja luvun 7 PWM eivät käänny sillä
(taulukon sijoitus kokonaisena, tapahtumalausekkeen muoto). Testattavat
moduulit valitaan siksi niistä, jotka kääntyvät molemmilla.

```{.python tiedosto="esimerkit/cocotb-testit/aja.py" osa="ajaja"}
```

Simulaattorin oma loki menee rakennushakemistoon. Testit kirjaavat
havaintonsa erilliseen raporttiin, jonka ajaja tulostaa lopuksi
yhdessä yhteenvedon kanssa. cocotb:n loki sisältää kellonaikoja ja
kestoja, joten sitä ei voi verrata odotettuun tulosteeseen:

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/laskuri.odotettu"}
```

Aaltomuodot saa vianetsintään valitsimella `waves=True`: Icarus
kirjoittaa silloin FST-tiedoston, jonka GTKWave avaa.

## FIFO viitemallia vastaan

Luvun 8 FIFO on hyvä kohde satunnaistetulle testille, koska sen
oikea käytös on helppo kuvata Pythonilla. Viitemalli on `deque`:
kirjoitus lisää loppuun, luku poistaa alusta. Malli on kirjoitettu
täysin eri tavalla kuin RTL, jossa on muisti, kaksi osoitinta ja
ylimääräinen bitti. Sama ajatusvirhe tuskin on molemmissa.

```{.python tiedosto="esimerkit/cocotb-testit/test_fifo.py" osa="testi"}
```

Jokaisella jaksolla testi tekee kolme asiaa samassa järjestyksessä
kuin laitteisto: vertaa ulostulot malliin, arpoo seuraavan jakson
syötteet ja päivittää mallin. Mallin päivityksessä molemmat ehdot
katsotaan reunaa *edeltävästä* tilasta, kuten RTL:ssä: täyteen
jonoon ei voi kirjoittaa, vaikka samalla jaksolla luettaisiin.

`@cocotb.parametrize` ajaa saman testin kolmella profiililla. Tasainen
profiili harvoin täyttää syvää FIFOa, täyttävä profiili pitää sen
lähes täynnä ja tyhjentävä lähes tyhjänä. Testi laskee, mitkä
yhdistelmät (FIFOn tila × toimenpide) se kohtasi. Tämä on toiminnallista
kattavuutta pienimmillään: se kertoo, testattiinko kulmatapauksia
lainkaan. Syvyys annetaan ajajalle parametrina, joten samat testit
ajetaan syvyyksillä 4 ja 16:

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/fifo-4.odotettu"}
```

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/fifo-16.odotettu"}
```

Syvä FIFO harvoin täyttyy, joten osa yhdistelmistä jää kohtaamatta.
Satunnaistus löytää tavalliset tapaukset helposti mutta reunat vain,
jos syötteitä ohjataan niitä kohti.

### Löytääkö testi virheen?

Läpi menevä testi ei vielä todista mitään. Hyvä tapa tarkistaa testi
on *mutaatio*: lähteeseen istutetaan tarkoituksella vika ja katsotaan,
huomaako testi sen. Ajaja korvaa ennen kääntämistä kirjoitusehdon
`kirjoita && !taynna` pelkällä `kirjoita`-ehdolla, jolloin täyteen
jonoon kirjoittaminen siirtää osoitinta:

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/fifo-vika.odotettu"}
```

Kaksi profiilia kolmesta huomaa vian heti, kun jono täyttyy.
Tyhjentävä profiili ei täytä jonoa lainkaan, joten se ei huomaa
mitään. Tämä on syy ajaa useita profiileja ja seurata kattavuutta.

## UART: ajuri ja monitori

Luvun 6 UART-lähettimen ulostulo on sarjalinja, joten testi tarvitsee
*monitorin*: korutiinin, joka purkaa linjaa kuten oikea vastaanotin.
Se odottaa aloitusbitin laskevaa reunaa, siirtyy bitin keskelle ja
näytteistää jokaisen bitin keskeltä:

```{.python tiedosto="esimerkit/cocotb-testit/test_uart_tx.py" osa="monitori"}
```

*Ajuri* antaa tavun lähettimelle kelvollinen/valmis-kättelyllä (luku
6): `kelvollinen` pysyy ylhäällä, kunnes lähetin kuittaa sen
nousevalla reunalla.

```{.python tiedosto="esimerkit/cocotb-testit/test_uart_tx.py" osa="ajuri"}
```

Testi käynnistää monitorin rinnakkaiseksi korutiiniksi
`cocotb.start_soon`-kutsulla ja lähettää tavut. Monitori laittaa
purkamansa tavut jonoon, josta testi lukee ne ja vertaa lähetettyihin.
Kulmatapaukset 0x00, 0xFF, 0x55 ja 0xAA ovat mukana aina, satunnaiset
tavut niiden lisäksi:

```{.python tiedosto="esimerkit/cocotb-testit/test_uart_tx.py" osa="testi"}
```

Testi ajetaan parametreilla `KELLO_HZ=1000000` ja `BAUD=100000`,
jolloin bitti kestää 10 kellojaksoa. Oikeilla arvoilla bittiin
kuluisi 434 jaksoa ja simulaatio olisi 40 kertaa hitaampi, vaikka
logiikka on sama.

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/uart.odotettu"}
```

Mutaatio, jossa lähetin lopettaa seitsemännen databitin jälkeen,
näkyy monitorissa puuttuvana lopetusbittinä:

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/uart-vika.odotettu"}
```

## Toistettavuus

Satunnainen testi on hyödyllinen vain, jos epäonnistunut ajo voidaan
toistaa. Tämän luvun testit ottavat siemenen ympäristömuuttujasta
`SIEMEN`, ja jokainen testi luo oman generaattorinsa:

```{.python tiedosto="esimerkit/cocotb-testit/apu.py" osa="satunnainen"}
```

Jos testit käyttäisivät yhteistä generaattoria, uuden testin
lisääminen muuttaisi kaikkien myöhempien testien syötteitä. Siemen
kirjataan aina raporttiin, ja regressioajo käy läpi useita
siemeniä. cocotb asettaa myös Pythonin oman `random`-moduulin
siemenen (`RANDOM_SEED`) ja tulostaa sen lokiin.

## Python vai SystemVerilog?

| Tilanne | Valinta |
|------------------------------|------------------------------------------|
| pieni itsetarkistava testi | SystemVerilog: ei uutta työkalua |
| viitemalli, data, raportit | cocotb: Pythonin kirjastot ja tietorakenteet |
| sama testi monelle kokoonpanolle | cocotb tai parametroitu SV-testipenkki |
| väittämät moduulin sisällä | SystemVerilog Assertions (SVA) |
| nopea pitkä simulaatio | Verilator ja C++- tai SV-testipenkki |
| yhteinen testi VHDL:lle ja Verilogille | cocotb |

cocotb ei korvaa väittämiä: SVA:t (*Laitteiston verifiointi*)
kulkevat moduulin mukana ja tarkistavat sisäisiä ehtoja, joita
ulkoinen testi ei näe. Hyvä testiympäristö käyttää molempia.

## Käytännössä

- Erota ajuri, monitori ja tarkistus omiksi funktioikseen. Ne ovat
  uudelleenkäytettäviä: UART-monitori kelpaa sellaisenaan
  vastaanottimen testiin ja järjestelmätason testiin.
- Kirjoita viitemalli eri tavalla kuin RTL. Jos malli on RTL:n
  käännös Pythoniksi, molemmissa on sama virhe.
- Aseta syötteet ja lue ulostulot reunojen välissä (laskeva reuna
  tai `ReadOnly`). Suurin osa cocotb-testien oudoista virheistä on
  ajoitusvirheitä testissä, ei RTL:ssä.
- Tarkista testisi mutaatiolla: istuta vika ja varmista, että testi
  kaatuu. Testi, joka ei koskaan kaadu, ei testaa mitään.
- Pidä simulaatio nopeana: pienennä jakajat ja syvyydet
  parametreilla. Sama RTL toimii pienillä ja suurilla arvoilla, jos
  parametrointi on tehty oikein (luku 7).
- Kirjaa siemen ja aja regressiossa useita siemeniä. Valmiita
  ajureita ja monitoreja on kirjastoissa, kuten cocotbext-axi
  (AXI-väylät) ja cocotbext-uart.

## Itsearviointi

- Osaat kirjoittaa cocotb-testin, joka käynnistää kellon, nollaa
  DUT:n, asettaa syötteet ja tarkistaa ulostulot oikeaan aikaan.
- Osaat rakentaa satunnaistetun testin viitemallia vastaan ja
  selittää, miksi mallin päivitysjärjestyksellä on väliä.
- Osaat kirjoittaa ajurin ja rinnakkaisen monitorin bittisarjaa
  käyttävälle rajapinnalle.
- Osaat ajaa saman testin eri parametreilla ja profiileilla ja
  tulkita kattavuusraportin aukot.
- Osaat tarkistaa testin tehon mutaatiolla.
