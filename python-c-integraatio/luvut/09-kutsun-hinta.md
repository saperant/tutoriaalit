# Kutsun hinta

C++-funktio on nopea, mutta sen kutsuminen Pythonista ei ole. Jokainen
rajan ylitys jäsentää argumentit, tarkistaa niiden tyypit, muuntaa ne
C++-arvoiksi, kutsuu funktion, muuntaa paluuarvon uudeksi
Python-olioksi ja käsittelee mahdolliset poikkeukset. Tämä vie
kymmenistä satoihin nanosekunteihin, mikä on enemmän kuin moni
yksinkertainen lasku itse. Laajennuksen nopeus riippuu siksi ennen
kaikkea siitä, kuinka paljon työtä yksi kutsu tekee. Edelliset luvut
viittasivat tähän hintaan monta kertaa; nyt, kun käytössä ovat sekä
listamuunnokset (luku 6) että NumPy-taulukot (luku 8), se mitataan.

## Kolme rajapintaa samalle laskulle

Sama lasku, alkioiden neliöt, on kirjoitettu kolmella tavalla:

```{.cpp tiedosto="esimerkit/09-hinta/hinta.cpp" osa="rajapinnat"}
```

- **Alkio kerrallaan:** yksi kutsu jokaista lukua kohden.
- **Lista:** yksi kutsu, mutta lista muunnetaan `std::vector`iksi ja
  tulos takaisin listaksi. Jokainen alkio on Python-olio, joka
  tarkistetaan, puretaan ja luodaan uudelleen.
- **NumPy-taulukko:** yksi kutsu ilman muunnoksia. Funktio lukee
  syötteen muistia suoraan ja kirjoittaa uuden taulukon muistiin.

Mittaus ajaa jokaisen 200 000 alkiolle ja vertaa puhtaaseen
Python-listakoosteeseen:

```{.python tiedosto="esimerkit/09-hinta/main.py" osa="mittaus"}
```

Tuloste sisältää vain väitteet, jotka pätevät väljin marginaalein
kaikilla koneilla:

```{.python tiedosto="esimerkit/09-hinta/main.py" osa="tulos"}
```

```{.tuloste tiedosto="esimerkit/09-hinta/main.odotettu"}
```

Kirjoittajan koneella (neliytiminen 2,1 GHz:n Intel Xeon
virtuaalikoneena, Python 3.13, ei muuta kuormaa) sama mittaus antoi
alkiota kohden seuraavat ajat. Ne tuottaa `kuvat/piirra.py`, joka ajaa
samat neljä kutsua samalla datalla:

```{.tuloste tiedosto="esimerkit/tulokset/09-hinta.txt"}
```

![Neljän tavan aika alkiota kohden (samat luvut kuin tulosteessa,
logaritminen asteikko). Vain taulukon välittäminen kerralla on Pythonia
nopeampi.](kuvat/hinta.png){width=85%}

Suhteet toistuivat ajosta toiseen suunnilleen samoina: alkio
kerrallaan kutsuttu C++ oli noin kaksi kertaa Pythonia hitaampi, ja
taulukko 30–40 kertaa listaa ja 60–75 kertaa alkiokutsuja nopeampi.

Ensimmäinen havainto on tärkein: **C++-funktion kutsuminen alkio
kerrallaan oli hitaampaa kuin sama lasku Pythonilla.** Pythonin
`x * x` on yksi tulkin käsky, kun taas C++-kutsu käy läpi
pybind11:n koko kutsukoneiston. Pieni funktio C++:lla ei nopeuta
mitään, jos kutsuja on yhtä monta kuin alkioita.

Lista ja taulukko tekevät saman laskun yhdellä kutsulla, mutta lista
oli kymmeniä kertoja hitaampi eikä yhtään Pythonin omaa silmukkaa
nopeampi. Aika ei kulunut laskuun vaan
muunnoksiin: 200 000 Python-liukulukua purettiin vektoriin ja 200 000
uutta luotiin tuloslistaan. Taulukon käsittely on pelkkä muistin
läpikäynti.

