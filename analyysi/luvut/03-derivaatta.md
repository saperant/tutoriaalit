# Derivaatta

Derivaatta on funktion hetkellinen muutosnopeus: kuinka paljon funktion
arvo muuttuu, kun muuttuja muuttuu hyvin vähän. Geometrisesti se on
kuvaajan tangentin kulmakerroin. Luvussa derivaatta määritellään
erotusosamäärän raja-arvona, sitä kokeillaan numeerisesti ja nähdään,
miksi liian pieni askel pilaa tuloksen. Sen jälkeen käydään läpi
derivoimissäännöt ja implisiittinen derivointi.

## Määritelmä erotusosamääränä

Funktion $f$ **derivaatta** kohdassa $a$ on

$$f'(a) = \lim_{h \to 0} \frac{f(a + h) - f(a)}{h},$$

jos raja-arvo on olemassa. Osamäärä on kuvaajan pisteiden $(a, f(a))$ ja
$(a + h, f(a + h))$ kautta kulkevan **sekantin** kulmakerroin. Kun $h$
pienenee, sekantti kääntyy kohti **tangenttia**, joka sivuaa kuvaajaa
pisteessä $a$.

![Funktion $\sin x$ sekantit pisteestä $x = 1$ askelilla 1,2 ja 0,6
sekä tangentti. Mitä pienempi askel, sitä lähempänä sekantti on
tangenttia.](kuvat/tangentti.png){width=62%}

Derivaatta ei ole aina olemassa. Funktiolla $|x|$ erotusosamäärä on
nollassa $+1$ oikealta ja $-1$ vasemmalta, joten raja-arvoa ei ole:
kuvaajassa on kärki. Derivoituva funktio on aina jatkuva, mutta jatkuva
funktio ei ole aina derivoituva.

## Numeerinen derivaatta ja askeleen valinta

Kun funktion kaavaa ei tunneta tai sitä ei kannata derivoida symbolisesti,
derivaatta arvioidaan erotusosamäärällä kiinteällä askeleella $h$.
**Eteenpäin-erotus** on määritelmän osamäärä sellaisenaan.
**Keskeinen erotus**

$$f'(a) \approx \frac{f(a + h) - f(a - h)}{2h}$$

käyttää pisteitä kohdan molemmin puolin. Esimerkki vertaa niiden virheitä
funktiolle $\sin x$ kohdassa $x = 1$, jossa tarkka derivaatta on
$\cos 1$.

```{.python tiedosto="esimerkit/03-erotusosamaara.py" osa="erotus"}
```

Virhe ensin pienenee, kun $h$ pienenee, mutta kääntyy sitten kasvuun.
Syitä on kaksi:

