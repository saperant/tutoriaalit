# Summat, sarjat ja integraalit signaaleille

Fourier-analyysi laskee kertoimia summina ja integraaleina. Ennen
Fourier-sarjaa tarvitaan siksi muutama työkalu: geometrisen summan
suljettu muoto, kompleksisten eksponenttien ortogonaalisuus,
numeerinen integrointi ja signaalin keskiarvo ja teho. Ne ovat
lineaarialgebran pistetulo ja normi pukeutuneina signaaleiksi, ja niistä
seuraa Parsevalin kaava: signaalin teho on kertoimien neliöiden summa.

## Geometrinen summa

**Geometrisessa summassa** jokainen termi on edellinen kerrottuna
samalla luvulla $r$. Sen suljettu muoto saadaan kertomalla summa
luvulla $r$ ja vähentämällä: lähes kaikki termit kumoutuvat, ja
jäljelle jää

$$S_n = \sum_{k=0}^{n-1} r^k = 1 + r + \cdots + r^{n-1} = \frac{1 - r^n}{1 - r}, \qquad r \ne 1.$$

Kun $r = 1$, summa on $n$. Kaava pätee myös kompleksiluvuille, ja juuri
kompleksisena se on hyödyllisin, koska kompleksisten eksponenttien summa
$\sum_k e^{ik\theta}$ on geometrinen summa suhdeluvulla $r = e^{i\theta}$.
Kun $|r| < 1$, termi $r^n$ häviää ja **geometrinen sarja** suppenee:
$\sum_{k=0}^{\infty} r^k = 1/(1 - r)$.

```{.python tiedosto="esimerkit/05-geometrinen.py" osa="geometrinen"}
```

Geometrinen summa esiintyy kaikkialla, missä jokin toistuu samalla
kertoimella: korkoa korolle, kaiku, joka vaimenee joka heijastuksella
samassa suhteessa, ja rekursiivinen suodatin $y[n] = x[n] + ry[n-1]$,
jonka impulssivaste on $1, r, r^2, \ldots$ Viimeinen on taidon
*Signaalit ja järjestelmät* keskeinen esimerkki.

## Dirichlet'n ydin

Symmetrinen kompleksisten eksponenttien summa on geometrinen summa,
jonka suljettu muoto on erityisen siisti. Kun summassa on taajuudet
$-N, \ldots, N$,

$$D_N(x) = \sum_{k=-N}^{N} e^{ikx} = e^{-iNx}\frac{1 - e^{i(2N+1)x}}{1 - e^{ix}}
= \frac{\sin\big((N + \tfrac12)x\big)}{\sin(x/2)}.$$

Viimeinen muoto saadaan ottamalla osoittajasta ja nimittäjästä
yhteiseksi tekijäksi puolikulman eksponentit, jolloin jäljelle jää
sinien osamäärä. Tulos on reaalinen, koska termit $e^{ikx}$ ja
$e^{-ikx}$ ovat toistensa liittolukuja ja niiden summa on $2\cos kx$.
Funktiota kutsutaan **Dirichlet'n ytimeksi**. Pisteessä $x = 0$ kaikki
termit ovat ykkösiä, joten raja-arvo on $2N + 1$.

```{.python tiedosto="esimerkit/05-geometrinen.py" osa="dirichlet"}
```

```{.tuloste tiedosto="esimerkit/05-geometrinen.odotettu"}
```

Esimerkissä summa lasketaan NumPylla ilman silmukkaa: taajuudet ovat
sarakevektori `k` ja pisteet rivivektori `x`, jolloin `1j * k * x` on
**levityksen** (*broadcasting*) ansiosta matriisi, jonka rivi $k$ on
$kx$. Summa rivien yli antaa jokaisen pisteen summan kerralla.
Dirichlet'n ydin on kapea piikki origossa, ja sen leveys on noin
$2\pi/(2N+1)$. Piikki kapenee ja kasvaa, kun $N$ kasvaa, mutta sen
sivuilla aaltoilu ei katoa. Tämä aaltoilu selittää luvun 6 Gibbsin
ilmiön, ja diskreettinä versiona se on liukuvan keskiarvon
taajuusvaste luvussa 9.

## Ortogonaalisuus

Lineaarialgebrassa vektorit ovat **ortogonaalisia**, kun niiden
pistetulo on nolla. Jaksollisille funktioille jakson $[0, 2\pi]$ yli
määritellään **sisätulo**

$$\langle u, v \rangle = \frac{1}{2\pi}\int_0^{2\pi} u(t)\,\overline{v(t)}\,dt.$$

