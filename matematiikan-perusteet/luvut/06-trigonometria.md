# Trigonometria

Trigonometria alkaa suorakulmaisen kolmion sivujen suhteista, mutta
tekniikassa sen tärkein käyttö on **jaksollisten ilmiöiden** kuvaaminen:
vaihtojännite, ääni, värähtely ja pyörimisliike. Luvussa käydään läpi
yksikköympyrä ja radiaanit, kaavojen tarkistaminen koneella,
trigonometriset yhtälöt ja lopuksi harmoninen värähtely, joka pohjustaa
taitoa *Kompleksiluvut ja Fourier-analyysi*.

## Yksikköympyrä ja radiaanit

Yksikköympyrä on origokeskinen ympyrä, jonka säde on 1. Kun ympyrän
kehältä mitataan positiivisesta $x$-akselista vastapäivään kulma
$\theta$, kehäpisteen koordinaatit ovat $(\cos\theta, \sin\theta)$. Tästä
seuraavat suoraan perusominaisuudet: $\sin^2\theta + \cos^2\theta = 1$
(Pythagoraan lause), arvot ovat välillä $[-1, 1]$, ja funktiot ovat
jaksollisia jaksolla $2\pi$.

![Yksikköympyrä: kulman $\pi/6$ kehäpiste on
$(\sqrt3/2,\ 1/2)$.](kuvat/yksikkoympyra.png){width=50%}

**Radiaani** mittaa kulmaa kaaren pituutena yksikköympyrällä: täysi
kierros on $2\pi$ radiaania, oikokulma $\pi$ ja suora kulma $\pi/2$.
Muunnos asteista radiaaneiksi on $\theta_{\text{rad}} = \theta_\circ \cdot
\pi/180$. Matemaattiset ohjelmakirjastot käyttävät aina radiaaneja.

Erikoiskulmien tarkat arvot kannattaa osata, koska ne toistuvat
tehtävissä. SymPy laskee ne tarkkoina lausekkeina.

```{.python tiedosto="esimerkit/06-tarkat-arvot.py" osa="tarkat"}
```

Pythonin `math`-moduuli laskee liukuluvuilla. Luku $\pi$ ei ole tarkasti
esitettävissä, joten `math.sin(math.pi)` ei ole tarkasti nolla vaan noin
$10^{-16}$. Yleisin trigonometriavirhe ohjelmissa on silti yksikkö:
`math.sin(30)` laskee 30 radiaanin sinin, ei 30 asteen.

```{.python tiedosto="esimerkit/06-tarkat-arvot.py" osa="liukuluku"}
```

```{.tuloste tiedosto="esimerkit/06-tarkat-arvot.odotettu"}
```

## Kaavat ja niiden tarkistus

Trigonometrisia kaavoja on paljon, ja niitä muistetaan usein väärin.
Kone tarkistaa kaavan kahdella tavalla.

**Symbolisesti**: kaava pätee, jos puolten erotus sievenee nollaksi.
`expand_trig` avaa summien ja monikertojen funktiot, kuten
$\sin(2x) \to 2\sin x\cos x$, minkä jälkeen `simplify` hoitaa loput.

```{.python tiedosto="esimerkit/06-kaavat.py" osa="kaavat"}
```

**Numeerisesti**: lasketaan erotus muutamassa testipisteessä. Jos jokin
erotus on selvästi nollasta poikkeava, kaava on väärin. Pieni erotus ei
kuitenkaan todista kaavaa, vaan on vain pistokoe. Siksi symbolinen
tarkistus on vahvempi, ja numeerinen on hyvä lisävarmistus, kun
symbolinen sievennys ei onnistu.

```{.python tiedosto="esimerkit/06-kaavat.py" osa="numeerinen"}
```

```{.tuloste tiedosto="esimerkit/06-kaavat.odotettu"}
```

Oikea kaksinkertaisen kulman tangenttikaava on
$\tan 2x = \frac{2\tan x}{1 - \tan^2 x}$. Väärän kaavan poikkeama on
suuri, koska testipisteiden joukossa on kohta, jossa $\tan 2x$ on lähellä
asymptoottiaan.

## Trigonometriset yhtälöt

Koska trigonometriset funktiot ovat jaksollisia, yhtälöllä
$\sin x = \tfrac12$ on äärettömän monta ratkaisua:
$x = \frac{\pi}{6} + 2\pi n$ ja $x = \frac{5\pi}{6} + 2\pi n$, kun
$n$ on kokonaisluku. Jälkimmäinen tulee symmetriasta
$\sin(\pi - x) = \sin x$. SymPyn `solveset` ilmaisee tämän
`ImageSet`-joukkoina: kuva joukosta `Integers` funktiolla
$n \mapsto 2\pi n + \pi/6$.

```{.python tiedosto="esimerkit/06-yhtalot.py" osa="yleinen"}
```

Käytännössä ratkaisut halutaan yleensä tietyltä väliltä. Kun
perusjoukoksi annetaan väli, `solveset` palauttaa äärellisen joukon.

```{.python tiedosto="esimerkit/06-yhtalot.py" osa="valilla"}
```

