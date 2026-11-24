# Lukujonot, summat ja induktio

Lukujono on funktio, jonka lähtöjoukko on luonnolliset luvut: järjestetty
luettelo $a_1, a_2, a_3, \ldots$ Ohjelmoijalle jono on silmukan
peräkkäiset arvot, ja summa on silmukan kerryttämä tulos. Siksi jonot ja
summat ovat algoritmien työmäärän, lainojen ja kasvun laskennan perusta.
Luvussa käsitellään aritmeettinen ja geometrinen jono, summien
suljetut muodot, korkoa korolle ja annuiteettilaina sekä
induktiotodistuksen tarkistaminen koneella.

## Aritmeettinen ja geometrinen jono

Jono voidaan määritellä **rekursiivisesti**, eli kertomalla, miten
seuraava jäsen saadaan edellisestä, tai **suljetussa muodossa** kaavana
$a_n$. Rekursio vastaa silmukkaa ja suljettu muoto suoraa laskua.

| Jono | Rekursio | Suljettu muoto | Esimerkki |
|------|----------|----------------|-----------|
| Aritmeettinen | $a_{n+1} = a_n + d$ | $a_n = a_1 + (n-1)d$ | Loki kasvaa 40 Mt päivässä |
| Geometrinen | $b_{n+1} = q\,b_n$ | $b_n = b_1 q^{n-1}$ | Puskuri kaksinkertaistuu |

Suljetun muodon etu on, että sen voi ratkaista: milloin loki ylittää
1000 Mt, tai monesko puskurin koko riittää miljoonalle alkiolle. Vastaus on
pienin kokonaisluku, joka on vähintään yhtälön ratkaisu, eli ratkaisun
**katto** (`ceiling`).

```{.python tiedosto="esimerkit/08-jonot.py" osa="aritmeettinen"}
```

```{.python tiedosto="esimerkit/08-jonot.py" osa="geometrinen"}
```

Puskurin kaksinkertaistaminen on tavallinen tapa toteuttaa dynaaminen
taulukko (Pythonin lista, C++:n `std::vector`). Geometrisen jonon ansiosta
miljoonan alkion lisääminen vaatii vain 17 uudelleenvarausta.

SymPyn `rsolve` ratkaisee rekursioyhtälön suljettuun muotoon. Esimerkissä
$f(n+1) = 3f(n) + 2$, $f(1) = 1$, ja ratkaisu on $2 \cdot 3^{n-1} - 1$.

```{.python tiedosto="esimerkit/08-jonot.py" osa="rsolve"}
```

```{.tuloste tiedosto="esimerkit/08-jonot.odotettu"}
```

## Summat

Summamerkintä $\sum_{k=1}^{n} a_k$ tarkoittaa $a_1 + a_2 + \dots + a_n$.
Tärkeimmät suljetut muodot ovat:

$$\sum_{k=1}^{n} k = \frac{n(n+1)}{2}, \qquad
  \sum_{k=1}^{n} k^2 = \frac{n(n+1)(2n+1)}{6}, \qquad
  \sum_{k=1}^{n} q^{k-1} = \frac{q^n - 1}{q - 1} \ (q \ne 1).$$

Geometrinen summa suppenee, kun $|q| < 1$ ja $n \to \infty$: sen raja-arvo
on $\frac{1}{1-q}$. SymPyn `summation` laskee suljetut muodot ja huomaa
erikoistapauksen $q = 1$.

```{.python tiedosto="esimerkit/08-summat.py" osa="summat"}
```

### Algoritmin työmäärä

Kun silmukan sisällä on toinen silmukka, jonka pituus riippuu
ulommasta, kokonaistyö on summa. Esimerkiksi kaikkien parien vertailu
(vaikkapa lisäyslajittelussa) tekee $0 + 1 + \dots + (n-1) =
\frac{n(n-1)}{2}$ vertailua. Tuhannella alkiolla se on puoli miljoonaa,
miljoonalla puoli biljoonaa: neliöllisen algoritmin työ kasvaa nopeasti.
Summan arvo kannattaa tarkistaa laskemalla sama silmukka oikeasti.

```{.python tiedosto="esimerkit/08-summat.py" osa="tyomaara"}
```

### Harmoninen summa

**Harmoninen summa** $H(n) = 1 + \tfrac12 + \dots + \tfrac1n$ kasvaa rajatta
mutta hyvin hitaasti, suunnilleen kuten $\ln n + 0{,}5772$. Se esiintyy
algoritmien analyysissa: esimerkiksi satunnaisen taulukon maksimin
päivityksiä tehdään keskimäärin $H(n)$ kertaa. `math.fsum` laskee
liukulukusumman tarkemmin kuin tavallinen `sum`, koska se ei kadota
pienten termien pyöristysvirheitä.

```{.python tiedosto="esimerkit/08-summat.py" osa="harmoninen"}
```

```{.tuloste tiedosto="esimerkit/08-summat.odotettu"}
```

## Korkoa korolle ja annuiteettilaina

**Koronkorko** on geometrinen jono: pääoma kerrotaan joka kausi
korkotekijällä $1 + p$. Kun lasku tehdään tarkoilla murtoluvuilla
(`fractions.Fraction`), kaava ja vuosi kerrallaan etenevä simulaatio
antavat täsmälleen saman tuloksen. Liukuluvuilla ne eroaisivat
viimeisissä desimaaleissa.

```{.python tiedosto="esimerkit/08-korko.py" osa="korko"}
```

