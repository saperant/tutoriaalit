# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

| Tilanne | Muista |
|---------|--------|
| matriisin merkitys | sarakkeet ovat kantavektorien kuvat |
| yhdistetty kuvaus | $AB$: ensin $B$, sitten $A$ |
| yhtälöryhmä | `np.linalg.solve`, ei `inv` |
| sama matriisi, monta oikeaa puolta | LU kerran, sijoitukset monta kertaa |
| symmetrinen positiivisesti definiitti | Cholesky |
| harva matriisi | `scipy.sparse`, älä muodosta tiheänä |
| singulaarisuus | ehtoluku tai aste, ei determinantti |
| kierron käänteismatriisi | transpoosi |
| kertyvät kierrot | ortogonalisoi tai normalisoi kvaternio säännöllisesti |
| datan sovitus | `lstsq` (QR tai SVD), ei normaaliyhtälöitä |
| riippuvat sarakkeet, aste | singulaariarvot (`svd`, `matrix_rank`, `pinv`) |
| tiivistäminen | $k$ suurinta singulaariarvoa on paras asteen $k$ approksimaatio |
| ylisovitus | arvioi testidatalla, ei opetusdatalla |
| ominaisarvot | `eigh` symmetrisille, `eig` muille |
| PCA | keskitä ja skaalaa ensin |
| grafiikka | pisteillä $w = 1$, suunnilla $w = 0$ |
| tarkkuus | $\kappa \approx 10^k$ vie noin $k$ numeroa |
| vertailu | `np.allclose`, ei `==` |

## Jatkotaidot

- *Numeeriset menetelmät* jatkaa siitä, mihin luku *Numeeriset
  näkökohdat* jää: virherajat ehtoluvusta ja jäännöksestä, harvojen
  matriisien iteratiiviset ratkaisijat, interpolointi ja
  regularisoitu sovitus.
- *Differentiaaliyhtälöt ja Laplace-muunnos* käyttää ominaisarvoja
  yhtälöryhmien ratkaisemiseen ja stabiilisuuden arviointiin.
- *Kompleksiluvut ja Fourier-analyysi* jatkaa kompleksiluvuilla ja
  Fourier-muunnoksella, joka on kannanvaihto taajuuksien kantaan.
- *Todennäköisyys ja tilastot* antaa kovarianssimatriisille ja
  pienimmän neliösumman sovitukselle tilastollisen tulkinnan, ja
  *Signaalit ja järjestelmät* käsittelee lineaarisia järjestelmiä.
- *Renderöinnin perusteet* rakentaa homogeenisten koordinaattien ja
  kameramatriisien päälle rasteroinnin, syvyyspuskurin ja valaistuksen.
  *GPU-ohjelmointi: OpenGL ja Vulkan* vie ne näytönohjaimelle, ja
  *Peliohjelmointi* käyttää vektoreita fysiikassa ja törmäyksissä.
- *Miten tietokone laskee* näyttää, miten matriisit tallennetaan
  muistiin ja miksi BLAS on niin paljon nopeampi kuin oma silmukka.

## Lähteet ja lisälukemista

- Jim Hefferon: *Linear Algebra*. Avoin oppikirja (GFDL tai CC BY-SA),
  <https://hefferon.net/linearalgebra/>.
- Robert A. Beezer: *A First Course in Linear Algebra*. Avoin
  oppikirja (GFDL), <http://linear.ups.edu/>.
- Gilbert Strang: *Introduction to Linear Algebra*, 6. painos.
  Wellesley-Cambridge Press, 2023. MIT OpenCourseWaren kurssi 18.06
  videoineen, <https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/>
  (CC BY-NC-SA).
- Lloyd N. Trefethen ja David Bau: *Numerical Linear Algebra*. SIAM,
  1997. Ehtoluvut, stabiilisuus, QR, SVD ja ominaisarvoalgoritmit.
- Gene H. Golub ja Charles F. Van Loan: *Matrix Computations*,
  4. painos. Johns Hopkins University Press, 2013.
- Nicholas J. Higham: *Accuracy and Stability of Numerical
  Algorithms*, 2. painos. SIAM, 2002.
- NumPyn lineaarialgebran dokumentaatio,
  <https://numpy.org/doc/stable/reference/routines.linalg.html>, ja
  SciPyn `scipy.linalg` ja `scipy.sparse.linalg`.
- LAPACK Users' Guide, <https://www.netlib.org/lapack/lug/>.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
Lähdeteosten tekstiä ei ole kopioitu; niihin viitataan lisälukemistona.
