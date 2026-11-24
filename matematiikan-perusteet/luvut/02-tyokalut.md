# Työkalut: SymPy, Maxima, NumPy ja Matplotlib

Tämä luku on käsikirja. Se esittelee jokaisen työkalun ne komennot, joita
tutoriaalissa ja sen jatkotaidoissa käytetään eniten. Lukua voi lukea
myöhemmin hakuteoksena: kun jokin komento tulee vastaan uudelleen, sen
selitys on täällä.

## Symbolinen ja numeerinen laskenta

Laskentaohjelmat jakautuvat kahteen leiriin.

| Ominaisuus | Symbolinen (SymPy, Maxima) | Numeerinen (NumPy, Octave) |
|------------|----------------------------|-----------------------------|
| Luvut | Tarkkoja: $\tfrac13$, $\sqrt2$, $\pi$ | Liukulukuja, noin 16 numeroa |
| Muuttujat | Symboleja, joilla ei ole arvoa | Aina lukuarvoja |
| Tulos | Lauseke tai tarkka luku | Lukutaulukko |
| Nopeus | Hidas, kasvaa lausekkeen koon mukana | Nopea, miljoonia arvoja sekunnissa |
| Tyypillinen käyttö | Kaavan johtaminen ja tarkistus | Simulointi, mittausdata, kuvaajat |

Käytännön työssä molempia tarvitaan. Kaava johdetaan ja tarkistetaan
symbolisesti, ja sitten se muunnetaan numeeriseksi funktioksi, jolla
lasketaan suuri määrä arvoja tai piirretään kuvaaja. Tämä työnkulku
toistuu koko tutoriaalin ajan.

## SymPy

SymPy on tavallinen Python-kirjasto. Se tuodaan nimellä `sp`, ja symbolit
luodaan funktiolla `sp.symbols`. Symbolille voi antaa oletuksia, kuten
`positive=True` tai `real=True`. Oletukset vaikuttavat sievennykseen:
$\sqrt{a^2} = a$ vain, jos $a \ge 0$. Ilman oletusta SymPy ei sievennä,
koska tulos olisi väärä negatiivisilla luvuilla.

```{.python tiedosto="esimerkit/02-sympy.py" osa="symbolit"}
```

SymPy ei sievennä lauseketta automaattisesti, vaan muokkausfunktio
valitaan tavoitteen mukaan:

| Funktio | Tekee | Esimerkki |
|----------|------------------------|--------------------------|
| `expand` | Kertoo sulut auki | $(x+1)^2 \to x^2 + 2x + 1$ |
| `factor` | Jakaa tekijöihin | $x^2 - 1 \to (x-1)(x+1)$ |
| `cancel` | Supistaa rationaalilausekkeen | $\frac{x^2-1}{x+1} \to x - 1$ |
| `collect` | Ryhmittelee muuttujan potenssien mukaan | $x^2 + xy + 2x \to x^2 + x(y+2)$ |
| `simplify` | Kokeilee useita keinoja ja valitsee lyhimmän | $\sin^2x + \cos^2x \to 1$ |

`simplify` on kätevä mutta hidas ja arvaamaton: sen tulos voi muuttua
SymPyn versiosta toiseen. Kun tiedät, mitä haluat, käytä tarkempaa
funktiota.

```{.python tiedosto="esimerkit/02-sympy.py" osa="muokkaus"}
```

Lausekkeen arvo lasketaan sijoittamalla: `subs` korvaa symbolin luvulla
tai toisella lausekkeella. Tulos pysyy tarkkana, kunnes pyydetään
likiarvo metodilla `evalf` tai funktiolla `sp.N`. Molemmille voi antaa
merkitsevien numeroiden määrän.

```{.python tiedosto="esimerkit/02-sympy.py" osa="sijoitus"}
```

Yhtälöitä ratkaistaan kahdella funktiolla. `solve` palauttaa listan
ratkaisuista tai yhtälöryhmälle sanakirjoja. `solveset` palauttaa
*joukon* ja ottaa vastaan perusjoukon (`domain`), joten se kertoo myös,
ettei ratkaisua ole: yhtälöllä $x^2 + 1 = 0$ ei ole reaalisia ratkaisuja,
mutta kompleksilukuja on kaksi. `solveset` on parempi, kun ratkaisuja on
äärettömästi tai ei lainkaan (luku 6).

```{.python tiedosto="esimerkit/02-sympy.py" osa="ratkaisu"}
```

Lopuksi lauseke muunnetaan numeeriseksi funktioksi funktiolla `lambdify`.
Moduuli `math` tuottaa funktion yksittäisille luvuille ja `numpy`
taulukoille. `nsolve` ratkaisee yhtälön numeerisesti alkuarvauksesta
lähtien, kun tarkkaa ratkaisua ei ole: yhtälöllä $\cos x = x$ ei ole
alkeisfunktioilla lausuttavaa ratkaisua.

```{.python tiedosto="esimerkit/02-sympy.py" osa="numeeriseksi"}
```

