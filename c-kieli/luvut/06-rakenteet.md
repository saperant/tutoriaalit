# Rakenteet, luettelot ja unionit {.runko-omat-tyypit}

Perustyypeistä kootaan omia tyyppejä kolmella rakennuspalikalla:
rakenne yhdistää useita kenttiä yhdeksi olioksi, luettelo antaa
kokonaislukuarvoille nimet ja unioni sallii saman muistin tulkinnan
usealla tavalla. Rakenteet ja osoittimet yhdessä ovat pohja kaikille
seuraavien lukujen tietorakenteille: viipaleelle, kasvavalle taulukolle
ja läpinäkymättömälle tyypille.

## Rakenteet

*Rakenne* (`struct`) kokoaa useita eri tyyppisiä kenttiä yhdeksi
olioksi. Rakenteen tyypin nimi on `struct nimi`. Usein sille annetaan
lyhyempi nimi `typedef`-määrittelyllä:

```{.c tiedosto="esimerkit/06-rakenteet.c" osa="maarittely"}
```

Kenttiin viitataan pisteellä (`p.x`) ja osoittimen kautta nuolella
(`k->vakiluku`, joka tarkoittaa samaa kuin `(*k).vakiluku`). Rakenteita
voi sijoittaa, välittää ja palauttaa arvoina, jolloin koko sisältö
kopioidaan. Toisin kuin taulukot, rakenteet eivät muutu osoittimiksi.

Pienet rakenteet, kuten kaksiulotteinen piste, välitetään luontevasti
arvoina. Suuremmat rakenteet välitetään osoittimina kopioinnin
välttämiseksi, ja `const` kertoo, muuttaako funktio rakennetta:

```{.c tiedosto="esimerkit/06-rakenteet.c" osa="funktiot"}
```

Rakenteen voi alustaa kentät järjestyksessä luettelemalla tai C99:n
nimetyillä alustimilla, jotka ovat selkeämpiä ja kestävät kenttien
järjestyksen muuttamisen. Mainitsematta jääneet kentät alustetaan
nolliksi. *Yhdistetty literaali* `(struct piste){1, 1}` luo nimettömän
olion lausekkeen keskelle:

```{.c tiedosto="esimerkit/06-rakenteet.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-rakenteet.odotettu"}
```

Kenttä `nimi` on merkkitaulukko, johon merkkijono mahtuu; taulukoita
ja merkkijonoja käsittelee seuraava luku. Rakenteen sisällä oleva
taulukko kopioituu sijoituksessa mukana. Jos rakenteessa on osoitin,
vain osoitin kopioituu, ja molemmat rakenteet osoittavat samaan dataan.
Tämän seurauksiin palataan dynaamisen muistinhallinnan yhteydessä.

### Rakenne, joka viittaa toiseen samanlaiseen

Rakenne ei voi sisältää itseään, mutta se voi sisältää osoittimen omaan
tyyppiinsä. Näin oliot voidaan ketjuttaa:

```{.c tiedosto="esimerkit/06-rakenteet.c" osa="solmu"}
```

```{.c tiedosto="esimerkit/06-rakenteet.c" osa="ketju"}
```

Ohjelman viimeinen tulosterivi on `ketju: 10 20 30`. Silmukka seuraa
`seuraava`-osoittimia, kunnes vastaan tulee tyhjä osoitin:

```{.dot otsikko="Kolme solmua ketjuna. Jokainen solmu sisältää arvon ja seuraavan solmun osoitteen; viimeisen osoitin on tyhjä."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.5;
  node [shape=record, style="filled", height=0.35];
  a [label="{<v> 10 | <n> seuraava}"];
  b [label="{<v> 20 | <n> seuraava}"];
  c [label="{<v> 30 | <n> nullptr}"];
  alku [label="&ensimmainen", shape=plain, style=""];
  alku -> a:v;
  a:n:e -> b:v:w;
  b:n:e -> c:v:w;
}
```

Samalla periaatteella rakennetaan linkitetyt listat, puut ja verkot.
Niiden toteutusta ja valintaa käsittelee taito *Tietorakenteet*.

### Muistiasettelu

Kääntäjä sijoittaa kentät muistiin esittelyjärjestyksessä, mutta lisää
niiden väliin *täytettä* (*padding*), jotta kukin kenttä on
suorittimelle sopivassa osoitteessa. Esimerkiksi 8-tavuinen kokonaisluku
sijoitetaan 8:lla jaolliseen osoitteeseen. Kenttien järjestys vaikuttaa
siksi rakenteen kokoon:

```{.c tiedosto="esimerkit/06-asettelu.c" osa="asettelu"}
```

Esimerkkiohjelma tulostaa kummankin rakenteen koon ja *tavukartan*:
jokainen merkki on yksi tavu, kirjain kertoo kentän ja piste on
täytettä. Kartta lasketaan `offsetof`- ja `sizeof`-arvoista, joten se
näyttää sen asettelun, jonka kääntäjä todella valitsi. Tuloste
x86-64-arkkitehtuurilla:

```{.tuloste tiedosto="esimerkit/06-asettelu.odotettu"}
```

Rakenteessa `huono` kentän `a` jälkeen on seitsemän tavua täytettä,
jotta `b` alkaa kahdeksalla jaollisesta siirtymästä. Loppuun tulee
vielä seitsemän tavua, jotta rakenteen koko on sen suurimman kentän
kohdistuksen monikerta; muuten taulukon seuraava alkio alkaisi
väärästä kohdasta. Rakenteessa `hyva` samat kentät vievät kolmanneksen
vähemmän tilaa.

Makro `offsetof` (`<stddef.h>`) kertoo kentän etäisyyden rakenteen
alusta. Täytteen vuoksi rakenteita ei pidä vertailla `memcmp`-funktiolla
eikä kirjoittaa sellaisinaan tiedostoon, jota luetaan toisella
alustalla.

## Luettelot

*Luettelo* (`enum`) määrittelee joukon nimettyjä kokonaislukuvakioita.
Arvot alkavat nollasta, ellei niitä anneta itse.

```{.c tiedosto="esimerkit/06-luettelot.c" osa="enum"}
```

Kun `switch` käsittelee luettelon arvoja ilman `default`-haaraa,
`-Wall` varoittaa puuttuvista arvoista. Uuden arvon lisääminen
luetteloon paljastaa näin kaikki kohdat, joita on päivitettävä:

```{.c tiedosto="esimerkit/06-switch.ei-kaanny.c"}
```

Luettelon arvoja käytetään usein bittilippuina, joita yhdistellään
operaattorilla `|` ja testataan operaattorilla `&`. C23:ssa luettelon
perustyypin voi määrätä, jolloin sen koko on tiedossa:

```{.c tiedosto="esimerkit/06-luettelot.c" osa="liput"}
```

## Unionit

*Unionin* kaikki jäsenet sijaitsevat samassa muistipaikassa, ja unionin
koko on sen suurimman jäsenen koko. Unionissa on siis kerrallaan
voimassa vain yksi jäsen. C ei pidä kirjaa siitä, mikä jäsen on
voimassa, joten unioni yhdistetään yleensä luetteloon, joka kertoo sen.
Tällaista rakennetta kutsutaan *merkityksi unioniksi* (*tagged union*).

```{.c tiedosto="esimerkit/06-luettelot.c" osa="unioni"}
```

Nimetön unioni (C11) sallii jäsenten käytön suoraan rakenteen kautta:
`a->luku` eikä `a->arvo.luku`.

```{.c tiedosto="esimerkit/06-luettelot.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-luettelot.odotettu"}
```

Merkitty unioni on C:n tapa esittää arvo, joka voi olla yksi monesta
tyypistä, esimerkiksi tulkin arvot tai jäsennyspuun solmut. Ohjelmoijan
vastuulla on lukea vain sitä jäsentä, jonka merkki ilmoittaa.

## Käytännössä

- **Nimetyt alustimet** aina, kun kenttiä on enemmän kuin kaksi. Ne
  kestävät kenttien järjestyksen muutokset ja nollaavat mainitsematta
  jääneet kentät.
- **Pienet rakenteet arvona, suuret `const`-osoittimena.** Raja on
  muutaman konesanan luokkaa; esimerkiksi kaksiulotteinen piste kulkee
  arvona, kaupunkitietue osoittimena.
- **Johdonmukainen `typedef`-käytäntö.** Osa projekteista (esimerkiksi
  Linux-ydin) välttää `typedef struct` -nimiä, jotta rakenne erottuu
  koodissa. Toiset käyttävät niitä aina. Kumpikin on hyvä, kunhan valinta
  on yhtenäinen.
- **Merkitty unioni ja kattava `switch`.** Kun merkki on luettelo ja
  `switch` käsittelee sen kaikki arvot ilman `default`-haaraa, kääntäjä
  varoittaa jokaisesta uudesta, käsittelemättömästä arvosta.
- **Kenttien järjestys** suurimmasta pienimpään vähentää täytettä.
  Rakenteita ei kirjoiteta sellaisinaan tiedostoon tai verkkoon (luku 10).
- **Bittikentät** säästävät tilaa, mutta niiden asettelu riippuu
  kääntäjästä. Laitteistorekistereihin ja tiedostomuotoihin käytetään
  maskeja ja bittisiirtoja (luku 3).

## Itsearviointi

- Osaat alustaa rakenteen nimetyillä alustimilla ja yhdistetyllä
  literaalilla.
- Osaat toteuttaa merkityn unionin ja käsitellä sen kattavasti
  `switch`-lauseella.
- Osaat ketjuttaa rakenteita osoittimilla ja käydä ketjun läpi.
- Osaat arvioida rakenteen koon täytteineen ja järjestää kentät
  tehokkaammin.
