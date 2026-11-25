# Binäärimuodot

Mittalaitteet, logiikka-analysaattorit, laiteohjelmistokuvat ja
protokollat tallentavat dataa binäärisenä: kiinteän kokoisia kenttiä,
joiden tavujärjestys ja asettelu on sovittu. Python käsittelee tavuja
tyypeillä `bytes` (muuttumaton), `bytearray` (muuttuva) ja
`memoryview` (näkymä ilman kopiointia). Rakenteisiin muuntamisesta
huolehtii `struct`-moduuli.

## Tavujärjestys

Monitavuinen luku voidaan tallentaa vähiten merkitsevä tavu ensin
(*little-endian*, x86 ja useimmat Arm-järjestelmät) tai eniten
merkitsevä ensin (*big-endian*, verkkoprotokollat):

```{.python tiedosto="esimerkit/05-struct.py" osa="jarjestys"}
```

## struct ja kohdistus

`struct`-muotomerkkijonon ensimmäinen merkki valitsee tavujärjestyksen
ja asettelun. `@` jäljittelee C-kääntäjää: kentät kohdistetaan, ja
väliin tulee täytettä. `<`, `>` ja `!` ovat tiiviitä:

```{.python tiedosto="esimerkit/05-struct.py" osa="kohdistus"}
```

```{.dot otsikko="Muodon `BI` (yksi tavu ja 32-bittinen luku) tavut. `@` lisää kolme täytetavua, jotta luku alkaa neljällä jaollisesta siirtymästä; tiivis muoto ei lisää."}
digraph {
  nodesep=0.25;
  node [shape=record, style=filled];
  a [label="{@BI}|{0|B}|{1|täyte}|{2|täyte}|{3|täyte}|{4|I}|{5|I}|{6|I}|{7|I}"];
  b [label="{\<BI}|{0|B}|{1|I}|{2|I}|{3|I}|{4|I}"];
  a -> b [style=invis];
}
```

Tiedostoissa ja protokollissa käytetään aina tiivistä muotoa ja
kiinteää tavujärjestystä. `@` riippuu alustasta, joten se sopii vain,
kun luetaan saman koneen C-ohjelman muistista kirjoittamaa rakennetta.

Usein käytetty muoto käännetään kerran `struct.Struct`-olioksi:

```{.python tiedosto="esimerkit/05-struct.py" osa="otsake"}
```

## Bittikentät

Laitteiston rekisterit pakkaavat useita kenttiä yhteen sanaan. Kenttä
luetaan siirtämällä ja maskaamalla ja kirjoitetaan päinvastoin.
Kirjoitettaessa tarkistetaan, että arvo mahtuu kenttään. Muuten liian
suuri arvo valuisi naapurikenttään:

```{.python tiedosto="esimerkit/05-struct.py" osa="bitit"}
```

```{.tuloste tiedosto="esimerkit/05-struct.odotettu"}
```

```{.dot otsikko="Tilarekisterin `STATUS` kentät ja esimerkin arvo `0x0A15` purettuna."}
digraph {
  node [shape=record, style=filled];
  r [label="{bitit|kenttä|0x0A15}|{15–8|JONO|0000 1010 = 10}|{7–5|ei käytössä|000}|{4–2|TILA|101 = 5}|{1|VIRHE|0}|{0|VALMIS|1}"];
}
```

## Oma tiedostomuoto

Mittausdatalle määritellään yksinkertainen muoto: otsake, lomitetut
16-bittiset näytteet ja lopussa CRC-32-tarkistussumma. Muodon kuvaus
kirjoitetaan modulin alkuun, koska se on rajapinta muihin työkaluihin.
Julkaistavan muodon kuvaus kuuluu myös työkalun dokumentaatioon (taito
*Tekninen dokumentaatio*).

