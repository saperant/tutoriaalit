# cocotb: testipenkin kerrokset Pythonilla

Luvun 3 testipenkki on kirjoitettu SystemVerilogilla, joka on
suunniteltu laitteiston kuvaamiseen eikä ohjelmointiin. Tietorakenteet,
merkkijonot ja kirjastot ovat sillä kömpelöitä, ja Verilator tukee
sen verifiointipiirteistä vain osaa. *cocotb* (coroutine
cosimulation testbench) kirjoittaa testipenkin Pythonilla ja ajaa
DUT:n tavallisessa HDL-simulaattorissa. Simulaattori hoitaa RTL:n ja
ajan, Python kaiken muun: generaattorit, mallit, tulostaulut ja
raportit.

cocotb:n perusteet (korutiinit, liipaisimet, kello, ensimmäinen testi
ja mutaatio) ovat tuttuja esitietotaidosta *RTL-suunnittelu
SystemVerilogilla*. Tässä luvussa niistä rakennetaan luvun 3
kerrosten mukainen ympäristö: transaktio, malli, ajuri, monitori ja
tulostaulu ovat omia luokkiaan. Seuraavat kaksi lukua lisäävät samaan
ympäristöön satunnaistuksen ja kattavuuden, ja luku 9 rakentaa siitä
UVM:n rakenteen.

## Kertaus: aika etenee vain liipaisimissa

cocotb liittyy simulaattoriin sen ohjelmointirajapinnan kautta
(Verilogissa VPI, VHDL:ssä VHPI tai FLI). Python-testi näkee DUT:n
olioina: `dut.push` on kahva signaaliin, jonka arvon voi lukea
(`dut.maara.value`) ja asettaa (`dut.push.value = 1`). Testit ovat
korutiineja (`async def`), ja simulaattorin aika etenee vain, kun
testi odottaa *liipaisinta*: `RisingEdge`, `FallingEdge`,
`ClockCycles`, `Timer` tai `ReadOnly`. Python-koodi ei siis koskaan
suorita samaan aikaan kuin simulaattori. Useita korutiineja ajetaan
rinnakkain funktiolla `cocotb.start_soon`, kuten SystemVerilogin
`fork`.

Tämän tutoriaalin esimerkit käyttävät cocotb:n simulaattorina Icarus
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
Alla oleva periaatekuva näyttää yhden kirjoituksen: ajuri vaihtaa
`push`-signaalin laskevalla reunalla, ja saman nousevan reunan
kohdalla `RisingEdge` näkee vielä vanhan määrän 2 ja `ReadOnly` jo
uuden määrän 3.

```{.ajoituskaavio otsikko="Periaatekuva: mitä monitori näkee nousevalla reunalla"}
{"signal": [
  {"name": "clk", "wave": "1.0.1.0.1.0."},
  {"name": "push (ajuri)", "wave": "0.1...0....."},
  {"name": "maara (DUT)", "wave": "=...=.......", "data": ["2", "3"]},
  {},
  {"name": "RisingEdge näkee", "wave": "=...=...=...",
   "data": ["", "push 1, maara 2", "push 0, maara 3"]},
  {"name": "ReadOnly näkee", "wave": "=...=...=...",
   "data": ["", "push 1, maara 3", "push 0, maara 3"]}
], "config": {"hscale": 1.1}}
```

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

Yhteinen apufunktio ajaa toimenpidelistan ajurin, monitorin ja
tulostaulun läpi. Python-testi epäonnistuu tavallisella
`assert`-lauseella, jonka viesti päätyy tulosraporttiin. Funktio
kirjaa havainnot myös kattavuusmalliin (`fifo_kattavuus`, `raportoi`),
joka esitellään luvussa 6; tässä vaiheessa ne rivit voi ohittaa.

```{.python tiedosto="esimerkit/pythonpenkit/test_fifo.py" osa="aja"}
```

Ensimmäinen testi on sama ohjattu testi kuin johdannossa, nyt
toimenpidelistana: viisi kirjoitusta neljän paikan jonoon ja viisi
lukua.

```{.python tiedosto="esimerkit/pythonpenkit/test_fifo.py" osa="ohjattu"}
```

Testimoduulissa on kaksi muutakin testiä, `satunnaistettu` ja
`kulmat`, jotka esitellään luvuissa 5 ja 6. Ajaja ajaa aina kaikki
kolme. Ohjatun testin raporttirivi ehjällä FIFOlla on:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fifo.odotettu" rivit="1-1"}
```

Kun FIFO käännetään makrolla `BUGI_TAYSI`, tulostaulu huomaa jo
ohjatussa testissä, että lippu `taysi` nousee, kun mallissa on vasta
kolme sanaa. Raportin lopussa ovat ajajan yhteenveto ja kunkin
kaatuneen testin ensimmäinen virhe:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fifo-taysi.odotettu" alkaen="läpi 0"}
```

## Python vai SystemVerilog

| Ominaisuus | SystemVerilog-testipenkki | cocotb |
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

- Osaat jakaa cocotb-testipenkin kerroksiin (transaktio, malli,
  ajuri, monitori, tulostaulu) niin, että vain ajuri ja monitori
  tuntevat signaalit.
- Osaat kirjoittaa cocotb-testin, joka käynnistää kellon, nollaa
  DUT:n ja ajaa toimenpidelistan ympäristön läpi.
- Osaat valita oikean liipaisimen ajuriin ja monitoriin ja selittää,
  mitä arvoja monitori näkee heti nousevan reunan jälkeen.
- Osaat ajaa testit Python-ajajalla ja välittää testille siemenen ja
  makrot.
- Osaat vertailla Python- ja SystemVerilog-testipenkkien vahvuuksia.