```{.python tiedosto="esimerkit/06-yhtalot.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/06-yhtalot.odotettu"}
```

Yhtälö $\cos 2x = \cos x$ ratkaistaan käsin kirjoittamalla
$\cos 2x = 2\cos^2 x - 1$, jolloin saadaan toisen asteen yhtälö
$\cos x$:n suhteen: $\cos x = 1$ tai $\cos x = -\tfrac12$. Välillä
$[0, 2\pi[$ ratkaisut ovat $0$, $2\pi/3$ ja $4\pi/3$, kuten SymPykin
kertoo.

## Harmoninen värähtely ja vaihe

Jaksollinen ilmiö kirjoitetaan muodossa

$$y(t) = A \sin(\omega t + \varphi),$$

jossa $A$ on **amplitudi**, $\omega = 2\pi f$ **kulmataajuus** ja
$\varphi$ **vaihe**. Verkkojännitteen taajuus on Euroopassa 50 Hz, joten
jaksonaika on $T = 1/f = 20$ ms.

Kaksi saman taajuuden värähtelyä summautuvat yhdeksi samantaajuiseksi
värähtelyksi. Summakaavasta
$R\sin(\omega t + \varphi) = R\cos\varphi\sin\omega t + R\sin\varphi\cos\omega t$
nähdään, että $A\sin\omega t + B\cos\omega t$ on sama, kun
$R = \sqrt{A^2 + B^2}$ ja $\varphi = \operatorname{atan2}(B, A)$.

Funktio `atan2` palauttaa kulman oikeasta neljänneksestä, toisin kuin
$\arctan(B/A)$, joka ei erota pisteitä $(A, B)$ ja $(-A, -B)$. Sitä
käytetään aina, kun kulma lasketaan koordinaateista.

```{.python tiedosto="esimerkit/06-varahtely.py" osa="summa"}
```

```{.python tiedosto="esimerkit/06-varahtely.py" osa="tarkistus"}
```

Vaihe muutetaan aikaeroksi jakamalla kulmataajuudella: $53{,}13$ asteen
vaihe-ero 50 hertsin taajuudella on noin 3 millisekuntia.

```{.python tiedosto="esimerkit/06-varahtely.py" osa="jakso"}
```

```{.tuloste tiedosto="esimerkit/06-varahtely.odotettu"}
```

Sama asia on kompleksiluvuilla kertolasku: värähtely
$R\sin(\omega t + \varphi)$ vastaa **osoitinta** $R e^{i\varphi}$, ja
saman taajuuden värähtelyjen summa on osoittimien summa. Tämä on
vaihtovirtapiirien laskennan perusta (taidot *Kompleksiluvut ja
Fourier-analyysi* ja *Elektroniikan perusteet ja SPICE*).

## Samat laskut Maximalla

Maximan `trigexpand` vastaa SymPyn `expand_trig`-funktiota ja
`trigreduce` muuntaa potenssit monikertakulmiksi. Maximan `solve`
varoittaa itse, että se antaa vain yhden ratkaisun. Toinen ratkaisu ja
jakso lisätään käsin.

```{.maxima tiedosto="esimerkit/maxima/06-trigonometria.mac" osa="arvot"}
```

```{.maxima tiedosto="esimerkit/maxima/06-trigonometria.mac" osa="kaavat"}
```

```{.maxima tiedosto="esimerkit/maxima/06-trigonometria.mac" osa="yhtalot"}
```

```{.tuloste tiedosto="esimerkit/maxima/06-trigonometria.odotettu"}
```

## Käytännössä

- **Radiaanit ohjelmissa, asteet ihmisille.** Muunna käyttöliittymän
  asteet radiaaneiksi heti (`math.radians`) ja takaisin vasta
  tulostettaessa.
- **`atan2`, ei `atan`.** Kulma koordinaateista lasketaan aina
  funktiolla `atan2(y, x)`, joka huomioi neljänneksen ja toimii myös, kun
  $x = 0$.
- **Tarkista kaava ennen käyttöä.** Symbolinen erotus tai muutaman
  testipisteen pistokoe vie sekunteja ja estää virheellisen kaavan
  päätymisen koodiin.
- **Yhtälöllä on yleensä äärettömästi ratkaisuja.** Rajaa väli
  ongelman mukaan ja muista symmetriaratkaisu $\pi - x$ sinille ja
  $-x$ kosinille.
- **Saman taajuuden värähtelyt summautuvat yhdeksi.** Amplitudi ja vaihe
  saadaan Pythagoraan lauseella ja `atan2`-funktiolla.

## Itsearviointi

- Osaat yksikköympyrän määritelmän, erikoiskulmien tarkat arvot ja
  muunnoksen asteiden ja radiaanien välillä.
- Osaat tarkistaa trigonometrisen kaavan symbolisesti ja numeerisesti
  sekä tiedät, miksi numeerinen pistokoe ei ole todistus.
- Osaat ratkaista trigonometrisen yhtälön yleisesti ja annetulta
  väliltä.
- Osaat kirjoittaa kahden saman taajuuden värähtelyn summan muodossa
  $R\sin(\omega t + \varphi)$ ja muuntaa vaiheen aikaeroksi.
