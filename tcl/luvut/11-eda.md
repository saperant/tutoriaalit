# EDA-skriptauksen mallit

Tässä luvussa edellisten lukujen keinot kootaan EDA-työkalujen
skriptauksen tyypillisiksi malleiksi: raportin jäsentäminen,
parametrisoitu kulku ja argumenttien käsittely. Oikeiden työkalujen
komennot vaihtelevat valmistajittain, ja ne ovat työkalun sisäisiä.
Siksi esimerkit käyttävät simuloitua työkalua: tavallisia proseduureja,
joilla on samanlainen rajapinta. Mallit siirtyvät sellaisinaan oikeisiin
työkaluihin. Työkaluketjujen kokonaisuus (Make, CI, Python, useat
työkalut) on taidon *EDA-työkaluketjujen automatisointi* aihe.

## Miksi EDA-työkalut käyttävät Tcl:ää

- **Upotettavuus.** Tulkki on pieni C-kirjasto. Työkalu rekisteröi
  omat komentonsa (`Tcl_CreateObjCommand`), ja ne näyttävät
  käyttäjälle samalta kuin Tcl:n omat.
- **Komentorivimäinen syntaksi.** `create_clock -period 2.5 -name clk
  [get_ports clk]` on luettava sekä interaktiivisesti että skriptissä.
  SDC-rajoitetiedostot (*Synopsys Design Constraints*) ovat juuri
  tällaisia Tcl-komentoja.
- **Historia ja yhteensopivuus.** Kun yksi työkalu valitsi Tcl:n, muut
  seurasivat, jotta skriptit ja rajoitteet siirtyisivät.

Työkalun komennot palauttavat usein *kokoelmia* tai *oliokahvoja*
(solut, netit, pinnit) eivätkä tavallisia listoja. Niitä käsitellään
työkalun omilla komennoilla (`get_property`, `foreach_in_collection`
tai vastaava), ja ne muunnetaan nimiksi vasta tulostusta varten.

## Raportin jäsentäminen

Raportti on tekstiä, jonka muoto voi muuttua työkaluversioiden välillä.
Kestävä jäsennin on tilakone: se tunnistaa rivityypit säännöllisillä
lausekkeilla, kokoaa tietueet sanakirjoiksi, tarkistaa, että pakolliset
kentät löytyivät, ja vertaa omaa laskelmaansa raportin
yhteenvetoon. Jos raportin muoto muuttuu, jäsennin kaatuu selvästi
eikä tuota vääriä lukuja hiljaa.

```{.tcl tiedosto="esimerkit/11-raportti.tcl" osa="jasennin"}
```

```{.tcl tiedosto="esimerkit/11-raportti.tcl" osa="tarkistus"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/11-raportti.syote"}
```

```{.tuloste tiedosto="esimerkit/11-raportti.odotettu"}
```

`switch -regexp -matchvar` asettaa osumat listaan, joten jokainen haara
käsittelee yhden rivityypin. Viimeinen haara hyväksyy kaiken muun
näkyvästi. Jos tuntemattomat rivit halutaan hylätä, se haara heittää
virheen.

## Parametrisoitu kulku

Kulkuskripti saa asetukset argumentteina, ajaa vaiheet järjestyksessä,
kirjaa lokin, tarkistaa tulokset ja palauttaa CI:lle paluuarvon.
Simuloitu työkalu on omassa tiedostossaan:

```{.tcl tiedosto="esimerkit/11-kulku/tyokalu.tcl"}
```

Argumentit jäsennetään määrityksen mukaan. Määritys kertoo valitsimen
tyypin (mikä tahansa `string is` -luokka tai luettelo) ja oletuksen;
valitsin ilman oletusta on pakollinen. Tcllib-kirjaston `cmdline`-paketti
tarjoaa saman valmiina, mutta EDA-työkalun tulkissa sitä ei välttämättä
ole.

```{.tcl tiedosto="esimerkit/11-kulku/main.tcl" osa="argumentit"}
```

