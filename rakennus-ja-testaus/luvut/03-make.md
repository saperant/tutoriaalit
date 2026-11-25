# Make

Make on vanhin ja yleisin rakennustyökalu. Se ei tiedä mitään
C-kielestä. Se tuntee vain *kohteita*, niiden *riippuvuuksia* ja
*komentoja*, joilla kohde tehdään riippuvuuksistaan. Make vertaa
tiedostojen muutosaikoja: kohde on vanhentunut, jos se puuttuu tai jos
jokin sen riippuvuuksista on muuttunut kohteen jälkeen. Vanhentunut
kohde tehdään uudelleen, ajantasaiseen ei kosketa. Tämä yksinkertainen
sääntö riittää erilliseen käännökseen, kunhan riippuvuudet on kuvattu
oikein.

Make on hyvä valinta pieneen ja keskikokoiseen projektiin, joka
käännetään yhdellä alustalla, sekä minkä tahansa komentojen
ketjuttamiseen: dokumenttien rakentamiseen, datan käsittelyyn ja
testien ajamiseen. Tämänkin tutoriaalin PDF:t rakennetaan Makella.

## Säännöt

Säännön ensimmäinen rivi on kohde, kaksoispiste ja riippuvuudet.
Seuraavat rivit ovat komentoja, ja ne alkavat sarkainmerkillä, eivät
välilyönneillä. Tämä on Maken tunnetuin sudenkuoppa: välilyönneillä
sisennetty komento antaa virheen `missing separator`.

```{.makefile tiedosto="esimerkit/03-make/Makefile" osa="saannot"}
```

Komennoissa käytetään *automaattisia muuttujia*: `$@` on kohde, `$<`
ensimmäinen riippuvuus ja `$^` kaikki riippuvuudet. Niiden ansiosta
tiedostonimiä ei toisteta, ja sääntöä voi muuttaa yhdestä kohdasta.
Ensimmäinen kohde (`tilasto`) on *oletuskohde*, jonka pelkkä `make`
rakentaa.

Muuttujat noudattavat Maken omia käytäntöjä, ja niitä kannattaa
noudattaa, koska sekä käyttäjät että Maken sisäiset säännöt tuntevat
ne:

| Muuttuja | Merkitys |
|----------|----------|
| `CC` | C-kääntäjä (oletus `cc`) |
| `CFLAGS` | C-kääntäjän valitsimet |
| `CPPFLAGS` | esikäsittelijän valitsimet (`-I`, `-D`) |
| `LDFLAGS` | linkkerin valitsimet ennen objekteja (`-L`) |
| `LDLIBS` | kirjastot objektien jälkeen (`-lm`) |

Esimerkin Makefile ei aseta muuttujaa `CC`, joten se tulee
ympäristöstä. Komento `make CC=clang-20` vaihtaa kääntäjän ilman, että
Makefileä muokataan.

## Valekohteet

Kaikki kohteet eivät ole tiedostoja. `testaa` ajaa ohjelman ja
`siivoa` poistaa käännöstuotteet. Ne merkitään erikoiskohteen
`.PHONY` riippuvuuksiksi:

```{.makefile tiedosto="esimerkit/03-make/Makefile" osa="phony"}
```

Ilman merkintää Make tulkitsisi kohteen tiedostoksi. Jos hakemistoon
syntyisi tiedosto nimeltä `testaa`, Make pitäisi kohdetta ajantasaisena
eikä ajaisi testejä enää koskaan. Valekohde on aina vanhentunut, joten
sen komennot ajetaan joka kerta. Valekohteen riippuvuudet toimivat
kuten muutkin: `testaa` rakentaa ensin ohjelman, jos se on vanhentunut.

## Make päättää, mitä tehdään

Esimerkki rakentaa ohjelman, rakentaa sen heti uudelleen, muuttaa
lähdetiedoston ja lopuksi otsakkeen. Komento `touch` päivittää
tiedoston muutosajan muuttamatta sisältöä, mikä riittää Makelle:

```{.bash tiedosto="esimerkit/03-make/aja.sh"}
```

```{.tuloste tiedosto="esimerkit/03-make.odotettu"}
```

Kolme ensimmäistä tapausta toimivat kuten pitää. Ensimmäinen rakennus
kääntää molemmat tiedostot ja linkittää. Toinen ei tee mitään. Kun
`tilasto.c` muuttuu, vain `tilasto.o` käännetään uudelleen, ja
ohjelma linkitetään, koska sen riippuvuus muuttui.

