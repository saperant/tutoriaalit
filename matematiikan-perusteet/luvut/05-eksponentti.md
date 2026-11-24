# Eksponentti- ja logaritmifunktiot

Eksponenttifunktio kuvaa ilmiöitä, joissa muutos on verrannollinen
nykyiseen määrään: käyttäjämäärän kasvu, korko, kondensaattorin
purkautuminen ja radioaktiivinen hajoaminen. Logaritmi on sen
käänteisfunktio, ja sillä ratkaistaan, *milloin* jokin määrä saavutetaan.
Logaritmi on myös insinöörin mittakaava: desibelit, pH ja algoritmin
$\log_2 n$ -vaativuus ovat kaikki logaritmeja.

## Eksponentiaalinen kasvu

Kun suure kasvaa joka aikayksikkö samalla prosenttimäärällä $p$, sen
arvo ajan $t$ kuluttua on

$$N(t) = N_0 (1 + p)^t.$$

**Kaksinkertaistumisaika** ratkaistaan yhtälöstä $N(t) = 2N_0$ eli
$(1+p)^t = 2$. Ottamalla logaritmi molemmin puolin saadaan
$t = \ln 2 / \ln(1 + p)$. Pienillä $p$:n arvoilla $\ln(1+p) \approx p$,
mistä tulee nyrkkisääntö: kaksinkertaistumisaika on noin 70 jaettuna
kasvuprosentilla.

```{.python tiedosto="esimerkit/05-kasvu.py" osa="kasvu"}
```

SymPyn tulos on oikein mutta kömpelösti kirjoitettu. Se kannattaa
tarkistaa vertaamalla siistimpään muotoon: erotuksen sievenemistä
nollaksi käytettiin jo luvussa 1.

### Luonnollinen eksponenttifunktio

Mikä tahansa eksponenttifunktio voidaan kirjoittaa Neperin luvun
$e \approx 2{,}718$ potenssina: $a^t = e^{t \ln a}$. Muotoa $e^{kt}$
käytetään luonnontieteissä ja tekniikassa, koska sen derivaatta on
yksinkertaisin ($k e^{kt}$), ja kerroin $k$ on **jatkuva kasvunopeus**.

```{.python tiedosto="esimerkit/05-kasvu.py" osa="jatkuva"}
```

```{.tuloste tiedosto="esimerkit/05-kasvu.odotettu"}
```

Viidessä vuodessa 6 prosentin kuukausikasvu kasvattaa tuhannen käyttäjän
palvelun yli 30-kertaiseksi. Eksponentiaalinen kasvu yllättää
intuitiivisesti, minkä vuoksi kapasiteettisuunnittelu tehdään laskemalla
eikä arvioimalla.

## Logaritmi ja sen laskusäännöt

**Logaritmi** $\log_a x$ on se eksponentti, johon kanta $a$ on
korotettava, jotta saadaan $x$: $a^{\log_a x} = x$. Luonnollinen logaritmi
$\ln x$ on $e$-kantainen, ja kymmenkantainen kirjoitetaan $\lg x$.
SymPyssä ja Maximassa `log` on luonnollinen logaritmi, ja kanta annetaan
erikseen: `sp.log(x, 2)`.

| Sääntö | Kaava | Ehto |
|--------|-------|------|
| Tulo | $\log(xy) = \log x + \log y$ | $x, y > 0$ |
| Osamäärä | $\log(x/y) = \log x - \log y$ | $x, y > 0$ |
| Potenssi | $\log x^r = r \log x$ | $x > 0$ |
| Kannanvaihto | $\log_a x = \ln x / \ln a$ | $a > 0$, $a \ne 1$ |

Ehdot eivät ole muodollisuus. SymPy soveltaa sääntöjä vain, kun se tietää
symbolien olevan positiivisia. Negatiivisilla luvuilla tulosääntö ei päde
edes kompleksilukujen logaritmille: tuloksiin tulee ero $2\pi i$.

```{.python tiedosto="esimerkit/05-logaritmit.py" osa="saannot"}
```

```{.python tiedosto="esimerkit/05-logaritmit.py" osa="vastaesimerkki"}
```

Kannanvaihtokaavalla mikä tahansa logaritmi lasketaan luonnollisella
logaritmilla. Ohjelmoijalle tärkein on $\log_2 n$: se kertoo, montako
kertaa $n$ voidaan puolittaa, eli binäärihaun ja tasapainotetun puun
syvyyden.

```{.python tiedosto="esimerkit/05-logaritmit.py" osa="kannanvaihto"}
```

```{.tuloste tiedosto="esimerkit/05-logaritmit.odotettu"}
```

## Logaritminen asteikko

Kun suure vaihtelee monta kertaluokkaa, kuvaajan pystyakseli kannattaa
piirtää **logaritmisena**: tasavälein ovat luvut 1, 10, 100, 1000 eivätkä
1, 2, 3. Eksponenttifunktio näkyy logaritmisella asteikolla suorana,
koska $\log N(t) = \log N_0 + t \log(1 + p)$ on $t$:n suhteen lineaarinen.
Suoruus on myös testi: jos mittausdata on logaritmisella asteikolla suora,
ilmiö on eksponentiaalinen.

