# Virtuaalikutsut

Virtuaalifunktio on C++:n tapa valita toteutus ajon aikana. Kutsun
hinta on pieni, muutama käsky, mutta sen todellinen hinta on se,
mitä se estää: kääntäjä ei voi sisällyttää kohdetta kutsukohtaan, joten
silmukkaa ei voi vektoroida eikä laskentaa yhdistää. Lisäksi
virtuaalisia olioita säilytetään tavallisesti osoittimien takana, jolloin
jokainen olio on omassa muistinvarauksessaan. Tässä luvussa verrataan
virtuaalikutsua, devirtualisoitua kutsua, `std::variant`ia ja CRTP:tä.

## Virtuaalitaulu

Jokaisella polymorfisella luokalla on *virtuaalitaulu* (engl. vtable),
taulukko funktio-osoittimia, ja jokaisessa oliossa on osoitin oman
luokkansa tauluun. Kutsu `k->pinta_ala()` lataa olion
taulun osoittimen, lataa siitä funktion osoitteen ja hyppää
epäsuorasti. Itaniumin C++-ABI, jota GCC ja Clang käyttävät Linuxissa,
määrittelee taulun rakenteen.

```{.cpp tiedosto="esimerkit/03-kuviot.cpp" osa="hierarkia"}
```

Sekalainen joukko kuvioita säilytetään osoittimina, ja summa kutsuu
virtuaalifunktiota:

```{.cpp tiedosto="esimerkit/03-kuviot.cpp" osa="virtuaali"}
```

Kolme hintaa kertyy:

1. **Epäsuora hyppy.** Prosessorin hyppykohteen ennustin arvaa
   kohteen. Kun kuvioiden tyypit vaihtelevat satunnaisesti, arvaus menee
   usein pieleen, ja jokainen väärä arvaus maksaa 15–20 jaksoa.
2. **Ei sisällyttämistä.** Funktion runko on erillinen, joten jokainen
   kutsu tallentaa ja palauttaa rekisterit kutsukonvention mukaan.
3. **Osoittimien seuraaminen.** Jokainen olio on omassa
   varauksessaan, mahdollisesti eri puolilla kekoa.

## Devirtualisointi ja `final`

Kääntäjä saa korvata virtuaalikutsun suoralla kutsulla, jos se tietää
olion dynaamisen tyypin. Viittaus `const Ympyra&` ei riitä, koska
viittauksen takana voi olla aliluokka, joka korvaa funktion.
Merkintä `final` lupaa, ettei aliluokkia ole:

```{.cpp tiedosto="esimerkit/03-kuviot.cpp" osa="final"}
```

Konekoodi näyttää eron. GCC tekee avoimelle luokalle *spekulatiivisen
devirtualisoinnin*: se vertaa virtuaalitaulun osoitetta tunnettuun
funktioon `Ympyra::pinta_ala`, laskee yhtäsuuruuden tapauksessa
sisällytetyn rungon ja kutsuu muussa tapauksessa epäsuorasti.
`final`-versiossa ei ole kutsua lainkaan:

```{.makefile tiedosto="esimerkit/Makefile" osa="devirtualisointi"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-devirtualisointi.txt"}
```

Devirtualisointi onnistuu myös ilman `final`ia, jos kääntäjä näkee
olion luonnin (`Ympyra y{2}; y.pinta_ala();`) tai jos luokka on
nimettömässä nimiavaruudessa ja koko ohjelma on yhdessä
käännösyksikössä. Linkitysaikainen optimointi (luku 9) laajentaa
näkyvyyden koko ohjelmaan: GCC:n `-fdevirtualize-at-ltrans` ja Clangin
`-fwhole-program-vtables` hyödyntävät tietoa siitä, mitkä luokat
ohjelmassa on.

## `std::variant`

Kun tyyppien joukko on suljettu ja tunnettu käännösaikana,
`std::variant` korvaa perinnän. Oliot ovat vektorissa peräkkäin
arvoina, ja `std::visit` valitsee funktion tyyppitunnisteen mukaan:

```{.cpp tiedosto="esimerkit/03-kuviot.cpp" osa="variant"}
```

