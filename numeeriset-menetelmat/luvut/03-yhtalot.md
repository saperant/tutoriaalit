# Epälineaariset yhtälöt

Yhtälön $f(x) = 0$ ratkaiseminen on numeriikan perustehtävä: mitoitus
(millä halkaisijalla jännitys on sallittu), tasapainotila (missä
lämpötilassa tuotto ja häviö ovat yhtä suuret) ja käänteinen laskenta
(mikä korko tuottaa annetun nykyarvon). Taidossa *Differentiaali- ja
integraalilaskenta* Newtonin menetelmä ja SciPyn `brentq` esiteltiin.
Tässä luvussa menetelmiä vertaillaan virheanalyysin avulla:
kuinka nopeasti ne suppenevat, milloin ne epäonnistuvat ja mitä
herkkyys tarkoittaa juurille.

## Puolitushaku ja etukäteen tunnettu virhe

Jos jatkuva funktio vaihtaa merkkiä välillä $[a, b]$, välillä on juuri
(Bolzanon lause). **Puolitushaku** puolittaa välin ja säilyttää sen
puolikkaan, jossa merkki vaihtuu. Sen suuri etu on, että virhe tiedetään
etukäteen: $k$ puolituksen jälkeen keskipiste on enintään
$(b-a)/2^{k+1}$ päässä juuresta.

```{.python tiedosto="esimerkit/03-puolitus.py" osa="puolitus"}
```

Keskipiste lasketaan muodossa `a + (b - a) / 2`. Se pysyy aina
välillä $[a, b]$, kun taas `(a + b) / 2` voi pyöristyä välin
ulkopuolelle ja suurilla luvuilla ylivuotaa. Merkkivertailu
`(fc < 0) == (fa < 0)` välttää tulon `fc * fa`, joka voi alivuotaa
nollaksi.

```{.python tiedosto="esimerkit/03-puolitus.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/03-puolitus.odotettu"}
```

Kierrosten määrä on täsmälleen ennustettu. Jokainen kierros antaa yhden
bitin, eli noin 3,3 kierrosta kymmenjärjestelmän numeroa kohden.
Puolitus on hidas mutta varma: se ei koskaan karkaa eikä tarvitse
derivaattaa.

## Kiintopisteiteraatio

Yhtälö kirjoitetaan muotoon $x = g(x)$, ja iteroidaan
$x_{k+1} = g(x_k)$. Jos $g$ on derivoituva ja $|g'(x^*)| < 1$
juuren ympäristössä, iteraatio suppenee, ja virhe pienenee joka
kierroksella noin kertoimella $|g'(x^*)|$:

$$x_{k+1} - x^* = g(x_k) - g(x^*) \approx g'(x^*)(x_k - x^*).$$

```{.python tiedosto="esimerkit/03-kiintopiste.py" osa="iteraatio"}
```

```{.python tiedosto="esimerkit/03-kiintopiste.py" osa="cos"}
```

Saman yhtälön voi kirjoittaa kiintopistemuotoon monella tavalla, ja
valinta ratkaisee:

```{.python tiedosto="esimerkit/03-kiintopiste.py" osa="sqrt2"}
```

```{.tuloste tiedosto="esimerkit/03-kiintopiste.odotettu"}
```

Muodossa $x = 2/x$ derivaatta on juuressa $-1$, joten iteraatio heiluu
arvojen 1 ja 2 välillä. Muodossa $x = (x + 2/x)/2$ derivaatta on juuressa
nolla, ja suppeneminen on neliöllistä: tämä on Newtonin menetelmä
neliöjuurelle, jota babylonialaiset käyttivät jo lähes 4000 vuotta sitten.

## Suppenemisen kertaluku

Menetelmän **kertaluku** $p$ kertoo, miten virhe $e_k = |x_k - x^*|$
pienenee: $e_{k+1} \approx C e_k^p$. Kertaluvulla 1 (lineaarinen)
saadaan joka kierroksella sama määrä numeroita, kertaluvulla 2
(neliöllinen) oikeiden numeroiden määrä kaksinkertaistuu. Kertaluku
voidaan mitata kokeellisesti kolmesta peräkkäisestä virheestä:

