# Muotoilu ja virrat

Luvun muuntaminen tekstiksi ja tekstin kirjoittaminen virtaan ovat
työtä, jota lähes jokainen ohjelma tekee: lokit, raportit, JSON ja
protokollat. C++:ssa samaan tehtävään on monta rajapintaa eri
vuosikymmeniltä, ja niiden hinnat eroavat yli kymmenkertaisesti. Tässä
luvussa verrataan kuutta tapaa muuntaa kokonaisluku merkkijonoksi ja
mitataan, mitä `std::endl` tekee virralle. Tapaustutkimuksen (luku 11)
ensimmäinen vaihe maksaa juuri näitä hintoja.

## Kokonaisluku merkkijonoksi

C++:ssa on ainakin kuusi tapaa muuntaa luku tekstiksi:

```{.cpp tiedosto="esimerkit/10-muotoilu.cpp" osa="tavat"}
```

```{.cpp tiedosto="esimerkit/10-muotoilu.cpp" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/10-muotoilu.odotettu"}
```

Yksikään tapa ei varaa muistia: tulokset ovat lyhyitä, joten ne
mahtuvat merkkijonon sisäiseen puskuriin.

Mitattava kierros käsittelee tuhat eri lukua, jotta ennustin ei opi yhtä
syötettä, ja `piilota` estää kääntäjää laskemasta tuloksia etukäteen.
Aika mitataan luvun 2 kalibroidulla mittauksella:

```{.cpp tiedosto="esimerkit/10-muotoilu.cpp" osa="kierros"}
```

```{.cpp tiedosto="esimerkit/10-muotoilu.cpp" osa="vertailu"}
```

Erot ovat suuria sekä käskyissä että ajassa:

```{.makefile tiedosto="esimerkit/Makefile" osa="muotoilu"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-muotoilu.txt"}
```

```{.tuloste tiedosto="esimerkit/tulokset/10-muotoilu.txt"}
```

![Käskyt muunnosta kohden kuudella tavalla (sama data kuin yllä).](kuvat/muotoilu.png){width=70%}

`std::to_chars` (C++17) on nopein, koska se tekee vain muunnoksen: ei
lokaalia, ei muotoilumerkkijonon jäsennystä eikä virheiden
tarkistusta puskurin koon lisäksi. `snprintf` jäsentää
muotoilumerkkijonon ajon aikana ja kulkee C-kirjaston yleisen
tulostuskoneiston läpi. `std::format` tarkistaa muotoilun
käännösaikana mutta tekee silti tyypin mukaisen ajonaikaisen
valinnan. `std::ostringstream` on hitain: virran rakentaminen alustaa
lokaalin ja puskurin, ja jokainen `<<` kulkee virtuaalikutsujen ja
vartijaolion (engl. sentry) läpi.

Käytännön valinta riippuu tarpeesta. Lokirivien ja virheilmoitusten
tekemiseen `std::format` ja `std::print` ovat sopivia ja turvallisia.
Sarjallistamiseen, kuten JSONin, CSV:n tai protokollien tuottamiseen,
`std::to_chars` ja `std::from_chars` ovat oikeat työkalut: ne ovat
lokaalista riippumattomia, eli ne tuottavat saman tuloksen joka
koneella, ja ne ovat moninkertaisesti nopeampia. `std::ostringstream`
kuuluu vanhaan koodiin.

## Virtojen perushinnat

`std::ostream` puskuroi tulosteensa, ja puskurin tyhjennys on kallis:
tiedostovirrassa se on `write`-järjestelmäkutsu. `std::endl` kirjoittaa
rivinvaihdon *ja* tyhjentää puskurin, joten rivi kerrallaan tulostava
silmukka tekee järjestelmäkutsun joka rivillä. Merkki `'\n'` vain
lisää rivinvaihdon puskuriin. Esimerkin puskuri laskee
tyhjennyspyynnöt:

```{.cpp tiedosto="esimerkit/10-virrat.cpp" osa="laskeva"}
```

```{.cpp tiedosto="esimerkit/10-virrat.cpp" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/10-virrat.odotettu"}
```

Tuhat riviä, tuhat tyhjennystä vastaan yksi. `std::endl` on oikea
valinta vain, kun rivin pitää näkyä heti, kuten kehotteessa tai
viimeisessä viestissä ennen kaatumista; `std::cerr` tyhjentää itsensä
joka kirjoituksen jälkeen juuri tästä syystä.

Kaksi muuta oletusta maksaa samalla tavalla. `std::cout` on
oletuksena synkronoitu C:n `stdout`in kanssa, jotta `printf` ja
`std::cout` voi sekoittaa: jokainen kirjoitus kulkee silloin
C-kirjaston läpi ilman virran omaa puskuria. Kutsu
`std::ios::sync_with_stdio(false)` ohjelman alussa poistaa
synkronoinnin, jos ohjelma käyttää vain toista rajapintaa. Lisäksi
`std::cin` on sidottu `std::cout`iin (`tie`), jolloin jokainen luku
tyhjentää ensin tulosteen; `std::cin.tie(nullptr)` katkaisee
sidoksen. Molemmat ovat turvallisia eräajo-ohjelmissa, jotka lukevat
syötteen ja kirjoittavat tuloksen, mutta eivät vuorovaikutteisissa
ohjelmissa.

## Käytännössä

- **Muotoile lukuja `std::to_chars`illa** sarjallistamisessa ja
  `std::format`illa ihmisille luettavassa tulosteessa.
- **`'\n'`, ei `std::endl`**, kun rivin ei tarvitse näkyä heti.
- **`sync_with_stdio(false)` ja `cin.tie(nullptr)`** eräajo-ohjelman
  alkuun, jos se käyttää vain C++:n virtoja.
- **Älä rakenna virtaa silmukassa.** `std::ostringstream`in
  rakentaminen alustaa lokaalin ja puskurin joka kerta; käytä puskuria
  uudelleen tai `std::format_to`a valmiiseen puskuriin.
- **Lokaali vaikuttaa tulokseen.** Virrat ja `snprintf` muotoilevat
  ohjelman lokaalin mukaan; `to_chars` ja `from_chars` eivät käytä
  lokaalia lainkaan, joten tulos on sama joka koneella.

## Itsearviointi

- Osaat perustella, miksi `std::to_chars` on nopeampi kuin
  `snprintf`, `std::format` ja `std::ostringstream`.
- Osaat valita muotoilutavan sarjallistamiseen ja ihmiselle
  luettavaan tulosteeseen.
- Osaat selittää, mitä `std::endl` tekee rivinvaihdon lisäksi ja
  milloin sitä tarvitaan.
- Osaat kertoa, mitä `sync_with_stdio(false)` ja `cin.tie(nullptr)`
  muuttavat ja milloin ne ovat turvallisia.
