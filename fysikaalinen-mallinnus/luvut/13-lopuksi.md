# Lopuksi {.runko-lahteet}

Tutoriaalin menetelmät vaihtuivat luvusta toiseen, mutta työnkulku
pysyi samana. Tämä luku kokoaa sen tarkistuslistaksi, kertoo, mitä
rajattiin pois, ja ohjaa eteenpäin.

## Työnkulku

1. **Kysymys.** Mikä suure halutaan ja millä tarkkuudella? Suurin
   lämpötila, pään taipuma ja alin ominaistaajuus vaativat eri mallin
   ja eri verkon.
2. **Käsilasku.** Suuruusluokka dimensiottomista luvuista ja
   yksinkertaisista kaavoista: $L^2/\alpha$, palkkiteoria,
   lämpövastukset. Jos Biot'n luku on pieni tai rakenne on palkki,
   malli voi olla valmis tässä.
3. **Malli.** Tase, aineen laki, reunaehdot, oletukset kirjattuina.
   Symmetria käyttöön.
4. **Diskretointi.** Säännöllinen alue ja yksinkertainen fysiikka:
   differenssimenetelmä. Mutkikas geometria tai rakenne:
   elementtimenetelmä, toisen asteen elementit, verkko tiheämmäksi
   siellä, missä ratkaisu muuttuu.
5. **Ratkaisu.** Diffuusio implisiittisesti, aallot eksplisiittisesti
   CFL-ehdon sisällä, tasapaino suoralla harvalla ratkaisijalla.
6. **Tarkistus.** Tase, symmetria, vertailu käsilaskuun. Kolme verkkoa
   ja virhearvio. Singulaariset suureet tunnistetaan ja jätetään
   raportoimatta.
7. **Tulos.** Luku, virhearvio ja oletukset samassa lauseessa.

## Tarkistukset koottuna

| Tarkistus | Mitä se löytää | Luku |
|---|---|---|
| kertaluvun mittaus tarkkaa ratkaisua vasten | väärän diskretoinnin, reunaehdon kertaluvun | 1, 3, 6, 7 |
| energia- tai voimatase | puuttuvat termit, väärät reunajoukot, yksikkövirheet | 2, 7, 10 |
| symmetria ja superpositio | kokoamis- ja indeksivirheet | 3 |
| stabiilisuusrajan koe | väärän aika-askeleen, väärän kaavion | 4, 5 |
| säilyvä suure (energia) ajassa | epästabiiliuden, numeerisen vaimennuksen | 5 |
| paikkatesti | elementtimatriisin ja numeroinnin virheet | 7 |
| kaksi riippumatonta toteutusta | työkalun väärän käytön | 7, 8, 9 |
| kirjallisuuden viitearvo | koko ketjun virheet vakiotehtävässä | 10 |
| valmistettu ratkaisu | minkä tahansa termin virheen ilman tarkkaa ratkaisua | 12 |
| kolme verkkoa ja ekstrapolointi | diskretointivirheen suuruuden, singulaariset suureet | 12 |
| ennuste uudessa tilanteessa | mallin muodon virheen | 12 |

## Mitä jäi pois

Tutoriaali rajautui lineaarisiin tehtäviin tasossa. Seuraavat aiheet
rakentuvat samalle pohjalle.

- **Kolme ulottuvuutta.** Kolmion tilalla on tetraedri ja nelikulmion
  tilalla heksaedri. Periaatteet ovat samat, mutta verkotus on
  vaikeampaa, tuntemattomia on miljoonia ja iteratiiviset ratkaisijat
  esiehdostimineen ovat välttämättömiä.
- **Epälineaarisuus.** Aineen ominaisuudet riippuvat ratkaisusta
  (lämpötilasta riippuva johtavuus, plastisuus), siirtymät ovat suuria
  tai kappaleet koskettavat toisiaan. Yhtälöryhmä ratkaistaan
  Newtonin menetelmällä, jonka jokainen askel on yksi tämän
  tutoriaalin lineaarinen tehtävä. Luvun 12 säteilyllä jäähtyvä tanko
  oli tällainen.
- **Rakenne-elementit.** Palkit, laatat ja kuoret mallinnetaan
  elementeillä, joiden vapausasteina ovat myös kiertymät. Ne ovat
  ohuille rakenteille paljon tehokkaampia kuin luvun 9 tasomalli.
- **Kytketyt ilmiöt.** Lämpö aiheuttaa jännityksiä, virta lämmittää
  johdinta, neste kuormittaa rakennetta. Ilmiöt ratkaistaan yhdessä
  tai vuorotellen.
- **Kaupalliset ja suuret avoimet ohjelmistot.** Ansys, Abaqus ja
  COMSOL sekä avoimet FEniCS, deal.II, Elmer ja CalculiX toteuttavat
  tämän tutoriaalin menetelmät teollisessa mittakaavassa. Niiden
  käytössä vaikeinta ei ole käyttöliittymä vaan luvun 12 kysymykset.

## Jatkotaidot

- *Virtauslaskenta* jatkaa suoraan tästä: säilymislait virtaavalle
  aineelle, advektio, kontrollitilavuusmenetelmä ja Navier–Stokesin
  yhtälöt.
