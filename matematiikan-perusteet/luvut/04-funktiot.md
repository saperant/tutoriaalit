# Funktiot ja kuvaajat

**Funktio** liittää jokaiseen lähtöjoukon alkioon täsmälleen yhden
maalijoukon alkion. Ohjelmoijalle käsite on tuttu: Python-funktio, joka
palauttaa aina saman tuloksen samalla syötteellä eikä muuta mitään
muuta, on matemaattinen funktio. Luvussa käydään läpi määrittely- ja
arvojoukko, yhdistetty ja käänteinen funktio sekä paloittain määritellyt
funktiot. Nollakohtia etsitään sekä kuvaajasta että ohjelmalla, ja
lopuksi katsotaan, miten kuvaaja voi johtaa harhaan.

## Määrittely- ja arvojoukko

**Määrittelyjoukko** on niiden $x$:n arvojen joukko, joilla funktion
lauseke on määritelty. Reaalifunktioilla kolme tavallisinta rajoitusta
ovat:

| Lauseke | Ehto | Syy |
|---------|------|-----|
| $\frac{p(x)}{q(x)}$ | $q(x) \ne 0$ | Nollalla ei voi jakaa |
| $\sqrt{g(x)}$ | $g(x) \ge 0$ | Negatiivisella luvulla ei ole reaalista neliöjuurta |
| $\ln g(x)$ | $g(x) > 0$ | Logaritmi on määritelty vain positiivisille luvuille |

**Arvojoukko** on niiden arvojen joukko, joita funktio saa. SymPyn
apufunktiot `continuous_domain` ja `function_range` laskevat molemmat.
Ensimmäinen palauttaa joukon, jossa funktio on jatkuva, mikä
alkeisfunktioilla on sama kuin määrittelyjoukko.

```{.python tiedosto="esimerkit/04-maarittely.py" osa="joukot"}
```

```{.tuloste tiedosto="esimerkit/04-maarittely.odotettu"}
```

Funktion $1/(x^2 - 4)$ arvojoukossa on aukko välillä $]-\tfrac14, 0]$:
välillä $-2 < x < 2$ nimittäjä on negatiivinen ja enintään $-4$, joten
funktion arvot ovat enintään $-\tfrac14$, ja muualla ne ovat positiivisia.
Tällaisen tuloksen tarkistaminen kuvaajasta on hyvä harjoitus. Ääretön
päätepiste `oo` ei kuulu väliin, vaikka SymPy kirjoittaa välin
suljetuksi.

## Yhdistetty funktio ja käänteisfunktio

**Yhdistetty funktio** $f(g(x))$ syöttää $g$:n tuloksen $f$:lle.
Järjestyksellä on väliä: $f(g(x))$ ja $g(f(x))$ ovat yleensä eri
funktioita. SymPyssä yhdistäminen on sijoitus.

```{.python tiedosto="esimerkit/04-kaanteis.py" osa="yhdistetty"}
```

**Käänteisfunktio** $f^{-1}$ kumoaa funktion $f$: $f^{-1}(f(x)) = x$.
Käänteisfunktio löydetään ratkaisemalla yhtälö $y = f(x)$ muuttujan $x$
suhteen ja vaihtamalla sitten muuttujien nimet. Celsius- ja
Fahrenheit-asteiden muunnos on tuttu esimerkki: muunnoskaava on
lineaarinen, joten käänteinen kaava saadaan suoraan.

```{.python tiedosto="esimerkit/04-kaanteis.py" osa="kaanteis"}
```

Käänteisfunktio on olemassa vain, jos funktio on **bijektio**: jokaiseen
arvoon päädytään täsmälleen yhdestä lähtöarvosta. Funktio $x^2$ ei ole
bijektio reaaliluvuilla, koska $(-3)^2 = 3^2$. Kun määrittelyjoukko
rajoitetaan ei-negatiivisiin lukuihin, käänteisfunktio on $\sqrt{x}$.
SymPyssä rajoitus tehdään symbolin oletuksella.

```{.python tiedosto="esimerkit/04-kaanteis.py" osa="rajoitus"}
```

```{.tuloste tiedosto="esimerkit/04-kaanteis.odotettu"}
```

Käänteisfunktion kuvaaja on alkuperäisen kuvaajan peilikuva suoran
$y = x$ suhteen, koska käänteisfunktio vaihtaa koordinaattien roolit.
Kuvassa on eksponenttifunktio ja sen käänteisfunktio luonnollinen
logaritmi (luku 5): piste $(0, 1)$ vaihtuu pisteeksi $(1, 0)$.

