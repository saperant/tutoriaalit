# Resurssit ja glTF

Tähän asti verkot ja luurangot on kirjoitettu koodiin. Oikeassa pelissä
ne tehdään mallinnusohjelmassa ja ladataan tiedostosta. Resurssien
elinkaari, kahvat ja välimuisti ovat tuttuja taidosta
*Peliohjelmointi*; tässä luvussa käydään läpi, mitä kolmiulotteinen
resurssi sisältää ja miten se luetaan turvallisesti. Esimerkkinä on
*glTF 2.0*, Khronos-ryhmän avoin tiedostomuoto, jota lähes jokainen
mallinnusohjelma ja pelimoottori osaa kirjoittaa ja lukea.

## Tiedoston rakenne

glTF-resurssi on kaksi tiedostoa: JSON-kuvaus (`.gltf`) ja
binääritiedosto (`.bin`), jossa luvut ovat. Muodossa `.glb` nämä on
pakattu yhdeksi tiedostoksi. Kuvaus koostuu taulukoista, joiden alkiot
viittaavat toisiinsa indekseillä:

```{.dot otsikko="glTF-tiedoston osat. Nuoli tarkoittaa viittausta indeksillä."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.25;
  node [width=0, height=0, margin="0.1,0.06"];
  scene [label="scene"];
  node_ [label="node\n(muunnos,\nlapset)"];
  mesh [label="mesh\n(primitives)"];
  skin [label="skin\n(joints)"];
  anim [label="animation\n(channels,\nsamplers)"];
  mat [label="material"];
  acc [label="accessor\n(tyyppi,\nmäärä)"];
  view [label="bufferView\n(alku,\npituus)"];
  buf [label="buffer\n(.bin)"];
  scene -> node_; node_ -> node_ [label="children"];
  node_ -> mesh; node_ -> skin; mesh -> mat;
  mesh -> acc; skin -> acc; anim -> acc; anim -> node_; skin -> node_;
  acc -> view -> buf;
}
```

Kaikki numeerinen data kulkee saman kolmiportaisen ketjun kautta.
*Buffer* on tavujono, *bufferView* on siitä rajattu pala ja *accessor*
kertoo, miten pala tulkitaan: komponentin tyyppi, komponenttien määrä
alkiota kohden ja alkioiden määrä.

```{.json tiedosto="esimerkit/resurssit/hahmo.gltf" rivit="168-182"}
```

Ensimmäinen accessor on 252 kokonaislukua (`5123` on 16-bittinen
etumerkitön luku): kolmioiden indeksit. Toinen on 56 kolmen
liukuluvun (`5126`) vektoria: kärkien paikat. Paikoille tiedosto kertoo
myös pienimmän ja suurimman arvon, joista saa verkon ympäryslaatikon
lukematta dataa.

Solmut ovat luvun *Muunnoshierarkia* näkymäpuu: nimi, paikallinen
muunnos osina ja luettelo lapsista. Kierto on kvaternio järjestyksessä
(x, y, z, w).

```{.json tiedosto="esimerkit/resurssit/taso.gltf" rivit="26-39"}
```

## Esimerkkien resurssit

Esimerkkien kaksi resurssia tuotetaan skriptillä, jotta niiden sisältö
on kokonaan näkyvissä eikä riipu mallinnusohjelmasta. Skriptin ydin on
luokka, joka kokoaa binääridatan ja kirjoittaa sitä vastaavat
bufferView- ja accessor-oliot:

```{.python tiedosto="esimerkit/resurssit/tee_resurssit.py" osa="puskuri"}
```

Jokainen näkymä alkaa neljällä jaollisesta tavusta, koska muoto vaatii
liukulukujen alkavan omalla tasatulla kohdallaan.

Taso näyttää kaksi tavallista käytäntöä. Sama kuution verkko on monen
solmun käytössä eri muunnoksilla (*instansointi*), ja tyhjät solmut
ovat pelin *merkkejä*: aloituspaikka ja kerättävät lyhdyt ovat tasossa
nimettyinä pisteinä, eivät pelikoodissa lukuina. Tason tekijä voi
siirtää lyhtyä mallinnusohjelmassa kääntämättä peliä.

