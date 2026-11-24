# Lopuksi {.runko-lahteet}

Tutoriaali kävi läpi numeeristen menetelmien ytimen: virheet ja
stabiilisuuden, yhtälöt, interpoloinnin ja sovituksen, derivoinnin ja
integroinnin, lineaariset yhtälöryhmät suorin ja iteratiivisin
menetelmin, differentiaaliyhtälöiden ratkaisijat ja optimoinnin.
Jokaisessa luvussa toistui sama kaava: menetelmällä on kertaluku ja
virhe, virheen voi ennustaa teoriasta ja mitata kokeella, ja
tehtävän ehtoluku asettaa rajan, jota mikään algoritmi ei ylitä.

## Nyrkkisäännöt

1. **Erota tehtävän herkkyys ja algoritmin laatu.** Laske tai arvioi
   ehtoluku. Huonoa tulosta huonokuntoisesta tehtävästä ei korjata
   vaihtamalla algoritmia, vaan muotoilemalla tehtävä uudelleen.
2. **Käytä stabiileja algoritmeja.** Tuenta, QR normaaliyhtälöiden
   sijaan, kaksivaiheinen varianssi, rekursio vakaaseen suuntaan.
3. **Mittaa kertaluku.** Puolita askel tai tuplaa pisteet ja tarkista,
   pieneneekö virhe odotetusti. Poikkeama kertoo virheestä koodissa tai
   puuttuvasta sileydestä.
4. **Käytä kirjastoa, mutta ymmärrä se.** SciPy, LAPACK ja QUADPACK
   ovat vuosikymmenten työn tulosta. Tiedä, mitä ne olettavat, ja lue
   niiden varoitukset ja virhearviot.
5. **Valitse menetelmä rakenteen mukaan.** Symmetrinen ja
   positiivisesti definiitti, harva, jäykkä, sileä, lineaarinen:
   jokaiselle on oma, selvästi parempi menetelmänsä.
6. **Testaa tunnetulla vastauksella ja suhteellisella toleranssilla.**
   Valmistettu ratkaisu (manufactured solution) on numeriikan
   yksikkötesti.

## Python ja Octave rinnakkain

| Tehtävä | NumPy ja SciPy | GNU Octave |
|------------------|-----------------------------|----------------------|
| Juuri välillä | `optimize.brentq(f, a, b)` | `fzero(f, [a b])` |
| Polynomin juuret | `np.roots(c)` | `roots(c)` |
| Yhtälöryhmä | `optimize.root(F, x0)` | `fsolve(F, x0)` |
| Interpolointi | `interpolate.CubicSpline` | `interp1(x, y, t, "spline")` |
| Polynomisovitus | `np.polynomial.Polynomial.fit` | `polyfit`, `polyval` |
| PNS | `np.linalg.lstsq(A, y)` | `A \ y` |
| Integraali | `integrate.quad(f, a, b)` | `integral`, `quadgk` |
| Taulukon integraali | `integrate.trapezoid` | `trapz` |
| Yhtälöryhmä $Ax = b$ | `linalg.solve(A, b)` | `A \ b` |
| Hajotelmat | `linalg.lu`, `cholesky`, `qr`, `svd` | `lu`, `chol`, `qr`, `svd` |
| Ehtoluku | `np.linalg.cond(A)` | `cond(A)`, `rcond(A)` |
| Harva ratkaisu | `sparse.linalg.spsolve`, `cg` | `A \ b`, `pcg` |
| ODE | `integrate.solve_ivp` | `ode45`, `ode15s` |
| Minimointi | `optimize.minimize` | `fminunc`, `fminsearch` |
| Lineaarinen ohjelma | `optimize.linprog`, `milp` | `glpk` |

Kielten suurin ero lukijalle on indeksointi: Octave ja MATLAB
alkavat ykkösestä, ja kertolasku `*` on matriisitulo, kun taas NumPyssä
alkioittainen tulo on `*` ja matriisitulo `@`.

