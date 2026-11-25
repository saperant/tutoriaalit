# Lopuksi {.runko-lahteet}

Tutoriaalin moottori on noin tuhat riviä, ja siitä puuttuu paljon.
Sen rakenne on silti sama kuin tuotantomoottoreissa, ja niiden
asetukset ovat tuttuja, kun tietää, mitä alla tapahtuu. Tämä luku
kertoo, millä nimillä käsitteet löytyvät neljästä yleisestä
moottorista, kokoaa nyrkkisäännöt ja ohjaa eteenpäin.

## Samat osat fysiikkamoottorissa

Jokainen moottori etenee askeleessa samassa järjestyksessä kuin
luvun 9 kaavio: voimat nopeuksiin, laaja vaihe, kapea vaihe,
ratkaisija, paikkojen integrointi ja lepotila. Erot ovat siinä, mitä
muotoja tuetaan, miten ratkaisija iteroi ja kuinka työ jaetaan
säikeille.

| Käsite | Box2D (2D) | Bullet | Jolt | PhysX |
|-------------|-------------|--------------------|-----------------|----------------|
| kappale | `b2Body` | `btRigidBody` | `Body` | `PxRigidDynamic` |
| törmäysmuoto | `b2Shape` | `btCollisionShape` | `Shape` | `PxShape` |
| laaja vaihe | AABB-puu | AABB-puu | nelipuu | lajittelu, ruudukko |
| monisto | `b2Manifold` | `btPersistentManifold` | `ContactManifold` | kosketusparit |
| ratkaisija | impulssit ja aliaskeleet | peräkkäiset impulssit | peräkkäiset impulssit | PGS tai TGS |
| nivel | `b2Joint` | `btTypedConstraint` | `Constraint` | `PxJoint` |
| lepotila | saaret | saaret | saaret | saaret |
| nopea kappale | *bullet*-lippu | CCD-kynnys | `LinearCast` | CCD-lippu |
| pehmeät | ei | `btSoftBody` | XPBD | FEM ja PBD |

: Tämän tutoriaalin käsitteet neljässä moottorissa. Nimet ovat
moottorien pääluokkia, eivät täydellisiä rajapintoja.

Muutama asetus toistuu kaikissa, ja jokaisella on vastine tässä
tutoriaalissa:

- **Nopeus- ja sijainti-iteraatiot** ovat ratkaisijan kierrokset
  (luku 7). Uudemmat moottorit tarjoavat niiden tilalle tai rinnalle
  aliaskeleet.
- **Kosketusmarginaali** (*contact offset*, *speculative distance*)
  on luvun 7 marginaali: etäisyys, jolta kosketus luodaan ennen kuin
  pinnat koskevat.
- **Sallittu tunkeuma** (*slop*, *penetration slop*) ja **Baumgarten
  kerroin** tai sen pehmeä vastine (*contact hertz*, *damping ratio*)
  säätävät sijainnin korjausta.
- **Lepokynnys ja lepoaika** säätävät nukahtamista (luku 9).
- **Liikkeen laatu** tai CCD-lippu valitsee jatkuvan
  törmäystunnistuksen kappalekohtaisesti (luku 10).
- **Törmäyskerrokset** (*collision layers*, *filter*) rajaavat, mitkä
  parit laaja vaihe ylipäätään päästää läpi. Tämän tutoriaalin
  ainoa suodatin oli nivelellä yhdistettyjen kappaleiden ohitus.

Tutoriaalista pois rajatut aiheet ovat näiden osien sovelluksia.
Räsynukke on luuranko, jonka luut ovat jäykkiä kappaleita ja nivelet
kulmarajoitettuja palloniveliä ja saranoita. Ajoneuvon pyörä on
tavallisesti säde alaspäin, jousi ja kitkamalli, ei pyörivä
kappale. Murtuminen vaihtaa yhden kappaleen ennalta leikattuihin
paloihin, kun impulssi ylittää rajan.

## Nyrkkisäännöt

| Tilanne | Sääntö |
|---------|--------|
| aika-askel | kiinteä; fysiikka ei saa seurata ruudunpäivitystä |
| integrointi | puoli-implisiittinen Euler: nopeus ennen paikkaa |
| yksiköt | metri, kilogramma, sekunti |
| kosketus | normaali, syvyys ja pisteet; pysyvä monisto |
| impulssi | kertynyt impulssi rajataan, ei yksittäinen korjaus |
| kitka | raja on kitkakerroin kertaa normaali-impulssi |
| pino kaatuu | lämmin käynnistys, lisää kierroksia tai aliaskeleita |
| kappale tärisee | marginaali ja vara; tarkista moniston pysyvyys |
| kappale ponnahtaa | korjausnopeudelle katto; pienempi β |
| nivel venyy | aliaskeleet; massasuhde alle 10:1 |
| luoti menee läpi | jatkuva törmäystunnistus vain nopeille kappaleille |
| suuri maailma | laaja vaihe, saaret ja lepotila |
| kangas ja köysi | sijaintipohjainen dynamiikka, ei jäykkiä jousia |
| vesi | pinta, hiukkaset tai tilavuus sen mukaan, mitä näkyy |
| toisto ja verkko | kiinteä järjestys, koko tila vedokseen, FMA pois |
| testaus | säilymislait, energia ei kasva, lepo, tiiviste |

