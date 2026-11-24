# Kameramalli ja kalibrointi

Tähän asti kuvia on käsitelty pelkkinä taulukoina. Kun kuvasta halutaan
mitata jotain maailmasta, kuten etäisyyksiä, kokoja tai asentoja,
tarvitaan malli siitä, miten kamera kuvaa kolmiulotteisen pisteen
pikseliksi. Taito *Renderöinnin perusteet* rakensi saman mallin toiseen
suuntaan: tunnetusta kolmiulotteisesta näkymästä laskettiin kuva.
Konenäössä tehtävä on käänteinen: kuvasta päätellään näkymä. Tässä
luvussa käydään läpi neulanreikämalli, linssivääristymä, kameran
kalibrointi ja kappaleen asennon ratkaiseminen.

## Neulanreikämalli

Neulanreikäkamerassa jokainen näkymän piste projisoituu kuvatasolle
suoraa linjaa pitkin yhden pisteen, projektiokeskuksen, kautta. Malli on
kahden muunnoksen ketju:

$$
s \begin{pmatrix} u \\ v \\ 1 \end{pmatrix}
= K\,[R \mid t] \begin{pmatrix} X \\ Y \\ Z \\ 1 \end{pmatrix},\qquad
K = \begin{pmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{pmatrix}.
$$

**Ulkoiset parametrit** $R$ ja $t$ siirtävät maailman pisteen kameran
koordinaatistoon, jossa $Z$ osoittaa kameran katsesuuntaan. **Sisäiset
parametrit** $K$ kuvaavat kameran itsensä: polttovälit $f_x$ ja $f_y$
pikseleinä sekä pääpisteen $(c_x, c_y)$, jossa optinen akseli osuu
kennoon. Kerroin $s = Z$ on syvyys, ja jakaminen sillä on projektio.
OpenCV esittää kierron yleensä **kiertovektorina** (Rodrigues):
vektorin suunta on kiertoakseli ja pituus kulma radiaaneina.

```{.python tiedosto="esimerkit/07-projektio.py" osa="kasin"}
```

```{.python tiedosto="esimerkit/07-projektio.py" osa="opencv"}
```

Projektio hävittää mittakaavan: kaksi kertaa suurempi maailma kaksi
kertaa kauempana näyttää täsmälleen samalta. Yksi kuva ei siksi riitä
etäisyyksien mittaamiseen, ellei kohteen kokoa tunneta. Tunnettu koko on
juuri se, mitä asennon ratkaiseminen ja kalibrointi käyttävät hyväkseen,
ja stereonäkö (luku 8) ratkaisee ongelman toisella kameralla.

## Linssivääristymä

Oikea linssi ei ole neulanreikä. **Säteittäinen vääristymä** siirtää
pisteitä keskeltä poispäin tai keskustaa kohti sitä enemmän, mitä
kauempana keskeltä ne ovat. Normalisoidulle pisteelle $(x, y) =
(X/Z, Y/Z)$ ja $r^2 = x^2 + y^2$ Brownin–Conradyn malli on

$$
x_d = x\,(1 + k_1 r^2 + k_2 r^4 + k_3 r^6) + \text{tangentiaaliset termit}.
$$

Kun $k_1 < 0$, kyseessä on tynnyrivääristymä (laajakulmaobjektiivit),
ja suorat viivat kaartuvat ulospäin. Vääristymä on pieni kuvan
keskellä ja kasvaa nopeasti reunoilla.

```{.python tiedosto="esimerkit/07-projektio.py" osa="vaaristyma"}
```

```{.tuloste tiedosto="esimerkit/07-projektio.odotettu"}
```

Kuvan kulmassa 23 pikselin virhe tekisi mittauksesta käyttökelvottoman.
Kun vääristymä tunnetaan, `undistort` oikaisee kuvan ja
`undistortPoints` yksittäiset pisteet.

## Synteettinen kamera

Kalibroinnin testaamiseen tarvitaan kuvia kamerasta, jonka parametrit
tunnetaan tarkasti. Esimerkissä kamera on ohjelma: se renderöi
shakkilaudan kuvan tunnetulla mallilla. Malli on tietorakenne:

```{.python tiedosto="esimerkit/07-kalibrointi/kamera.py" osa="malli"}
```

Renderöinti tehdään säteenseurannan tapaan takaperin (taito
*Säteenseuranta ja fysikaalinen valaistus*): jokaiselle pikselille
lasketaan vääristymätön suunta `undistortPoints`-funktiolla, säde
leikataan laudan tasolla, ja väri luetaan laudalta. Laudan taso
$Z = 0$ muuttaa projektion homografiaksi $[r_1\ r_2\ t]$, jonka
käänteismatriisi antaa laudan pisteen. Kuva lasketaan nelinkertaisella
tarkkuudella ja pienennetään `INTER_AREA`:lla, jotta reunat ovat
pehmeät kuten oikeassa kamerassa.

```{.python tiedosto="esimerkit/07-kalibrointi/kamera.py" osa="render"}
```

Renderöijä on testattava ennen kuin sen kuvilla testataan kalibrointia.
Muuten kalibroinnin virhe voi olla renderöijän virhe. Testit tarkistavat,
että vääristymä ja sen kumoaminen ovat toistensa käänteiset ja että
kuvasta löydetyt kulmat osuvat sinne, minne `projectPoints` ne laskee.

```{.python tiedosto="esimerkit/07-kalibrointi/test_kamera.py" osa="testit"}
```

## Kalibrointi

**Kalibrointi** ratkaisee kameran sisäiset parametrit ja vääristymän
kuvista, joissa on tunnettu kappale. Tavallisin kappale on shakkilauta:
sen sisäkulmat löytyvät luotettavasti (`findChessboardCorners`), ne
voidaan tarkentaa alipikselitarkkuuteen (`cornerSubPix`), ja niiden
sijainti laudalla tunnetaan. `calibrateCamera` sovittaa mallin
minimoimalla **uudelleenprojektiovirheen**: kuinka kaukana havaitut kulmat
ovat siitä, minne malli ne projisoi. Jokaisella kuvalla on omat
ulkoiset parametrit, ja kaikilla yhteiset sisäiset parametrit.

```{.python tiedosto="esimerkit/07-kalibrointi/main.py" osa="kalibrointi"}
```

![Synteettinen kuva shakkilaudasta tunnetulla kameralla ja vääristymällä.
Värilliset pisteet ovat löydetyt sisäkulmat.](kuvat/kalibrointi.png){width=60%}

Polttovälit ja pääpiste palautuvat alle pikselin tarkkuudella, ja $k_1$
hyvin. $k_2$ on epätarkempi: korkeamman kertaluvun termi vaikuttaa
vain kuvan reunoilla, ja sen arvio korreloi $k_1$:n kanssa. Siksi
kalibroinnissa lauta pitää kuvata myös kuvan kulmissa, ja malliin
otetaan vain ne termit, joita objektiivi tarvitsee. Esimerkki kiinnittää
$k_3$:n ja tangentiaaliset termit nollaan lipuilla `CALIB_FIX_K3` ja
`CALIB_ZERO_TANGENT_DIST`.

## Asennon ratkaiseminen

Kun kamera on kalibroitu, yhden kuvan tunnetusta kappaleesta saa
kappaleen asennon kameraan nähden. Tämä on **PnP-ongelma**
(*perspective-n-point*), ja `solvePnP` ratkaisee sen. Lisätyssä
todellisuudessa, robotiikassa ja mittauksissa PnP on konenäön ja
maailman välinen silta.

```{.python tiedosto="esimerkit/07-kalibrointi/main.py" osa="pnp"}
```

```{.tuloste tiedosto="esimerkit/07-kalibrointi.odotettu"}
```

## Käytännössä

- **Kalibroi jokainen kamera, ja kalibroi uudelleen, kun jokin
  muuttuu.** Tarkennus, zoomaus ja objektiivin vaihto muuttavat sisäisiä
  parametreja. Tallenna parametrit kuvien yhteyteen.
- **Kuvaa lauta monesta asennosta ja koko kuvan alueelta.** Kallistetut
  asennot erottavat polttovälin etäisyydestä, ja kulmissa olevat
  kuvat määräävät vääristymän.
- **Tarkista uudelleenprojektiovirhe.** Hyvä kalibrointi antaa
  tyypillisesti alle 0,5 pikselin keskivirheen. Suuri virhe johtuu
  yleensä epätarkasta laudasta, liike-epäterävyydestä tai väärästä
  kuviokoosta.
- **Älä mallinna enempää kuin objektiivi tarvitsee.** Ylimääräiset
  vääristymätermit sovittuvat kohinaan ja voivat pilata reunojen
  korjauksen.
- **Testaa synteettisellä kameralla.** Tunnettu kamera paljastaa, ovatko
  virheet algoritmissa, datassa vai odotuksissa, ennen kuin oikeita kuvia
  edes otetaan.

## Itsearviointi

- Osaat laskea pisteen projektion käsin sisäisistä ja ulkoisista
  parametreista ja selittää, miksi mittakaava katoaa.
- Osaat selittää säteittäisen vääristymän mallin ja arvioida sen
  vaikutuksen kuvan eri osissa.
- Osaat kalibroida kameran shakkilautakuvista ja arvioida tuloksen
  uudelleenprojektiovirheellä ja tunnettuja parametreja vasten.
- Osaat ratkaista tunnetun kappaleen asennon `solvePnP`-funktiolla
  kalibroidulla kameralla.
