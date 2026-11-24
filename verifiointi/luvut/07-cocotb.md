# cocotb: testipenkit Pythonilla

Luvun 3 testipenkki on kirjoitettu SystemVerilogilla, joka on
suunniteltu laitteiston kuvaamiseen eikä ohjelmointiin. Tietorakenteet,
merkkijonot ja kirjastot ovat sillä kömpelöitä, ja Verilator tukee
sen verifiointipiirteistä vain osaa. *cocotb* (coroutine
cosimulation testbench) kirjoittaa testipenkin Pythonilla ja ajaa
DUT:n tavallisessa HDL-simulaattorissa. Simulaattori hoitaa RTL:n ja
ajan, Python kaiken muun: generaattorit, mallit, tulostaulut ja
raportit.

## Toimintaperiaate

cocotb liittyy simulaattoriin sen ohjelmointirajapinnan kautta
(Verilogissa VPI, VHDL:ssä VHPI tai FLI). Python-testi näkee DUT:n
olioina: `dut.push` on kahva signaaliin, jonka arvon voi lukea
(`dut.maara.value`) ja asettaa (`dut.push.value = 1`). Testit ovat
korutiineja (`async def`). Simulaattorin aika etenee vain, kun testi
odottaa jotakin *liipaisinta* (trigger):

| Liipaisin | Odottaa |
|-----------|---------|
| `RisingEdge(dut.clk)`, `FallingEdge(dut.clk)` | kellon reunaa |
| `ClockCycles(dut.clk, n)` | n nousevaa reunaa |
| `Timer(10, unit="ns")` | aikaa |
| `ReadOnly()` | aika-askeleen loppua, kun kaikki signaalit ovat asettuneet |
| `Edge(dut.x)` | mitä tahansa muutosta |

Kun korutiini odottaa, simulaattori jatkaa. Python-koodi ei siis
koskaan suorita samaan aikaan kuin simulaattori, eikä kilpatilanteita
Pythonin ja RTL:n välillä synny. Useita korutiineja ajetaan
rinnakkain funktiolla `cocotb.start_soon`, kuten SystemVerilogin
`fork`.

cocotb tukee Icarus Verilogia, Verilatoria, GHDL:ää ja kaupallisia
simulaattoreita. Tämän tutoriaalin esimerkit käyttävät Icarus
Verilogia, koska cocotb tukee Verilatoria vasta versiosta 5.036
alkaen ja Ubuntu 24.04:ssä on versio 5.020.

## Ajaja

Testit käännetään ja ajetaan cocotb:n Python-rajapinnalla
(`cocotb_tools.runner`). Vanhempi tapa on cocotb:n Makefile-kehys,
mutta Python-ajaja on helpompi yhdistää omiin työkaluihin.
Esimerkkien ajaja `pythonpenkit/aja.py` kääntää lähteet, ajaa
valitun testimoduulin ja tulostaa testien raportit ja yhteenvedon:

```{.python tiedosto="esimerkit/pythonpenkit/aja.py" osa="ajaja"}
```

`defines` välittää istutetun vian makron kääntäjälle. Tulokset
kirjoitetaan JUnit-muotoiseen XML-tiedostoon, jonka CI-järjestelmät
osaavat lukea, ja ajaja poimii siitä epäonnistuneet testit.

## Testi ja nollaus

Testi on korutiini, jolla on koriste `@cocotb.test()`. Se saa
parametrina DUT:n ylimmän tason kahvan. Kahvat syntyvät ajon aikana,
joten tyyppitarkistin ei tunne niitä; esimerkeissä `dut` on tyypiltään
`Any`, ja muu koodi tarkistetaan `mypy --strict` -tasolla.

```{.python tiedosto="esimerkit/pythonpenkit/test_fifo.py" osa="aloitus"}
```

`Clock(...).start()` käynnistää taustakorutiinin, joka vaihtaa kelloa
10 ns:n jaksolla koko testin ajan.

## Ympäristön osat

Luvun 3 osat siirtyvät Pythoniin lähes sellaisinaan. Transaktio on
muuttumaton tietoluokka:

```{.python tiedosto="esimerkit/pythonpenkit/fifo_ymparisto.py" osa="transaktio"}
```

Referenssimalli on `deque`. Se on kirjoitettu määrittelystä:
kirjoitus ja luku päätetään jakson alun tilasta, joten täyteen jonoon
ei kirjoiteta, vaikka samalla luettaisiin.

```{.python tiedosto="esimerkit/pythonpenkit/fifo_ymparisto.py" osa="malli"}
```

Ajuri asettaa signaalit laskevalla reunalla, kuten
SystemVerilog-versio:

```{.python tiedosto="esimerkit/pythonpenkit/fifo_ymparisto.py" osa="ajuri"}
```

Monitori lukee liitännän heti nousevan reunan jälkeen. cocotb palaa
korutiiniin reunan hetkellä ennen kuin simulaattori on päivittänyt
reunalla liipaistut rekisterit, joten luetut arvot ovat samat, jotka
DUT näki reunalla. Jos monitori odottaisi `ReadOnly()`-liipaisinta,
se näkisi rekisterien *uudet* arvot ja havainto siirtyisi jaksolla.

```{.python tiedosto="esimerkit/pythonpenkit/fifo_ymparisto.py" osa="monitori"}
```

Tyhjän jonon lukupää osoittaa muistipaikkaan, johon ei ole
kirjoitettu, ja Icarus antaa sen arvoksi `x`. `int()` ei osaa muuntaa
sitä, joten monitori tarkistaa ensin `is_resolvable`-ominaisuuden.

