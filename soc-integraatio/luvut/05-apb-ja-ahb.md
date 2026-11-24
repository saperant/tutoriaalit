# APB, AHB ja sillat

Kaikki lohkot eivät tarvitse AXI:n rinnakkaisia kanavia. Oheislaitteen
rekisteriä luetaan harvoin ja yksi sana kerrallaan, ja sen liitännän
pitää olla pieni, koska oheislaitteita on piirissä kymmeniä. Tähän on
AMBA:n yksinkertaisin väylä, APB (Advanced Peripheral Bus).

## APB

APB:ssa on yksi isäntä, tavallisesti silta nopeammalta väylältä, ja
jokaisella orjalla on oma valintasignaali `PSEL`. Muut signaalit ovat
yhteisiä:

```{.systemverilog tiedosto="esimerkit/rtl/vaylat.sv" osa="apb"}
```

Jokainen siirto kestää vähintään kaksi kellojaksoa:

```{.ajoituskaavio otsikko="Kaksi APB-siirtoa: ensimmäinen ilman odotustiloja, toinen yhdellä odotustilalla"}
{"signal": [
  {"name": "PCLK", "wave": "P......"},
  {"name": "vaihe", "wave": "34z344z", "data": ["SETUP", "ACCESS", "SETUP", "ACCESS", "ACCESS"]},
  {"name": "PSEL", "wave": "1.01..0"},
  {"name": "PENABLE", "wave": "010.1.0"},
  {"name": "PADDR", "wave": "=.x=..x", "data": ["A", "B"]},
  {"name": "PREADY", "wave": "x1x.01x"}
]}
```

Ensimmäinen siirto päättyy jaksolla 2, koska orja vastaa `PREADY`llä
heti. Toisessa siirrossa orja pitää `PREADY`n alhaalla yhden jakson, ja
ACCESS-vaihe kestää kaksi jaksoa.

1. **SETUP**: isäntä asettaa osoitteen, suunnan, datan ja `PSEL`-
   signaalin.
2. **ACCESS**: isäntä nostaa `PENABLE`-signaalin. Siirto päättyy sillä
   jaksolla, jolla orja vastaa `PREADY`-signaalilla. Orja voi pidentää
   siirtoa pitämällä `PREADY`n alhaalla (odotustilat, wait states).

APB3 lisäsi `PREADY`- ja `PSLVERR`-signaalit, APB4 tavukohtaiset
kirjoitusluvat (`PSTRB`) ja suojaustiedon (`PPROT`), ja APB5 muun
muassa käyttäjäsignaalit ja pariteettisuojauksen. Pikku-SoC käyttää
APB4:n signaalijoukkoa ilman `PPROT`ia.

APB-orja on yksinkertainen: kirjoitus tehdään, kun `PSEL`, `PENABLE` ja
`PWRITE` ovat ylhäällä, ja luettu arvo valitaan osoitteen perusteella
kombinatorisesti. UARTin rekisteriliitäntä on tyypillinen:

```{.systemverilog tiedosto="esimerkit/rtl/uart.sv"}
```

Pikku-SoC:n oheislaitteet vaativat sanakirjoitukset: osittainen
kirjoitus (`PSTRB` ≠ `1111`) vastaa virheellä. Sääntö on yleinen, koska
tavukirjoitus 32-bittiseen ohjausrekisteriin on lähes aina
ohjelmointivirhe, ja virhevastaus paljastaa sen (luku 12).

## AXI4-Lite → APB -silta

Silta on AXI4-Lite-orja ja APB-isäntä. Se ottaa vastaan yhden AXI-
siirron, tekee sen APB:n kahdella vaiheella ja palauttaa vastauksen.
Osoitteen bitit 15–12 valitsevat oheislaitteen:

```{.systemverilog tiedosto="esimerkit/rtl/apb_silta.sv" osa="apb"}
```

