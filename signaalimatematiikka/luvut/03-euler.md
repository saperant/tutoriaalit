# Eulerin kaava ja kompleksinen eksponentti

Edellisessä luvussa napaesitys $r(\cos\varphi + i\sin\varphi)$
kirjoitettiin lyhyesti muodossa $re^{i\varphi}$. Merkintä ei ole
pelkkä sopimus, vaan se on **Eulerin kaava**

$$e^{i\varphi} = \cos\varphi + i \sin\varphi.$$

Kaava yhdistää eksponenttifunktion ja trigonometriset funktiot. Se on
signaalimatematiikan tärkein yksittäinen kaava, koska sen avulla
sinimuotoisia signaaleja voi käsitellä eksponenttifunktioina, joiden
laskusäännöt ovat paljon yksinkertaisempia kuin trigonometrian
kaavaston. Tässä luvussa kaava johdetaan kahdella tavalla ja
tarkistetaan numeerisesti, ja sen avulla johdetaan trigonometrian
kaavoja ja ykkösen juuret, joita DFT tarvitsee luvussa 9.

## Johto sarjasta

Eksponenttifunktio voidaan määritellä potenssisarjana

$$e^z = \sum_{k=0}^{\infty} \frac{z^k}{k!} = 1 + z + \frac{z^2}{2!} + \frac{z^3}{3!} + \cdots$$

Sarja suppenee jokaisella kompleksiluvulla $z$, koska kertoma $k!$
kasvaa lopulta nopeammin kuin mikään potenssi $|z|^k$. Sijoitetaan
$z = i\varphi$ ja käytetään potensseja $i^0 = 1$, $i^1 = i$, $i^2 = -1$,
$i^3 = -i$, $i^4 = 1$, jotka toistuvat neljän jaksoissa. Parilliset
termit ovat reaalisia ja parittomat imaginaarisia:

$$e^{i\varphi} = \Big(1 - \frac{\varphi^2}{2!} + \frac{\varphi^4}{4!} - \cdots\Big)
+ i\Big(\varphi - \frac{\varphi^3}{3!} + \frac{\varphi^5}{5!} - \cdots\Big).$$

Sulkeissa ovat täsmälleen kosinin ja sinin Taylorin sarjat, joten
$e^{i\varphi} = \cos\varphi + i\sin\varphi$.

Seuraava ohjelma laskee sarjan osasummia ja vertaa niitä lukuun
$\cos 2 + i\sin 2$. Jokainen termi lasketaan edellisestä kertomalla
luvulla $z/(k+1)$, jolloin suuria kertomia ja potensseja ei tarvita
erikseen.

```{.python tiedosto="esimerkit/03-sarja.py" osa="sarja"}
```

Virhe pienenee ensin hitaasti ja sitten erittäin nopeasti: kun termejä
on 20, virhe on enää $10^{-13}$:n luokkaa. Näin nopea suppeneminen on
tyypillistä sarjoille, joiden kertoimissa on kertoma.

## Johto differentiaaliyhtälöstä

Toinen tapa nähdä kaava on kysyä, mikä funktio $z(t)$ toteuttaa
yhtälön $z'(t) = iz(t)$ alkuarvolla $z(0) = 1$. Reaalisella kertoimella
$a$ yhtälön $z' = az$ ratkaisu on $e^{at}$, joten luonteva arvaus on
$z(t) = e^{it}$. Geometrisesti yhtälö sanoo, että nopeus $z'$ on aina
paikka $z$ kierrettynä 90 astetta. Nopeus on siis kohtisuorassa
paikkavektoriin nähden, joten piste ei lähesty eikä loittone origosta:
se kiertää yksikköympyrää vakionopeudella yksi radiaani aikayksikössä.
Ajan $t$ kuluttua piste on kulmassa $t$, eli kohdassa
$\cos t + i \sin t$.

