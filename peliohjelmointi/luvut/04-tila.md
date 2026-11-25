# Pelin tila ja tapahtumat

Pelissä on tiloja kaikilla tasoilla: valikko, peli ja tauko; vartija,
joka partioi, ajaa takaa tai etsii; hahmo, joka seisoo, juoksee,
hyppää tai on lyöty. Tilat kannattaa tehdä näkyviksi tilakoneiksi
lippumuuttujien sijaan.

## Tilakone

Tilakoneessa on rajattu joukko tiloja ja siirtymät niiden välillä.
C++:ssa tilat voi kuvata tyyppeinä `std::variant`illa: jokaisella
tilalla on vain omat tietonsa, eikä mahdottomia yhdistelmiä
(takaa-ajo ilman kohdetta) voi syntyä.

```{.cpp tiedosto="esimerkit/04-tilakone.cpp" osa="tilat"}
```

Päivitys käsittelee kunkin tilan omassa haarassaan ja palauttaa
seuraavan tilan. `if constexpr` valitsee haaran käännösaikana, joten
uuden tilan lisääminen ilman käsittelyä on käännösvirhe.

```{.cpp tiedosto="esimerkit/04-tilakone.cpp" osa="siirtymat"}
```

```{.tuloste tiedosto="esimerkit/04-tilakone.odotettu"}
```

```{.dot otsikko="Esimerkin vartija tilakoneena" leveys="70%"}
digraph {
  rankdir=LR; nodesep=0.5;
  node [shape=box, style=rounded];
  partio [label="Partio"]; takaa [label="TakaaAjo"];
  etsinta [label="Etsinta"];
  partio -> takaa [label="näkee"];
  takaa -> etsinta [label="ei näe"];
  etsinta -> takaa [label="näkee"];
  etsinta -> partio [label="3 ruutua kulunut"];
}
```

Tässä vartija elää yksiulotteisella käytävällä ja näkee kaiken
viiden metrin säteellä. Luku *Pelitekoäly* antaa samalle tilakoneelle
kartan, näkölinjan ja reitinhaun. Pelimoottoreissa myös animaatiot
ohjataan yleensä tilakoneella, jonka siirtymät muokataan graafisesti.

## Kohtaukset

Pelin päätason tilat ovat *kohtauksia* (scene, screen): valikko,
pelitaso, taukovalikko, asetukset. Ne pidetään pinossa. Päällimmäinen
saa syötteen, ja läpinäkyvä kohtaus (tauko) piirretään alla olevan
päälle.

```{.cpp tiedosto="esimerkit/04-kohtaukset.cpp" osa="rajapinta"}
```

```{.tuloste tiedosto="esimerkit/04-kohtaukset.odotettu"}
```

Pinon muutokset tehdään vasta ruudun lopussa. Jos tauko poistaisi
itsensä suoraan `syote`-metodissa, olio tuhoutuisi kesken oman
metodinsa suorituksen, mikä on määrittelemätöntä käyttäytymistä. Sama
periaate koskee kaikkia peliolioita: poisto merkitään ja tehdään, kun
kukaan ei käsittele oliota.

## Tapahtumajono

Kun pelaaja kerää kolikon, pitää soittaa ääni, kasvattaa pisteitä,
päivittää saavutukset ja ehkä näyttää partikkeliefekti. Jos keräyslogiikka
kutsuu näitä suoraan, se riippuu kaikista järjestelmistä. Tapahtumajono
kääntää riippuvuuden: logiikka ilmoittaa, mitä tapahtui, ja kiinnostuneet
järjestelmät käsittelevät tapahtumat.

```{.cpp tiedosto="esimerkit/04-tapahtumat.cpp" osa="jono"}
```

```{.cpp tiedosto="esimerkit/04-tapahtumat.cpp" osa="ruudun-loppu"}
```

```{.tuloste tiedosto="esimerkit/04-tapahtumat.odotettu"}
```

Käsittely ruudun lopussa tekee järjestyksestä ennustettavan ja estää
sisäkkäiset kutsuketjut, joissa ääni käynnistää efektin, joka laukaisee
uuden tapahtuman, joka muuttaa juuri käsiteltävää taulukkoa.

## Käytännössä

- **Tilakone** (state) korvaa toisiaan poissulkevat lippumuuttujat
  (`hyppaa`, `kyykkii`, `lyoty`). Siirtymät ovat yhdessä paikassa, ja
  mahdottomat yhdistelmät poistuvat.
- **Kohtauspino** ja **viivästetyt muutokset**: kohtaukset ja oliot
  poistetaan ruudun lopussa, ei kesken käsittelyn.
- **Tapahtumajono** (event queue) tai **havainnoija** (observer)
  irrottaa pelilogiikan esitysjärjestelmistä. Jono on havainnoijaa
  turvallisempi, koska käsittely tapahtuu hallitussa kohdassa.
- **Hinta:** tapahtumat vaikeuttavat koodin seuraamista, koska
  kutsuja ja käsittelijä ovat eri paikoissa. Käytä niitä järjestelmien
  välillä, ei saman järjestelmän sisällä.
- Robert Nystromin kirja *Game Programming Patterns* käsittelee nämä
  mallit perusteellisesti (ks. luku *Lopuksi*).

## Itsearviointi

- Osaat mallintaa hahmon tai tekoälyn tilakoneena, jossa tilat ovat
  tyyppejä.
- Osaat toteuttaa kohtauspinon, jossa muutokset tehdään ruudun lopussa.
- Osaat irrottaa pelilogiikan äänestä ja pisteistä tapahtumajonolla ja
  perustella käsittelyn ajankohdan.
