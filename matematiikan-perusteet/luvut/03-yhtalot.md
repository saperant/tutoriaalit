# Lausekkeet, yhtälöt ja epäyhtälöt

Yhtälön ratkaiseminen on matematiikan perustaito, ja juuri siinä
symbolinen laskenta säästää eniten aikaa ja virheitä. Luvussa käydään
läpi polynomit ja rationaalilausekkeet, toisen asteen yhtälö, yhtälöparit
sekä itseisarvo- ja epäyhtälötehtävät. Sovelluksena lasketaan, kuinka
kovaa autolla voi ajaa, jotta se pysähtyy annetulla matkalla.

## Polynomit

**Polynomi** on lauseke $a_n x^n + \dots + a_1 x + a_0$. Sen
**nollakohdat** eli **juuret** ovat ne $x$:n arvot, joilla lauseke on
nolla. Jos $x = r$ on juuri, $x - r$ on polynomin tekijä
(**jäännöslause**): jakolasku $p(x) / (x - r)$ menee tasan, ja jakojäännös
on $p(r)$. Tekijöihin jakaminen ja juuret ovat siis saman asian kaksi
puolta.

```{.python tiedosto="esimerkit/03-polynomit.py" osa="polynomit"}
```

`sp.roots` palauttaa juuret ja niiden **kertaluvut**: kaksinkertainen
juuri tarkoittaa, että tekijä esiintyy toisessa potenssissa, ja kuvaaja
sivuaa $x$-akselia leikkaamatta sitä. `sp.div` tekee jakolaskun ja
palauttaa osamäärän ja jakojäännöksen.

## Rationaalilausekkeet ja määrittelyehto

**Rationaalilauseke** on kahden polynomin osamäärä. Sen
**määrittelyehto** on, että nimittäjä ei ole nolla. Supistaminen voi
hävittää määrittelyehdon näkyvistä: lauseke
$\frac{x^2 - 4}{x^2 - 5x + 6}$ supistuu muotoon $\frac{x + 2}{x - 3}$,
mutta alkuperäinen lauseke ei ole määritelty kohdassa $x = 2$, vaikka
supistettu on. SymPyn `cancel` supistaa varoittamatta, joten
määrittelyehto lasketaan erikseen alkuperäisen lausekkeen nimittäjästä.

```{.python tiedosto="esimerkit/03-polynomit.py" osa="rationaali"}
```

**Osamurtohajotelma** kirjoittaa rationaalilausekkeen yksinkertaisempien
murtolausekkeiden summana. Sitä tarvitaan integroinnissa ja
Laplace-muunnoksessa (taidot *Differentiaali- ja integraalilaskenta* ja
*Differentiaaliyhtälöt ja Laplace-muunnos*). `apart` tekee hajotelman, ja
`together` kokoaa sen takaisin.

```{.python tiedosto="esimerkit/03-polynomit.py" osa="osamurrot"}
```

```{.tuloste tiedosto="esimerkit/03-polynomit.odotettu"}
```

## Toisen asteen yhtälö

Yhtälön $ax^2 + bx + c = 0$ ratkaisukaava on

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}.$$

**Diskriminantti** $D = b^2 - 4ac$ kertoo ratkaisujen määrän: kaksi
reaalista, kun $D > 0$, yksi kaksinkertainen, kun $D = 0$, ja ei yhtään
reaalista (mutta kaksi kompleksista), kun $D < 0$. SymPy johtaa kaavan
itse, kun kertoimet ovat symboleja.

```{.python tiedosto="esimerkit/03-toinen-aste.py" osa="kaava"}
```

### Kumoutuminen: kun oikea kaava antaa väärän tuloksen

Ratkaisukaava on matemaattisesti oikein, mutta liukuluvuilla se voi
antaa pahasti väärän tuloksen. Yhtälön $x^2 - 10^8 x + 1 = 0$ juuret ovat
noin $10^8$ ja $10^{-8}$. Pienen juuren kaavassa vähennetään toisistaan
kaksi lähes yhtä suurta lukua, $-b \approx 10^8$ ja
$\sqrt{D} \approx 10^8$, jolloin merkitsevät numerot kumoutuvat ja jäljelle
jää pyöristysvirhe. Tätä kutsutaan **kumoutumiseksi** (engl.
*catastrophic cancellation*).