$$p \approx \frac{\log(e_{k+1}/e_k)}{\log(e_k/e_{k-1})}.$$

Mittaus vaatii, että virheet näkyvät monen kierroksen ajan.
Kaksoistarkkuudella Newton saavuttaa pyöristystason kolmessa
neljässä kierroksessa, joten esimerkki laskee 80 numeron tarkkuudella
Pythonin `decimal`-moduulilla.

```{.python tiedosto="esimerkit/03-kertaluku.py" osa="menetelmat"}
```

**Sekanttimenetelmä** korvaa Newtonin derivaatan kahden edellisen
pisteen kautta kulkevan suoran kulmakertoimella. Se ei tarvitse
derivaattaa ja käyttää vain yhden funktion arvon kierrosta kohden.

```{.python tiedosto="esimerkit/03-kertaluku.py" osa="kertaluku"}
```

Kun juuri on **moninkertainen**, $f'(x^*) = 0$, ja Newtonin
menetelmän neliöllisyys katoaa. Jos kertaluku $m$ tiedetään, askel
kerrotaan luvulla $m$:

```{.python tiedosto="esimerkit/03-kertaluku.py" osa="moninkertainen"}
```

```{.tuloste tiedosto="esimerkit/03-kertaluku.odotettu"}
```

Mitatut kertaluvut ovat teorian mukaiset: kiintopiste 1, sekantti
kultainen leikkaus $1{,}618$ ja Newton 2. Sekantti on kertaluvultaan
hitaampi, mutta koska se laskee vain yhden funktion arvon kierroksella
ja Newton kaksi (funktio ja derivaatta), sekantti on funktion arvoa
kohden usein nopeampi. Kaksinkertaisella juurella Newtonin virhe vain
puolittuu kierroksittain.

**Brentin menetelmä** (`scipy.optimize.brentq`, Octaven `fzero`)
yhdistää puolituksen varmuuden ja sekantin sekä käänteisen
neliöllisen interpoloinnin nopeuden: se pitää juuren aina
merkinvaihtovälissä ja käyttää nopeaa askelta, kun se pysyy välissä.
Se on yhden muuttujan juurenhaun oletusvalinta.

## Polynomien juuret ja niiden herkkyys

Polynomin juuret löytyvät luotettavimmin **kumppanimatriisin**
ominaisarvoina: NumPyn `roots` ja Octaven `roots` toimivat näin. Juuret
voivat silti olla äärimmäisen herkkiä kertoimille. James Wilkinson
havaitsi tämän 1960-luvulla polynomilla

$$w(x) = (x-1)(x-2)\cdots(x-20),$$

jonka juuret ovat kokonaisluvut 1–20 ja jotka ovat selvästi erillään.

```{.python tiedosto="esimerkit/03-wilkinson.py" osa="wilkinson"}
```

```{.python tiedosto="esimerkit/03-wilkinson.py" osa="herkkyys"}
```

```{.tuloste tiedosto="esimerkit/03-wilkinson.odotettu"}
```

Kun kertoimen $-210$ muuttaa määrällä $2^{-23} \approx 10^{-7}$,
kymmenen juurta muuttuu kompleksisiksi, ja imaginaariosat ovat
suuruusluokaltaan yksi. Herkkyys $|\partial r/\partial a| =
r^{19}/|w'(r)|$ on juurelle 16 noin $2{,}4 \cdot 10^9$, joten
kertoimen muutos $10^{-7}$ siirtää juurta satoja yksiköitä
ensimmäisen kertaluvun arviossa. Tulos ei johdu algoritmista vaan
siitä, että *juuret ovat huonokuntoinen funktio kertoimista*.
Opetus: jos sovellus tarvitsee polynomin juuria, polynomia ei kannata
esittää kertoimina, jos se voidaan välttää. Esimerkiksi
ominaisarvotehtävää ei ratkaista karakteristisen polynomin kautta.

## Yhtälöryhmät: Newtonin menetelmä usealle muuttujalle

