# Fourier-muunnos

Fourier-sarja käsittelee jaksollisia signaaleja. Useimmat signaalit
eivät kuitenkaan ole jaksollisia: puhe, yksittäinen tutkapulssi ja
kiihtyvyysanturin mittaama isku alkavat ja loppuvat. **Fourier-muunnos**
yleistää sarjan jaksottomille signaaleille. Harmonisten erillisten
taajuuksien sijaan signaalissa on jatkumo taajuuksia, ja kertoimien
sijaan sillä on **spektri** $X(f)$, joka on määritelty kaikilla
reaalisilla taajuuksilla.

## Sarjasta muunnokseen

Jakson $T$ Fourier-sarjassa taajuudet ovat $k/T$, ja niiden väli on
$1/T$. Kun jaksoa pidennetään, taajuudet tihenevät, ja rajalla
$T \to \infty$ yksi jakso kattaa koko aika-akselin. Kerroinkaavasta
$c_k = \frac1T\int_{-T/2}^{T/2} x(t)e^{-2\pi i (k/T) t}\,dt$ tulee
taajuuden $f = k/T$ funktio, ja kun kerroin kerrotaan jaksolla $T$,
saadaan raja-arvona **Fourier-muunnos** ja sen käänteismuunnos:

$$X(f) = \int_{-\infty}^{\infty} x(t)\,e^{-2\pi i f t}\,dt, \qquad
x(t) = \int_{-\infty}^{\infty} X(f)\,e^{2\pi i f t}\,df.$$

Käänteismuunnos on sarjan summa, jossa summa on muuttunut
integraaliksi. Kaavat ovat lähes symmetriset: ainoa ero on
eksponentin merkki. Tässä muodossa taajuus on hertseinä, eikä
kaavoissa tarvita normituskertoimia. Kirjallisuudessa käytetään myös
kulmataajuutta $\omega = 2\pi f$, jolloin käänteismuunnokseen tulee
kerroin $1/(2\pi)$; kaavoja eri lähteistä yhdistäessä on tarkistettava,
kumpaa sopimusta lähde käyttää.

$X(f)$ on yleensä kompleksinen. Sen itseisarvo $|X(f)|$ on
**amplitudispektri** ja kulma $\arg X(f)$ **vaihespektri**. Reaaliselle
signaalille $X(-f) = \overline{X(f)}$, joten negatiiviset taajuudet
eivät tuo uutta tietoa; ne ovat luvun 4 vastakkaiseen suuntaan
pyöriviä nuolia, joita tarvitaan, jotta summa on reaalinen.

## Numeerinen muunnos

Integraali lasketaan numeerisesti summana tasavälisessä hilassa:
$X(f) \approx \sum_n x(t_n)e^{-2\pi i f t_n}\,\Delta t$. Kun halutaan
monta taajuutta kerralla, summa on matriisin ja vektorin tulo: matriisin
rivi $f$ sisältää luvut $e^{-2\pi i f t_n}$. Luvussa 9 nähdään, että
DFT on juuri tällainen matriisitulo erityisellä taajuushilalla.

Ensimmäinen muunnospari on **kanttipulssi** $\operatorname{rect}(t)$,
joka on 1 välillä $|t| < \frac12$ ja muualla 0. Sen muunnos lasketaan
suoraan:

$$X(f) = \int_{-1/2}^{1/2} e^{-2\pi i f t}\,dt
= \frac{e^{-\pi i f} - e^{\pi i f}}{-2\pi i f}
= \frac{\sin \pi f}{\pi f} = \operatorname{sinc} f.$$

NumPyn `numpy.sinc` on juuri tämä normitettu sinc-funktio, ja sen arvo
nollassa on 1.

```{.python tiedosto="esimerkit/07-parit.py" osa="muunnos"}
```

Sinc-funktion nollakohdat ovat kokonaisluvuissa $f = \pm1, \pm2, \ldots$,
ja sen sivukeilat pienenevät kuten $1/f$. Pulssin terävät reunat
näkyvät hitaasti vaimenevana spektrinä, kuten kanttiaallon kertoimissa
luvussa 6.

Toinen tärkeä pari on **Gaussin pulssi**. Funktion $e^{-\pi t^2}$
muunnos on $e^{-\pi f^2}$: Gaussin funktio on oma Fourier-muunnoksensa.
Gaussin pulssi on sileä ja vaimenee nopeasti, joten sen spektrikin on
sileä ja vaimenee nopeasti.