Se on pistetulon jatkuva vastine: summa on korvattu integraalilla, ja
kompleksisessa tapauksessa jälkimmäinen tekijä on liittoluku, jotta
$\langle u, u\rangle = \frac{1}{2\pi}\int |u|^2\,dt$ on reaalinen ja
positiivinen, kuten normin neliön pitää. Kompleksiset eksponentit
$e_n(t) = e^{int}$ ovat tämän sisätulon suhteen **ortonormaaleja**:

$$\langle e_m, e_n \rangle = \frac{1}{2\pi}\int_0^{2\pi} e^{i(m-n)t}\,dt
= \begin{cases} 1, & m = n,\\ 0, & m \ne n.\end{cases}$$

Kun $m \ne n$, funktio $e^{i(m-n)t}$ kiertää yksikköympyrää kokonaisen
määrän kierroksia, ja sen keskiarvo on nolla. Reaalisille funktioille
saadaan vastaavat relaatiot: jakson yli $\sin mt$ ja $\cos nt$ ovat aina
ortogonaalisia, $\sin mt$ ja $\sin nt$ ovat ortogonaalisia, kun $m \ne n$,
ja $\sin^2 nt$:n keskiarvo on $\frac12$.

Ohjelma laskee integraalin keskiarvona 64 tasavälisestä pisteestä
jakson yli. Kompleksisille eksponenteille tämä keskiarvo on luvun 3
ykkösen juurten summa jaettuna $N$:llä, joten se on tarkka: nolla tai
yksi pyöristysvirheen tarkkuudella.

```{.python tiedosto="esimerkit/05-ortogonaalisuus.py" osa="ortogonaalisuus"}
```

```{.tuloste tiedosto="esimerkit/05-ortogonaalisuus.odotettu"}
```

Viimeinen rivi näyttää diskreetin laskun rajan: 64 näytteellä taajuuksia
$65$ ja $1$ ei voi erottaa, koska $e^{i65t}$ ja $e^{it}$ saavat samat
arvot jokaisessa näytepisteessä $t = 2\pi j/64$. Tämä on **aliasointi**,
jota käsitellään taidossa *Signaalit ja järjestelmät*. Fourier-analyysin
kannalta tärkeää on, että eri taajuudet ovat ortogonaalisia, joten
kunkin taajuuden kerroin voidaan mitata erikseen pistetulolla, kuten
luvun 4 korrelaatiomittauksessa. Ortogonaalisessa kannassa vektorin
koordinaatit ovat juuri pistetulot kantavektorien kanssa, ilman
yhtälöryhmän ratkaisemista.

## Integraalit summina

Integraali on pinta-ala käyrän alla, ja numeerisesti se lasketaan
summana. **Puolisuunnikassääntö** jakaa välin $n$ yhtä pitkään osaan,
korvaa käyrän jokaisella osalla janalla ja laskee puolisuunnikkaiden
alat yhteen:

$$\int_a^b g(x)\,dx \approx h\Big(\tfrac12 g(x_0) + g(x_1) + \cdots + g(x_{n-1}) + \tfrac12 g(x_n)\Big), \qquad h = \frac{b-a}{n}.$$

Tavallisesti virhe on verrannollinen lukuun $h^2$: kaksinkertainen
pistemäärä pienentää virhettä neljäsosaan. Jaksolliselle sileälle
funktiolle koko jakson yli sääntö on kuitenkin poikkeuksellisen tarkka,
koska päätepisteet ovat sama piste ja virhetermit kumoutuvat. Silloin
virhe pienenee nopeammin kuin mikään $h$:n potenssi.

```{.python tiedosto="esimerkit/05-integraali.py" osa="integraali"}
```

```{.tuloste tiedosto="esimerkit/05-integraali.odotettu"}
```

Funktion $x^2$ virhe pienenee tasaisesti neljäsosaan aina, kun
pistemäärä kaksinkertaistuu, mutta jaksollisen
funktion $e^{\cos x}$ virhe putoaa jo 16 pisteellä pyöristysvirheen
tasolle. Jaksollisen funktion puolisuunnikassääntö jakson yli on
tasavälisten näytteiden keskiarvo kerrottuna jakson pituudella. Siksi
tutoriaalin esimerkit laskevat jaksollisia integraaleja muodossa
`numpy.mean(...)`, ja sama havainto selittää, miksi DFT laskee
Fourier-sarjan kertoimet niin hyvin sileille signaaleille.

## Keskiarvo, teho ja tehollisarvo

Signaalin **keskiarvo** eli tasakomponentti ja **teho** määritellään
aikakeskiarvoina, jaksolliselle signaalille yhden jakson yli:

$$\bar x = \frac1T\int_0^T x(t)\,dt, \qquad P = \frac1T\int_0^T |x(t)|^2\,dt.$$

