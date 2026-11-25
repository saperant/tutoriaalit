# Fourier-sarja

Jaksollinen signaali toistaa samaa muotoa jakson $T$ välein. Fourier'n
havainto oli, että tällainen signaali voidaan kirjoittaa sinimuotoisten
aaltojen summana, joiden taajuudet ovat perustaajuuden $1/T$
monikertoja. Monikertoja kutsutaan **harmonisiksi**: ensimmäinen
harmoninen on perustaajuus, toinen sen kaksinkertainen ja niin
edelleen. Viulun ja huilun sama sävel kuulostaa erilaiselta, koska
harmonisten voimakkuudet ovat erilaiset, ja verkkojännitteen
säröytyminen mitataan sen harmonisista.

Tässä luvussa jakso on $2\pi$, jolloin kaavat ovat lyhyimmillään.
Jakson $T$ signaali saadaan sijoittamalla $t \mapsto 2\pi t/T$, jolloin
taajuudet ovat $k/T$ hertsiä.

## Kertoimet ortogonaalisuudesta

**Fourier-sarja** esittää jaksollisen signaalin muodossa

$$x(t) = \sum_{k=-\infty}^{\infty} c_k e^{ikt}, \qquad
c_k = \frac{1}{2\pi}\int_0^{2\pi} x(t)e^{-ikt}\,dt.$$

Kerroinkaava seuraa luvun 5 ortogonaalisuudesta. Kun sarjan molemmat
puolet kerrotaan funktiolla $e^{-imt}$ ja otetaan keskiarvo jakson yli,
jokainen termi $k \ne m$ häviää, ja jäljelle jää $c_m$. Kerroin on siis
sisätulo $c_k = \langle x, e_k\rangle$, eli signaalin koordinaatti
kantafunktion $e^{ikt}$ suhteen. Tämä on sama korrelaatiomittaus kuin
luvussa 4, nyt jokaiselle harmoniselle erikseen.

Reaalisessa muodossa sarja kirjoitetaan kosinien ja sinien avulla:

$$x(t) = \frac{a_0}{2} + \sum_{k=1}^{\infty}\big(a_k\cos kt + b_k \sin kt\big),
\qquad a_k = \frac1\pi\int_0^{2\pi} x(t)\cos kt\,dt, \quad
b_k = \frac1\pi\int_0^{2\pi} x(t)\sin kt\,dt.$$

Muodot ovat saman asian kaksi esitystä. Eulerin kaavasta saadaan
$a_k = c_k + c_{-k}$ ja $b_k = i(c_k - c_{-k})$. Reaaliselle signaalille
$c_{-k} = \bar c_k$, joten $a_k = 2\operatorname{Re} c_k$ ja
$b_k = -2\operatorname{Im} c_k$. Harmonisen $k$ amplitudi on
$\sqrt{a_k^2 + b_k^2} = 2|c_k|$ ja vaihe $\arg c_k$; kompleksinen kerroin
on siis jälleen osoitin, nyt jaettuna kahdella, koska puolet kuuluu
negatiiviselle taajuudelle.

Symmetria säästää laskuja. Jos signaali on **pariton**, $x(-t) = -x(t)$,
kaikki kosinikertoimet ovat nollia ja sarjassa on vain sinejä. Jos se
on **parillinen**, $x(-t) = x(t)$, sarjassa on vain kosineja.

## Kanttiaalto ja saha-aalto

**Kanttiaalto** on $+1$ jakson ensimmäisellä puoliskolla ja $-1$
toisella. Se on pariton (origon ympäri jaksollisesti jatkettuna), joten
$a_k = 0$, ja

$$b_k = \frac1\pi\Big(\int_0^\pi \sin kt\,dt - \int_\pi^{2\pi}\sin kt\,dt\Big)
= \frac{2}{\pi k}\big(1 - \cos k\pi\big)
= \begin{cases}4/(\pi k), & k \text{ pariton},\\ 0, & k \text{ parillinen}.\end{cases}$$

Kanttiaalto on siis
$\frac4\pi\big(\sin t + \frac13\sin 3t + \frac15\sin 5t + \cdots\big)$:
pelkkiä parittomia harmonisia, joiden amplitudit pienenevät kuten
$1/k$. Seuraava ohjelma laskee kertoimet numeerisesti 16384 pisteen
keskipistesäännöllä ja vertaa niitä kaavaan. Pisteet ovat jakson
osavälien keskipisteissä, jotta mikään piste ei osu hyppykohtaan.

```{.python tiedosto="esimerkit/06-kertoimet.py" osa="kertoimet"}
```