```{.tuloste tiedosto="esimerkit/02-sympy.odotettu"}
```

## Tarkat luvut ja liukuluvut

Tietokone esittää desimaaliluvut binäärimuotoisina **liukulukuina**,
joissa on noin 16 merkitsevää numeroa. Luku $0{,}1$ ei ole tarkasti
esitettävissä binäärimuodossa, joten $0{,}1 + 0{,}2$ ei ole tarkasti
$0{,}3$. Liukulukujen rakenne ja virheiden synty selitetään taidossa
*Miten tietokone laskee*; tässä riittää kolme sääntöä:

1. Älä vertaa liukulukuja operaattorilla `==`. Käytä toleranssia:
   `math.isclose` tai `numpy.isclose`.
2. Kun laskun pitää olla tarkka, käytä SymPyn rationaalilukuja
   (`sp.Rational(1, 3)`) tai Pythonin `fractions.Fraction`-tyyppiä.
3. Tarkka luku muutetaan likiarvoksi vasta lopussa.

```{.python tiedosto="esimerkit/02-tarkat.py" osa="liukuluvut"}
```

Yleisin ansa on kirjoittaa SymPy-lausekkeeseen `1/3`. Python laskee
jakolaskun ennen kuin SymPy näkee sen, joten lausekkeeseen päätyy
liukuluku $0{,}333\ldots$ eikä tarkka kolmasosa. Korjaus on
`sp.Rational(1, 3)` tai `sp.S(1)/3`, jossa `sp.S` muuttaa ensimmäisen
luvun SymPy-luvuksi. `nsimplify` arvaa liukuluvun tarkan muodon.

```{.python tiedosto="esimerkit/02-tarkat.py" osa="ansa"}
```

SymPyn kokonaisluvut ovat mielivaltaisen suuria, ja `evalf` laskee
halutulla tarkkuudella. Liukuluku pyöristää luvun $10^{20} + 1$ luvuksi
$10^{20}$, koska ykkönen on 21. merkitsevä numero.

```{.python tiedosto="esimerkit/02-tarkat.py" osa="tarkkuus"}
```

```{.tuloste tiedosto="esimerkit/02-tarkat.odotettu"}
```

## NumPy

NumPyn perustietotyyppi on taulukko (`ndarray`). Laskutoimitukset tehdään
koko taulukolle kerralla ilman silmukkaa, mikä on sekä lyhyempää että
satoja kertoja nopeampaa kuin Pythonin listat. `np.linspace(a, b, n)`
luo $n$ tasavälistä pistettä välille $[a, b]$ päätepisteet mukaan
lukien, ja sitä käytetään kuvaajan $x$-akselina.

```{.python tiedosto="esimerkit/02-numpy.py" osa="taulukko"}
```

SymPyn lauseke muunnetaan NumPy-funktioksi `lambdify`-funktiolla
moduulilla `numpy`. Saatu funktio ottaa taulukon ja palauttaa taulukon.
Tulosta verrataan käsin kirjoitettuun kaavaan toleranssilla.

```{.python tiedosto="esimerkit/02-numpy.py" osa="lambdify"}
```

```{.python tiedosto="esimerkit/02-numpy.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/02-numpy.odotettu"}
```

## Matplotlib

Matplotlibilla on kaksi rajapintaa. Tilallinen `pyplot` on kätevä
vuorovaikutteisessa käytössä, mutta ohjelmissa ja skripteissä
oliopohjainen tapa on selkeämpi: luodaan `Figure`, siihen akselit
(`add_subplot`) ja piirretään akseleille. Tiedosto tallennetaan metodilla
`savefig`, eikä näyttöä tarvita, joten sama koodi toimii palvelimella ja
CI-ympäristössä.

```{.python tiedosto="esimerkit/02-kuvaaja.py" osa="kuvaaja"}
```

```{.tuloste tiedosto="esimerkit/02-kuvaaja.odotettu"}
```

Hyvä kuvaaja kertoo, mitä akseleilla on, käyttää riittävän tiheää
näytteistystä (luku 4) ja merkitsee erikseen kiinnostavat pisteet, kuten
nollakohdat. Tämän tutoriaalin kuvat on piirretty samalla tavalla
skriptillä `kuvat/piirra.py`.

## Maxima

Maxima ajetaan joko vuorovaikutteisesti komennolla `maxima` tai
eräajona skriptitiedostosta. Eräajossa `batchload` lukee tiedoston
tulostamatta komentoja, joten tuloste syntyy vain `print`-kutsuista.
Valitsin `--very-quiet` jättää aloitusviestit pois, ja asetus
`display2d: false` tulostaa lausekkeet yhdelle riville, mikä on
välttämätöntä tulosteen vertailussa ja jatkokäsittelyssä.

Maximan kieli eroaa Pythonista muutamassa asiassa: komento päättyy
puolipisteeseen (`;` näyttää tuloksen) tai dollariin (`$` ei näytä),
sijoitus on `:`, funktio määritellään `:=`, potenssi on `^` ja vakiot
ovat `%pi`, `%e` ja `%i`.

