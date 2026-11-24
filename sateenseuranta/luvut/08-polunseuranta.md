# Polunseuranta

Polunseuranta arvioi renderöintiyhtälön yhdellä satunnaisella
näytteellä jokaisessa pinnan pisteessä. Kamerasta lähtevä säde osuu
pintaan, pinnalta poimitaan yksi uusi suunta BRDF:n mukaan, säde osuu
seuraavaan pintaan, ja niin edelleen. Tuloksena on *polku*, jonka
varrella kerätään valolähteiden säteily painotettuna kaikkien
heijastusten painoilla. Pikselin arvo on monen polun keskiarvo.

## Yksi polku

Kun renderöintiyhtälön integraalia arvioidaan yhdellä näytteellä
$\omega_i$ tiheydestä $p$, saadaan

$$L_o \approx L_e + \frac{f(\omega_i, \omega_o)\,\cos\theta_i}
{p(\omega_i)}\,L_i(\omega_i).$$

Termi $f\cos\theta/p$ on heijastuksen *paino*. Polun radianssi on
summa, jossa jokainen säteilevä pinta kerrotaan kaikkien edeltävien
painojen tulolla. Silmukka pitää yllä painojen tuloa (`kerroin`) ja
kerää säteilyn (`L`). Diffuusilla pinnalla ja kosinipainotetulla
poiminnalla paino on suoraan pinnan väri, koska
$(\rho/\pi)\cos\theta / (\cos\theta/\pi) = \rho$:

```{.cpp tiedosto="esimerkit/yhteinen/materiaali.hpp" osa="poiminta"}
```

Yksinkertaisimmillaan polunseuranta on siis: osu, lisää säteily,
kerro painolla, jatka. Tällä *naiivilla* versiolla on kuitenkin
ongelma. Pieneen valoon osutaan sattumalta harvoin, ja kun osutaan,
osuma on kirkas. Kuva koostuu pimeistä pikseleistä ja yksittäisistä
kirkkaista pisteistä.

## Suora valaistus valolähteen näytteellä

Ratkaisu on jakaa integraali kahtia: suora valo valolähteistä ja
epäsuora valo muilta pinnoilta. Suora valo arvioidaan poimimalla
piste valolähteen pinnalta, ei suuntaa pinnalta, ja epäsuora jatkaa
polkua BRDF:n mukaan mutta ei enää laske valolähteeseen osumista,
koska se on jo laskettu. Menetelmän englanninkielinen nimi on *next
event estimation* (NEE).

Valon pinnalta poimittu piste on tiheydeltään $1/A$ pinta-alaa
kohden. Integraali avaruuskulman yli muunnetaan pinta-alan yli
edellisen luvun kaavalla $d\omega = \cos\theta'\,dA / r^2$, joten
estimaatti on

