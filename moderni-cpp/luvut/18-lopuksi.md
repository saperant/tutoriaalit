# Lopuksi {.runko-kaytannot .runko-lahteet}

## Idiomit ja mallit

Tutoriaalin nimetyt idiomit ja mallit koottuina. Nimet kannattaa
tunnistaa, sillä niihin viitataan koodikatselmoinneissa, dokumentaatiossa
ja kirjallisuudessa.

| Idiomi tai malli | Mitä se ratkaisee | Luku |
|------------------|-------------------|------|
| RAII | Resurssi vapautuu automaattisesti ja poikkeusturvallisesti | Resurssienhallinta |
| Nollan sääntö | Luokka ei tarvitse omia erikoisjäsenfunktioita | Siirtosemantiikka |
| Viiden sääntö, copy-and-swap | Resurssikääreen kopiointi ja siirto oikein ja vahvalla takuulla | Siirtosemantiikka |
| Sink-parametri (arvo ja siirto) | Yksi funktio palvelee kopioitavia ja siirrettäviä argumentteja | Siirtosemantiikka |
| IIFE | Monivaiheinen alustus vakioon | Funktiot ja lambdat |
| Vahva tyyppi | Samantyyppisten parametrien sekoittaminen on käännösvirhe | Luokat |
| Tyyppien pyyhintä | Arvosemantiikka ja ajonaikainen monimuotoisuus ilman periytymistä | Mallit ja konseptit |
| `variant` ja `visit` (*overloaded*) | Suljettu joukko vaihtoehtoja ilman periytymistä | Sanastotyypit |
| CRTP | Staattinen monimuotoisuus ja sekoiteluokat | Mallit ja konseptit |
| Pimpl | Vakaa binäärirajapinta ja lyhyemmät käännösajat | Ohjelman rakenne |
| Virhe arvona (`expected`) | Odotettava virhe ilman poikkeuksen hintaa | Virheenkäsittely |
| Tuottaja–kuluttaja | Työn jako säikeille ja hallittu lopetus | Rinnakkaisuus |
| Funktion sisäinen staattinen muuttuja | Alustusjärjestyksen ongelman välttäminen | Työkalut ja testaus |

## Nyrkkisäännöt

1. Anna olioiden hallita resurssit (RAII). Älä kirjoita `new`- ja
   `delete`-operaatioita itse, vaan käytä säiliöitä ja älykkäitä
   osoittimia.
2. Suosi nollan sääntöä: rakenna luokat jäsenistä, jotka huolehtivat
   itsestään.
3. Ilmaise omistus tyypillä: `std::unique_ptr` omistaa, viittaus
   lainaa, `std::shared_ptr` vain todelliseen jaettuun omistukseen.
4. Välitä parametrit lukemista varten `const`-viittauksina tai
   näkymätyypeillä (`std::string_view`, `std::span`). Ota parametri
   arvona, kun funktio tallentaa siitä kopion.
5. Alusta muuttujat aina, mieluiten aaltosulkein, ja pidä niiden
   näkyvyysalue pienenä.
6. Kirjoita `const` ja `constexpr` kaikkialle, minne ne sopivat.
7. Merkitse siirtomuodostimet `noexcept`, korvaavat funktiot
   `override` ja yksiparametriset muodostimet `explicit`.
8. Käytä standardikirjaston algoritmeja ja näkymiä omien silmukoiden
   sijaan.
9. Ilmaise mahdollinen puuttuminen tyypillä `std::optional`, vaihtoehdot
   tyypillä `std::variant` ja odotettavat virheet tyypillä
   `std::expected`. Käytä poikkeuksia vain poikkeuksellisiin tilanteisiin.
10. Rajoita mallit konsepteilla.
11. Älä jaa muuttuvaa tilaa säikeiden kesken, jos sen voi välttää; jos
    jaat, suojaa se lukolla.
12. Käännä varoitukset päällä, testaa sanitoijilla ja mittaa ennen kuin
    optimoit.

## Mitä jäi käsittelemättä