**Saha-aalto** nousee tasaisesti arvosta $-1$ arvoon $1$ ja hyppää
jakson lopussa takaisin. Kun $x(t) = (t - \pi)/\pi$ välillä $(0, 2\pi)$,
osittaisintegroinnilla saadaan $b_k = -2/(\pi k)$ kaikilla $k$:
saha-aallossa on kaikki harmoniset, ja nekin pienenevät kuten $1/k$.

```{.python tiedosto="esimerkit/06-kertoimet.py" osa="saha"}
```

```{.tuloste tiedosto="esimerkit/06-kertoimet.odotettu"}
```

Numeeriset kertoimet täsmäävät kaavoihin neljän desimaalin
tarkkuudella. Hyppykohta heikentää numeerista integrointia, koska
funktio ei ole sileä, mutta 16384 pistettä riittää runsaasti.

## Osasummat ja paras approksimaatio

Käytännössä sarjasta lasketaan **osasumma**, jossa on äärellinen määrä
termejä. Ortogonaalisuudesta seuraa tärkeä ominaisuus: osasumma
$\sum_{|k|\le N} c_k e^{ikt}$ on signaalin **ortogonaaliprojektio**
taajuuksien $-N, \ldots, N$ virittämään aliavaruuteen. Lineaarialgebran
tavoin projektio on lähin piste aliavaruudessa: mikään muu
trigonometrinen polynomi, jonka taajuudet ovat korkeintaan $N$, ei
approksimoi signaalia pienemmällä keskineliövirheellä. Parsevalin
kaavasta virhe on poisjätettyjen kertoimien tehojen summa:

$$\frac1{2\pi}\int_0^{2\pi}\Big|x(t) - \sum_{|k|\le N} c_k e^{ikt}\Big|^2 dt
= \sum_{|k| > N}|c_k|^2 = P - \sum_{|k| \le N}|c_k|^2.$$

Kanttiaallon teho on 1, ja harmonisen $k$ teho on
$b_k^2/2 = 8/(\pi k)^2$. Ohjelma laskee keskineliövirheen sekä
numeerisesti että kaavalla "1 miinus selitetty teho".

```{.python tiedosto="esimerkit/06-energia.py" osa="osasummat"}
```

## Energian jakautuminen ja sileys

Parsevalin kaava kertoo, miten signaalin teho jakautuu harmonisille.
Seuraava ohjelma vertaa kolmea aaltoa: kanttia, sahaa ja **kolmioaaltoa**,
joka nousee ja laskee tasaisesti. Kolmioaalto on jatkuva, mutta sen
derivaatta hyppää huippukohdissa.

```{.python tiedosto="esimerkit/06-energia.py" osa="energia"}
```

```{.tuloste tiedosto="esimerkit/06-energia.odotettu"}
```

![Kanttiaallon osasummat. Vasemmalla 1, 3 ja 25 termiä: osasumma
seuraa aaltoa yhä tarkemmin, mutta hypyn viereen jää piikki. Oikealla
suurennos hypyn vierestä: piikki kapenee, kun termejä lisätään, mutta
sen korkeus pysyy arvossa 1,179.](kuvat/osasummat.png){width=100%}

Kanttiaallon tehosta 81 prosenttia on perustaajuudella, koska
$8/\pi^2 \approx 0.81$. Saha-aallon teho jakautuu laajemmalle, koska
siinä ovat myös parilliset harmoniset. Kolmioaallon kertoimet
pienenevät kuten $1/k^2$, ja jo perustaajuudella on 98.6 prosenttia
tehosta ($96/\pi^4$).

Havainto on yleinen: **mitä sileämpi signaali, sitä nopeammin sen
Fourier-kertoimet pienenevät**. Hyppäävän signaalin kertoimet
pienenevät kuten $1/k$, jatkuvan mutta kulmikkaan kuten $1/k^2$, ja
kerran jatkuvasti derivoituvan kuten $1/k^3$. Äärettömän sileän
jaksollisen signaalin, kuten $e^{\cos t}$, kertoimet pienenevät
nopeammin kuin mikään potenssi; siksi luvun 5 puolisuunnikassääntö oli
sille niin tarkka. Käytännössä terävät reunat tarkoittavat leveää
spektriä: digitaalisen signaalin jyrkät bittirajat levittävät tehoa
korkeille taajuuksille, ja siksi lähetin suodattaa pulssinsa
pyöreämmiksi.

![Kertoimien itseisarvot logaritmisilla asteikoilla. Kantti- ja
saha-aallon pisteet laskevat kulmakertoimella −1 (kuten $1/k$),
kolmioaallon kulmakertoimella −2 (kuten
$1/k^2$).](kuvat/kertoimet.png){width=68%}

