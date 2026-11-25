# Pyöristys ja virheen kertyminen

Jokainen liukulukuoperaatio pyöristää tuloksensa, ja virhe on
enintään puoli ulp:tä. Yksittäinen virhe on mitätön, noin $10^{-16}$
binary64:ssä. Ongelmia syntyy, kun virheitä kertyy miljoonia, kun
melkein yhtä suuret luvut vähennetään toisistaan tai kun laskujen
järjestys muuttuu. Tämä luku käy ensin läpi pyöristyssäännöt ja rahan
laskemisen, jossa sääntö on osa vaatimuksia, ja sitten tilanteet, joissa
virhe kasvaa, sekä niiden korjaukset.

## Pyöristystilat ja -funktiot

IEEE 754 määrittelee neljä pyöristystilaa. Oletus on pyöristys
lähimpään esitettävään lukuun ja tasapelissä parilliseen (*round half
to even*). Muut tilat ovat ylös, alas ja kohti nollaa. Niitä
käytetään esimerkiksi intervalliaritmetiikassa, jossa laskettu väli
taataan sisältävän oikean tuloksen.

![Pyöristystilat lukusuoralla, kun tulos pyöristetään kokonaisluvuksi.
Arvot ±0,5 ja ±2,5 ovat tasapelejä: lähimpään pyöristävä tila vie ne
parilliseen lukuun. Liukulukulaskennassa asteikon paikalla ovat
esitettävät luvut.](kuvat/pyoristystilat.png){width=88%}

Kolme suunnattua tilaa tekevät virheen aina samaan suuntaan. Vain
lähimpään pyöristävä tila tekee virheitä kumpaankin suuntaan, ja siksi
se on oletus.

```{.c tiedosto="esimerkit/07-pyoristys.c" osa="tilat"}
```

Pyöristysfunktiot eroavat tasapelin käsittelyssä. `round` pyöristää
tasapelin poispäin nollasta, kuten koulussa. `rint` ja `nearbyint`
käyttävät pyöristystilaa, joka on oletuksena pyöristys parilliseen,
kuten myös Pythonin `round`. Parilliseen pyöristäminen ei vinouta
summaa, koska puolet tasapeleistä pyöristyy ylös ja puolet alas.

```{.c tiedosto="esimerkit/07-pyoristys.c" osa="funktiot"}
```

```{.tuloste tiedosto="esimerkit/07-pyoristys.odotettu"}
```

Viimeisellä rivillä 2,4999999999999996 on liukuluku, joka on
lähimpänä lukua 2,5 sen alapuolella. Väärin toteutettu pyöristys
`floor(x + 0.5)` antaisi sille tuloksen 3, koska summa pyöristyy
luvuksi 3,0.

## Raha

Rahasummat ovat tarkkoja desimaalilukuja, joten binääriliukuluku on
niille väärä tyyppi. Sentteinä tallennettu kokonaisluku tai
desimaaliaritmetiikka (`Decimal`, SQL:n `numeric`, Javan `BigDecimal`)
laskee oikein. Pyöristys tehdään kirjanpidon säännön mukaan, ja sääntö
kirjoitetaan koodiin näkyviin:

```{.python tiedosto="esimerkit/07-raha.py" osa="raha"}
```

```{.python tiedosto="esimerkit/07-raha.py" osa="alv"}
```

```{.tuloste tiedosto="esimerkit/07-raha.odotettu"}
```

Viimeinen rivi näyttää, miksi `round(2.675, 2)` antaa 2,67: liukuluku
2,675 on todellisuudessa hieman alle 2,675, joten tasapeliä ei ole.

## Katastrofaalinen kumoutuminen

Kun kaksi lähes yhtä suurta lukua vähennetään toisistaan, yhteiset
alkunumerot kumoutuvat, ja jäljelle jäävät vain epätarkat loppunumerot.
Vähennyslasku itsessään on tarkka, mutta se paljastaa aiemmin tehdyt
pyöristykset. Kun kummassakin luvussa on 16 merkitsevää numeroa ja
viimeinen niistä (`?`) on jo pyöristetty, erotukseen jää tässä vain
kaksi luotettavaa numeroa:

```text
  1,23456789012345?
- 1,23456789012311?
= 0,00000000000034?
```

Tyypillinen esimerkki on varianssin oppikirjakaava
$\overline{x^2} - \overline{x}^2$. Mikrosekunnin aikaleimat ovat
suuruusluokkaa $10^{15}$, joten niiden neliöt ovat suuruusluokkaa
$10^{30}$, ja pyöristysvirhe on niissä suurempi kuin koko vaihtelu.
Welfordin algoritmi päivittää keskiarvoa ja poikkeamien neliösummaa
yksi arvo kerrallaan eikä koskaan muodosta suuria neliöitä.

