# Virtauksen yhtälöt

Virtauksen yhtälöt ovat kaksi tasetta: massa säilyy ja liikemäärä
muuttuu vain voimien vaikutuksesta. Tässä luvussa ne kirjoitetaan
kontrollitilavuudelle samalla tavalla kuin lämmön tase, katsotaan, mitä
kukin termi tekee, ja opitaan lukemaan virtauksen luonne Reynoldsin
luvusta ennen kuin mitään lasketaan. Lopuksi ratkaistaan tapaus, jossa
yhtälöt supistuvat yhteen tuttuun tasapainoyhtälöön.

## Massan tase

Valitaan paikallaan pysyvä pieni tilavuus, jonka läpi neste virtaa.
Nopeudella on vaakakomponentti $u$ ja pystykomponentti $v$. Pinnan läpi
kulkee aikayksikössä massa $\rho$ kertaa pintaa vastaan kohtisuora
nopeus kertaa pinnan ala. Jos tiheys ei muutu, tilavuuteen tulee yhtä
paljon kuin siitä lähtee:

$$\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 0
  \qquad\text{eli}\qquad \nabla\cdot\mathbf u = 0.$$

Tämä on **jatkuvuusyhtälö** kokoonpuristumattomalle virtaukselle.
Nopeuskenttää, joka toteuttaa sen, sanotaan lähteettömäksi.

Kokoonpuristumattomuus on virtauksen ominaisuus, ei aineen. Ilma
puristuu helposti, mutta hitaassa virtauksessa paine-erot ovat niin
pieniä, ettei tiheys ehdi muuttua. Mittari on **Machin luku**
$\mathrm{Ma} = U/c$, virtausnopeuden suhde äänen nopeuteen. Tiheyden
suhteellinen muutos on suuruusluokkaa $\mathrm{Ma}^2/2$, joten rajana
pidetään arvoa 0,3: sen alapuolella virhe on alle viisi prosenttia.
Ilmassa raja on noin 100 m/s. Rakennusten, autojen ja ilmanvaihdon
virtaukset ovat kokoonpuristumattomia, matkustajakoneen siiven virtaus
ei.

## Liikemäärän tase

Sama tilavuus, nyt liikemäärälle. Vaakasuuntaista liikemäärää on
tilavuusyksikössä $\rho u$. Se muuttuu kolmesta syystä.

- **Advektio.** Neste, joka virtaa pinnan läpi, tuo liikemääränsä
  mukanaan. Pystypinnan läpi kulkee tilavuusvirta $u$ pinta-alayksikköä
  kohden, ja se kuljettaa suuretta $\rho u$: vuo on $\rho u\,u$.
  Vaakapinnan läpi virtaa $v$, ja se kuljettaa samaa suuretta: vuo on
  $\rho u\,v$.
- **Paine.** Tilavuuden vastakkaisilla pinnoilla on eri paine, ja erotus
  työntää nestettä matalamman paineen suuntaan.
- **Viskositeetti.** Naapurikerrokset vetävät toisiaan
  leikkausjännityksellä, kuten johdannon levyesimerkissä.

Kun tase jaetaan tilavuudella ja tiheydellä, saadaan **Navier–Stokesin
yhtälöt**

$$\frac{\partial \mathbf u}{\partial t}
  + \nabla\cdot(\mathbf u\,\mathbf u)
  = -\nabla p + \nu\,\nabla^2\mathbf u,
  \qquad \nabla\cdot\mathbf u = 0.$$

Komponenteittain ensimmäinen yhtälö on

$$\frac{\partial u}{\partial t}
  + \frac{\partial (uu)}{\partial x} + \frac{\partial (uv)}{\partial y}
  = -\frac{\partial p}{\partial x}
  + \nu\left(\frac{\partial^2 u}{\partial x^2}
  + \frac{\partial^2 u}{\partial y^2}\right),$$

ja $v$:lle vastaavasti. Tuntemattomia on kolme, $u$, $v$ ja $p$, ja
yhtälöitä kolme. Yhtälöt ovat säilyvässä muodossa: advektiotermi on
vuon divergenssi, ei auki kerrottu $\mathbf u\cdot\nabla\mathbf u$.
Jatkuvalle ratkaisulle muodot ovat samat, mutta taidon *Fysikaalinen
mallinnus ja simulointi* sääntö pätee tässäkin: diskretoidaan tase.

Jokainen termi tuo oman numeerisen luonteensa, ja siksi yhtälöitä ei
ratkaista yhdellä menetelmällä vaan termi kerrallaan:

