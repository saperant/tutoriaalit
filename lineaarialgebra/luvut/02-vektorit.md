# Vektorit

Vektori on järjestetty lukujono. Geometrisesti se on nuoli: tason
vektori $(3, 4)$ osoittaa kolme yksikköä oikealle ja neljä ylös.
Sama vektori voi kuvata paikkaa (pistettä suhteessa origoon),
siirtymää, nopeutta, voimaa, väriä tai ostoskoria. Laskusäännöt ovat
kaikille samat. Tämä luku esittelee ne ja niiden geometrisen
merkityksen; kaikki myöhemmät luvut rakentuvat näiden operaatioiden
varaan.

## Summa ja skalaarilla kertominen

Vektorit lasketaan yhteen alkioittain, ja skalaarilla (luvulla)
kertominen kertoo jokaisen alkion. Geometrisesti summa on nuolten
asettaminen peräkkäin ja skalaarilla kertominen nuolen venyttäminen tai
kääntäminen vastakkaiseksi.

$$u + v = (u_1 + v_1, \dots, u_n + v_n), \qquad
  k u = (k u_1, \dots, k u_n)$$

```{.python tiedosto="esimerkit/02-vektorit.py" osa="perus"}
```

```{.tuloste tiedosto="esimerkit/02-vektorit.odotettu" rivit="1-2"}
```

![Vasemmalla vektorien summa: nuolet asetetaan peräkkäin, ja
järjestyksellä ei ole väliä (pisteviiva). Oikealla projektio, johon
palataan tämän luvun osiossa *Projektio*: painovoima jaetaan rinteen
suuntaiseen ja sitä vastaan kohtisuoraan
osaan.](kuvat/vektorit.png){width=92%}

Nämä kaksi operaatiota tekevät joukosta vektoriavaruuden: jokainen
**lineaarikombinaatio** $a u + b v$ on taas vektori. Lineaarialgebra on
lineaarikombinaatioiden tutkimista.

## Pituus ja normit

Vektorin pituus eli euklidinen normi on Pythagoraan lauseesta
$\lVert v \rVert_2 = \sqrt{v_1^2 + \dots + v_n^2}$. Muitakin pituuden
mittoja käytetään:

- $\lVert v \rVert_1 = \sum |v_i|$ on korttelimatka: liike
  ruudukossa vain akselien suuntaan.
- $\lVert v \rVert_\infty = \max |v_i|$ on suurin yksittäinen
  poikkeama, esimerkiksi suurin mittausvirhe.

Vektori jaettuna pituudellaan on **yksikkövektori**, jonka pituus on 1.
Se kuvaa pelkkää suuntaa.

```{.python tiedosto="esimerkit/02-vektorit.py" osa="normit"}
```

```{.tuloste tiedosto="esimerkit/02-vektorit.odotettu" rivit="3-6"}
```

```{.python tiedosto="esimerkit/02-vektorit.py" osa="numpy"}
```

```{.tuloste tiedosto="esimerkit/02-vektorit.odotettu" rivit="7-"}
```

Kahden pisteen etäisyys on niiden erotuksen normi
$\lVert p - q \rVert$. Normin valinta riippuu tehtävästä: robotin
liikkeen energiaa mittaa usein L2-normi, varaston keräilyreittiä L1 ja
toleranssin ylitystä L∞.

## Pistetulo ja kulma

Pistetulo $u \cdot v = \sum u_i v_i$ yhdistää algebran ja geometrian:

$$u \cdot v = \lVert u \rVert \, \lVert v \rVert \cos \theta,$$

missä $\theta$ on vektorien välinen kulma. Pistetulo on positiivinen,
kun vektorit osoittavat samaan suuntaan, nolla, kun ne ovat
**kohtisuorassa** (ortogonaaliset), ja negatiivinen, kun ne osoittavat
vastakkain.

```{.python tiedosto="esimerkit/02-pistetulo.py" osa="kulma"}
```

```{.tuloste tiedosto="esimerkit/02-pistetulo.odotettu" rivit="1-3"}
```

Kosinin argumentti rajataan välille $[-1, 1]$, koska pyöristysvirhe voi
tuottaa arvon 1,0000000000000002, ja `acos` kaatuu siihen. Tämä on
tyypillinen numeerinen yksityiskohta: matemaattisesti mahdoton arvo on
liukuluvuilla mahdollinen.

## Projektio

Vektorin $v$ **projektio** suunnalle $u$ on se osa $v$:stä, joka
osoittaa $u$:n suuntaan:

$$\operatorname{proj}_u v = \frac{v \cdot u}{u \cdot u} \, u.$$