Yhtälöryhmälle $F(x) = 0$, jossa $F: \mathbb{R}^n \to \mathbb{R}^n$,
Newtonin menetelmä linearisoi $F$:n Jacobin matriisilla $J$ ja ratkaisee
joka kierroksella lineaarisen yhtälöryhmän $J(x_k)\,\Delta x = -F(x_k)$.
Käänteismatriisia ei muodosteta (luku 6).

```{.python tiedosto="esimerkit/03-jarjestelma.py" osa="malli"}
```

```{.python tiedosto="esimerkit/03-jarjestelma.py" osa="newton"}
```

```{.python tiedosto="esimerkit/03-jarjestelma.py" osa="scipy"}
```

```{.tuloste tiedosto="esimerkit/03-jarjestelma.odotettu"}
```

Jäännös $|F|$ pienenee neliöllisesti: $4 \cdot 10^{-2}$, $10^{-4}$,
$8 \cdot 10^{-10}$ ja pyöristystaso. Suurissa tehtävissä Jacobin matriisin
laskeminen ja hajottaminen joka kierroksella on kallista, joten
käytännön ratkaisijat käyttävät **kvasi-Newton-menetelmiä**, jotka
päivittävät Jacobin arviota (Broyden), ja **vaimennusta** tai
**luottamusalueita**, jotka estävät liian pitkät askeleet kaukana
juuresta. SciPyn `optimize.root` oletusmenetelmä `hybr` on Powellin
hybridimenetelmä, joka tekee juuri näin.

## Sama Octavella

```{.octave tiedosto="esimerkit/octave/03-juuret.m"}
```

```{.tuloste tiedosto="esimerkit/octave/03-juuret.odotettu"}
```

Octavessa skriptin alussa oleva lause `1;` kertoo, että tiedosto on
skripti eikä funktiotiedosto; muuten tiedostossa määriteltyä funktiota
ei voi käyttää. Funktiot määritellään ennen käyttöä.

## Käytännössä

- **Rajaa juuri ensin.** Kuvaaja tai merkinvaihdon etsiminen
  karkealla ruudukolla kertoo, montako juurta on ja missä. Sen jälkeen
  `brentq` välillä on varma ja nopea.
- **Newton on paras, kun derivaatta on halpa ja alkuarvo hyvä.**
  Kaukana juuresta se voi karata; vaimennettu Newton tai
  yhdistelmämenetelmä on turvallisempi.
- **Lopetusehto tarvitsee sekä askeleen että jäännöksen.** Pieni askel
  ei takaa pientä jäännöstä (moninkertainen juuri), eikä pieni jäännös
  takaa tarkkaa juurta (huonokuntoinen juuri).
- **Hidastuminen lineaariseksi on oire.** Jos Newton suppenee yllättävän
  hitaasti, juuri on todennäköisesti moninkertainen tai derivaatta on
  väärin. Tarkista derivaatta erotusosamäärällä (luku 5).
- **Älä esitä polynomeja kertoimina, jos juuret ovat tärkeitä.**
  Tulomuoto, ominaisarvotehtävä tai ortogonaalinen kanta on
  hyväkuntoisempi.
- **Yhtälöryhmille anna Jacobin matriisi, jos se on saatavilla.**
  Numeerisesti arvioitu Jacobi maksaa $n$ ylimääräistä funktion arvoa
  kierroksella ja on epätarkempi.

## Itsearviointi

- Osaat toteuttaa puolitushaun turvallisesti ja laskea etukäteen,
  montako kierrosta annettu tarkkuus vaatii.
- Osaat päätellä kiintopisteiteraation suppenemisen derivaatasta
  $g'(x^*)$ ja valita yhtälölle suppenevan kiintopistemuodon.
- Osaat mitata menetelmän suppenemisen kertaluvun kokeellisesti ja
  tunnistaa lineaarisen, superlineaarisen ja neliöllisen suppenemisen.
- Osaat selittää, miksi moninkertainen juuri hidastaa Newtonin
  menetelmää ja miten se korjataan.
- Osaat selittää Wilkinsonin polynomin opetuksen juurten herkkyydestä.
- Osaat ratkaista epälineaarisen yhtälöryhmän Newtonin menetelmällä ja
  kirjastofunktiolla.
