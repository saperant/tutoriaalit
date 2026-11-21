# Lopuksi

## C23 lyhyesti

Tutoriaalissa käytettiin seuraavia C23:n uudistuksia. Ne toimivat
GCC 14:ssä ja Clang 20:ssä valitsimella `-std=c23`.

| Ominaisuus | Aiempi tapa | Luku |
|------------|-------------|------|
| `bool`, `true`, `false` avainsanoina | `#include <stdbool.h>` | 2 |
| `nullptr` | `NULL` | 4 |
| `constexpr`-vakiot | `#define`, `enum` | 2 |
| `auto` ja `typeof` | tyyppi kirjoitettiin auki | 2 |
| tyhjä alustin `{}` | `{0}` | 2 |
| binääriliteraalit `0b1010` | heksadesimaaliluvut | 2 |
| numeroerotin `1'000'000` | – | 2 |
| `static_assert` ilman viestiä | `_Static_assert(ehto, "viesti")` | 10 |
| attribuutit, kuten `[[fallthrough]]` | kääntäjäkohtaiset laajennokset | 3 |
| luettelon perustyyppi `enum e : uint8_t` | – | 7 |
| `<stdckdint.h>` | omat ylivuototarkistukset | 10 |
| `strdup` standardikirjastossa | POSIX-laajennos | 6 |
| funktio `f()` tarkoittaa samaa kuin `f(void)` | `()` tarkoitti määrittelemättömiä parametreja | 3 |

Muita C23:n uudistuksia ovat esimerkiksi `#embed`, joka liittää
binääritiedoston sisällön taulukoksi, `<stdbit.h>`-otsikon
bittioperaatiot sekä mielivaltaisen levyiset kokonaisluvut `_BitInt(N)`.

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

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
