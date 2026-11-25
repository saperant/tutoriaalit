# Lausekkeet ja listat

Imperatiivisessa kielessä ohjelma on jono lauseita, jotka muuttavat
tilaa. Funktionaalisessa kielessä ohjelma on **lauseke**, jolla on arvo.
Racketissa ei ole erillisiä lauseita. `if`, `cond`, `let` ja
funktiokutsu tuottavat kaikki arvon, ja ohjelma rakennetaan
yhdistelemällä lausekkeita.

## Arvioinnin säännöt

Lauseke arvioidaan kolmella säännöllä:

1. **Vakio**, kuten `42`, `"teksti"` tai `#t`, on oma arvonsa.
2. **Nimi**, kuten `hinta`, korvataan siihen sidotulla arvolla.
3. **Lista** `(f a b ...)` on kutsu. Ensin arvioidaan `f` ja
   argumentit, sitten funktiota sovelletaan argumentteihin.

Poikkeuksen tekevät **erikoismuodot**, kuten `define`, `if`, `let`,
`lambda` ja `quote`. Niillä on omat arviointisääntönsä. `(if ehto a b)`
arvioi vain toisen haaroista. Funktio ei voisi toimia näin, koska sen
argumentit arvioidaan aina ennen kutsua. Luku 7 näyttää, miten makroilla
tehdään omia erikoismuotoja.

## Luvut

Racketin lukutorni eroaa useimmista kielistä. Kokonaisluvut ovat
rajattomia ja jakolasku tuottaa tarkan rationaaliluvun. Liukulukuja
käytetään vain, kun niitä pyydetään (desimaalipiste literaalissa tai
`exact->inexact`).

```{.scheme tiedosto="esimerkit/02-luvut.rkt" osa="tarkat"}
```

Tarkat luvut sopivat rahalaskentaan: summa pysyy tarkkana, ja pyöristys
tehdään kerran, lopuksi, valitulla säännöllä. Racketin `round` pyöristää
puolikkaat parilliseen (pankkiirin pyöristys).

```{.scheme tiedosto="esimerkit/02-luvut.rkt" osa="rahat"}
```

```{.tuloste tiedosto="esimerkit/02-luvut.odotettu"}
```

## Listat ja parit