```{.python tiedosto="esimerkit/07-parit.py" osa="gauss"}
```

```{.tuloste tiedosto="esimerkit/07-parit.odotettu"}
```

Gaussin pulssin numeerinen muunnos on tarkka pyöristysvirheen
tasolla, koska pulssi on sileä ja häviää käytännössä kokonaan hilan
ulkopuolella. Kanttipulssin virhe on alle $10^{-6}$ mutta paljon
pyöristysvirhettä suurempi, koska reunat heikentävät summan tarkkuutta. Kummankin muunnos on reaalinen, koska
signaali on parillinen: parillisen signaalin integraalissa sinitermit
kumoavat toisensa.

| Signaali $x(t)$ | Muunnos $X(f)$ | Huomio |
|--------------------------|--------------------------|-----------------------------|
| $\operatorname{rect}(t)$ | $\operatorname{sinc} f$ | terävä reuna, hidas vaimeneminen |
| $e^{-\pi t^2}$ | $e^{-\pi f^2}$ | oma muunnoksensa |
| $e^{-\lvert t\rvert}$ | $2/(1 + 4\pi^2 f^2)$ | kulma origossa, vaimeneminen $1/f^2$ |
| kolmio $\max(0, 1 - \lvert t\rvert)$ | $\operatorname{sinc}^2 f$ | rect konvoloituna itsensä kanssa (luku 8) |
| $\delta(t)$ (impulssi) | $1$ | kaikki taajuudet samalla painolla |
| $\cos 2\pi f_0 t$ | $\frac12\delta(f - f_0) + \frac12\delta(f + f_0)$ | kaksi piikkiä $\pm f_0$ |

Kaksi viimeistä paria sisältävät **Diracin deltan** $\delta$, joka on
idealisoitu äärettömän kapea pulssi, jonka pinta-ala on 1. Se ei ole
tavallinen funktio, mutta käytännössä sen voi ajatella hyvin kapeaksi
Gaussin pulssiksi. Puhtaan kosinin spektri on kaksi piikkiä taajuuksilla
$\pm f_0$, mikä sopii yhteen luvun 3 kaavan
$\cos\theta = \frac12(e^{i\theta} + e^{-i\theta})$ kanssa.

## Ominaisuudet

Muunnoksen hyöty ei ole yksittäisissä pareissa vaan ominaisuuksissa,
joilla uusia pareja johdetaan vanhoista. Kaikki seuraavat saadaan
sijoittamalla määritelmään:

| Ominaisuus | Signaali | Muunnos |
|------------|----------|---------|
| lineaarisuus | $a x(t) + b y(t)$ | $a X(f) + b Y(f)$ |
| aikasiirto | $x(t - t_0)$ | $e^{-2\pi i f t_0} X(f)$ |
| modulaatio | $x(t) e^{2\pi i f_0 t}$ | $X(f - f_0)$ |
| skaalaus | $x(at)$ | $\frac{1}{\lvert a\rvert} X(f/a)$ |
| liittoluku | $\overline{x(t)}$ | $\overline{X(-f)}$ |
| derivaatta | $x'(t)$ | $2\pi i f\, X(f)$ |
| konvoluutio | $(x * y)(t)$ | $X(f)\,Y(f)$ |

Aikasiirto ei muuta amplitudispektriä vaan lisää vaiheeseen lineaarisen
termin $-2\pi f t_0$: viive näkyy taajuustasossa vaiheena, joka kasvaa
tasaisesti taajuuden mukana. Modulaatio on aikasiirron peilikuva: kun
signaali kerrotaan kompleksisella eksponentilla, spektri siirtyy. Näin
radiolähetin siirtää äänen tai datan spektrin kantoaallon ympärille.
Kosinilla kertominen siirtää spektrin kahteen paikkaan, $\pm f_0$,
puolella painolla. Skaalaus sanoo, että aikatasossa kapeampi signaali
on taajuustasossa leveämpi. Derivaatta on taas kertolasku, kuten
osoittimilla luvussa 4.

Ohjelma tarkistaa ominaisuudet Gaussin pulssilla, jonka muunnos
tunnetaan. Jokaisessa rivissä vasen puoli on numeerisesti laskettu
muunnos ja oikea puoli ominaisuudella johdettu lauseke.

```{.python tiedosto="esimerkit/07-ominaisuudet.py" osa="ominaisuudet"}
```

```{.tuloste tiedosto="esimerkit/07-ominaisuudet.odotettu"}
```

