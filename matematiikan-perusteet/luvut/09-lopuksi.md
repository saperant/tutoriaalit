# Lopuksi {.runko-lahteet}

Tutoriaali kertasi lukion pitkän matematiikan keskeiset sisällöt ja
opetti samalla neljä työkalua. Tärkein opittava asia ei ole yksittäinen
komento vaan työtapa: laske ensin ajatuksen tasolla, tarkista koneella ja
epäile tulosta, joka näyttää liian siistiltä tai liian sotkuiselta.

## Nyrkkisäännöt

1. **Tarkista käsinlasku erotuksella.** Kaksi lauseketta ovat samat, jos
   niiden erotus sievenee nollaksi. Yhtälön ratkaisu tarkistetaan
   sijoittamalla.
2. **Tarkat luvut ensin, likiarvot lopuksi.** `sp.Rational`, `sp.sqrt` ja
   `sp.pi` pysyvät tarkkoina; `evalf` ja `float` vasta tulostettaessa.
3. **Ei `==`-vertailua liukuluvuille.** Toleranssi, kuten `math.isclose`.
4. **Määrittelyehdot ja oletukset näkyviin.** Nimittäjät, juuret ja
   logaritmit rajoittavat määrittelyjoukkoa, ja symbolin oletukset
   (`positive=True`) ohjaavat sievennystä.
5. **Kaava on oikein vasta, kun se on tarkistettu kahdella tavalla.**
   Symbolinen ja numeerinen, SymPy ja Maxima tai kaava ja simulaatio.
6. **Epäile kuvaajaa.** Liian harva näytteistys ja asymptootit
   tuottavat kuvaajia, jotka näyttävät uskottavilta mutta ovat vääriä.
7. **Numeeriset menetelmät tarvitsevat ehdot.** Puolitushaku vaatii
   merkinvaihdon; tarkista ehto ja ilmoita, jos se ei täyty.

## Työkalut rinnakkain

| Tehtävä | SymPy | Maxima | NumPy / Matplotlib |
|---------|-------|--------|--------------------|
| Symboli | `x = sp.symbols("x")` | (automaattinen) | (ei symboleja) |
| Tarkka luku | `sp.Rational(1, 3)` | `1/3` | `fractions.Fraction(1, 3)` |
| Sievennys | `simplify`, `factor` | `ratsimp`, `factor` | (ei) |
| Yhtälö | `solve`, `solveset` | `solve` | `np.roots` (polynomit) |
| Numeerinen juuri | `nsolve` | `find_root` | `scipy.optimize.brentq` |
| Funktion arvot | `lambdify` | `float(f(2))` | `y = f(x)` taulukolle |
| Kuvaaja | (`sp.plot`) | `plot2d` | `ax.plot`, `savefig` |
| Eräajo | `python3 skripti.py` | `maxima -b skripti.mac` | `python3 skripti.py` |

## Jatkotaidot

- *Differentiaali- ja integraalilaskenta* jatkaa suoraan funktioista:
  raja-arvo, derivaatta, integraali ja sarjat samoilla työkaluilla.
- *Elektroniikan perusteet ja SPICE* käyttää yhtälöitä, eksponentti-
  funktiota ja trigonometriaa sähköpiirien laskentaan ja simulointiin.
- *Lineaarialgebra* yleistää tason vektorit ja yhtälöparit matriiseiksi.
- *Kompleksiluvut ja Fourier-analyysi* jatkaa harmonisesta
  värähtelystä osoittimiin ja Fourier-sarjoihin.
- *Numeeriset menetelmät* ja *Differentiaaliyhtälöt ja
  Laplace-muunnos* käyttävät myös GNU Octavea.

## Lähteet

Työkalujen dokumentaatio:

- SymPy Development Team. *SymPy Documentation*.
  <https://docs.sympy.org/>
- Meurer, A. ym. (2017). SymPy: symbolic computing in Python.
  *PeerJ Computer Science* 3:e103.
- *Maxima Manual*. Maxima-projekti. <https://maxima.sourceforge.io/>
- *NumPy Documentation*. <https://numpy.org/doc/>
- *Matplotlib Documentation*. <https://matplotlib.org/>
- Eaton, J. W. ym. *GNU Octave Manual*. <https://octave.org/doc/>
- Python Software Foundation. *fractions* ja *decimal*, Pythonin
  standardikirjaston dokumentaatio. <https://docs.python.org/3/>

Matematiikka:

- Abramson, J. ym. (2021). *Precalculus 2e*. OpenStax. Avoin oppikirja,
  lisenssi CC BY 4.0. <https://openstax.org/>
- Lukion opetussuunnitelman perusteet 2019, matematiikan pitkä oppimäärä.
  Opetushallitus. <https://www.oph.fi/>

Numeriikka ja sovellukset:

- Goldberg, D. (1991). What every computer scientist should know about
  floating-point arithmetic. *ACM Computing Surveys* 23(1), 5–48.
- Higham, N. J. (2002). *Accuracy and Stability of Numerical
  Algorithms*, toinen painos. SIAM. (Kumoutuminen ja toisen asteen yhtälön vakaa ratkaisu.)
- Ericson, C. (2005). *Real-Time Collision Detection*. Morgan Kaufmann.
  (Jatkuva törmäyksen tunnistus.)

Kaikki tämän tutoriaalin työkalut ovat avointa lähdekoodia: SymPy (BSD),
Maxima (GPL), NumPy (BSD), Matplotlib (PSF-pohjainen) ja GNU Octave
(GPL).