$$L_\text{suora} \approx \frac{f\,L_e\,\cos\theta\,\cos\theta'}
{r^2\,(1/A)}\,V,$$

missä $V$ on varjosäteen tulos: 1, jos piste näkyy valoon, muuten 0.
Usean valon kohtauksessa valo valitaan pinta-alan mukaan, ja $A$ on
kaikkien valojen yhteispinta-ala. Kolmion tasainen piste saadaan
neliöjuurikuvauksella (Shirley 1990):

```{.cpp tiedosto="esimerkit/yhteinen/polku.hpp" osa="suora"}
```

## Polunseurantasilmukka

```{.cpp tiedosto="esimerkit/yhteinen/polku.hpp" osa="asetukset"}
```

```{.cpp tiedosto="esimerkit/yhteinen/polku.hpp" osa="polku"}
```

Silmukan rakenne:

1. **Osuma.** Jos säde ei osu mihinkään, se näkee taivaan, ja
   taivaan radianssi lisätään painolla.
2. **Säteily.** Pinnan oma säteily lisätään, jos edellinen pomppu ei
   jo laskenut sitä suorana valona (`sateily_mukaan`). Peili ja lasi
   eivät käytä suoraa valoa, koska täydellisen peilin heijastussuunta on
   yksi piste, johon valon näyte osuu todennäköisyydellä nolla.
3. **Suora valo** diffuusilla ja karhealla pinnalla.
4. **Uusi suunta** BRDF:n mukaan, ja paino kerrotaan.
5. **Venäläinen ruletti** lopettaa polun satunnaisesti.

Kohtauksen leikkaus on raakahaku pienissä kohtauksissa:

```{.cpp tiedosto="esimerkit/yhteinen/kohtaus.hpp" osa="kohtaus"}
```

```{.cpp tiedosto="esimerkit/yhteinen/kohtaus.hpp" osa="leikkaa"}
```

Kuva lasketaan pikseli kerrallaan, ja jokaisella pikselillä on oma
satunnaislukuvirta. Pikselin näytteet sijoitetaan satunnaisesti
pikselin alueelle kuten luvussa *Säteet ja kamera*:

```{.cpp tiedosto="esimerkit/yhteinen/polku.hpp" osa="renderoi"}
```

## Cornellin laatikko

Cornellin yliopiston tutkijat rakensivat vuonna 1984 laatikon, jonka
seinät olivat valkoinen, punainen ja vihreä, ja vertasivat valokuvaa
laskettuun kuvaan. Laatikosta tuli polunseurannan vakiotesti, koska
epäsuora valo näkyy siinä selvästi: punainen ja vihreä seinä
värjäävät valkoisen pinnan läheltä.

```{.cpp tiedosto="esimerkit/yhteinen/cornell.hpp" osa="cornell"}
```

Esimerkki vertaa naiivia polunseurantaa ja suoraa valaistusta samalla
näytemäärällä. Vertailukuva on laskettu suoralla valaistuksella ja 128
näytteellä. Vertailukuvissa valolähdettä ei piirretä: muuten sen
reunapikselit, 25 kertaa näytön valkoista kirkkaammat, hallitsisivat
virhettä.

```{.cpp tiedosto="esimerkit/08-polku.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/08-polku.odotettu"}
```

![Cornellin laatikko polunseurannalla ja suoralla valaistuksella.
Valkoiset pinnat saavat sävyä seinistä, ja pallojen alla on pehmeät
varjot.](kuvat/08-polku.png){width=60%}

Suora valaistus maksaa yhden lisäsäteen jokaisella pompulla (3,0
sädettä näytettä kohden 2,1:n sijaan), mutta sen virhe on 15
kertaa pienempi. Saman virheen saavuttaminen naiivilla menetelmällä
vaatisi yli 200 kertaa enemmän näytteitä. Naiivin version keskiarvo
on myös kauempana oikeasta, koska harvat kirkkaat osumat tekevät
keskiarvosta epävakaan, vaikka se on odotusarvoltaan oikea.

## Venäläinen ruletti

Polun pituutta ei voi rajoittaa kiinteästi ilman harhaa: jokainen
pois jätetty pomppu on valoa, joka puuttuu kuvasta. Venäläinen ruletti
jatkaa polkua todennäköisyydellä $q$ ja jakaa painon $q$:lla, jos se
jatkuu. Odotusarvo säilyy, koska $q \cdot (w/q) + (1 - q)\cdot 0 = w$,
mutta lyhyitä polkuja on enemmän. Kun $q$ valitaan painon mukaan,
tummat polut, jotka vaikuttavat kuvaan vähän, katkeavat useimmin.

```{.cpp tiedosto="esimerkit/08-ruletti.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/08-ruletti.odotettu"}
```

Kiinteä syvyys on selvästi harhainen: yhdellä pompulla kuva on 42 %
liian tumma, kolmella 9 % ja viidellä 4 %. Viidenkymmenen pompun
raja on käytännössä harhaton, ja ruletti antaa saman keskiarvon puolta
pienemmällä sädemäärällä. Venäläinen ruletti lisää varianssia, koska
yksittäinen jatkuva polku saa suuremman painon, mutta säästetyllä
laskennalla saa enemmän näytteitä. Raja $q \le 0{,}95$ varmistaa, että
polku katkeaa joskus myös, kun paino ei pienene, kuten kahden peilin
välissä.

## Monitärkeysnäytteistys

Suora valaistus ei ole aina paras strategia. Kun pinta on lähes
peili ja valo suuri, valon pinnalta poimittu piste osuu
harvoin kapeaan heijastuslohkoon, ja kiiltävään pintaan tulee
kirkkaita pisteitä. BRDF:n mukaan poimittu suunta osuisi valoon
helposti. Toisaalta pienelle valolle ja himmeälle pinnalle BRDF:n
poiminta on huono ja valon poiminta hyvä.

Veachin ja Guibasin (1995) *monitärkeysnäytteistys* (MIS, multiple
importance sampling) käyttää molempia strategioita ja painottaa
kunkin näytteen sen mukaan, kuinka todennäköisesti kumpikin
strategia olisi sen tuottanut. Tasapainoheuristiikassa strategian $i$
näytteen paino on

$$w_i(x) = \frac{n_i\,p_i(x)}{\sum_j n_j\,p_j(x)},$$

jolloin estimaatti on
$\sum_i \frac{1}{n_i}\sum_k w_i(x_{ik})\,g(x_{ik}) / p_i(x_{ik})$.
Painot summautuvat yhteen jokaisessa pisteessä, joten estimaatti on
harhaton. Jos jompikumpi strategia on hyvä, sen tiheys on suuri
siellä, missä integrandi on suuri, ja sen näytteet saavat suuren
painon. Esimerkki laskee integraalin $\int L\,b\,d\omega$, jossa $L$ on
kartion muotoinen valo ja $b$ kiiltolohko:

```{.cpp tiedosto="esimerkit/08-mis.cpp" osa="tilanne"}
```

```{.cpp tiedosto="esimerkit/08-mis.cpp" osa="strategiat"}
```

```{.cpp tiedosto="esimerkit/08-mis.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/08-mis.odotettu"}
```

Kumpikin yksittäinen strategia epäonnistuu toisessa tilanteessa
täysin: virhe on monikertainen koko integraaliin verrattuna. MIS on
molemmissa lähellä parasta. Se ei ole aina paras, sillä se käyttää
puolet näytteistä huonompaan strategiaan, mutta se ei koskaan
epäonnistu pahasti, ja renderöijä ei voi tietää etukäteen, kumpi
tilanne pikselissä on. Tämän tutoriaalin polunseurannassa MIS:iä ei
ole, mikä näkyy seuraavan luvun kiiltävissä palloissa kirkkaina
pisteinä. Tuotantorenderöijissä se on aina mukana.

## Käytännössä

- **Käytä suoraa valaistusta valon näytteellä** kaikilla
  ei-peilimäisillä pinnoilla. Laske valoon osuminen mukaan vain
  silloin, kun suoraa valoa ei laskettu.
- **Pidä kirjaa painojen tulosta** ja kerro uusi paino joka
  pompulla. Paino on $f\cos\theta/p$, ja sen on oltava johdonmukainen
  poiminnan kanssa.
- **Lopeta polut venäläisellä ruletilla**, älä kiinteällä syvyydellä.
  Aseta jatkamisen todennäköisyydelle yläraja.
- **Käytä MIS:iä**, kun kohtauksessa on sekä kiiltäviä pintoja että
  suuria valoja. Se on vakuutus pahimpia tapauksia vastaan.
- **Vertaa naiiviin versioon.** Kun suora valaistus tai MIS lisätään,
  kuvan keskiarvon on pysyttävä samana; vain kohinan saa vähentyä.

## Itsearviointi

- Osaat kirjoittaa polunseurantasilmukan, joka kerää säteilyn ja
  pitää yllä polun painoa.
- Osaat toteuttaa suoran valaistuksen valon näytteellä ja muuntaa
  pinta-alan tiheyden avaruuskulman tiheydeksi.
- Osaat perustella venäläisen ruletin harhattomuuden ja selittää,
  miksi kiinteä syvyys tummentaa kuvaa.
- Osaat selittää monitärkeysnäytteistyksen ja tasapainoheuristiikan
  ja tunnistaa tilanteet, joissa yksittäinen strategia epäonnistuu.
