# Lopuksi {.runko-lahteet}

Tutoriaali kävi läpi differentiaali- ja integraalilaskennan ytimen:
raja-arvon ja jatkuvuuden, derivaatan ja sen sovellukset, integraalin ja
sen sovellukset, sarjat ja Taylorin polynomit sekä usean muuttujan
derivaatat ja integraalit. Jokainen tulos laskettiin käsin, symbolisesti
ja numeerisesti, ja eroista opittiin yhtä paljon kuin
yhtäpitävyyksistä.

## Nyrkkisäännöt

1. **Laske ensin ajatuksen tasolla.** Arvioi tuloksen suuruusluokka ja
   etumerkki ennen konetta. Silloin huomaat, kun kone tai kaava vastaa
   väärin.
2. **Tarkista symbolinen tulos toisella tavalla.** Integraalin
   tarkistaa derivoimalla, derivaatan erotusosamäärällä ja kaavan
   toisella ohjelmalla.
3. **Epäile vähennyslaskua ja pientä askelta.** Kumoutuminen pilaa
   numeeriset raja-arvot ja derivaatat. Paras askel on kompromissi
   katkaisu- ja pyöristysvirheen välillä.
4. **Käytä kirjastoa ja lue sen virhearvio.** `brentq`, `quad` ja
   `minimize` ovat tarkempia ja luotettavampia kuin oma toteutus, ja ne
   kertovat, kuinka paljon tulokseen voi luottaa.
5. **Tunne approksimaatioiden rajat.** Linearisointi, Taylorin
   polynomi ja pienen kulman kaavat ovat hyviä vain kehityskohdan
   lähellä. Kirjoita pätevyysalue näkyviin.
6. **Pidä yksiköt mukana.** Derivaatan yksikkö on osamäärä, integraalin
   yksikkö tulo. Yksikkötarkistus löytää monta virhettä ennen kuin ne
   päätyvät tuloksiin.

## Työkalut rinnakkain

| Tehtävä | SymPy | Maxima | NumPy ja SciPy |
|------------------|-------------------------|-------------------------|-------------------|
| Raja-arvo | `limit(f, x, a, "+")` | `limit(f, x, a, plus)` | (vain kokeilu) |
| Derivaatta | `diff(f, x, n)` | `diff(f, x, n)` | `np.gradient` |
| Implisiittinen | `idiff(F, y, x)` | `depends`, `diff`, `solve` | (ei) |
| Juuri | `nsolve` | `find_root` | `optimize.brentq` |
| Integraali | `integrate(f, (x, a, b))` | `integrate(f, x, a, b)` | `integrate.quad` |
| Näytteiden integraali | (ei) | (ei) | `trapezoid`, `simpson` |
| Osamurrot | `apart` | `partfrac` | (ei) |
| Sarja | `summation`, `series` | `sum`, `taylor` | (ei) |
| Gradientti ja Hessen | `Matrix.jacobian`, `hessian` | `diff`, `hessian` | `optimize.minimize` |
| Rajoitettu optimi | `solve` Lagrangen ehdoille | `solve` | `minimize`, SLSQP |
| Kaksoisintegraali | sisäkkäinen `integrate` | sisäkkäinen `integrate` | `integrate.dblquad` |

## Jatkotaidot

- *Differentiaaliyhtälöt ja Laplace-muunnos* käyttää derivaattoja ja
  integraaleja dynaamisten järjestelmien mallintamiseen: värähtelijät,
  sähköpiirit ja säätö.
- *Numeeriset menetelmät* syventää tämän tutoriaalin numeerisia
  osuuksia: virhekertaluvut, adaptiiviset menetelmät, yhtälöryhmät ja
  optimointi.
- *Analogiaelektroniikka* ja *Elektroniikan perusteet ja SPICE*
  soveltavat derivaattaa ja integraalia kondensaattoreihin, keloihin ja
  vahvistimiin.
- *Kompleksiluvut ja Fourier-analyysi* jatkaa sarjoista
  Fourier-sarjoihin ja -muunnokseen.
- *Todennäköisyys ja tilastot* käyttää integraaleja jatkuvien
  jakaumien käsittelyyn.

## Lähteet

Avoimet oppikirjat (lisenssi CC BY-NC-SA 4.0 tai CC BY 4.0):

- Strang, G. ja Herman, E. (2016). *Calculus*, osat 1–3. OpenStax.
  <https://openstax.org/>
- Guichard, D. *Calculus: Early Transcendentals*. Whitman College.
  Avoin oppikirja, CC BY-NC-SA.

Työkalujen dokumentaatio:

- SymPy Development Team. *SymPy Documentation*, erityisesti osat
  Calculus, Series ja Integrals. <https://docs.sympy.org/>
- Virtanen, P. ym. (2020). SciPy 1.0: fundamental algorithms for
  scientific computing in Python. *Nature Methods* 17, 261–272.
- *SciPy Documentation*: `scipy.integrate` ja `scipy.optimize`.
  <https://docs.scipy.org/>
- *Maxima Manual*. Maxima-projekti. <https://maxima.sourceforge.io/>
- Piessens, R. ym. (1983). *QUADPACK: A Subroutine Package for
  Automatic Integration*. Springer. (SciPyn `quad` ja Maximan
  `quad_qags`.)

Numeriikka:

- Goldberg, D. (1991). What every computer scientist should know about
  floating-point arithmetic. *ACM Computing Surveys* 23(1), 5–48.
- Higham, N. J. (2002). *Accuracy and Stability of Numerical
  Algorithms*, toinen painos. SIAM. (Erotusosamäärän askeleen valinta ja
  kumoutuminen.)
- Muller, J.-M. (2016). *Elementary Functions: Algorithms and
  Implementation*, kolmas painos. Birkhäuser. (Välin supistus ja
  kirjastofunktioiden toteutus.)
- Nocedal, J. ja Wright, S. J. (2006). *Numerical Optimization*, toinen
  painos. Springer. (Gradienttimenetelmä ja BFGS.)

Kaikki tämän tutoriaalin työkalut ovat avointa lähdekoodia: SymPy (BSD),
NumPy (BSD), SciPy (BSD), Matplotlib (PSF-pohjainen) ja Maxima (GPL).
