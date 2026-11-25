# Kombinatoriikka

Kombinatoriikka laskee, montako vaihtoehtoa on: kuinka monta
salasanaa, kuinka monta testitapausta, kuinka monta reittiä. Vastaus
kertoo, voiko kaikki käydä läpi, kuinka vahva salasana on ja kuinka
todennäköinen törmäys on. Jokainen tämän luvun kaava tarkistetaan
luettelemalla vaihtoehdot `itertools`-moduulilla pienellä tapauksella.
Luettelo on hidas mutta ilmeisen oikea, joten se on erinomainen testi
kaavalle.

## Summa- ja tuloperiaate

**Summaperiaate**: jos tehtävän voi tehdä joko $m$ tai $n$ tavalla,
eivätkä tavat ole päällekkäisiä, tapoja on $m + n$. **Tuloperiaate**:
jos tehtävä koostuu vaiheista, joissa on $m$ ja $n$ vaihtoehtoa, tapoja
on $m \cdot n$. Kahdeksan merkin salasana, jonka merkit ovat pieniä
kirjaimia tai numeroita, valitaan summaperiaatteella 36 merkistä ja
tuloperiaatteella kahdeksan kertaa:

```{.python tiedosto="esimerkit/08-laskusaannot.py" osa="tulo"}
```

```{.tuloste tiedosto="esimerkit/08-laskusaannot.odotettu" rivit="1-3"}
```

$36^8 \approx 2{,}8 \cdot 10^{12}$ kuulostaa paljolta, mutta
näytönohjain kokeilee nopeita tiivisteitä miljardeja sekunnissa.
Pituuden kasvattaminen kasvattaa vaihtoehtoja eksponentiaalisesti, kun
taas merkistön kasvattaminen vain polynomisesti; siksi pitkä
salalause voittaa lyhyen monimutkaisen salasanan.

## Permutaatiot ja kombinaatiot

Kun $n$:stä alkiosta valitaan $k$ ilman toistoa, ratkaisee
**järjestyksen merkitys**:

- **Permutaatio** (järjestys merkitsee):
  $P(n, k) = n(n-1)\cdots(n-k+1) = \frac{n!}{(n-k)!}$.
  Mitalijärjestykset, ensimmäiset $k$ jonossa.
- **Kombinaatio** (järjestys ei merkitse):
  $\binom{n}{k} = \frac{n!}{k!\,(n-k)!}$. Joukkueet, lottorivit,
  osajoukot.

Jokainen $k$:n alkion kombinaatio voidaan järjestää $k!$ tavalla,
joten $P(n, k) = \binom{n}{k} \cdot k!$.

```{.python tiedosto="esimerkit/08-laskusaannot.py" osa="jarjestys"}
```

```{.tuloste tiedosto="esimerkit/08-laskusaannot.odotettu" rivit="4-6"}
```

Kun toistot sallitaan ja järjestys ei merkitse, puhutaan
**kombinaatioista toistoineen**: $k$ jäätelöpalloa $n$ mausta voi
valita $\binom{n + k - 1}{k}$ tavalla. Kaava tulee ”tähdistä ja
väliviivoista”: jono, jossa on $k$ palloa ja $n - 1$ väliviivaa
makujen välissä, määrää annoksen yksikäsitteisesti.

```{.python tiedosto="esimerkit/08-laskusaannot.py" osa="toisto"}
```

```{.tuloste tiedosto="esimerkit/08-laskusaannot.odotettu" rivit="7-"}
```

| Valinta | Järjestys merkitsee | Järjestys ei merkitse |
|---------|---------------------|-----------------------|
| ilman toistoa | $\frac{n!}{(n-k)!}$ — `permutations(x, k)` | $\binom{n}{k}$ — `combinations(x, k)` |
| toistoin | $n^k$ — `product(x, repeat=k)` | $\binom{n+k-1}{k}$ — `combinations_with_replacement(x, k)` |

## Binomikertoimet

Binomikertoimet muodostavat **Pascalin kolmion**, jossa jokainen luku
on kahden yläpuolisen summa. Sääntö
$\binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}$ on kombinatorinen:
valitaanko tietty alkio vai ei.

```{.python tiedosto="esimerkit/08-binomi.py" osa="pascal"}
```

```{.tuloste tiedosto="esimerkit/08-binomi.odotettu" rivit="1-7"}
```

Kertoimien identiteetit voi tarkistaa suoraan. **Binomilause**
$(x + y)^n = \sum_{k=0}^{n} \binom{n}{k} x^k y^{n-k}$ antaa nimen
kertoimille, ja kun $x = y = 1$, saadaan
$\sum_k \binom{n}{k} = 2^n$: osajoukkojen määrä kokoluokittain
laskettuna (luku *Joukot ja funktiot*).

```{.python tiedosto="esimerkit/08-binomi.py" osa="identiteetit"}
```

```{.tuloste tiedosto="esimerkit/08-binomi.odotettu" rivit="8-11"}
```

Kombinatorinen ajattelu ratkaisee laskutehtävän usein ilman
laskemista. Ruudukossa, jossa saa kulkea vain oikealle ja ylös, reitti
$6 \times 4$ -alueen yli on 10 askeleen jono, josta 4 on ylös-askelia:
reittejä on $\binom{10}{4}$. Sama tulos saadaan rekursiolla, joka laskee
reitit ruutu ruudulta, ja luettelemalla:

```{.python tiedosto="esimerkit/08-binomi.py" osa="hilapolut"}
```

```{.tuloste tiedosto="esimerkit/08-binomi.odotettu" rivit="12-"}
```

![Reittien määrä jokaiseen risteykseen on vasemman ja alemman
naapurin summa, sama sääntö kuin Pascalin kolmiossa. Korostettu reitti
on yksi 210:stä.](kuvat/hilapolut.png){width=58%}

## Lokeroperiaate

**Lokeroperiaate**: jos $n + 1$ esinettä laitetaan $n$ lokeroon,
jossakin lokerossa on vähintään kaksi. Yleisemmin jossakin lokerossa on
vähintään $\lceil m / n \rceil$ esinettä. Periaate on ilmeinen mutta
sen seuraukset eivät:

- Hajautustaulussa on väistämättä törmäyksiä, kun avaimia on enemmän
  kuin lokeroita (luku *Joukot ja funktiot*).
- Mikään häviötön pakkausalgoritmi ei lyhennä kaikkia syötteitä:
  $n$-bittisiä tiedostoja on $2^n$ mutta lyhyempiä vain $2^n - 1$.
- Tiivistefunktiolla on törmäyksiä, koska syötteitä on enemmän kuin
  tiivisteitä.

```{.python tiedosto="esimerkit/08-lokero.py" osa="lokero"}
```

```{.tuloste tiedosto="esimerkit/08-lokero.odotettu" rivit="1-2"}
```

## Inkluusio–ekskluusio

Kun joukot ovat päällekkäisiä, summaperiaate laskee leikkauksen
kahdesti. **Inkluusion ja ekskluusion periaate** korjaa sen:

$$\lvert A \cup B \cup C \rvert = \lvert A \rvert + \lvert B \rvert +
\lvert C \rvert - \lvert A \cap B \rvert - \lvert A \cap C \rvert -
\lvert B \cap C \rvert + \lvert A \cap B \cap C \rvert.$$

```{.python tiedosto="esimerkit/08-lokero.py" osa="inkluusio"}
```

```{.tuloste tiedosto="esimerkit/08-lokero.odotettu" rivit="3-3"}
```

![Esimerkin joukot Vennin kaaviona. Alueiden luvut ovat erillisiä
osia: $\lvert A \rvert = 267 + 133 + 33 + 67 = 500$. Summa
$\lvert A \rvert + \lvert B \rvert + \lvert C \rvert$ laskee
parileikkaukset kahdesti ja keskustan kolmesti; kaava poistaa parit ja
palauttaa keskustan. Seitsemän alueen summa on
734.](kuvat/venn-inkluusio.png){width=55%}

Periaate ratkaisee myös **epäjärjestykset**: montako permutaatiota
on, joissa yksikään alkio ei ole paikallaan? Jos jokainen vie
pikkujoulujen lahjan ja nostaa satunnaisen, kuinka usein kukaan ei saa
omaansa? Vastaus lähestyy nopeasti lukua $1/e \approx 0{,}368$
osallistujamäärästä riippumatta:

```{.python tiedosto="esimerkit/08-lokero.py" osa="epajarjestys"}
```

```{.tuloste tiedosto="esimerkit/08-lokero.odotettu" rivit="4-"}
```

## Käytännössä

- **Laske ennen kuin luettelet.** Testimatriisi, jossa on kymmenen
  kaksiarvoista asetusta, on $2^{10} = 1024$ tapausta; kolmella
  arvolla $3^{10} \approx 59\,000$. Laskelma kertoo, onko kaikkien
  tapausten testaus mahdollista vai tarvitaanko parittaista testausta
  (*pairwise testing*).
- **Tarkista kaava luettelemalla.** `itertools.product`,
  `permutations` ja `combinations` tekevät pienen tapauksen
  luettelosta yhden rivin. Ristiintarkistus löytää ”off by one”- ja
  järjestysvirheet.
- **Kysy, merkitseekö järjestys ja sallitaanko toisto.** Kaavan valinta
  riippuu vain näistä kahdesta kysymyksestä.
- **Käytä `math.comb` ja `math.perm`.** Ne laskevat tarkasti
  kokonaisluvuilla; kertomien jakaminen liukuluvuilla menettää
  tarkkuuden suurilla luvuilla.
- **Muista lokeroperiaate, kun lupaat yksikäsitteisyyttä.** Lyhyt
  tunniste, tiiviste tai pakattu esitys ei voi olla yksikäsitteinen,
  jos mahdollisia syötteitä on enemmän kuin tunnisteita.

## Itsearviointi

- Osaat käyttää summa- ja tuloperiaatetta ja laskea esimerkiksi
  salasanojen tai testitapausten määrän.
- Osaat valita oikean kaavan (permutaatio, kombinaatio, toistoin tai
  ilman) ja tarkistaa sen luettelemalla `itertools`-moduulilla.
- Osaat käyttää binomikertoimia ja Pascalin kolmiota sekä ratkaista
  hilapolkutehtävän kombinatorisesti.
- Osaat soveltaa lokeroperiaatetta ja inkluusion ja ekskluusion
  periaatetta.