Saman voi laskea numeerisesti. Eulerin menetelmä etenee askelin
$z_{k+1} = z_k + h \cdot iz_k = (1 + ih)z_k$, joten $n$ askeleen
jälkeen ajassa $t = nh$ ollaan pisteessä $(1 + it/n)^n$. Kun
$n \to \infty$, tämä lähestyy lukua $e^{it}$, aivan kuten reaalinen
$(1 + x/n)^n$ lähestyy lukua $e^x$.

```{.python tiedosto="esimerkit/03-sarja.py" osa="raja"}
```

```{.tuloste tiedosto="esimerkit/03-sarja.odotettu"}
```

Kulma tarkentuu nopeasti, mutta itseisarvo on aina hieman yli yhden:
jokainen askel kulkee ympyrän tangentin suuntaan ja ajautuu siksi
ulospäin, koska $|1 + ih| = \sqrt{1 + h^2} > 1$. Virhe on verrannollinen
askeleen pituuteen, mikä on Eulerin menetelmän tunnettu ominaisuus.
Tulos on silti selvä: yhtälön $z' = iz$ ratkaisu kiertää yksikköympyrää,
ja se on $e^{it}$.

## Tarkistus ja Eulerin identiteetti

NumPyn `numpy.exp` laskee kompleksisen eksponentin suoraan. Seuraava
ohjelma vertaa sitä kosinin ja sinin yhdistelmään 2001 pisteessä
väliltä $[-10, 10]$. Samalla tarkistetaan Eulerin kaavan käänteiset
muodot

$$\cos\varphi = \frac{e^{i\varphi} + e^{-i\varphi}}{2}, \qquad
\sin\varphi = \frac{e^{i\varphi} - e^{-i\varphi}}{2i},$$

jotka saadaan laskemalla kaava $e^{i\varphi} = \cos\varphi + i\sin\varphi$
ja sen liittoluku $e^{-i\varphi} = \cos\varphi - i\sin\varphi$ yhteen
tai vähentämällä ne toisistaan. Nämä muodot ovat Fourier-analyysin
perusta: kosini on kahden vastakkaisiin suuntiin pyörivän nuolen
keskiarvo.

```{.python tiedosto="esimerkit/03-euler.py" osa="tarkistus"}
```

Sijoittamalla $\varphi = \pi$ saadaan **Eulerin identiteetti**
$e^{i\pi} + 1 = 0$. Liukuluvuilla tulos ei ole tasan nolla, vaan
imaginaariosaksi jää noin $1.2 \cdot 10^{-16}$. Syy ei ole
eksponenttifunktiossa vaan siinä, että `math.pi` ei ole tasan $\pi$:
`math.sin(math.pi)` on tarkasti laskettu sini luvusta, joka on hieman
pienempi kuin $\pi$, ja tulos on likimain $\pi$:n ja sen
liukulukulikiarvon erotus. Tällaiset jäännökset ovat
syy siihen, että tuloksia verrataan aina toleranssilla eikä
yhtäsuuruudella.

## Trigonometria ilman kaavastoa

Koska $e^{i\alpha}e^{i\beta} = e^{i(\alpha + \beta)}$, kulmien
summakaavat saadaan kertomalla:

$$\cos(\alpha + \beta) + i\sin(\alpha + \beta)
= (\cos\alpha + i\sin\alpha)(\cos\beta + i\sin\beta),$$

ja vertaamalla reaali- ja imaginaariosia saadaan
$\cos(\alpha + \beta) = \cos\alpha\cos\beta - \sin\alpha\sin\beta$ ja
$\sin(\alpha + \beta) = \sin\alpha\cos\beta + \cos\alpha\sin\beta$.
Samalla tavalla **de Moivren kaava**
$(\cos x + i\sin x)^n = \cos nx + i\sin nx$ on vain
$(e^{ix})^n = e^{inx}$. Tulo- ja potenssikaavat saadaan käänteisistä
muodoista. Esimerkiksi

$$\cos^2 x = \Big(\frac{e^{ix} + e^{-ix}}{2}\Big)^2
= \frac{e^{2ix} + 2 + e^{-2ix}}{4} = \frac{1 + \cos 2x}{2}.$$