## Mihin tästä jatketaan

- **Differentiaaliyhtälöt ja Laplace-muunnos** soveltaa luvun 8
  ratkaisijoita dynaamisten järjestelmien mallintamiseen.
- **Suorituskyvyn analyysi ja optimointi** ja **GPU-laskenta**
  käsittelevät, miten numeerinen koodi saadaan nopeaksi: välimuistit,
  vektorointi, BLAS ja rinnakkaisuus.
- **Lukujen esitys ja kiinteän pilkun aritmetiikka** ja **Digitaalinen
  signaalinkäsittely** soveltavat virheanalyysiä lukuesityksiin, joissa
  bittejä on vähemmän kuin liukuluvuissa.
- **Analogiaelektroniikka** käyttää SPICE-simulointia, jonka ytimessä
  ovat tämän tutoriaalin Newtonin menetelmä, harvat yhtälöryhmät ja
  jäykät ratkaisijat.
- **Konenäkö (OpenCV)** käyttää pienimmän neliösumman sovitusta, SVD:tä
  ja epälineaarista optimointia kameroiden kalibrointiin.

## Lähteet

Kirjat:

- Higham, N. J. (2002). *Accuracy and Stability of Numerical
  Algorithms*, 2. painos. SIAM. Virheanalyysin perusteos.
- Trefethen, L. N. ja Bau, D. (1997). *Numerical Linear Algebra*.
  SIAM.
- Heath, M. T. (2018). *Scientific Computing: An Introductory
  Survey*, 2. painos (SIAM Classics). Laaja johdanto koko alaan.
- Trefethen, L. N. (2019). *Approximation Theory and Approximation
  Practice*, laajennettu painos. SIAM. Interpolointi ja Tšebyšovin
  menetelmät.
- Hairer, E., Nørsett, S. P. ja Wanner, G. (1993) sekä Hairer, E. ja
  Wanner, G. (1996). *Solving Ordinary Differential Equations* I ja II.
  Springer.
- Nocedal, J. ja Wright, S. J. (2006). *Numerical Optimization*,
  2. painos. Springer.
- Saad, Y. (2003). *Iterative Methods for Sparse Linear Systems*,
  2. painos. SIAM. Kirjoittaja jakaa kirjan verkkosivuillaan.

Artikkelit:

- Goldberg, D. (1991). What every computer scientist should know about
  floating-point arithmetic. *ACM Computing Surveys* 23(1), 5–48.
- Wilkinson, J. H. (1984). The perfidious polynomial. Teoksessa
  *Studies in Numerical Analysis*, MAA Studies in Mathematics 24.
- Welford, B. P. (1962). Note on a method for calculating corrected
  sums of squares and products. *Technometrics* 4(3), 419–420.
- Kahan, W. (1965). Further remarks on reducing truncation errors.
  *Communications of the ACM* 8(1), 40.
- Dormand, J. R. ja Prince, P. J. (1980). A family of embedded
  Runge–Kutta formulae. *Journal of Computational and Applied
  Mathematics* 6(1), 19–26.

Työkalujen dokumentaatio:

- Virtanen, P. ym. (2020). SciPy 1.0: fundamental algorithms for
  scientific computing in Python. *Nature Methods* 17, 261–272.
- *SciPy Documentation*: `scipy.linalg`, `scipy.sparse.linalg`,
  `scipy.integrate`, `scipy.interpolate` ja `scipy.optimize`.
  <https://docs.scipy.org/>
- *NumPy Documentation*. <https://numpy.org/doc/>
- Eaton, J. W. ym. *GNU Octave Manual*. <https://octave.org/doc/>
- Piessens, R. ym. (1983). *QUADPACK: A Subroutine Package for
  Automatic Integration*. Springer.
- Huangfu, Q. ja Hall, J. A. J. (2018). Parallelizing the dual revised
  simplex method. *Mathematical Programming Computation* 10, 119–142
  (HiGHS).