```{.maxima tiedosto="esimerkit/maxima/02-perusteet.mac" osa="muokkaus"}
```

```{.maxima tiedosto="esimerkit/maxima/02-perusteet.mac" osa="sijoitus"}
```

```{.maxima tiedosto="esimerkit/maxima/02-perusteet.mac" osa="ratkaisu"}
```

```{.tuloste tiedosto="esimerkit/maxima/02-perusteet.odotettu"}
```

Tulokset ovat samat kuin SymPyllä, vaikka järjestys ja kirjoitusasu
vaihtelevat: Maxima listaa juuret laskevassa järjestyksessä ja kirjoittaa
kertolaskun ilman välilyöntejä. Tämän paketin esimerkkien Makefile ajaa
skriptit näin:

```{.makefile tiedosto="esimerkit/Makefile" osa="maxima"}
```

Ubuntun Maxima on käännetty GCL-nimisellä Lisp-toteutuksella, joka
kytkee käynnistyessään osoiteavaruuden satunnaistuksen pois päältä.
Dockerin oletusarvoinen järjestelmäkutsusuodatin (seccomp) estää tämän,
jolloin Maxima kaatuu kontissa virheeseen *Segmentation fault*. Siksi
tämän paketin kehityskontti käynnistetään asetuksella
`--security-opt=seccomp=unconfined`. Tavallisessa asennuksessa asetusta
ei tarvita.

Seuraava taulukko kokoaa vastaavat komennot. Se on myös pikaoppaassa.

| Tehtävä | SymPy | Maxima |
|---------|-------|--------|
| Laajenna | `expand(e)` | `expand(e)` |
| Jaa tekijöihin | `factor(e)` | `factor(e)` |
| Supista | `cancel(e)` | `ratsimp(e)` |
| Sijoita | `e.subs(x, 2)` | `subst(2, x, e)` tai `ev(e, x=2)` |
| Likiarvo | `e.evalf()`, `sp.N(e)` | `float(e)` |
| Ratkaise | `solve(e, x)` | `solve(e, x)` |
| Numeerinen juuri | `nsolve(e, x, x0)` | `find_root(e, x, a, b)` |
| Osamurrot | `apart(e, x)` | `partfrac(e, x)` |
| Summa | `summation(e, (k, 1, n))` | `sum(e, k, 1, n)`, `simpsum: true` |

## GNU Octave

Octave on numeerisen laskennan ympäristö, jonka kieli on lähes sama kuin
kaupallisen MATLABin: matriisit ovat perustietotyyppi, ja valmiita
funktioita on tuhansia. Octave on hyödyllinen erityisesti silloin, kun
työpaikalla tai kurssilla käytetään MATLABia. Tässä tutoriaalissa sitä ei
tarvita, koska NumPy kattaa samat tehtävät; jatkotaidot
*Differentiaaliyhtälöt ja Laplace-muunnos* ja *Numeeriset menetelmät*
näyttävät samat laskut myös Octavella.

## Käytännössä

- **Tarkista symbolisesti, laske numeerisesti.** Johda kaava
  SymPyllä tai Maximalla, varmista se sijoituksella tai erotuksella ja
  muunna se vasta sitten `lambdify`-funktiolla numeeriseksi.
- **Kaksi riippumatonta laskua.** Kun tulos on tärkeä, laske se kahdella
  eri tavalla: symbolisesti ja numeerisesti tai SymPyllä ja Maximalla.
  Kaksi samaan päätyvää ohjelmaa ovat vahvempi todiste kuin yksi.
- **Oletukset symboleille.** `positive=True` ja `real=True` estävät
  turhan monimutkaiset tulokset ja kertovat lukijalle, mitä muuttuja
  esittää.
- **Ei `1/3`:a SymPy-lausekkeeseen.** Kirjoita `sp.Rational(1, 3)`.
- **Ei `==`-vertailua liukuluvuille.** Käytä `math.isclose` tai
  `np.isclose` ja mieti, mikä toleranssi on järkevä.
- **Oliopohjainen Matplotlib ja `savefig`.** Kuva syntyy samoin
  komentoriviltä, palvelimelta ja testeistä.
- **Maxima eräajona.** `display2d: false`, `batchload` ja `print`
  tuottavat tulosteen, jota voi verrata ja jäsentää.

## Itsearviointi

- Osaat luoda SymPy-symbolit oletuksineen ja valita oikean
  muokkausfunktion (`expand`, `factor`, `cancel`, `simplify`).
- Osaat ratkaista yhtälön sekä funktiolla `solve` että `solveset` ja
  kertoa, milloin kumpaakin kannattaa käyttää.
- Osaat selittää, miksi $0{,}1 + 0{,}2 \ne 0{,}3$ liukuluvuilla ja miten
  tarkka laskenta tehdään SymPyllä.
- Osaat muuntaa SymPy-lausekkeen NumPy-funktioksi ja piirtää kuvaajan
  tiedostoon Matplotlibilla.
- Osaat ajaa Maxima-skriptin eräajona ja tulkita sen tulosteen.
