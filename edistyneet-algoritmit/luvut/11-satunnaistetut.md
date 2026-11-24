# Satunnaistetut algoritmit

Satunnaistettu algoritmi tekee omia arvontojaan. Sen aika tai tulos
on satunnaismuuttuja, mutta jakauma riippuu vain algoritmin
arvonnoista eikä syötteestä. Tämä ero on tärkeä. Keskimääräisen
tapauksen analyysi olettaa, että syöte on satunnainen, mutta
hyökkääjä tai sattumalta järjestetty data rikkoo oletuksen.
Satunnaistettu algoritmi takaa odotusarvonsa jokaiselle syötteelle.

Satunnaistetut algoritmit jaetaan kahteen luokkaan:

- **Las Vegas:** vastaus on aina oikein, ja aika on satunnainen.
  Esimerkkejä ovat pikalajittelu ja pikavalinta satunnaisella
  jakoalkiolla, treap (luku 3) ja skip-lista.
- **Monte Carlo:** aika on rajattu, ja vastaus voi olla väärä
  pienellä todennäköisyydellä. Esimerkkejä ovat Freivaldsin tarkistus,
  Millerin–Rabinin alkulukutesti ja tämän luvun jälkeen
  Bloom-suodatin (luku 12).

Las Vegas -algoritmista saa Monte Carlo -algoritmin keskeyttämällä sen
aikarajaan. Monte Carlo -algoritmin virheen todennäköisyyden saa
pieneksi toistamalla: $k$ riippumatonta toistoa, joista kukin erehtyy
todennäköisyydellä enintään $1/2$, erehtyvät kaikki todennäköisyydellä
enintään $2^{-k}$.

## Skip-lista

*Skip-lista* (Pugh 1990) on järjestetty linkitetty lista, jonka
yläpuolella on harvenevia "pikakaistoja". Jokainen solmu on tasolla 0,
ja kukin solmu nousee seuraavalle tasolle todennäköisyydellä $1/2$.
Tasolla $k$ on siis odotusarvoisesti $n/2^k$ solmua. Haku aloittaa
ylimmältä tasolta, etenee kunnes seuraava avain olisi liian suuri ja
laskeutuu tasoa alemmas. Jokaisella tasolla edetään odotusarvoisesti
yksi askel, joten haku on odotusarvoisesti $O(\log n)$. Yhdenkään
tasapainotuksen ei tarvitse tapahtua.

```{.cpp tiedosto="esimerkit/11-skiplista.cpp" osa="haku"}
```

Lisäys muistaa jokaisen tason viimeisen solmun ennen paikkaa (`polku`)
ja liittää uuden solmun niiden perään:

```{.cpp tiedosto="esimerkit/11-skiplista.cpp" osa="lisays"}
```

Tason arpominen heittää kolikkoa, kunnes tulee kruuna. Omistus kulkee tasolla 0
`std::unique_ptr`-ketjuna, ja ylemmät tasot ovat tavallisia
osoittimia. Purkaja käy ketjun läpi silmukassa, koska
satatuhatta sisäkkäistä `unique_ptr`-purkajaa ylittäisi pinon koon.

Mittaus lisää avaimet järjestyksessä ja tekee 10 000 satunnaista
hakua:

```{.tuloste tiedosto="esimerkit/11-skiplista.odotettu"}
```

Järjestyksessä lisätyt avaimet eivät haittaa, koska tasot arvotaan
avaimista riippumatta. Eteenpäin otettuja askelia on hieman alle
$\log_2 n$, ja korkein taso on hieman yli $\log_2 n$. Skip-listan
vahvuus on rinnakkaisuus. Lisäys muuttaa vain paikallisia linkkejä,
joten lukitsemattomat versiot ovat suhteellisen yksinkertaisia.
Javan `ConcurrentSkipListMap` ja LevelDB:n ja RocksDB:n muistitaulut
ovat skip-listoja.

## Pikavalinta

$k$:nneksi pienimmän alkion löytämiseen ei tarvita lajittelua.
*Pikavalinta* (Hoare 1961) jakaa taulukon jakoalkion ympärille kuten
pikalajittelu, mutta jatkaa vain siihen osaan, jossa $k$:s alkio on.
Jako kolmeen osaan (pienemmät, yhtä suuret ja suuremmat) käsittelee
toistuvat arvot oikein:

```{.cpp tiedosto="esimerkit/11-valinta.cpp" osa="valinta"}
```

