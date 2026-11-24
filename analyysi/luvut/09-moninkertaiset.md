# Moninkertaiset integraalit

Yhden muuttujan integraali laskee pinta-alan käyrän alla. **Kaksoisintegraali**
laskee tilavuuden pinnan alla tasoalueen yllä, tai yleisemmin kerää
tason yli jakautuneen suureen: levyn massan tiheydestä, kuorman
kokonaisvoiman painejakaumasta tai todennäköisyyden kahden muuttujan
tiheysfunktiosta. Luvussa kaksoisintegraali lasketaan toistettuna
integraalina, integrointijärjestys vaihdetaan, siirrytään
napakoordinaatteihin ja verrataan Monte Carlo -menetelmään.

## Toistettu integraali

Kaksoisintegraali suorakulmion $[a, b] \times [c, d]$ yli lasketaan
**toistettuna integraalina**: ensin sisempi integraali yhden muuttujan
suhteen toinen vakiona pitäen, sitten ulompi.

$$\iint_R f(x, y)\,dA = \int_a^b \left( \int_c^d f(x, y)\,dy \right) dx.$$

Esimerkissä metallilevyn tiheys vaihtelee paikan mukaan, ja levyn massa
on tiheyden integraali levyn yli.

```{.python tiedosto="esimerkit/09-kaksois.py" osa="suorakulmio"}
```

**Fubinin lause** takaa, että jatkuvalla funktiolla järjestys ei vaikuta
tulokseen. Laskun vaikeuteen se voi vaikuttaa paljonkin.

## Integrointijärjestyksen vaihto

Kun alue ei ole suorakulmio, sisemmän integraalin rajat riippuvat
ulommasta muuttujasta. Kolmio $0 \le y \le x \le 1$ voidaan kuvata kahdella
tavalla:

- $x$ välillä $[0, 1]$ ja jokaisella $x$:llä $y$ välillä $[0, x]$, tai
- $y$ välillä $[0, 1]$ ja jokaisella $y$:llä $x$ välillä $[y, 1]$.

Integraali $\iint e^{x^2}\,dA$ kolmion yli on oppikirjaesimerkki
järjestyksen merkityksestä. Jos sisempi integraali otetaan $x$:n
suhteen, se on $\int e^{x^2}\,dx$, jolla ei ole alkeisfunktiona
kirjoitettavaa integraalifunktiota (SymPy vastaa erikoisfunktiolla
$\operatorname{erfi}$). Jos sisempi integraali otetaan $y$:n suhteen,
$e^{x^2}$ on vakio, ja jäljelle jää helppo $\int_0^1 x e^{x^2}\,dx$.

```{.python tiedosto="esimerkit/09-kaksois.py" osa="kolmio"}
```

```{.tuloste tiedosto="esimerkit/09-kaksois.odotettu"}
```

Käsin laskiessa järjestyksen vaihto on usein ainoa tie. Symbolinen
ohjelma selviää molemmista, mutta erikoisfunktioiden kautta kulkeva
tulos on vaikeampi tarkistaa ja tulkita. Rajojen kääntämisessä auttaa
piirtää alue ja lukea siitä uudet rajat.

## Napakoordinaatit

Ympyrän muotoisilla alueilla suorakulmaiset rajat johtavat
juurilausekkeisiin, mutta **napakoordinaateissa** $(r, \theta)$ alue on
suorakulmio. Muuttujanvaihdossa pinta-alkio muuttuu Jacobin
determinantin (luku 8) verran:

$$dA = dx\,dy = r\,dr\,d\theta.$$

Kerroin $r$ on helppo unohtaa, ja ilman sitä ympyrän alaksi tulisi
$2\pi R$ eli kehän pituus. Kerroin kertoo, että kauempana origosta
kulman muutos $d\theta$ vastaa pidempää kaarta.

```{.python tiedosto="esimerkit/09-napa.py" osa="ala"}
```

Napakoordinaattien kuuluisin sovellus on **Gaussin integraali**
$I = \int_{-\infty}^\infty e^{-x^2}\,dx$, jolle ei ole alkeisfunktiota.
Sen neliö on tason integraali
$I^2 = \iint e^{-(x^2 + y^2)}\,dA$, ja napakoordinaateissa kerroin $r$
tekee integroitavasta $r e^{-r^2}$, joka integroituu suoraan. Tulos
$I = \sqrt\pi$ on normaalijakauman normitusvakion lähde.