Konvoluutio-ominaisuus on muunnoksen tärkein, ja se on luvun 8 aihe.

## Aika–taajuus-epätarkkuus

Skaalausominaisuus kertoo, että signaalia ei voi tiivistää sekä ajassa
että taajuudessa. Tämän voi muotoilla täsmällisesti. Tulkitaan
$|x(t)|^2$ ja $|X(f)|^2$ todennäköisyysjakaumiksi (Parsevalin kaavan
jatkuvan version mukaan niiden kokonaispinta-alat ovat samat) ja
lasketaan niiden keskihajonnat $\sigma_t$ ja $\sigma_f$. **Epätarkkuus-
periaatteen** mukaan

$$\sigma_t\,\sigma_f \ge \frac{1}{4\pi},$$

ja yhtäsuuruus pätee vain Gaussin pulssille. Kvanttimekaniikan
Heisenbergin epätarkkuusperiaate on matemaattisesti sama tulos.

Taajuushajonnan voi laskea ilman muunnosta. Derivaattaominaisuuden ja
Parsevalin kaavan mukaan
$\int f^2 |X(f)|^2\,df = \frac{1}{4\pi^2}\int |x'(t)|^2\,dt$, joten
reaaliselle signaalille, jonka spektri on symmetrinen nollan suhteen,

$$\sigma_f^2 = \frac{\int |x'(t)|^2\,dt}{4\pi^2\int |x(t)|^2\,dt}.$$

Ohjelma laskee hajonnat neljälle pulssille. Derivaatta lasketaan
numeerisesti funktiolla `numpy.gradient`.

```{.python tiedosto="esimerkit/07-epatarkkuus.py" osa="epatarkkuus"}
```

```{.tuloste tiedosto="esimerkit/07-epatarkkuus.odotettu"}
```

Molemmat Gaussin pulssit saavuttavat alarajan, vaikka niiden leveydet
eroavat kymmenkertaisesti: kapeampi pulssi on taajuudessa
kymmenkertaisesti leveämpi. Eksponenttipulssin $e^{-|t|}$ tulo on noin
40 prosenttia yli rajan, ja Hann-pulssin (kosinin muotoinen
kumpare) vain vähän yli. Kanttipulssi puuttuu taulukosta, koska sen
taajuushajonta on ääretön: $\operatorname{sinc}^2$ vaimenee kuten
$1/f^2$, joten $f^2 \operatorname{sinc}^2 f$ ei vaimene lainkaan.
Kaavan kielellä kanttipulssin derivaatta on kaksi deltaa, eikä
$\int|x'|^2$ ole äärellinen.

Epätarkkuus on käytännön rajoite. Lyhyt mittausikkuna ei voi erottaa
lähellä toisiaan olevia taajuuksia, ja kapean taajuuskaistan
tietoliikennekanava ei voi siirtää lyhyitä pulsseja. Tutkan
etäisyystarkkuus riippuu pulssin kaistanleveydestä samasta syystä.

## Käytännössä

- **Tarkista muunnoksen sopimus.** Hertseinä ($e^{-2\pi ift}$, ei
  kertoimia) vai kulmataajuutena ($e^{-i\omega t}$, kerroin $1/2\pi$
  käänteismuunnoksessa); kaavoja ei voi sekoittaa.
- **Johda uudet parit ominaisuuksista.** Siirto, modulaatio ja skaalaus
  muuttavat tunnetun parin uudeksi ilman integrointia.
- **Lue viive vaiheesta.** Lineaarisesti taajuuden mukana kasvava vaihe
  on aikasiirto; kulmakerroin on $-2\pi t_0$.
- **Muista epätarkkuus.** Kapea pulssi tarkoittaa leveää spektriä ja
  päinvastoin; Gaussin pulssi on paras mahdollinen kompromissi.

## Itsearviointi

- Osaat kirjoittaa Fourier-muunnoksen ja sen käänteismuunnoksen ja
  selittää, miten ne seuraavat Fourier-sarjasta.
- Osaat laskea kanttipulssin muunnoksen ja tarkistaa parit
  rect–sinc ja Gauss–Gauss numeerisesti.
- Osaat käyttää aikasiirron, modulaation ja skaalauksen ominaisuuksia
  ja selittää niiden merkityksen signaaleille.
- Osaat muotoilla aika–taajuus-epätarkkuuden ja laskea pulssin
  hajonnat $\sigma_t$ ja $\sigma_f$ numeerisesti.
