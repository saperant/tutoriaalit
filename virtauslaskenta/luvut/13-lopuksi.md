# Lopuksi {.runko-lahteet}

Tutoriaalin ohjelmat ovat muutaman sadan rivin mittaisia, mutta
kysymykset, joihin ne vastasivat, ovat samat kuin teollisessa
virtauslaskennassa. Tämä luku kokoaa ne työnkuluksi ja
tarkistuslistaksi, näyttää, millä nimillä samat valinnat tehdään
valmiissa ohjelmissa, kertoo, mitä rajattiin pois, ja ohjaa eteenpäin.

## Työnkulku

1. **Kysymys.** Mikä suure halutaan ja millä tarkkuudella?
   Painehäviö, pyörteen irtoamistaajuus ja seinän leikkausjännitys
   vaativat eri hilan ja eri mallin.
2. **Dimensiottomat luvut.** Reynoldsin luku kertoo, onko virtaus
   laminaari vai turbulentti ja kuinka ohuita rajakerrokset ovat.
   Machin luku kertoo, saako virtauksen olettaa
   kokoonpuristumattomaksi. Käsilasku antaa suuruusluokan, johon
   tulosta verrataan.
3. **Alue ja reunaehdot.** Reunat niin kauas, etteivät ne vaikuta, ja
   reunaehdoksi se, mikä todella tiedetään. Symmetria käyttöön vain,
   jos virtauskin on symmetrinen.
4. **Hila.** Tiheä siellä, missä ratkaisu muuttuu: rajakerroksissa,
   esteen ympärillä ja vanassa. Turbulenssimalli määrää seinän
   viereisen ruudun koon.
5. **Kaaviot.** Advektiolle toisen kertaluvun rajoitettu kaavio,
   vastavirta korkeintaan alkuun pääsemiseksi. Aika-askel
   Courantin luvusta ja siitä, mitä ajassa halutaan erottaa.
6. **Ajo ja seuranta.** Jäännös ja kiinnostava suure näkyviin. Lasku
   lopetetaan, kun suure on asettunut, ei kun aika loppuu.
7. **Tarkistus.** Tase, kolme hilaa ja virhearvio, reunojen paikan
   kokeilu. Turbulentissa virtauksessa vertailu mittaukseen.
8. **Tulos.** Luku, virhearvio ja oletukset samassa lauseessa.

## Tarkistuslista

Taulukko kokoaa tutoriaalin tarkistukset. Sarake *luku* kertoo, missä
tarkistus tehtiin ensimmäisen kerran tai perusteellisimmin.

| Tarkistus | Mitä se löytää | Luku |
|--------------------|-----------------------|-----|
| kertaluvun mittaus tarkkaa ratkaisua vasten | väärän diskretoinnin, reunaehdon kertaluvun | 1, 4, 7 |
| aineen tai liikemäärän tase | säilymättömän kaavion, vuotavan reunan | 2, 3, 8 |
| ylitykset ja negatiiviset arvot | rajoittamattoman kaavion heilahtelun | 4, 5 |
| hilan Péclet'n tai Reynoldsin luku | keskeiskaavion sahalaidan syyn | 5, 10 |
| vana vinossa hilaan nähden | väärän diffuusion suuruuden | 5 |
| nopeuden divergenssi | painekytkennän ja reunaehtojen virheet | 6, 7 |
| aika-askeleen puolitus | aikavirheen, stabiilisuusrajan läheisyyden | 7 |
| reunan siirtäminen | liian lähelle asetetun sisään- tai ulosvirtauksen | 8 |
| kolme hilaa ja ekstrapolointi | diskretointivirheen suuruuden | 9 |
| sama lasku toisella kaaviolla | kaavion vaimennuksen osuuden tuloksessa | 10 |
| $y^+$ seinillä | turbulenssimallin ja hilan ristiriidan | 11 |
| seurattava suure jäännöksen rinnalla | kesken jääneen iteroinnin | 12 |

Lista ei ole tärkeysjärjestyksessä, mutta kolme tarkistusta kattaa
suurimman osan käytännön virheistä: tase, kolme hilaa ja reunan
siirtäminen. Jos aikaa on vain yhteen, tee laskenta toisella hilalla.

## Samat käsitteet valmiissa ohjelmissa

