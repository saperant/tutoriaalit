# Staattinen analyysi

Testit ja sanitoijat löytävät virheet koodista, jota ajetaan.
*Staattinen analyysi* tutkii koodia ajamatta sitä, joten se löytää
virheitä myös poluilta, joita yksikään testi ei kokeile. Hintana ovat
väärät hälytykset: analysaattori ei aina tiedä, mitkä tilanteet ovat
mahdollisia. Hyvä analyysi on siksi säädetty projektiin: käytössä ovat
tarkistukset, joiden löydökset kannattaa korjata, ja loput on kytketty
pois perusteluineen.

Tavallisesti käytetään kolmea tasoa:

| Työkalu | Tapa | Vahvuus |
|---------|------|---------|
| kääntäjän varoitukset | tyypit ja vuo yhdessä funktiossa | nopea, aina käytössä |
| clang-tidy | Clangin jäsennyspuu, polkuherkkä analyysi | laaja, säädettävä, korjausehdotukset |
| cppcheck | oma jäsennin, arvoalueanalyysi | ei tarvitse käännöskomentoja, vähän vääriä hälytyksiä |

## Tutkittava koodi

Asetustiedoston käsittelijässä on neljä tavallista virhettä:
etumerkillisen ja etumerkittömän arvon vertailu, `atoi`, joka ei
ilmoita virheestä, muistivuoto varhaisessa paluussa ja taulukon rajan
ylitys:

```{.c tiedosto="esimerkit/11-analyysi/asetus.c"}
```

Mikään näistä ei välttämättä näy testeissä. Vuoto syntyy vain liian
pitkällä tunnisteella, `atoi` palauttaa virheelliselle syötteelle
nollan, joka voi olla kelvollinen arvo, ja rajan ylitys lukee pinosta
jotain, mikä sattuu olemaan siellä.

## Kolme työkalua

Esimerkki ajaa kaikki kolme työkalua sekä virheelliselle että korjatulle
tiedostolle ja näyttää kustakin löydöksestä tiedoston, rivin ja
tarkistuksen nimen:

```{.bash tiedosto="esimerkit/11-analyysi/aja.sh"}
```

```{.tuloste tiedosto="esimerkit/11-analyysi.odotettu"}
```

Työkalut löytävät eri asioita, ja jokaisella on löydöksiä, joita muut
eivät näe:

- **GCC** varoittaa vertailusta `int` ja `size_t` (`-Wsign-compare`,
  osa `-Wextra`-joukkoa) ja rajan ylityksestä (`-Warray-bounds`).
  Jälkimmäinen toimii vain optimoinnin kanssa, koska tarvittava
  arvoanalyysi tehdään optimointivaiheissa. Varoitukset kannattaa siksi
  tarkistaa myös `-O2`-käännöksestä.
- **clang-tidy** löytää kavennuksen (osoitinero `ptrdiff_t` sijoitetaan
  `int`-muuttujaan), `atoi`-funktion käytön (`cert-err34-c`: virhettä ei
  voi havaita), muistivuodon (`unix.Malloc`), `strcpy`-funktion ja
  alustamattoman arvon palauttamisen. Vuodon ja rajan ylityksen
  löytää *Clang Static Analyzer* (`clang-analyzer-*`), joka seuraa
  ohjelman polkuja symbolisesti.
- **cppcheck** löytää rajan ylityksen ja vuodon omalla
  analyysillään ja ehdottaa lisäksi, että muuttamaton taulukko
  merkitään `const`-määreellä (`constVariable`).

Korjattu versio vertailee `size_t`-arvoja, jäsentää luvun `strtol`-
funktiolla ja tarkistaa virheet, tarkistaa pituuden ennen varausta ja
lukee taulukon viimeisen alkion oikealla indeksillä. Kaikki kolme
työkalua ovat hiljaa:

```{.c tiedosto="esimerkit/11-analyysi/korjattu.c"}
```

## Asetukset versionhallintaan

clang-tidyn tarkistukset luetaan projektin juuren tiedostosta
`.clang-tidy`. Kun asetukset ovat versionhallinnassa, kehittäjän
editori, komentorivi ja CI käyttävät samoja sääntöjä:

```{.yaml tiedosto="esimerkit/11-analyysi/.clang-tidy"}
```

Ryhmät valitaan jokerimerkeillä, ja yksittäiset tarkistukset kytketään
pois miinusmerkillä. Tässä `DeprecatedOrUnsafeBufferHandling` on pois,
koska se varoittaa jokaisesta `memcpy`-kutsusta ja suosittelee C11:n
valinnaisen liitteen K funktioita (`memcpy_s`), joita glibc ei
toteuta. Pois kytketty tarkistus ja sen syy kuuluvat samaan paikkaan.
`WarningsAsErrors: '*'` tekee löydöksistä virheitä, jolloin
`clang-tidy` palauttaa virhekoodin ja CI epäonnistuu.