Neljäs tapaus on virhe. Otsake `tilasto.h` muuttui, mutta Make
ilmoittaa, ettei mitään tarvitse tehdä. Syy on Makefilessä:
riippuvuudeksi on kirjoitettu vain `.c`-tiedosto. Make ei tiedä, että
`main.c` ja `tilasto.c` lukevat otsakkeen. Jos otsakkeeseen olisi
lisätty rakenteen kenttä, toinen objektitiedosto käyttäisi vanhaa
rakennetta ja toinen uutta, ja ohjelma toimisi väärin ilman yhtään
varoitusta. Tällainen vika katoaa komennolla `make siivoa && make`,
minkä vuoksi se jää usein selvittämättä.

Vian näkee, kun Makefilen riippuvuudet piirtää verkoksi. Esimerkin
viimeinen vaihe tekee sen: `make -pn` tulostaa Maken *tietokannan* eli
kaikki kohteet ja riippuvuudet sellaisina kuin Make ne näkee, ja
esimerkkien skripti `verkko.sh` poimii niistä tiedostojen väliset
kaaret Graphvizin DOT-muotoon.

```{.dot tiedosto="esimerkit/03-make/verkko.dot" otsikko="Ensimmäisen Makefilen riippuvuusverkko Maken tietokannasta piirrettynä. Nuoli kulkee riippuvuudesta kohteeseen. Otsaketta `lahde/tilasto.h` ei ole verkossa lainkaan, joten sen muutos ei voi vanhentaa mitään."}
```

Make käy verkon läpi kohteesta taaksepäin ja tekee uudelleen jokaisen
solmun, jonka jokin edeltäjä on sitä uudempi. Tiedosto, joka ei ole
verkossa, ei vaikuta mihinkään.

Otsakeriippuvuuksia voisi kirjoittaa käsin (`main.o: lahde/tilasto.h`),
mutta ne vanhenevat heti, kun joku lisää `#include`-rivin. Oikea
ratkaisu on antaa kääntäjän kirjoittaa ne, ja se on seuraavan luvun
ensimmäinen aihe.

## Maken tulosteen lukeminen

Make tulostaa jokaisen komennon ennen sen ajamista. Tuloste on siksi
myös rakennuksen loki: siitä näkee, millä valitsimilla kukin tiedosto
käännettiin. Linkkauskomennon tuplavälilyönti (`gcc-14  main.o`) on
tyhjä `LDFLAGS`-muuttuja. Muutama valitsin on hyödyllinen vianetsinnässä:

```text
make -n          näytä komennot, älä aja niitä
make -B          tee kaikki kohteet uudelleen
make -d          kerro, miksi kukin kohde tehdään (paljon tulostetta)
make --trace     näytä kohde ja syy jokaisen komennon kohdalla
make -p          tulosta kaikki säännöt ja muuttujat, myös sisäiset
```

## Käytännössä

- **Kirjoita riippuvuudet koneella, ei käsin.** Käsin kirjoitettu
  otsakeriippuvuus vanhenee ensimmäisessä `#include`-muutoksessa.
  Seuraavan luvun `-MMD` korjaa tämän pysyvästi.
- **Merkitse valekohteet.** Jokainen kohde, joka ei tuota samannimistä
  tiedostoa (`testaa`, `siivoa`, `asenna`), kuuluu `.PHONY`-listaan.
- **Käytä vakiintuneita muuttujanimiä.** `CC`, `CFLAGS`, `CPPFLAGS`,
  `LDFLAGS` ja `LDLIBS` ovat sopimus Makefilen ja sen käyttäjän välillä:
  jakelupaketoijat, CI ja ristiinkääntäjät asettavat juuri niitä.
- **Älä luota siivoukseen.** Jos `make siivoa && make` korjaa vian,
  riippuvuuksissa on virhe. Se kannattaa korjata heti, koska seuraavaksi
  se ilmenee jonkun toisen koneella eri muodossa.

## Itsearviointi

- Osaat kirjoittaa Make-säännön automaattisilla muuttujilla `$@`, `$<`
  ja `$^` ja kertoa, milloin Make ajaa sen.
- Osaat merkitä valekohteet ja selittää, mitä tapahtuu, jos merkintä
  puuttuu.
- Osaat tunnistaa puuttuvan otsakeriippuvuuden oireet ja selittää,
  miksi `make siivoa` peittää vian.
- Osaat vaihtaa kääntäjän ja valitsimet komentoriviltä muokkaamatta
  Makefileä.