Jäljelle jäävä osa $v - \operatorname{proj}_u v$ on kohtisuorassa
$u$:ta vastaan. Fysiikassa näin jaetaan voima rinteen suuntaiseen ja
rinnettä vastaan kohtisuoraan osaan:

```{.python tiedosto="esimerkit/02-pistetulo.py" osa="projektio"}
```

```{.tuloste tiedosto="esimerkit/02-pistetulo.odotettu" rivit="4-"}
```

Edellä olevan kuvan oikea puoli näyttää jaon: projektio ja kohtisuora
osa ovat suorakulmaisen kolmion kateetit ja alkuperäinen voima sen
hypotenuusa.

Projektio on koko tutoriaalin toistuva idea. Pienimmän neliösumman
sovitus (luku *Pienimmän neliösumman sovitus*) on projektio,
Gram–Schmidt-menetelmä (luku *Ortogonaalisuus*) poistaa
projektioita, ja varjo grafiikassa on projektio tasolle.

## Ristitulo ja normaali

Kolmiulotteisessa avaruudessa kahden vektorin **ristitulo** $a \times b$
on vektori, joka on kohtisuorassa molempia vastaan. Sen pituus on
vektorien virittämän suunnikkaan pinta-ala, ja suunta noudattaa oikean
käden sääntöä: kun sormet kiertyvät $a$:sta $b$:hen, peukalo osoittaa
ristitulon suuntaan.

$$a \times b = (a_2 b_3 - a_3 b_2,\; a_3 b_1 - a_1 b_3,\; a_1 b_2 - a_2 b_1)$$

Grafiikassa ristitulo antaa kolmion **normaalin**, pinnan
ulospäin osoittavan suunnan. Kärkien järjestys ratkaisee, kumpaan
suuntaan normaali osoittaa, ja juuri siihen perustuu takapintojen
karsinta (*back-face culling*): kameraan päin osoittamattomia kolmioita
ei piirretä.

```{.python tiedosto="esimerkit/02-ristitulo.py" osa="risti"}
```

```{.python tiedosto="esimerkit/02-ristitulo.py" osa="karsinta"}
```

```{.tuloste tiedosto="esimerkit/02-ristitulo.odotettu"}
```

Ristitulo on määritelty vain kolmessa ulottuvuudessa. Tasossa sen
vastine on luku $a_1 b_2 - a_2 b_1$, joka kertoo, kääntyykö $b$
vastapäivään ($> 0$) vai myötäpäivään ($< 0$) $a$:sta. Sitä käytetään
esimerkiksi tarkistamaan, kummalla puolella suoraa piste on.

## Käytännössä

- **Normalisoi suunnat vain kerran.** Yksikkövektori säästää
  jakolaskuja kulmien ja projektioiden kaavoissa, mutta nollavektoria
  ei voi normalisoida. Tarkista pituus ennen jakoa, tai suunnittele data
  niin, että nollan pituinen suunta on mahdoton.
- **Vertaa neliöityjä pituuksia.** Kun tarvitaan vain tieto, kumpi
  piste on lähempänä, vertaa $\lVert v \rVert^2 = v \cdot v$:tä ja
  säästä neliöjuuri. Pelien törmäystarkistukset tekevät näin.
- **Rajaa käänteisfunktioiden argumentit.** `acos` ja `asin`
  kaatuvat pyöristysvirheestä. Rajaa argumentti tai käytä
  `atan2`:ta, joka on tarkempi myös pienillä kulmilla.
- **Pidä kärkien kiertosuunta johdonmukaisena.** Mallin kaikki
  kolmiot vastapäivään (tai kaikki myötäpäivään); muuten normaalit ja
  takapintojen karsinta toimivat satunnaisesti.
- **Älä tee vektoriluokkaa NumPyn päälle.** Pienissä ohjelmissa oma
  vektoriluokka on selkeä, mutta NumPyn taulukot ovat nopeampia, ja
  niiden operaatiot (`@`, `np.cross`, `np.linalg.norm`) ovat valmiina.

## Itsearviointi

- Osaat laskea vektorien summan, skalaarimonikerran, pituuden ja
  yksikkövektorin sekä selittää ne geometrisesti.
- Osaat valita tehtävään sopivan normin (L1, L2 tai L∞).
- Osaat laskea kahden vektorin välisen kulman ja tunnistaa
  kohtisuorat vektorit pistetulosta.
- Osaat jakaa vektorin annetun suunnan suuntaiseen ja sitä vastaan
  kohtisuoraan osaan.
- Osaat laskea kolmion normaalin ja pinta-alan ristitulolla ja
  päätellä, onko kolmio kameraan päin.
