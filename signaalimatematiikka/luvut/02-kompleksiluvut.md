# Kompleksiluvut

Kompleksiluku on reaalilukupari, jolla on oma kertolaskunsa. Pari
$(a, b)$ kirjoitetaan muodossa $z = a + bi$, missä $a = \operatorname{Re} z$
on **reaaliosa** ja $b = \operatorname{Im} z$ **imaginaariosa**. Uutta
on vain yksi sääntö: $i^2 = -1$. Kaikki muu seuraa tavallisista
laskusäännöistä.

Kompleksiluvut keksittiin aikanaan kolmannen asteen yhtälöiden
ratkaisukaavojen sivutuotteena, mutta insinöörille niiden hyöty on
geometrinen. Kompleksiluku on tason piste tai nuoli, ja
kompleksilukujen kertolasku kiertää ja skaalaa nuolia. Koska
sinimuotoinen signaali on pohjimmiltaan pyörivä nuoli, kompleksiluvut
ovat sille luonteva kieli.

## Kompleksitaso ja laskutoimitukset

Kompleksiluku $z = a + bi$ piirretään **kompleksitasoon** pisteeksi
$(a, b)$: vaaka-akseli on reaaliakseli ja pystyakseli imaginaariakseli.
Yhteenlasku tehdään osittain, kuten vektoreilla:

$$(a + bi) + (c + di) = (a + c) + (b + d)i.$$

Kertolasku saadaan kertomalla sulut auki ja käyttämällä sääntöä
$i^2 = -1$:

$$(a + bi)(c + di) = ac + adi + bci + bdi^2 = (ac - bd) + (ad + bc)i.$$

**Liittoluku** $\bar z = a - bi$ peilaa luvun reaaliakselin suhteen.
Luvun ja sen liittoluvun tulo on aina reaalinen ja ei-negatiivinen:

$$z \bar z = (a + bi)(a - bi) = a^2 + b^2 = |z|^2,$$

missä $|z| = \sqrt{a^2 + b^2}$ on **itseisarvo** eli pisteen etäisyys
origosta. Tästä saadaan jakolasku: kerrotaan osoittaja ja nimittäjä
nimittäjän liittoluvulla, jolloin nimittäjästä tulee reaalinen,

$$\frac{z}{w} = \frac{z \bar w}{w \bar w} = \frac{z \bar w}{|w|^2}.$$

Esimerkiksi
$\frac{3 + 4i}{1 - 2i} = \frac{(3 + 4i)(1 + 2i)}{1 + 4} = \frac{-5 + 10i}{5} = -1 + 2i$.

Pythonissa kompleksiluvut ovat sisäänrakennettu tyyppi `complex`.
Imaginaariyksikkö kirjoitetaan luvun perään liitettynä `j`:nä, joten
`3 + 4j` on kompleksiluku ja `4j` sen imaginaariosa. Pelkkä `j` on
muuttujan nimi, ei imaginaariyksikkö; imaginaariyksikkö on `1j`.

```{.python tiedosto="esimerkit/02-aritmetiikka.py" osa="perus"}
```

Esimerkin apufunktio `kl` muotoilee kompleksiluvun pyöristettynä
merkinnällä `a + bi`. Pythonin oma esitys `(3+4j)` on tarkka mutta
kömpelö lukea, ja pyöristetyssä esityksessä on varottava negatiivista
nollaa: `round(-1e-17, 3)` on `-0.0`, joka tulostuisi muodossa `-0.000`.
Lisäämällä `0.0` miinusnolla muuttuu tavalliseksi nollaksi.

## Napakoordinaatit: pituus ja kulma

Tason pisteen voi antaa myös etäisyytenä origosta ja kulmana
positiivisesta reaaliakselista. Kompleksiluvun **napaesitys** on

$$z = r(\cos\varphi + i \sin\varphi),$$

missä $r = |z|$ ja $\varphi = \arg z$ on **vaihekulma** eli
**argumentti**. Muunnokset suorakulmaisesta muodosta napamuotoon ja
takaisin ovat

$$r = \sqrt{a^2 + b^2}, \quad \varphi = \operatorname{atan2}(b, a), \qquad
a = r \cos\varphi, \quad b = r \sin\varphi.$$

