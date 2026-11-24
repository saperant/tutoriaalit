# Kellot ja nollaukset

Kello on FPGA-suunnitelman selkäranka: jokainen kiikku tarvitsee sen,
ja sen on saavuttava kaikkialle yhtä aikaa. Luku näyttää, mistä kello
saadaan, miten sen taajuutta muutetaan PLL:llä ja miten nollaus
vapautetaan turvallisesti, kun kello on vakaa.

## Kellon lähteet

iCE40UP5K saa kellonsa kolmesta lähteestä:

| Lähde | Primitiivi | Taajuus | Tarkkuus |
|-------|------------|---------|----------|
| Ulkoinen kide tai oskillaattori nastaan | `SB_IO` + `SB_GB` | kortin mukaan, iCEBreakerissa 12 MHz | ppm-luokkaa |
| Sisäinen nopea oskillaattori | `SB_HFOSC` | 48, 24, 12 tai 6 MHz | noin ±10 % |
| Sisäinen hidas oskillaattori | `SB_LFOSC` | 10 kHz | epätarkka |

Sisäinen oskillaattori riittää ledien vilkutukseen ja ohjauslogiikkaan,
mutta ei sarjaliikenteeseen: UART sietää vain muutaman prosentin
taajuusvirheen. Tarkka ajoitus vaatii ulkoisen kiteen.

Kun kello tulee nastasta, nextpnr vie sen globaaliin verkkoon. Kellon
nimi raportissa (`clk$SB_IO_IN_$glb_clk`) kertoo juuri tämän: nastan
IO-lohko ja globaali puskuri.

## PLL

Kiteen taajuus on harvoin se, jota logiikka tarvitsee. PLL tuottaa
tulokellosta uuden taajuuden: vaihevertailija lukitsee
jänniteohjatun oskillaattorin (VCO) tulokellon monikertaan, ja
lähtöjakaja jakaa VCO:n taajuuden halutuksi. iCE40:n PLL:n kaava on

$$f_{\text{lähtö}} = \frac{f_{\text{tulo}} \cdot (\text{DIVF} + 1)}{(\text{DIVR} + 1) \cdot 2^{\text{DIVQ}}}$$

ja VCO:n on pysyttävä välillä 533–1066 MHz. Parametrit lasketaan
IceStormin apuohjelmalla:

```text
$ icepll -i 12 -o 48
F_PLLIN:    12.000 MHz (given)
F_PLLOUT:   48.000 MHz (requested)
F_PLLOUT:   48.000 MHz (achieved)

FEEDBACK: SIMPLE
F_PFD:   12.000 MHz
F_VCO:  768.000 MHz

DIVR:  0 (4'b0000)
DIVF: 63 (7'b0111111)
DIVQ:  4 (3'b100)

FILTER_RANGE: 1 (3'b001)
```

Kaikkia taajuuksia ei saa tarkasti: pyyntö `-o 25` antaa 25,125 MHz.
Jos tarkka taajuus on tärkeä (esimerkiksi videon pikselikello), kide
valitaan sen mukaan.

PLL instansioidaan suoraan, koska synteesi ei päättele sitä
kuvauksesta. Simulaattori ei tunne valmistajan primitiiviä, joten
simulaatiossa PLL korvataan suoralla kytkennällä:

```{.systemverilog tiedosto="esimerkit/07-pll/pll_ylin.sv" osa="pll"}
```

Yosys määrittelee makron `SYNTHESIS` synteesin aikana, Verilator ei.
Rajaus on tehtävä huolella: kaikki `ifdef SYNTHESIS` -lohkon sisällä on
simuloimatonta. Siksi lohkossa on vain primitiivi, ei logiikkaa.
Testipenkki ei voi tarkistaa PLL:n taajuutta; sen tarkistaa
ajoitusraportti, jossa PLL:n lähtökello näkyy omalla nimellään.

`SB_PLL40_PAD` ottaa tulokellon suoraan nastasta, ja se toimii vain
tietyissä nastoissa. iCEBreakerin kide on kytketty sellaiseen (nasta
35):

```{tiedosto="esimerkit/07-pll/icebreaker.pcf"}
```

Jos kello tulee muualta, käytetään primitiiviä `SB_PLL40_CORE`, joka
ottaa kellon globaalista verkosta.

## Nollaus PLL:n jälkeen

PLL:n lähtö ei ole käyttökelpoinen heti käynnistyksessä: taajuus
hakeutuu paikalleen, ja signaali `LOCK` nousee vasta, kun PLL on
lukittunut. Sitä ennen kellossa voi olla liian lyhyitä jaksoja, jotka
rikkovat ajoituksen. Siksi logiikka pidetään nollauksessa, kunnes PLL
on lukittunut, ja nollaus vapautetaan kelloon tahdistettuna:

```{.systemverilog tiedosto="esimerkit/07-pll/pll_ylin.sv" osa="nollaus"}
```

Tahdistin on sama malli kuin taidon *RTL-suunnittelu* luvussa
*Kellot ja nollaukset*: nollaus asetetaan asynkronisesti (`LOCK`
putoaa, tahdistin nollautuu heti) ja vapautetaan synkronisesti (kaksi
kiikkua kellon tahdissa). Näin nollauksen vapautuminen ei koskaan osu
kellon reunan lähelle, ja kaikki kiikut lähtevät liikkeelle samalla
jaksolla.

