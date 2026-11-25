# Törmäykset

Törmäysten käsittely on kaksivaiheinen. *Laaja vaihe* (broad phase)
karsii nopeasti parit, jotka eivät voi koskettaa. *Kapea vaihe* (narrow
phase) testaa jäljelle jääneet parit tarkasti ja laskee, miten
kappaleet erotetaan. Tämä luku tunnistaa törmäykset; se, mitä
osuman jälkeen tapahtuu (pysähtyminen, kimpoaminen, pinoutuminen), on
seuraavan luvun aihe.

## Perusmuodot

Pelien törmäysmuodot ovat yksinkertaisempia kuin piirretty grafiikka:
laatikoita, ympyröitä ja kapseleita. Akselien suuntainen laatikko
(AABB, axis-aligned bounding box) on nopein. Kahden laatikon
päällekkäisyys selviää vertaamalla kummallakin akselilla
keskipisteiden etäisyyttä puolikokojen summaan.

```{.cpp tiedosto="esimerkit/07-muodot.cpp" osa="aabb"}
```

Funktio palauttaa myös *erottavan siirtymän* (minimum translation
vector): lyhimmän työnnön, jolla pelaaja irtoaa seinästä. Lyhin suunta
on se akseli, jolla päällekkäisyys on pienin.

```{.cpp tiedosto="esimerkit/07-muodot.cpp" osa="ympyra"}
```

```{.tuloste tiedosto="esimerkit/07-muodot.odotettu"}
```

Ympyröiden vertailu tehdään neliöinä, jolloin neliöjuurta ei tarvita.
Ympyrän ja laatikon testi etsii laatikon lähimmän pisteen ympyrän
keskipisteestä.

![Esimerkin tapaukset mittakaavassa. Vasemmalla pelaajan laatikko
työnnetään seinästä lyhintä tietä: sivulta tullut sivulle, ylhäältä
tullut ylös. Oikealla pallo ei kosketa seinää, koska lähin piste on
säteen ulkopuolella, mutta pallot koskettavat
toisiaan.](kuvat/tormaysmuodot.png){width=90%}

## Erottavan akselin lause

Kahdella kuperalla kappaleella ei ole leikkausta, jos löytyy akseli,
jolle projisoidut välit ovat erillään. Monikulmioilla riittää kokeilla
kaikkien särmien normaalit (*separating axis theorem*, SAT). Jos
erottavaa akselia ei löydy, pienin limitys kertoo erottavan siirtymän.

```{.cpp tiedosto="esimerkit/07-sat.cpp" osa="sat"}
```

```{.tuloste tiedosto="esimerkit/07-sat.odotettu"}
```

Samassa paikassa oleva laatikko törmää kolmioon, mutta 45 astetta
kierretty ei: AABB-testi kiertyneen kappaleen ympärille olisi antanut
väärän tuloksen. SAT on kierrettyjen laatikoiden ja kuperien
monikulmioiden perustesti 2D:ssä. Koverat muodot jaetaan kuperiksi
paloiksi.

## Laaja vaihe

Kaikkien parien testaus on O(n²). 2000 kappaleella se on lähes kaksi
miljoonaa testiä ruudussa. *Tasainen ruudukko* jakaa maailman soluihin,
ja vain samassa tai viereisessä solussa olevat kappaleet testataan.

```{.cpp tiedosto="esimerkit/07-laajavaihe.cpp" osa="ruudukko"}
```

```{.tuloste tiedosto="esimerkit/07-laajavaihe.odotettu"}
```

![Laajan vaiheen periaate kahdellakymmenellä kappaleella. Viivat ovat
kapean vaiheen testejä: vasemmalla kaikki parit, oikealla vain parit,
joiden kappaleet ovat samassa tai viereisessä
solussa.](kuvat/ruudukko.png){width=85%}

Testejä on 435 kertaa vähemmän, ja tulos on sama. Ruudukko toimii, kun
kappaleet ovat suunnilleen samankokoisia ja tasaisesti jakautuneita.
Erikokoisille kappaleille sopivat *nelipuu* (quadtree), joka jakaa
tiheät alueet tarkemmin, tai *pyyhkäisy ja karsinta* (sweep and prune),
joka lajittelee kappaleiden välit yhdellä akselilla. Fysiikkamoottorit
käyttävät usein dynaamista rajauslaatikkopuuta (BVH).

## Tunneloituminen

Diskreetti törmäystesti katsoo vain askeleen loppupisteen. Kappale,
joka liikkuu askeleessa pidemmälle kuin seinä on paksu, hyppää seinän
yli (*tunneling*).

```{.cpp tiedosto="esimerkit/07-tunnelointi.cpp" osa="diskreetti"}
```

*Pyyhkäisytesti* (swept test) leikkaa koko liikkeen janan seinän
kanssa ja palauttaa osuman ajan askeleen sisällä.

```{.cpp tiedosto="esimerkit/07-tunnelointi.cpp" osa="pyyhkaisy"}
```

```{.tuloste tiedosto="esimerkit/07-tunnelointi.odotettu"}
```

![Kappaleen paikka askelten lopussa. Hidas kappale pysähtyy askeleen
lopussa seinän kohdalle, nopea on seinän edessä ja seuraavalla
askeleella jo sen takana.](kuvat/tunnelointi.png){width=90%}

60 m/s:n kappale liikkuu askeleessa metrin ja osuu, 420 m/s:n kappale
seitsemän metriä ja ohittaa 20 senttimetrin seinän. Ammukset
kannattaa käsitellä säteinä (raycast), ja fysiikkamoottoreissa nopeille
kappaleille kytketään jatkuva törmäystunnistus (CCD).

## Käytännössä

- **Törmäysmuoto erikseen grafiikasta.** Pelaajan laatikko on usein
  spriteä pienempi, jotta osumat tuntuvat reiluilta.
- **Erota ennen vastetta.** Siirrä kappale ensin irti (MTV), sitten
  muuta nopeutta (pysäytys, kimpoaminen tai liukuminen seinää pitkin).
  Seuraava luku toteuttaa molemmat.
- **Törmäyskerrokset ja -maskit:** ammus ei osu ampujaansa, kolikot
  eivät törmää toisiinsa. Moottoreissa nämä ovat asetuksia.
- **Hinta:** laaja vaihe maksaa ylläpidon (rakenne päivitetään, kun
  kappaleet liikkuvat). Alle sadalla kappaleella kaikkien parien
  testaus voi olla nopeampi.

## Itsearviointi

- Osaat testata laatikoiden, ympyröiden ja niiden yhdistelmien
  törmäykset ja laskea erottavan siirtymän.
- Osaat toteuttaa erottavan akselin testin kuperille monikulmioille.
- Osaat rakentaa laajan vaiheen ruudukolla ja kertoa, milloin nelipuu tai
  pyyhkäisy ja karsinta sopii paremmin.
- Osaat tunnistaa tunneloitumisen ja estää sen pyyhkäisytestillä.