```{.python tiedosto="esimerkit/resurssit/tee_resurssit.py" osa="taso"}
```

Hahmo tuotetaan samalla tavalla (skriptin funktio `hahmo`). Siinä on
seitsemän nivelen luuranko, laatikoista koottu verkko, jonka jokainen
laatikko on sidottu yhteen niveleen, ja kaksi animaatiota, lepo ja
kävely. Animaatioiden kierrot lasketaan ilman trigonometrisia
funktioita, jotta tiedosto on tavulleen sama jokaisella koneella.

Tiedostot ovat versionhallinnassa, ja esimerkkien Makefile varmistaa,
että ne vastaavat skriptiä:

```{.makefile tiedosto="esimerkit/Makefile" osa="tarkistus"}
```

## Lataus

Lataaja muuntaa tiedoston pelin omiksi rakenteiksi. Peli ei käytä
JSON-puuta eikä tiedostomuodon käsitteitä latauksen jälkeen: jos muoto
vaihtuu, vain lataaja kirjoitetaan uudelleen.

```{.cpp tiedosto="esimerkit/yhteinen/gltf.hpp" osa="rakenteet"}
```

Tiedosto on *epäluotettavaa syötettä*, vaikka se olisi pelin oma.
Vientityökalun virhe, keskeytynyt kopiointi tai käsin muokattu tiedosto
tuottaa indeksejä, jotka osoittavat taulukon ohi, ja accessoreja, jotka
lupaavat enemmän dataa kuin puskurissa on. Jokainen luku tarkistetaan
yhdessä paikassa:

```{.cpp tiedosto="esimerkit/yhteinen/gltf.hpp" osa="lukija"}
```

Solmujen jäsennys on suoraviivaista. Vanhempaa ei ole tiedostossa
erikseen, vaan se päätellään lapsiluetteloista.

```{.cpp tiedosto="esimerkit/yhteinen/gltf.hpp" osa="solmut"}
```

Verkot ja animaatiot luetaan samalla tavalla (funktiot `verkot` ja
`animaatiot` samassa tiedostossa). Verkosta luetaan paikat, indeksit
ja, jos verkko on sidottu luurankoon, nivelet ja painot; jokainen
indeksi tarkistetaan kärkien määrää vastaan. Animaation kanava viittaa
solmuun ja näytteistäjään, joka viittaa kahteen accessoriin: ajat ja
arvot. Ne luetaan suoraan luvun *Luurankoanimaatio* rakenteisiin, ja
kvaternion komponentit järjestetään uudelleen muotoon (w, x, y, z).

Lataus palauttaa joko resurssin tai virheilmoituksen. Rikkinäinen
tiedosto ei saa kaataa peliä eikä varsinkaan lukea muistia puskurin
ulkopuolelta.

```{.cpp tiedosto="esimerkit/yhteinen/gltf.hpp" osa="lataa"}
```

```{.cpp tiedosto="esimerkit/12-gltf.cpp" osa="yhteenveto"}
```

```{.cpp tiedosto="esimerkit/12-gltf.cpp" osa="lataus"}
```

```{.tuloste tiedosto="esimerkit/12-gltf.odotettu" rivit="1-4"}
```

## Solmuista maailmaan

Tiedosto ei lupaa, että vanhempi on taulukossa ennen lasta, joten
maailmamatriisit lasketaan seuraamalla vanhempia tarvittaessa:

```{.cpp tiedosto="esimerkit/yhteinen/gltf.hpp" osa="maailmat"}
```

```{.cpp tiedosto="esimerkit/12-gltf.cpp" osa="instanssit"}
```

```{.tuloste tiedosto="esimerkit/12-gltf.odotettu" rivit="6-21"}
```

Neljästä verkosta syntyy kymmenen kappaletta, ja viisi solmua on
merkkejä.

## Luuranko ja animaatiot

Iho (*skin*) luettelee nivelinä toimivat solmut ja antaa niiden
käänteiset sidontamatriisit. Pelin luurangossa nivelet numeroidaan ihon
järjestyksessä, ja animaatioiden kanavat osoitetaan samoihin numeroihin.

