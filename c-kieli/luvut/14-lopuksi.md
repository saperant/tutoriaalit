# Lopuksi {.runko-kaytannot .runko-lahteet}

## C23 lyhyesti

Tutoriaalissa käytettiin seuraavia C23:n uudistuksia. Ne toimivat
GCC 14:ssä ja Clang 20:ssä valitsimella `-std=c23`.

| Ominaisuus | Aiempi tapa | Luku |
|------------|-------------|------|
| `bool`, `true`, `false` avainsanoina | `#include <stdbool.h>` | 3 |
| `nullptr` | `NULL` | 5 |
| `constexpr`-vakiot | `#define`, `enum` | 3 |
| `auto` ja `typeof` | tyyppi kirjoitettiin auki | 3 |
| tyhjä alustin `{}` | `{0}` | 3 |
| binääriliteraalit `0b1010` | heksadesimaaliluvut | 3 |
| numeroerotin `1'000'000` | – | 3 |
| `<stdbit.h>`-otsikon bittifunktiot | kääntäjäkohtaiset `__builtin`-funktiot | 3 |
| `static_assert` ilman viestiä | `_Static_assert(ehto, "viesti")` | 11 |
| attribuutit, kuten `[[fallthrough]]` | kääntäjäkohtaiset laajennokset | 4 |
| luettelon perustyyppi `enum e : uint8_t` | – | 6 |
| `<stdckdint.h>` | omat ylivuototarkistukset | 11 |
| `strdup` standardikirjastossa | POSIX-laajennos | 8 |
| `thread_local` avainsanana | `_Thread_local` | 12 |
| attribuutti `[[nodiscard]]` | kääntäjäkohtaiset laajennokset | 11 |
| funktio `f()` tarkoittaa samaa kuin `f(void)` | `()` tarkoitti määrittelemättömiä parametreja | 4 |

Muita C23:n uudistuksia ovat esimerkiksi `#embed`, joka liittää
binääritiedoston sisällön taulukoksi, sekä mielivaltaisen levyiset
kokonaisluvut `_BitInt(N)`.

## Mallit ja idiomit

Tutoriaalissa esitellyt mallit ovat C-kehittäjien yhteistä sanastoa.
Niiden nimet kannattaa tuntea, sillä ne toistuvat koodikatselmoinneissa
ja avoimen lähdekoodin projekteissa.

| Malli | Ongelma, jonka se ratkaisee | Luku |
|-------|-----------------------------|------|
| Maski ja siirto | rekisterin tai lippujoukon yksittäiset kentät | 3 |
| Tulosparametri ja onnistumisen paluuarvo | useita tuloksia ja virheen ilmaisu ilman poikkeuksia | 5 |
| Osoitin ja pituus, viipale | taulukot ja alijonot ilman kopiointia | 7 |
| Dynaaminen taulukko geometrisella kasvatuksella | kasvava kokoelma | 8 |
| Areena | monen olion yhteinen elinaika ilman vuotoja | 8 |
| Luonti- ja tuhoamisfunktiopari | resurssin elinkaari ilman konstruktoreita | 8, 9 |
| Merkitty unioni | arvo, joka voi olla yksi monesta tyypistä | 6 |
| Funktio-osoitintaulu | rajapinnat ja vaihdettavat toteutukset | 9 |
| Läpinäkymätön tyyppi | kapselointi ja vakaa binäärirajapinta | 9 |
| Moduulietuliite | nimiavaruudet | 9 |
| X-makro | saman luettelon useat näkymät | 9 |
| `goto`-siivous | resurssien vapautus kaikilla poluilla | 11 |
| Virhekoodiluettelo ja tekstitaulukko | yhtenäinen virheenkäsittely | 11 |
| Tuottaja–kuluttaja-jono | työnjako säikeiden välillä | 12 |

## Nyrkkisäännöt

1. Käännä aina varoitukset päällä (`-Wall -Wextra`) ja testaa
   sanitoijien kanssa.
2. Alusta jokainen muuttuja.
3. Kuljeta taulukon koko aina taulukon mukana ja käytä kokoja,
   joiden tyyppi on `size_t`.
