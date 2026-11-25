# Lopuksi {.runko-lahteet}

Tutoriaali rakensi yhden ajatuksen ympärille: lineaarinen ja
aikainvariantti järjestelmä on täysin kuvattu impulssivasteellaan, ja
sen Z-muunnos ja taajuusvaste ovat saman asian eri näkymiä. Näytteistys
selitti, milloin jono edustaa jatkuvaa signaalia, ja DFT:n käytännön
luvut, miten spektriä mitataan luotettavasti.

## Nyrkkisäännöt

| Tilanne | Sääntö |
|---------|--------|
| näytetaajuus | $f_s > 2B$ marginaalilla; antialias-suodin ennen näytteistystä |
| harvennus | suodata ensin: `decimate`, ei `x[::q]` |
| kvantisointi | noin 6 dB bittiä kohti |
| LTI-oletus | tarkista: saturaatio, kynnys ja harvennus rikkovat sen |
| stabiilisuus | $\sum\lvert h\rvert < \infty$; kausaalisella suotimella navat $\lvert p\rvert < 1$ |
| suotimen kertoimet | `lfilter(b, a, x)`, normita $a_0 = 1$ |
| korkea-asteinen IIR | toisen asteen lohkot: `output="sos"`, `sosfilt` |
| lohkokäsittely | säilytä tila (`zi`), testaa lohkopituus 1 |
| alkutila | `lfilter_zi` vakaalle signaalille, nollatila levosta |
| EMA | $\alpha = 1 - e^{-T_s/\tau}$; vastaa keskiarvoa $M = (2-\alpha)/\alpha$ |
| taajuusvaste | `freqz(b, a, worN, fs=fs)`, tarkista sinisyötteellä |
| aaltomuoto tärkeä | symmetrinen FIR (lineaarinen vaihe) tai `filtfilt` |
| verkkohäiriö | lovi: nollat yksikköympyrällä, navat säteellä $r < 1$ |
| resoluutio | $\Delta f = 1/(\text{mittausaika})$ |
| vuotaminen | ikkuna (Hann oletuksena), amplitudi $2\lvert X\rvert/\sum w$ |
| nollilla täyttö | tarkentaa huipun paikan, ei erottelukykyä |
| kohinan spektri | Welch, ei yksittäistä periodogrammia |
| pitkä konvoluutio | FFT (`fftconvolve`, `oaconvolve`) |
| testaus | ominaisuudet, referenssi, vaatimukset, rajatapaukset |

## Jatkotaidot

- *Digitaalinen signaalinkäsittely* suunnittelee suotimet, joita tässä
  vain analysoitiin: FIR-ikkunamenetelmä, IIR-suotimet, kertoimien
  kvantisointi, monitaajuuskäsittely ja adaptiiviset suotimet sekä
  lohkopohjainen reaaliaikakäsittely C:llä.
- *Digitaalinen tiedonsiirto* käyttää konvoluutiota, sovitettua suodinta
  ja taajuusvastetta modulaatioissa, pulssinmuokkauksessa ja
  synkronoinnissa.
- *Ohjelmistoradio* soveltaa näytteistystä, desimointia ja
  kompleksisia signaaleja IQ-näytteisiin.
- *DSP-algoritmien laitteistototeutus* toteuttaa luvun 6
  differenssiyhtälöt ja luvun 7 toisen asteen lohkot laitteistona.

## Lähteet ja lisälukemista

- Alan V. Oppenheim ja Ronald W. Schafer: *Discrete-Time Signal
  Processing*, 3. painos. Pearson, 2010. Alan perusteos:
  LTI-järjestelmät, Z-muunnos, näytteistys ja DFT.
- Alan V. Oppenheim, Alan S. Willsky ja S. Hamid Nawab: *Signals and
  Systems*, 2. painos. Prentice Hall, 1997. MIT OpenCourseWaren kurssi
  6.003 (CC BY-NC-SA).
- Julius O. Smith III: *Introduction to Digital Filters with Audio
  Applications*. W3K Publishing, 2007. Verkossa
  <https://ccrma.stanford.edu/~jos/filters/>. Differenssiyhtälöt,
  siirtofunktiot, navat ja nollat sekä taajuusvaste.
- Julius O. Smith III: *Spectral Audio Signal Processing*. W3K
  Publishing, 2011. Verkossa <https://ccrma.stanford.edu/~jos/sasp/>.
  Ikkunat, STFT ja spektrin estimointi.
- Steven W. Smith: *The Scientist and Engineer's Guide to Digital Signal
  Processing*. California Technical Publishing, 1997. Verkossa
  <https://www.dspguide.com/>.
- Richard G. Lyons: *Understanding Digital Signal Processing*,
  3. painos. Prentice Hall, 2010.
- Allen B. Downey: *Think DSP: Digital Signal Processing in Python*.
  Green Tea Press, 2016. Avoin kirja (CC BY-NC),
  <https://greenteapress.com/wp/think-dsp/>.
- Fredric J. Harris: On the use of windows for harmonic analysis with
  the discrete Fourier transform. *Proceedings of the IEEE* 66 (1978),
  51–83.
- Peter D. Welch: The use of fast Fourier transform for the estimation
  of power spectra. *IEEE Transactions on Audio and Electroacoustics*
  15 (1967), 70–73.
- SciPyn signaalinkäsittelyn dokumentaatio,
  <https://docs.scipy.org/doc/scipy/reference/signal.html>.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
Lähdeteosten tekstiä ei ole kopioitu; niihin viitataan lisälukemistona.
