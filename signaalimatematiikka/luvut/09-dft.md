# Diskreetti Fourier-muunnos kannanvaihtona

Tietokone ei laske integraaleja eikä käsittele äärettömiä signaaleja.
Se käsittelee äärellisiä näytejonoja $x[0], \ldots, x[N-1]$, ja niille
Fourier-analyysin työkalu on **diskreetti Fourier-muunnos** (DFT):

$$X[k] = \sum_{n=0}^{N-1} x[n]\,e^{-2\pi i k n/N}, \qquad k = 0, \ldots, N-1.$$

DFT on Fourier-sarjan kerroinkaava, jossa integraali on korvattu
summalla $N$ tasavälisen näytteen yli. Samalla se on lineaarialgebran
peruskäsite: **kannanvaihto ortogonaaliseen kantaan**. Tässä luvussa DFT
kirjoitetaan matriisina, sen ortogonaalisuus tarkistetaan, se
toteutetaan itse ja verrataan funktioon `numpy.fft.fft`, ja lopuksi
nähdään, miksi FFT-algoritmi laskee saman tuloksen paljon nopeammin.

## DFT-matriisi

Koska DFT on lineaarinen, se on matriisin ja vektorin tulo $X = Fx$,
missä matriisin alkiot ovat

$$F_{kn} = e^{-2\pi i k n/N} = w^{kn}, \qquad w = e^{-2\pi i/N}.$$

Luku $w$ on ykkösen $N$:s juuri (luku 3), ja matriisin rivi $k$ sisältää
sen potenssit $w^{0}, w^{k}, w^{2k}, \ldots$ Kun $N = 4$, $w = -i$, ja
matriisi koostuu luvuista $1, -i, -1, i$.

Matriisin sarakkeet ovat ortogonaalisia: sarakkeiden $m$ ja $n$
sisätulo on $\sum_k w^{k(n-m)}$, joka on ykkösen juurten summa, siis $N$
tai nolla. Matriisimuodossa

$$F^H F = N I,$$

missä $F^H = \bar F^T$ on **liittotranspoosi**: transpoosi, jonka
alkioista on otettu liittoluku. Kompleksisille vektoreille sisätulo on
$\langle u, v\rangle = \sum_n u_n \bar v_n$, ja liittotranspoosi on
transpoosin vastine. Matriisi $U = F/\sqrt N$ toteuttaa ehdon
$U^H U = I$; se on **unitaarinen**, ortogonaalisen matriisin
kompleksinen vastine. Unitaarinen kuvaus säilyttää pituudet ja kulmat,
kuten taidon *Lineaarialgebra* kierrot ja peilaukset.

```{.python tiedosto="esimerkit/09-dft-matriisi.py" osa="matriisi"}
```

## Oma toteutus

DFT:n määritelmä on kaksi sisäkkäistä silmukkaa: jokaiselle
taajuudelle $k$ summa kaikkien näytteiden yli. Työmäärä on $N^2$
kompleksista kertolaskua. Sama saadaan matriisitulona, joka on NumPylla
nopeampi mutta yhtä lailla neliöllinen ja vaatii lisäksi $N^2$ alkion
matriisin muistiin.

```{.python tiedosto="esimerkit/09-dft-matriisi.py" osa="oma"}
```

```{.tuloste tiedosto="esimerkit/09-dft-matriisi.odotettu"}
```

Satunnaisdata on hyvä testisyöte, koska sillä on kaikki taajuudet.
Siemen on kiinteä, ja vertailu tehdään toleranssilla funktiolla
`numpy.allclose`, koska eri algoritmit summaavat eri järjestyksessä ja
saavat siksi hieman eri pyöristysvirheet.

## Kertoimet ovat koordinaatteja

Matriisin $F$ rivi $k$ on kantavektorin
$e_k[n] = e^{2\pi i k n/N}$ liittoluku. Siksi

$$X[k] = \sum_n x[n]\,\overline{e_k[n]} = \langle x, e_k \rangle:$$

DFT:n kerroin on signaalin sisätulo kantavektorin $e_k$ kanssa, eli
signaalin koordinaatti tämän kantavektorin suunnassa (kerrottuna
kantavektorin normin neliöllä $N$). Kantavektorit ovat ortogonaalisia,
joten signaali saadaan takaisin koordinaateistaan suoraan:

$$x[n] = \frac1N\sum_{k=0}^{N-1} X[k]\,e^{2\pi i k n/N}.$$

