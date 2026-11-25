# Ohjelman rakenne ja modulit {.runko-modulit}

Suurempi C++-ohjelma jaetaan käännösyksiköihin: jokainen lähdetiedosto
(`.cpp`) käännetään erikseen objektitiedostoksi, ja linkittäjä yhdistää
ne. Tiedostojen välinen rajapinta kirjoitetaan otsikkotiedostoihin
(`.hpp` tai `.h`), jotka liitetään `#include`-direktiivillä. C++20 toi
lisäksi moduulit, joista kerrotaan luvun lopussa.

## Otsikko- ja lähdetiedostot

Otsikkotiedostossa on rajapinta: luokkien ja funktioiden esittelyt,
mallit, `inline`-funktiot ja vakiot. Lähdetiedostossa ovat määrittelyt.
Otsikkotiedosto suojataan kaksinkertaiselta liittämiseltä direktiivillä
`#pragma once`, jota kaikki yleiset kääntäjät tukevat, tai perinteisellä
`#ifndef`-vartijalla.

**Yhden määrittelyn sääntö** (*one definition rule*, ODR) sallii
funktiolle tai muuttujalle vain yhden määrittelyn koko ohjelmassa.
Poikkeuksia ovat `inline`-funktiot ja -muuttujat, mallit sekä
luokkien sisällä määritellyt jäsenfunktiot: ne saavat esiintyä useassa
käännösyksikössä, kunhan määrittely on joka kerta sama. Siksi
otsikkotiedoston vakio kirjoitetaan muodossa `inline constexpr`.

**Nimiavaruudet** estävät nimien törmäykset kirjastojen välillä.
Kirjaston kaikki nimet sijoitetaan sen omaan nimiavaruuteen, kuten alla
`tutoriaali::mittaus`. *Nimetön nimiavaruus* rajaa nimen näkyvyyden
yhteen käännösyksikköön. Se korvaa C:n `static`-sanan apufunktioille.

### Rajapinnan dokumentointi

Otsikkotiedosto on myös paikka, jossa rajapinta dokumentoidaan.
Tyypit kertovat jo paljon, joten kommentti kertoo sen, mitä tyypit
eivät kerro: esiehdot, mitä poikkeuksia funktio heittää ja missä
tilassa olio on sen jälkeen, kuinka kauan palautettu viittaus on
voimassa, onko luokka säieturvallinen ja mitä siirretylle oliolle saa
tehdä. Kommentti, joka toistaa funktion nimen sanoina, on turha.

C++-projekteissa rajapintakommentit kirjoitetaan yleensä
*Doxygen*-muodossa. Kommentti alkaa merkeillä `///`, ja komennot
`@brief`, `@param`, `@return`, `@pre` ja `@throws` jäsentävät sen.
Doxygen kokoaa kommenteista selattavan viitedokumentaation, ja sen
asetukset `WARN_IF_UNDOCUMENTED`, `WARN_NO_PARAMDOC` ja `WARN_AS_ERROR`
muuttavat puuttuvat kuvaukset virheiksi, jolloin jatkuva integraatio
huomaa dokumentoimattoman funktion. Seuraavan osion
`mittausloki.hpp` on kommentoitu näin. Dokumentaation rakennetta ja
julkaisemista käsittelee taitopuun taito *Tekninen dokumentaatio*.

## Pimpl-malli

Otsikkotiedosto paljastaa käyttäjälle luokan yksityisetkin kentät, koska
kääntäjä tarvitsee niitä olion koon laskemiseen. Jos kenttiä muutetaan,
jokainen otsikkoa käyttävä tiedosto on käännettävä uudelleen, ja
binäärirajapinta muuttuu. *Pimpl-malli* (*pointer to implementation*)
siirtää kentät lähdetiedostossa määriteltävään rakenteeseen, johon
luokka viittaa `std::unique_ptr`:lla.

Esimerkkinä on mittausloki, joka koostuu kolmesta tiedostosta. Rajapinta
on otsikkotiedostossa:

```{.cpp tiedosto="esimerkit/14-mittausloki/mittausloki.hpp"}
```

Otsikko liittää vain muutaman standardikirjaston perusotsikon. Toteutuksen
`std::vector` ja algoritmit eivät näy käyttäjälle. Hajotin ja
siirto-operaatiot on vain esitelty, koska `unique_ptr` tarvitsee
`Toteutus`-tyypin täydellisen määrittelyn tuhotessaan sen. Ne määritellään
lähdetiedostossa:

```{.cpp tiedosto="esimerkit/14-mittausloki/mittausloki.cpp"}
```

Käyttäjä näkee vain julkisen rajapinnan:

```{.cpp tiedosto="esimerkit/14-mittausloki/main.cpp"}
```

```{.tuloste tiedosto="esimerkit/14-mittausloki.odotettu"}
```

```{.dot otsikko="Pimpl-mallin näkyvyys. Käyttäjän koodi riippuu vain otsikkotiedostosta, jossa `Toteutus` on pelkkä esittely. Kentät tuntee vain `mittausloki.cpp`, joten niiden muuttaminen ei käännä käyttäjän koodia uudelleen."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.7;
  node [shape=box, fontsize=10];
  main [label="main.cpp\nkäyttää Mittauslokia"];
  hpp [label="mittausloki.hpp\nclass Mittausloki\n  unique_ptr<Toteutus> t_\nstruct Toteutus;  (esittely)"];
  cpp [label="mittausloki.cpp\nstruct Toteutus {\n  std::string nimi;\n  std::vector<double> arvot;\n}", style=filled, fillcolor="#e8eef7"];
  main -> hpp [label="#include"];
  cpp -> hpp [label="#include"];
}
```

