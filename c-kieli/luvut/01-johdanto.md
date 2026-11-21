# Johdanto

C on Dennis Ritchien 1970-luvun alussa Bell Labsissa kehittämä
ohjelmointikieli. Se luotiin Unix-käyttöjärjestelmän toteutuskieleksi,
ja se on edelleen järjestelmäohjelmoinnin peruskieli:
käyttöjärjestelmien ytimet, sulautetut järjestelmät, tietokannat,
verkkopinot ja monien muiden kielten tulkit on kirjoitettu C:llä.

C on pieni kieli. Se tarjoaa suoran pääsyn muistiin osoittimien avulla,
ja sen rakenteet vastaavat läheisesti konekielen toimintoja. Siksi
C-ohjelmat ovat nopeita ja kannettavia, ja C:tä kutsutaan joskus
"kannettavaksi symboliseksi konekieleksi". Vastapainona kieli ei suojaa
ohjelmoijaa: taulukon rajojen ylitystä, vapautetun muistin käyttöä
tai kokonaisluvun ylivuotoa ei tarkisteta, vaan ne johtavat
*määrittelemättömään käyttäytymiseen*. Hyvä C-ohjelmointi on suurelta
osin sen tuntemista, mitä ei saa tehdä.

## Standardit

| Standardi | Keskeisiä lisäyksiä |
|-----------|---------------------|
| K&R C (1978) | Kernighanin ja Ritchien kirjan kuvaama alkuperäinen kieli |
| C89/C90 | ensimmäinen standardi, funktioprototyypit, standardikirjasto |
| C99 | `//`-kommentit, `<stdint.h>`, `bool`, nimetyt alustimet, `inline` |
| C11 | säikeet, atomiset tyypit, `_Generic`, `static_assert` |
| C17 | korjausversio, ei uusia ominaisuuksia |
| C23 | `nullptr`, `constexpr`, `typeof`, `auto`, attribuutit, `<stdckdint.h>` |

C23 julkaistiin ISO-standardina vuonna 2024 (ISO/IEC 9899:2024).
Seuraavaa versiota kutsutaan työnimellä C2y. Tämä tutoriaali käyttää
C23:a niiltä osin kuin GCC 14 ja Clang 20 sitä tukevat, ja kertoo, kun
ominaisuus on uusi. Vanhemmissa standardeissa kirjoitetussa koodissa
näkyy usein vanhempia muotoja, kuten `NULL` ja `#include <stdbool.h>`,
joten nekin mainitaan.

## Kenelle tutoriaali on tarkoitettu

Tutoriaali olettaa, että lukija osaa ohjelmoida jollakin kielellä ja
tuntee perusasiat, kuten muuttujat, ehtolauseet, silmukat ja funktiot.
C:n erityispiirteet, kuten osoittimet, muistinhallinta ja
määrittelemätön käyttäytyminen, käydään läpi alusta.

## Työkalut

Esimerkit on testattu GCC 14- ja Clang 20 -kääntäjillä Linuxissa.
Yksittäinen esimerkki käännetään ja ajetaan näin:

```text
gcc-14 -std=c23 -Wall -Wextra -Wpedantic hei.c -o hei -lm
./hei
```

Valitsin `-std=c23` valitsee standardin, ja `-Wall -Wextra -Wpedantic`
kytkee päälle tavallisimmat varoitukset. C:ssä varoitukset ovat vielä
tärkeämpiä kuin monissa muissa kielissä, koska kääntäjä hyväksyy paljon
koodia, joka on lähes varmasti virheellistä. Valitsin `-lm` linkittää
matematiikkakirjaston, jota `<math.h>`-funktiot tarvitsevat.

Kehitysvaiheessa ohjelma kannattaa kääntää *sanitoijien* kanssa:

```text
gcc-14 -std=c23 -Wall -Wextra -g -fsanitize=address,undefined hei.c -o hei
```

AddressSanitizer havaitsee muistivirheet, kuten taulukon rajojen
ylityksen, vapautetun muistin käytön ja muistivuodot.
UndefinedBehaviorSanitizer havaitsee muun muassa etumerkillisten
kokonaislukujen ylivuodot ja virheelliset bittisiirrot. Sanitoijat
hidastavat ohjelmaa, joten niitä ei käytetä lopullisessa versiossa.

## Ensimmäinen ohjelma

```{.c tiedosto="esimerkit/01-hei.c"}
```

```{.tuloste tiedosto="esimerkit/01-hei.odotettu"}
```

Rivi `#include <stdio.h>` ottaa käyttöön standardikirjaston syöte- ja
tulostefunktiot, kuten `printf`. Ohjelman suoritus alkaa
`main`-funktiosta. Parametrilista `(void)` tarkoittaa, ettei funktio ota
parametreja. Paluuarvo `0` kertoo käyttöjärjestelmälle, että ohjelma
onnistui; `main` palauttaa nollan myös ilman `return`-lausetta.

`printf` tulostaa muotoilumerkkijonon ja korvaa *muunnosmääreet*
argumenteilla: `%d` kokonaisluvulla, `%f` liukuluvulla, `%s`
merkkijonolla ja `%zu` `sizeof`-operaattorin tuloksella. Määreen on
vastattava argumentin tyyppiä. Kääntäjä tarkistaa tämän, kun
varoitukset ovat päällä.

## Käännösprosessi

C-ohjelman kääntäminen etenee neljässä vaiheessa:

1. **Esikäsittely** käsittelee `#`-alkuiset direktiivit: liittää
   `#include`-tiedostot, laajentaa makrot ja poistaa kommentit.
2. **Käännös** muuntaa esikäsitellyn lähdekoodin konekielelle
   (symboliseksi konekieleksi).
3. **Kokoaminen** tuottaa objektitiedoston (`.o`).
4. **Linkitys** yhdistää objektitiedostot ja kirjastot suoritettavaksi
   ohjelmaksi.

`gcc` tekee kaikki vaiheet kerralla, mutta ne voi myös suorittaa
erikseen. Esimerkiksi `gcc -E hei.c` näyttää esikäsittelyn tuloksen ja
`gcc -c hei.c` tuottaa objektitiedoston `hei.o`. Vaiheiden tunteminen
auttaa ymmärtämään virheilmoituksia: puuttuva otsikkotiedosto on
esikäsittelyvirhe, mutta määrittelemätön funktio (`undefined reference`)
on linkitysvirhe.

## Esimerkkien testaus

Kaikki tämän tutoriaalin koodi on peräisin hakemiston `esimerkit`
tiedostoista, jotka käännetään ja ajetaan automaattisesti molemmilla
kääntäjillä sanitoijien kanssa. Jokaisen ohjelman tulostetta verrataan
tiedostoon, josta myös tekstissä näkyvät tulosteet on poimittu.

Osa esimerkeistä havainnollistaa koodia, jonka *ei* pidä kääntyä.
Tällaiset tiedostot testataan kahdesti: ensin varmistetaan, että
käännös epäonnistuu, ja sitten, että se onnistuu, kun virheellinen
kohta on poistettu esikääntäjän makrolla `KORJATTU`. Lisäksi muutama
esimerkki näyttää virheen, jonka sanitoija havaitsee ajon aikana.
Niiden testi varmistaa, että ohjelma todella kaatuu odotetulla tavalla.
