# Tcl työkalun sisällä

Lähes jokaisessa kaupallisessa EDA-työkalussa on sisäänrakennettu
Tcl-tulkki. Synteesi-, ajoitus-, sijoittelu- ja FPGA-työkalut lukevat
käyttäjän komennot Tcl-skripteinä, ja työkalun omat toiminnot ovat
Tcl-komentoja: `read_verilog`, `create_clock`, `report_timing`.
Myös SDC, ajoitusrajoitteiden standardimuoto, on Tcl:ää. Skriptissä voi
käyttää silmukoita, muuttujia ja proseduureja kuten missä tahansa
Tcl-ohjelmassa, ja työkalun komennot palauttavat arvoja, joita
skripti voi käsitellä.

Vuon kannalta työnjako on selvä. Työkalun sisällä ajetaan Tcl:ää, koska
vain siellä on pääsy työkalun tietokantaan: netlistaan,
ajoituspolkuihin ja soluihin. Työkalun ulkopuolella vuota ohjataan
Pythonilla, joka käynnistää työkalun eräajona, antaa sille skriptin ja
parametrit ja lukee tulokset tiedostoista. Tcl-skriptin kannattaa
olla lyhyt ja tehdä vain se, mikä vaatii työkalua.

## Yosysin Tcl-tila

Yosys ajaa Tcl-skriptin valitsimella `-c`. Komento `yosys -import`
tuo Yosysin komennot Tcl-komennoiksi, jolloin niitä voi kutsua
sellaisinaan. Seuraava skripti syntetisoi laskurin usealla leveydellä:

```{.tcl tiedosto="esimerkit/tcl/synteesi.tcl"}
```

Skripti lukee parametrinsa ympäristömuuttujista taulukon `::env`
kautta. Python-vuo asettaa ne vaiheen ympäristöön (luku 2), joten
parametrit näkyvät leimassa ja manifestissa. `design -reset`
tyhjentää työkalun tietokannan kierrosten välillä. Ilman sitä toinen
kierros lukisi laskurin uudelleen jo olemassa olevan rinnalle, ja
Yosys ilmoittaisi moduulin olevan jo määritelty.

Yosysin komennot eivät tässä versiossa palauta Tcl:lle arvoja:
`[select -count t:*]` on tyhjä merkkijono. Tulokset kirjoitetaan siksi
tiedostoihin komennolla `tee -q -o`, joka ohjaa komennon tulosteen
tiedostoon ja jättää sen pois lokista. Raportti `stat -json` on JSONia,
jota Python lukee luotettavasti. Ihmiselle tarkoitettu `ltp`-raportti
jäsennetään säännöllisellä lausekkeella (luku 5). Kaupallisissa
työkaluissa komennot yleensä palauttavat arvoja tai *kokoelmia*
(collection), joita käydään läpi omilla komennoillaan, kuten
`foreach_in_collection`.

Virheen sattuessa Yosysin komento aiheuttaa Tcl-virheen. Jos sitä ei
oteta kiinni, skripti pysähtyy ja `yosys` päättyy nollasta
poikkeavaan arvoon, mikä on eräajossa juuri oikein. Joskus virheestä
voi toipua, esimerkiksi käyttämällä varaversiota puuttuvan tiedoston
tilalla:

```{.tcl tiedosto="esimerkit/tcl/sieto.tcl" osa="sieto"}
```

`catch` kannattaa rajata yhteen komentoon ja tehdä toipumisesta
näkyvää. Koko skriptin ympärille kirjoitettu `catch` piilottaisi
kaikki virheet, ja vuo luulisi synteesin onnistuneen.

## Kaupallisen työkalun malli: opetus-sta

Kaupallisten työkalujen eräajo noudattaa samaa kaavaa riippumatta
valmistajasta: työkalu käynnistetään valitsimella, joka kertoo
ajettavan skriptin (esimerkiksi `-mode batch -source kulku.tcl` tai
`-f kulku.tcl`). Työkalu kirjoittaa lokin, ajaa skriptin ja päättyy.
Jos skriptissä on virhe, työkalu kirjoittaa sen lokiin ja päättyy
virhekoodiin. Joissain työkaluissa virheen jälkeen jatketaan, mikä
on vaarallinen oletus. Esimerkkien `tcl/opetus_sta.tcl` on pieni
ajoitusanalysaattori, joka toimii samoin. Se lukee Yosysin
BLIF-netlistan, ja sen komennot `read_blif`, `create_clock`,
`get_cells` ja `report_timing` ovat Tcl-proseduureja.

