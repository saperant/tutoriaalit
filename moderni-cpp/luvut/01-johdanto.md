# Johdanto {.runko-johdanto}

C++ on yleiskäyttöinen, käännettävä ohjelmointikieli, jonka vahvuuksia
ovat suorituskyky, suora pääsy laitteistoon ja kyky rakentaa
korkean tason abstraktioita, joista ei makseta ajoaikana. Kieli on
muuttunut huomattavasti vuoden 2011 jälkeen. *Modernilla C++:lla*
tarkoitetaan tässä tutoriaalissa C++11-standardista alkanutta
ohjelmointityyliä, jossa

- resurssit hallitaan olioiden elinkaaren avulla (RAII) eikä käsin
  kutsuttavilla `new`- ja `delete`-operaatioilla,
- arvoja siirretään kopioimisen sijaan aina, kun se on mahdollista,
- standardikirjaston säiliöitä, algoritmeja ja tyyppejä suositaan omien
  toteutusten sijaan,
- virheet pyritään havaitsemaan käännösaikana tyyppijärjestelmän,
  `constexpr`-laskennan ja konseptien avulla.

## Historia ja käyttökohteet

Bjarne Stroustrup aloitti kielen kehittämisen Bell Labsissa vuonna 1979
nimellä *C with Classes*. Tavoitteena oli yhdistää C:n tehokkuus ja
laitteistoläheisyys Simula-kielen luokkiin. Nimi C++ otettiin käyttöön
vuonna 1983, ja ensimmäinen ISO-standardi julkaistiin vuonna 1998.

C++:aa käytetään, kun suorituskyvyllä, muistinkäytöllä tai
ennustettavalla ajoituksella on merkitystä ja kun ohjelma on niin suuri,
että se tarvitsee abstraktioita. Tyypillisiä käyttökohteita ovat
pelimoottorit, selaimet, tietokannat, kääntäjät, kaupankäyntijärjestelmät,
tieteellinen laskenta, sulautetut järjestelmät, laitteistomallit
(SystemC) sekä työpöytäsovellukset (esimerkiksi Qt-kirjaston päällä).
Monen muun kielen ajoympäristö, kuten Pythonin NumPy, on kirjoitettu
C:llä tai C++:lla.

### Mihin C++ ei sovellu

C++ ei ole hyvä valinta, kun kehitysnopeus on tärkeämpää kuin
suorituskyky. Pienet työkalut, automaatio ja kertaluonteinen analyysi
syntyvät nopeammin Pythonilla. Verkkopalvelujen liiketoimintalogiikkaan
on yleensä tarjolla tuottavampia ympäristöjä. Kielen laajuus ja
määrittelemätön käyttäytyminen tekevät siitä myös raskaan oppia ja
virhealttiin ilman hyviä käytäntöjä ja työkaluja. Uusissa
järjestelmäohjelmointiprojekteissa vaihtoehtona harkitaan usein Rustia,
jonka kääntäjä takaa muistiturvallisuuden.

## Standardit

C++-standardia kehittää ISO-komitea WG21. Uusi versio julkaistaan
kolmen vuoden välein.

| Standardi | Keskeisiä lisäyksiä |
|-----------|---------------------|
| C++11 | `auto`, lambdat, siirtosemantiikka, älykkäät osoittimet, säikeet |
| C++14 | yleiset lambdat, `std::make_unique`, laajempi `constexpr` |
| C++17 | rakenteiset sidonnat, `std::optional`, `std::variant`, `if constexpr` |
| C++20 | konseptit, ranges, `<=>`-operaattori, moduulit, korutiinit, `std::format` |
| C++23 | `std::print`, `std::expected`, uusia näkymiä, `std::ranges::to` |
| C++26 | staattinen reflektio, sopimukset (*contracts*), `std::execution` |

C++26:n sisältö on päätetty, mutta kääntäjätuki on vielä keskeneräinen.
Tässä tutoriaalissa pitäydytään C++23:ssa ja niissä sen osissa, joita
yleiset kääntäjät jo tukevat.

## Kenelle tutoriaali on tarkoitettu

