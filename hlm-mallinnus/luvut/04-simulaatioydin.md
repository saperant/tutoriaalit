# Simulaatioydin, delta-syklit ja aika

Rinnakkaisuuden simulointi yhdellä säikeellä vaatii säännön, joka tekee
tuloksesta riippumattoman siitä, missä järjestyksessä prosessit
ajetaan. SystemC:n sääntö on sama kuin VHDL:ssä ja Verilogin
ei-estävissä sijoituksissa: signaalin uusi arvo näkyy vasta, kun kaikki
samanaikaiset prosessit on ajettu. Tämä luku kuvaa simulaattorin
vaiheet, näyttää delta-syklit toiminnassa, käsittelee simulaatioajan
tarkkuuden ja kokoaa tavallisimmat ajonaikaiset virheet.

## Ytimen vaiheet

Simulaattori (*scheduler*) toistaa seuraavaa kierrosta:

1. **Arviointi** (*evaluate*). Ajetaan kaikki ajettaviksi merkityt
   prosessit yksi kerrallaan. Prosessit kirjoittavat signaaleja ja
   ilmoittavat tapahtumia. Välitön ilmoitus merkitsee odottajat
   ajettaviksi heti, samassa vaiheessa.
2. **Päivitys** (*update*). Kanavat, jotka pyysivät päivitystä
   (`request_update()`), siirtävät uuden arvon näkyviin. Signaali, jonka
   arvo muuttui, ilmoittaa muutostapahtumansa delta-ilmoituksena.
3. **Delta-ilmoitukset.** Delta-ilmoitusten odottajat merkitään
   ajettaviksi. Jos ajettavia on, palataan vaiheeseen 1 samalla
   simulaatiohetkellä: tämä on yksi *delta-sykli*.
4. **Ajan siirto.** Kun ajettavia ei enää ole, aika siirtyy
   aikaisimpaan ajastettuun ilmoitukseen ja kierros alkaa alusta.

Alla oleva kuva näyttää kierroksen silmukkana. Sisempi silmukka on
delta-sykli, joka ei kuluta aikaa; ulompi siirtää simulaatioaikaa.

```{.dot otsikko="Simulaatioytimen kierros: delta-syklit ja ajan siirto"}
digraph {
  rankdir=TB; nodesep=0.5; ranksep=0.35;
  alustus [label="alustus\n(prosessit kerran)"];
  arviointi [label="1. arviointi\najettavat prosessit"];
  paivitys [label="2. päivitys\nkanavien uudet arvot näkyviin"];
  delta [label="3. delta-ilmoitukset\nodottajat ajettaviksi", shape=diamond,
         style="filled", height=0.8];
  aika [label="4. ajan siirto\nseuraava ajastettu ilmoitus", shape=diamond,
        style="filled", height=0.8];
  loppu [label="loppu", shape=plaintext, style=""];
  alustus -> arviointi -> paivitys -> delta;
  delta -> arviointi [label=" ajettavia:\n delta-sykli"];
  delta -> aika [label=" ei ajettavia"];
  aika -> arviointi [label=" aika etenee"];
  aika -> loppu [label=" ei ilmoituksia\n tai sc_stop()"];
}
```

Ennen ensimmäistä kierrosta on *alustusvaihe*, jossa kaikki prosessit
paitsi `dont_initialize()`-merkityt ajetaan kerran. Simulointi päättyy,
kun ajastettuja ilmoituksia ei ole jäljellä, kun `sc_start`ille annettu
aika täyttyy tai kun jokin prosessi kutsuu `sc_stop()`.

Delta-sykli ei kuluta simulaatioaikaa. Se on järjestysnumero saman
hetken sisällä: syy edeltää seurausta, vaikka molemmat tapahtuvat
hetkellä 10 ns.

## Delta-syklit esimerkissä

Kahden rekisterin vaihto on klassinen testi päivityssemantiikalle.
Samaa vaihtoa tehdään sekä signaaleilla että tavallisilla
jäsenmuuttujilla:

```{.cpp tiedosto="esimerkit/03-delta/main.cpp" osa="vaihto"}
```