| Termi | Mitä se tekee | Luonne | Luku |
|---|---|---|---|
| $\nu\nabla^2\mathbf u$ | tasoittaa nopeuseroja | parabolinen, kuten lämpö | 1 |
| $\nabla\cdot(\mathbf u\mathbf u)$ | kuljettaa liikemäärää virtauksen mukana | hyperbolinen, epälineaarinen | 4, 5 |
| $-\nabla p$ ja $\nabla\cdot\mathbf u = 0$ | pitää massan tallessa | elliptinen: vaikuttaa heti kaikkialle | 6 |

Advektiotermi on **epälineaarinen**: nopeus kuljettaa itseään. Siitä
seuraa, ettei ratkaisuja voi laskea yhteen, että sama geometria voi
tuottaa aivan erilaisen virtauksen eri nopeudella ja lopulta myös
turbulenssi.

## Reynoldsin luku

Mitataan pituudet kappaleen koolla $L$, nopeudet tyypillisellä
nopeudella $U$, aika suureella $L/U$ ja paine suureella $U^2$.
Yhtälöihin jää yksi luku:

$$\frac{\partial \mathbf u}{\partial t}
  + \nabla\cdot(\mathbf u\,\mathbf u)
  = -\nabla p + \frac{1}{\mathrm{Re}}\,\nabla^2\mathbf u,
  \qquad \mathrm{Re} = \frac{UL}{\nu}.$$

**Reynoldsin luku** on hitausvoimien suhde kitkavoimiin. Kaksi
virtausta, joilla on sama geometria ja sama Reynoldsin luku, ovat
samanlaiset koosta, nopeudesta ja aineesta riippumatta. Tähän perustuvat
pienoismallikokeet, ja siksi myös laskennan tulokset esitetään
dimensiottomina.

```{.python tiedosto="esimerkit/02-reynolds.py" osa="luvut"}
```

```{.tuloste tiedosto="esimerkit/02-reynolds.odotettu"}
```

Luvut ovat suuruusluokkia, ja ne riittävät kertomaan tehtävän luonteen.
Kun Reynoldsin luku on pieni, advektiotermin voi jättää pois ja
yhtälöt ovat lineaariset. Kun se on tuhansia tai enemmän, virtaus on
yleensä turbulentti. Raja riippuu geometriasta: putkessa se on noin
2 300, tasolevyn rajakerroksessa satoja tuhansia. Arkisen kokoiset
veden ja ilman virtaukset ovat lähes aina turbulentteja, koska
kummankin viskositeetti on pieni.

Reynoldsin luku kertoo myös, missä viskositeetti vaikuttaa. Johdannon
rajakerroksen paksuus suhteessa kappaleen kokoon on suuruusluokkaa
$1/\sqrt{\mathrm{Re}}$: mitä suurempi luku, sitä ohuempi kerros ja sitä
tiheämpi hila seinän lähelle tarvitaan.

## Tapaus, jossa yhtälöt ratkeavat: virtaus raossa

Kahden yhdensuuntaisen levyn välissä, kaukana raon päistä, nopeus on
levyjen suuntainen eikä muutu virtaussuunnassa. Silloin advektiotermi
häviää, paine riippuu vain $x$:stä ja liikemäärän tase supistuu
muotoon

$$\frac{d}{dy}\left(\mu\,\frac{du}{dy}\right) = \frac{dp}{dx}.$$

Leikkausjännityksen muutos raon poikki kumoaa painegradientin. Yhtälö
on sama kuin lämmönjohtuminen tangossa, jossa on lähde. Kun
viskositeetti on vakio, ratkaisu on paraabeli. Kaksi erikoistapausta on
nimetty: **Couetten virtaus**, jossa toinen levy liikkuu eikä
painegradienttia ole (suora profiili), ja **Poiseuillen virtaus**, jossa
levyt ovat paikallaan ja paine ajaa virtausta (symmetrinen paraabeli).

Esimerkki on liukulaakerin voitelukalvo, jossa on molemmat: alalevy
liikkuu ja paine laskee virtaussuuntaan. Toisessa tapauksessa liikkuva
pinta on kuuma, ja öljyn viskositeetti on siellä kolmasosa kylmän
puolen arvosta.

```{.python tiedosto="esimerkit/02-kanava.py" osa="tehtava"}
```

Diskretointi on kontrollitilavuuksien tase. Pinnan "johtavuus" on
viskositeetti jaettuna keskipisteiden etäisyydellä, ja seinän vieressä
etäisyys on puolikas.

```{.python tiedosto="esimerkit/02-kanava.py" osa="ratkaisu"}
```

Muuttuvalle viskositeetille tarkka ratkaisu saadaan integroimalla.
Leikkausjännitys on lineaarinen, $\tau(y) = \tau_0 + (dp/dx)\,y$, ja
nopeus on suureen $\tau/\mu$ integraali.

