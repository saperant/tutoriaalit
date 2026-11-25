# Kokonainen peli: Kipinä

*Kipinä* kokoaa edellisten lukujen rakenteet pieneksi peliksi.
Pelaaja ohjaa alusta, kerää kiteitä ja väistää ajelehtivia miinoja.
Miinoja tulee lisää kymmenen sekunnin välein, ja kolmannen osuman
jälkeen peli päättyy. Peli on jaettu niin, että sama logiikka ja
piirto toimivat ilman ikkunaa testissä ja ikkunassa SDL2:lla.

| Tiedosto | Sisältö | Riippuu |
|----------|---------|---------|
| `pcg.hpp` | satunnaislukugeneraattori | – |
| `peli.hpp`, `peli.cpp` | tila ja päivitys | `pcg.hpp` |
| `piirto.hpp`, `piirto.cpp` | ohjelmistopiirto kuvapuskuriin | `peli.hpp` |
| `main.cpp` | ikkunaton ajo tallenteesta | kaikki yllä |
| `sdl/src/kipina-sdl.cpp` | ikkuna, näppäimistö, kello | kaikki yllä, SDL2 |

## Tila ja päivitys

Pelilogiikka tuntee vain toiminnot, kappaleet ja kiinteän askeleen.
Se ei tiedä ikkunoista, kellosta eikä grafiikasta.

```{.cpp tiedosto="esimerkit/12-kipina/peli.hpp" osa="tila"}
```

Satunnaisuus tulee pelin omasta generaattorista, jonka siemen on
osa pelin tilaa (luku *Pelisilmukka*):

```{.cpp tiedosto="esimerkit/12-kipina/pcg.hpp"}
```

Päivitys etenee aina samassa järjestyksessä: pelaajan liike
syötteestä, miinojen liike, keräys, osumat ja vaikeuden kasvu.
Kiinteä järjestys on osa determinismiä.

```{.cpp tiedosto="esimerkit/12-kipina/peli.cpp" osa="paivita"}
```

Osuman jälkeen pelaaja on kaksi sekuntia haavoittumaton. Ilman suojaa
sama miina osuisi seuraavalla ruudulla uudelleen, koska kappaleet ovat
yhä päällekkäin. Kerätty kide korvataan uudella samassa taulukon
paikassa, joten silmukan aikana taulukko ei muutu.

## Piirto

Piirto lukee pelin tilaa ja kirjoittaa kuvapuskuriin. Se ei muuta
pelin tilaa, joten saman tilan voi piirtää vaikka kahdesti.

```{.cpp tiedosto="esimerkit/12-kipina/piirto.hpp"}
```

```{.cpp tiedosto="esimerkit/12-kipina/piirto.cpp" osa="piirra"}
```

Pisteet piirretään omalla 3 × 5 pikselin numerofontilla, joten peli
ei tarvitse fonttikirjastoa. Haavoittumaton pelaaja vilkkuu, ja
vilkunta lasketaan ruutulaskurista, ei kellosta.

## Ajo tallenteesta

Ikkunaton versio lukee syötteen tallenteesta ja ajaa pelin kiinteällä
askeleella. Tämä on samalla pelin regressiotesti: jos pelimekaniikka
muuttuu, tilan ja kuvan tarkistussummat muuttuvat.

```{.cpp tiedosto="esimerkit/12-kipina/main.cpp" osa="silmukka"}
```

```{.text tiedosto="esimerkit/12-kipina.syote"}
```

```{.tuloste tiedosto="esimerkit/12-kipina.odotettu"}
```

Ajo tallentaa lopputilan kuvaksi `kipina.ppm`. Kuvassa vasemmassa
yläkulmassa ovat pisteet ja oikeassa yläkulmassa jäljellä olevat elämät.

![Kipinän lopputila tallenteen jälkeen: pelaaja (sininen), kiteet
(keltaiset) ja miinat (punaiset).](kuvat/kipina.png){width=60%}