clang-tidy tarvitsee tiedostojen käännöskomennot. Esimerkissä ne
annetaan komentorivillä kaksoisviivan jälkeen (`-- -std=c17`).
Projektissa ne tulevat CMaken tiedostosta `compile_commands.json`
(`clang-tidy -p build/kehitys`), ja `run-clang-tidy` analysoi kaikki
tiedostot rinnakkain. Yksittäisen löydöksen voi ohittaa kommentilla
`// NOLINT(tarkistus)` ja cppcheckin kommentilla
`// cppcheck-suppress tunniste`. Ohitus kertoo lukijalle, että asia on
tutkittu, joten sen viereen kirjoitetaan syy.

Samaan paikkaan kuuluu muotoilun asetustiedosto `.clang-format`.
`clang-format -i` muotoilee tiedostot sen mukaan, ja CI:ssä
`clang-format --dry-run -Werror` epäonnistuu, jos jokin tiedosto
poikkeaa muotoilusta. Kun muotoilu on työkalun vastuulla, katselmoinnissa
ei keskustella sisennyksistä, ja muutosten erot pysyvät pieninä.

## -Werror ja varoitusten hallinta

Varoitus, joka ei pysäytä mitään, jää korjaamatta. `-Werror` tekee
varoituksista virheitä, mutta sen käyttö vaatii harkintaa:

- **CI:ssä kyllä, julkaistavassa rakennuksessa ei.** Uusi
  kääntäjäversio tuo uusia varoituksia. Jos käyttäjän rakennus
  epäonnistuu niiden takia, `-Werror` estää ohjelman asentamisen
  uudemmalla kääntäjällä ilman, että koodissa on vikaa. Tämän
  tutoriaalin esimerkit kirjoittavat lipun suoraan, koska ne
  käännetään aina samalla kääntäjällä. Julkaistavassa CMake-projektissa
  käytetään kohteen ominaisuutta `COMPILE_WARNING_AS_ERROR`, jonka
  CI asettaa päälle ja jonka käyttäjä voi ohittaa valitsimella
  `cmake --compile-no-warning-as-error`.
- **Vanhaan koodiin vähitellen.** Kun varoituksia on satoja, ne
  korjataan tiedosto tai varoitus kerrallaan. `-Werror=format-security`
  ja muut yksittäiset varoitukset voi muuttaa virheiksi ennen kuin
  kaikki on korjattu.
- **Analyysi vain muuttuneisiin tiedostoihin.** Suuressa vanhassa
  projektissa CI voi ajaa analyysin vain muutokselle, jolloin uutta
  velkaa ei synny, vaikka vanhaa on vielä jäljellä.

Varoitusten määrä on yksi harvoista koodin laadun mittareista, joka on
yksiselitteinen: nolla on ainoa arvo, joka pysyy nollana.

## Käytännössä

- **Kolme kerrosta.** Kääntäjän varoitukset jokaisessa käännöksessä,
  clang-tidy ja cppcheck CI:ssä. Työkalut eivät korvaa toisiaan.
- **Asetukset tiedostoon.** `.clang-tidy` ja cppcheckin
  ohitustiedosto ovat versionhallinnassa, jotta kaikki ajavat samaa
  analyysiä.
- **Kytke pois perustellen.** Jokainen pois kytketty tarkistus ja
  jokainen `NOLINT` saa syyn viereensä. Ilman syytä ohitusta ei voi
  arvioida myöhemmin.
- **Varoitukset virheiksi CI:ssä.** `-Werror` ja `WarningsAsErrors`
  pitävät varoitusmäärän nollassa. Julkaistavan lähdekoodin oletus on
  ilman `-Werror`-lippua.
- **Analysoi myös optimoitu käännös.** Osa GCC:n varoituksista vaatii
  optimoinnin tuottamaa arvoanalyysiä.

## Itsearviointi

- Osaat ajaa GCC:n varoitukset, clang-tidyn ja cppcheckin samalle
  koodille ja kertoa, millaisia virheitä kukin löytää.
- Osaat kirjoittaa `.clang-tidy`-tiedoston, joka valitsee
  tarkistusryhmät, kytkee yksittäisen tarkistuksen pois ja tekee
  löydöksistä virheitä.
- Osaat korjata tyypilliset löydökset: etumerkkivertailun, `atoi`-
  funktion, vuodon varhaisessa paluussa ja rajan ylityksen.
- Osaat perustella, missä `-Werror` kuuluu käyttää ja missä ei.
