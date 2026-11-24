# Vektorit ja analyyttinen geometria

Analyyttinen geometria kuvaa pisteet, suorat ja ympyrät yhtälöinä, jolloin
geometriset kysymykset muuttuvat laskuiksi: leikkaavatko suorat, kuinka
kaukana piste on suorasta, osuuko pallo esteeseen. Tämä on
tietokonegrafiikan, pelien ja robotiikan arkipäivää. Luvussa käsitellään
tason vektorit, suorat ja ympyrät, ja sovelluksena lasketaan liikkuvan
pallon törmäyshetki. Vektorit ja matriisit yleisessä muodossa ovat
taidon *Lineaarialgebra* aihe.

## Vektorit

**Vektorilla** on suuruus ja suunta. Tasossa se kirjoitetaan
koordinaatteina $\mathbf a = (a_1, a_2)$. Vektoreita lasketaan yhteen
koordinaateittain ja kerrotaan luvulla koordinaateittain. Vektorin
**pituus** on Pythagoraan lauseesta $|\mathbf a| = \sqrt{a_1^2 + a_2^2}$.

**Pistetulo** $\mathbf a \cdot \mathbf b = a_1 b_1 + a_2 b_2$ on luku,
joka kertoo vektorien suuntien yhteneväisyydestä:

$$\mathbf a \cdot \mathbf b = |\mathbf a|\,|\mathbf b| \cos\theta,$$

jossa $\theta$ on vektorien välinen kulma. Pistetulo on nolla täsmälleen
silloin, kun vektorit ovat **kohtisuorassa**. SymPyn `Matrix` laskee
tarkasti, joten pituudet ja kulmat ovat tarkkoja lausekkeita.

```{.python tiedosto="esimerkit/07-vektorit.py" osa="tarkasti"}
```

**Projektio** jakaa vektorin kahteen osaan: toisen vektorin suuntaiseen
ja sitä vastaan kohtisuoraan. Vektorin $\mathbf a$ projektio vektorille
$\mathbf b$ on
$\frac{\mathbf a \cdot \mathbf b}{\mathbf b \cdot \mathbf b}\,\mathbf b$.
Peleissä projektiolla lasketaan esimerkiksi seinän suuntainen liuku:
nopeudesta poistetaan seinää vastaan kohtisuora osa.

```{.python tiedosto="esimerkit/07-vektorit.py" osa="projektio"}
```

NumPylla samat laskut tehdään liukuluvuilla. Kun kulma lasketaan
kosinista, pyöristysvirhe voi viedä kosinin hieman yli yhden, jolloin
`arccos` palauttaa NaN-arvon. Tavallinen suojaus on rajata arvo välille
$[-1, 1]$ funktiolla `np.clip`. Virhe ei ole teoreettinen: se kaataa
fysiikkamoottoreita ja kulmamittauksia, kun vektorit ovat lähes
yhdensuuntaiset.

```{.python tiedosto="esimerkit/07-vektorit.py" osa="numpy"}
```

```{.tuloste tiedosto="esimerkit/07-vektorit.odotettu"}
```

## Suorat

Suoran voi kirjoittaa kolmella tavalla, ja kukin sopii eri tehtävään:

| Muoto | Yhtälö | Käyttö |
|-------|--------|--------|
| Ratkaistu | $y = kx + b$ | Kuvaajat; ei pystysuoria suoria |
| Normaalimuoto | $ax + by + c = 0$ | Etäisyys pisteestä; kaikki suorat |
| Parametrimuoto | $\mathbf p = \mathbf p_0 + t\,\mathbf v$ | Liike, säteet, janat ($0 \le t \le 1$) |

Normaalimuodon kertoimet $(a, b)$ ovat suoraa vastaan kohtisuora
**normaalivektori**. Se saadaan suuntavektorista $(v_1, v_2)$ vaihtamalla
koordinaatit ja toisen merkki: $(-v_2, v_1)$.

```{.python tiedosto="esimerkit/07-suorat.py" osa="suora"}
```

Kahden suoran leikkauspiste on niiden yhtälöparin ratkaisu (luku 3).
Suorat ovat kohtisuorassa, kun niiden kulmakertoimien tulo on $-1$.

```{.python tiedosto="esimerkit/07-suorat.py" osa="leikkaus"}
```

Pisteen $(p_x, p_y)$ **etäisyys** suorasta $ax + by + c = 0$ on

$$d = \frac{|a p_x + b p_y + c|}{\sqrt{a^2 + b^2}}.$$

Kaavan osoittaja on pisteen sijoitus suoran yhtälöön, ja nimittäjä
normittaa normaalivektorin pituuden ykköseksi. Osoittajan etumerkki
kertoo, kummalla puolella suoraa piste on, mitä käytetään esimerkiksi
monikulmion sisäpisteiden testaamiseen.

```{.python tiedosto="esimerkit/07-suorat.py" osa="etaisyys"}
```

```{.tuloste tiedosto="esimerkit/07-suorat.odotettu"}
```

## Ympyrä

Ympyrän, jonka keskipiste on $(x_0, y_0)$ ja säde $r$, yhtälö on
$(x - x_0)^2 + (y - y_0)^2 = r^2$. Laajennetusta muodosta keskipiste ja
säde löydetään **täydentämällä neliöiksi**: esimerkiksi
$x^2 - 4x = (x - 2)^2 - 4$. Tarkistus on helppo: laajennetaan neliömuoto ja
verrataan.

```{.python tiedosto="esimerkit/07-ympyra.py" osa="nelio"}
```