Signaalin kannalta kaava sanoo, että kosinin neliöön syntyy
tasakomponentti ja kaksinkertainen taajuus. Tämä on syy siihen, että
epälineaarinen vahvistin tuottaa yliaaltoja ja että sinimuotoisen
virran teho sykkii kaksinkertaisella taajuudella.

```{.python tiedosto="esimerkit/03-euler.py" osa="identiteetit"}
```

```{.tuloste tiedosto="esimerkit/03-euler.odotettu"}
```

## Ykkösen juuret

Yhtälöllä $w^N = 1$ on kompleksiluvuissa täsmälleen $N$ ratkaisua,
**ykkösen $N$:nnet juuret**

$$w_k = e^{2\pi i k/N}, \qquad k = 0, 1, \ldots, N - 1.$$

Ne ovat yksikköympyrällä tasavälein, säännöllisen $N$-kulmion
kärkipisteinä. Juuri $w = w_1 = e^{2\pi i/N}$ on **primitiivinen**:
sen potenssit $w^0, w^1, \ldots, w^{N-1}$ käyvät läpi kaikki juuret.
Juurien tärkein ominaisuus on, että niiden summa on nolla:

$$\sum_{k=0}^{N-1} w^{km} = \begin{cases} N, & \text{kun } m \text{ on } N\text{:n monikerta},\\ 0, & \text{muuten.}\end{cases}$$

Geometrisesti tasavälein ympyrälle sijoitetut nuolet kumoavat
toisensa, koska niiden summa ei muutu, kun koko kuvio kierretään
kulman $2\pi m/N$ verran. Ainoa luku, joka ei muutu nollasta
poikkeavalla kierrolla, on nolla. Kun $m$ on $N$:n monikerta, kaikki
termit ovat ykkösiä ja summa on $N$.

```{.python tiedosto="esimerkit/03-juuret.py" osa="juuret"}
```

```{.tuloste tiedosto="esimerkit/03-juuret.odotettu"}
```

Tämä summa on luvun 5 ortogonaalisuusrelaatioiden diskreetti versio ja
luvun 9 DFT-matriisin ortogonaalisuuden syy. Tietoliikennetekniikassa
sama ilmiö näkyy OFDM:ssä: alikantoaallot on valittu niin, että niiden
taajuuserot ovat symbolin keston käänteisluvun monikertoja, jolloin
niiden tulojen summa symbolin yli on nolla, eivätkä ne häiritse
toisiaan.

## Käytännössä

- **Korvaa trigonometria eksponenteilla.** Kun lauseke sisältää sinien
  ja kosinien tuloja tai potensseja, kirjoita ne muodossa
  $(e^{ix} \pm e^{-ix})/2$; lasku on lähes aina lyhyempi.
- **Käytä `numpy.exp(1j * x)` kosinin ja sinin parin sijaan.**
  Kompleksinen eksponentti on yksi taulukko ja yksi kertolasku vaihetta
  kohti.
- **Odota pyöristysjäännöksiä.** `e^(i pi) + 1` ei ole tasan nolla, eikä
  ykkösen juurten summa ole tasan nolla; vertaa toleranssilla.
- **Tunnista ykkösen juurten summat.** Summa $\sum_k e^{2\pi ikm/N}$
  on joko $N$ tai nolla, ja se esiintyy jokaisessa DFT:tä koskevassa
  laskussa.

## Itsearviointi

- Osaat johtaa Eulerin kaavan eksponenttifunktion sarjasta ja selittää,
  miksi yhtälön $z' = iz$ ratkaisu kiertää yksikköympyrää.
- Osaat kirjoittaa kosinin ja sinin kompleksisten eksponenttien avulla
  ja johtaa niillä summakaavan tai kaavan $\cos^2 x = (1 + \cos 2x)/2$.
- Osaat laskea ykkösen $N$:nnet juuret NumPylla ja perustella, miksi
  niiden summa on nolla.
- Osaat selittää, miksi `cmath.exp(1j * math.pi) + 1` ei ole tasan nolla.
