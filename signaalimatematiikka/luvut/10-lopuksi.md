# Lopuksi {.runko-lahteet}

Tutoriaalin punainen lanka on yksi ajatus kolmessa asussa. Kompleksinen
eksponentti $e^{2\pi i f t}$ on pyörivä nuoli, joka kuvaa yhden
taajuuden. Eri taajuuksien nuolet ovat keskenään ortogonaalisia, joten
ne muodostavat kannan, ja signaalin koordinaatit tässä kannassa ovat
sen Fourier-kertoimet. Lisäksi nuolet kulkevat derivoinnin, viiveen ja
konvoluution läpi muotoaan muuttamatta, joten taajuustasossa nämä
operaatiot ovat kertolaskuja. Fourier-sarja, Fourier-muunnos ja DFT
ovat saman kannanvaihdon versiot jaksolliselle, jaksottomalle ja
diskreetille signaalille.

## Nyrkkisäännöt

| Tilanne | Muista |
|---------|--------|
| kompleksiluvun kulma | `cmath.phase` tai `numpy.angle`, ei `atan(b / a)` |
| vaihe-ero | `cmath.phase(z / w)`, tulos välillä $(-\pi, \pi]$ |
| kertolasku | itseisarvot kerrotaan, kulmat lasketaan yhteen |
| trigonometrinen lauseke | kirjoita eksponentteina $(e^{ix} \pm e^{-ix})/2$ |
| saman taajuuden summa | laske osoittimet yhteen |
| osoittimen mittaus | $2 \cdot$ keskiarvo$(x e^{-2\pi i f t})$ kokonaisten jaksojen yli |
| sinin teho | $A^2/2$, tehollisarvo $A/\sqrt 2$ |
| desibelit | teho $10\log_{10}$, amplitudi $20\log_{10}$ |
| jaksollinen integraali | tasavälisten näytteiden keskiarvo, ei toistettua päätepistettä |
| Fourier-kertoimet | $c_k = \langle x, e_k\rangle$; reaaliselle $c_{-k} = \bar c_k$ |
| terävä reuna | kertoimet $\sim 1/k$, Gibbsin ylitys noin 9 % |
| muunnoksen sopimus | hertsit ($e^{-2\pi ift}$) vai kulmataajuus ($e^{-i\omega t}$) |
| viive | lineaarinen vaihe $-2\pi f t_0$ |
| kapea pulssi | leveä spektri, $\sigma_t\sigma_f \ge 1/(4\pi)$ |
| konvoluutio | taajuustasossa kertolasku |
| FFT-konvoluutio | täytä nollilla pituuteen $N_x + N_h - 1$ |
| DFT-indeksi | taajuus $k f_s/N$, yläpuolisko negatiivinen |
| DFT-normitus | `fft` ei jaa, `ifft` jakaa $N$:llä; amplitudi $2\lvert X[k]\rvert/N$ |
| vertailu | `numpy.allclose` tai toleranssi, ei `==` |

## Jatkotaidot

- *Signaalit ja järjestelmät* rakentaa tämän perustan päälle
  näytteistyksen ja aliasoinnin, diskreettiaikaiset LTI-järjestelmät,
  Z-muunnoksen, navat ja nollat, taajuusvasteen sekä DFT:n käytännön
  kysymykset kuten ikkunoinnin ja vuotamisen.
- *Tietoliikennetekniikka* käyttää osoittimia, modulaatiota, desibelejä
  ja OFDM:n ortogonaalisia alikantoaaltoja. Tämän tutoriaalin luvut 4,
  7 ja 9 selittävät niiden matematiikan.
- *Digitaalinen signaalinkäsittely* jatkaa siitä suodattimien
  suunnitteluun ja toteutukseen.
- *Differentiaaliyhtälöt ja Laplace-muunnos* käsittelee
  Fourier-muunnoksen sukulaisen, Laplace-muunnoksen, sekä jatkuva-aikaisen
  järjestelmän siirtofunktion ja taajuusvasteen.
- *Lineaarialgebra* on edellytys, mutta sen kannanvaihto,
  ortogonaalisuus ja ominaisarvot näkyvät tässä uudessa valossa:
  Fourier-kanta diagonalisoi konvoluution.

## Lähteet ja lisälukemista

- Julius O. Smith III: *Mathematics of the Discrete Fourier Transform
  (DFT) with Audio Applications*, 2. painos. W3K Publishing, 2007.
  Verkossa <https://ccrma.stanford.edu/~jos/mdft/>. Kompleksiluvut,
  Eulerin kaava, osoittimet ja DFT kannanvaihtona.
- Allen B. Downey: *Think DSP: Digital Signal Processing in Python*.
  Green Tea Press, 2016. Avoin kirja (CC BY-NC),
  <https://greenteapress.com/wp/think-dsp/>.
- Steven W. Smith: *The Scientist and Engineer's Guide to Digital Signal
  Processing*. California Technical Publishing, 1997. Verkossa
  <https://www.dspguide.com/>.
- Brad Osgood: *Lectures on the Fourier Transform and Its
  Applications*. American Mathematical Society, 2019. Stanfordin kurssin
  EE261 luentomuistiinpanot ja videot,
  <https://see.stanford.edu/Course/EE261>.
- Alan V. Oppenheim, Alan S. Willsky ja S. Hamid Nawab: *Signals and
  Systems*, 2. painos. Prentice Hall, 1997. MIT OpenCourseWaren kurssi
  6.003 (CC BY-NC-SA).
- Tristan Needham: *Visual Complex Analysis*. Oxford University Press,
  1997. Kompleksilukujen geometria kuvin.
- James W. Cooley ja John W. Tukey: An algorithm for the machine
  calculation of complex Fourier series. *Mathematics of Computation*
  19 (1965), 297–301.
- NumPyn FFT-dokumentaatio,
  <https://numpy.org/doc/stable/reference/routines.fft.html>.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
Lähdeteosten tekstiä ei ole kopioitu; niihin viitataan lisälukemistona.
