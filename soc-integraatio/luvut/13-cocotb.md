# Lohkotestit Pythonilla: cocotb

Pikku-SoC:n ohjelmat testaavat koko järjestelmää: ydin ajaa C-koodia,
ja tulosteesta nähdään, toimiiko kokonaisuus. Järjestelmätesti on
välttämätön, mutta hidas ja karkea. Jos UART-ohjelma ei tulosta
mitään, vika voi olla ytimessä, kytkimessä, sillassa tai UARTissa.
Siksi jokainen oheislaite testataan ensin yksinään omalla
väylärajapinnallaan. Tässä luvussa RAM testataan AXI4-Lite-väylän ja
GPIO APB-väylän kautta *cocotb*-testeillä, jotka on kirjoitettu
Pythonilla. cocotb:n perusteet (liipaisimet, korutiinit, ajaja)
käsitellään taidossa *RTL-suunnittelu SystemVerilogilla* ja
menetelmät syvemmin taidossa *Laitteiston verifiointi*.

## Kääre: väylä erillisinä signaaleina

Pikku-SoC:n väylät ovat pakattuja rakenteita (luku 4). Simulaattorin
ohjelmointirajapinnassa pakattu rakenne näkyy yhtenä leveänä
vektorina, joten Python ei voisi käsitellä kenttiä nimeltä. Testejä
varten tehdään kääre, joka tuo kanavien signaalit erillisinä portteina
ja kokoaa niistä rakenteen:

```{.systemverilog tiedosto="esimerkit/tb/cocotb_ram.sv"}
```

Kääre on testiympäristön osa, ei suunnitelman. Samalla tavalla
kytketään valmiit väyläkirjastot, jotka odottavat signaaleja
nimillä kuten `awvalid` ja `rdata`.

Testit ajetaan Icarus Verilogilla, koska Ubuntun Verilator on cocotb
2:lle liian vanha. Icarus ei käännä kaikkia Pikku-SoC:n lohkoja: APB-
silta sijoittaa rakennetaulukon kokonaisena, mitä se ei tue. RAM:n
kirjoitus oli alun perin silmukka, jossa tavun paikka riippui
silmukkamuuttujasta; nyt kirjoitus tehdään maskilla samoin kuin
generoiduissa rekisterilohkoissa, ja se kääntyy kaikilla työkaluilla.

## AXI4-Lite-isäntä Pythonilla

AXI4-Liten viisi kanavaa ovat jokainen oma valid/ready-kättelynsä
(luku 4). Kättely on siksi testin perusosa: VALID nousee, pysyy
ylhäällä ja laskee vasta sillä reunalla, jolla READY on ylhäällä.
Odotukselle annetaan yläraja, jotta lukkiutunut väylä näkyy virheenä
eikä jumiutuneena simulaationa:

```{.python tiedosto="esimerkit/cocotb-testit/axil.py" osa="kattely"}
```

Reunalla luettu `ready.value` on arvo juuri ennen reunaa, siis se
arvo, jonka laitteisto näki siirtohetkellä. Kirjoituksessa AW- ja
W-kanavat ovat toisistaan riippumattomia, joten isäntä ajaa ne
rinnakkaisina korutiineina. Orja saa hyväksyä ne eri jaksoilla tai,
kuten Pikku-SoC:n RAM, vasta kun molemmat ovat voimassa:

```{.python tiedosto="esimerkit/cocotb-testit/axil.py" osa="kirjoita"}
```

Isäntä voi viivyttää vastauskanavien READY-signaalia satunnaisesti.
Se on tärkeää, koska orjan on pidettävä vastaus voimassa, kunnes isäntä
ottaa sen vastaan. Ilman viivettä tätä sääntöä ei testata lainkaan.

## RAM viitemallia vastaan

Testi kirjoittaa ja lukee satunnaisia osoitteita satunnaisin
tavuluvin (WSTRB). Viitemalli on Pythonin sanakirja, ja osittainen
kirjoitus päivittää siitä vain valitut tavut:

```{.python tiedosto="esimerkit/cocotb-testit/test_ram.py" osa="testi"}
```

RAM:ia ei nollata, joten muisti alustetaan ensin kokonaisilla
sanoilla. Muuten osittainen kirjoitus alustamattomaan sanaan jättäisi
X-tavuja, ja niiden muuttaminen luvuksi kaatuisi.

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/ram.odotettu"}
```

### Mutaatiot

Testin teho tarkistetaan istuttamalla RTL:ään vika ennen kääntämistä.
Ensimmäinen mutaatio rikkoo R-kanavan säännön: RAM pudottaa RVALIDin
seuraavalla jaksolla, vaikka isäntä ei ole vielä ottanut dataa
vastaan. Satunnaisesti viivyttävä isäntä huomaa sen; viiveetön testi
`perakkaiset` ei huomaa:

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/ram-rready.odotettu"}
```

