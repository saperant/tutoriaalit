# Rakenteet, luettelot ja unionit

## Rakenteet

*Rakenne* (`struct`) kokoaa useita eri tyyppisiä kenttiä yhdeksi
olioksi. Rakenteen tyypin nimi on `struct nimi`. Usein sille annetaan
lyhyempi nimi `typedef`-määrittelyllä:

```{.c tiedosto="esimerkit/07-rakenteet.c" osa="maarittely"}
```

Kenttiin viitataan pisteellä (`p.x`) ja osoittimen kautta nuolella
(`k->vakiluku`, joka tarkoittaa samaa kuin `(*k).vakiluku`). Rakenteita
voi sijoittaa, välittää ja palauttaa arvoina, jolloin koko sisältö
kopioidaan. Toisin kuin taulukot, rakenteet eivät muutu osoittimiksi.

Pienet rakenteet, kuten kaksiulotteinen piste, välitetään luontevasti
arvoina. Suuremmat rakenteet välitetään osoittimina kopioinnin
välttämiseksi, ja `const` kertoo, muuttaako funktio rakennetta:

```{.c tiedosto="esimerkit/07-rakenteet.c" osa="funktiot"}
```

Rakenteen voi alustaa kentät järjestyksessä luettelemalla tai C99:n
nimetyillä alustimilla, jotka ovat selkeämpiä ja kestävät kenttien
järjestyksen muuttamisen. Mainitsematta jääneet kentät alustetaan
nolliksi. *Yhdistetty literaali* `(struct piste){1, 1}` luo nimettömän
olion lausekkeen keskelle:

```{.c tiedosto="esimerkit/07-rakenteet.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-rakenteet.odotettu"}
```

Rakenteen sisällä oleva taulukko, kuten `nimi`, kopioituu sijoituksessa
mukana. Jos rakenteessa on osoitin, vain osoitin kopioituu, ja
molemmat rakenteet osoittavat samaan dataan, kuten edellisen luvun
viimeisessä esimerkissä.

### Muistiasettelu

Kääntäjä sijoittaa kentät muistiin esittelyjärjestyksessä, mutta lisää
niiden väliin *täytettä* (*padding*), jotta kukin kenttä on
suorittimelle sopivassa osoitteessa. Esimerkiksi 8-tavuinen kokonaisluku
sijoitetaan 8:lla jaolliseen osoitteeseen. Kenttien järjestys vaikuttaa
siksi rakenteen kokoon:

```{.c tiedosto="esimerkit/07-asettelu.c" osa="asettelu"}
```

```{.c tiedosto="esimerkit/07-asettelu.c" osa="kaytto"}
```

Tuloste x86-64-arkkitehtuurilla:

```{.tuloste tiedosto="esimerkit/07-asettelu.odotettu"}
```

Makro `offsetof` (`<stddef.h>`) kertoo kentän etäisyyden rakenteen
alusta. Täytteen vuoksi rakenteita ei pidä vertailla `memcmp`-funktiolla
eikä kirjoittaa sellaisinaan tiedostoon, jota luetaan toisella
alustalla.

## Luettelot

*Luettelo* (`enum`) määrittelee joukon nimettyjä kokonaislukuvakioita.
Arvot alkavat nollasta, ellei niitä anneta itse.

```{.c tiedosto="esimerkit/07-luettelot.c" osa="enum"}
```

Kun `switch` käsittelee luettelon arvoja ilman `default`-haaraa,
`-Wall` varoittaa puuttuvista arvoista. Uuden arvon lisääminen
luetteloon paljastaa näin kaikki kohdat, joita on päivitettävä:

```{.c tiedosto="esimerkit/07-switch.ei-kaanny.c"}
```

Luettelon arvoja käytetään usein bittilippuina, joita yhdistellään
operaattorilla `|` ja testataan operaattorilla `&`. C23:ssa luettelon
perustyypin voi määrätä, jolloin sen koko on tiedossa:

```{.c tiedosto="esimerkit/07-luettelot.c" osa="liput"}
```

## Unionit

*Unionin* kaikki jäsenet sijaitsevat samassa muistipaikassa, ja unionin
koko on sen suurimman jäsenen koko. Unionissa on siis kerrallaan
voimassa vain yksi jäsen. C ei pidä kirjaa siitä, mikä jäsen on
voimassa, joten unioni yhdistetään yleensä luetteloon, joka kertoo sen.
Tällaista rakennetta kutsutaan *merkityksi unioniksi* (*tagged union*).

```{.c tiedosto="esimerkit/07-luettelot.c" osa="unioni"}
```

Nimetön unioni (C11) sallii jäsenten käytön suoraan rakenteen kautta:
`a->luku` eikä `a->arvo.luku`.

```{.c tiedosto="esimerkit/07-luettelot.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-luettelot.odotettu"}
```

Merkitty unioni on C:n tapa esittää arvo, joka voi olla yksi monesta
tyypistä, esimerkiksi tulkin arvot tai jäsennyspuun solmut. Ohjelmoijan
vastuulla on lukea vain sitä jäsentä, jonka merkki ilmoittaa.