```{.python tiedosto="esimerkit/02-kanava.py" osa="tarkka"}
```

```{.tuloste tiedosto="esimerkit/02-kanava.odotettu"}
```

![Nopeus voitelukalvossa. Painegradientti pullistaa profiilin levyn
nopeutta suuremmaksi. Kuumalla puolella öljy on juoksevampaa, joten
nopeus muuttuu siellä jyrkemmin ja virtaama
kasvaa.](kuvat/voitelukalvo.png){width=70%}

Virhe pienenee neljäsosaan, kun tilavuuksien määrä kaksinkertaistuu,
ja **voimatase** toteutuu jokaisella hilalla pyöristystarkkuudella:
seinien leikkausvoimien erotus on yhtä suuri kuin painevoima. Se on
säilyvän diskretoinnin ominaisuus, ei tarkkuuden merkki. Vakioviskositeetin
tilavuusvirta 194,5 mm²/s on prosentin sadasosan päässä kaavan arvosta
$Q = UH/2 - (dp/dx)\,H^3/(12\mu) = 194{,}44$ mm²/s.

Leikkausjännitys liikkuvalla levyllä on positiivinen: neste vetää levyä
eteenpäin, koska painegradientti ajaa nestettä levyä nopeammin. Merkin
olisi voinut päätellä kuvasta, sillä nopeus kasvaa levystä poispäin.

## Pyörteisyys ja virtafunktio

Kaksi johdettua kenttää tekevät tasovirtauksesta luettavan, ja niitä
käytetään kuvissa luvusta 7 alkaen.

**Virtafunktio** $\psi$ määritellään niin, että
$u = \partial\psi/\partial y$ ja $v = -\partial\psi/\partial x$.
Tällainen kenttä on automaattisesti lähteetön. Virtafunktion
tasa-arvokäyrät ovat **virtaviivoja**, joita pitkin neste kulkee, ja
kahden virtaviivan arvojen erotus on niiden välistä kulkeva
tilavuusvirta. Tiheässä olevat viivat tarkoittavat siis suurta nopeutta.

**Pyörteisyys**
$\omega = \partial v/\partial x - \partial u/\partial y$ on nesteen
paikallinen pyörimisnopeus kaksinkertaisena. Sitä syntyy seinillä,
joilla nopeus pakotetaan nollaan, ja se kulkeutuu sieltä virtaukseen.
Pyörteisyyskuva näyttää rajakerrokset ja pyörteet, joita nopeuskuvasta
on vaikea erottaa.

## Käytännössä

- **Laske Reynoldsin ja Machin luku ensin.** Ne kertovat, mitkä termit
  ovat mukana, onko virtaus laminaari ja riittääkö kokoonpuristumaton
  malli. Väärä malli tarkalla hilalla on edelleen väärä.
- **Valitse mitat harkiten.** Reynoldsin luvun $L$ ja $U$ ovat
  sopimuksia: putkelle halkaisija ja keskinopeus, siivelle jänne ja
  lentonopeus. Kirjallisuusarvoon voi verrata vain, jos määritelmä on
  sama.
- **Esitä tulokset dimensiottomina.** Painehäviö suureena
  $\Delta p / (\rho U^2/2)$ ja taajuus Strouhalin lukuna (luku 10)
  pätevät kaikille samanlaisille virtauksille.
- **Tarkista tase.** Kehittyneessä kanavavirtauksessa painevoima on
  yhtä suuri kuin seinien kitka. Mille tahansa virtaukselle sisään
  tuleva massavirta on ulos lähtevä massavirta.
- **Käytä tunnettuja ratkaisuja.** Couetten ja Poiseuillen virtaus ovat
  jokaisen virtausohjelman ensimmäiset testit, koska niissä voi mennä
  vikaan vain viskoositermi ja reunaehto.

## Itsearviointi

- Osaat kirjoittaa massan taseen kontrollitilavuudelle ja selittää,
  milloin virtausta voi pitää kokoonpuristumattomana.
- Osaat nimetä Navier–Stokesin yhtälöiden termit, kertoa, mitä kukin
  tekee fysikaalisesti ja miksi advektiotermi tekee yhtälöistä
  epälineaariset.
- Osaat laskea Reynoldsin luvun ja päätellä siitä virtauksen luonteen
  ja rajakerroksen paksuuden suuruusluokan.
- Osaat johtaa kehittyneen rakovirtauksen yhtälön liikemäärän taseesta
  ja tunnistat Couetten ja Poiseuillen virtauksen.
- Osaat lukea virtaviiva- ja pyörteisyyskuvaa.
