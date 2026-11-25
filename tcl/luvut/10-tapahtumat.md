# Tapahtumasilmukka ja korutiinit {.runko-rinnakkaisuus}

Tcl:n rinnakkaisuus perustuu tapahtumasilmukkaan. Tulkki odottaa
tapahtumia (ajastimet, luettavissa oleva kanava, käyttöliittymä) ja
kutsuu niihin rekisteröityjä käsittelijöitä yksi kerrallaan. Säikeitä
ei tarvita moneen samanaikaiseen odotukseen, eikä jaetun tilan
lukituksia tarvita, koska käsittelijät eivät keskeydy kesken.
EDA-skriptissä tyypillinen tarve on ajaa useita työkaluajoja
rinnakkain ja koota tulokset.

## Ajastimet ja `vwait`

`after ms skripti` ajastaa skriptin ja `after idle skripti` ajaa sen,
kun muuta tehtävää ei ole. `tclsh` ei pyöritä silmukkaa itsestään:
`vwait muuttuja` käsittelee tapahtumia, kunnes muuttuja saa arvon.
(`wish` ja monet EDA-työkalut pyörittävät silmukkaa jatkuvasti.)

```{.tcl tiedosto="esimerkit/10-korutiinit.tcl" osa="ajastimet"}
```

`after ms` ilman skriptiä pysäyttää koko tulkin; sitä ei käytetä
tapahtumakäsittelijöissä.

## Rinnakkaiset prosessit

`open |[list ohjelma arg…] r` käynnistää prosessin ja palauttaa kanavan
sen tulosteeseen. Estämätön tila (`-blocking 0`) ja `fileevent
readable` kutsuvat käsittelijää aina, kun luettavaa on. Kun kaikki
prosessit ovat päättyneet, `vwait` palaa. Esimerkissä "työkaluajot"
ovat saman skriptin lapsiprosesseja, jotka odottavat hetken ja
tulostavat tuloksen; oikeassa kulussa ne olisivat simulaattorin tai
synteesityökalun ajoja.

```{.tcl tiedosto="esimerkit/10-ajot.tcl" osa="lapsi"}
```

```{.tcl tiedosto="esimerkit/10-ajot.tcl" osa="kaynnistys"}
```

Käsittelijä lukee rivin kerrallaan. Tiedoston loppu tarkoittaa, että
prosessi on päättynyt. `close` estävässä tilassa palauttaa lapsen
paluuarvon virheenä (`CHILDSTATUS`):

```{.tcl tiedosto="esimerkit/10-ajot.tcl" osa="lukeminen"}
```

```{.tcl tiedosto="esimerkit/10-ajot.tcl" osa="paaohjelma"}
```

```{.tuloste tiedosto="esimerkit/10-ajot.odotettu"}
```

Ajot kestävät yhteensä 850 ms, mutta rinnakkain noin 300 ms.
Esimerkki mittaa jokaisen ajon keston ja vertaa kokonaisaikaa niiden
summaan. Tulokset lajitellaan ennen tulostusta, koska
valmistumisjärjestys ei ole sama kuin käynnistysjärjestys.

```{.ajoituskaavio otsikko="Esimerkin neljä ajoa peräkkäin (850 ms) ja rinnakkain (300 ms). Yksi jakso on 50 ms; kuva on piirretty esimerkin kestoista, ei mitatusta ajosta."}
{"signal": [
  ["peräkkäin",
   {"name": "alu", "wave": "01.....0..........."},
   {"name": "fifo", "wave": "0......1.0........."},
   {"name": "dsp", "wave": "0........1...0....."},
   {"name": "regs", "wave": "0............1....0"}],
  {},
  ["rinnakkain",
   {"name": "alu", "wave": "01.....0..........."},
   {"name": "fifo", "wave": "01.0..............."},
   {"name": "dsp", "wave": "01...0............."},
   {"name": "regs", "wave": "01....0............"}]
]}
```

## Korutiinit

`coroutine nimi komento args` käynnistää proseduurin korutiinina.
`yield arvo` keskeyttää sen ja palauttaa arvon kutsujalle; seuraava
kutsu `nimi` jatkaa keskeytyskohdasta. Korutiini sopii generaattoriksi,
joka tuottaa arvoja yksi kerrallaan:

```{.tcl tiedosto="esimerkit/10-korutiinit.tcl" osa="generaattori"}
```

Korutiinin ja tapahtumasilmukan yhdistelmä tekee asynkronisesta
koodista peräkkäisen näköistä. `after ms [info coroutine]` ajastaa
korutiinin jatkamisen, ja `yield` luovuttaa vuoron muille. Sama malli
toimii kanavien kanssa: `fileevent $kanava readable [info coroutine]`.

```{.tcl tiedosto="esimerkit/10-korutiinit.tcl" osa="odotus"}
```

```{.tuloste tiedosto="esimerkit/10-korutiinit.odotettu"}
```

## Säikeet

Tcl:n säikeet ovat erillisessä `Thread`-paketissa. Jokaisella säikeellä
on oma tulkkinsa, ja säikeet viestivät lähettämällä skriptejä
toisilleen. Paketti ei kuulu Tcl 8.6:n perusasennukseen (Ubuntussa
`tcl-thread`), eikä sitä yleensä ole EDA-työkalujen tulkeissa.
Raskas rinnakkainen laskenta tehdään prosesseilla tai työkalun omilla
rinnakkaisuusasetuksilla.

## Käytännössä

- **Prosessit rinnakkaisuuteen, tapahtumasilmukka odottamiseen.**
  Jokainen raskas ajo omaan prosessiinsa; Tcl-skripti vain käynnistää,
  seuraa ja kokoaa.
- **Rajoita samanaikaisten ajojen määrä** lisenssien ja muistin
  mukaan: pidä jonoa ja käynnistä uusi ajo, kun edellinen päättyy.
- **Tarkista lapsen paluuarvo** sulkemalla kanava estävässä tilassa.
- **Tulokset avaimen mukaan, ei valmistumisjärjestyksessä.**
  Valmistumisjärjestys vaihtelee ajosta toiseen.
- **Korutiini takaisinkutsuketjun sijaan,** kun käsittely etenee
  vaiheittain (lue otsikko, odota, lue runko).
- **Älä estä tapahtumasilmukkaa** pitkillä laskennoilla tai
  `after ms`-odotuksilla käyttöliittymässä tai palvelimessa.

## Itsearviointi

- Osaat ajastaa tapahtumia ja odottaa niitä `vwait`-komennolla.
- Osaat käynnistää useita prosesseja rinnakkain, lukea niiden tulosteen
  `fileevent`-käsittelijällä ja tarkistaa niiden paluuarvot.
- Osaat kirjoittaa generaattorin korutiinina ja käyttää korutiinia
  tapahtumasilmukan kanssa.
- Osaat perustella, milloin käytät prosesseja, tapahtumasilmukkaa ja
  säikeitä.
