# Painotetut graafit

Tieverkossa kaarilla on pituudet, tietoverkossa viiveet ja
kaapeloinnissa hinnat. Leveyshaku ei enää riitä, koska vähiten kaaria
sisältävä reitti ei ole välttämättä lyhin. Tässä luvussa on kaksi
tehtävää: *lyhimmät polut* yhdestä lähtösolmusta kaikkiin muihin ja
*pienin virittävä puu*, halvin kaarijoukko, joka yhdistää kaikki
solmut. Molempien perusalgoritmit ovat ahneita, ja molemmissa
binäärikeko (Tietorakenteet, luku 9) tekee ahneesta valinnasta
halvan.

## Relaksaatio

Lyhimpien polkujen algoritmit pitävät yllä arviota $d[v]$, joka on
lyhimmän toistaiseksi löydetyn polun pituus lähtösolmusta solmuun $v$.
Alussa $d[\textrm{lähtö}] = 0$ ja muut ovat äärettömiä. Ainoa operaatio,
joka muuttaa arvioita, on kaaren $u \to v$ *relaksaatio*: jos polku
$u$:n kautta on lyhyempi kuin nykyinen arvio, arvio päivitetään ja
$u$ merkitään $v$:n edeltäjäksi.

$$d[v] \leftarrow \min(d[v],\ d[u] + w(u, v))$$

Arvio ei koskaan alita todellista etäisyyttä, koska se on aina jonkin
olemassa olevan polun pituus. Algoritmit eroavat siinä, missä
järjestyksessä kaaret relaksoidaan: oikeassa järjestyksessä jokainen
kaari tarvitsee relaksoida vain kerran.

## Dijkstran algoritmi

Edsger Dijkstran algoritmi (1959) käsittelee solmut etäisyyden mukaan
kasvavassa järjestyksessä, kuten leveyshaku, mutta etäisyys on nyt
painojen summa. Seuraavaksi käsitellään se solmu, jonka arvio on pienin,
ja sen lähtevät kaaret relaksoidaan. Pienin arvio saadaan keosta.

Esimerkki käyttää kekoa, johon samaa solmua voidaan lisätä monta
kertaa: kun arvio paranee, solmu lisätään uudelleen uudella
etäisyydellä, ja vanhentuneet parit ohitetaan, kun ne tulevat keosta.
Näin keko ei tarvitse operaatiota, joka pienentää olemassa olevan
alkion avainta, ja sen koko on enintään kaarten määrä.

```{.c tiedosto="esimerkit/12-dijkstra.c" osa="dijkstra"}
```

Oikeellisuus on ahneen valinnan perustelu. Kun solmu $u$ otetaan keosta
ensimmäisen kerran, jokainen muu reitti $u$:hun kulkee jonkin keossa
yhä olevan solmun $x$ kautta, ja $d[x] \ge d[u]$. Koska kaaret ovat
ei-negatiivisia, loppumatka $x$:stä $u$:hun ei voi lyhentää reittiä, ja
$d[u]$ on lopullinen. Jokainen kaari relaksoidaan kerran ja jokainen
lisäys kekoon on $O(\log m) = O(\log n)$, joten aika on
$O((n + m) \log n)$.

Tieverkon esimerkissä on kymmenen kaupunkia ja niiden väliset tiet
likimääräisinä kilometreinä:

```{.c tiedosto="esimerkit/12-dijkstra.c" osa="tieverkko"}
```

Kartalla tieverkko ja Dijkstran löytämä lyhimpien reittien puu
Helsingistä (lihavoidut tiet; luvut kilometreinä):

```{.dot otsikko="Esimerkin tieverkko ja lyhimpien reittien puu"}
graph {
  layout=neato; overlap=false; splines=true;
  edge [fontsize=8, color="#B8C4C8"];
  node [shape=box, fontsize=9];
  HKI [label="Helsinki", pos="4,0!"]; TKU [label="Turku", pos="0,0.6!"];
  HML [label="Hämeenlinna", pos="2.8,1.5!"]; LTI [label="Lahti", pos="4.6,1.6!"];
  KVL [label="Kouvola", pos="6.2,1.2!"]; TRE [label="Tampere", pos="2.3,3!"];
  PRI [label="Pori", pos="0.2,3.3!"]; JKL [label="Jyväskylä", pos="4.2,4.4!"];
  MLI [label="Mikkeli", pos="6.6,3.4!"]; KUO [label="Kuopio", pos="6.4,5.4!"];
  TKU -- TRE [label="160"]; TKU -- PRI [label="140"];
  LTI -- TRE [label="130"]; LTI -- MLI [label="125"];
  TRE -- JKL [label="150"]; MLI -- KUO [label="160"];
  JKL -- KUO [label="145"];
  edge [color="#B04848", penwidth=1.8, fontcolor="#B04848"];
  HKI -- HML [label="100"]; HKI -- LTI [label="105"];
  HKI -- TKU [label="165"]; HKI -- KVL [label="135"];
  HML -- TRE [label="75"]; TRE -- PRI [label="110"];
  LTI -- JKL [label="170"]; KVL -- MLI [label="90"];
}
```

