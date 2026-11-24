# Muistit ja datapolku

Kiikku muistaa bitin, rekisteri sanan. Suurempi muisti on
osoitettava taulukko, ja kun muisti, laskentayksikkö ja ohjaus
yhdistetään, syntyy datapolku, joka suorittaa ohjelmaa. Tämä luku
kokoaa tutoriaalin rakennuspalikat yhteen.

## ROM

Lukumuisti (ROM) on totuustaulu laitteistona: osoite on syöte ja data
lähtö. Mikä tahansa kombinaatiologiikka voidaan toteuttaa ROM:na, kun
syötteitä on vähän. Esimerkki on seitsensegmenttinäytön dekooderi:

```{.systemverilog tiedosto="esimerkit/12-muistit.sv" osa="rom"}
```

Synteesityökalu toteuttaa vakiotaulukon logiikkana tai muistilohkona
koon mukaan. FPGA:n hakutaulut (luku 5) ovat juuri pieniä ROM-muisteja,
joiden sisältö ladataan konfiguroinnissa.

## RAM ja rekisteritiedosto

Luku–kirjoitusmuisti (RAM) on rekisterijoukko, jolla on osoitedekooderi
(luku 5) kirjoitusta varten ja multiplekseri lukua varten. Suorittimen
*rekisteritiedosto* on pieni RAM, jossa on useita lukuportteja, koska
käsky lukee kaksi operandia ja kirjoittaa yhden tuloksen samassa
jaksossa:

```{.systemverilog tiedosto="esimerkit/12-muistit.sv" osa="rekisteritiedosto"}
```

```{.systemverilog tiedosto="esimerkit/12-muistit.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/12-muistit.odotettu"}
```

Lukuportit ovat tässä asynkronisia: data tulee heti osoitteen
muuttuessa. Suuret muistit (FPGA:n lohko-RAM, piirin SRAM-makrot)
lukevat synkronisesti kellon reunalla, jolloin data tulee jakson
viiveellä. Ero vaikuttaa koko datapolun ajoitukseen, ja muistin tyyppi
valitaan ennen datapolun suunnittelua.

Muistiteknologiat eroavat hinnaltaan ja nopeudeltaan:

| Muisti | Bittisolu | Nopeus | Käyttö |
|--------|-----------|--------|--------|
| Kiikut | noin 20 transistoria | nopein | rekisterit |
| SRAM | 6 transistoria | nopea | välimuistit, lohko-RAM |
| DRAM | 1 transistori + kondensaattori | hidas, virkistettävä | keskusmuisti |
| Flash | kelluva hila | luku nopea, kirjoitus hidas | pysyvä tallennus |

## Pieni datapolku

Datapolku yhdistää ohjelmalaskurin (PC), ohjelmamuistin, käskyn
dekoodauksen, rekisteritiedoston ja ALUn. Esimerkin käskykannassa on
kolme käskyä: vakion lataus (LI), yhteenlasku (ADD) ja siirto (MOV).
Ohjelma laskee Fibonaccin lukuja:

```{.systemverilog tiedosto="esimerkit/12-datapolku/ohjelma.sv" osa="ohjelma"}
```

Jokainen käsky suoritetaan yhdessä jaksossa. Käskyn kentät ovat pelkkää
johdotusta, lukuportit valitsevat operandit, ALU laskee, ja reunalla
tulos kirjoitetaan rekisteriin ja PC kasvaa:

```{.systemverilog tiedosto="esimerkit/12-datapolku/datapolku.sv" osa="datapolku"}
```

```{.systemverilog tiedosto="esimerkit/12-datapolku/testipenkki.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/12-datapolku.odotettu"}
```

Tämä on yksijaksoisen suorittimen ydin. Siitä puuttuu hyppykäskyt
(PC:n seuraava arvo multiplekserin kautta), datamuisti (lataus ja
tallennus) ja liukuhihna. Ne ovat taidon *Tietokonearkkitehtuuri*
aiheita, ja *Assembly* kertoo, miltä sama näyttää ohjelmoijan
puolelta.

Datapolun kriittinen polku kulkee PC-rekisteristä ohjelmamuistin,
dekoodauksen, rekisteritiedoston luvun, ALUn ja tulosmultiplekserin
kautta takaisin rekisteritiedostoon. Juuri siksi oikeat suorittimet
jakavat suorituksen liukuhihnavaiheiksi (luku 11).

## Käytännössä

- **Muistit päätellään kuvioista.** RTL-kuvauksessa RAM kirjoitetaan
  taulukkona, jota kirjoitetaan kellotetussa lohkossa. Synteesityökalu
  tunnistaa kuvion ja valitsee muistilohkon. Väärä kuvio (esimerkiksi
  nollaus koko taulukolle) tuottaa tuhansia kiikkuja.
- **Lukuporttien määrä maksaa.** Jokainen lukuportti on oma
  multiplekserinsä. Rekisteritiedostoissa portteja on yleensä kaksi
  tai kolme; enempää varten muisti monistetaan.
- **Erota ohjaus ja datapolku.** Datapolku (rekisterit, ALU,
  multiplekserit) ja ohjaus (tilakone tai käskydekooderi) suunnitellaan
  erikseen. Ohjaus antaa datapolulle valintasignaalit ja saa siltä
  tilatietoa (liput).
- **Simuloi ohjelmalla.** Datapolku testataan ajamalla sillä ohjelma,
  jonka tulos tiedetään (esimerkiksi Fibonaccin lukujono).

## Itsearviointi

- Osaat selittää ROM:n totuustaulun toteutuksena ja RAM:n rakenteen
  dekooderin ja multipleksereiden avulla.
- Osaat kertoa, miksi rekisteritiedostossa on useita lukuportteja ja
  mitä synkroninen luku muuttaa.
- Osaat kuvata yksijaksoisen datapolun osat ja käskyn kulun niiden
  läpi.
- Osaat tunnistaa datapolun kriittisen polun.