`std::visit` kääntyy hyppytauluksi tai vertailuketjuksi, jonka haarat
on sisällytetty. Kutsu on yhä ajonaikainen valinta, mutta ilman
funktiokutsua ja osoittimien seuraamista. Variantin koko on suurimman
vaihtoehdon koko ja tyyppitunniste tasattuna, tässä 24 tavua.

## CRTP

*CRTP* (engl. curiously recurring template pattern) on staattinen
polymorfismi: kantaluokka saa aliluokan tyyppiparametrina ja kutsuu sen
funktioita suoraan. Ratkaisu on käännösaikainen, joten eri
aliluokkia ei voi laittaa samaan säiliöön:

```{.cpp tiedosto="esimerkit/03-kuviot.cpp" osa="crtp"}
```

C++23:n *eksplisiittinen olioparametri* (engl. deducing this) korvaa
CRTP:n usein yksinkertaisemmin: `double pinta_ala(this const auto&
self)` saa kutsujan todellisen tyypin ilman kantaluokan
malliparametria.

## Tulokset

Toiminnallinen testi tarkistaa, että kaikki tavat antavat saman
summan, ja laskee muistinvaraukset:

```{.cpp tiedosto="esimerkit/03-kuviot.cpp" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/03-kuviot.odotettu"}
```

Käskyt kuviota kohden ja ajat miljoonalle kuviolle:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-kuviot.txt"}
```

```{.tuloste tiedosto="esimerkit/tulokset/03-kuviot.txt"}
```

Käskymäärien erot ovat pieniä, mutta aikojen erot suuria. Sekalaisen
joukon virtuaalikutsu ja `std::variant` häviävät pelkille ympyröille
moninkertaisesti, koska tyyppi vaihtelee satunnaisesti ja haarojen tai
hyppykohteiden ennustus epäonnistuu. Variantti on silti
virtuaalikutsua nopeampi, koska oliot ovat peräkkäin muistissa eikä
funktiota kutsuta. Pelkkien ympyröiden joukossa spekulatiivinen
devirtualisointi tekee avoimesta luokasta lähes yhtä nopean kuin
`final`: arvaus osuu joka kerta.

Johtopäätös ei ole "vältä virtuaalifunktioita". Virtuaalikutsu on
oikea työkalu, kun tyyppien joukko on avoin, kuten liitännäisissä tai
kirjaston rajapinnoissa, ja kun kutsun takana on enemmän työtä kuin
muutama kertolasku. Kuumassa silmukassa, jossa jokaiselle alkiolle
tehdään pieni operaatio, ratkaisu on järjestää data tyypeittäin:
erilliset vektorit ympyröille ja suorakulmioille poistavat sekä
ajonaikaisen valinnan että väärät ennustukset (ks. luku 8).

## Käytännössä

- **Merkitse lehtiluokat `final`iksi**, kun aliluokkia ei ole
  tarkoitettu. Merkintä dokumentoi tarkoituksen ja antaa kääntäjälle
  luvan devirtualisoida.
- **Suljettu tyyppijoukko: `std::variant`.** Arvot ovat peräkkäin,
  muistia varataan vähemmän, ja kääntäjä tarkistaa, että `std::visit`
  käsittelee jokaisen vaihtoehdon.
- **Avoin tyyppijoukko: virtuaalifunktio.** Pidä kutsun takana
  tarpeeksi työtä: yksi virtuaalikutsu koko taulukon käsittelyyn on
  halpa, yksi kutsu alkiota kohden ei.
- **Järjestä tyypeittäin kuumissa silmukoissa.** Erilliset säiliöt
  tyypeittäin tai lajittelu tyypin mukaan tekevät ennustuksesta
  osuvan.
- **CRTP ja `deducing this`** ovat staattista polymorfismia: sopivat
  koodin jakamiseen tyyppien kesken, eivät ajonaikaiseen valintaan.

## Itsearviointi

- Osaat selittää virtuaalikutsun kolme hintaa: epäsuora hyppy, estetty
  sisällyttäminen ja osoittimien seuraaminen.
- Osaat lukea konekoodista spekulatiivisen devirtualisoinnin ja
  selittää, miksi `final` poistaa kutsun kokonaan.
- Osaat valita virtuaalifunktion, `std::variant`in ja CRTP:n välillä
  tyyppijoukon ja käyttötavan perusteella.
- Osaat perustella, miksi samat käskymäärät voivat kestää eri ajan.