![Neljä ruutua saman tallenteen varrelta. Kuvat on tuotettu ajamalla
tallenteen alkua eripituisina paloina: koska peli on deterministinen,
jokainen ajo päätyy samaan tilaan kuin koko tallenne samassa
kohdassa.](kuvat/kipina-sarja.png){width=100%}

## SDL2-etupää

Ikkunaversio lisää vain sen, mitä ikkuna vaatii: tapahtumien
muuntamisen toiminnoiksi, oikean kellon ja kuvan viemisen näytölle.
SDL:n tapahtumista pidetään kirjaa samalla tavalla kuin luvun *Syöte*
toiminnoista.

```{.cpp tiedosto="esimerkit/sdl/src/kipina-sdl.cpp" osa="syote"}
```

Pelisilmukka käyttää SDL:n tarkkaa laskuria kokonaislukuina ja ajaa
kiinteitä askelia kertymästä. Kuvapuskuri kopioidaan tekstuuriin, ja
SDL skaalaa 160 × 120 pikselin kuvan ikkunan kokoon
(`SDL_RenderSetLogicalSize`). Pystytahdistus (`PRESENTVSYNC`) rajaa
piirron näytön tahtiin, eikä peli kuluta suoritinta turhaan.

```{.cpp tiedosto="esimerkit/sdl/src/kipina-sdl.cpp" osa="ikkuna"}
```

Ikkunaa ei voi avata testipalvelimella eikä kontissa. Testitila
käyttää SDL:n dummy-videoajuria ja ohjelmistorenderöijää, joka piirtää
muistissa olevaan pintaan. Testi syöttää näppäintapahtumat SDL:n
jonoon, piirtää ruudut samalla koodilla kuin ikkunaversio ja vertaa
lopuksi pinnan pikseleitä omaan kuvapuskuriin.

```{.cpp tiedosto="esimerkit/sdl/src/kipina-sdl.cpp" osa="esitys"}
```

```{.tuloste tiedosto="esimerkit/sdl/kipina-sdl.odotettu"}
```

SDL2-versio käännetään esimerkkihakemiston Makefilellä, joka hakee
kirjaston liput `sdl2-config`-ohjelmalla:

```{.makefile tiedosto="esimerkit/Makefile" osa="sdl"}
```

`make pelaa` avaa ikkunan, jossa ohjataan nuolinäppäimillä tai
WASD-näppäimillä.

## Käytännössä

- **Ydin ilman alustaa.** Pelilogiikka ja piirto omaan kuvapuskuriin
  ovat alustasta riippumattomia; SDL, konsoli tai selain (WebAssembly)
  on ohut etupää. Samaa periaatetta noudattavat moottoritkin.
- **Tallenne ja tarkistussumma testinä.** Kokonaisen pelin
  regressiotesti ei tarvitse näyttöä eikä ihmistä.
- **Ikkunaton testi oikealla kirjastolla.** SDL:n dummy-ajuri ja
  ohjelmistorenderöijä testaavat tapahtumankäsittelyn ja piirtoketjun
  ilman näytönohjainta.
- **Pystytahdistus ja kiinteä askel yhdessä:** piirto näytön tahdissa,
  simulaatio omassa tahdissaan, interpolointi tarvittaessa välissä.
- **Pienestä valmiiseen:** pieni valmis peli opettaa enemmän kuin suuri
  keskeneräinen. Lisää ominaisuuksia vasta, kun silmukka, syöte ja
  testit toimivat.

## Itsearviointi

- Osaat jakaa pelin logiikkaan, piirtoon ja alustakohtaiseen etupäähän.
- Osaat testata kokonaisen pelin tallennetulla syötteellä ja
  tarkistussummilla.
- Osaat toteuttaa SDL2-etupään kiinteällä askeleella ja testata sen ilman
  näyttöä.
