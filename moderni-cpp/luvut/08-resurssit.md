# Resurssienhallinta {.runko-muisti}

C++:ssa ei ole roskienkerääjää. Muisti, tiedostokahvat, lukot ja
verkkoyhteydet on vapautettava, kun niitä ei enää tarvita. Moderni C++
ratkaisee tämän sitomalla resurssin olion elinkaareen.

## RAII

*RAII* (*Resource Acquisition Is Initialization*) tarkoittaa, että
resurssi hankitaan olion muodostimessa ja vapautetaan sen hajottimessa.
Kieli takaa, että paikallisen olion hajotinta kutsutaan, kun olio
poistuu näkyvyysalueeltaan, poistuttiinpa siitä normaalisti,
`return`-lauseella tai poikkeuksen vuoksi.

Seuraava luokka tulostaa viestin, kun resurssi hankitaan ja vapautetaan:

```{.cpp tiedosto="esimerkit/08-raii.cpp" osa="jaljitin"}
```

```{.cpp tiedosto="esimerkit/08-raii.cpp" osa="poikkeus"}
```

```{.cpp tiedosto="esimerkit/08-raii.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-raii.odotettu"}
```

Oliot tuhotaan päinvastaisessa järjestyksessä kuin ne luotiin.
Myös poikkeustilanteessa molemmat resurssit vapautetaan ennen kuin
poikkeus saavuttaa `catch`-lohkon. Kutsuvan koodin ei tarvitse tietää,
mitä resursseja funktio käytti.

RAII toimii myös C-kirjastojen kanssa. Alla `std::unique_ptr` saa
omaksi *vapauttajakseen* (*deleter*) funktio-olion, joka kutsuu
`fclose`-funktiota:

```{.cpp tiedosto="esimerkit/08-raii.cpp" osa="tiedosto"}
```

Standardikirjasto käyttää RAII:ta kaikkialla: `std::vector` ja
`std::string` vapauttavat muistinsa, `std::ifstream` sulkee
tiedostonsa ja `std::scoped_lock` vapauttaa lukkonsa.

## Älykkäät osoittimet

Modernissa C++:ssa `new`- ja `delete`-operaatioita ei yleensä
kirjoiteta itse. Dynaamisesti varattu olio annetaan *älykkään
osoittimen* omistukseen, ja älykäs osoitin vapauttaa sen.

| Tyyppi | Omistus | Käyttö |
|--------|---------|--------|
| `std::unique_ptr<T>` | yksi omistaja | oletusvalinta |
| `std::shared_ptr<T>` | jaettu, viitelaskenta | kun omistajia on useita |
| `std::weak_ptr<T>` | ei omista | viittaus jaettuun olioon ilman omistusta |
| `T*` tai `T&` | ei omista | lainaus, kun omistus on muualla |

### `std::unique_ptr`

`std::unique_ptr` on yhtä kevyt kuin tavallinen osoitin, mutta se
vapauttaa olion automaattisesti. Olio luodaan funktiolla
`std::make_unique`:

```{.cpp tiedosto="esimerkit/08-unique.cpp" osa="tehdas"}
```

Funktion parametrin tyyppi kertoo, mitä funktio tekee oliolle.
Viittaus tai tavallinen osoitin tarkoittaa lainaamista, `unique_ptr`
arvona tarkoittaa omistuksen ottamista:

```{.cpp tiedosto="esimerkit/08-unique.cpp" osa="lainaus"}
```

```{.cpp tiedosto="esimerkit/08-unique.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-unique.odotettu"}
```

`unique_ptr`:ää ei voi kopioida, koska silloin olisi kaksi omistajaa.
Omistus siirretään funktiolla `std::move`, jota käsitellään tarkemmin
seuraavassa luvussa:

```{.cpp tiedosto="esimerkit/08-unique-kopio.ei-kaanny.cpp"}
```

### `std::shared_ptr` ja `std::weak_ptr`

`std::shared_ptr` sallii useita omistajia. Se pitää kirjaa omistajien
määrästä, ja olio vapautetaan, kun viimeinen omistaja tuhoutuu.
Olio luodaan funktiolla `std::make_shared`, joka varaa olion ja
viitelaskurin samalla kertaa.

```{.cpp tiedosto="esimerkit/08-shared.cpp" osa="laskuri"}
```

Laskurit ovat erillisessä *ohjauslohkossa*, johon jokainen `shared_ptr`
osoittaa olion lisäksi. Vahva laskuri kertoo omistajien määrän, ja
heikko laskuri pitää kirjaa `weak_ptr`-viittauksista.

```{.dot otsikko="Yksinomainen ja jaettu omistus. `unique_ptr` on pelkkä osoitin; `shared_ptr`-kopiot jakavat ohjauslohkon, jonka vahva laskuri kertoo omistajien määrän."}
digraph {
  rankdir=TB; nodesep=0.3; ranksep=0.4;
  node [shape=box, fontsize=10];
  subgraph cluster_u {
    label="std::unique_ptr"; fontsize=10; style=rounded;
    u [label="unique_ptr p"];
    uo [label="olio", style=filled, fillcolor="#e8eef7"];
    u -> uo [label="omistaa"];
  }
  subgraph cluster_s {
    label="std::shared_ptr"; fontsize=10; style=rounded;
    b [label="shared_ptr b"];
    a [label="shared_ptr a"];
    ol [label="ohjauslohko\nvahvat: 2\nheikot: 0"];
    so [label="olio", style=filled, fillcolor="#e8eef7"];
    a -> ol; b -> ol;
    ol -> so [label="omistaa"];
  }
}
```

