# Elementtimenetelmä tasossa

Kahdessa ulottuvuudessa elementtimenetelmän periaate on sama kuin
yhdessä: heikko muoto, kantafunktiot, elementtimatriisi ja kokoaminen.
Uutta on verkko. Alue jaetaan kolmioihin, ja ohjelman pitää tietää,
mitkä solmut kuuluvat mihinkin kolmioon. Tässä luvussa kirjoitetaan
pieni kirjasto, `pienfem`, joka ratkaisee lämmönjohtumisen
mielivaltaisessa kolmioverkossa. Sillä tarkistetaan menetelmän
kertaluku, nähdään, miten alueen nurkka voi pilata sen, ja toteutetaan
vuo- ja konvektioreunat. Myöhemmät luvut käyttävät samaa kirjastoa.

## Heikko muoto tasossa

Lämmönjohtumisen tasapainoyhtälö alueessa $\Omega$ on
$-\nabla \cdot (k \nabla u) = s$. Kerrotaan testifunktiolla ja
integroidaan. Osittaisintegroinnin tilalla on Greenin kaava, joka
siirtää derivaatan testifunktiolle ja tuottaa reunaintegraalin:

$$\int_\Omega k\,\nabla u \cdot \nabla v\,dA
  = \int_\Omega s\,v\,dA + \int_{\partial\Omega} k\,\frac{\partial u}{\partial n}\,v\,ds.$$

Reunaintegraalissa on reunan läpi tuleva lämpövuo. Dirichlet'n
reunalla testifunktio on nolla ja termi häviää. Eristetyllä reunalla
vuo on nolla ja termi häviää. Jäljelle jäävät vain reunat, joilla vuo
on annettu tai riippuu lämpötilasta, ja niihin palataan luvun lopussa.

## Verkko

Verkko on kaksi taulukkoa: solmujen koordinaatit ja kolmioiden
solmunumerot. Muuta ei tarvita.

```{.python tiedosto="esimerkit/07-pienfem/pienfem.py" osa="verkko"}
```

Kolmion solmut luetellaan vastapäivään, jolloin pinta-alan kaava antaa
positiivisen luvun. Alueen reuna löytyy topologiasta: särmä, joka
kuuluu vain yhteen kolmioon, on reunalla. Reunaa ei siis tarvitse
kuvata erikseen, eikä geometriasta tarvitse tietää mitään.

Funktio `suorakulmio` tekee yksinkertaisimman mahdollisen verkon.
Oikeissa töissä verkon tuottaa verkkogeneraattori (luku 11), mutta
tietorakenne on sama.

## Lineaarinen kolmioelementti

Kolmiossa on kolme kantafunktiota, yksi jokaista kärkeä kohden.
Kantafunktio $\varphi_i$ on taso, joka on yksi kärjessä $i$ ja nolla
kahdessa muussa. Yhdessä ne muodostavat solmun ympärille pyramidin,
hattufunktion vastineen tasossa.

Tason gradientti on vakio. Kun kärjet ovat $(x_i, y_i)$ ja kolmion
ala $A$, kärjen 0 kantafunktion gradientti on

$$\nabla\varphi_0 = \frac{1}{2A}\begin{pmatrix} y_1 - y_2 \\ x_2 - x_1 \end{pmatrix},$$

ja muut saadaan kiertämällä indeksejä. Gradientti on kohtisuorassa
vastakkaista sivua vastaan, ja sen pituus on sivua vastaavan korkeuden
käänteisluku. Koska gradientit ovat vakioita, elementtimatriisin
integraali on pelkkä tulo:

$$K^e_{ij} = k\,A\,\nabla\varphi_i \cdot \nabla\varphi_j.$$

```{.python tiedosto="esimerkit/07-pienfem/pienfem.py" osa="elementti"}
```

Kokoaminen on sama silmukka kuin sauvalla. Elementtimatriisin alkio
$(a, b)$ lisätään globaalin matriisin riville ja sarakkeelle, jotka
ovat kolmion solmujen $a$ ja $b$ numerot. Alkiot kerätään luetteloihin
ja muunnetaan lopuksi harvaksi matriisiksi; COO-muoto summaa samaan
paikkaan osuvat arvot.

```{.python tiedosto="esimerkit/07-pienfem/pienfem.py" osa="kokoaminen"}
```

Kuormavektori vaatii integraalin $\int s\,\varphi_i\,dA$, joka
lasketaan kvadratuurilla. Kolmion sivujen keskipisteet ovat
kvadratuuripisteinä tarkkoja toisen asteen polynomeille, mikä riittää
lineaarisille elementeille.

Dirichlet'n reunaehto asetetaan kuten yhdessä ulottuvuudessa: tunnettu
arvo siirretään oikealle puolelle ja ratkaistaan vain vapaat solmut.

```{.python tiedosto="esimerkit/07-pienfem/pienfem.py" osa="dirichlet"}
```

## Kirjaston tarkistus