Avoimista virtauslaskentaohjelmista käytetyimmät ovat OpenFOAM ja
SU2. Kumpaakaan ei tässä ajeta, mutta tutoriaalin käsitteet löytyvät
niiden asetuksista lähes sellaisinaan. Alla olevat nimet ovat
OpenFOAMin, jossa laskenta määritellään tekstitiedostoilla. Nimet
vaihtelevat hieman ohjelman versioiden ja haarojen välillä, joten
tarkka kirjoitusasu kannattaa katsoa oman version ohjeesta.

| Tutoriaalin käsite | OpenFOAMissa | Luku |
|-------------------|------------------------|-----|
| advektiokaavio | `fvSchemes`, kohta `divSchemes` | 4, 5 |
| vastavirta, keskeiskaavio | `upwind`, `linear` | 4 |
| rajoitettu toisen kertaluvun kaavio | `linearUpwind`, `limitedLinear`, `vanLeer` | 4 |
| aikakaavio | `ddtSchemes`: `Euler`, `backward`, `steadyState` | 7 |
| aika-askel ja Courantin luku | `controlDict`: `deltaT`, `maxCo` | 7 |
| annettu arvo, nollagradientti | `fixedValue`, `zeroGradient` | 8 |
| tarttumaton seinä | `noSlip` | 8 |
| takaisinvirtauksen salliva ulosvirtaus | `inletOutlet` | 8 |
| projektio askel kerrallaan | `PISO`, ratkaisija `icoFoam` | 7, 12 |
| tasapainotila alirelaksaatiolla | `SIMPLE`, `relaxationFactors`, ratkaisija `simpleFoam` | 12 |
| paineyhtälön ratkaisija | `fvSolution`: `GAMG` (monihila), `PCG` | 12 |
| vinon verkon korjauskierrokset | `nNonOrthogonalCorrectors` | 12 |
| verkon laadun tarkistus | apuohjelma `checkMesh` | 12 |
| turbulenssimalli | `kEpsilon`, `kOmegaSST` | 11 |
| seinän etäisyys seinäyksiköissä | jälkikäsittelyfunktio `yPlus` | 11 |

Kaksi huomiota taulukosta. Ensinnäkin OpenFOAMin opetusesimerkeistä
ensimmäinen on luvun 9 kansivetoinen onkalo, joten tutoriaalin
tuloksia voi verrata suoraan sen tuloksiin. Toiseksi oletusarvot ja
opetusesimerkkien asetukset eivät ole suosituksia: ne on valittu
niin, että esimerkki suppenee varmasti ja nopeasti, ei sinun
tehtäväsi tarkkuusvaatimuksen mukaan.

SU2 on lähtöisin lentokoneiden aerodynamiikasta ja kokoonpuristuvan
virtauksen laskennasta. Sen asetustiedostossa valitaan samat asiat eri
nimillä: advektiokaavio ja sen rajoitin, Courantin luku, lineaarinen
ratkaisija ja monihilan tasojen määrä sekä reunat merkintöinä, joihin
ehdot liitetään. Kaupalliset ohjelmat, kuten Ansys Fluent ja
Simcenter STAR-CCM+, piilottavat valinnat valikoihin, mutta valinnat
ovat samat.

Yhteistä kaikille on, että ohjelma laskee tuloksen millä tahansa
asetuksilla. Edellisen kohdan tarkistukset ovat käyttäjän vastuulla.

## Mitä jäi pois

Tutoriaali rajautui kokoonpuristumattomaan laminaariin virtaukseen
tasossa. Seuraavat aiheet rakentuvat samalle pohjalle.

- **Kokoonpuristuva virtaus ja shokkiaallot.** Kun Machin luku
  lähestyy yhtä, tiheys muuttuu ja mukaan tulevat energiayhtälö ja
  tilanyhtälö. Paine ei enää ole rajoitteen kerroin vaan
  termodynaaminen suure, ja ääniaallot ovat osa ratkaisua. Shokit
  ovat epäjatkuvuuksia, joiden yli luvun 4 rajoittimet ovat
  välttämättömiä, ja pintojen vuot lasketaan Riemannin tehtävän
  likiratkaisusta.
- **Vapaat pinnat ja monifaasivirtaukset.** Aallot, valut ja kuplat
  vaativat nesteen ja kaasun rajapinnan seuraamista. Yleisin tapa on
  kuljettaa ruutujen täyttöastetta (*volume of fluid*), jolloin
  rajapinnan terävänä pitäminen on luvun 4 advektio-ongelma
  vaikeimmillaan.