Kolmen invertterin ketju näyttää, miten muutos etenee delta-sykli
kerrallaan, ja sama moduuli tarkistaa, mitä signaalista luetaan heti
kirjoituksen jälkeen:

```{.cpp tiedosto="esimerkit/03-delta/main.cpp" osa="ketju"}
```

Pääohjelma ajaa ensin ketjun herätteet ja sitten kolme kellojaksoa:

```{.cpp tiedosto="esimerkit/03-delta/main.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/03-delta/odotettu"}
```

Tulosteesta näkyy neljä asiaa:

- **Alustus.** Kaikki kolme astetta ajetaan alustusvaiheessa, ja ne
  lukevat toistensa alkuarvoja (0). Tulos `y1=1 y2=1 y3=1` on
  väliaikainen, ja ketju asettuu oikeaan tilaan kahden lisäsyklin
  aikana. Sama ilmiö näkyy RTL-simulaattorissa ajan 0 välkkeinä.
- **Etenevä muutos.** Kun `x` vaihtuu 10 ns:n kohdalla, muutos
  etenee yhden asteen delta-sykliä kohden (+1 … +4). Kombinaatiopolun
  pituus näkyy delta-syklien määränä, ei aikana.
- **Lukeminen kirjoituksen jälkeen.** Heti `write(true)`-kutsun jälkeen
  `x.read()` palauttaa yhä vanhan arvon 0. Uusi arvo näkyy vasta
  `wait(SC_ZERO_TIME)`:n jälkeen, kun päivitysvaihe on ajettu.
- **Vaihto.** Signaaleilla rekisterit vaihtavat arvonsa joka jaksolla
  (2 1, 1 2, 2 1). Jäsenmuuttujilla molemmista tulee 1: simulaattori
  ajoi ensin rekisterin b, joka luki a:n vanhan arvon, ja sitten
  rekisterin a, joka luki b:n jo muuttuneen arvon. Toinen ajojärjestys
  antaisi `2 2`. Prosessien välinen tieto kulkee siis kanavien kautta,
  ei jaettujen muuttujien.

## Signaalien muunnelmat

`sc_signal<T>` ilmoittaa muutostapahtuman vain, kun arvo todella
muuttuu. `sc_buffer<T>` ilmoittaa jokaisesta kirjoituksesta, mikä on
oikein esimerkiksi jonon kirjoitusvihjeelle, jossa sama arvo voi toistua.
`sc_signal_resolved` ja `sc_signal_rv<N>` ratkaisevat usean ajurin arvon
neliarvoisella logiikalla (luku 6), kuten kolmitilaväylä.

Tavallisella signaalilla saa olla vain yksi kirjoittava prosessi. Toinen
mallin parametri `SC_MANY_WRITERS` poistaa tarkistuksen; silloin
viimeinen kirjoitus delta-syklin aikana voittaa, mikä on harvoin se,
mitä halutaan. Sopivampaa on mallintaa erikseen, kumpi lähde väylää
ohjaa.

## Simulaatioaika ja tarkkuus

Simulaatioaika `sc_time` on kokonaisluku *aikatarkkuuden* (*time
resolution*) kerrannaisina. Oletustarkkuus on 1 ps, ja sen voi vaihtaa
vain ennen kuin yhtään nollasta poikkeavaa aikaa on luotu:

```{.cpp tiedosto="esimerkit/04-aika/main.cpp" osa="tarkkuus"}
```

Koska aika on kokonaisluku, summat ja vertailut ovat tarkkoja. Liukuluku
ei ole:

```{.cpp tiedosto="esimerkit/04-aika/main.cpp" osa="laskenta"}
```

Esimerkki luo lisäksi kellon, jonka jakso on 25 ns, pulssisuhde 40 % ja
ensimmäinen nouseva reuna 5 ns:n kohdalla
(`sc_clock clk("clk", sc_time(25, SC_NS), 0.4, sc_time(5, SC_NS))`),
ja tulostaa sen neljän ensimmäisen jakson reunat. Kun simulointi on alkanut, tarkkuutta ei voi enää vaihtaa:

```{.cpp tiedosto="esimerkit/04-aika/main.cpp" osa="myohassa"}
```