Ennen kuin kirjastolla lasketaan mitään, sen pitää läpäistä
tarkistukset, joiden vastaus tiedetään. Tässä on neljä, helpoimmasta
vaativimpaan.

**Elementtimatriisi käsin.** Suorakulmaisen yksikkökolmion matriisi
on helppo laskea paperilla. Rivisummien pitää olla nollia millä
tahansa kolmiolla, koska vakiolämpötila ei synnytä vuota.

```{.python tiedosto="esimerkit/07-pienfem/main.py" osa="elementti"}
```

```{.tuloste tiedosto="esimerkit/07-pienfem.odotettu" rivit="1-5"}
```

**Paikkatesti.** Lineaarinen funktio $1 + 2x - 3y$ toteuttaa Laplacen
yhtälön ja on esitettävissä kantafunktioilla tarkasti. Menetelmän on
siis tuotettava se pyöristystarkkuudella verkosta riippumatta. Testi
löytää väärät gradientit, pinta-alat ja numerointivirheet.

```{.python tiedosto="esimerkit/07-pienfem/main.py" osa="paikkatesti"}
```

```{.tuloste tiedosto="esimerkit/07-pienfem.odotettu" rivit="6-6"}
```

**Vertailu toiseen menetelmään.** Tasaisella verkolla, jonka ruudut
on jaettu lävistäjällä, sisäsolmujen yhtälöt ovat täsmälleen viiden
pisteen kaava kerrottuna $h^2$:lla: lävistäjän suuntaisten naapurien
osuudet kumoutuvat.

```{.python tiedosto="esimerkit/07-pienfem/main.py" osa="viisipiste"}
```

```{.tuloste tiedosto="esimerkit/07-pienfem.odotettu" rivit="7-7"}
```

**Kertaluku.** Tehtävälle, jonka ratkaisu on
$\sin \pi x \sin \pi y$, $L^2$-virheen pitää pienentyä kuten $h^2$.

```{.python tiedosto="esimerkit/07-pienfem/main.py" osa="kertaluku"}
```

```{.tuloste tiedosto="esimerkit/07-pienfem.odotettu" rivit="8-13"}
```

Kaikki neljä menevät läpi. Vasta nyt kirjastoa voi käyttää tehtäviin,
joiden vastausta ei tiedetä.

## Sisäänpäin kääntyvä kulma

L-kirjaimen muotoisessa alueessa on yksi nurkka, jossa alueen
sisäkulma on 270 astetta. Funktio

$$u(r, \theta) = r^{2/3}\,\sin\tfrac{2\theta}{3}$$

toteuttaa Laplacen yhtälön ja on nolla nurkan kummallakin sivulla. Sen
gradientti käyttäytyy kuten $r^{-1/3}$ ja kasvaa rajatta nurkkaa
lähestyttäessä. Tämä ei ole keksitty kuriositeetti: jokaisen
sisäänpäin kääntyvän nurkan lähellä tasapainotehtävän ratkaisu on tätä
muotoa. Lämpövuo, sähkökenttä ja jännitys keskittyvät teräviin
sisänurkkiin.

```{.python tiedosto="esimerkit/07-l-alue.py" osa="tarkka"}
```

Reuna-arvot otetaan tarkasta ratkaisusta, jolloin virhe voidaan mitata.

```{.python tiedosto="esimerkit/07-l-alue.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/07-l-alue.odotettu"}
```

![L-alueen verkko ja ratkaisu. Tasa-arvokäyrät tihenevät nurkassa,
jossa gradientti kasvaa rajatta.](kuvat/l-alue.png){width=95%}

Kertaluku on 1,33 eikä 2. Teoria selittää luvun: virheraja $Ch^2$
olettaa, että ratkaisun toiset derivaatat ovat rajoitettuja, ja tässä
ne eivät ole. Singulariteetin $r^{2/3}$ kanssa $L^2$-virhe pienenee
kuten $h^{4/3}$. Nurkan vieressä virhe pienenee vielä hitaammin, ja
nurkan gradientin arvo ei suppene lainkaan, koska tarkka arvo on
ääretön.

![$L^2$-virhe neliössä ja L-alueessa. Sama koodi ja samanlainen
verkko, mutta eri kaltevuus.](kuvat/kertaluvut.png){width=62%}

Käytännön seuraus on kaksiosainen. Tihentäminen kaikkialla on tehoton
tapa parantaa tulosta, kun virhe syntyy yhdessä pisteessä; luku 11
näyttää, miten solmut keskitetään nurkkaan. Ja nurkan jännitys tai vuo
on suure, jota malli ei pysty antamaan, vaikka verkko olisi kuinka
tiheä. Oikeassa kappaleessa nurkka on pyöristetty, ja pyöristyksen
säde on mallinnettava, jos huippuarvoa tarvitaan.

## Vuo- ja konvektioreunat

