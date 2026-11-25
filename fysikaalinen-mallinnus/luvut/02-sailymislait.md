# Säilymislaista yhtälöksi

Kaikki tämän tutoriaalin yhtälöt syntyvät samalla tavalla: valitaan
pieni tilavuus, kirjataan sille tase ja lisätään aineen laki. Tässä
luvussa johdetaan niin lämpöyhtälö ja aaltoyhtälö, katsotaan, mitä
reunaehdot fysikaalisesti tarkoittavat, ja opitaan lukemaan tehtävän
luonne dimensiottomista luvuista jo ennen kuin mitään lasketaan. Samalla
nähdään, miksi tase kannattaa säilyttää myös ohjelmakoodissa.

## Tase kontrollitilavuudessa

Tarkastellaan tankoa, jonka sivut on eristetty, ja siitä palaa välillä
$[x, x + \Delta x]$. Palan lämpöenergia muuttuu vain sen verran kuin
päiden läpi virtaa ja sisällä syntyy:

$$\rho c\,A\,\Delta x\,\frac{\partial u}{\partial t}
  = A\,q(x) - A\,q(x + \Delta x) + A\,\Delta x\,s.$$

Tässä $u$ on lämpötila, $\rho c$ tilavuuslämpökapasiteetti
(J/(m³ K)), $q$ lämpövuo (W/m²) positiivisena kasvavan $x$:n suuntaan
ja $s$ lämmönlähde (W/m³). Yhtälö on **säilymislaki**: se ei oleta
aineesta mitään. Kun se jaetaan tilavuudella ja $\Delta x$ lähestyy
nollaa, saadaan

$$\rho c\,\frac{\partial u}{\partial t} + \frac{\partial q}{\partial x} = s.$$

**Aineen laki** sitoo vuon lämpötilaan. Fourier'n lain mukaan lämpö
virtaa kuumasta kylmään nopeudella, joka on verrannollinen lämpötilan
gradienttiin: $q = -k\,\partial u/\partial x$. Sijoitus antaa
**lämpöyhtälön**

$$\rho c\,\frac{\partial u}{\partial t}
  = \frac{\partial}{\partial x}\!\left(k\,\frac{\partial u}{\partial x}\right) + s.$$

Jos $k$ on vakio, yhtälö saa tutun muodon $u_t = \alpha u_{xx} + s/(\rho c)$,
jossa $\alpha = k/(\rho c)$ on **lämpötilanjohtavuus** (m²/s). Kahdessa
ja kolmessa ulottuvuudessa derivaatan paikalle tulevat divergenssi ja
gradientti: $\rho c\,u_t = \nabla \cdot (k \nabla u) + s$.

Sama rakenne toistuu muualla. Vain suureiden nimet vaihtuvat:

| Ilmiö | Säilyvä suure | Vuon laki | Tasapainoyhtälö |
|---|---|---|---|
| lämmönjohtuminen | energia | Fourier: $q = -k\nabla u$ | $-\nabla\cdot(k\nabla u) = s$ |
| diffuusio | aineen määrä | Fick: $j = -D\nabla c$ | $-\nabla\cdot(D\nabla c) = s$ |
| sähköstatiikka | varaus | $D = -\varepsilon\nabla\varphi$ | $-\nabla\cdot(\varepsilon\nabla\varphi) = \rho$ |
| pohjaveden virtaus | massa | Darcy: $v = -K\nabla h$ | $-\nabla\cdot(K\nabla h) = s$ |
| vetosauva | liikemäärä | Hooke: $\sigma = E u'$ | $-(EA\,u')' = f$ |

Kun osaa ratkaista yhden näistä, osaa ratkaista kaikki. Siksi
tutoriaalin esimerkit ovat enimmäkseen lämmönjohtumista: se on helpoin
kuvitella, ja tulokset siirtyvät muihin sellaisinaan.

## Säilyvä muoto koodissa

Taseen voi diskretoida suoraan ilman, että differentiaaliyhtälöä
kirjoitetaan auki. Tanko jaetaan kontrollitilavuuksiin, ja jokaisen
rajapinnan vuo lasketaan kerran. Sama luku vähennetään toisesta
tilavuudesta ja lisätään toiseen, joten mitään ei katoa matkalla.

Esimerkin tangon vasen puolisko on kuparia ja oikea terästä. Vasenta
päätä lämmitetään kahden watin teholla, ja muut pinnat on eristetty.

```{.python tiedosto="esimerkit/02-tase.py" osa="tanko"}
```

```{.python tiedosto="esimerkit/02-tase.py" osa="sailyva"}
```

Rajapinnan johtavuus on kahden puolikkaan **harmoninen keskiarvo**,
koska puolikkaat ovat lämpövastuksina sarjassa. Luku 3 näyttää, että
tämä valinta on tarkka ja aritmeettinen keskiarvo ei.

