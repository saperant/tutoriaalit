# Integraali

Integraali kokoaa pienistä osista kokonaisuuden. Jos nopeus on vakio,
matka on nopeus kertaa aika. Jos nopeus vaihtelee, aika jaetaan lyhyisiin
pätkiin, joilla nopeus on lähes vakio, ja pätkien matkat lasketaan
yhteen. Kun pätkät lyhenevät rajatta, summa lähestyy **määrättyä
integraalia**. Luvussa integraali määritellään Riemannin summien
raja-arvona, yhdistetään derivaattaan analyysin peruslauseella ja käydään
läpi tavallisimmat integrointitekniikat.

## Riemannin summat

Jaetaan väli $[a, b]$ $n$ yhtä pitkään osaväliin, joiden pituus on
$\Delta x = (b - a)/n$. Kultakin osaväliltä valitaan piste $x_i$, ja
lasketaan **Riemannin summa**

$$\sum_{i=0}^{n-1} f(x_i)\,\Delta x.$$

Summa on suorakulmioiden pinta-alojen summa. Jos se lähestyy samaa
raja-arvoa riippumatta pisteiden valinnasta, kun $n \to \infty$, raja-arvo
on funktion **määrätty integraali** $\int_a^b f(x)\,dx$. Jatkuvalla
funktiolla näin käy aina.

![Riemannin summat funktiolle $x^2$ kahdeksalla osavälillä. Vasemmalla
suorakulmion korkeus otetaan osavälin vasemmasta päätepisteestä,
oikealla keskipisteestä.](kuvat/riemann.png){width=100%}

Esimerkki laskee summat funktiolle $x^2$ välillä $[0, 1]$, jossa tarkka
arvo on $\tfrac13$. Pisteeksi valitaan osavälin vasen tai oikea
päätepiste tai keskipiste.

```{.python tiedosto="esimerkit/05-riemann.py" osa="summat"}
```

```{.tuloste tiedosto="esimerkit/05-riemann.odotettu"}
```

Päätepistesummien virhe pienenee kymmenesosaan, kun $n$ kymmenkertaistuu:
virhe on kertalukua $1/n$. Keskipistesumman virhe pienenee sadasosaan,
eli se on kertalukua $1/n^2$. Ero syntyy siitä, että keskipisteen
virheet osavälin molemmissa puolissa kumoavat toisiaan. Tämä on
numeerisen integroinnin perusajatus, johon palataan luvussa 6.

Integraalilla on etumerkki: $x$-akselin alapuolella oleva osa lasketaan
negatiivisena. Siksi $\int_0^{2\pi} \sin x\,dx = 0$, vaikka käyrän ja
akselin väliin jää pinta-alaa. Pinta-ala saadaan integroimalla
itseisarvo tai jakamalla väli nollakohtien kohdalta.

## Analyysin peruslause

Integraalien laskeminen summien raja-arvoina olisi työlästä. **Analyysin
peruslause** yhdistää integraalin derivaattaan kahdella tavalla:

1. Jos $F' = f$ välillä $[a, b]$, niin
   $\displaystyle\int_a^b f(x)\,dx = F(b) - F(a)$.
2. Jos $f$ on jatkuva, funktion $G(x) = \int_a^x f(t)\,dt$ derivaatta
   on $G'(x) = f(x)$.

Funktiota $F$, jonka derivaatta on $f$, sanotaan $f$:n
**integraalifunktioksi**. Se on yksikäsitteinen vakiota vaille, koska
vakion derivaatta on nolla; merkitään
$\int f(x)\,dx = F(x) + C$. SymPyn `integrate(f, x)` antaa
integraalifunktion ilman vakiota, ja `integrate(f, (x, a, b))` laskee
määrätyn integraalin.

```{.python tiedosto="esimerkit/05-peruslause.py" osa="peruslause"}
```

Peruslauseen toinen puoli sanoo, että integraali muuttuvan ylärajan
funktiona on derivoituva ja sen derivaatta on integroitava funktio. Se
pätee, vaikka integraalifunktiota ei voisi kirjoittaa alkeisfunktioilla.
Normaalijakauman kertymäfunktio on tällainen: $e^{-t^2}$:n
integraalifunktio on **virhefunktio** $\operatorname{erf}$, joka on
määritelty juuri integraalina.

```{.python tiedosto="esimerkit/05-peruslause.py" osa="ylaraja"}
```

```{.tuloste tiedosto="esimerkit/05-peruslause.odotettu"}
```

## Integrointitekniikat

Derivointi on mekaanista, integrointi ei. Integraalifunktio löydetään
tunnistamalla derivoimissääntö takaperin. Kolme tekniikkaa kattaa
suurimman osan insinöörin tarpeista.

**Osittaisintegrointi** on tulon säännön käänteinen muoto:

$$\int u\,dv = u v - \int v\,du.$$

Se sopii tuloon, jossa toinen tekijä yksinkertaistuu derivoitaessa ja
toinen ei monimutkaistu integroitaessa. Integraalissa $\int x e^x\,dx$
valitaan $u = x$ ja $dv = e^x\,dx$, jolloin jäljelle jää helppo
$\int e^x\,dx$.

```{.python tiedosto="esimerkit/05-tekniikat.py" osa="osittain"}
```

**Sijoitus** on ketjusäännön käänteinen muoto. Jos integroitavassa on
sisäfunktio $g(x)$ ja sen derivaatta tekijänä, sijoitus $u = g(x)$,
$du = g'(x)\,dx$ poistaa ketjun. Integraalissa $\int x\cos(x^2)\,dx$
sisäfunktio on $x^2$ ja sen derivaatta $2x$ on mukana vakiota vaille.