Suora ja ympyrä voivat leikata kahdessa pisteessä, sivuta yhdessä tai
ohittaa toisensa. Kun suoran yhtälö sijoitetaan ympyrän yhtälöön,
saadaan toisen asteen yhtälö, jonka diskriminantti (luku 3) ratkaisee
tapauksen. Symbolin oletus `real=True` pitää huolen siitä, että
kompleksiset ratkaisut eivät tule mukaan.

```{.python tiedosto="esimerkit/07-ympyra.py" osa="leikkaus"}
```

Ympyrän **tangentti** on kohtisuorassa sivuamispisteeseen piirrettyyn
säteeseen nähden. Säde on siis tangentin normaalivektori, ja tangentin
normaalimuoto saadaan suoraan.

```{.python tiedosto="esimerkit/07-ympyra.py" osa="tangentti"}
```

```{.tuloste tiedosto="esimerkit/07-ympyra.odotettu"}
```

![Ympyrä $x^2 + y^2 = 25$, leikkaava, sivuava ja ohittava suora sekä
tangentti pisteessä $(3, 4)$.](kuvat/geometria.png){width=55%}

## Samat laskut Maximalla

Maximan listoja voi laskea yhteen ja kertoa pisteellä kuten vektoreita:
`a . b` on pistetulo. Leikkauspisteet ratkaistaan samalla `solve`-
funktiolla kuin muutkin yhtälöryhmät.

```{.maxima tiedosto="esimerkit/maxima/07-geometria.mac" osa="vektorit"}
```

```{.maxima tiedosto="esimerkit/maxima/07-geometria.mac" osa="leikkaukset"}
```

```{.tuloste tiedosto="esimerkit/maxima/07-geometria.odotettu"}
```

## Sovellus: törmäyksen tunnistus

Pelissä pallo liikkuu tasaisella nopeudella, ja sen keskipiste on hetkellä
$t$ pisteessä $\mathbf p(t) = \mathbf p_0 + t\,\mathbf v$. Pallo osuu
pyöreään tolppaan, kun keskipisteiden etäisyys on säteiden summa $r$:
$|\mathbf p_0 + t\mathbf v - \mathbf c| = r$. Kun molemmat puolet
korotetaan toiseen ja merkitään $\mathbf d = \mathbf p_0 - \mathbf c$,
pistetulon laskusäännöillä saadaan toisen asteen yhtälö

$$(\mathbf v \cdot \mathbf v)\, t^2 + 2(\mathbf d \cdot \mathbf v)\, t
  + \mathbf d \cdot \mathbf d - r^2 = 0.$$

Ensimmäinen kosketus on pienempi juuri. Jos diskriminantti on negatiivinen,
pallo ohittaa tolpan, ja jos molemmat juuret ovat negatiivisia, tolppa
on jo takana.

```{.python tiedosto="esimerkit/07-tormays.py" osa="tormays"}
```

```{.python tiedosto="esimerkit/07-tormays.py" osa="kaytto"}
```

Analyyttisen ratkaisun etu näkyy nopeilla kappaleilla. Yksinkertainen
peli tarkistaa törmäyksen vain jokaisessa kuvaruudussa. Jos pallo liikkuu
yhden ruudun aikana enemmän kuin tolpan läpimitan verran, se voi hypätä
tolpan yli: ilmiön nimi on **tunneloituminen**. Se on sama
näytteistysongelma kuin luvun 4 kuvaajassa. Analyyttinen törmäyshetki
löytää osuman ruutujen välistäkin.

```{.python tiedosto="esimerkit/07-tormays.py" osa="tunnelointi"}
```

```{.tuloste tiedosto="esimerkit/07-tormays.odotettu"}
```

Tätä jatkuvaa törmäyksen tunnistusta (engl. *continuous collision
detection*) käytetään fysiikkamoottoreissa nopeille kappaleille, kuten
luodeille (taito *Peliohjelmointi*).

## Käytännössä

- **Valitse suoran muoto tehtävän mukaan.** Normaalimuoto etäisyyksiin,
  parametrimuoto liikkeeseen ja säteisiin, ratkaistu muoto kuvaajiin.
- **Vertaa neliöityjä etäisyyksiä.** Törmäystarkistus
  $|\mathbf d|^2 \le r^2$ ei tarvitse neliöjuurta, mikä on nopeampaa ja
  välttää pyöristystä.
- **Rajaa kosini ennen `arccos`-kutsua.** `np.clip(c, -1, 1)` estää
  NaN-arvon lähes yhdensuuntaisilla vektoreilla.
- **Tarkista tapaukset diskriminantilla.** Leikkaus, sivuaminen ja
  ohitus ovat saman yhtälön kolme tapausta, ja koodin on käsiteltävä
  kaikki.
- **Analyyttinen törmäyshetki nopeille kappaleille.** Ruutukohtainen
  tarkistus päästää nopeat kappaleet esteiden läpi.

## Itsearviointi

- Osaat laskea vektorien summan, pituuden, pistetulon, välisen kulman ja
  projektion.
- Osaat kirjoittaa suoran ratkaistussa, normaali- ja parametrimuodossa
  sekä laskea pisteen etäisyyden suorasta.
- Osaat määrittää ympyrän keskipisteen ja säteen neliöksi täydentämällä
  sekä ratkaista suoran ja ympyrän leikkauspisteet.
- Osaat muotoilla liikkuvan kappaleen törmäyksen toisen asteen
  yhtälöksi ja selittää tunneloitumisen.