- **Lämmönsiirron kytkentä.** Lämpötila kulkeutuu virtauksen mukana
  luvun 5 yhtälöllä. Kytkentä on kaksisuuntainen, kun
  lämpölaajeneminen saa virtauksen liikkeelle (vapaa konvektio) tai
  kun kiinteän kappaleen johtuminen ratkaistaan samassa laskussa.
- **Turbulenssimallien toteutus.** Mallien yhtälöt ovat luvun 5
  advektio–diffuusioyhtälöitä lähdetermein, mutta niiden
  kalibrointi, seinäkäsittely ja pätevyysalueet ovat oma oppiaineensa.
- **Kolme ulottuvuutta ja rinnakkaislaskenta.** Menetelmät yleistyvät
  suoraan, mutta ruutuja on miljoonia, alue jaetaan osiin eri
  suorittimille ja tulosten katselu on oma työvaiheensa.
- **Muut menetelmät.** Hila-Boltzmann-menetelmä laskee virtauksen
  hiukkasjakaumien avulla ja sopii hyvin grafiikkasuorittimille.
  Hiukkasmenetelmät (SPH) seuraavat nestettä ilman hilaa.
  Spektrimenetelmät ovat tarkimpia yksinkertaisissa geometrioissa, ja
  niillä on tehty monet suurimmista suorista simuloinneista.
  Elementtimenetelmää käytetään virtauksiin erityisesti silloin, kun
  virtaus on kytketty rakenteeseen.

## Jatkotaidot

- *GPU-laskenta* näyttää, miten hilakaaviot siirretään
  grafiikkasuorittimelle. Tämän tutoriaalin eksplisiittiset askeleet
  ovat siihen luontevia; paineyhtälön ratkaisija on vaikein osa.
- *Rinnakkaisohjelmointi* antaa perustan alueen jakamiselle
  suorittimien kesken, jolla suuret virtauslaskut tehdään.
- *Pelifysiikka* käsittelee nesteiden ja kappaleiden liikettä
  reaaliajassa. Yhtälöt ovat samat, mutta tavoite on toinen:
  uskottava ja varmasti stabiili liike kiinteässä aikabudjetissa.
- *Suorituskyvyn analyysi ja optimointi* auttaa löytämään, mihin
  ratkaisijan aika kuluu, ennen kuin sitä ryhdytään nopeuttamaan.
- *Python ja C/C++ yhteen* kertoo, miten silmukat, joita NumPyn
  taulukko-operaatiot eivät kata, siirretään käännettyyn kieleen.

## Lähteet

Oppikirjat:

- Ferziger, J. H., Perić, M. ja Street, R. L. (2020). *Computational
  Methods for Fluid Dynamics*, 4. painos. Springer. Alan
  yleisoppikirja; projektiomenetelmä, SIMPLE ja rakenteettomat verkot.
- Versteeg, H. K. ja Malalasekera, W. (2007). *An Introduction to
  Computational Fluid Dynamics: The Finite Volume Method*, 2. painos.
  Pearson. Kontrollitilavuusmenetelmä alusta alkaen.
- Patankar, S. V. (1980). *Numerical Heat Transfer and Fluid Flow*.
  Hemisphere. Hilan Péclet'n luku, porrastettu hila ja SIMPLE.
- LeVeque, R. J. (2002). *Finite Volume Methods for Hyperbolic
  Problems*. Cambridge University Press. Advektiokaaviot, rajoittimet
  ja Godunovin lause.
- Griebel, M., Dornseifer, T. ja Neunhoeffer, T. (1998). *Numerical
  Simulation in Fluid Dynamics: A Practical Introduction*. SIAM.
  Porrastetun hilan ratkaisija ohjelmana.
- Moukalled, F., Mangani, L. ja Darwish, M. (2016). *The Finite Volume
  Method in Computational Fluid Dynamics*. Springer. Menetelmät
  sellaisina kuin OpenFOAM ne toteuttaa.
- Pope, S. B. (2000). *Turbulent Flows*. Cambridge University Press.
  Mittakaavat, seinälaki ja mallien perusteet.
- Briggs, W. L., Henson, V. E. ja McCormick, S. F. (2000). *A
  Multigrid Tutorial*, 2. painos. SIAM.
- Barba, L. A. ja Forsyth, G. F. (2018). CFD Python: the 12 steps to
  Navier–Stokes equations. *Journal of Open Source Education*
  1(9), 21. Avoin kurssi (CC BY), jossa samat yhtälöt ratkaistaan
  differenssimenetelmällä.

