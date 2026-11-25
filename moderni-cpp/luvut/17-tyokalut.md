# Työkalut ja testaus {.runko-tyokalut}

C++-kehittäjän päivittäiset työkalut ovat käännösjärjestelmä, debuggeri,
sanitoijat, staattinen analyysi, profiloija ja testikehys. Tämä luku
kertoo, mitä kukin tekee C++-projektissa. Yleiset käytännöt, kuten
jatkuva integraatio, käsitellään taitopuun taidossa *Käännösjärjestelmät,
testaus ja CI*.

## Käännösjärjestelmä: CMake

CMake on C++-projektien yleisin käännösjärjestelmä. Se ei itse käännä,
vaan tuottaa käännösohjeet esimerkiksi Ninjalle tai Makelle. Projektin
kuvaus kirjoitetaan tiedostoon `CMakeLists.txt`. Luvun
[Ohjelman rakenne ja modulit](#ohjelman-rakenne-ja-modulit)
mittauslokille se on tällainen:

```{.cmake tiedosto="esimerkit/14-mittausloki/CMakeLists.txt"}
```

Nykyaikaisessa CMakessa asetukset kiinnitetään *kohteisiin* (`target_*`)
eikä globaaleihin muuttujiin. `PUBLIC`-asetukset periytyvät kohteen
käyttäjille, `PRIVATE` eivät. Käännös tehdään erilliseen hakemistoon:

```text
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build
ctest --test-dir build
```

Viimeinen komento ajaa `add_test`-komennolla rekisteröidyt testit.
CMaken rakenteita, esiasetuksia ja riippuvuuksien hakua käsittelee
tarkemmin taito *Käännösjärjestelmät, testaus ja CI*.

## Debuggaus ja sanitoijat

Debuggeri gdb (tai lldb) pysäyttää ohjelman keskeytyskohtiin ja näyttää
muuttujat ja kutsupinon. Ohjelma käännetään valitsimella `-g`, jotta
debug-tieto on mukana. Tavallisimmat komennot ovat `break tiedosto:rivi`,
`run`, `next`, `step`, `print lauseke` ja `backtrace`. Kokonainen
debuggausistunto käydään läpi taidossa *Käännösjärjestelmät, testaus ja
CI*.

Sanitoijat löytävät virheet, joita debuggerilla ei edes etsitä:
AddressSanitizer muistivirheet, UndefinedBehaviorSanitizer
määrittelemättömän käyttäytymisen ja ThreadSanitizer kilpatilanteet. Ne
ovat käytössä tämän tutoriaalin kaikissa testeissä, ja
AddressSanitizerin raportteja on luvussa
[C++ kokeneelle](#c-kokeneelle). Raportin ensimmäinen rivi nimeää
virheen lajin, ja sen alla ovat kutsupinot: missä virheellinen käyttö
tapahtui ja missä muisti varattiin ja vapautettiin. Valitsin
`-D_GLIBCXX_ASSERTIONS` kytkee lisäksi päälle libstdc++:n omat
tarkistukset, kuten indeksien rajatarkistuksen `std::vector`in
`operator[]`-kutsussa.

## Staattinen analyysi ja muotoilu

clang-tidy tarkistaa koodin käännöksen tasolla satojen sääntöjen avulla:
esimerkiksi tarpeettomat kopiot, puuttuvat `override`-merkinnät,
käyttö siirron jälkeen ja C++ Core Guidelines -ohjeiden rikkomukset.
Luvun [Siirtosemantiikka](#siirtosemantiikka) puskuriesimerkki lukee
tarkoituksella olion kokoa siirron jälkeen, ja clang-tidy huomaa sen:

```text
$ clang-tidy -checks='-*,bugprone-use-after-move' 09-puskuri.cpp \
      -- -std=c++23
09-puskuri.cpp:68:52: warning: 'a' used after it was moved
    [bugprone-use-after-move]
   68 |     std::println("  a.koko() = {}, c.koko() = {}", a.koko(), ...
09-puskuri.cpp:67:17: note: move occurred here
   67 |     Puskuri c = std::move(a);
```

clang-format muotoilee koodin projektin tyyliasetusten mukaan, jolloin
tyylistä ei tarvitse kiistellä katselmoinneissa. Molemmat lukevat
asetuksensa projektin juuren tiedostoista (`.clang-tidy`,
`.clang-format`), ja ne ajetaan jatkuvassa integraatiossa.

## Profilointi

Suorituskyky mitataan ennen kuin sitä optimoidaan. Linuxissa `perf
record` ja `perf report` näyttävät, missä funktioissa ohjelma käyttää
aikansa, ja `perf stat` kertoo laitteistolaskureista esimerkiksi
välimuistihudit. Profiloitava ohjelma käännetään optimoituna (`-O2`) ja
debug-tiedon kanssa (`-g`), jotta tulokset vastaavat todellista ohjelmaa
ja funktioiden nimet näkyvät. Mikrovertailuihin käytetään kirjastoa
Google Benchmark, joka toistaa mittaukset ja estää kääntäjää
optimoimasta mitattavaa koodia pois. Kielikohtaista optimointia
käsitellään taitopuun taidossa *C++:n suorituskyky*.

## Yksikkötestaus

Yksikkötesti kutsuu funktiota tunnetuilla syötteillä ja tarkistaa
tuloksen. C++-projekteissa käytetään yleisimmin kehyksiä GoogleTest ja
Catch2. Niiden periaatteen näkee pienestä itse tehdystä kehyksestä.
Testattavana on funktio, joka jäsentää keston muodossa `1h30m`:

```{.cpp tiedosto="esimerkit/17-testit.cpp" osa="testattava"}
```

Kehys rekisteröi testit automaattisesti makron avulla. Jokainen
`TESTI`-makro määrittelee funktion ja staattisen olion, jonka muodostin
lisää funktion luetteloon ennen `main`-funktion alkua.

```{.cpp tiedosto="esimerkit/17-testit.cpp" osa="kehys"}
```

Luettelo on funktion sisäinen staattinen muuttuja, joka alustetaan
ensimmäisellä kutsulla. Jos se olisi globaali muuttuja, eri
käännösyksiköiden testien rekisteröinti voisi tapahtua ennen kuin
luettelo on alustettu. `std::source_location` kertoo epäonnistuneen
tarkistuksen rivin ilman makroja.

Testit kuvaavat käyttäytymistä, myös virhetapauksia:

```{.cpp tiedosto="esimerkit/17-testit.cpp" osa="testit"}
```

```{.cpp tiedosto="esimerkit/17-testit.cpp" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/17-testit.odotettu"}
```

Paluuarvo on nolla vain, jos kaikki testit menevät läpi, joten
käännösjärjestelmä ja jatkuva integraatio havaitsevat epäonnistumisen.
GoogleTest ja Catch2 tarjoavat saman perusidean lisäksi muun muassa
testien suodatuksen, parametrisoidut testit, tarkemmat
vertailuilmoitukset ja tulosraportit.

## Käytännössä

- **Varoitukset virheinä jatkuvassa integraatiossa.** Paikallisesti
  varoitukset voivat olla varoituksia, mutta CI hylkää koodin, joka
  tuottaa niitä. Muuten varoituksia kertyy, ja uudet hukkuvat vanhoihin.
- **Debug-käännös sanitoijilla, julkaisu optimoituna.** Testit ajetaan
  sanitoijien kanssa, koska ne löytävät virheet, jotka optimoitu käännös
  piilottaa tai muuttaa satunnaisiksi.
- **Testit ovat osa käännöstä.** CMaken `ctest` ajaa testit, ja ne
  kirjoitetaan samaan aikaan kuin koodi. Testattava koodi rakennetaan
  kirjastoksi, jota sekä ohjelma että testit käyttävät.
- **Testi kuvaa käyttäytymistä, ei toteutusta.** Testi tarkistaa
  julkisen rajapinnan tuloksia, jotta toteutusta voi muuttaa testejä
  rikkomatta. Virhetapaukset ja raja-arvot testataan yhtä huolellisesti
  kuin onnistuneet tapaukset.
- **Mittaa ennen kuin optimoit.** Profiili näyttää, missä aika kuluu;
  arvaus on yleensä väärä. Mikrovertailu ei korvaa koko ohjelman
  profilointia.
- **Toistettava kehitysympäristö.** Kääntäjäversio, kirjastot ja
  työkalut kiinnitetään kehityskonttiin ja paketinhallintaan, jotta
  kaikki kehittäjät ja CI kääntävät samalla tavalla. Tämän tutoriaalin
  esimerkeille on valmis kehityskontti.

## Itsearviointi

- Osaat kirjoittaa CMake-projektin, jossa on kirjasto ja sitä käyttävä
  ohjelma.
- Osaat etsiä virheen gdb:llä ja sanitoijilla.
- Osaat kirjoittaa yksikkötestejä, jotka kattavat myös virhetapaukset.
- Osaat profiloida ohjelman perfillä ja kertoa, miksi mittaus tehdään
  optimoidulla käännöksellä.