![Käyttäjämäärä 6 prosentin kuukausikasvulla viiden vuoden ajan
tavallisella ja logaritmisella asteikolla.](kuvat/logasteikko.png){width=100%}

## Sovellus: aikavakio mittauksista

Kun vastuksen kautta purkautuvan kondensaattorin jännite mitataan,
tulokseksi saadaan $u(t) = U_0 e^{-t/\tau}$, jossa **aikavakio**
$\tau = RC$. Logaritmi suoristaa eksponentin:

$$\ln u = \ln U_0 - \frac{t}{\tau}.$$

Pisteisiin $(t, \ln u)$ sovitetaan suora `numpy.polyfit`-funktiolla, ja
sen kulmakertoimesta saadaan $\tau$. Mittausdataan on lisätty prosentin
kohinaa kiinteällä satunnaissiemenellä, jotta tulos on toistettava.

```{.python tiedosto="esimerkit/05-puoliintuminen.py" osa="mittaukset"}
```

```{.python tiedosto="esimerkit/05-puoliintuminen.py" osa="sovitus"}
```

```{.tuloste tiedosto="esimerkit/05-puoliintuminen.odotettu"}
```

**Puoliintumisaika** on aika, jossa jännite putoaa puoleen:
$e^{-t/\tau} = \tfrac12$ eli $t = \tau \ln 2$. Viiden aikavakion jälkeen
jäljellä on alle prosentti, minkä vuoksi elektroniikassa sanotaan, että
piiri on asettunut $5\tau$:n jälkeen. Taito *Elektroniikan perusteet ja
SPICE* simuloi saman piirin.

## Desibelit

**Desibeli** on kahden tehon suhteen logaritminen mitta:
$10 \lg (P_2/P_1)$ dB. Jännite- ja virta-amplitudeille kerroin on 20,
koska teho on verrannollinen amplitudin neliöön:
$10 \lg (A^2) = 20 \lg A$. Muistisäännöt: tehon tuplaus on $+3$ dB,
amplitudin tuplaus $+6$ dB, ja kymmenkertainen amplitudi $+20$ dB.

```{.python tiedosto="esimerkit/05-desibelit.py" osa="desibelit"}
```

Logaritmin tulosääntö tekee desibeleistä käytännöllisiä: ketjun
vahvistukset kerrotaan, joten niiden desibeliarvot lasketaan yhteen.

```{.python tiedosto="esimerkit/05-desibelit.py" osa="ketju"}
```

```{.tuloste tiedosto="esimerkit/05-desibelit.odotettu"}
```

## Samat laskut Maximalla

Maximan `solve` ei ratkaise eksponenttiyhtälöä suoraan, vaan palauttaa
yhtälön toisessa muodossa. Kun logaritmi otetaan ensin, yhtälö on
lineaarinen ja ratkeaa. Tämä on hyvä muistutus siitä, että symbolinen
ohjelma ei aina ratkaise tehtävää valmiiksi: joskus käyttäjän pitää tehdä
ratkaiseva muunnos.

```{.maxima tiedosto="esimerkit/maxima/05-logaritmit.mac" osa="yhtalot"}
```

```{.maxima tiedosto="esimerkit/maxima/05-logaritmit.mac" osa="saannot"}
```

```{.tuloste tiedosto="esimerkit/maxima/05-logaritmit.odotettu"}
```

## Käytännössä

- **Logaritmi ratkaisee "milloin".** Eksponenttiyhtälö
  $a^t = b$ ratkeaa ottamalla logaritmi: $t = \ln b / \ln a$.
- **Tarkista logaritmisäännön ehdot.** Säännöt pätevät vain
  positiivisille luvuille. SymPyssä symbolit luodaan oletuksella
  `positive=True`, kun säännöt halutaan käyttöön.
- **Piirrä monta kertaluokkaa logaritmisella asteikolla.** Suora viiva
  paljastaa eksponentiaalisen ilmiön, ja sovitus tehdään suoralle.
- **Desibeleissä kerroin 10 teholle, 20 amplitudille.** Väärä kerroin on
  yleisin desibelivirhe.
- **Kiinteä satunnaissiemen.** Kun esimerkki tai testi käyttää
  satunnaislukuja, kiinteä siemen (`default_rng(7)`) tekee tuloksesta
  toistettavan.

## Itsearviointi

- Osaat mallintaa prosentuaalisen kasvun eksponenttifunktiolla ja laskea
  kaksinkertaistumis- ja puoliintumisajan.
- Osaat logaritmin laskusäännöt, niiden ehdot ja kannanvaihtokaavan.
- Osaat tunnistaa eksponentiaalisen ilmiön logaritmiselta asteikolta ja
  sovittaa siihen mallin suoran avulla.
- Osaat muuntaa teho- ja amplitudisuhteet desibeleiksi ja laskea ketjun
  kokonaisvahvistuksen.