```{.tuloste tiedosto="esimerkit/12-dijkstra.odotettu"}
```

Kuopioon on kolme kilpailevaa reittiä: Kouvolan ja Mikkelin kautta
385 km, Lahden ja Mikkelin kautta 390 km ja Jyväskylän kautta 420 km.
Reitit luetaan edeltäjätaulukosta kuten leveyshaussa. Tulosteen
neljäs rivi vertaa Dijkstraa Bellman–Fordin algoritmiin 200
satunnaisella graafilla, joissa on silmukoita, rinnakkaisia kaaria,
nollapainoisia kaaria ja saavuttamattomia solmuja.

## Negatiiviset painot ja Bellman–Ford

Dijkstran perustelu nojasi siihen, ettei loppumatka voi lyhentää
reittiä. Negatiivinen kaari rikkoo tämän. Esimerkin pienessä
graafissa kaaret ovat A → B 2, A → C 3, C → B −2 ja B → D 1:

```{.c tiedosto="esimerkit/12-dijkstra.c" osa="negatiivinen"}
```

Dijkstra ottaa B:n keosta etäisyydellä 2, julistaa sen valmiiksi ja
relaksoi kaaren B → D, jolloin D saa arvon 3. Myöhemmin C:n kautta
löytyy B:hen reitti, jonka pituus on 1, mutta B on jo valmis, eikä sen
kaaria relaksoida uudelleen. D:n oikea etäisyys on 2, ja Dijkstra
antaa 3 ilman mitään varoitusta. Kaikkien painojen kasvattaminen
samalla vakiolla ei korjaa ongelmaa, koska se suosii reittejä, joissa
on vähän kaaria.

Bellman–Fordin algoritmi relaksoi kaikki kaaret $n - 1$ kertaa. Lyhin
polku sisältää enintään $n - 1$ kaarta, ja kierroksen $k$ jälkeen
jokainen enintään $k$ kaaren lyhin polku on löydetty, joten
järjestyksellä ei ole väliä:

```{.c tiedosto="esimerkit/12-dijkstra.c" osa="bellman"}
```

Hinta on aika $O(nm)$, joka on suurilla graafeilla paljon enemmän kuin
Dijkstran. Vastineeksi algoritmi havaitsee *negatiivisen syklin*: jos
$n$:s kierros vielä parantaa jotain arviota, jokin sykli lyhentää
reittiä loputtomasti, eikä lyhintä polkua ole olemassa. Esimerkin
viimeinen rivi lisää kaaren B → C 1, jolloin sykli C → B → C on
pituudeltaan −1. Esimerkki lopettaa myös aikaisin, jos kierros ei
muuta mitään, mikä tekee algoritmista nopean graafeilla, joiden
lyhimmät polut ovat lyhyitä.

Negatiivisia painoja esiintyy, kun painot ovat hyötyjä tai
logaritmeja. Valuuttakurssien arbitraasi on negatiivinen sykli
graafissa, jonka painot ovat kurssien logaritmien vastalukuja.
Etäisyysvektorireititys (RIP) on hajautettu Bellman–Ford, jossa
jokainen reititin relaksoi naapureiltaan saamansa arviot.

## Pienin virittävä puu

Kuuden kylän välille vedetään valokuitu. Mahdollisilla kaivuureiteillä
on hinnat, ja kaikkien kylien on oltava yhteydessä toisiinsa. Halvin
ratkaisu on puu, koska syklin minkä tahansa kaaren voi poistaa
katkaisematta yhteyksiä. Sitä kutsutaan pienimmäksi virittäväksi
puuksi (engl. minimum spanning tree).

Molemmat tunnetut algoritmit ovat ahneita ja perustuvat samaan
*leikkausominaisuuteen*: kun solmut jaetaan kahteen ryhmään, halvin
ryhmien välinen kaari kuuluu johonkin pienimpään virittävään puuhun.
Vaihtoargumentti todistaa sen: jos puussa ei ole tätä kaarta, sen
lisääminen sulkee syklin, joka ylittää leikkauksen myös toista,
kalliimpaa kaarta pitkin, ja tämän kaaren poistaminen antaa
halvemman tai yhtä halvan puun.

**Kruskalin algoritmi** käy kaaret läpi painojärjestyksessä ja ottaa
kaaren, jos se ei sulje sykliä. Syklin tarkistukseen tarvitaan
rakenne, joka pitää kirjaa jo yhdistetyistä solmuryhmistä:
*union-find*. Sen jokaisella ryhmällä on edustaja, puun juuri. Kaksi
solmua ovat samassa ryhmässä, jos niiden edustajat ovat samat, ja
ryhmät yhdistetään liittämällä pienemmän juuri suuremman alle:

```{.c tiedosto="esimerkit/12-virittava.c" osa="unionfind"}
```

Polun puolitus lyhentää puita jokaisessa haussa, ja koon mukaan
yhdistäminen pitää ne matalina. Yhdessä ne tekevät operaatioista
käytännössä vakioaikaisia; tarkka raja on käänteinen
Ackermannin funktio, joka on kaikilla todellisilla syötteillä
enintään neljä. Rakenteen yksityiskohdat ja muut käyttökohteet
kuuluvat taitoon *Edistyneet algoritmit ja tietorakenteet*.

```{.c tiedosto="esimerkit/12-virittava.c" osa="kruskal"}
```

**Primin algoritmi** kasvattaa yhtä puuta: se aloittaa yhdestä solmusta
ja lisää aina halvimman kaaren, joka johtaa puusta sen ulkopuolelle.
Rakenteeltaan se on Dijkstran algoritmi, jossa solmun avain on halvin
puuhun johtava kaari eikä etäisyys lähtösolmusta. Esimerkin versio
etsii pienimmän avaimen taulukosta, mikä on $O(n^2)$ ja tiheillä
graafeilla nopeampi kuin keko:

```{.c tiedosto="esimerkit/12-virittava.c" osa="prim"}
```

```{.tuloste tiedosto="esimerkit/12-virittava.odotettu"}
```

Kruskal valitsee kaaret halvimmasta alkaen: Koski–Salo 2, Mäki–Niemi 6
ja Aho–Kangas 7. Seuraavat kaksi, Aho–Koski 9 ja Niemi–Salo 9,
yhdistävät ryhmät yhdeksi, ja algoritmi lopettaa, kun viisi kaarta on
valittu. Kalliimmat kaaret, kuten Kangas–Koski 10, sulkisivat syklin. Satunnaistesti vertaa
algoritmeja 300 graafilla. Puu on yksikäsitteinen vain, jos painot ovat
erisuuria, joten testi vertaa kokonaishintoja. Epäyhtenäisellä
graafilla virittävää puuta ei ole, ja molempien on ilmoitettava se.

Kruskal on $O(m \log m)$ lajittelun vuoksi ja sopii harvoille
graafeille, joiden kaaret ovat jo listana. Prim keolla on
$O(m \log n)$ ja taulukolla $O(n^2)$, mikä sopii tiheille graafeille.

## Algoritmin valinta

| Tehtävä | Ehto | Algoritmi | Aika |
|---------|------|-----------|------|
| lyhin polku | painottomat kaaret | leveyshaku | $O(n + m)$ |
| lyhin polku | painot $\ge 0$ | Dijkstra keolla | $O((n + m) \log n)$ |
| lyhin polku | negatiiviset painot | Bellman–Ford | $O(nm)$ |
| lyhin polku | syklitön graafi | topologinen järjestys | $O(n + m)$ |
| virittävä puu | harva graafi | Kruskal | $O(m \log m)$ |
| virittävä puu | tiheä graafi | Prim taulukolla | $O(n^2)$ |

Syklittömässä graafissa lyhimmät polut saa relaksoimalla kaaret
topologisessa järjestyksessä (luku 11), myös negatiivisilla painoilla.
Projektinhallinnan kriittisen polun menetelmä on sama algoritmi
pisimmille poluille.

## Käytännössä

- **Dijkstra vain ei-negatiivisille painoille.** Negatiivinen kaari
  antaa väärän vastauksen ilman varoitusta. Tarkista painot syötettä
  luettaessa.
- **Laiska poisto keosta.** Lisää solmu uudelleen paremmalla
  etäisyydellä ja ohita vanhentuneet parit; avaimen pienennystä ei
  tarvita.
- **Bellman–Ford negatiivisille painoille ja syklien havaitsemiseen.**
  $n$:s kierros, joka vielä muuttaa jotain, todistaa negatiivisen
  syklin.
- **Union-find puolituksella ja koolla.** Molemmat optimoinnit ovat
  muutaman rivin mittaisia, ja ilman niitä puut voivat kasvaa
  lineaarisen syviksi.
- **Vertaa kahta algoritmia toisiinsa.** Dijkstra ja Bellman–Ford sekä
  Kruskal ja Prim ratkaisevat saman tehtävän eri tavoin, joten ne ovat
  toistensa testireferenssejä.

## Itsearviointi

- Osaat toteuttaa Dijkstran algoritmin keolla, jossa vanhentuneet
  parit ohitetaan, ja perustella sen oikeellisuuden.
- Osaat näyttää esimerkin, jossa negatiivinen kaari rikkoo Dijkstran,
  ja ratkaista tehtävän Bellman–Fordilla.
- Osaat havaita negatiivisen syklin Bellman–Fordin $n$:nnellä
  kierroksella.
- Osaat toteuttaa Kruskalin algoritmin union-findilla ja Primin
  algoritmin sekä valita niiden välillä graafin tiheyden mukaan.