Tämä on **käänteinen DFT**, matriisimuodossa $x = \frac1N F^H X$.
Kannanvaihdon käänteismatriisia ei tarvitse ratkaista, koska
ortogonaalisessa kannassa se on liittotranspoosi. Pituuksien
säilymisestä seuraa diskreetti **Parsevalin kaava**
$\sum_n |x[n]|^2 = \frac1N\sum_k |X[k]|^2$.

```{.python tiedosto="esimerkit/09-kanta.py" osa="kanta"}
```

```{.tuloste tiedosto="esimerkit/09-kanta.odotettu"}
```

Taidon *Lineaarialgebra* kannanvaihdossa vektori esitettiin uusien
kantavektorien painotettuna summana. DFT tekee täsmälleen saman: se
vaihtaa näytekannasta, jossa jokainen kantavektori on yksi hetki,
taajuuskantaan, jossa jokainen kantavektori on yksi kompleksinen
värähtely. Sama signaali, eri koordinaatit.

## Indeksit ja taajuudet

DFT:n indeksi $k$ ei ole hertsejä. Kun näytetaajuus on $f_s$ ja
näytteitä on $N$, indeksi $k$ vastaa taajuutta $k f_s/N$, ja taajuuksien
väli on $f_s/N$, mittausajan käänteisluku. Lisäksi indeksit
$k > N/2$ ovat oikeasti negatiivisia taajuuksia: koska
$e^{2\pi i k n/N} = e^{2\pi i (k - N) n/N}$ jokaisella kokonaisluvulla
$n$, indeksi $N - 1$ on sama kuin $-1$. Funktio `numpy.fft.fftfreq`
antaa kunkin indeksin taajuuden, ja `numpy.fft.fftshift` järjestää
taulukon niin, että nollataajuus on keskellä.

Reaaliselle signaalille $X[N - k] = \overline{X[k]}$, joten puolet
kertoimista on tarpeettomia. `numpy.fft.rfft` laskee vain
ei-negatiiviset taajuudet, ja siksi luvun 1 esimerkki käytti sitä.
Sinimuotoisen komponentin amplitudi jakautuu kahdelle kertoimelle,
$+k$ ja $-k$, kummallekin puolet; siksi amplitudi on $2|X[k]|/N$.

```{.python tiedosto="esimerkit/09-taajuudet.py" osa="taajuudet"}
```

```{.tuloste tiedosto="esimerkit/09-taajuudet.odotettu"}
```

Kosinin osoitin $1$ jakautuu kertoimiksi $\frac12$ taajuuksille
$\pm 100$ Hz, ja sinin osoitin $-0.5i$ kertoimiksi $-0.25i$ ja $0.25i$.
Luvun 1 tulos oli niin siisti, koska molemmat taajuudet tekivät
mittausaikana kokonaisen määrän jaksoja ja osuivat siten tarkasti DFT:n
taajuushilaan. Kun näin ei ole, komponentin teho leviää naapuri-
indekseihin. Tämä **vuotaminen** ja sen hillitseminen ikkunoinnilla
kuuluvat taitoon *Signaalit ja järjestelmät*.

## DFT, Fourier-sarja ja Fourier-muunnos

DFT liittyy edellisten lukujen muunnoksiin kahdella tavalla. Jos
jaksollinen signaali on trigonometrinen polynomi, jonka korkein
taajuus on alle $N/2$, sen näytteistä laskettu $X[k]/N$ on **tarkalleen**
Fourier-sarjan kerroin $c_k$. Tämä on luvun 5 havainto: tasavälinen
keskiarvo jakson yli on trigonometrisille polynomeille tarkka integraali.
Muille jaksollisille signaaleille tulos on likiarvo, johon korkeammat
harmoniset sekoittuvat aliasoitumalla.

Jaksottomalle pulssille DFT antaa Fourier-muunnoksen likiarvon
taajuuksilla $k/(N\Delta t)$, kun tulos kerrotaan näytevälillä
$\Delta t$ ja aika-akselin nollakohta siirretään indeksiin 0
(`numpy.fft.ifftshift`). Likiarvo on hyvä, kun pulssi mahtuu
näyteikkunaan ja sen spektri on lähes nolla taajuuden $1/(2\Delta t)$
yläpuolella.

```{.python tiedosto="esimerkit/09-yhteys.py" osa="sarja"}
```

```{.python tiedosto="esimerkit/09-yhteys.py" osa="muunnos"}
```

```{.tuloste tiedosto="esimerkit/09-yhteys.odotettu"}
```

## FFT: miksi `numpy.fft` on nopea