## Jatkotaidot

- *Reaaliaikaiset moninpelit*: fysiikan tilan ennustus, takaisinkelaus
  ja täsmäytys verkon yli. Luvun 13 determinismi ja tilannevedokset
  ovat sen lähtökohta.
- *Fysikaalinen mallinnus ja simulointi*: sama mekaniikka, kun
  tavoite on tarkkuus: elementtimenetelmä, implisiittiset
  integraattorit ja virhearviot.
- *Virtauslaskenta*: nesteen ja kaasun virtauksen laskenta
  tilavuudessa.
- *GPU-laskenta*: hiukkasten, kankaan ja nesteen simulointi
  näytönohjaimella, kun kappaleita on satoja tuhansia.
- *C++:n suorituskyky*: ratkaisijan datan asettelu ja vektorointi.
- *Rinnakkaisohjelmointi*: saarten ja kosketusparien ratkaisu
  usealla säikeellä.
- *Numeeriset menetelmät*: integraattorien stabiilisuus ja
  iteratiivisten ratkaisijoiden suppeneminen yleisesti.

## Lähteet ja jatkolukeminen

Kirjat:

- Christer Ericson: *Real-Time Collision Detection*. Morgan
  Kaufmann, 2005. Erotteluakselit, lähimmät pisteet ja laaja vaihe.
- Gino van den Bergen: *Collision Detection in Interactive 3D
  Environments*. Morgan Kaufmann, 2003. GJK perusteellisesti.
- Ian Millington: *Game Physics Engine Development*, 2. painos.
  CRC Press, 2010. Fysiikkamoottori alusta loppuun.
- Jason Gregory: *Game Engine Architecture*, 3. painos. CRC
  Press, 2018. Fysiikka pelimoottorin osana.

Artikkelit ja esitykset:

- David Baraff: *Physically Based Modeling: Rigid Body Simulation*.
  SIGGRAPH 2001, kurssimoniste. Jäykän kappaleen yhtälöt.
- Joachim Baumgarte: *Stabilization of Constraints and Integrals of
  Motion in Dynamical Systems*. Computer Methods in Applied Mechanics
  and Engineering, 1972.
- Erin Catto: *Iterative Dynamics with Temporal Coherence*, 2005,
  sekä GDC-esitykset *Fast and Simple Physics using Sequential
  Impulses* (2006), *Modeling and Solving Constraints* (2009) ja
  *Understanding Constraints* (2014), <https://box2d.org/publications/>.
  Peräkkäiset impulssit, kertyvä impulssi ja lämmin käynnistys.
- Elmer Gilbert, Daniel Johnson ja Sathiya Keerthi: *A Fast Procedure
  for Computing the Distance Between Complex Objects in
  Three-Dimensional Space*. IEEE Journal on Robotics and
  Automation, 1988. GJK-algoritmi.
- Dirk Gregorius: *The Separating Axis Test between Convex Polyhedra*,
  GDC 2013, ja *Robust Contact Creation for Physics Simulations*,
  GDC 2015.
- Thomas Jakobsen: *Advanced Character Physics*. GDC 2001.
  Verlet-integrointi ja etäisyysrajoitteiden iterointi.
- Matthias Müller, Bruno Heidelberger, Marcus Hennix ja John Ratcliff:
  *Position Based Dynamics*. Journal of Visual Communication and Image
  Representation, 2007.
- Miles Macklin, Matthias Müller ja Nuttapong Chentanez: *XPBD:
  Position-Based Simulation of Compliant Constrained Dynamics*.
  Motion in Games, 2016.
- Miles Macklin ja Matthias Müller: *Position Based Fluids*. ACM
  Transactions on Graphics, 2013.
- Glenn Fiedler: *Fix Your Timestep!* ja *Floating Point
  Determinism*. Gaffer On Games, <https://gafferongames.com>.

Fysiikkamoottorit:

- Box2D, <https://box2d.org> (MIT-lisenssi).
- Bullet, <https://github.com/bulletphysics/bullet3> (zlib-lisenssi).
- Jolt Physics, <https://github.com/jrouwe/JoltPhysics>
  (MIT-lisenssi).
- PhysX, <https://github.com/NVIDIA-Omniverse/PhysX>
  (BSD-3-lisenssi).

Tutoriaalin koodi on kirjoitettu tätä tutoriaalia varten, eikä se
sisällä moottorien koodia. Algoritmit ovat alan yleisesti tunnettuja
menetelmiä, jotka on toteutettu lähteissä kuvattujen periaatteiden
pohjalta. Otsakkeet `vektori.hpp`, `tulostus.hpp` ja `piirto.hpp` ovat
samat kuin tämän sarjan tutoriaalissa *3D-peliohjelmointi*.
