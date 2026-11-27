# Tulkki viitetoteutuksena

Tarkistetun syntaksipuun voi suorittaa suoraan. **Puuta kulkeva
tulkki** (*tree-walking interpreter*) käy puun läpi ja laskee jokaisen
solmun arvon. Se on hidas verrattuna käännettyyn koodiin, mutta se on
lyhyt ja selkeä, ja siksi se on paras mahdollinen **viitetoteutus**:
kun kääntäjä ja tulkki tulostavat samalle ohjelmalle eri tuloksen,
virhe on lähes aina kääntäjässä. Luvun 17 differentiaalitestaus
perustuu tähän.

## Kehykset

Tulkki tarvitsee kullekin funktiokutsulle **kehyksen**
(*activation record*), jossa ovat kutsun muuttujat. Koska semanttinen
analyysi numeroi muuttujat (luku 7), kehys on pelkkä taulukko
(`std::vector<std::int64_t>`), ja muuttujan haku on indeksointi.
Funktiokutsu luo kehyksen ja kopioi argumentit parametrien paikoille:

```{.cpp tiedosto="esimerkit/kide/tulkki.cpp" osa="kehys"}
```

Rekursio toimii, koska jokainen kutsu luo uuden kehyksen. Tulkki
käyttää C++:n omaa kutsupinoa: Kide-funktion kutsu on C++-funktion
`kutsu` kutsu. Siksi tulkki rajoittaa kutsujen syvyyttä; muuten
päättymätön rekursio Kide-ohjelmassa kaataisi tulkin.

## Lauseet ja ohjausvuo

Lauseen suoritus palauttaa tiedon siitä, suorittiko se
`return`-lauseen. Arvo kulkee ylöspäin silmukoiden ja lohkojen läpi
funktiokutsuun asti:

```{.cpp tiedosto="esimerkit/kide/tulkki.cpp" osa="lause"}
```

`std::optional` on tässä selkeämpi kuin poikkeus, jota monet tulkit
käyttävät `return`-lauseeseen. Poikkeus ohjausvuona on C++:ssa kallis
ja hämärtää koodin kulkua; paluuarvo näkyy jokaisessa kohdassa, jossa
se voi syntyä.

## Lausekkeet

Lausekkeen arvo lasketaan rekursiivisesti. Totuusarvot esitetään
lukuina 0 ja 1, samoin kuin konekielessä:

```{.cpp tiedosto="esimerkit/kide/tulkki.cpp" osa="arvo"}
```

Kaksi kohtaa ansaitsee huomion. Aritmetiikka kutsuu luvun 2
`semantiikka`-funktioita eikä C++:n operaattoreita, joten tulkki on
määritelmän mukainen myös ylivuodossa ja nollalla jakamisessa. Lisäksi
`&&` ja `||` käsitellään ennen operandien laskemista, koska ne laskevat
oikean puolen vain tarvittaessa. Oikosulku näkyy, kun oikea puoli
kutsuu funktiota, jolla on sivuvaikutus:

```{.rust tiedosto="esimerkit/ohjelmat/oikosulku.kide"}
```

```{.tuloste tiedosto="esimerkit/ohjelmat/oikosulku.odotettu"}
```

Laskentajärjestys on osa merkitystä myös muualla: Kide laskee
binäärioperaation vasemman operandin ennen oikeaa ja argumentit
vasemmalta oikealle. C ja C++ jättävät argumenttien laskentajärjestyksen
määrittelemättä, mikä on ollut lukemattomien siirrettävyysvirheiden
lähde.

## Ajonaikaiset virheet

Tulkki raportoi ajonaikaisen virheen ja palauttaa paluuarvon 3:

```{.rust tiedosto="esimerkit/virheet/ajo_syva.kide"}
```

```{.tuloste tiedosto="esimerkit/virheet/ajo_syva.virhe"}
```

Raja on 1000 kutsua, mikä riittää testiohjelmille ja pitää C++:n pinon
turvallisena myös AddressSanitizerin kanssa, joka kasvattaa kehyksiä.
Käännetyllä ohjelmalla ei ole tätä rajaa: sen pino on Linuxissa
oletuksena 8 MiB, ja yksi Kide-kehys vie muutamia kymmeniä tavuja.
Raja on siis tulkin ominaisuus eikä kielen. Differentiaalitestien
ohjelmat on generoitu niin, ettei raja tule vastaan.

## Tulkista kääntäjään

Puuta kulkeva tulkki tekee joka kerta saman työn: se valitsee
solmutyypin, hakee operandit ja hyppää käsittelijään. Kääntäjä tekee
nämä valinnat kerran, käännösaikana, ja jättää ajonaikaan vain
laskennan. Välimuotoja on paljon:

| Toteutus | Esimerkkejä | Nopeus |
|----------|-------------|--------|
| puuta kulkeva tulkki | varhainen Ruby, monet konfiguraatiokielet | hidas |
| tavukooditulkki | CPython, Lua, varhainen Java | 2–10 × puuta nopeampi |
| JIT-kääntäjä | V8, HotSpot, LuaJIT, PyPy | lähellä käännettyä |
| AOT-kääntäjä | GCC, Clang, rustc, Kide | nopein käynnistys ja tasainen |

Tavukoodi on välikieli, jota tulkki suorittaa. Se on lähellä tämän
tutoriaalin välikieltä (luku 9), ja moni JIT-kääntäjä alkaa
tulkitsemalla tavukoodia ja kääntää vain usein suoritetut osat.

## Käytännössä

- **Kirjoita tulkki ennen kääntäjää.** Tulkki on lyhyt, ja sillä voi
  kokeilla kielen merkitystä ennen kuin takaosaa on olemassa. Se
  jää testien viitetoteutukseksi.
- **Jaa semantiikka tulkin ja kääntäjän kesken.** Aritmetiikka,
  vakioiden laskostus ja ajonaikainen kirjasto käyttävät samaa
  määrittelyä.
- **Määrittele laskentajärjestys.** Sivuvaikutuksellisten lausekkeiden
  järjestys on osa merkitystä, ja määrittelemätön järjestys on
  siirrettävyysvirhe odottamassa.
- **Rajaa tulkin resurssit.** Kutsujen syvyys, silmukoiden
  kierrokset ja muisti rajataan, jos tulkki ajaa käyttäjien ohjelmia.

## Itsearviointi

- Osaat toteuttaa puuta kulkevan tulkin, jossa muuttujat ovat
  numeroidussa kehyksessä ja `return` välittyy paluuarvona.
- Osaat toteuttaa oikosulkevat `&&`- ja `||`-operaattorit ja näyttää
  esimerkillä, miksi oikosulku on osa merkitystä.
- Osaat selittää, miksi tulkki on hyvä viitetoteutus kääntäjän
  testaukseen.
- Osaat sijoittaa puutulkin, tavukooditulkin, JIT- ja AOT-kääntäjän
  samalle jatkumolle ja kertoa niiden erot.