Testipenkki tarkistaa juuri tämän viiveen. Se lukee sisäisiä
signaaleja hierarkkisella nimellä (`dut.nollaus`), mikä on
simulaatiossa sallittua ja kätevää:

```{.systemverilog tiedosto="esimerkit/07-pll/testipenkki.sv"}
```

```{.tuloste tiedosto="esimerkit/07-pll.odotettu"}
```

Nollaus vapautuu toisella jaksolla, ja laskuri alkaa kasvaa jaksoa
myöhemmin. Synteesin tilastoissa tahdistin näkyy kahtena kiikkuna
`SB_DFFR` (asynkroninen nollaus) ja laskuri kiikkuina `SB_DFFSR`
(synkroninen nollaus):

```{.tuloste tiedosto="esimerkit/raportit/pll.odotettu"}
```

Vuo antaa PLL:n lähtökellolle tavoitteen 48 MHz. Saavutettu Fmax on
noin 73 MHz, ja suunnitelma vie 34 logiikkasolua.

## Johdetut kellot ja sallinnat

Hidasta tahtia tarvitaan usein: UART-bitti 115 200 kertaa sekunnissa,
näytteenotto kilohertsin välein. Houkutteleva ratkaisu on jakaa kello
laskurilla ja käyttää laskurin bittiä toisen logiikan kellona. FPGA:lla
se on virhe:

- Laskurin lähtö on tavallinen logiikkasignaali. Se kulkee yleisen
  reitityksen kautta, ja sen viive eri kiikkuihin vaihtelee.
- Johdettu kello on uusi kellotusalue. Jokainen signaali alkuperäisen
  ja johdetun kellon välillä on kellotusalueen ylitys (luku 8).
- Ajoitusanalyysi ei tiedä johdetun kellon vaihetta, joten se ei voi
  tarkistaa polkuja oikein.

Oikea ratkaisu on **kellon sallinta** (clock enable): kaikki logiikka
toimii samalla kellolla, ja hidas logiikka päivittyy vain jaksoilla,
joilla sallinta on päällä. Luvun 10 UART-lähetin tekee näin: ajastin
laskee bittiajan kellojaksoja, ja lähetin siirtää bittiä vain, kun
ajastin on nollassa. Sallinta päätyy kiikun omaan tuloon (`SB_DFFE`),
joten se ei maksa logiikkasoluja.

Kun eri taajuus on todella tarpeen, se tehdään PLL:llä, ja kellot
käsitellään erillisinä kellotusalueina.

## Kellon portitus

ASICissa kellon portitus säästää tehoa: pysähtynyt kello ei kuluta.
FPGA:lla kelloa ei portiteta logiikalla. Portti kellopolulla lisää
viivettä, jota ajoitusanalyysi ei näe oikein, ja voi tuottaa
välähdyksiä, jotka laukaisevat kiikkuja. Suurissa FPGA:issa on
erilliset portitetut kellopuskurit (AMD:n `BUFGCE`), joiden kanssa
portitus on turvallista. iCE40:ssä vastaava keino on sallinta, ja
tehon säästämiseen käytetään PLL:n ja oskillaattorien
sammutustuloja.

## Globaalit verkot

iCE40UP5K:ssa on kahdeksan globaalia verkkoa. nextpnr sijoittaa niihin
kellot ja muut signaalit, joilla on suuri tuulettuvuus, kuten
nollauksen ja laajat sallinnat. Kun verkot loppuvat, loput signaalit
kulkevat yleisessä reitityksessä, mikä heikentää ajoitusta. Siksi
suunnitelmassa on hyvä olla vain vähän kelloja ja vain yksi
nollaussignaali kellotusaluetta kohden.

## Käytännössä

- **Yksi kello, jos mahdollista.** Hidas tahti tehdään sallinnalla,
  ei johdetulla kellolla. Jokainen uusi kello on uusi kellotusalue.
- **PLL:n parametrit työkalulla.** `icepll` (tai valmistajan
  ohjattu työkalu) laskee jakajat ja tarkistaa VCO:n rajat. Kirjaa
  komento kommenttiin parametrien viereen.
- **Nollaus vasta lukituksen jälkeen.** `LOCK` nollauksen ehdoksi ja
  nollauksen vapautus tahdistettuna kuhunkin kellotusalueeseen.
- **Rajaa simuloimaton osa.** `ifdef SYNTHESIS` -lohkoon vain
  primitiivi; kaikki logiikka on simuloitavalla puolella.

## Itsearviointi

- Osaat laskea PLL:n lähtötaajuuden jakajista ja tuottaa parametrit
  `icepll`-ohjelmalla.
- Osaat instansioida PLL:n niin, että sama RTL voidaan simuloida ja
  syntetisoida.
- Osaat kirjoittaa nollauksen, joka asetetaan asynkronisesti ja
  vapautetaan synkronisesti PLL:n lukituttua.
- Osaat perustella, miksi hidas tahti tehdään sallinnalla eikä
  johdetulla kellolla.
