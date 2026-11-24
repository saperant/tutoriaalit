# Rekisterilohko RTL:ksi PeakRDL:llä

PeakRDL on avoimen lähdekoodin työkaluketju SystemRDL-kuvauksille.
Komentorivityökalu `peakrdl` kääntää kuvauksen ja antaa mallin
liitännäiselle, joka tuottaa halutun muodon: `regblock` tuottaa
rekisterilohkon SystemVerilogina, `c-header` C-otsakkeen, `uvm`
UVM-rekisterimallin, `ip-xact` IP-XACT-kuvauksen ja `html`
dokumentaatiosivuston. Liitännäisiä voi kirjoittaa itse samalla
rajapinnalla. Tässä luvussa tuotetaan RTL ja testataan se.

## Tuottaminen

Esimerkkien kaikki tuotetut tiedostot syntyvät yhdessä paikassa,
moduulissa `kuvaus/tuota.py`. PeakRDL ajetaan väliaikaiseen
hakemistoon, ja tiedostot palautetaan sanakirjana:

```{.python tiedosto="esimerkit/kuvaus/tuota.py" osa="peakrdl"}
```

```{.python tiedosto="esimerkit/kuvaus/tuota.py" osa="tuota"}
```

Regblockille annetaan neljä valitsinta:

| Valitsin | Merkitys |
|----------------|---------------------------------------------------|
| `--cpuif apb4-flat` | väyläliitäntä: APB4, signaalit erillisinä portteina. Muita ovat esimerkiksi `axi4-lite`, `avalon-mm`, `wishbone` ja `obi` |
| `--type-style hier` | tuotettujen tyyppien nimet hierarkiasta (`ajastin__STATUS`). Oletustyyli käyttää kuvauksen tyyppinimiä, jotka voivat sisältää tiivisteen |
| `--err-if-bad-rw` | virhevastaus (`PSLVERR`), jos ohjelmisto kirjoittaa vain luettavaan tai lukee vain kirjoitettavaa rekisteriä |
| `--hwif-report` | luettelo laitteiston puolen signaaleista (luku 4) |

Tyyppinimien tyyli on yllättävän tärkeä. Ajastimen kuvauksessa
keskeytyksen sallinta asetetaan rekisterin ulkopuolelta
(`STATUS.VALMIS->enable = CTRL.IE`). Kääntäjä tekee siitä uuden,
nimeltään yksilöllisen tyypin, jonka nimessä on tiiviste
(`STATUS_VALMIS_445f00e8`). Oletustyylillä tiiviste päätyy
SystemVerilogin tyyppeihin, C-otsakkeen makroihin ja UVM-luokkiin.
Hierarkiatyylillä nimet tulevat instanssien poluista ja pysyvät
vakaina, kun kuvausta muutetaan.

## Tuotettu lohko

Lohko on yksi moduuli ja sen paketti. Paketissa on rakennetyypit
laitteiston puolen tuloille ja lähdöille (`hwif_in`, `hwif_out`), joten
lohkon portteja ei tarvitse kytkeä kenttä kerrallaan. Moduulissa on
väyläliitäntä, osoitedekoodaus, jokaisen kentän logiikka ja
lukumultiplekseri. `STATUS.VALMIS`-kentän logiikka:

```{.systemverilog tiedosto="esimerkit/tuotettu/otteet/regblock_valmis.sv"}
```

Ote on tuotetusta tiedostosta poimittu ja rivitetty kirjaan sopivaksi.
Rakenne on jokaisessa kentässä sama: yhdistelmälogiikka laskee
seuraavan arvon ja latausehdon, ja kiikku tallentaa sen. Ohjelmiston
ykkösen kirjoitus nollaa bitin (`& ~(...)`), laitteiston `hwset`
asettaa sen, ja ohjelmiston kirjoitus on ehtolauseessa ensimmäisenä
eli voittaa (`precedence = sw`). Keskeytyslähtö on tilan ja sallinnan
JA. Lukumultiplekseri kokoaa rekisterin bitit kentistä:

```{.systemverilog tiedosto="esimerkit/tuotettu/otteet/regblock_lukumux.sv"}
```

`LASKURI` luetaan suoraan laitteiston tulosta (`hwif_in`), koska
kentällä ei ole tallennusta. Kuvaamattomat bitit luetaan nollina.

## Testipenkki

Testipenkki kytkee lohkon APB-väylään ja ohjaa laitteiston puolta
suoraan rakenteiden jäsenten kautta:

```{.systemverilog tiedosto="esimerkit/tb/ajastin_tb.sv" osa="kytkenta"}
```

Väylän tehtävät ovat yhteisessä tiedostossa `tb/apb.svh`. Testipenkki
ohjaa ja lukee signaaleja kellon laskevalla reunalla, jolloin ne ovat
vakaat eikä testipenkki kilpaile lohkon kanssa nousevalla reunalla:

```{.systemverilog tiedosto="esimerkit/tb/apb.svh" osa="apb"}
```

```{.systemverilog tiedosto="esimerkit/tb/apb.svh" osa="odota"}
```

Ajastimen testit tarkistavat nollausarvot, kirjoituksen ja luvun,
laitteiston arvon, kielletyn kirjoituksen virhevastauksen sekä W1C-
lipun asettumisen ja kuittauksen:

```{.systemverilog tiedosto="esimerkit/tb/ajastin_tb.sv" osa="testit"}
```

Tapahtumalaskurin testipenkki lisäksi seuraa laitteiston puolen
lähtöjä ja laskee, kuinka monta jaksoa kertapulssi kesti ja kuinka
monta kirjoitus- ja lukuilmoitusta tuli:

```{.systemverilog tiedosto="esimerkit/tb/tapahtumat_tb.sv" osa="havainnot"}
```

## Tuotetun koodin varoitukset

Tuotettua koodia ei muokata, mutta sen on läpäistävä samat
tarkistukset kuin käsin kirjoitetun. Verilator `-Wall` antaa
tuotetusta lohkosta varoituksia. Ne hyväksytään poikkeustiedostossa
perusteluineen, ei poistamalla tarkistusta kokonaan:

```{.systemverilog tiedosto="esimerkit/tb/tuotettu.vlt" osa="vlt"}
```

Poikkeukset koskevat vain hakemiston `tuotettu/` tiedostoja, joten
testipenkin oma koodi tarkistetaan täysillä säännöillä. `MULTIDRIVEN`
johtuu siitä, että tuotettu koodi kirjoittaa saman rakenteen eri
jäseniin eri `always_comb`-lohkoissa. Standardin mukaan se on
sallittua, mutta Verilator 5.020 käsittelee rakennetta yhtenä
muuttujana. Lohko simuloituu silti oikein, minkä testit osoittavat.

Esimerkki `05-regblock.py` lint-tarkistaa lohkot ilman poikkeuksia ja
niiden kanssa ja ajaa molemmat testipenkit:

```{.python tiedosto="esimerkit/05-regblock.py" osa="lint"}
```

```{.python tiedosto="esimerkit/05-regblock.py" osa="simuloi"}
```

```{.tuloste tiedosto="esimerkit/05-regblock.odotettu"}
```

Tulosteessa näkyy jokainen luvun 4 käyttäytyminen: kertapulssi kestää
yhden jakson ja lukee nollana, laskuri nollautuu luettaessa ja
saturoituu, ja keskeytys nousee vasta sallinnan jälkeen ja laskee
kuittauksessa. `TILA swmod: 2 kertaa` paljastaa yksityiskohdan:
`swmod` ilmoittaa *kirjoituksesta*, ei arvon muutoksesta.
Ensimmäinen kirjoitus koski `KAYNNISTA`-kenttää, mutta se kirjoitti
samalla `TILA`-kenttään nollan, koska molemmat ovat samassa
rekisterissä. Jos laitteisto haluaa tietää vain muutoksista, sen on
verrattava arvoja itse.

## Käytännössä

- **Valitse väyläliitäntä generaattorissa,** älä kirjoita siltaa
  käsin. Sama kuvaus tuottaa APB-, AXI4-Lite- tai Avalon-lohkon.
- **Käytä vakaita tyyppinimiä** (`--type-style hier`), kun kuvauksessa
  on dynaamisia sijoituksia. Tiivisteitä sisältävät nimet muuttuvat,
  kun kuvausta muutetaan, ja rikkovat ajurit ja testipenkit.
- **Pyydä virhevastaukset.** Kielletty pääsy, joka vastaa virheellä,
  löytää ajurin virheet testeissä. Hiljaa ohitettu kirjoitus ei löydä.
- **Hyväksy tuotetun koodin varoitukset poikkeustiedostossa**
  perusteluineen ja rajattuna tuotettuihin tiedostoihin.
- **Testaa tuotettu lohko käyttäytymisittäin.** Jokaiselle kuvauksen
  käyttäytymiselle (W1C, RC, kertapulssi, laskuri, keskeytys) yksi
  testi, joka käy sen läpi väylän kautta.

## Itsearviointi

- Osaat tuottaa SystemRDL-kuvauksesta rekisterilohkon halutulla
  väyläliitännällä ja valita tyyppinimien tyylin.
- Osaat lukea tuotetun kentän logiikan ja selittää, miten
  käyttäytyminen ja etusija näkyvät siinä.
- Osaat kytkeä tuotetun lohkon testipenkkiin rakenteisten
  `hwif`-signaalien kautta ja testata sen väylän kautta.
- Osaat käsitellä tuotetun koodin lint-varoitukset poikkeustiedostolla.