Harmonisten jakauma on myös se, minkä korva kuulee **sointivärinä**.
Seuraava ohjelma kirjoittaa saman sävelen (220 Hz) äänitiedostoiksi
sini-, kantti- ja saha-aaltona. Harmonisia otetaan mukaan vain puoleen
näytetaajuudesta asti; syyn kertoo taidon *Signaalit ja järjestelmät*
näytteistysteoreema. Sini kuulostaa pehmeältä, kanttiaalto ontolta ja
saha-aalto terävältä, vaikka sävelkorkeus on sama.

```{.python tiedosto="esimerkit/06-sointi.py" osa="sointi"}
```

```{.tuloste tiedosto="esimerkit/06-sointi.odotettu"}
```

## Gibbsin ilmiö

Hyppykohdan lähellä osasumma ylittää signaalin arvon. Ylityksen voi
olettaa pienenevän, kun termejä lisätään, mutta niin ei käy: ylitys
kapenee ja siirtyy lähemmäs hyppyä, mutta sen korkeus lähestyy noin
9 prosenttia hypyn suuruudesta. Tätä kutsutaan **Gibbsin ilmiöksi**.

Edellinen kuva näytti ilmiön; ohjelma mittaa sen. Se etsii
kanttiaallon osasumman ensimmäisen huipun hienojakoisesta hilasta. Huippu on kohdassa $t = \pi/(2n)$, kun osasummassa on $n$
parittoman taajuuden termiä.

```{.python tiedosto="esimerkit/06-gibbs.py" osa="gibbs"}
```

Ylityksen raja-arvo voidaan laskea. Osasumman derivaatta on
Dirichlet'n ytimen kaltainen kosinien summa,
$\frac{2}{\pi}\sin(2nt)/\sin t$, ja integroimalla se
huippuun asti saadaan raja-arvoksi $\frac{2}{\pi}\operatorname{Si}(\pi)$,
missä $\operatorname{Si}(x) = \int_0^x \frac{\sin u}{u}\,du$ on
**integraalisini**. Ohjelma laskee integraalin keskipistesäännöllä.

```{.python tiedosto="esimerkit/06-gibbs.py" osa="raja"}
```

Ylitys ei estä sarjaa suppenemasta keskineliön mielessä: virheen teho
pienenee kohti nollaa, koska ylitysalue kapenee. Suurin pisteittäinen
virhe sen sijaan pysyy lähes yhtenä, koska aivan hypyn vieressä
osasumma kulkee nollan kautta, kun signaali hyppää arvosta $-1$ arvoon
$1$. Hyppykohdassa osasumma on tasan hypyn keskiarvo.

```{.python tiedosto="esimerkit/06-gibbs.py" osa="keskineliö"}
```

```{.tuloste tiedosto="esimerkit/06-gibbs.odotettu"}
```

Gibbsin ilmiö näkyy käytännössä aina, kun spektri katkaistaan jyrkästi:
kuvan pakkauksessa terävien reunojen ympärille syntyy renkaita, ja
jyrkkä alipäästösuodatin aiheuttaa askelvasteeseen värähtelyä.
Katkaisua pehmentämällä (kertoimet painotetaan ennen summausta)
ylitys saadaan pienemmäksi, mutta reuna loivenee. Tämä on sama
valinta, jonka edessä ollaan DFT:n ikkunoinnissa.

## Käytännössä

- **Laske kertoimet korrelaatiolla.** $c_k$ on signaalin ja funktion
  $e^{ikt}$ sisätulo; numeerisesti tasavälisten näytteiden keskiarvo
  `numpy.mean(x * numpy.exp(-1j * k * t))` jakson yli.
- **Muunna kompleksinen ja reaalinen muoto.** Reaaliselle signaalille
  $a_k = 2\operatorname{Re}c_k$, $b_k = -2\operatorname{Im}c_k$ ja
  harmonisen amplitudi on $2|c_k|$.
- **Käytä symmetriaa.** Parittomassa signaalissa on vain sinejä,
  parillisessa vain kosineja.
- **Arvioi tarvittava termimäärä Parsevalilla.** Virheen teho on
  poisjätettyjen kertoimien neliöiden summa.
- **Odota ylitystä hyppyjen lähellä.** Gibbsin ilmiö ei katoa termejä
  lisäämällä; jos ylitys haittaa, pehmennä katkaisua.

## Itsearviointi

- Osaat johtaa Fourier-sarjan kerroinkaavan ortogonaalisuudesta ja
  laskea kertoimet numeerisesti.
- Osaat laskea kanttiaallon ja saha-aallon kertoimet ja selittää,
  miksi kanttiaallossa on vain parittomia harmonisia.
- Osaat selittää, miksi osasumma on paras approksimaatio keskineliön
  mielessä, ja laskea sen virheen Parsevalin kaavalla.
- Osaat kuvata, miten signaalin sileys näkyy kertoimien pienenemisessä,
  ja selittää Gibbsin ilmiön.