Korjaus on laskea ensin itseisarvoltaan suurempi juuri, jossa ei
vähennetä, ja pieni juuri **Vietan kaavasta** $x_1 x_2 = c/a$.

```{.python tiedosto="esimerkit/03-toinen-aste.py" osa="kumoutuminen"}
```

```{.tuloste tiedosto="esimerkit/03-toinen-aste.odotettu"}
```

Naiivi kaava antaa pienelle juurelle $7{,}45 \cdot 10^{-9}$, mikä on 25
prosenttia väärin. Vakaa kaava ja SymPyn tarkka ratkaisu antavat
$10^{-8}$. Esimerkki näyttää, miksi tarkka symbolinen laskenta on hyvä
vertailukohta numeeriselle koodille: ilman sitä virhettä ei huomaisi.
Liukulukujen virheistä enemmän taidossa *Numeeriset menetelmät*.

## Yhtälöparit ja -ryhmät

Lineaarisen yhtälöparin ratkaisu on yksi piste, ääretön joukko (yhtälöt
ovat saman suoran yhtälöitä) tai tyhjä joukko (suorat ovat
yhdensuuntaiset). `linsolve` kertoo kaikki kolme tapausta: äärettömän
ratkaisujoukon se ilmaisee parametrin avulla.

```{.python tiedosto="esimerkit/03-yhtalopari.py" osa="lineaarinen"}
```

Sama toimii useammalle tuntemattomalle. Suuret lineaariset yhtälöryhmät
ratkaistaan matriiseilla, mikä on taidon *Lineaarialgebra* aihe.

```{.python tiedosto="esimerkit/03-yhtalopari.py" osa="kolme"}
```

Epälineaarisessa ryhmässä on yleensä useita ratkaisuja. Suorakulmion,
jonka piiri on 14 ja ala 12, sivut ovat 3 ja 4. SymPy antaa kaksi
ratkaisua, koska se ei tiedä, kumpaa sivua kutsumme leveydeksi. Ympyrän ja
suoran leikkauspisteisiin palataan luvussa 7.

```{.python tiedosto="esimerkit/03-yhtalopari.py" osa="epalineaarinen"}
```

```{.tuloste tiedosto="esimerkit/03-yhtalopari.odotettu"}
```

## Itseisarvo ja epäyhtälöt

**Itseisarvo** $|a|$ on luvun etäisyys nollasta. Siksi $|x - 2| = 3$
tarkoittaa, että $x$:n etäisyys luvusta 2 on 3, eli $x = -1$ tai $x = 5$,
ja $|x - 2| < 3$ tarkoittaa avointa väliä $-1 < x < 5$.

**Epäyhtälön** ratkaisu on joukko, yleensä väli tai välien yhdiste.
SymPyn merkinnät ovat:

| SymPy | Matematiikka | Merkitys |
|-------|--------------|----------|
| `Interval(a, b)` | $[a, b]$ | Suljettu väli |
| `Interval.open(a, b)` | $]a, b[$ | Avoin väli |
| `Interval.Lopen(a, b)` | $]a, b]$ | Vasemmalta avoin |
| `Interval.Ropen(a, b)` | $[a, b[$ | Oikealta avoin |
| `Union(A, B)` | $A \cup B$ | Yhdiste |
| `oo` | $\infty$ | Ääretön, aina avoin päätepiste |

`solveset` ratkaisee epäyhtälön, kun perusjoukoksi annetaan reaaliluvut.
Symboli kannattaa luoda oletuksella `real=True`, koska epäyhtälöt eivät
ole määriteltyjä kompleksiluvuille.

```{.python tiedosto="esimerkit/03-epayhtalot.py" osa="itseisarvo"}
```

```{.python tiedosto="esimerkit/03-epayhtalot.py" osa="epayhtalot"}
```

Käsin rationaaliepäyhtälö ratkaistaan **merkkikaaviolla**: osoittajan ja
nimittäjän nollakohdat jakavat lukusuoran väleihin, ja lausekkeen merkki
on kullakin välillä vakio. Sama ajatus toimii tarkistuksena koneelle:
valitaan testipiste jokaiselta väliltä ja kustakin rajakohdasta.
Nimittäjän nollakohta $x = -2$ ei kuulu joukkoon, koska lauseke ei ole
siinä määritelty, kun taas osoittajan nollakohta $x = 1$ kuuluu, koska
ehto on $\le 0$.

```{.python tiedosto="esimerkit/03-epayhtalot.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/03-epayhtalot.odotettu"}
```

## Samat laskut Maximalla

Maximan `solve` ratkaisee yhtälöt, `divide` jakaa polynomit ja
`partfrac` tekee osamurtohajotelman. Epäyhtälöille on lisäpaketti
`fourier_elim`, joka palauttaa ratkaisun ehtojen listana.

```{.maxima tiedosto="esimerkit/maxima/03-yhtalot.mac" osa="polynomit"}
```

```{.maxima tiedosto="esimerkit/maxima/03-yhtalot.mac" osa="yhtalot"}
```

```{.maxima tiedosto="esimerkit/maxima/03-yhtalot.mac" osa="epayhtalot"}
```

```{.tuloste tiedosto="esimerkit/maxima/03-yhtalot.odotettu"}
```

## Sovellus: pysähtymismatka

Auton pysähtymismatka koostuu **reaktiomatkasta** $v t_r$, jonka auto
kulkee ennen kuin kuljettaja jarruttaa, ja **jarrutusmatkasta**
$v^2/(2a)$, jossa $a$ on hidastuvuus. Kysytään: millä nopeudella auto
pysähtyy 50 metrissä?

$$v t_r + \frac{v^2}{2a} = s$$

on toisen asteen yhtälö nopeuden $v$ suhteen. Kun symbolit ovat
positiivisia, SymPy palauttaa vain positiivisen juuren.

```{.python tiedosto="esimerkit/03-pysahtyminen.py" osa="malli"}
```

```{.python tiedosto="esimerkit/03-pysahtyminen.py" osa="arvot"}
```

```{.tuloste tiedosto="esimerkit/03-pysahtyminen.odotettu"}
```

Kuivalla tiellä 50 metriin riittää noin 73 km/h, jäällä vain 33 km/h.
Malli on yksinkertaistus (hidastuvuus vaihtelee renkaiden, tien ja
jarrujen mukaan), mutta se näyttää, miksi nopeusrajoitukset ovat
talvella alempia: jarrutusmatka kasvaa nopeuden neliössä.

## Käytännössä

- **Määrittelyehto ensin.** Kirjoita rationaalilausekkeen ja juuren
  määrittelyehto ylös ennen supistamista tai neliöön korottamista. Kone ei
  muistuta siitä.
- **Tarkista ratkaisu sijoittamalla.** Neliöön korottaminen ja
  kertominen muuttujalla voivat tuottaa vääriä juuria, jotka sijoitus
  paljastaa.
- **Käytä oletuksia.** `positive=True` pudottaa fysikaalisesti
  mahdottomat negatiiviset ratkaisut automaattisesti.
- **Älä luota ratkaisukaavaan liukuluvuilla, kun kertoimet ovat hyvin
  eri suuruisia.** Laske iso juuri ensin ja pieni Vietan kaavasta, tai
  käytä valmista kirjastoa (`numpy.roots`), joka hoitaa asian.
- **Testaa ratkaisujoukko testipisteillä.** Valitse piste jokaiselta
  väliltä ja jokaisesta rajakohdasta.

## Itsearviointi

- Osaat jakaa polynomin tekijöihin, löytää sen juuret ja selittää
  jäännöslauseen.
- Osaat määrittää rationaalilausekkeen määrittelyehdon ja tiedät, miksi
  supistaminen voi kadottaa sen.
- Osaat ratkaista toisen asteen yhtälön ja selittää, milloin
  ratkaisukaava antaa liukuluvuilla väärän tuloksen ja miten se
  korjataan.
- Osaat ratkaista lineaarisen ja epälineaarisen yhtälöparin sekä
  tulkita tyhjän ja äärettömän ratkaisujoukon.
- Osaat ratkaista itseisarvo- ja rationaaliepäyhtälöitä sekä tarkistaa
  ratkaisujoukon testipisteillä.