![Funktio $e^x$ ja sen käänteisfunktio $\ln x$ ovat toistensa peilikuvia
suoran $y = x$ suhteen.](kuvat/kaanteis.png){width=50%}

## Paloittain määritelty funktio

Monet käytännön säännöt ovat **paloittain määriteltyjä**: verotus,
porrastetut hinnat ja ohjauskäyrät. SymPyn `Piecewise` ottaa listan
pareja (lauseke, ehto), ja ensimmäinen tosi ehto ratkaisee. Esimerkin
kuvitteellisessa siirtohinnassa ensimmäiset 300 kWh maksavat 8 senttiä
ja loput 6 senttiä kilowattitunnilta.

```{.python tiedosto="esimerkit/04-paloittain.py" osa="paloittain"}
```

Hinnoittelun on hyvä olla **jatkuva**: jos hinta hyppäisi rajakohdassa,
yksi lisäkilowattitunti voisi maksaa kymmeniä euroja. Jatkuvuus
tarkistetaan vertaamalla toispuoleisia **raja-arvoja**: arvoa, jota
funktio lähestyy vasemmalta ja oikealta. Raja-arvot käsitellään tarkemmin
taidossa *Differentiaali- ja integraalilaskenta*; tässä riittää, että
`sp.limit` laskee ne.

```{.python tiedosto="esimerkit/04-paloittain.py" osa="jatkuvuus"}
```

Paloittain määritellyn funktion käänteisongelma, eli kuinka paljon voi
kuluttaa annetulla summalla, ratkeaa samalla `solve`-kutsulla. SymPy
valitsee automaattisesti oikean palan.

```{.python tiedosto="esimerkit/04-paloittain.py" osa="kaanteinen"}
```

```{.tuloste tiedosto="esimerkit/04-paloittain.odotettu"}
```

## Nollakohdat numeerisesti: puolitushaku

Kaikilla yhtälöillä ei ole tarkkaa ratkaisua. Silloin nollakohta
etsitään numeerisesti. Yksinkertaisin menetelmä on **puolitushaku**: jos
jatkuva funktio on välin päätepisteissä erimerkkinen, sillä on välillä
nollakohta (**Bolzanon lause**). Jaetaan väli kahtia, valitaan se puolisko,
jonka päätepisteissä merkki vaihtuu, ja toistetaan.

```{.python tiedosto="esimerkit/04-puolitus.py" osa="puolitus"}
```

Puolitushaun etu on ennustettavuus: jokainen kierros puolittaa välin,
joten $n$ kierroksen jälkeen välin pituus on $(b - a)/2^n$. Toleranssiin
$\varepsilon$ päästään, kun $(b-a)/2^n \le 2\varepsilon$, eli
$n = \lceil \log_2 \frac{b-a}{2\varepsilon} \rceil$ kierroksella.
Funktiolle $x^3 - x - 2$ välillä $[1, 2]$ ja toleranssilla $10^{-9}$
kierroksia tarvitaan 29.

```{.python tiedosto="esimerkit/04-puolitus.py" osa="kaytto"}
```

Funktio tarkistaa ehtonsa ja nostaa poikkeuksen, jos merkki ei vaihdu.
Ilman tarkistusta haku palauttaisi välin päätepisteen ja antaisi
vaikutelman ratkaisusta, jota ei ole.

```{.python tiedosto="esimerkit/04-puolitus.py" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/04-puolitus.odotettu"}
```

Tulokset eroavat yhdeksännessä desimaalissa, koska puolitushaku
pysähtyy, kun virhe on alle $10^{-9}$, eikä se pyöristä tulosta.
Nopeammat menetelmät, kuten Newtonin menetelmä, opetetaan taidoissa
*Differentiaali- ja integraalilaskenta* ja *Numeeriset menetelmät*.
Puolitushaku on sama idea kuin binäärihaku järjestetystä taulukosta
(taito *Algoritmit*).

## Kuvaajan sudenkuopat

Tietokone piirtää kuvaajan laskemalla funktion arvon äärellisessä
määrässä pisteitä ja yhdistämällä ne viivoilla. Kaksi asiaa voi mennä
pieleen.