```{.dot otsikko="MDAT-tiedoston rakenne. Otsake on 16 tavua, ja kaikki luvut ovat pieni-endian-muodossa."}
digraph {
  node [shape=record, style=filled];
  t [label="{siirtymä|tyyppi|sisältö}|{0|4 s|taikasana}|{4|u16|versio}|{6|u16|kanavia}|{8|u32|taajuus}|{12|u32|näytteitä}|{16|i16 × kanavia × näytteitä|näytteet lomitettuina}|{loppu − 4|u32|CRC-32}"];
}
```

```{.python tiedosto="esimerkit/05-mittausdata/muoto.py" osa="muoto"}
```

Hyvä binäärimuoto alkaa *taikasanalla* (väärä tiedosto tunnistetaan
heti) ja *versiolla* (muoto voi muuttua ilman, että vanhat tiedostot
tulkitaan väärin), ja siinä on *tarkistussumma* (katkennut tai
muuttunut tiedosto huomataan).

Kirjoittaja tarkistaa syötteen, lomittaa kanavat `array`-taulukkoon ja
laskee tarkistussumman otsakkeesta ja datasta:

```{.python tiedosto="esimerkit/05-mittausdata/muoto.py" osa="kirjoita"}
```

Lukija tarkistaa kaiken ennen kuin luottaa mihinkään: pituuden,
taikasanan, version, odotetun koon ja tarkistussumman. `memoryview`
viipaloi tiedoston sisällön kopioimatta, ja `cast("h")` tulkitsee
tavut 16-bittisinä kokonaislukuina suoraan samassa muistissa:

```{.python tiedosto="esimerkit/05-mittausdata/muoto.py" osa="lue"}
```

`cast` käyttää koneen omaa tavujärjestystä. Siksi lukija ja kirjoittaja
tarkistavat `sys.byteorder`in ja kääntävät tavut big-endian-koneella.

Käyttö ja rikkinäisten tiedostojen hylkäys:

```{.python tiedosto="esimerkit/05-mittausdata/main.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-mittausdata.odotettu"}
```

Suurilla tiedostoilla sama data luetaan NumPy-taulukoksi yhdellä
kutsulla (luku 8).

## Käytännössä

- **Kirjoita muodon kuvaus ennen koodia** ja pidä se lukijan ja
  kirjoittajan vieressä. Muoto on rajapinta, jota käyttävät myös C-,
  Verilog- ja Tcl-koodi.
- **Taikasana, versio, pituus ja tarkistussumma** jokaiseen omaan
  muotoon. Ne maksavat muutaman tavun ja säästävät päiviä vianetsintää.
- **Tarkista ennen kuin luotat.** Pituus otsakkeesta on syöte, ei
  totuus. Ilman tarkistusta väärä pituus johtaa ylilukemiseen tai
  valtavaan muistinvaraukseen.
- **Kiinteä tavujärjestys** (`<` tai `>`) aina tiedostoissa ja
  protokollissa. `@` ja `memoryview.cast` ovat alustasta riippuvaisia.
- **Hinta:** tavu kerrallaan Python-silmukassa käsittely on hidasta.
  `struct.iter_unpack`, `array` ja NumPyn `frombuffer` käsittelevät
  miljoonia tietueita kerralla.
- **Sudenkuoppa:** `bytes` ja `str` sekaisin. `b"MDAT" == "MDAT"` on
  epätosi. Tekstiksi muunnetaan vain reunalla ja aina koodaus nimeten.

## Itsearviointi

- Osaat pakata ja purkaa rakenteen `struct`illa ja valita
  tavujärjestyksen ja asettelun oikein.
- Osaat lukea ja kirjoittaa rekisterin bittikenttiä siirroilla ja
  maskeilla ja tarkistaa, että arvo mahtuu kenttään.
- Osaat suunnitella binäärimuodon, jossa on taikasana, versio ja
  tarkistussumma, ja toteuttaa sille lukijan, joka hylkää rikkinäiset
  tiedostot.
- Osaat käyttää `memoryview`tä datan käsittelyyn kopioimatta.