## Rajan ylitys maksaa kerran

Tästä seuraa laajennusten suunnittelun pääsääntö: **siirrä silmukka
rajan toiselle puolelle.** Rajapinnan on otettava kokonainen erä
dataa, mieluiten taulukkona, ja tehtävä koko työ yhdellä kutsulla.

- Pikselin käsittelyn sijaan koko kuva (luku 8).
- Rivin jäsennyksen sijaan koko tiedosto tai puskuri.
- Yhden näytteen suodatuksen sijaan näytelohko, ja suodattimen tila
  säilyy C++-oliossa lohkojen välillä (luku 4).
- Takaisinkutsu jokaista alkiota kohden on sama ongelma toiseen
  suuntaan: C++:sta Pythoniin kutsuminen on yhtä kallista.

Kun erä on suuri, kutsun kiinteä hinta katoaa, ja sidontakirjaston
valinnalla (luku 7) ei ole merkitystä. Kun kutsuja on paljon pakosta,
esimerkiksi tapahtumapohjaisessa rajapinnassa, nanobind tai
`METH_FASTCALL`-tyyppinen kevyt sidonta (luku 11) auttaa.

## Mittaaminen

Kutsun hinnan mittaaminen on altis virheille, koska mitattava aika
on lyhyt. Muutama sääntö:

- **Mittaa silmukassa ja jaa**, koska yksittäinen kutsu on lyhyempi
  kuin kellon tarkkuus. `timeit` tekee tämän valmiiksi:
  `python3 -m timeit -s "import hinta" "hinta.nelio(2.0)"`.
- **Paras usean ajon ajasta** (luku 2).
- **Vertaa samaan työhön.** Listan ja taulukon vertailussa molemmat
  tuottavat saman tuloksen, ja esimerkki tarkistaa sen.
- **Tulosta suhdeluvut, älä testaa niitä tiukasti.** Esimerkki
  tulostaa tarkat suhteet virhetulosteeseen ja testaa vain väljiä
  rajoja, jotta testi ei kaadu hitaalla tai kuormitetulla koneella.
- **Optimointi päälle.** `-O0`-käännöksellä C++ on monta kertaa
  hitaampi, ja vertailu on merkityksetön. pybind11-mallit ovat
  erityisen herkkiä tälle.

Natiivikoodin sisäinen profilointi tehdään natiiviprofiloijalla:
`perf record python3 main.py` ja `perf report` näyttävät C++-funktiot
ja pybind11:n kutsukoneiston omina riveinään. Python 3.12:sta alkaen
`python3 -X perf` lisää samaan näkymään Python-funktiot.

## Käytännössä

- **Rajapinta erille, ei alkioille.** Tämä on tärkeämpää kuin
  kielen, kääntäjän tai sidontakirjaston valinta.
- **Taulukko listan sijaan.** Listan muunnos maksaa alkiota kohden
  enemmän kuin useimmat laskut. Jos kutsujalla on lista, muunnos
  `np.asarray(lista)` on yhtä kallis mutta tehdään kerran.
- **Pieni C++-funktio ei nopeuta mitään**, jos sitä kutsutaan
  Python-silmukassa.
- **Pidä tila C++-oliossa** kutsujen välillä, jotta jokainen kutsu voi
  käsitellä uuden erän palauttamatta välituloksia Pythonille.
- **Sudenkuoppa:** mikrovertailun tulos ei kerro kokonaisuudesta.
  Mittaa lopuksi koko ohjelma, koska muunnokset ja kopiot vaiheiden
  välillä voivat syödä hyödyn (luku 2).

## Itsearviointi

- Osaat kertoa, mistä Python–C++-kutsun hinta koostuu ja miksi se on
  usein suurempi kuin laskun hinta.
- Osaat suunnitella laajennuksen rajapinnan niin, että silmukka on
  C++:n puolella ja data kulkee taulukkoina.
- Osaat mitata kutsun hinnan luotettavasti ja kirjoittaa mittauksesta
  testin, joka ei riipu koneen nopeudesta.