Teho on signaalin normin neliö. Sähkötekniikassa nimitys on
kirjaimellinen: jos $x$ on jännite yhden ohmin vastuksen yli, $P$ on
keskimääräinen teho watteina. **Tehollisarvo** (*RMS*, *root mean
square*) on $\sqrt{P}$, se tasajännite, joka tuottaa saman tehon.
Sinimuotoiselle signaalille $A\cos(2\pi ft + \varphi)$ teho on $A^2/2$,
koska kosinin neliön keskiarvo on $\frac12$, ja tehollisarvo on siten
$A/\sqrt2$. Suomen verkkojännitteen tehollisarvo on 230 V, joten sen
huippuarvo on noin 325 V.

Kun signaalissa on tasakomponentti $c$ ja sinimuotoinen osa, teho on
$c^2 + A^2/2$: ristitermi $2cA\cos(\cdot)$ on keskiarvoltaan nolla,
koska vakio ja kosini ovat ortogonaalisia.

```{.python tiedosto="esimerkit/05-teho.py" osa="teho"}
```

## Parsevalin kaava

Jos signaali on kompleksisten eksponenttien summa
$x(t) = \sum_k c_k e^{ikt}$, sen teho on

$$P = \frac{1}{2\pi}\int_0^{2\pi} |x(t)|^2\,dt = \sum_k |c_k|^2.$$

Tämä on **Parsevalin kaava**. Se seuraa suoraan ortogonaalisuudesta:
kun $|x|^2 = x\bar x$ kerrotaan auki, saadaan termejä
$c_m \bar c_n e^{i(m-n)t}$, joiden keskiarvo on nolla aina, kun
$m \ne n$. Jäljelle jäävät termit $|c_k|^2$. Lineaarialgebran kielellä
kaava on Pythagoraan lause ortonormaalissa kannassa: vektorin pituuden
neliö on koordinaattien neliöiden summa. Teho jakautuu siis
taajuuksille, ja jokaisen taajuuden osuus on sen kertoimen itseisarvon
neliö.

```{.python tiedosto="esimerkit/05-teho.py" osa="parseval"}
```

Reaalisessa signaalissa kertoimet tulevat pareittain, $c_{-k} = \bar c_k$,
joten taajuuden $k$ kosinin ja sinin teho jakautuu tasan
positiiviselle ja negatiiviselle taajuudelle. Esimerkissä taajuudella
1 on yli 90 prosenttia koko tehosta, puolet kummallakin merkillä.

## Desibelit

Tehot vaihtelevat signaalinkäsittelyssä monella kertaluvulla, joten
niitä verrataan logaritmisesti. Desibeli määriteltiin luvussa 4
interferenssin yhteydessä: tehosuhteelle $10\log_{10}(P/P_0)$ ja
amplitudisuhteelle $20\log_{10}(A/A_0)$. Nyt kun teho ja tehollisarvo
on määritelty, muunnokset voi laskea. Taidon *Tietoliikennetekniikka*
signaali-kohinasuhde (SNR) ja linkkibudjetti ovat juuri tällaisia
lukuja.

```{.python tiedosto="esimerkit/05-teho.py" osa="desibelit"}
```

```{.tuloste tiedosto="esimerkit/05-teho.odotettu"}
```

| Suhde | Teho | Amplitudi |
|-------|------|-----------|
| kaksinkertainen | $+3.01$ dB | $+6.02$ dB |
| puolikas | $-3.01$ dB | $-6.02$ dB |
| kymmenkertainen | $+10$ dB | $+20$ dB |
| tuhatkertainen | $+30$ dB | $+60$ dB |

## Käytännössä

- **Tunnista geometrinen summa.** Kun summassa on termi $r^k$ tai
  $e^{ik\theta}$, käytä suljettua muotoa $(1 - r^n)/(1 - r)$ äläkä
  laske silmukassa.
- **Laske jaksolliset integraalit keskiarvona.** Tasavälisten
  näytteiden keskiarvo koko jakson yli on erittäin tarkka sileille
  jaksollisille funktioille. Älä toista päätepistettä: jakson
  $[0, 2\pi)$ näytteistä viimeinen on $2\pi(N-1)/N$.
- **Ajattele tehoa normin neliönä.** Ortogonaalisten osien tehot
  lasketaan yhteen, ja ristitermit häviävät.
- **Käytä desibelejä vertailuun.** Muista kerroin 10 teholle ja 20
  amplitudille.

## Itsearviointi

- Osaat johtaa geometrisen summan suljetun muodon ja käyttää sitä
  kompleksisten eksponenttien summaan.
- Osaat selittää, miksi kompleksiset eksponentit ovat ortogonaalisia
  jakson yli, ja tarkistaa sen numeerisesti.
- Osaat laskea signaalin keskiarvon, tehon ja tehollisarvon ja
  perustella sinisignaalin tehon $A^2/2$.
- Osaat muotoilla Parsevalin kaavan ja selittää sen yhteyden Pythagoraan
  lauseeseen ortonormaalissa kannassa.