```{.c tiedosto="esimerkit/07-varianssi.c" osa="naiivi"}
```

```{.c tiedosto="esimerkit/07-varianssi.c" osa="welford"}
```

```{.tuloste tiedosto="esimerkit/07-varianssi.odotettu"}
```

Naiivi kaava antaa varianssiksi $7 \cdot 10^{16}$ ja joillakin
syötteillä negatiivisen luvun, josta neliöjuurta ei voi ottaa.
Welfordin tulos on oikea. Kumoutumisen voi usein välttää
muuttamalla kaavaa: $\sqrt{x+1} - \sqrt{x}$ on parempi laskea muodossa
$1/(\sqrt{x+1} + \sqrt{x})$, ja `log1p(x)` ja `expm1(x)` ovat
tarkkoja pienillä $x$:n arvoilla, joilla `log(1 + x)` ei ole.

## Summauksen virhe

Kun $n$ lukua lasketaan yhteen silmukassa, virheen yläraja kasvaa
$n$:n mukana. Kun summa kasvaa suureksi, pienet lisäykset menettävät
tarkkuuttaan, kuten aikaleimaesimerkissä luvussa 6. Kymmenen miljoonaa
0,1 kWh:n mittausta `float`-muuttujaan antaa yhdeksän prosentin virheen:

```{.c tiedosto="esimerkit/07-summaus.c" osa="naiivi"}
```

Kahanin kompensoitu summa pitää kirjaa jokaisessa lisäyksessä
hukatusta osasta ja lisää sen seuraavaan:

```{.c tiedosto="esimerkit/07-summaus.c" osa="kahan"}
```

Parittainen summa jakaa taulukon puoliksi ja laskee puoliskot
rekursiivisesti. Virhe kasvaa vain logaritmisesti, ja algoritmi on yhtä
nopea kuin tavallinen silmukka. NumPyn `sum` käyttää sitä.

```{.c tiedosto="esimerkit/07-summaus.c" osa="parittain"}
```

```{.tuloste tiedosto="esimerkit/07-summaus.odotettu"}
```

![Sama summa lukemien määrän funktiona. Naiivin silmukan virhe kasvaa,
kun summa kasvaa lisäyksiin nähden suureksi. Kahanin ja parittaisen
summan virhe pysyy yksittäisen pyöristyksen
tasolla.](kuvat/summaus.png){width=72%}

Naiivin summan virhe ei kasva tasaisesti, koska virheen suunta vaihtuu
summan eksponentin mukana: välillä 0,1 pyöristyy ylöspäin ja välillä
alaspäin. Suunta ei kuitenkaan vaihdu satunnaisesti, vaan sama virhe
toistuu tuhansia kertoja peräkkäin. Luku 9 palaa tähän.

Summaus ei ole liitännäinen: $(a + b) + c$ ja $a + (b + c)$ voivat
erota. Järjestyksellä on siis väliä. Pienimmät luvut kannattaa laskea
yhteen ensin. Python 3.12:n `sum` kompensoi virheen, ja `math.fsum`
antaa oikein pyöristetyn tarkan summan:

```{.python tiedosto="esimerkit/07-jarjestys.py" osa="jarjestys"}
```

```{.tuloste tiedosto="esimerkit/07-jarjestys.odotettu"}
```

Liitännäisyyden puute vaikuttaa myös rinnakkaisuuteen. Kun summa
jaetaan säikeille tai GPU:lle, tulos riippuu jaosta ja voi vaihdella
ajosta toiseen. Jos tulosten on oltava toistettavia, jako on
kiinnitettävä tai summa kompensoitava.

## Fused multiply-add

`fma(a, b, c)` laskee $a \cdot b + c$ tarkasti ja pyöristää vain kerran.
Nykyprosessoreissa se on yksi käsky. Se on sekä nopeampi että
tarkempi, ja sillä saa tulon pyöristysvirheen talteen:
`fma(a, b, -a*b)` on tarkalleen $a \cdot b$ miinus pyöristetty tulo.

```{.c tiedosto="esimerkit/07-fma.c" osa="virhe"}
```

Kun sama tehdään summille (*TwoSum*), saadaan kompensoitu pistetulo,
joka on lähes yhtä tarkka kuin kaksinkertaisella tarkkuudella laskettu:

```{.c tiedosto="esimerkit/07-fma.c" osa="pistetulo"}
```