- *Pelifysiikka* käsittelee samoja liikeyhtälöitä toisesta suunnasta:
  jäykät kappaleet, rajoitteet ja pehmeät kappaleet reaaliajassa,
  jossa stabiilisuus ja nopeus menevät tarkkuuden edelle.
- *GPU-laskenta* ja *Rinnakkaisohjelmointi* kertovat, miten suuret
  simulaatiot saadaan nopeiksi. Luvun 5 eksplisiittiset hilakaaviot
  ovat grafiikkasuorittimelle luontevimpia tehtäviä.
- *Analogiaelektroniikka* käyttää piirisimulaattoria, joka ratkaisee
  jäykkiä yhtälöryhmiä samoilla implisiittisillä menetelmillä kuin
  luku 4.
- *Suorituskyvyn analyysi ja optimointi* auttaa, kun kokoamissilmukka
  tai ratkaisija on liian hidas.

## Lähteet

Oppikirjat:

- LeVeque, R. J. (2007). *Finite Difference Methods for Ordinary and
  Partial Differential Equations*. SIAM. Lukujen 3–5 teoria.
- Langtangen, H. P. ja Linge, S. (2017). *Finite Difference Computing
  with PDEs: A Modern Software Approach*. Springer. Avoimesti saatavilla
  (CC BY).
- Hughes, T. J. R. (2000). *The Finite Element Method: Linear Static
  and Dynamic Finite Element Analysis*. Dover.
- Johnson, C. (2009). *Numerical Solution of Partial Differential
  Equations by the Finite Element Method*. Dover.
- Larson, M. G. ja Bengzon, F. (2013). *The Finite Element Method:
  Theory, Implementation, and Applications*. Springer.
- Cook, R. D., Malkus, D. S., Plesha, M. E. ja Witt, R. J. (2002).
  *Concepts and Applications of Finite Element Analysis*, 4. painos.
  Wiley. Rakenteiden laskennan käytännöt, lukkiutuminen.
- Incropera, F. P., DeWitt, D. P., Bergman, T. L. ja Lavine, A. S.
  (2011). *Fundamentals of Heat and Mass Transfer*, 7. painos. Wiley.
  Lämmönsiirron mallit ja dimensiottomat luvut.
- Timoshenko, S. P. ja Goodier, J. N. (1970). *Theory of
  Elasticity*, 3. painos. McGraw-Hill. Reikälevyn ja palkin tarkat
  ratkaisut.
- Oberkampf, W. L. ja Roy, C. J. (2010). *Verification and Validation
  in Scientific Computing*. Cambridge University Press.

Artikkelit:

- Courant, R., Friedrichs, K. ja Lewy, H. (1928). Über die partiellen
  Differenzengleichungen der mathematischen Physik. *Mathematische
  Annalen* 100, 32–74. CFL-ehto.
- Crank, J. ja Nicolson, P. (1947). A practical method for numerical
  evaluation of solutions of partial differential equations of the
  heat-conduction type. *Proceedings of the Cambridge Philosophical
  Society* 43(1), 50–67.
- Kirsch, E. G. (1898). Die Theorie der Elastizität und die
  Bedürfnisse der Festigkeitslehre. *Zeitschrift des Vereines
  deutscher Ingenieure* 42, 797–807.
- Babuška, I. ja Aziz, A. K. (1976). On the angle condition in the
  finite element method. *SIAM Journal on Numerical Analysis* 13(2),
  214–226.
- Fox, L., Henrici, P. ja Moler, C. (1967). Approximations and bounds
  for eigenvalues of elliptic operators. *SIAM Journal on Numerical
  Analysis* 4(1), 89–102. L-alueen ominaisarvot.
- Betcke, T. ja Trefethen, L. N. (2005). Reviving the method of
  particular solutions. *SIAM Review* 47(3), 469–491. L-alueen
  ominaisarvojen tarkat lukuarvot.
- Roache, P. J. (1994). Perspective: a method for uniform reporting of
  grid refinement studies. *Journal of Fluids Engineering* 116(3),
  405–413. Verkkosuppenemisindeksi.
- Roache, P. J. (2002). Code verification by the method of
  manufactured solutions. *Journal of Fluids Engineering* 124(1),
  4–10.

Työkalut:

- Gustafsson, T. ja McBain, G. D. (2020). scikit-fem: A Python package
  for finite element assembly. *Journal of Open Source Software*
  5(52), 2369. <https://scikit-fem.readthedocs.io/>
- Virtanen, P. ym. (2020). SciPy 1.0: fundamental algorithms for
  scientific computing in Python. *Nature Methods* 17, 261–272.
  <https://docs.scipy.org/>
- Meurer, A. ym. (2017). SymPy: symbolic computing in Python. *PeerJ
  Computer Science* 3, e103.
- Geuzaine, C. ja Remacle, J.-F. (2009). Gmsh: a 3-D finite element
  mesh generator with built-in pre- and post-processing facilities.
  *International Journal for Numerical Methods in Engineering*
  79(11), 1309–1331. <https://gmsh.info/>