Viitelaskennan heikkous ovat *syklit*. Jos kaksi oliota omistaa
toisensa `shared_ptr`:n kautta, kummankaan laskuri ei koskaan laske
nollaan, ja muisti vuotaa. Sykli katkaistaan `std::weak_ptr`:llä, joka
viittaa olioon omistamatta sitä. Ennen käyttöä `weak_ptr` muutetaan
väliaikaisesti `shared_ptr`:ksi metodilla `lock`, joka palauttaa
tyhjän osoittimen, jos olio on jo tuhottu.

```{.cpp tiedosto="esimerkit/08-shared.cpp" osa="solmut"}
```

```{.cpp tiedosto="esimerkit/08-shared.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-shared.odotettu"}
```

```{.dot otsikko="Vasemmalla omistussykli: kumpikin olio pitää toisen laskurin ykkösenä, eikä kumpaakaan vapauteta. Oikealla lapsen viittaus on `weak_ptr` (katkoviiva), joka ei kasvata vahvaa laskuria."}
digraph {
  rankdir=TB; nodesep=0.6; ranksep=0.5;
  node [shape=box, fontsize=10];
  subgraph cluster_sykli {
    label="sykli: muisti vuotaa"; fontsize=10; style=rounded;
    v1 [label="Vanhempi\nvahvat: 1"];
    l1 [label="Lapsi\nvahvat: 1"];
    v1 -> l1 [label="shared_ptr"];
    l1 -> v1 [label="shared_ptr"];
  }
  subgraph cluster_weak {
    label="weak_ptr katkaisee syklin"; fontsize=10; style=rounded;
    v2 [label="Vanhempi\nvahvat: 0 → tuhotaan"];
    l2 [label="Lapsi\nvahvat: 1 → 0"];
    v2 -> l2 [label="shared_ptr"];
    l2 -> v2 [label="weak_ptr", style=dashed];
  }
}
```

Vanhempi omistaa lapsensa, mutta lapsi vain tuntee vanhempansa. Kun
lohko päättyy, vanhemman laskuri laskee nollaan, vanhempi tuhoutuu ja
sen mukana lapsiluettelo, jolloin myös lapsen laskuri laskee nollaan.

`shared_ptr` on hyödyllinen, mutta se tekee omistussuhteista
vaikeammin hahmotettavia, ja sen laskurin päivitys on atominen
operaatio. Kannattaa aloittaa `unique_ptr`:llä ja siirtyä jaettuun
omistukseen vain, kun siihen on todellinen tarve.

## Käytännössä

- **Ei paljaita `new`- ja `delete`-kutsuja.** Olio luodaan funktioilla
  `std::make_unique` tai `std::make_shared`, tai se sijoitetaan
  säiliöön. Paljas `new` on paikallaan vain uuden RAII-tyypin sisällä
  (Core Guidelines R.11).
- **Omistus näkyy tyypistä.** `std::unique_ptr<T>`-parametri ottaa
  omistuksen, `T&` ja `T*` lainaavat, ja `std::shared_ptr<T>` arvona jakaa
  omistuksen. Tavallinen osoitin ei koskaan omista. Kun tyypit noudattavat
  tätä sopimusta, koodista näkee, kuka vapauttaa minkäkin.
- **`shared_ptr` vain todelliseen jaettuun omistukseen.** Jos funktio vain
  käyttää oliota, se ottaa `T&`:n tai `const T&`:n, ei `shared_ptr`:ää.
  Jokainen `shared_ptr`-kopio päivittää laskurin atomisesti, ja jaettu
  omistus vaikeuttaa elinajan päättelyä.
- **C-rajapinnat kääritään heti.** C-kirjaston kahva annetaan
  `unique_ptr`:lle omalla vapauttajalla jo sen luontihetkellä, kuten
  `fclose`-esimerkissä. Samaa mallia käytetään esimerkiksi
  käyttöjärjestelmän kahvoille ja grafiikkarajapintojen olioille.
- **Syklit katkaistaan `weak_ptr`:llä.** Tavallinen rakenne on, että
  vanhempi omistaa lapset ja lapsi viittaa vanhempaan `weak_ptr`:llä tai
  tavallisella osoittimella, jos vanhemman tiedetään elävän pidempään.
- **Hinnat.** `unique_ptr` maksaa saman kuin tavallinen osoitin.
  `make_shared` varaa olion ja laskurit yhdellä varauksella, mutta muisti
  vapautuu vasta, kun viimeinenkin `weak_ptr` on tuhoutunut.

## Itsearviointi

- Osaat kirjoittaa RAII-luokan, joka hankkii resurssin muodostimessa ja
  vapauttaa sen hajottimessa.
- Osaat kääriä C-kirjaston kahvan `unique_ptr`:iin omalla vapauttajalla.
- Osaat valita omistuksen tyypin: `unique_ptr`, `shared_ptr`, `weak_ptr`
  tai lainaava viittaus.
- Osaat selittää, miksi poikkeus ei aiheuta resurssivuotoa RAII-koodissa.