```{.tuloste tiedosto="esimerkit/07-fma.odotettu"}
```

Kääntäjä voi yhdistää `a * b + c` -lausekkeen FMA-käskyksi itse
(*contraction*), kun kohdeprosessorissa on FMA. Tämä muuttaa tuloksia
hieman: sama ohjelma antaa eri tuloksen eri käännösvalitsimilla.
Valitsin `-ffp-contract=off` estää yhdistämisen, jos bittitarkka
toistettavuus on tärkeämpää kuin nopeus.

## `-ffast-math`

`-ffast-math` lupaa kääntäjälle, ettei ohjelmassa ole NaN:eja eikä
äärettömiä ja että laskujen järjestystä saa muuttaa vapaasti. Kääntäjä
saa silloin vektoroida summat, korvata jakolaskun käänteisluvulla
kertomisella ja sieventää lausekkeita algebran sääntöjen mukaan. Tämä
rikkoo juuri ne algoritmit, jotka ovat tarkkuuden kannalta tärkeimpiä:

```{.c tiedosto="esimerkit/07-nopea.c" osa="nopea"}
```

Esimerkkien Makefile kääntää ohjelman kahdesti:

```{.makefile tiedosto="esimerkit/Makefile" osa="nopea"}
```

Tavallisena ohjelma tulostaa summan 1000 ja yhden puuttuvan arvon.
`-ffast-math`-versiossa Kahanin korjaustermi sievenee nollaksi, joten
summa on 0, eikä `isnan` enää tunnista NaN:ia (Clang varoittaa tästä:
*use of NaN is undefined behavior*):

```{.tuloste tiedosto="esimerkit/07-nopea-ffast-math.odotettu"}
```

`-ffast-math` on perusteltu vain koodissa, jonka tarkkuusvaatimukset
tunnetaan ja joka on testattu sillä, esimerkiksi grafiikassa tai
äänenkäsittelyssä. Valitsin vaikuttaa myös linkitykseen: GCC asettaa
prosessorin käsittelemään subnormaalit lukuina nolla koko
ohjelmassa, myös kirjastoissa, jotka eivät pyytäneet sitä.

## Käytännössä

- **Summaa kompensoiden tai parittain.** Pitkät summat (kirjanpidon
  kertymät, energian kulutus, tilastot) lasketaan `math.fsum`-,
  `np.sum`- tai Kahanin summalla. Tavallinen silmukka riittää lyhyille
  summille.
- **Welford varianssille.** Oppikirjakaava $\overline{x^2} -
  \overline{x}^2$ kuuluu oppikirjoihin. Kirjastojen funktiot
  (`statistics.pvariance`, `np.var`) käyttävät vakaita menetelmiä.
- **Muotoile kaava uudelleen kumoutumisen välttämiseksi.** `log1p`,
  `expm1`, `hypot` ja vastaavat on kirjoitettu tätä varten.
- **Ei `-ffast-math`-valitsinta oletuksena.** Jos nopeutta tarvitaan,
  valitse yksittäiset lupaukset (`-fno-math-errno`,
  `-fassociative-math` vain tietyille tiedostoille) ja testaa tulokset.
- **Toistettavuus on päätös.** Bittitarkka toistettavuus eri koneilla
  vaatii kiinteän laskujärjestyksen ja `-ffp-contract=off`-valitsimen.
  Lisäksi standardi takaa oikean pyöristyksen vain perusoperaatioille
  ja neliöjuurelle: `sin`, `exp`, `pow` ja muut kirjastofunktiot voivat
  erota viimeisessä bitissä kirjastosta ja versiosta toiseen.
  Useimmiten riittää, että tulokset ovat toleranssin sisällä, ja
  testit kirjoitetaan sen mukaan.
- **Raha desimaalina tai kokonaislukuna, pyöristyssääntö näkyviin.**
  Kirjanpidossa pyöristetään vasta lopuksi ja yhdessä kohdassa.

## Itsearviointi

- Osaat selittää pyöristystilat ja eron `round`-, `rint`- ja
  `floor(x + 0.5)`-pyöristysten välillä.
- Osaat tunnistaa katastrofaalisen kumoutumisen ja korvata
  varianssin oppikirjakaavan Welfordin algoritmilla.
- Osaat toteuttaa Kahanin ja parittaisen summan ja kertoa, milloin
  niitä tarvitaan.
- Osaat kertoa, mitä `fma` ja `-ffast-math` tekevät ja miten ne
  muuttavat tuloksia.
- Osaat laskea rahasummat oikein kokonaisluvuilla tai `Decimal`-tyypillä.