Kulma lasketaan funktiolla `atan2(b, a)` eikä lausekkeella
$\arctan(b/a)$, koska jälkimmäinen ei erota vastakkaisia neljänneksiä:
luvuilla $1 + i$ ja $-1 - i$ on sama osamäärä $b/a = 1$. Pythonin
moduuli `cmath` tarjoaa muunnokset valmiina: `cmath.polar(z)` palauttaa
parin $(r, \varphi)$, `cmath.phase(z)` pelkän kulman ja
`cmath.rect(r, phi)` rakentaa luvun napaesityksestä.

```{.python tiedosto="esimerkit/02-aritmetiikka.py" osa="napa"}
```

```{.tuloste tiedosto="esimerkit/02-aritmetiikka.odotettu"}
```

Kulma on aina välillä $(-\pi, \pi]$, ja sen arvo hyppää negatiivisella
reaaliakselilla: luku $-1$ saa kulman $\pi$, mutta luku, jonka
imaginaariosa on negatiivinen nolla (`complex(-1, -0.0)`), saa kulman
$-\pi$. Tällainen **haarakatkos** on väistämätön, koska kulman
$\varphi$ ja $\varphi + 2\pi$ esittävät samaa pistettä. Käytännössä se
tarkoittaa, että vaihekulmia ei voi vertailla suoraan: kulmat $3.14$ ja
$-3.14$ ovat lähes samat. Vaiheiden erotus kannattaa laskea
kompleksilukujen osamääränä, `cmath.phase(z / w)`, jolloin tulos on
automaattisesti välillä $(-\pi, \pi]$. Signaalinkäsittelyssä vaiheen
"avaaminen" jatkuvaksi käyräksi (`numpy.unwrap`) on oma operaationsa.

| Muoto | Merkintä | Hyvä laskuun |
|------------------|------------------------------|------------------------------|
| suorakulmainen | $a + bi$ | yhteen- ja vähennyslasku |
| napaesitys | $r(\cos\varphi + i\sin\varphi)$ | kerto- ja jakolasku, potenssit |
| eksponenttimuoto | $re^{i\varphi}$ | sama kuin napaesitys, lyhyemmin |

Eksponenttimuoto $re^{i\varphi}$ on luvun 3 aihe. Toistaiseksi se on
vain lyhennysmerkintä napaesitykselle.

## Kertolasku on kierto ja skaalaus

Napaesityksessä kertolasku saa yksinkertaisen muodon. Kun
$z = r(\cos\alpha + i\sin\alpha)$ ja $w = s(\cos\beta + i\sin\beta)$,
niin

$$zw = rs\big[(\cos\alpha\cos\beta - \sin\alpha\sin\beta)
+ i(\sin\alpha\cos\beta + \cos\alpha\sin\beta)\big],$$

ja kosinin ja sinin summakaavojen mukaan sulkeissa ovat summakulman
kosini ja sini:

$$zw = rs\big(\cos(\alpha + \beta) + i\sin(\alpha + \beta)\big).$$

**Kertolaskussa
itseisarvot kerrotaan ja kulmat lasketaan yhteen.** Luvulla $w$
kertominen siis kiertää tason jokaista pistettä kulman $\arg w$ verran
ja skaalaa sitä kertoimella $|w|$. Erikoistapauksina:

- Kertominen luvulla $i$ kiertää 90 astetta vastapäivään:
  $i(a + bi) = -b + ai$. Kahdesti kiertäminen antaa $i^2 = -1$, eli
  puolen kierroksen.
- Kertominen yksikköympyrän luvulla ($|w| = 1$) on puhdas kierto.
- Kertominen positiivisella reaaliluvulla on puhdas skaalaus.
- Liittoluvun ottaminen ei ole kertolasku vaan peilaus; se kääntää
  kulman merkin.

Seuraava esimerkki kertoo neliön kärkipisteet luvulla, jonka itseisarvo
on 2 ja kulma 30 astetta. Sama kuvaus on lineaarialgebran kielellä
$2 \times 2$ -matriisi: luku $w = a + bi$ vastaa matriisia

$$M_w = \begin{pmatrix} a & -b \\ b & a \end{pmatrix}
= |w| \begin{pmatrix} \cos\varphi & -\sin\varphi \\ \sin\varphi & \cos\varphi \end{pmatrix},$$