Tutoriaali olettaa, että lukija osaa ohjelmoida C:llä tai tuntee
muuten C-tyylisen syntaksin: muuttujat, funktiot, silmukat, rakenteet
ja osoittimet. Aiempaa C++:n tuntemusta ei tarvita. Luvut
[C:stä C++:aan](#cstä-caan) ja [Luokan perusteet](#luokan-perusteet)
esittelevät viittaukset, standardikirjaston merkkijonon ja vektorin
sekä luokat, ja myöhemmät luvut nojaavat niihin. Tavoitteena ei ole
kattaa koko kieltä, vaan esitellä ne piirteet, joiden varaan
nykyaikainen C++-koodi rakentuu.

Tutoriaali palvelee kolmella tavalla:

- **Kieltä opetteleva** lukee luvut järjestyksessä. Luvun
  [C++ kokeneelle](#c-kokeneelle) voi ensimmäisellä kerralla silmäillä
  ja lukea tarkemmin, kun perusteet ovat tuttuja.
- **Toista kieltä osaava kokenut kehittäjä** aloittaa luvusta
  [C++ kokeneelle](#c-kokeneelle) ja erillisestä pikaoppaasta ja lukee
  muista luvuista ensin loppuosion *Itsearviointi*.
- **Kaikille** tärkeimmät osiot ovat lukujen lopun *Käytännössä*-osiot.
  Niissä kerrotaan, miten C++-kehittäjät asioita oikeasti käyttävät:
  nimetyt mallit, parhaat käytännöt perusteluineen sekä kielikohtaiset
  hinnat ja sudenkuopat.

Kieliriippumattomat aiheet, kuten algoritmien suunnittelu, yleinen
suorituskykyanalyysi ja verkko-ohjelmointi, käsitellään taitopuun omissa
tutoriaaleissa. Tämä tutoriaali kertoo, miten ne tehdään C++:lla.

## Työkalut

Esimerkit on testattu GCC 14- ja Clang 20 -kääntäjillä Linuxissa.
Yksittäinen esimerkki käännetään ja ajetaan näin:

```text
g++-14 -std=c++23 -Wall -Wextra -Wpedantic hei.cpp -o hei
./hei
```

Valitsin `-std=c++23` ottaa käyttöön C++23-standardin, ja
`-Wall -Wextra -Wpedantic` kytkee päälle tavallisimmat varoitukset.
Varoitukset kannattaa pitää aina päällä: ne löytävät suuren osan
virheistä jo ennen ohjelman ajamista.

Kehitysvaiheessa kannattaa käyttää myös *sanitoijia*. Valitsimella
`-fsanitize=address,undefined` kääntäjä lisää ohjelmaan tarkistuksia,
jotka pysäyttävät ajon esimerkiksi taulukon rajojen ylityksessä,
vapautetun muistin käytössä tai etumerkillisen kokonaisluvun
ylivuodossa. Säikeitä käyttävälle koodille on oma
`-fsanitize=thread`.

## Ensimmäinen ohjelma

```{.cpp tiedosto="esimerkit/01-hei.cpp"}
```

Ohjelma tulostaa:

```{.tuloste tiedosto="esimerkit/01-hei.odotettu"}
```

C++23:n `std::println` muotoilee tulosteen Pythonin `format`-funktiota
muistuttavalla tavalla: jokainen `{}` korvataan vuorollaan seuraavalla
argumentilla. Muotoilumerkkijono tarkistetaan käännösaikana, joten
väärä määrä argumentteja on käännösvirhe eikä ajonaikainen yllätys.
Vanhempi `std::cout << ...` -tyyli toimii edelleen, mutta uudessa
koodissa `std::print` ja `std::format` ovat yleensä selkeämpiä.

Funktio `main` palauttaa arvon `0`, vaikka `return`-lausetta ei ole
kirjoitettu. Tämä poikkeus koskee vain `main`-funktiota.

## Esimerkkien testaus

Kaikki tämän tutoriaalin koodi on peräisin hakemiston `esimerkit`
tiedostoista, jotka käännetään ja ajetaan automaattisesti. Jokaisen
ohjelman tulostetta verrataan tiedostoon, josta myös tekstissä näkyvät
tulosteet on poimittu. Kun koodiesimerkin vieressä lukee, mitä ohjelma
tulostaa, tulos on siis todennettu.

Osa esimerkeistä havainnollistaa koodia, jonka *ei* pidä kääntyä.
Tällaiset tiedostot testataan kahdesti: ensin varmistetaan, että
käännös epäonnistuu, ja sitten, että se onnistuu, kun virheellinen
kohta on poistettu esikääntäjän makrolla `KORJATTU`. Muutama esimerkki
näyttää virheen, jonka sanitoija havaitsee ajon aikana; niiden testi
varmistaa, että ohjelma todella kaatuu odotetulla tavalla.