**Annuiteettilainassa** maksetaan joka kuukausi sama erä $A$, josta osa
on korkoa ja osa lyhennystä. Erä ratkaistaan ehdosta, että velka on
viimeisen erän jälkeen nolla. Kun lainan $L$ arvo $n$ kuukauden päästä,
$L(1+i)^n$, merkitään yhtä suureksi kuin erien arvo samalla hetkellä,
saadaan geometrinen summa, ja siitä erän kaava

$$A = \frac{L\, i\, (1+i)^n}{(1+i)^n - 1}.$$

SymPy johtaa kaavan itse, kun summa ja yhtälö annetaan sille.

```{.python tiedosto="esimerkit/08-korko.py" osa="annuiteetti"}
```

Kaava tarkistetaan simuloimalla laina kuukausi kerrallaan: velkaan
lisätään korko ja siitä vähennetään erä. Velan on oltava 300 erän
jälkeen nolla.

```{.python tiedosto="esimerkit/08-korko.py" osa="simulaatio"}
```

```{.tuloste tiedosto="esimerkit/08-korko.odotettu"}
```

Esimerkin luvut ovat havainnollistus, eivät lainatarjous: pankit
käyttävät viitekorkoa ja marginaalia, ja koron laskentatapa vaihtelee.
Periaate on kuitenkin sama kuin pankkien laskureissa.

## Induktio

**Induktiotodistus** osoittaa, että väite $P(n)$ pätee kaikilla
luonnollisilla luvuilla $n \ge n_0$. Se koostuu kahdesta osasta:

1. **Perusaskel**: $P(n_0)$ pätee.
2. **Induktioaskel**: jos $P(n)$ pätee, myös $P(n+1)$ pätee.

Todistuksen logiikka ja sen muunnelmat opetetaan taidossa *Diskreetti
matematiikka*. Tässä katsotaan, miten kone tarkistaa todistuksen
laskuvaiheet. Väite $1^3 + 2^3 + \dots + n^3 = \left(\frac{n(n+1)}{2}\right)^2$
on tyypillinen: perusaskel on sijoitus, ja induktioaskeleessa pitää
näyttää, että $F(n) + (n+1)^3 = F(n+1)$, mikä on polynomien
yhtäsuuruus.

```{.python tiedosto="esimerkit/08-induktio.py" osa="induktio"}
```

### Testaaminen ei ole todistamista

Kaava $n^2 + n + 41$ tuottaa alkuluvun kaikilla $n = 0, \ldots, 39$.
Neljäkymmentä onnistunutta testiä ei silti todista väitettä: kohdassa
$n = 40$ arvo on $41^2$. Sama pätee ohjelmistotestaukseen: testit
löytävät virheitä, mutta eivät osoita niiden puuttumista.

```{.python tiedosto="esimerkit/08-induktio.py" osa="vaara"}
```

Epäyhtälöiden induktiotodistuksissa induktioaskel nojaa usein
apuepäyhtälöön, joka pätee vasta tietystä $n$:stä alkaen. Väitteessä
$2^n > n^2$ ($n \ge 5$) tarvitaan $2n^2 \ge (n+1)^2$, joka pätee, kun
$n \ge 1 + \sqrt 2 \approx 2{,}41$. Kone ratkaisee apuepäyhtälön, ja
perusaskel tarkistetaan sijoituksella.

```{.python tiedosto="esimerkit/08-induktio.py" osa="epayhtalo"}
```

```{.tuloste tiedosto="esimerkit/08-induktio.odotettu"}
```

## Samat laskut Maximalla

Maximan `sum` laskee summan suljetun muodon, kun asetus `simpsum` on
päällä. Induktioaskeleen polynomiyhtälö tarkistetaan `ratsimp`-
funktiolla.

```{.maxima tiedosto="esimerkit/maxima/08-summat.mac" osa="summat"}
```

```{.maxima tiedosto="esimerkit/maxima/08-summat.mac" osa="induktio"}
```

```{.maxima tiedosto="esimerkit/maxima/08-summat.mac" osa="korko"}
```

```{.tuloste tiedosto="esimerkit/maxima/08-summat.odotettu"}
```

## Käytännössä

- **Etsi suljettu muoto.** Rekursio sopii laskemiseen, suljettu muoto
  ratkaisemiseen ja arviointiin. `rsolve` ja `summation` löytävät sen
  usein suoraan.
- **Tarkista kaava simuloimalla.** Kaava ja silmukka laskevat saman
  asian eri tavoin, joten niiden yhtäpitävyys on vahva tarkistus.
- **Raha tarkoilla luvuilla.** Käytä rahalaskuissa `Fraction`- tai
  `decimal.Decimal`-tyyppiä, älä liukulukuja, ja pyöristä vasta
  tulostettaessa.
- **Sisäkkäiset silmukat ovat summia.** Kirjoita työmäärä summana ja
  laske sen suljettu muoto ennen kuin ajat koodin suurella syötteellä.
- **Kone tarkistaa todistuksen laskut, ei logiikkaa.** Perusaskel ja
  induktioaskeleen algebra ovat koneelle helppoja, mutta päättelyn
  rakenne on oma vastuusi.

## Itsearviointi

- Osaat kirjoittaa aritmeettisen ja geometrisen jonon rekursiivisesti ja
  suljetussa muodossa sekä ratkaista, monesko jäsen ylittää annetun rajan.
- Osaat laskea aritmeettisen, geometrisen ja potenssisumman suljetun
  muodon sekä arvioida sisäkkäisten silmukoiden työmäärän summana.
- Osaat johtaa annuiteettilainan erän kaavan ja tarkistaa sen
  simuloimalla.
- Osaat tarkistaa induktiotodistuksen perus- ja induktioaskeleen
  SymPyllä ja selittää, miksi testaus ei ole todistus.
