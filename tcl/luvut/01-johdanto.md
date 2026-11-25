# Johdanto {.runko-johdanto}

Tcl (*Tool Command Language*, lausutaan "tikl") on pieni tulkattu
kieli, joka on suunniteltu upotettavaksi muihin ohjelmiin niiden
komentokieleksi. Tästä syystä se on lähes kaikkien digitaalisuunnittelun
EDA-työkalujen (*electronic design automation*) skriptikieli: synteesi-,
simulointi-, sijoittelu- ja ajoitusanalyysityökaluja ohjataan
Tcl-skripteillä. Laitesuunnittelija kirjoittaa Tcl:ää, vaikka ei olisi
koskaan valinnut sitä itse.

Tämä tutoriaali opettaa Tcl:n niin, että skriptit ovat luettavia,
testattavia ja kestävät virheellisen syötteen. Kieli on pieni, joten
paketti on lyhyt. Painopiste on säännöissä, joiden ymmärtämättömyys
tuottaa suurimman osan Tcl-virheistä, ja EDA-skriptauksen malleissa.

## Historia

- **1988** John Ousterhout kehitti Tcl:n Berkeleyssä. Hänen
  piirisuunnittelutyökaluissaan oli kussakin oma, puolivalmis
  komentokielensä. Ratkaisu oli yksi yhteinen, upotettava tulkki, jota
  sovellus laajentaa omilla komennoillaan.
- **1991** Tk-graafinen kirjasto teki Tcl/Tk:sta suositun
  käyttöliittymien tekoon. Tk elää yhä esimerkiksi Pythonin
  `tkinter`-moduulissa.
- **1990-luku** EDA-yritykset ottivat Tcl:n komentokielekseen. Nykyään
  sitä käyttävät esimerkiksi AMD Vivado, Altera Quartus (aiemmin
  Intel), Siemens Questa ja
  ModelSim, Synopsysin ja Cadencen työkalut sekä avoimet OpenROAD,
  OpenSTA ja Yosys (`yosys -c skripti.tcl`).
- **2012** Tcl 8.6: olio-ohjelmointi (TclOO), korutiinit,
  `try`/`throw` ja `lmap`. Tämä tutoriaali käyttää
  versiota 8.6, jota EDA-työkalut yleisimmin upottavat.
- **2024** Tcl 9.0: 64-bittiset koot, tiukempi merkistökäsittely ja
  joitain yhteensopimattomia muutoksia. Ne mainitaan luvussa 13.

## Mihin Tcl sopii ja mihin ei

Tcl sopii, kun

- sovellus tarjoaa Tcl-tulkin ja omat komentonsa (EDA-työkalut, osa
  verkkolaitteista, testauslaitteistot),
- tarvitaan pieni, helposti upotettava ja laajennettava komentokieli
  omaan C-ohjelmaan,
- tai halutaan tapahtumapohjainen apuohjelma ja yksinkertainen
  käyttöliittymä Tk:lla.

Tcl ei ole hyvä valinta laajaan erilliseen sovellukseen, numeeriseen
laskentaan tai tietojenkäsittelyyn. Niihin Python on parempi, ja
monet EDA-ympäristöt tarjoavatkin nykyään myös Python-rajapinnan.
Hyvä työnjako: Tcl ohjaa työkalua sen sisällä, Python ja Make tai CI
ohjaavat koko työkaluketjua sen ulkopuolelta (taidot *Python
työkaluohjelmointiin* ja *EDA-työkaluketjujen automatisointi*).

## Toteutukset ja työkalut

- `tclsh` on komentorivitulkki ja `wish` sama Tk:lla. Ubuntussa paketti
  `tcl8.6` asentaa komennon `tclsh8.6`.
- EDA-työkalu sisältää oman tulkkinsa, jonka versio voi olla vanha.
  `info patchlevel` kertoo version. Kirjoita siis varovasti uusien
  ominaisuuksien kanssa ja tarkista versio skriptin alussa:
  `package require Tcl 8.6`.
- Vakiokirjasto on pieni. **Tcllib** on puhdas Tcl-kirjasto
  (komentoriviargumentit, JSON, CSV, lokitus, testauksen apuvälineet).
- Esimerkit ajetaan komennolla `tclsh8.6 tiedosto.tcl`. Hakemiston
  `esimerkit` kehityskontti sisältää tulkin.

## Esitiedot ja rajaus

Esitiedoksi riittää taito *Ohjelmoinnin perusteet (Python)*:
muuttujat, ehdot, silmukat, funktiot ja listat oletetaan tutuiksi.
EDA-työkaluja ei tarvitse tuntea eikä asentaa: luvun 11 esimerkit
käyttävät simuloitua työkalua, ja kaikki ajetaan tavallisella
`tclsh`-tulkilla. Kehityskontin käyttö neuvotaan taidossa
*Kehitysympäristöt ja Dev Containers*.

Paketin ulkopuolelle jäävät

- Tk-käyttöliittymät, joita EDA-skriptauksessa ei tarvita
- oikeiden työkalujen komennot, jotka vaihtelevat valmistajittain ja
  opitaan työkalun omasta oppaasta
- työkaluketjun ohjaus työkalun ulkopuolelta (Make, CI, Python):
  *EDA-työkaluketjujen automatisointi*
- rajoitteiden ja raporttien sisältö: *FPGA-toteutus* ja
  *ASIC-toteutus*.

## Ensimmäinen ohjelma

Ohjelma lukee kellomäärittelyt syötteestä, ohittaa kommentit ja
virheelliset rivit ja tulostaa taajuudet.

```{.tcl tiedosto="esimerkit/01-kellot.tcl"}
```

Syöte ja tuloste. Ohitetusta rivistä kerrotaan virhevirtaan
(`puts stderr`), joten se ei sotke varsinaista tulostetta.

```{.tuloste tiedosto="esimerkit/01-kellot.syote"}
```

```{.tuloste tiedosto="esimerkit/01-kellot.odotettu"}
```

Jo tästä näkyy Tcl:n tyyli: kaikki on komentoja (`proc`, `while`,
`if`, `dict`), laskenta tehdään komennolla `expr`, ja aaltosulkeet
`{…}` ryhmittelevät koodia ilman korvauksia. Seuraava luku kertoo,
miksi.