**Liian harva näytteistys.** Funktio $\sin(2\pi \cdot 99x)$ värähtelee 99
kertaa välillä $[0, 1]$. Jos se lasketaan sadassa tasavälisessä
pisteessä, pisteiden väli on $1/99$, ja jokainen piste osuu nollakohtaan:
kuvaaja on vaakasuora viiva. 101 pisteellä kuvaaja näyttää
yhdeltä hitaalta siniaallolta. Vasta riittävän tiheä näytteistys
paljastaa todellisen funktion.

```{.python tiedosto="esimerkit/04-naytteistys.py" osa="harva"}
```

![Sama funktio $\sin(2\pi\cdot 99x)$ 101 pisteellä (vasemmalla) ja
2000 pisteellä kymmenesosalla välistä (oikealla). Harva näytteistys
näyttää aivan eri funktion.](kuvat/naytteistys.png){width=100%}

Ilmiön nimi on **laskostuminen** (engl. *aliasing*), ja se on
signaalinkäsittelyn keskeinen käsite: ääni tai mittaussignaali pitää
näytteistää yli kaksi kertaa sen suurinta taajuutta tiheämmin. Siitä
lisää taidossa *Signaalit ja järjestelmät*.

**Asymptootit.** Funktiolla $\tan x$ on pystyasymptootti kohdassa
$x = \pi/2$. Piirto-ohjelma yhdistää asymptootin molemmin puolin olevat
pisteet pystysuoralla viivalla, joka näyttää funktion osalta mutta ei ole.
Korjaus on katkaista viiva: kun suuret arvot korvataan NaN-arvoilla
(*not a number*), Matplotlib jättää niiden kohdalle aukon.

```{.python tiedosto="esimerkit/04-naytteistys.py" osa="asymptootti"}
```

```{.tuloste tiedosto="esimerkit/04-naytteistys.odotettu"}
```

## Samat laskut Maximalla

Maximassa funktio määritellään operaattorilla `:=`, ja paloittain
määritelty funktio kirjoitetaan `if`-lausekkeena. Numeerisen juuren
etsii `find_root`, joka käyttää puolitushakua yhdistettynä nopeampaan
menetelmään, ja `realroots` antaa polynomin kaikki reaalijuuret
halutulla tarkkuudella. Tulokset eroavat toisistaan viimeisissä
desimaaleissa, koska menetelmien pysähtymisehdot ovat erilaiset.

```{.maxima tiedosto="esimerkit/maxima/04-funktiot.mac" osa="funktiot"}
```

```{.maxima tiedosto="esimerkit/maxima/04-funktiot.mac" osa="paloittain"}
```

```{.maxima tiedosto="esimerkit/maxima/04-funktiot.mac" osa="juuri"}
```

```{.tuloste tiedosto="esimerkit/maxima/04-funktiot.odotettu"}
```

## Käytännössä

- **Selvitä määrittelyjoukko ennen laskua.** Se kertoo, mitkä tulokset
  ovat mahdollisia, ja paljastaa jakolaskut nollalla ja negatiiviset
  logaritmien argumentit ennen kuin ohjelma kaatuu.
- **Tarkista käänteisfunktio molempiin suuntiin.** Sekä $f(f^{-1}(x))$
  että $f^{-1}(f(x))$ sievenevät muotoon $x$, jos kaava on oikein.
- **Tarkista paloittain määritellyn funktion rajakohdat.** Jatkuvuus
  tai tarkoituksellinen hyppy kannattaa testata erikseen, koska
  virheellinen vertailuoperaattori (`<` vs. `<=`) on tavallinen
  ohjelmointivirhe.
- **Numeerinen haku tarvitsee lähtöehdot.** Puolitushaku vaatii
  merkinvaihdon ja Newtonin menetelmä hyvän alkuarvauksen. Tarkista ehto
  ja nosta poikkeus, jos se ei täyty.
- **Epäile kuvaajaa.** Piirrä tiheämmin ja eri väleillä. Jos kuva
  muuttuu oleellisesti, näytteistys oli liian harva.

## Itsearviointi

- Osaat määrittää funktion määrittely- ja arvojoukon käsin ja SymPyllä.
- Osaat muodostaa yhdistetyn funktion ja käänteisfunktion ja tarkistaa
  jälkimmäisen symbolisesti.
- Osaat kirjoittaa paloittain määritellyn funktion `Piecewise`-oliona ja
  tutkia sen jatkuvuutta rajakohdassa.
- Osaat toteuttaa puolitushaun ja laskea etukäteen, montako kierrosta
  annettuun tarkkuuteen tarvitaan.
- Osaat tunnistaa harvan näytteistyksen ja asymptoottien aiheuttamat
  virheet kuvaajassa.