Satunnaisella jakoalkiolla jäljelle jäävä osa on odotusarvoisesti
enintään $3/4$ edellisestä, joten vertailuja on odotusarvoisesti
enintään $4n$. Jos jakoalkioksi otetaan aina ensimmäinen alkio,
järjestetty syöte tekee jokaisesta jaosta mahdollisimman huonon.
Valinnan oikeellisuus testataan lajitellun taulukon $k$:nnetta alkiota
vastaan syötteillä, joissa on paljon yhtä suuria arvoja. Sen jälkeen
esimerkki etsii 5000 alkion järjestetyn taulukon mediaanin molemmilla
jakoalkioilla. Ero on yli 500-kertainen (tuloste on alempana). `std::nth_element` käyttää
*introselect*-menetelmää. Se aloittaa pikavalinnalla ja vaihtaa
kekoon perustuvaan valintaan, jos rekursio syvenee liikaa. *Mediaanien
mediaani* (Blum ym. 1973) valitsee jakoalkion deterministisesti
viiden alkion ryhmien mediaaneista ja takaa ajan $O(n)$, mutta sen
vakiokerroin on suuri.

## Freivaldsin tarkistus

Onko $AB = C$? Tulon laskeminen vie ajan $O(n^3)$ suoralla
algoritmilla. Freivaldsin algoritmi (1977) arpoo vektorin
$x \in \{0, 1\}^n$ ja vertaa vektoreita $A(Bx)$ ja $Cx$. Vertailu
vaatii kolme matriisin ja vektorin tuloa, eli ajan $O(n^2)$. Jos
$AB = C$, vektorit ovat aina samat. Jos $AB \ne C$, niiden erotuksen
$D = AB - C$ jokin alkio $d_{ij}$ on nollasta eroava, ja $(Dx)_i = 0$
pätee enintään puolelle vektoreista $x$:

```{.cpp tiedosto="esimerkit/11-valinta.cpp" osa="freivalds"}
```

Esimerkki tarkistaa $60 \times 60$ -matriisien oikean tulon 1000
kertaa yhdellä kierroksella. Sitten se muuttaa tulosta yhden alkion ja
toistaa kokeen yhdellä ja kymmenellä kierroksella:

```{.tuloste tiedosto="esimerkit/11-valinta.odotettu"}
```

Yhdellä kierroksella virheellinen tulo hyväksyttiin noin puolessa
kokeista, kuten raja ennustaa. Kymmenellä kierroksella todennäköisyys
on alle tuhannesosa. Algoritmi on yksipuolinen: oikeaa tuloa se ei
koskaan hylkää. Sama periaate toimii laajemminkin. Laskennan
tarkistaminen on usein paljon halvempaa kuin laskeminen, ja
satunnaistettu tarkistus on tapa testata nopeaa algoritmia suurilla
syötteillä, joille raaka malli on liian hidas.

## Satunnaisuuden lähde

Satunnaistetun algoritmin takuu edellyttää, että arvonnat ovat
riippumattomia syötteestä. Jos hyökkääjä tietää siemenen, se voi
laskea, mitkä jakoalkiot algoritmi valitsee, ja rakentaa pahimman
syötteen. Tämän tutoriaalin esimerkit käyttävät kiinteää siementä,
jotta tulosteet ovat toistettavia. Tuotannossa siemen otetaan
käyttöjärjestelmältä (`std::random_device`, `getrandom`), ja
hajautustauluissa käytetään avaimellista hajautusfunktiota, kuten
SipHashia. Pythonin, Rustin ja Perlin hajautustaulut tekevät näin, koska
ennustettavat hajautusarvot mahdollistavat palvelunestohyökkäyksen.

## Käytännössä

- Satunnaista jakoalkiot ja vastaavat valinnat aina, kun syötteen
  järjestystä ei hallita. Järjestetty data on käytännössä yleisin
  pahin tapaus.
- Tulosta siemen ja salli sen antaminen komentoriviltä. Satunnaistetun
  ohjelman virhe on muuten mahdoton toistaa.
- Monte Carlo -algoritmissa päätä virheen todennäköisyys etukäteen ja
  laske kierrosten määrä siitä. $2^{-40}$ on pienempi kuin
  laitteistovirheen todennäköisyys.
- Skip-lista on hyvä valinta, kun järjestettyä rakennetta käyttää moni
  säie. Yhden säikeen käytössä tasapainotettu puu tai B-puu on yleensä
  nopeampi välimuistin takia.
- Käytä `std::nth_element`-funktiota mediaaniin ja persentiileihin.
  Se on keskimäärin lineaarinen ja muuttaa taulukon niin, että
  $k$:nnen alkion vasemmalla puolella on vain pienempiä tai yhtä
  suuria alkioita.

## Itsearviointi

- Osaat erottaa Las Vegas- ja Monte Carlo -algoritmit ja muuttaa
  virhetodennäköisyyden toistoilla halutun pieneksi.
- Osaat toteuttaa skip-listan ja perustella sen odotetun
  hakuajan tasojen jakaumasta.
- Osaat toteuttaa pikavalinnan kolmijaolla ja perustella, miksi
  satunnainen jakoalkio antaa odotetun lineaarisen ajan.
- Osaat toteuttaa Freivaldsin tarkistuksen ja todistaa sen
  virherajan $1/2$ kierrosta kohden.
- Osaat selittää, miksi satunnaistetun algoritmin siemen on pidettävä
  arvaamattomana, kun syöte tulee ulkoa.