```{.python tiedosto="esimerkit/05-tekniikat.py" osa="sijoitus"}
```

**Osamurtohajotelma** jakaa rationaalifunktion yksinkertaisiin
murtolukuihin, joiden integraalit ovat logaritmeja ja arkustangentteja.
SymPyn `apart` tekee hajotelman. Samaa hajotelmaa käytetään
Laplace-muunnoksen käänteismuunnoksessa (taito *Differentiaaliyhtälöt
ja Laplace-muunnos*).

```{.python tiedosto="esimerkit/05-tekniikat.py" osa="osamurto"}
```

SymPy kirjoittaa $\int \frac{dx}{x - 3}$ muotoon $\log(x - 3)$ ilman
itseisarvoa, koska se laskee kompleksiluvuilla. Reaalisella välillä
$x < 3$ oikea muoto on $\ln|x - 3|$. Symbolisen ohjelman tulos on aina
luettava ajatuksella.

Kaikilla alkeisfunktioilla ei ole alkeisfunktiona kirjoitettavaa
integraalifunktiota. Tämä on matemaattinen tosiasia eikä ohjelman
puute. SymPy palauttaa silloin erikoisfunktion: integraalisinin
$\operatorname{Si}$, eksponentti-integraalin $\operatorname{Ei}$ tai
virhefunktion. Niiden arvot lasketaan numeerisesti.

```{.python tiedosto="esimerkit/05-tekniikat.py" osa="eialkeis"}
```

```{.tuloste tiedosto="esimerkit/05-tekniikat.odotettu"}
```

## Epäoleelliset integraalit

Integraali on **epäoleellinen**, jos väli on ääretön tai funktio on
rajoittamaton välillä. Se määritellään raja-arvona:

$$\int_1^\infty f(x)\,dx = \lim_{R \to \infty} \int_1^R f(x)\,dx.$$

Jos raja-arvo on olemassa, integraali **suppenee**, muuten se
**hajaantuu**. Funktioiden $1/x^2$ ja $1/x$ ero on opettavainen: kumpikin
lähestyy nollaa, mutta vain ensimmäinen niin nopeasti, että pinta-ala
jää äärelliseksi. Yleisesti $\int_1^\infty x^{-p}\,dx$ suppenee, kun
$p > 1$, ja $\int_0^1 x^{-p}\,dx$ suppenee, kun $p < 1$.

```{.python tiedosto="esimerkit/05-epaoleellinen.py" osa="symbolinen"}
```

```{.python tiedosto="esimerkit/05-epaoleellinen.py" osa="raja"}
```

Numeerisesti epäoleellinen integraali lasketaan SciPyn `quad`-funktiolla,
joka hyväksyy äärettömän rajan ja muuntaa välin sisäisesti äärelliseksi.
Se palauttaa arvon lisäksi arvion virheestä, mikä on hyvä tapa: kirjasto
kertoo itse, kuinka paljon tulokseen voi luottaa.

```{.python tiedosto="esimerkit/05-epaoleellinen.py" osa="quad"}
```

```{.tuloste tiedosto="esimerkit/05-epaoleellinen.odotettu"}
```

Epäoleelliset integraalit ovat tärkeitä todennäköisyyslaskennassa
(tiheysfunktion integraali koko reaaliakselin yli on 1, taito
*Todennäköisyys ja tilastot*) ja muunnoksissa, kuten Fourier- ja
Laplace-muunnoksessa, jotka ovat integraaleja äärettömän välin yli.

## Samat laskut Maximalla

Maximan `integrate` antaa integraalifunktion kahdella argumentilla ja
määrätyn integraalin neljällä. `partfrac` tekee osamurtohajotelman.

```{.maxima tiedosto="esimerkit/maxima/05-integraali.mac" osa="integraali"}
```

```{.tuloste tiedosto="esimerkit/maxima/05-integraali.odotettu"}
```

Maxima kysyy joskus ehtoja, kuten onko parametri positiivinen. Eräajossa
kysymys pysäyttää skriptin, joten oletukset annetaan etukäteen
`assume`-funktiolla (luku 9).

## Käytännössä

- **Tarkista integraalifunktio derivoimalla.** Jos $F' - f$ sievenee
  nollaksi, tulos on oikein. Tarkistus on aina helpompi kuin itse
  integrointi.
- **Muista integroimisvakio ja itseisarvo.** Integraalifunktio on
  määrätty vakiota vaille, ja $\int dx/x = \ln|x| + C$.
- **Kaikkea ei voi integroida suljetusti.** Kun tuloksena on
  erikoisfunktio tai symbolinen ohjelma ei vastaa, laske numeerisesti
  (luku 6).
- **Tarkista epäoleellisen integraalin suppeneminen ensin.**
  Numeerinen ohjelma palauttaa luvun myös hajaantuvalle integraalille;
  virhearvio ja varoitukset kertovat, onko siihen syytä luottaa.
- **Keskipiste voittaa päätepisteen.** Jos integraali on arvioitava
  summalla, keskipisteet antavat kertalukua tarkemman tuloksen samalla
  työllä.

## Itsearviointi

- Osaat selittää määrätyn integraalin Riemannin summien raja-arvona ja
  laskea summat ohjelmallisesti.
- Osaat soveltaa analyysin peruslausetta molempiin suuntiin.
- Osaat integroida osittaisintegroinnilla, sijoituksella ja
  osamurtohajotelmalla sekä tarkistaa tuloksen derivoimalla.
- Osaat laskea epäoleellisen integraalin raja-arvona ja numeerisesti
  `quad`-funktiolla sekä päätellä, suppeneeko integraali.
