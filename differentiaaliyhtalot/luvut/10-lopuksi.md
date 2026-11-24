# Lopuksi {.runko-lahteet}

Tutoriaali kävi läpi differentiaaliyhtälöt insinöörin näkökulmasta:
mallintamisen taseista, ensimmäisen ja toisen kertaluvun yhtälöt,
yhtälöryhmät ja tilaesityksen, Laplace-muunnoksen ja siirtofunktion,
stabiilisuuden sekä numeeriset ratkaisijat. Jokainen tulos laskettiin
vähintään kahdella tavalla, ja eroista opittiin yhtä paljon kuin
yhtäpitävyyksistä.

## Nyrkkisäännöt

1. **Malli on tase.** Muutos = sisään − ulos. Tarkista yksiköt ennen
   kuin ratkaiset mitään.
2. **Etsi aikavakio ja ominaistaajuus.** Ne kertovat, kuinka nopeasti
   järjestelmä reagoi ja värähteleekö se, usein ilman ratkaisua.
3. **Navat ja ominaisarvot ovat järjestelmän sormenjälki.** Reaaliosa
   kertoo vaimenemisen, imaginaariosa värähtelyn ja merkki
   stabiilisuuden.
4. **Lineaariselle yhtälölle Laplace, epälineaariselle simulointi.**
   Analyyttinen ratkaisu kertoo rakenteen; numeerinen toimii aina.
5. **Tarkista ratkaisu toisella menetelmällä.** Sijoitus yhtälöön,
   toinen ohjelma, tunnettu erikoistapaus tai tiukempi toleranssi.
6. **Varo jäykkyyttä ja kriittisiä parametreja.** Kumpikin muuttaa
   numeerisen tai laadullisen tuloksen huomaamatta.

## Työkalut rinnakkain

| Tehtävä | SymPy ja SciPy | Maxima | Octave |
|---------|----------------|--------|--------|
| yleinen ratkaisu | `sp.dsolve` | `ode2` | (ei) |
| alkuehdot | `dsolve(..., ics=...)` | `ic1`, `ic2` | (ei) |
| tarkistus | `sp.checkodesol` | sijoitus `ev` | (ei) |
| Laplace | `laplace_transform` | `laplace`, `ilt` | (ei peruspaketissa) |
| osamurrot | `sp.apart` | `partfrac` | `residue` |
| alkuarvotehtävä Laplacella | `apart` + `inverse_laplace_transform` | `desolve` | (ei) |
| ominaisarvot | `Matrix.eigenvals`, `np.linalg.eig` | `eigenvalues` | `eig` |
| matriisieksponentti | `Matrix.exp`, `scipy.linalg.expm` | `matrixexp` (linearalgebra) | `expm` |
| numeerinen ratkaisu | `solve_ivp` | (ei) | `ode45`, `ode23s`, `ode15s` |
| siirtofunktio | `scipy.signal.lti`, `step`, `freqs` | (ei) | `roots`, (control-paketti) |

Octaven `control`-paketti (Octave Forge) tarjoaa MATLABin Control System
Toolboxin kaltaiset `tf`-, `step`- ja `bode`-funktiot. Sitä ei käytetä
tässä tutoriaalissa, koska se ei kuulu Octaven peruspakettiin.

## Mihin tästä jatketaan

- **Numeeriset menetelmät** analysoi ratkaisijoiden virheet,
  kertaluvut, vakausalueet ja adaptiivisen askeleen.
- **Analogiaelektroniikka** käyttää siirtofunktioita, navoja ja
  takaisinkytkentää vahvistimiin ja suodattimiin.
- **Signaalit ja järjestelmät** ja **Digitaalinen signaalinkäsittely**
  käsittelevät samaa teoriaa diskreetissä ajassa Z-muunnoksella.
- **Elektroniikan perusteet ja SPICE** simuloi tämän tutoriaalin RC- ja
  RLC-piirejä piirisimulaattorilla.

## Lähteet

Avoimet oppikirjat:

- Lebl, J. *Notes on Diffy Qs: Differential Equations for Engineers*.
  Avoin oppikirja, CC BY-SA 4.0. <https://www.jirka.org/diffyqs/>
- Trench, W. F. *Elementary Differential Equations*. Trinity
  University, avoin oppikirja (CC BY-NC-SA 3.0).
- Åström, K. J. ja Murray, R. M. (2021). *Feedback Systems: An
  Introduction for Scientists and Engineers*, 2. painos. Princeton
  University Press; tekijöiden verkkoversio vapaasti luettavissa.

Työkalujen dokumentaatio:

- SymPy Development Team. *SymPy Documentation*, osat ODE ja Integral
  Transforms. <https://docs.sympy.org/>
- Virtanen, P. ym. (2020). SciPy 1.0: fundamental algorithms for
  scientific computing in Python. *Nature Methods* 17, 261–272.
- *SciPy Documentation*: `scipy.integrate.solve_ivp` ja `scipy.signal`.
  <https://docs.scipy.org/>
- Eaton, J. W. ym. *GNU Octave Manual*, luku Differential Equations.
  <https://octave.org/doc/>
- *Maxima Manual*, luvut Differential Equations ja Laplace.
  <https://maxima.sourceforge.io/>

Menetelmät:

- Dormand, J. R. ja Prince, P. J. (1980). A family of embedded
  Runge–Kutta formulae. *Journal of Computational and Applied
  Mathematics* 6(1), 19–26.
- Hairer, E. ja Wanner, G. (1996). *Solving Ordinary Differential
  Equations II: Stiff and Differential-Algebraic Problems*, 2. painos.
  Springer.