Suora DFT vaatii $N^2$ kertolaskua. Miljoonan näytteen signaalille se
on $10^{12}$ operaatiota, mikä on liian paljon. **Nopea Fourier-muunnos**
(FFT, Cooleyn ja Tukeyn algoritmi vuodelta 1965) laskee saman tuloksen
noin $N\log_2 N$ operaatiolla hyödyntämällä matriisin $F$ rakennetta.

Kun $N$ on parillinen, summa jaetaan parillisiin ja parittomiin
indekseihin:

$$X[k] = \sum_{m=0}^{N/2-1} x[2m]\,w_N^{2mk} + w_N^k \sum_{m=0}^{N/2-1} x[2m+1]\,w_N^{2mk}
= E[k] + w_N^k\,O[k],$$

missä $w_N = e^{-2\pi i/N}$. Koska $w_N^2 = w_{N/2}$, molemmat summat ovat
puolen pituuden DFT:itä: $E$ parillisista näytteistä ja $O$
parittomista. Ne ovat jaksollisia jaksolla $N/2$, ja koska
$w_N^{k + N/2} = -w_N^k$, saadaan molemmat puoliskot kerralla:

$$X[k] = E[k] + w_N^k O[k], \qquad X[k + N/2] = E[k] - w_N^k O[k], \qquad k < N/2.$$

Yksi $N$:n pituinen DFT on siis kaksi $N/2$:n pituista ja $N/2$
kertolaskua **kiertokertoimilla** $w_N^k$ (*twiddle factors*). Kun $N$
on kahden potenssi, jakoa voi jatkaa rekursiivisesti yhden näytteen
DFT:hen asti, ja yhden näytteen DFT on näyte itse.

```{.python tiedosto="esimerkit/09-fft.py" osa="fft"}
```

Kertolaskujen määrä toteuttaa rekursion $T(N) = 2T(N/2) + N/2$, jonka
ratkaisu on $T(N) = \frac N2\log_2 N$. Ohjelma laskee rekursion ja
vertaa suoran DFT:n määrään $N^2$.

```{.python tiedosto="esimerkit/09-fft.py" osa="laskut"}
```

```{.tuloste tiedosto="esimerkit/09-fft.odotettu"}
```

Miljoonan näytteen signaalilla FFT on satatuhatta kertaa nopeampi.
Ero on algoritminen, ei toteutuksen hienosäätöä, ja se teki
spektrianalyysin, nopean konvoluution, OFDM:n ja kuvanpakkauksen
käytännölliseksi. Oikeat FFT-kirjastot (NumPyn `pocketfft`, FFTW)
käsittelevät myös muut kuin kahden potenssin pituudet jakamalla pituuden
alkutekijöihin, välttävät rekursion ja hyödyntävät reaalisen datan
symmetriaa. Silti pituus, jolla on vain pieniä alkutekijöitä, on
nopein; alkuluvun pituinen FFT on selvästi hitaampi.

## Käytännössä

- **Ajattele DFT:tä kannanvaihtona.** Kertoimet ovat signaalin
  koordinaatit kompleksisten värähtelyjen ortogonaalisessa kannassa, ja
  käänteismuunnos on liittotranspoosi jaettuna $N$:llä.
- **Muunna indeksit hertseiksi `fftfreq`:llä.** Indeksin $k$ taajuus on
  $k f_s/N$, ja yläpuolisko on negatiivisia taajuuksia.
- **Normita tietoisesti.** NumPyn `fft` ei jaa millään, `ifft` jakaa
  $N$:llä. Fourier-kertoimet saadaan jakamalla $N$:llä, sinin amplitudi
  kaavalla $2|X[k]|/N$ ja jatkuvan muunnoksen likiarvo kertomalla
  $\Delta t$:llä.
- **Käytä `rfft`:tä reaaliselle datalle.** Se laskee vain tarpeelliset
  kertoimet ja on noin kaksi kertaa nopeampi.
- **Älä toteuta FFT:tä itse tuotantokoodiin.** Oma toteutus on hyvä
  oppimiseen ja testaamiseen; kirjasto on nopeampi ja tarkempi.

## Itsearviointi

- Osaat kirjoittaa DFT-matriisin ja osoittaa, että $F^H F = NI$.
- Osaat toteuttaa DFT:n silmukoilla ja matriisitulona ja verrata
  tulosta funktioon `numpy.fft.fft` toleranssilla.
- Osaat selittää, miksi DFT on kannanvaihto ja miksi käänteismuunnos
  ja Parsevalin kaava seuraavat ortogonaalisuudesta.
- Osaat muuntaa DFT-indeksit taajuuksiksi ja selittää FFT:n
  parillinen–pariton-jaon ja sen työmäärän $\frac N2 \log_2 N$.