```{.tuloste tiedosto="esimerkit/04-aika/odotettu"}
```

Aika 14 ps pyöristyy 10 ps:iin ja 4 ps nollaan ilman varoitusta, joten
tarkkuuden on oltava mallin pienintä viivettä hienompi. Toisaalta
64-bittinen laskuri riittää 1 ps:n tarkkuudella noin 213 päivän
simulointiin, joten liian hienosta tarkkuudesta ei ole haittaa.
Kello on jaksossa 25 ns ylhäällä 40 % eli 10 ns. Ajan suhde
(`sc_time / sc_time`) on liukuluku, ja ajan voi kertoa luvulla.

> Staattinen `sc_time`-olio, kuten globaali vakio `const sc_time
> jakso(10, SC_NS);`, luodaan ennen `sc_main`ia ja lukitsee tarkkuuden
> oletusarvoon ennen kuin pääohjelma ehtii asettaa sen. Ajat kannattaa
> luoda funktioiden sisällä tai rakentimissa.

## Tavalliset virheet

SystemC tarkistaa ajon aikana monia asioita, joita kääntäjä ei näe.
Kolme yleisintä virhettä:

```{.cpp tiedosto="esimerkit/05-virheet/main.cpp" osa="kytkematon"}
```

```{.cpp tiedosto="esimerkit/05-virheet/main.cpp" osa="odotus"}
```

```{.cpp tiedosto="esimerkit/05-virheet/main.cpp" osa="ajurit"}
```

Virhe on poikkeus `sc_report`, jonka pääohjelma voi siepata. Esimerkin
pääohjelma tulostaa ilmoituksen tyypin ja tekstin:

```{.tuloste tiedosto="esimerkit/05-virheet/odotettu"}
```

Kytkemätön portti huomataan elaboroinnin lopussa, ennen kuin yksikään
prosessi on ajettu; nimetyn portin ansiosta ilmoitus kertoo suoraan,
mikä portti on kyseessä. `wait()` metodissa huomataan vasta, kun metodi
ajetaan, ja kahden ajurin virhe vasta, kun toinen ajuri kirjoittaa.
Molemmat ovat siis ajonaikaisia virheitä, jotka testin on ajettava esiin.
Ilman sieppausta SystemC:n oma `main` tulostaa ilmoituksen ja lähdekoodin
sijainnin ja lopettaa ohjelman.

## Käytännössä

- **Kanavat prosessien välille.** Kaikki prosessien välinen tieto
  kulkee signaalien, jonojen tai muiden kanavien kautta. Jaettu
  jäsenmuuttuja on kilpailutilanne, vaikka säikeitä on vain yksi.
- **Delta-syklien määrä on kustannus.** Jokainen delta-sykli on
  kierros simulaattorissa. Syvä kombinaatioketju, jossa jokainen portti
  on oma prosessinsa, on hidas; sama logiikka yhdessä metodissa on
  nopea ja yhtä oikea.
- **Tarkkuus kerran ja aikaisin.** `sc_set_time_resolution` kutsutaan
  `sc_main`in ensimmäisellä rivillä, jos oletus 1 ps ei käy. Mallissa,
  jossa on 1 GHz:n kello, 1 ps riittää; analogia- tai RF-malleissa
  tarvitaan femtosekunteja.
- **Virheet virheinä.** Mallin omat tarkistukset raportoidaan
  makroilla `SC_REPORT_WARNING`, `SC_REPORT_ERROR` ja `SC_REPORT_FATAL`
  eikä tulosteilla. Niiden käsittelyn voi vaihtaa keskitetysti,
  esimerkiksi niin, että regressiotestissä varoituskin pysäyttää ajon.

## Itsearviointi

- Osaat luetella ytimen vaiheet ja selittää, miksi signaalin
  kirjoitettu arvo ei näy heti.
- Osaat ennustaa, montako delta-sykliä muutoksen eteneminen vie
  prosessiketjussa.
- Osaat valita aikatarkkuuden ja selittää, mitä liian karkea tarkkuus
  tekee viiveille.
- Osaat tunnistaa kytkemättömän portin, metodin `wait()`-kutsun ja
  kahden ajurin virheilmoitukset ja korjata ne.