Listan perusosa on **pari** eli cons-solu. `(cons a b)` luo parin, jonka
osat saadaan funktioilla `car` ja `cdr` (nykyään myös `first` ja
`rest`). Lista on parien ketju, joka päättyy tyhjään listaan `'()`:

    (list 1 2 3) = (cons 1 (cons 2 (cons 3 '())))

Määritelmä on **rekursiivinen**: lista on joko tyhjä tai pari, jonka
loppuosa on lista. Luvun 3 rekursiiviset funktiot seuraavat tätä
rakennetta.

```{.scheme tiedosto="esimerkit/02-listat.rkt" osa="rakenne"}
```

`cons` ei kopioi vanhaa listaa, vaan uusi lista *jakaa* sen. Jakaminen
on turvallista, koska listoja ei muuteta. Etuun lisääminen on siksi
O(1), kun taas loppuun lisääminen (`append`) kopioi koko listan.

```{.dot otsikko="Laatikko–osoitin-kaavio esimerkin listoista. Jokainen pari on kaksi lokeroa: `car` osoittaa alkioon ja `cdr` loppulistaan. `lisatty` on yksi uusi pari, jonka `cdr` osoittaa vanhaan listaan."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.45;
  node [shape=plain, style=""];
  nimi1 [label=<<i>lisatty</i>>];
  nimi2 [label=<<i>kaupungit</i>>];
  p0 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr><td port="a" bgcolor="#EEF1F6">car</td><td port="d" bgcolor="#EEF1F6">cdr</td></tr></table>>];
  p1 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr><td port="a" bgcolor="#FFFFFF">car</td><td port="d" bgcolor="#FFFFFF">cdr</td></tr></table>>];
  p2 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr><td port="a" bgcolor="#FFFFFF">car</td><td port="d" bgcolor="#FFFFFF">cdr</td></tr></table>>];
  p3 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6"><tr><td port="a" bgcolor="#FFFFFF">car</td><td port="d" bgcolor="#FFFFFF">cdr</td></tr></table>>];
  tyhja [label="'()"];
  e [label="\"Espoo\""]; o [label="\"Oulu\""]; t [label="\"Tampere\""]; u [label="\"Turku\""];
  { rank=same; nimi1 -> p0 [minlen=1]; e; }
  { rank=same; nimi2 -> p1 [minlen=1]; o; }
  { rank=same; p2; t; }
  { rank=same; p3; u; }
  p0:d:c -> p1:a:w; p1:d:c -> p2:a:w; p2:d:c -> p3:a:w; p3:d:c -> tyhja;
  p0:a:s -> e; p1:a:s -> o; p2:a:s -> t; p3:a:s -> u;
}
```

### Lainaus

`quote` eli lyhyesti `'` estää arvioinnin. `'(maito 5)` ei kutsu
funktiota `maito`, vaan se on kaksialkioinen lista, jonka ensimmäinen
alkio on **symboli** `maito`. Symboli on nimetty, tunnistettava arvo,
jota verrataan vakioajassa. Symbolit vastaavat muiden kielten
enumeraatioita ja internoituja merkkijonoja.

```{.scheme tiedosto="esimerkit/02-listat.rkt" osa="lainaus"}
```

Tulostusfunktiot eroavat toisistaan: `display` ja `~a` tulostavat
ihmiselle (merkkijono ilman lainausmerkkejä), `write` ja `~s` tulostavat
luettavassa muodossa, ja `print` ja `~v` tulostavat lausekkeena, jonka
arvioiminen tuottaa saman arvon.

```{.scheme tiedosto="esimerkit/02-listat.rkt" osa="valmiit"}
```

```{.tuloste tiedosto="esimerkit/02-listat.odotettu"}
```

`list-ref` ja `length` käyvät listan läpi alusta. Jos dataa haetaan
indeksillä, oikea rakenne on **vektori** (`vector`, `vector-ref`), joka
vastaa muiden kielten taulukkoa.

## Ehdot, sidonnat ja yhtäsuuruus

`cond` on monihaarainen ehto. Se palauttaa ensimmäisen toteutuvan haaran
arvon. `let` sitoo nimet lohkon ajaksi ja `let*` peräkkäin, jolloin
myöhempi sidonta näkee aiemmat.

```{.scheme tiedosto="esimerkit/02-ehdot.rkt" osa="cond"}
```

```{.scheme tiedosto="esimerkit/02-ehdot.rkt" osa="let"}
```

Totuusarvoissa on yksinkertainen sääntö: **vain `#f` on epätosi**.
Tyhjä lista, nolla ja tyhjä merkkijono ovat tosia. Siksi monet
funktiot palauttavat onnistuessaan hyödyllisen arvon ja
epäonnistuessaan `#f` (`member`, `assoc`, `string->number`).
`or` palauttaa ensimmäisen toden arvon, joten sillä saa oletusarvon.

```{.scheme tiedosto="esimerkit/02-ehdot.rkt" osa="totuus"}
```

Yhtäsuuruutta on useaa lajia:

| Funktio | Vertaa | Vastine |
|---------|--------|---------|
| `eq?` | samaa oliota (osoitinvertailu) | Javan `==` olioille, Pythonin `is` |
| `eqv?` | kuten `eq?`, lisäksi luvut ja merkit arvoina | |
| `equal?` | rakennetta rekursiivisesti | Javan `equals`, Pythonin `==` |
| `=` | lukuarvoa | |

```{.scheme tiedosto="esimerkit/02-ehdot.rkt" osa="yhtasuuruus"}
```

```{.tuloste tiedosto="esimerkit/02-ehdot.odotettu"}
```

## Käytännössä

- **Lauseke-ajattelu yleistyy.** Rustissa, Kotlinissa ja Scalassa `if`
  ja `match`/`when` ovat lausekkeita, ja Javassa `switch`-lauseke
  (Java 14) toimii samoin. Kun haarojen arvo sijoitetaan yhteen
  nimeen, muuttujaa ei tarvitse esitellä ilman arvoa ja täyttää
  myöhemmin. Koko luokka "muuttuja jäi alustamatta" -virheitä katoaa.
- **Tarkat luvut ovat harvinaisia muualla.** Pythonissa on `fractions`
  ja `decimal`, Javassa `BigDecimal`. Useimmissa kielissä `0.1 + 0.2`
  on epätarkka ja kokonaisluku voi vuotaa yli. Rahat lasketaan
  kokonaislukuina sentteinä tai desimaalityypillä, ei liukulukuina.
- **Linkitetty lista ei ole yleiskäyttöinen säiliö.** Funktionaalisissa
  kielissä lista on luonteva, koska sen alku ja loppu voidaan jakaa.
  Indeksointiin ja suuriin datamääriin vektori on nopeampi, ja
  välimuistin kannalta se on lähes aina parempi.
- **Totuusarvosääntöjen erot ovat yleinen virhelähde.** Racketissa vain
  `#f` on epätosi, Pythonissa myös `0`, `""` ja `[]` ja JavaScriptissä
  lisäksi `NaN`, `null` ja `undefined`. Kun "ei arvoa" ja "nolla"
  pitää erottaa, vertaa eksplisiittisesti.
- **Moduulin ylätason lausekkeiden arvot tulostuvat.** Racket tulostaa
  `racket tiedosto.rkt` -ajossa jokaisen ylätason lausekkeen arvon,
  joka ei ole `(void)`. Kääri pelkän sivuvaikutuksen vuoksi kutsuttu
  lauseke `void`-kutsuun tai sido sen arvo nimeen.

## Itsearviointi

- Osaat selittää, miksi `if` on erikoismuoto eikä funktio.
- Osaat rakentaa listan `cons`-kutsuilla ja selittää, miksi etuun
  lisääminen on O(1) ja loppuun lisääminen O(n).
- Osaat valita `eq?`-, `equal?`- ja `=`-vertailun väliltä.
- Osaat käyttää tarkkoja rationaalilukuja ja selittää, miksi rahalaskenta
  ei saa käyttää liukulukuja.
- Osaat kertoa, mitkä arvot ovat Racketissa epätosia, ja käyttää
  `or`-lauseketta oletusarvon antamiseen.