```{.cpp tiedosto="esimerkit/yhteinen/gltf.hpp" osa="luurangoksi"}
```

```{.cpp tiedosto="esimerkit/12-gltf.cpp" osa="luuranko"}
```

```{.tuloste tiedosto="esimerkit/12-gltf.odotettu" rivit="23-31"}
```

Tiedoston käänteiset sidontamatriisit vastaavat niitä, jotka lasketaan
itse lepopoosista. Tarkistus kannattaa: jos ne eroavat, vientityökalu ja
lataaja ovat eri mieltä koordinaatistosta tai matriisien
tallennusjärjestyksestä.

```{.cpp tiedosto="esimerkit/12-gltf.cpp" osa="kavely"}
```

```{.tuloste tiedosto="esimerkit/12-gltf.odotettu" rivit="32-38"}
```

Kävelyssä vasen jalkaterä heilahtaa 41 senttiä eteen ja taakse ja
nousee heilahduksen ääripäissä kymmenen senttiä.

## Rikkinäinen resurssi

```{.cpp tiedosto="esimerkit/12-gltf.cpp" osa="rikki"}
```

```{.tuloste tiedosto="esimerkit/12-gltf.odotettu" rivit="40-41"}
```

Kun binääritiedostosta puuttuu loppu, lataaja kertoo, mikä accessor
yritti lukea ohi ja kuinka paljon. Ilman tarkistusta sama tiedosto
olisi lukenut muistia puskurin jälkeen, ja virhe olisi näkynyt
satunnaisena roskana verkossa tai kaatumisena jossain aivan muualla.

## Tuontiputki

Pelit eivät yleensä lataa glTF-tiedostoja pelin aikana. Vaihtomuoto on
tarkoitettu työkalujen väliseen siirtoon: se on yleinen, ja sen
lukeminen vaatii jäsennystä ja tarkistuksia. *Tuontiputki* muuntaa
resurssit rakennusvaiheessa pelin omaan muotoon, jossa data on valmiiksi
siinä asettelussa, jossa peli ja näytönohjain sitä käyttävät. Samalla
tehdään työ, jota ei haluta tehdä latausruudussa: koordinaatiston ja
yksiköiden muunnos, painojen normalisointi, verkon optimointi,
tekstuurien pakkaus ja törmäysverkon BVH:n rakennus. Tämän luvun
lataaja on se osa putkesta, joka lukee vaihtomuodon.

## Käytännössä

- **Tiedostomuoto pysähtyy lataajaan.** Peli käyttää omia
  rakenteitaan; JSON-puu ja indeksiviittaukset eivät vuoda pelikoodiin.
- **Jokainen indeksi ja pituus tarkistetaan.** Resurssi on syötettä.
  Tarkistus tehdään yhdessä paikassa, jonka läpi kaikki luku kulkee.
- **Virhe on arvo.** Lataus palauttaa virheen, ja peli päättää,
  korvaako se puuttuvan resurssin paikanpitäjällä vai keskeyttääkö.
- **Merkit dataan, ei koodiin.** Aloituspaikat, kerättävät esineet ja
  laukaisualueet ovat tason nimettyjä solmuja.
- **Muunna tuonnissa.** Koordinaatiston, yksiköiden ja
  kvaternioiden järjestyksen erot korjataan kerran, ei pelin aikana.
- **Älä kirjoita JSON-jäsennintä itse.** Jäsennin on valmis ja
  testattu kirjasto; oma työ kohdistuu siihen, mitä data tarkoittaa.

## Itsearviointi

- Osaat kuvata glTF-tiedoston osat ja ketjun accessorista
  bufferView'n kautta puskuriin.
- Osaat lukea accessorin datan niin, ettei rikkinäinen tiedosto voi
  aiheuttaa lukua puskurin ulkopuolelta.
- Osaat muuntaa tiedoston solmut, ihon ja animaatiot pelin omiksi
  rakenteiksi ja tarkistaa sidontamatriisit.
- Osaat perustella, miksi peli käyttää tuontiputkea eikä lataa
  vaihtomuotoa suoraan.