- **Katkaisuvirhe** syntyy siitä, että sekantti ei ole tangentti.
  Taylorin kehitelmästä (luku 7) saadaan eteenpäin-erotuksen
  virheeksi noin $\tfrac{h}{2}|f''(a)|$ ja keskeisen erotuksen virheeksi
  noin $\tfrac{h^2}{6}|f'''(a)|$. Keskeinen erotus on siis kertalukua
  tarkempi.
- **Pyöristysvirhe** syntyy osoittajan vähennyslaskusta. Kun $h$ on
  pieni, $f(a + h)$ ja $f(a)$ ovat lähes samat, ja niiden erotuksessa
  merkitsevät numerot kumoutuvat (luku 2). Virhe on noin
  $\varepsilon|f(a)|/h$, missä $\varepsilon \approx 2{,}2 \cdot 10^{-16}$
  on liukulukujen suhteellinen tarkkuus, ja se kasvaa, kun $h$ pienenee.

Kokonaisvirhe on pienimmillään, kun virheet ovat yhtä suuret. Eteenpäin-
erotukselle paras askel on noin $\sqrt{\varepsilon}$ ja keskeiselle
erotukselle noin $\sqrt[3]{\varepsilon}$, kun funktio ja sen derivaatat
ovat suuruusluokaltaan yhden luokkaa.

```{.python tiedosto="esimerkit/03-erotusosamaara.py" osa="paras"}
```

```{.tuloste tiedosto="esimerkit/03-erotusosamaara.odotettu"}
```

![Erotusosamäärän virhe askeleen $h$ funktiona logaritmisella
asteikolla. Oikealla katkaisuvirhe pienenee askeleen mukana, vasemmalla
pyöristysvirhe kasvaa.](kuvat/erotusvirhe.png){width=62%}

Kuvan V-muoto on numeerisen laskennan tunnusmerkki: tarkkuutta ei voi
parantaa loputtomiin pienentämällä askelta. Numeeristen menetelmien
virhekertaluvut käsitellään perusteellisesti taidossa *Numeeriset
menetelmät*. Mittausdatassa on lisäksi kohinaa, jota erotusosamäärä
vahvistaa: kohina jaetaan pienellä luvulla $h$. Siksi mitattu signaali
yleensä suodatetaan ennen derivointia (taito *Digitaalinen
signaalinkäsittely*).

## Derivoimissäännöt

Käytännössä derivaatat lasketaan säännöillä, jotka johdetaan
määritelmästä kerran ja sitten vain sovelletaan:

| Funktio | Derivaatta | Funktio | Derivaatta |
|---------|------------|---------|------------|
| $x^n$ | $n x^{n-1}$ | $\sin x$ | $\cos x$ |
| $e^{x}$ | $e^{x}$ | $\cos x$ | $-\sin x$ |
| $a^x$ | $a^x \ln a$ | $\tan x$ | $1/\cos^2 x$ |
| $\ln x$ | $1/x$ | $\arctan x$ | $1/(1 + x^2)$ |

```{.python tiedosto="esimerkit/03-saannot.py" osa="perus"}
```

Yhdistetyille lausekkeille on kolme sääntöä. **Tulon sääntö**
$(uv)' = u'v + uv'$, **osamäärän sääntö**
$(u/v)' = (u'v - uv')/v^2$ ja **ketjusääntö**
$\bigl(u(v(x))\bigr)' = u'(v(x))\,v'(x)$. Kun SymPylle antaa
tuntemattomat funktiot `sp.Function`, se näyttää säännöt yleisessä
muodossa.

```{.python tiedosto="esimerkit/03-saannot.py" osa="saannot"}
```

Ketjusääntö on säännöistä tärkein ja helpoin unohtaa. Lausekkeessa
$\sin(x^2 + 1)$ ulkofunktio on sini ja sisäfunktio $x^2 + 1$, joten
derivaatta on $\cos(x^2 + 1) \cdot 2x$. Käsinlaskun tarkistus on sama
kuin taidossa *Matematiikan perusteet ohjelmallisesti*: erotuksen on
sievennyttävä nollaksi. Korkeammat derivaatat saadaan antamalla `diff`:lle
kertaluku.

```{.python tiedosto="esimerkit/03-saannot.py" osa="ketju"}
```

```{.tuloste tiedosto="esimerkit/03-saannot.odotettu"}
```

SymPy kirjoittaa $\tan x$:n derivaatan muodossa `cos(x)**(-2)`, joka on
sama kuin $1/\cos^2 x$ ja $1 + \tan^2 x$. Symbolinen tulos voi olla
oikein mutta eri muodossa kuin oppikirjan. Siksi vertailu tehdään
erotuksella eikä merkkijonona.

Ketjusääntö on myös koneoppimisen **vastavirta-algoritmin**
(*backpropagation*) ydin: neuroverkon virheen derivaatta kunkin
painon suhteen lasketaan ketjusäännöllä kerros kerrokselta. Kirjastot
kuten PyTorch tekevät tämän **automaattisella derivoinnilla**, joka on
symbolisen ja numeerisen derivoinnin välimuoto: tarkka kuin symbolinen
mutta laskee lukuja eikä lausekkeita.

## Implisiittinen derivointi

Kaikkia käyriä ei voi kirjoittaa muodossa $y = f(x)$. Ympyrä
$x^2 + y^2 = 25$ on kahden funktion yhdiste, ja Descartesin lehti
$x^3 + y^3 = 6xy$ ei ratkea $y$:n suhteen siististi lainkaan.
**Implisiittisessä derivoinnissa** yhtälö derivoidaan puolittain
olettaen, että $y$ on $x$:n funktio, ja $y$:n derivaatta saa
ketjusäännöstä tekijän $y'$:

$$\frac{d}{dx}(x^2 + y^2) = 2x + 2y\,y' = 0 \implies y' = -\frac{x}{y}.$$

SymPyn `idiff(F, y, x)` tekee saman yhtälölle $F(x, y) = 0$.

```{.python tiedosto="esimerkit/03-implisiittinen.py" osa="ympyra"}
```

Tulos voidaan tarkistaa ylemmän puoliympyrän eksplisiittisellä kaavalla
$y = \sqrt{25 - x^2}$:

```{.python tiedosto="esimerkit/03-implisiittinen.py" osa="tarkistus"}
```

Descartesin lehdellä eksplisiittistä kaavaa ei ole tarjolla, mutta
tangentin kulmakerroin saadaan silti mistä tahansa käyrän pisteestä.

```{.python tiedosto="esimerkit/03-implisiittinen.py" osa="kayra"}
```

```{.tuloste tiedosto="esimerkit/03-implisiittinen.odotettu"}
```

Implisiittinen derivointi on arkea tekniikassa: tilanyhtälöt, kuten
ideaalikaasun $pV = nRT$, sitovat suureita toisiinsa, ja derivaatta
kertoo, miten yksi suure muuttuu toisen mukana, kun loput pidetään
vakioina.

## Samat laskut Maximalla

Maximan `diff` toimii kuten SymPyn. Implisiittisessä derivoinnissa
`depends(y, x)` kertoo, että $y$ riippuu $x$:stä, jolloin yhtälön
derivaatta sisältää termin `'diff(y, x, 1)`, ja sen voi ratkaista
`solve`-funktiolla.

```{.maxima tiedosto="esimerkit/maxima/03-derivaatta.mac" osa="derivaatta"}
```

```{.tuloste tiedosto="esimerkit/maxima/03-derivaatta.odotettu"}
```

## Käytännössä

- **Derivoi symbolisesti, kun kaava on tiedossa.** Symbolinen
  derivaatta on tarkka ja nopea laskea; numeerinen erotusosamäärä on
  aina likiarvo.
- **Valitse askel tietoisesti.** Keskeinen erotus askeleella noin
  $10^{-5}$ (suhteessa muuttujan suuruuteen) on hyvä oletus. Liian pieni
  askel on yhtä huono kuin liian suuri.
- **Tarkista käsinlasku erotuksella.** Kirjoita oma derivaattasi ja
  sievennä erotus koneen tulokseen. Muotojen vertailu silmällä johtaa
  harhaan.
- **Muista ketjusääntö.** Useimmat käsinderivoinnin virheet ovat
  unohtunut sisäfunktion derivaatta.
- **Derivoi mittausdata varoen.** Erotusosamäärä vahvistaa kohinaa.
  Suodata ensin tai sovita mittauksiin funktio ja derivoi se.

## Itsearviointi

- Osaat määritellä derivaatan erotusosamäärän raja-arvona ja tulkita
  sen tangentin kulmakertoimena.
- Osaat laskea numeerisen derivaatan eteenpäin- ja keskeisellä
  erotuksella ja selittää, miksi virhe kasvaa liian pienellä askeleella.
- Osaat derivoida alkeisfunktioita sekä tulon, osamäärän ja
  ketjusäännön avulla ja tarkistaa tuloksen SymPyllä.
- Osaat derivoida implisiittisesti ja laskea käyrän tangentin.