Ohjelma käännetään antamalla kääntäjälle molemmat lähdetiedostot:

```text
g++-14 -std=c++23 -Wall -Wextra main.cpp mittausloki.cpp -o mittausloki
```

Pimpl maksaa yhden muistinvarauksen oliota kohti ja epäsuoran
viittauksen jokaisessa kutsussa. Siksi sitä käytetään kirjastojen
julkisissa rajapinnoissa ja luokissa, joiden toteutus muuttuu usein, ei
pienissä arvotyypeissä.

## Moduulit

C++20:n moduulit korvaavat otsikkotiedostot: moduuli käännetään kerran, ja
sen käyttäjä näkee vain sen, minkä moduuli vie ulos sanalla `export`.
Makrot eivät vuoda moduulin ulkopuolelle, eikä liittämisjärjestyksellä ole
merkitystä. C++23 lisäsi standardikirjaston moduulin `std`, jolloin koko
kirjaston voi ottaa käyttöön esittelyllä `import std;`.

Kääntäjien ja käännösjärjestelmien tuki on kuitenkin epätasaista ja
muuttuu versio versiolta. Tämän tutoriaalin testeissä käytetty GCC 14
tukee moduuleja valitsimella `-fmodules-ts` mutta ei
`import std`-esittelyä. Moduulit vaativat lisäksi käännösjärjestelmältä
riippuvuuksien selvittämistä ennen käännöstä; CMake tukee tätä
versiosta 3.28 alkaen. Tilanne kannattaa tarkistaa käytettävän
kääntäjän dokumentaatiosta. Tämän tutoriaalin esimerkit käyttävät
otsikkotiedostoja, jotka ovat edelleen yleisin tapa.

## Riippuvuudet

C++:lla ei ole yhtä virallista paketinhallintaa. Ulkoiset kirjastot
otetaan tavallisesti käyttöön käännösjärjestelmän kautta. CMakessa
asennettu kirjasto löydetään komennolla `find_package` ja liitetään
kohteeseen komennolla `target_link_libraries` (luku
[Työkalut ja testaus](#työkalut-ja-testaus)). Kirjastojen asentamiseen
ja versioiden hallintaan käytetään paketinhallintaa: vcpkg ja Conan ovat
yleisimmät, ja Linux-jakeluiden paketit ovat vaihtoehto järjestelmän
laajuisille kirjastoille. Pienen, vain otsikkotiedostoista koostuvan
kirjaston voi myös lisätä projektiin sellaisenaan tai CMaken
`FetchContent`-toiminnolla.

## Käytännössä

- **Otsikkotiedosto on sopimus.** Siinä on vain se, mitä käyttäjä
  tarvitsee. Jokainen ylimääräinen `#include` hidastaa kaikkien käyttäjien
  käännöstä ja kytkee ne toteutukseen. Esittely ilman määrittelyä
  (*forward declaration*) riittää, kun tyyppiä käytetään vain osoittimen
  tai viittauksen kautta.
- **Rajapintakommentti kertoo sopimuksen, ei toteutusta.** Esiehdot,
  poikkeukset, elinajat ja säieturvallisuus kirjataan otsikkotiedostoon
  esittelyn viereen, missä ne pysyvät ajan tasalla. Toteutuksen
  yksityiskohdat kuuluvat lähdetiedoston kommentteihin.
- **Otsikkotiedosto kääntyy yksinään.** Jokainen otsikko liittää itse
  kaiken, mitä se tarvitsee. Yleinen tapa varmistaa tämä on liittää
  lähdetiedoston oma otsikko ensimmäisenä, kuten `mittausloki.cpp`
  tekee.
- **Ei `using namespace` otsikkotiedostoon.** Se tuo nimet jokaiseen
  tiedostoon, joka liittää otsikon. Lähdetiedostossa paikallinen
  `using namespace` tai nimiavaruuden lyhenne
  (`namespace mittaus = tutoriaali::mittaus;`) on sallittu.
- **Apufunktiot nimettömään nimiavaruuteen.** Se pitää ne poissa muiden
  käännösyksiköiden näkyvistä ja estää linkitysvirheet samannimisten
  apufunktioiden välillä.
- **Pimpl kirjaston rajalle.** Se vakauttaa binäärirajapinnan ja
  lyhentää käännösaikoja. Sisäisissä luokissa yksinkertaisuus on yleensä
  arvokkaampaa.
- **Riippuvuudet lukitaan.** Kirjastojen versiot kiinnitetään
  paketinhallinnan manifestiin, jotta käännös toistuu samanlaisena
  kaikilla koneilla ja jatkuvassa integraatiossa.

## Itsearviointi

- Osaat jakaa ohjelman otsikko- ja lähdetiedostoihin ja selittää yhden
  määrittelyn säännön.
- Osaat käyttää nimiavaruuksia ja nimetöntä nimiavaruutta.
- Osaat kirjoittaa funktiolle rajapintakommentin, joka kertoo esiehdot,
  poikkeukset ja palautetun viittauksen elinajan.
- Osaat toteuttaa pimpl-mallin ja kertoa, miksi hajotin määritellään
  lähdetiedostossa.
- Osaat kertoa, miten ulkoinen kirjasto otetaan käyttöön CMakella ja
  paketinhallinnalla.