Vertailuksi sama yhtälö kirjoitetaan auki tulon derivaatan säännöllä,
$(k u')' = k u'' + k' u'$, ja kumpikin derivaatta korvataan
keskeisdifferenssillä. Matemaattisesti muodot ovat samat, kun $k$ on
derivoituva.

```{.python tiedosto="esimerkit/02-tase.py" osa="sailymaton"}
```

```{.python tiedosto="esimerkit/02-tase.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/02-tase.odotettu"}
```

![Vasemmalla lämpötilan nousu kolmella hetkellä: kuparissa profiili on
loiva, teräksessä jyrkkä, ja taitekohta on aineiden rajalla. Oikealla
tankoon varastoitunut energia: säilyvä muoto seuraa syötettyä energiaa
tarkasti, auki kerrottu muoto luo energiaa
tyhjästä.](kuvat/tase.png){width=95%}

Säilyvä muoto palauttaa syötetyn energian tarkasti millä tahansa
hilalla, koska tase on rakennettu koodiin. Auki kerrottu muoto tuottaa
kymmenessä minuutissa kaksitoistakertaisen energian. Syy on aineiden
raja: siinä $k$ hyppää, sen derivaatta ei ole olemassa, ja
erotusosamäärä tekee hypystä valtavan lähdetermin. Virhe ei pienene
hilaa tihentämällä.

Tästä seuraa sääntö, jota tutoriaali noudattaa: **diskretoidaan tase,
ei auki kerrottua yhtälöä**. Differenssimenetelmässä se tarkoittaa
vuon laskemista rajapinnoilla, ja elementtimenetelmän heikko muoto
(luku 6) tekee saman automaattisesti.

## Aaltoyhtälö

Kun säilyvä suure on liikemäärä ja aineen laki on kimmoinen, tulee
toisenlainen yhtälö. Jännitetyn kielen pala, jonka massa on
$\mu\,\Delta x$, kiihtyy poikittain sen mukaan, miten paljon jännitys
$T$ vetää sitä eri suuntiin palan päissä:

$$\mu\,\Delta x\,\frac{\partial^2 u}{\partial t^2}
  = T\,u_x(x + \Delta x) - T\,u_x(x)
  \quad\Longrightarrow\quad
  u_{tt} = c^2 u_{xx}, \qquad c = \sqrt{T/\mu}.$$

Tämä on **aaltoyhtälö**, ja $c$ on aallon etenemisnopeus. Sama yhtälö
kuvaa pitkittäisvärähtelyä sauvassa ($c = \sqrt{E/\rho}$), ääntä
ilmassa ja sähkömagneettista aaltoa johtimessa. Taidon
*Differentiaaliyhtälöt ja Laplace-muunnos* jousi–massa-värähtelijä on
sen yhden vapausasteen versio.

## Kolme yhtälötyyppiä

Tutoriaalin kolme perusyhtälöä käyttäytyvät eri tavoin, ja ero määrää,
millainen numeerinen menetelmä niille sopii.

| Tyyppi | Esimerkki | Käyttäytyminen | Numeerinen seuraus |
|---|---|---|---|
| elliptinen | Poisson $-\nabla^2 u = f$ | tasapaino: jokainen piste riippuu kaikista reunoista | yksi suuri yhtälöryhmä |
| parabolinen | lämpö $u_t = \alpha\nabla^2 u$ | tasoittuu: terävät muodot häviävät heti | jäykkä, implisiittinen aika-askel kannattaa |
| hyperbolinen | aalto $u_{tt} = c^2\nabla^2 u$ | etenee äärellisellä nopeudella, muoto säilyy | aika-askelta rajoittaa aallon nopeus |

Lämpöyhtälön tasapainotila ($u_t = 0$) on Poissonin yhtälö. Ilman
lähdettä se on **Laplacen yhtälö** $\nabla^2 u = 0$.

## Reunaehdot ja alkuehdot

Yhtälö kertoo, mitä kappaleen sisällä tapahtuu. Reunaehto kertoo, miten
kappale on kytketty ympäristöönsä, ja se on yhtä lailla mallin osa.

| Nimi | Ehto reunalla | Lämpötehtävässä | Rakenteessa |
|---|---|---|---|
| Dirichlet | $u = g$ | pinnan lämpötila tunnetaan | tuki, pakotettu siirtymä |
| Neumann | $-k\,\partial u/\partial n = q$ | lämpövuo tunnetaan; $q = 0$ on eriste tai symmetriataso | kuorma; vapaa reuna |
| Robin | $-k\,\partial u/\partial n = h(u - T_\infty)$ | konvektio ympäristöön | jousituki |

Ajasta riippuva tehtävä tarvitsee lisäksi **alkuehdon**: lämpöyhtälö
alkulämpötilan ja aaltoyhtälö sekä alkuaseman että alkunopeuden, koska
siinä on toinen aikaderivaatta.

Pelkillä Neumannin ehdoilla tasapainotehtävällä on ratkaisu vain, jos
reunan läpi tuleva ja lähteissä syntyvä lämpö summautuvat nollaan, ja
silloinkin ratkaisu on yksikäsitteinen vain vakiota vaille. Ohjelmassa
tämä näkyy singulaarisena matriisina. Syy on fysikaalinen: eristetyn
kappaleen lämpötilatasoa ei määrää mikään.

## Dimensiottomat luvut

Lämpöyhtälössä on kolme aineen ja kappaleen suuretta: $\alpha$,
kappaleen koko $L$ ja aika $t$. Kun paikka mitataan yksikössä $L$ ja
lämpötila alku- ja loppulämpötilan erotuksen osuutena $\theta$,
yhtälöön jää yksi luku, **Fourier'n luku**

$$\mathrm{Fo} = \frac{\alpha t}{L^2}.$$

Kaikki samanmuotoiset kappaleet, joilla on sama reunaehto, noudattavat
samaa käyrää $\theta(\mathrm{Fo})$. Esimerkki laskee käyrän levylle,
jonka pinnat pakotetaan äkkiä uuteen lämpötilaan, ja muuntaa sen
neljän aineen jäähtymisajoiksi.

```{.python tiedosto="esimerkit/02-dimensioton.py" osa="sarja"}
```

```{.python tiedosto="esimerkit/02-dimensioton.py" osa="aineet"}
```

```{.tuloste tiedosto="esimerkit/02-dimensioton.odotettu"}
```

![Levyn keskikohdan dimensioton lämpötila Fourier'n luvun funktiona.
Käyrä on sama kaikille aineille ja
paksuuksille.](kuvat/dimensioton.png){width=62%}

Tuloksesta voi lukea kolme asiaa laskematta mitään uudelleen. Aika
kasvaa paksuuden **neliössä**: kaksinkertainen levy tarvitsee
nelinkertaisen ajan. Lämpö tasoittuu, kun $\mathrm{Fo}$ on ykkösen
luokkaa, eli ajassa $L^2/\alpha$. Ja kuparin ja männyn välillä on
lähes kolme kertalukua. Tällainen suuruusluokka-arvio kannattaa tehdä
ennen jokaista simulointia: se kertoo, kuinka pitkä aika pitää
simuloida ja onko tulos järkevä.

Muut dimensiottomat luvut toimivat samoin. **Biot'n luku**
$\mathrm{Bi} = hL/k$ vertaa pinnan konvektiota kappaleen sisäiseen
johtumiseen ja kertoo, tarvitaanko kappaleen sisälle lainkaan
paikkariippuvaa mallia (luku 4). Aaltotehtävien **Courantin luku**
määrää aika-askeleen (luku 5).

## Käytännössä

- **Aloita taseesta.** Kirjoita ensin sanoin, mikä säilyy ja mitä
  reunojen läpi kulkee. Suurin osa mallinnusvirheistä on unohtuneita
  termejä tai vääriä reunaehtoja, ei numeriikkaa.
- **Diskretoi vuo, älä auki kerrottua yhtälöä.** Säilyvä muoto toimii
  myös aineiden rajoilla ja antaa taseen, jonka voi tarkistaa.
- **Tarkista tase jokaisesta ajosta.** Sisään tullut miinus ulos
  mennyt on varastoitunut. Tarkistus on halpa ja löytää sekä koodin että
  mallin virheitä.
- **Laske suuruusluokka käsin.** $L^2/\alpha$ lämmölle, $L/c$
  aallolle. Jos simulaatio on eri mieltä kertaluvulla, toinen on
  väärässä.
- **Pidä yksiköt mukana.** Käytä SI-perusyksiköitä koko laskun läpi ja
  muunna vain tulostettaessa. Millimetrien ja metrien sekoittaminen
  muuttaa lämpötilanjohtavuuden miljoonakertaiseksi.
- **Eristetty reuna ja symmetriataso ovat sama ehto.** Symmetrian
  käyttö puolittaa tai neljännestää tehtävän (luku 9).

## Itsearviointi

- Osaat kirjoittaa kontrollitilavuuden taseen ja johtaa siitä
  lämpöyhtälön Fourier'n lain avulla.
- Osaat selittää, miksi säilyvä diskretointi toimii aineiden rajalla ja
  auki kerrottu muoto ei.
- Osaat nimetä elliptisen, parabolisen ja hyperbolisen yhtälön
  esimerkin ja kertoa, miten niiden ratkaisut käyttäytyvät.
- Osaat valita Dirichlet'n, Neumannin tai Robinin reunaehdon
  fysikaalisen tilanteen perusteella ja tiedät, miksi pelkät Neumannin
  ehdot eivät määrää ratkaisua.
- Osaat arvioida Fourier'n luvulla, kuinka kauan kappaleen
  lämpeneminen kestää.