Viivemalli on yksinkertainen: kiikun kello–lähtö-viive, vakioviive
jokaiselle portille ja kiikun asetusaika. Raportin rakenne on silti
sama kuin oikeissa STA-työkaluissa: lähtö- ja loppupiste, polun
saapumisaika, vaadittu aika ja niiden erotus, slack, sekä tila `MET`
tai `VIOLATED`. Komento palauttaa tilan Tcl-arvona, joten skripti voi
toimia sen mukaan. Raportti 8-bittisestä laskurista näyttää tältä
(luku 5 jäsentää sen):

```{.tuloste tiedosto="esimerkit/naytteet/sta.txt"}
```

Eräajon kehys on tiedoston lopussa:

```{.tcl tiedosto="esimerkit/tcl/opetus_sta.tcl" osa="eraajo"}
```

Käyttäjän skripti ajetaan globaalissa nimiavaruudessa
(`uplevel #0`), kuten kaupallisissa työkaluissa, joten sen muuttujat
eivät sekoitu työkalun omiin. Virheen sijainti löytyy Tcl:n
pinojäljestä `-errorinfo`, jossa `source` kertoo tiedoston rivin.
Skriptille omat argumentit erotetaan työkalun argumenteista
merkinnällä `--`. Käyttäjän skripti on lyhyt:

```{.tcl tiedosto="esimerkit/tcl/sta_kulku.tcl"}
```

Toisessa skriptissä on kirjoitusvirhe komennon nimessä:

```{.tcl tiedosto="esimerkit/tcl/sta_rikki.tcl"}
```

## Python ajaa, Tcl tekee

Python-puoli ajaa ensin Yosysin synteesiskriptin ja lukee sen
tiedostoihin kirjoittamat tulokset:

```{.python tiedosto="esimerkit/04-tcl.py" osa="yosys"}
```

Sitten se ajaa opetus-sta:n kullekin netlistalle. Onnistunut ajo
jäsennetään raportista, epäonnistuneesta näytetään lokin `Error:`-rivi:

```{.python tiedosto="esimerkit/04-tcl.py" osa="sta"}
```

```{.tuloste tiedosto="esimerkit/04-tcl.odotettu"}
```

Synteesin tuloksista tulostetaan vain arvioita, jotka eivät riipu
Yosysin versiosta. Laskurissa on aina `LEVEYS + 1` kiikkua (arvo ja
ylivuotolippu). Solumäärä kasvaa leveyden mukana, ja pisin polku ei
lyhene. Tarkka solumäärä ja polun pituus riippuvat siitä, miten ABC
optimoi logiikan, joten niitä ei kannata verrata testissä tarkkoina
lukuina. Samasta syystä ajoitusta kokeillaan jaksoilla, joista tulos on
selvä: 10 ns riittää millä tahansa järkevällä toteutuksella, ja 0,5 ns
ei riitä edes yhdelle portille.

Kirjoitusvirhe pysäyttää skriptin rivillä 5. Työkalu päättyy arvoon 1,
ja lokin virheviesti kertoo komennon, tiedoston ja rivin. Ilman
virhekoodia vuo jatkaisi kuin ajoitus olisi analysoitu, ja raportin
puuttuminen huomattaisiin vasta seuraavassa vaiheessa tai ei
ollenkaan.

## Käytännössä

- **Tcl-skripti tekee vain työkalun työn.** Parametrien valinta,
  sweepit, tulosten vertailu ja raportointi kuuluvat Python-vuolle.
  Työkalun sisällä ajetaan lukeminen, rajoitteet, optimointi ja
  raporttien kirjoitus.
- **Parametrit sisään ympäristöstä tai argumenteista, tulokset ulos
  tiedostoihin.** Konekielinen muoto (JSON, CSV) on parempi kuin
  ihmiselle tarkoitettu raportti, jos työkalu osaa sen.
- **Virhe pysäyttää skriptin.** Tarkista, jatkaako työkalu virheen
  jälkeen oletuksena. Jos jatkaa, ota käyttöön asetus, joka pysäyttää
  ajon.
- **`catch` yhden komennon ympärille.** Toipuminen kirjoitetaan
  lokiin, jotta sen huomaa.
- **Sama skripti interaktiivisesti ja eräajona.** Kun skripti ei
  oleta mitään käyttäjän istunnosta, sen voi ajaa työkalun konsolissa
  virheen tutkimiseksi.

## Itsearviointi

- Osaat kirjoittaa Yosysin Tcl-skriptin, joka lukee parametrinsa
  ympäristöstä ja kirjoittaa tuloksensa tiedostoihin.
- Osaat selittää, miten kaupallinen EDA-työkalu ajaa Tcl-skriptin
  eräajona ja miten virhe välittyy paluuarvoksi.
- Osaat jakaa työn Tcl:n ja Pythonin välillä ja perustella jaon.
- Osaat käyttää `catch`-komentoa niin, ettei se piilota virheitä.