Heikon muodon reunaintegraali toteutetaan samalla kokoamisperiaatteella
kuin alueen integraalit, mutta elementteinä ovat reunan särmät.
Annettu vuo $q$ antaa kuormavektoriin termin $\int q\,\varphi_i\,ds$:
särmän vuo jaetaan puoliksi sen kahdelle solmulle. Konvektioreunalla
vuo on $h(T_\infty - u)$, jossa on tuntematon $u$. Sen osuus siirtyy
vasemmalle puolelle matriisiksi, joka on yksiulotteinen massamatriisi
särmällä:

$$\int_{\partial\Omega} h\,u\,v\,ds
  \quad\Rightarrow\quad
  \frac{h\,\ell}{6}\begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}.$$

```{.python tiedosto="esimerkit/07-pienfem/pienfem.py" osa="reuna"}
```

Esimerkkinä on alumiinilevy, jonka vasemmalla reunalla on lämmitin ja
jonka oikea reuna jäähtyy ilmaan. Ylä- ja alareuna on eristetty.

```{.python tiedosto="esimerkit/07-reunaehdot.py" osa="ratkaisu"}
```

Eristetyille reunoille ei kirjoiteta riviäkään. Kokeessa on kaksi
tapausta: ensin lämmitin kattaa koko reunan, jolloin tehtävä on
yksiulotteinen ja vastaus tunnetaan, ja sitten vain keskimmäisen
kolmanneksen.

```{.python tiedosto="esimerkit/07-reunaehdot.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/07-reunaehdot.odotettu"}
```

![Levyn lämpötila, kun lämmitin on vasemman reunan keskellä. Lämpö
leviää ensin koko korkeudelle ja kulkee sitten tasaisena rintamana
jäähdytettävälle reunalle.](kuvat/lammitin.png){width=78%}

Ensimmäinen tapaus toistaa tarkan ratkaisun kaikilla näytetyillä
numeroilla, koska ratkaisu on lineaarinen. Toisessa tarkkaa ratkaisua
ei ole, mutta energiatase voidaan tarkistaa: lämmittimestä tulee
75 wattia levyn paksuusmetriä kohden, ja täsmälleen sama poistuu
konvektioreunalta. Tase toteutuu elementtimenetelmässä millä tahansa
verkolla, koska vakio on kelvollinen testifunktio ja heikko muoto on
silloin itse tase. Tarkistus ei siis kerro, että ratkaisu on tarkka,
mutta se kertoo, että reunaehdot on koottu oikein.

Esimerkin tuloksesta näkyy myös luvun 4 Biot'n luku: alumiinilevyssä
johtuminen on konvektioon nähden niin tehokasta, että kuumimman ja
kylmimmän kohdan ero on alle aste, vaikka levy on 30 astetta ilmaa
lämpimämpi.

## Käytännössä

- **Testaa kirjasto ennen kuin käytät sitä.** Elementtimatriisi
  käsin, paikkatesti, vertailu tunnettuun menetelmään ja kertaluku.
  Paikkatesti on tehokkain: se on halpa ja löytää useimmat
  kokoamisvirheet.
- **Verkko on dataa, ei geometriaa.** Solmut ja kolmiot riittävät.
  Reunat, naapurit ja reunaehtojen joukot johdetaan niistä.
- **Sisänurkka on singulariteetti.** Älä raportoi suurinta jännitystä
  tai vuota terävästä sisänurkasta: luku kasvaa verkkoa tihennettäessä
  rajatta. Mallinna pyöristys tai käytä suuretta, joka suppenee.
- **Kertaluku paljastaa singulariteetin.** Jos mitattu kertaluku on
  selvästi teoriaa pienempi eikä koodissa ole vikaa, ratkaisu ei ole
  sileä. Etsi nurkka, pistekuorma tai reunaehdon hyppy.
- **Tarkista tase jälkikäteen.** Reunojen läpi kulkevien tehojen summa
  on nolla tasapainossa. Poikkeama tarkoittaa väärin valittua
  reunajoukkoa tai etumerkkiä.
- **Silmukka Pythonissa on hidas.** `pienfem` kokoaa kymmeniä tuhansia
  elementtejä sekunnissa, mikä riittää opetteluun. Tuotantokirjastot
  laskevat kaikki elementtimatriisit kerralla taulukko-operaatioina
  (luku 8).

## Itsearviointi

- Osaat kuvata kolmioverkon tietorakenteen ja löytää reunasärmät
  pelkästä kolmioluettelosta.
- Osaat johtaa lineaarisen kolmion kantafunktioiden gradientit ja
  elementtimatriisin.
- Osaat suunnitella elementtikoodille paikkatestin ja tiedät, mitä
  virheitä se löytää.
- Osaat selittää, miksi sisäänpäin kääntyvä kulma pienentää kertalukua
  ja miksi nurkan vuo ei suppene.
- Osaat toteuttaa vuo- ja konvektioreunaehdon reunasärmien yli ja
  tarkistaa tuloksen energiataseella.