Artikkelit:

- Reynolds, O. (1883). An experimental investigation of the
  circumstances which determine whether the motion of water shall be
  direct or sinuous. *Philosophical Transactions of the Royal
  Society* 174, 935–982.
- Courant, R., Isaacson, E. ja Rees, M. (1952). On the solution of
  nonlinear hyperbolic differential equations by finite differences.
  *Communications on Pure and Applied Mathematics* 5(3), 243–255.
  Vastavirtakaavio.
- Godunov, S. K. (1959). A difference method for numerical calculation
  of discontinuous solutions of the equations of hydrodynamics.
  *Matematicheskii Sbornik* 47(89), 271–306. Venäjänkielinen.
- Lax, P. ja Wendroff, B. (1960). Systems of conservation laws.
  *Communications on Pure and Applied Mathematics* 13(2), 217–237.
- van Leer, B. (1974). Towards the ultimate conservative difference
  scheme II. *Journal of Computational Physics* 14(4), 361–370.
  Rajoitin.
- Sweby, P. K. (1984). High resolution schemes using flux limiters for
  hyperbolic conservation laws. *SIAM Journal on Numerical Analysis*
  21(5), 995–1011.
- de Vahl Davis, G. ja Mallinson, G. D. (1976). An evaluation of
  upwind and central difference approximations by a study of
  recirculating flow. *Computers & Fluids* 4(1), 29–43. Väärä
  diffuusio.
- Harlow, F. H. ja Welch, J. E. (1965). Numerical calculation of
  time-dependent viscous incompressible flow of fluid with free
  surface. *Physics of Fluids* 8(12), 2182–2189. Porrastettu hila.
- Chorin, A. J. (1968). Numerical solution of the Navier–Stokes
  equations. *Mathematics of Computation* 22(104), 745–762.
  Projektiomenetelmä.
- Taylor, G. I. ja Green, A. E. (1937). Mechanism of the production of
  small eddies from large ones. *Proceedings of the Royal Society A*
  158(895), 499–521.
- Ghia, U., Ghia, K. N. ja Shin, C. T. (1982). High-Re solutions for
  incompressible flow using the Navier–Stokes equations and a
  multigrid method. *Journal of Computational Physics* 48(3),
  387–411. Onkalovirtauksen vertailutaulukot.
- Roache, P. J. (1994). Perspective: a method for uniform reporting of
  grid refinement studies. *Journal of Fluids Engineering* 116(3),
  405–413.
- Kolmogorov, A. N. (1941). The local structure of turbulence in
  incompressible viscous fluid for very large Reynolds numbers.
  *Doklady Akademii Nauk SSSR* 30, 301–305.
- Patankar, S. V. ja Spalding, D. B. (1972). A calculation procedure
  for heat, mass and momentum transfer in three-dimensional parabolic
  flows. *International Journal of Heat and Mass Transfer* 15(10),
  1787–1806. SIMPLE.
- Issa, R. I. (1986). Solution of the implicitly discretised fluid
  flow equations by operator-splitting. *Journal of Computational
  Physics* 62(1), 40–65. PISO.
- Rhie, C. M. ja Chow, W. L. (1983). Numerical study of the turbulent
  flow past an airfoil with trailing edge separation. *AIAA Journal*
  21(11), 1525–1532.
- Brandt, A. (1977). Multi-level adaptive solutions to boundary-value
  problems. *Mathematics of Computation* 31(138), 333–390.

Työkalut ja ohjelmat:

- Harris, C. R. ym. (2020). Array programming with NumPy. *Nature*
  585, 357–362. <https://numpy.org/doc/>
- Virtanen, P. ym. (2020). SciPy 1.0: fundamental algorithms for
  scientific computing in Python. *Nature Methods* 17, 261–272.
  <https://docs.scipy.org/>
- Weller, H. G., Tabor, G., Jasak, H. ja Fureby, C. (1998). A
  tensorial approach to computational continuum mechanics using
  object-oriented techniques. *Computers in Physics* 12(6), 620–631.
  OpenFOAMin perusta. <https://www.openfoam.com/> ja
  <https://openfoam.org/>
- Economon, T. D., Palacios, F., Copeland, S. R., Lukaczyk, T. W. ja
  Alonso, J. J. (2016). SU2: an open-source suite for multiphysics
  simulation and design. *AIAA Journal* 54(3), 828–846.
  <https://su2code.github.io/>