Alla oleva kaavio on piirretty käynnistysohjelman simulaatiosta
(`make -C esimerkit`). Siinä on ohjelman ensimmäinen kirjoitus UARTin
lähetysrekisteriin: merkki `P` (0x50) osoitteeseen 0x10000000. AXI-
puolella osoite ja data hyväksytään samalla jaksolla. Silta aloittaa
APB-siirron seuraavalla jaksolla (SETUP), UART vastaa ACCESS-vaiheessa
heti, ja silta palauttaa AXI-vastauksen (`BVALID`) vasta sen jälkeen.
Yksi kirjoitus oheislaitteeseen kestää siis neljä jaksoa, kun RAMiin
kirjoitus kestää yhden.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/uart-kirjoitus.json" otsikko="Kirjoitus UARTiin simulaatiosta: AXI4-Lite-siirto sillalle ja APB-siirto UARTille"}
```

Silta myös muuntaa virheet: `PSLVERR` muuttuu AXI:n SLVERR-vastaukseksi
ja ikkuna, jossa ei ole laitetta, DECERR-vastaukseksi. Silta toimii
lisäksi rajana, jonka yli voi kulkea kellotusalue: monissa piireissä APB
käy hitaammalla kellolla, ja silta sisältää kellotusalueen ylityksen.

## AHB

AHB (Advanced High-performance Bus) oli AMBA 2:n suorituskykyinen väylä
ennen AXI:ta, ja sitä käytetään yhä mikrokontrollereissa (esimerkiksi
Cortex-M-ytimet). Sen keskeiset erot AXI:hin:

- **Liukuhihnoitettu osoite ja data.** Siirron osoitevaihe ja edellisen
  siirron datavaihe ovat samalla jaksolla. Yksi siirto kestää siis
  kaksi vaihetta, mutta peräkkäiset siirrot menevät jakson välein.
- **Yksi kanava.** Luku ja kirjoitus eivät voi olla käynnissä yhtä
  aikaa, eikä kesken olevan siirron ohi voi päästä toinen.
- **HREADY.** Orja pidentää datavaihetta pitämällä `HREADY`n alhaalla,
  ja se pysäyttää myös seuraavan osoitevaiheen.
- **Purskeet** (`HBURST`) ja koon (`HSIZE`) ilmaisu kuten AXI:ssa.

AHB-Lite on yhden isännän versio, joka on käytännössä yleisin. Usean
isännän AHB-järjestelmässä on *väyläsovitin* (bus matrix), joka on
AXI-kytkimen vastine.

## Muut väylät

Kaikki järjestelmäpiirit eivät käytä AMBA:a:

- **Wishbone** on avoin väyläperhe, jota käytetään paljon avoimissa
  piireissä (OpenCores, LiteX). Se on käsitteiltään AHB:n ja
  AXI4-Liten välissä.
- **TileLink** on RISC-V-maailmassa (Chipyard, Rocket) käytetty väylä,
  jossa on myös koherenssiprotokolla.
- **Avalon** on Intelin FPGA-työkalujen väylä.

Väylien käsitteet ovat samat: osoite, data, kättely, vastaus ja
virhe. Sillat niiden välillä ovat tavallisia IP-lohkoja.

## Käytännössä

- **APB jokaiselle rekisterilohkolle.** Oheislaitteen
  rekisteriliitäntä APB:na tekee siitä siirrettävän: lohko kelpaa
  mihin tahansa järjestelmään, jossa on APB-silta, ja liitännän voi
  testata kerran.
- **Odotustilat harvoin.** `PREADY` kannattaa pitää ylhäällä, ellei
  rekisterin arvo todella tule hitaasta lähteestä (esimerkiksi toisesta
  kellotusalueesta). Jokainen odotustila hidastaa ajuria.
- **Lukemisen sivuvaikutukset harkiten.** Rekisteri, jonka lukeminen
  muuttaa tilaa (FIFO:n luku, keskeytyksen lunastus), on altis
  virheille: debuggerin muistinäkymä tai spekulatiivinen luku voi
  kuluttaa arvon. Sivuvaikutus dokumentoidaan aina.
- **Silta on luonteva kellotusalueen raja.** Kun APB-alue käy omalla
  kellollaan, ylitys tehdään kerran sillassa eikä jokaisessa
  oheislaitteessa.
- **Valitse väylä järjestelmän mukaan.** Valmis ydin ja valmiit IP-
  lohkot määräävät väylän; sillat ovat halpoja, mutta jokainen silta
  lisää viivettä ja testattavaa.

## Itsearviointi

- Osaat kuvata APB-siirron SETUP- ja ACCESS-vaiheet ja odotustilan.
- Osaat kirjoittaa APB-orjan, joka tekee kirjoitukset ACCESS-vaiheessa
  ja vastaa tuntemattomaan osoitteeseen virheellä.
- Osaat selittää AXI4-Lite → APB -sillan toiminnan ja sen, miten
  virheet välittyvät sillan läpi.
- Osaat kertoa AHB:n liukuhihnoitetun osoite- ja datavaiheen idean ja
  erot AXI:hin.
- Osaat perustella, miksi lukemisen sivuvaikutukset ovat riskialttiita.
