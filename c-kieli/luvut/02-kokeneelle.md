# C kokeneelle {.runko-kokeneelle}

Tämä luku on tarkoitettu lukijalle, joka osaa jo jonkin toisen kielen ja
haluaa päästä C:ssä nopeasti tuottavaksi. Luku kokoaa C:n ajattelutavan,
vastaavuudet tuttuihin kieliin, hinnat ja tärkeimmät sudenkuopat.

## Ajattelutapa

C:ssä ohjelmoija vastaa kaikesta, mitä muissa kielissä hoitaa kieli tai
ajonaikainen ympäristö:

- **Ei piiloja kustannuksia.** Jokainen rivi kääntyy ennustettavaksi
  konekieleksi. Ei roskienkeruuta, ei poikkeuksia, ei konstruktoreita
  eikä automaattisia kopioita. Kun koodissa ei lue `malloc`, muistia ei
  varata.
- **Ei tarkistuksia.** Taulukon rajoja, osoittimien kelvollisuutta tai
  kokonaislukujen ylivuotoa ei tarkisteta. Virhe on *määrittelemätöntä
  käyttäytymistä*: ohjelma voi toimia, kaatua tai tuottaa väärän tuloksen.
  Siksi C-koodia kehitetään aina varoitukset ja sanitoijat päällä.
- **Rajapinta on sopimus.** Kieli ei ilmaise omistusta, elinaikaa eikä
  virheitä. Ne sovitaan nimeämisellä, `const`-määreillä, paluuarvoilla ja
  dokumentaatiolla.
- **Pieni kieli, iso vastuu.** Kielessä on vähän rakenteita, joten mallit
  (*Käytännössä*-osiot lukujen lopussa) korvaavat puuttuvia
  kieliominaisuuksia: rajapinnat funktio-osoittimilla,
  resurssienhallinta `goto`-siivouksella ja kapselointi läpinäkymättömillä
  tyypeillä.

## Vastaavuudet muihin kieliin

| Asia | Python / Java | C++ | C |
|----------------|------------------|----------------------|------------------------------|
| Merkkijono | `str`, `String` | `std::string` | `char`-taulukko, päättyy `'\0'` |
| Dynaaminen taulukko | `list`, `ArrayList` | `std::vector` | `malloc` + `realloc` itse (luku 8) |
| Hajautustaulu | `dict`, `HashMap` | `std::unordered_map` | ei standardikirjastossa |
| Luokka ja rajapinta | `class`, `interface` | `class`, virtuaalifunktiot | `struct` + funktio-osoitintaulu (luku 9) |
| Kapselointi | `_nimi`, `private` | `private` | läpinäkymätön tyyppi (luku 9) |
| Virheet | poikkeukset | poikkeukset, `std::expected` | paluuarvo, `errno` (luku 11) |
| Resurssien vapautus | GC, `with`, `try-with-resources` | RAII | `goto`-siivous, init/destroy-parit |
| Geneerisyys | dynaaminen tyypitys, generics | mallit | `void *`, makrot, `_Generic` |
| Modulit | `import` | otsikot, C++20-modulit | otsikkotiedostot ja linkitys |

## Hinnat

C:ssä useimmat operaatiot ovat halpoja ja niiden hinta näkyy koodissa.
Kalliit asiat ovat niitä, joita ohjelmoija kirjoittaa itse:

- **Muistinvaraus.** `malloc` ja `free` voivat ottaa lukon ja etsiä
  vapaata tilaa. Kuumissa silmukoissa varataan kerran ja käytetään
  uudelleen, tai käytetään areenaa (luku 8).
- **Merkkijonojen käsittely.** `strlen` käy merkkijonon läpi joka kutsulla.
  `strlen` silmukan ehdossa tekee lineaarisesta algoritmista
  neliöllisen. Pituus kannattaa kuljettaa mukana (viipale, luku 7).
- **Rakenteet arvona.** Iso rakenne kopioidaan kokonaan, kun se välitetään
  tai palautetaan arvona. Suuret rakenteet välitetään osoittimina.
- **Epäsuoruus.** Funktio-osoittimen kautta tehtyä kutsua kääntäjä ei
  yleensä voi upottaa (*inline*). Hinta on pieni mutta näkyy tiukoissa
  silmukoissa.
- **Muistin käyttötapa.** Välimuistin kannalta peräkkäinen läpikäynti on
  moninkertaisesti nopeampaa kuin hajasaanti. Taulukko on lähes aina
  linkitettyä listaa nopeampi.

## Tärkeimmät sudenkuopat

1. **Määrittelemätön käyttäytyminen** ei aina kaada ohjelmaa. Optimoiva
   kääntäjä saa olettaa, ettei sitä tapahdu, ja voi poistaa koodia sen
   perusteella (luku 11).
2. **Etumerkittömät vertailut.** `-1 < 1u` on epätosi, ja `size_t`-tyyppinen
   silmukkamuuttuja ei koskaan ole negatiivinen (luku 3).
3. **Merkkijonon päättyminen.** Kopiointifunktiot eivät aina kirjoita
   päättävää nollamerkkiä (`strncpy`). Käytä `snprintf`iä (luku 7).
4. **Osoittimen elinaika.** Osoitin paikalliseen muuttujaan on roikkuva
   funktion palattua. Osoitin dynaamiseen muistiin on roikkuva `free`n
   jälkeen, myös kopiot siitä (luku 8).
5. **Kokonaislukujen ylivuoto** etumerkillisillä tyypeillä on
   määrittelemätöntä. Tarkista ennen laskua (`<stdckdint.h>`, luku 11).
6. **Esikääntäjä on tekstinkorvausta.** Makron argumentti voi tulla
   lasketuksi kahdesti, ja sulkeiden puute muuttaa laskujärjestyksen
   (luku 9).

## Lukuohje

Jos osaat jo ohjelmoida C:n kaltaisella kielellä:

1. Lue jokaisen luvun lopusta ensin *Itsearviointi*. Jos osaat kaikki
   väitteet, siirry seuraavaan lukuun.
2. Lue *Käytännössä*-osiot kaikista luvuista. Niissä ovat C-kehittäjien
   käyttämät mallit, joita muiden kielten osaaja ei tunne.
3. Luvut 5 (osoittimet), 7 (dynaaminen muisti) ja 11 (virheenkäsittely)
   kannattaa lukea kokonaan, sillä niissä C eroaa muista kielistä eniten.
4. Pikaopas (`c-kieli-pikaopas.pdf`) kokoaa syntaksin, mallit, hinnat ja
   sudenkuopat muutamalle sivulle.
