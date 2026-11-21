# Lopuksi

## Mitä jäi käsittelemättä

Tutoriaali keskittyi piirteisiin, joita lähes jokainen C++-ohjelma
käyttää. Muutama suuri kokonaisuus jäi pois tai mainittiin vain
ohimennen.

**Moduulit** (C++20) korvaavat otsikkotiedostot ja `#include`-direktiivit.
Moduuli käännetään kerran, ja sen käyttäjä näkee vain sen, mitä moduuli
erikseen vie ulos (`export`). Tämä nopeuttaa käännöksiä ja estää
makrojen vuotamisen. C++23 lisäsi standardikirjaston moduulin
`std`, jolloin koko kirjaston voi ottaa käyttöön yhdellä
`import`-esittelyllä. Kääntäjien ja käännösjärjestelmien tuki on
kuitenkin vielä epätasaista, joten moduulit vaativat käytännössä
CMaken kaltaisen käännösjärjestelmän tukea.

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

## Tiivistelmä: modernin C++:n nyrkkisäännöt

1. Anna olioiden hallita resurssit (RAII). Älä kirjoita `new`- ja
   `delete`-operaatioita itse, vaan käytä säiliöitä ja älykkäitä
   osoittimia.
2. Suosi nollan sääntöä: rakenna luokat jäsenistä, jotka huolehtivat
   itsestään.
3. Käytä `std::unique_ptr`:ää oletuksena ja `std::shared_ptr`:ää vain,
   kun omistus on aidosti jaettu.
4. Välitä parametrit lukemista varten `const`-viittauksina tai
   näkymätyypeillä (`std::string_view`, `std::span`). Ota parametri
   arvona, kun funktio tallentaa siitä kopion.
5. Alusta muuttujat aina, mieluiten aaltosulkein.
6. Kirjoita `const` ja `constexpr` kaikkialle, minne ne sopivat.
7. Merkitse siirtomuodostimet `noexcept`, korvaavat funktiot
   `override` ja yksiparametriset muodostimet `explicit`.
8. Käytä standardikirjaston algoritmeja ja näkymiä omien silmukoiden
   sijaan.
9. Ilmaise mahdollinen puuttuminen tyypillä `std::optional`, vaihtoehdot
   tyypillä `std::variant` ja odotettavat virheet tyypillä
   `std::expected`.
10. Rajoita mallit konsepteilla.
11. Käännä varoitukset päällä ja testaa sanitoijilla.

## Lähteet ja jatkolukeminen

- **cppreference.com** (<https://en.cppreference.com>) on kattavin
  verkossa oleva hakuteos kielestä ja standardikirjastosta. Se kertoo
  myös, missä standardissa kukin piirre esiteltiin ja mitkä kääntäjät
  sitä tukevat. Sisältö on lisensoitu CC BY-SA- ja GFDL-lisensseillä.
- **C++ Core Guidelines** (<https://isocpp.github.io/CppCoreGuidelines/>)
  on Bjarne Stroustrupin ja Herb Sutterin toimittama ohjeisto modernin
  C++:n käytännöistä. Monet tämän tutoriaalin suosituksista ovat
  peräisin sieltä.
- **Standardin luonnokset** (<https://eel.is/c++draft/>) ovat
  lopullinen lähde kielen tarkalle määrittelylle.
- **Compiler Explorer** (<https://godbolt.org>) kääntää koodia selaimessa
  useilla kääntäjillä ja näyttää tuotetun konekielen. Se sopii
  pienten kokeilujen tekemiseen.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