Toinen mutaatio jättää WSTRB:n huomiotta, jolloin osittainen kirjoitus
kirjoittaa koko sanan. Vika näkyy, kun malli ja RAM eroavat ensimmäisen
kerran:

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/ram-wstrb.odotettu"}
```

Kumpikin vika olisi järjestelmätestissä vaikea löytää: ydin lukee
dataa heti eikä tee osittaisia kirjoituksia RAM:iin juuri koskaan.

## APB-isäntä ja GPIO

APB-siirrossa on kaksi vaihetta. SETUP-vaiheessa PSEL nousee ja osoite
asettuu, ACCESS-vaiheessa nousee PENABLE ja siirto päättyy sillä
reunalla, jolla orja nostaa PREADYn (luku 5):

```{.python tiedosto="esimerkit/cocotb-testit/apb.py" osa="siirto"}
```

GPIO:n rekisterikartta tulee generoidusta kuvauksesta (luku 8).
Testi tuntee kartan ja tietää, mitkä osoitteet ovat kirjoitettavia:

```{.python tiedosto="esimerkit/cocotb-testit/test_gpio.py" osa="kartta"}
```

Satunnainen testi lukee ja kirjoittaa sekä rekistereitä että
osoitteita, joissa ei ole rekisteriä. Jokaisen vastauksen virhekoodi
tarkistetaan: kirjoitus vain luettavaan rekisteriin tai tuntemattomaan
osoitteeseen on PSLVERR, joka muuttuu sillassa SLVERR-vastaukseksi
ja ytimessä poikkeukseksi (luku 12). Testi laskee myös, kuinka monta
kertaa kukin siirron ja vastauksen yhdistelmä esiintyi. Se on
yksinkertaista toiminnallista kattavuutta: jos jokin yhdistelmä
puuttuisi, testi ei olisi kokeillut sitä.

```{.python tiedosto="esimerkit/cocotb-testit/test_gpio.py" osa="rekisterit"}
```

Keskeytystesti kulkee saman polun kuin ohjelmisto luvussa 9: sallitaan
yksi tulo, nostetaan tuloja ja tarkistetaan, että keskeytys nousee vain
sallitusta reunasta ja kuittautuu kirjoittamalla ykkönen
REUNAT-rekisteriin (write-1-to-clear):

```{.python tiedosto="esimerkit/cocotb-testit/test_gpio.py" osa="keskeytys"}
```

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/gpio.odotettu"}
```

Mutaatio, jossa W1C-kuittaus kääntyy (kirjoitettu ykkönen *säilyttää*
bitin ja nollaa muut), jättää keskeytyksen päälle. Toinen mutaatio
poistaa virhevastauksen kirjoitukselta vain luettavaan rekisteriin:

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/gpio-w1c.odotettu"}
```

```{.tuloste tiedosto="esimerkit/cocotb-testit/odotettu/gpio-pslverr.odotettu"}
```

## Valmiit väyläkirjastot

Tämän luvun ajurit ovat tarkoituksella pieniä, jotta protokolla näkyy.
Tuotannossa käytetään valmiita kirjastoja. *cocotbext-axi* (MIT-
lisenssi) tarjoaa AXI4-, AXI4-Lite- ja AXI-Stream-isännät ja -orjat,
muistimallit ja satunnaiset viiveet, ja *cocotbext-uart* ja muut
saman tekijän kirjastot vastaavasti muille rajapinnoille. Kirjastot
etsivät signaalit nimien perusteella, joten tämän luvun kaltainen
kääre tarvitaan myös niille, kun väylä on rakenteena. Ennen
käyttöönottoa kannattaa tarkistaa kirjaston yhteensopivuus käytettävän
cocotb-version kanssa ja lukita versio.

## Käytännössä

- Testaa jokainen oheislaite ensin yksin omalla väylällään. Lohkotesti
  on nopea ja kertoo tarkasti, missä vika on; järjestelmätesti kertoo,
  että osat sopivat yhteen.
- Viivytä vastauskanavien READYä ja hyväksy kättely eri jaksoilla.
  Moni protokollavirhe näkyy vasta, kun isäntä tai orja ei ole heti
  valmis.
- Tarkista jokaisen siirron vastauskoodi, myös onnistuneiden. Testi,
  joka katsoo vain dataa, ei huomaa puuttuvaa virhevastausta.
- Anna kättelyille yläraja. Lukkiutunut väylä on virhe, ja sen on
  näyttävä virheenä, ei loputtomana simulaationa.
- Tuo väylä testejä varten erillisinä signaaleina kääreellä, älä muuta
  suunnitelman rajapintaa testauksen takia.
- Tarkista testit mutaatioilla. Ne kertovat, mitä testi oikeasti
  huomaa: viiveetön testi ei huomaa R-kanavan vikaa.

## Itsearviointi

- Osaat kirjoittaa AXI4-Lite- ja APB-isännän cocotbilla ja selittää,
  miksi kättelyn READY luetaan reunalla.
- Osaat testata väyläorjan satunnaisesti viitemallia vastaan, myös
  tavuluvat ja vastausten viiveet.
- Osaat tarkistaa virhevastaukset (SLVERR, PSLVERR) ja keskeytyksen
  koko polun lohkotestissä.
- Osaat tehdä kääreen, joka tuo pakatun väylärakenteen testille
  erillisinä signaaleina.
- Osaat arvioida testin tehoa mutaatioilla.