Tulostaulu vertaa jokaista havaintoa malliin samaan tapaan kuin
luvussa 3:

```{.python tiedosto="esimerkit/pythonpenkit/fifo_ymparisto.py" osa="tulostaulu"}
```

## Testit

Yhteinen apufunktio ajaa toimenpidelistan ajurin, monitorin,
kattavuuden ja tulostaulun läpi. Python-testi epäonnistuu
tavallisella `assert`-lauseella, jonka viesti päätyy tulosraporttiin:

```{.python tiedosto="esimerkit/pythonpenkit/test_fifo.py" osa="aja"}
```

Satunnaistettu testi käyttää luvun 4 kohteliasta generaattoria
siemenellä, joka tulee ympäristömuuttujasta:

```{.python tiedosto="esimerkit/pythonpenkit/test_fifo.py" osa="satunnainen"}
```

Kulmatestin rakenne on kiinteä ja satunnaisuus on vain määrissä ja
datassa. Se tuottaa tilanteet, jotka kattavuusraportti näytti
puuttuviksi (luku 5):

```{.python tiedosto="esimerkit/pythonpenkit/test_fifo.py" osa="kulmat"}
```

Kun FIFOssa on vika `BUGI_SAMANAIKAINEN`, vain satunnaistettu testi
löytää sen. Ohjattu testi ei kirjoita ja lue yhtä aikaa, ja kulmatesti
tekee sen vain täyteen tai tyhjään jonoon, joissa jompikumpi
toimenpide hylätään:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fifo-samanaikainen.odotettu"}
```

`BUGI_TAYSI` näkyy kaikissa kolmessa testissä. Kattavuusraportti
kertoo samalla, että lokeroon `taysi` ei osuttu, koska DUT ei koskaan
päässyt neljään:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fifo-taysi.odotettu"}
```

Kattavuus kirjataan DUT:n havaitusta tilasta, joten viallinen DUT
näyttää kattavuusaukkoja, joita ehjällä ei ole. Kattavuus luetaan
siksi vain ajoista, jotka läpäisivät tarkistukset.

## Python vai SystemVerilog

| | SystemVerilog-testipenkki | cocotb |
|--------------|----------------------------|----------------------------|
| kieli | sama kuin RTL | yleiskäyttöinen, laajat kirjastot |
| satunnaistus | rajoiteratkaisija kielessä (kaupalliset simulaattorit) | `random`, PyVSC |
| kattavuus | `covergroup`, työkalujen tietokannat | omat mallit, cocotb-coverage |
| väitteet | SVA | eivät korvaa SVA:ta; kirjoitetaan RTL-puolelle |
| nopeus | testipenkki käännetään simulaattoriin | jokainen liipaisin vaihtaa Pythonin ja simulaattorin välillä |
| referenssimallit | DPI:llä C/C++:aan | suoraan Python-kirjastot (numpy, scipy) |
| simulaattorit | testipenkin ominaisuudet riippuvat simulaattorista | sama testipenkki eri simulaattoreille |

cocotb sopii erityisesti lohkoihin, joiden referenssimalli on jo
olemassa Pythonilla (signaalinkäsittely, salaus, protokollat), ja
tiimeihin, joissa ohjelmistokehittäjät osallistuvat verifiointiin.
Hitaus näkyy, kun testipenkki tekee työtä joka jaksolla; se lievenee,
kun transaktiot ovat isoja ja Python herää harvoin.

## Käytännössä

- **Näytteistyksen hetki on sovittava.** Lue tilaa heti reunan jälkeen
  tai `ReadOnly()`-vaiheessa, mutta tee se kaikkialla samoin ja
  kirjoita valinta monitorin dokumentaatioon.
- **Älä kirjoita ReadOnly-vaiheessa.** Signaalin asettaminen
  vaiheessa, jossa simulaattori on lupautunut olemaan muuttamatta
  arvoja, on virhe, jonka cocotb ilmoittaa.
- **`x` ja `z` käsitellään erikseen.** `int(dut.x.value)` epäonnistuu
  määräämättömällä arvolla. Päätä, onko `x` virhe vai sallittu.
- **Tyyppitarkistus muuhun kuin kahvoihin.** Ympäristön, mallien ja
  tulostaulujen koodi on tavallista Pythonia ja hyötyy mypystä ja
  ruffista kuten mikä tahansa ohjelma.
- **Yksi ajaja.** Sama komento ajaa testit kehittäjän koneella ja
  CI:ssä, ja sen tuloste on tiivis ja toistettava.
- **Valmiit väyläkomponentit.** cocotbext-kirjastot (esimerkiksi
  AXI, Ethernet, PCIe) sisältävät ajurit ja monitorit tavallisille
  liitännöille.

## Itsearviointi

- Osaat selittää, miten cocotb liittyy simulaattoriin ja milloin
  simulaattorin aika etenee.
- Osaat kirjoittaa cocotb-testin, joka käynnistää kellon, nollaa
  DUT:n ja ajaa ajurin ja monitorin.
- Osaat valita oikean liipaisimen ajuriin ja monitoriin ja selittää,
  mitä arvoja monitori näkee heti nousevan reunan jälkeen.
- Osaat ajaa testit Python-ajajalla ja välittää testille siemenen ja
  makrot.
- Osaat vertailla Python- ja SystemVerilog-testipenkkien vahvuuksia.