eli kiertomatriisia kerrottuna luvulla $|w|$.

```{.python tiedosto="esimerkit/02-kierto.py" osa="kierto"}
```

```{.tuloste tiedosto="esimerkit/02-kierto.odotettu"}
```

![Neliö ennen kertolaskua ja sen jälkeen. Jokainen kärki kiertyy 30
astetta origon ympäri ja etääntyy siitä
kaksinkertaiseksi.](kuvat/kierto.png){width=50%}

Kompleksilukujen kertolasku on siis tason kiertojen ja skaalausten
ryhmä tiiviissä muodossa. Matriisissa on neljä lukua, joista vain kaksi
on vapaita; kompleksiluku tallentaa juuri ne kaksi. Lisäksi
kompleksilukujen kertolasku on vaihdannainen, kuten tason kiertojen
yhdistäminenkin: ensin 30 ja sitten 45 astetta on sama kuin ensin 45 ja
sitten 30.

## Kompleksiluvut NumPyssa

NumPyn taulukon alkiotyyppi `complex128` tallentaa kunkin luvun kahtena
64-bittisenä liukulukuna. Funktiot `numpy.abs`, `numpy.angle` ja
`numpy.conj` toimivat alkioittain, ja ominaisuudet `.real` ja `.imag`
antavat reaali- ja imaginaariosat omina taulukkoinaan. Funktio
`numpy.angle` palauttaa kulman radiaaneina tai argumentilla `deg=True`
asteina.

```{.python tiedosto="esimerkit/02-numpy.py" osa="numpy"}
```

```{.tuloste tiedosto="esimerkit/02-numpy.odotettu"}
```

Lauseke `numpy.exp(1j * numpy.angle(z))` normittaa luvut
yksikköympyrälle: jäljelle jää pelkkä suunta. Tämä on tavallinen
operaatio, kun signaalista halutaan vain vaihe.

Kaksi sudenkuoppaa on hyvä tietää. Ensiksi reaalitaulukko ei muutu
kompleksiseksi itsestään: `numpy.sqrt(numpy.array([-1.0]))` antaa
tuloksen `nan` ja varoituksen, kun taas `numpy.sqrt(numpy.array([-1+0j]))`
antaa `1j`. Toiseksi kompleksitaulukon sijoittaminen reaalitaulukon
viipaleeseen (`a[:] = z`) hylkää imaginaariosan pelkän varoituksen
(`ComplexWarning`) kera, ja virhe huomataan vasta tuloksista. Kun
lasket kompleksiluvuilla, luo taulukot alusta asti tyypillä
`complex128`, esimerkiksi `numpy.zeros(n, dtype=numpy.complex128)`.

## Käytännössä

- **Kirjoita imaginaariyksikkö muodossa `1j`.** Pelkkä `j` on
  muuttuja, ja `2*j` on eri asia kuin `2j`.
- **Laske kulmat `atan2`:lla tai `cmath.phase`:lla.** Pelkkä
  `atan(b / a)` sekoittaa vastakkaiset neljännekset ja kaatuu, kun
  $a = 0$.
- **Vertaa vaiheita osamäärän kautta.** `cmath.phase(z / w)` antaa
  vaihe-eron oikealta väliltä ilman käsin tehtäviä $2\pi$-korjauksia.
- **Ajattele kertolaskua kiertona.** Kun koodi kertoo luvulla, jonka
  itseisarvo on 1, se kiertää; kun itseisarvo poikkeaa ykkösestä, se
  myös vahvistaa tai vaimentaa.
- **Pyöristä tulosteet ja normita miinusnolla.** `round(x, 3) + 0.0`
  tekee tulosteista koneesta riippumattomia.

## Itsearviointi

- Osaat laskea kompleksilukujen summan, tulon, osamäärän ja liittoluvun
  sekä käsin että Pythonilla.
- Osaat muuntaa kompleksiluvun suorakulmaisesta muodosta napaesitykseen
  ja takaisin ja selittää, miksi kulma lasketaan `atan2`:lla.
- Osaat selittää, miksi kertolasku kompleksiluvulla kiertää ja skaalaa,
  ja kirjoittaa vastaavan $2 \times 2$ -matriisin.
- Osaat käyttää NumPyn kompleksitaulukoita ja funktioita `abs`, `angle`
  ja `conj`.