4. Käytä merkkijonojen muodostamiseen `snprintf`-funktiota ja lukemiseen
   `fgets`-funktiota. Älä käytä `gets`-, `strcpy`- tai
   `sprintf`-funktioita puskureihin, joiden riittävyydestä et ole varma.
5. Tarkista jokaisen muistinvarauksen, tiedostotoiminnon ja muunnoksen
   paluuarvo.
6. Sovi ja dokumentoi, kuka omistaa kunkin dynaamisesti varatun olion
   ja kuka vapauttaa sen.
7. Merkitse osoitinparametrit `const`-määreellä, kun dataa ei muuteta.
8. Merkitse tiedoston sisäiset funktiot ja muuttujat `static`.
9. Piilota rakenteiden toteutus epätäydellisten tyyppien taakse, kun
   rajapinta on tarkoitettu muiden käyttöön.
10. Suosi `constexpr`-vakioita, luetteloita ja funktioita makrojen
    sijaan.
11. Älä luota etumerkillisten kokonaislukujen ylivuodon tai muun
    määrittelemättömän käyttäytymisen tulokseen, vaikka koodi näyttäisi
    toimivan.

## Jatkotaidot

C-kieli on esitietona suurelle osalle taitopuuta:

- *Moderni C++*: sama laiteläheisyys, mutta tyyppijärjestelmä ja
  kirjasto, jotka hoitavat resurssit ohjelmoijan puolesta.
- *Tietorakenteet* ja *Algoritmit*: rakenteiden ja algoritmien toteutus
  C:llä.
- *Käännösjärjestelmät, testaus ja CI*: Make, CMake, testit ja
  sanitoijat suuremmassa projektissa.
- *Assembly*, *Objektitiedostot, linkitys ja ABI* ja
  *Käyttöjärjestelmät*: mitä C-ohjelmasta tulee konekielenä ja miten
  käyttöjärjestelmä ajaa sen.
- *Mikrokontrollerit ja bare-metal-ohjelmointi*: C ilman
  käyttöjärjestelmää.
- *C ja assembly yhteen* ja *Python ja C/C++ yhteen*: C:n yhdistäminen
  muihin kieliin.

## Lähteet ja jatkolukeminen

- **cppreference.com** (<https://en.cppreference.com/w/c>) sisältää
  kattavan hakuteoksen C-kielestä ja sen standardikirjastosta. Se
  kertoo myös, missä standardissa kukin ominaisuus esiteltiin. Sisältö
  on lisensoitu CC BY-SA- ja GFDL-lisensseillä.
- **Standardin luonnokset** ovat saatavilla ISO:n C-työryhmän WG14
  sivuilta (<https://www.open-std.org/jtc1/sc22/wg14/>). C23:a lähes
  vastaava luonnos on asiakirja N3220.
- **GCC:n ja Clangin käyttöohjeet** kuvaavat varoitukset, sanitoijat ja
  kääntäjäkohtaiset laajennokset.
- **Compiler Explorer** (<https://godbolt.org>) kääntää koodia selaimessa
  ja näyttää tuotetun konekielen. Se sopii pienten kokeilujen tekemiseen.
- **SEI CERT C Coding Standard**
  (<https://wiki.sei.cmu.edu/confluence/display/c>) on turvallisen
  C-ohjelmoinnin sääntökokoelma perusteluineen ja esimerkkeineen.
- **Kirjat:** Kernighanin ja Ritchien *The C Programming Language* on
  kielen klassinen kuvaus (C89). Jens Gustedtin *Modern C* käsittelee
  nykyistä C:tä ja sen hyviä käytäntöjä.

### Kirjastot

- **GLib** (<https://docs.gtk.org/glib/>): tietorakenteet, merkkijonot,
  tapahtumasilmukka ja säikeet; GNOME-projektin perusta.
- **stb** (<https://github.com/nothings/stb>): yksitiedostoisia
  kirjastoja, mm. kuvien lataus ja dynaamiset taulukot (`stb_ds.h`).
- **klib** (<https://github.com/attractivechaos/klib>): kevyitä,
  makroilla tyypitettyjä tietorakenteita.
- **SQLite** (<https://sqlite.org>): sulautettava tietokanta ja
  esimerkki huolellisesti testatusta C-koodista.