Jokainen vaihe ajetaan `vaihe`-rakenteella, joka tulostaa vaiheen nimen,
kirjaa keston lokiin ja lisää vaiheen nimen virheilmoitukseen:

```{.tcl tiedosto="esimerkit/11-kulku/main.tcl" osa="vaiheet"}
```

```{.tcl tiedosto="esimerkit/11-kulku/main.tcl" osa="paaohjelma"}
```

Ajo argumenteilla `-top alu -clock 2.5 -strategy perf`:

```{.tuloste tiedosto="esimerkit/11-kulku.odotettu"}
```

Liian tiukalla kellolla (`-clock 2.2`) kulku päättyy paluuarvolla 1, ja
virheellinen argumentti tuottaa käyttöohjeen ja paluuarvon 2:

```text
$ tclsh main.tcl -top alu -clock fast
virhe: -clock: odotettiin double, saatiin 'fast'
käyttö: tclsh main.tcl -top NIMI -clock NS
         [-strategy area|default|perf] [-out HAK]
```

Oikeassa työkalussa skripti ajetaan eräajona, esimerkiksi
`vivado -mode batch -source kulku.tcl -tclargs -top alu …` tai
`quartus_sh -t kulku.tcl …`. Argumentit ovat silloin muuttujassa
`argv` kuten `tclsh`-ajossa.

## Muita malleja

- **Rajoitteet dataksi.** Kellot, I/O-viiveet ja poikkeukset kuvataan
  sanakirjana tai CSV-tiedostona, ja Tcl-proseduuri tuottaa niistä
  työkalun komennot. Sama data palvelee useaa työkalua ja dokumentaatiota.
- **Tarkistuspisteet.** Jokainen vaihe kirjoittaa tuloksensa
  (tarkistuspiste, raportti) omaan tiedostoonsa. Kulun voi aloittaa
  mistä tahansa vaiheesta, ja vaihe ohitetaan, jos sen tulos on
  uudempi kuin syötteet.
- **Kuivaharjoitus.** Valitsin `-dry_run` tulostaa komennot ajamatta
  niitä. Komento rakennetaan listana, joten sen voi sekä tulostaa että
  ajaa: `puts $komento` ja `{*}$komento`.
- **Viestien tarkistus lopuksi.** Kriittiset varoitukset ja virheet
  lasketaan lokista tai työkalun viestirajapinnasta, ja kynnyksen
  ylitys kaataa kulun.
- **Versiotarkistus alussa.** `package require Tcl 8.6` ja työkalun
  version tarkistus estävät väärän ympäristön hiljaiset virheet.

## Käytännössä

- **Erota työkalun komennot ja logiikka.** Jäsennys, laskenta ja
  päätökset puhtaina proseduureina, jotka voi testata tclsh:lla
  (luku 12). Työkalun komennot ohueen kerrokseen.
- **Älä luota tekstiraportin muotoon.** Käytä koneluettavaa muotoa, jos
  työkalu tarjoaa sen (CSV, JSON, työkalun ominaisuushaut); muuten
  tarkista jäsennys raportin omaa yhteenvetoa vasten.
- **Paluuarvo kertoo tuloksen.** 0 onnistui, 1 tulos ei kelpaa, 2
  käyttövirhe. CI ja Make luottavat siihen.
- **Pinni- ja instanssinimet aaltosulkeissa ja muuttujissa,** ei
  lainausmerkeissä (luku 3).
- **Hae kerran, käsittele Tcl:ssä.** Työkalun haut ja raportit ovat
  kalliita; tallenna tulos muuttujaan.

## Itsearviointi

- Osaat kirjoittaa raportin jäsentimen, joka tunnistaa rivityypit,
  kokoaa tietueet ja havaitsee muodon muutoksen.
- Osaat jäsentää nimetyt argumentit määrityksen perusteella ja
  palauttaa käyttövirheestä oikean paluuarvon.
- Osaat rakentaa kulun vaiheista, joiden virheet ja kestot kirjataan.
- Osaat erottaa työkalun komennot testattavasta logiikasta.