**Korutiinit** (C++20) ovat funktioita, joiden suorituksen voi keskeyttää
ja jatkaa myöhemmin. Ne mahdollistavat asynkronisen koodin ja
generaattorit ilman takaisinkutsuja. Kieli tarjoaa vain matalan tason
mekanismin; C++23:n `std::generator` on ensimmäinen valmis
korutiinityyppi standardikirjastossa.

**C++26** tuo muun muassa staattisen reflektion, jolla ohjelma voi
käännösaikana tutkia omia tyyppejään (esimerkiksi luetella rakenteen
jäsenet), sopimukset (*contracts*), joilla funktion esi- ja jälkiehdot
voi kirjoittaa osaksi sen esittelyä, sekä `std::execution`-kirjaston
asynkroniseen ohjelmointiin.

## Jatkotaidot

Erityistarpeet käsitellään taidoissa, joissa tämä tutoriaali on
esitietona:

- *C++:n suorituskyky*: kielen rakenteiden hinnat mitattuina.
- *Rinnakkaisohjelmointi*: säikeet, muistijärjestykset ja lukottomat
  rakenteet.
- *Edistyneet algoritmit ja tietorakenteet* ja *Kääntäjätekniikka*:
  suuremmat C++-ohjelmat.
- *Verkko-ohjelmointi*: soketit ja palvelinmallit.
- *Python ja C/C++ yhteen*: C++-kirjasto Pythonin käytettäväksi.
- *Renderöinnin perusteet* ja *Peliohjelmointi*: grafiikka ja pelit
  C++:lla.
- *Korkean tason mallinnus (SystemC/TLM)*: laitteiston mallinnus
  C++-kirjastolla.

## Lähteet ja jatkolukeminen

**Dokumentaatio**

- **cppreference.com** (<https://en.cppreference.com>) on kattavin
  verkossa oleva hakuteos kielestä ja standardikirjastosta. Se kertoo
  myös, missä standardissa kukin piirre esiteltiin ja mitkä kääntäjät
  sitä tukevat. Sisältö on lisensoitu CC BY-SA- ja GFDL-lisensseillä.
- **C++ Core Guidelines** (<https://isocpp.github.io/CppCoreGuidelines/>)
  on Bjarne Stroustrupin ja Herb Sutterin toimittama ohjeisto modernin
  C++:n käytännöistä. Monet tämän tutoriaalin suosituksista ovat
  peräisin sieltä, ja sääntöihin viitataan tunnuksilla kuten C.21.
- **Standardin luonnokset** (<https://eel.is/c++draft/>) ovat
  lopullinen lähde kielen tarkalle määrittelylle.
- **Compiler Explorer** (<https://godbolt.org>) kääntää koodia selaimessa
  useilla kääntäjillä ja näyttää tuotetun konekielen. Se sopii
  pienten kokeilujen ja abstraktioiden hinnan tarkistamiseen.

**Kirjoja**

- Bjarne Stroustrup: *A Tour of C++* (3. painos) – kielen tekijän
  tiivis yleiskatsaus nykyaikaiseen C++:aan.
- Scott Meyers: *Effective Modern C++* – C++11- ja C++14-piirteiden
  käytännöt ja sudenkuopat.
- Klaus Iglberger: *C++ Software Design* – suunnittelumallit ja
  tyyppien pyyhintä nykyaikaisessa C++:ssa.
- Anthony Williams: *C++ Concurrency in Action* (2. painos) –
  rinnakkaisohjelmointi ja muistimalli.

**Ulkoisia kirjastoja**

- **Boost** (<https://www.boost.org>) – laaja kokoelma vertaisarvioituja
  kirjastoja, joista moni on päätynyt standardiin.
- **{fmt}** (<https://fmt.dev>) – `std::format`in esikuva ja sen
  laajennettu toteutus vanhemmille standardeille.
- **Abseil** (<https://abseil.io>) – Googlen yleiskirjasto, muun muassa
  nopeat hajautustaulut.
- **GoogleTest** (<https://github.com/google/googletest>) ja **Catch2**
  (<https://github.com/catchorg/Catch2>) – yksikkötestaus.
- **Google Benchmark** (<https://github.com/google/benchmark>) –
  mikrovertailut.
- **Qt** (<https://www.qt.io>) – graafiset käyttöliittymät ja laaja
  sovelluskehys.