```{.python tiedosto="esimerkit/09-napa.py" osa="gauss"}
```

```{.tuloste tiedosto="esimerkit/09-napa.odotettu"}
```

Kolmessa ulottuvuudessa vastaavat muunnokset ovat
**lieriökoordinaatit** ($dV = r\,dr\,d\theta\,dz$) ja
**pallokoordinaatit** ($dV = \rho^2 \sin\varphi\,d\rho\,d\theta\,d\varphi$).
Molemmat kertoimet ovat Jacobin determinantteja.

## Monte Carlo -integrointi

Kun ulottuvuuksia on paljon, toistetut integraalit käyvät
mahdottomiksi: jos jokaisessa ulottuvuudessa käytetään sataa pistettä,
kymmenulotteinen integraali vaatii $100^{10}$ funktion arvoa. **Monte
Carlo -integrointi** arvioi integraalin satunnaisten pisteiden
keskiarvona:

$$\int_\Omega f\,dV \approx |\Omega| \cdot \frac1N \sum_{i=1}^N f(\mathbf p_i).$$

Arvion keskivirhe pienenee kuten $1/\sqrt N$ ulottuvuuksien määrästä
riippumatta. Se on hidas tahti (sata kertaa enemmän pisteitä antaa
kymmenen kertaa tarkemman tuloksen) mutta voittaa suurissa
ulottuvuuksissa kaiken muun. Klassinen esimerkki arvioi luvun $\pi$:
neliön satunnaisista pisteistä yksikköympyrän sisään osuu osuus $\pi/4$.

```{.python tiedosto="esimerkit/09-montecarlo.py" osa="pii"}
```

Kahdessa ulottuvuudessa SciPyn `dblquad` on paljon tarkempi kuin
Monte Carlo samalla työllä. Vertailu näyttää, miksi Monte Carloa
käytetään vasta, kun ulottuvuuksia on paljon tai alue on
monimutkainen.

```{.python tiedosto="esimerkit/09-montecarlo.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/09-montecarlo.odotettu"}
```

Satunnaisluvut tuotetaan kiinteällä siemenellä, jotta ajo on
toistettava ja testattavissa. Monte Carlo -menetelmien tilastollinen
tausta (odotusarvo, varianssi ja keskeinen raja-arvolause) käsitellään
taidossa *Todennäköisyys ja tilastot*, ja sovellus valon kulun
laskentaan taidossa *Säteenseuranta ja fysikaalinen valaistus*.

## Samat laskut Maximalla

Maximassa toistettu integraali kirjoitetaan sisäkkäisinä
`integrate`-kutsuina. Oletus `assume(R > 0)` kertoo, että säde on
positiivinen; ilman sitä eräajo pysähtyisi Maximan kysymykseen.

```{.maxima tiedosto="esimerkit/maxima/09-moninkertaiset.mac" osa="moninkertaiset"}
```

```{.tuloste tiedosto="esimerkit/maxima/09-moninkertaiset.odotettu"}
```

## Käytännössä

- **Piirrä alue ennen rajoja.** Integrointirajat luetaan kuvasta.
  Väärät rajat ovat moninkertaisten integraalien yleisin virhe.
- **Valitse järjestys ja koordinaatit helpoimman sisemmän integraalin
  mukaan.** Jos sisempi integraali ei ratkea, vaihda järjestystä tai
  koordinaatistoa.
- **Muista Jacobin kerroin.** Napakoordinaateissa $r$, pallokoordinaateissa
  $\rho^2\sin\varphi$.
- **Monte Carlo suurille ulottuvuuksille.** Muutamassa ulottuvuudessa
  käytä kvadratuuria (`dblquad`, `tplquad`). Kun ulottuvuuksia on paljon
  tai alue on hankala, Monte Carlo on usein ainoa käytännöllinen
  vaihtoehto. Kiinnitä siemen ja raportoi keskivirhe.

## Itsearviointi

- Osaat laskea kaksoisintegraalin toistettuna integraalina sekä
  SymPyllä ja Maximalla.
- Osaat kuvata alueen kahdessa integrointijärjestyksessä ja valita
  järjestyksen, jossa sisempi integraali ratkeaa.
- Osaat vaihtaa napakoordinaatteihin ja perustella Jacobin kertoimen $r$.
- Osaat laskea Monte Carlo -arvion ja kertoa, miten sen virhe riippuu
  pisteiden määrästä.
