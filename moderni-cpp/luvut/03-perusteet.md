# Kielen perusteet modernisti {.runko-tyypit .runko-ohjaus}

Tässä luvussa käydään läpi pieniä mutta jokapäiväisiä parannuksia,
jotka tekevät koodista lyhyempää ja turvallisempaa.

## Tyyppipäättely: `auto`

Avainsana `auto` antaa kääntäjän päätellä muuttujan tyypin
alustuslausekkeesta. Tyyppi on edelleen staattinen ja kiinteä; se
vain jätetään kirjoittamatta.

```{.cpp tiedosto="esimerkit/03-auto.cpp" osa="paattely"}
```

Merkkijonoliteraali `"C++"` on tyypiltään merkkitaulukko, joka
muuttuu osoittimeksi `const char*`. Jos tarvitaan `std::string`, tyyppi
kannattaa kirjoittaa näkyviin.

`auto` pudottaa pois viittaukset ja `const`-määreen. Jos alkiota halutaan
muokata tai sen kopioimista välttää, viittaus on kirjoitettava itse:

```{.cpp tiedosto="esimerkit/03-auto.cpp" osa="viittaus"}
```

```{.tuloste tiedosto="esimerkit/03-auto.odotettu"}
```

Nyrkkisääntö silmukoille: `const auto&` lukemiseen, `auto&`
muokkaamiseen ja pelkkä `auto` vain halvoille tyypeille, kuten
kokonaisluvuille, kun kopio on tarkoituksellinen.

`auto` sopii erityisesti tilanteisiin, joissa tyyppi näkyy jo
lausekkeesta (`auto p = std::make_unique<Olio>()`) tai on pitkä ja
epäolennainen, kuten iteraattoreissa. Rajapinnoissa, joissa tyyppi
kertoo lukijalle jotain tärkeää, se kannattaa kirjoittaa auki.

## Yhtenäinen alustus

C++11 toi aaltosulkualustuksen, joka toimii samalla tavalla lähes kaikille
tyypeille:

```{.cpp tiedosto="esimerkit/03-alustus.cpp" osa="aaltosulut"}
```

Tyhjät aaltosulkeet *arvoalustavat* muuttujan: perustyypit saavat arvon
nolla. Tämä on hyvä oletus, sillä alustamattoman muuttujan lukeminen on
määrittelemätöntä käyttäytymistä.

Aaltosulkujen tärkein etu on, että ne kieltävät *kaventavat
muunnokset*, joissa tietoa voi kadota:

```{.cpp tiedosto="esimerkit/03-kaventaminen.ei-kaanny.cpp"}
```

Standardin mukaan aaltosulkeissa tapahtuva kaventaminen on virhe.
Clang antaa siitä käännösvirheen. GCC antaa muuttujan tapauksessa
oletuksena vain varoituksen, joka muuttuu virheeksi valitsimella
`-Werror` (kuten tämän tutoriaalin testeissä).

Yksi sudenkuoppa on syytä tuntea. Jos luokalla on
`std::initializer_list`-muodostin, kuten säiliöillä, aaltosulkeet
valitsevat sen:

```{.cpp tiedosto="esimerkit/03-alustus.cpp" osa="sudenkuoppa"}
```

### Jäsenten oletusarvot ja nimetyt alustimet

Rakenteen jäsenille voi antaa oletusarvot suoraan esittelyssä. C++20:n
*nimetyillä alustimilla* (*designated initializers*) voi asettaa vain
halutut jäsenet. Jäsenet on lueteltava esittelyjärjestyksessä.

```{.cpp tiedosto="esimerkit/03-alustus.cpp" osa="jasenet"}
```

```{.cpp tiedosto="esimerkit/03-alustus.cpp" osa="nimetyt"}
```

Jäsen, jota ei mainita, saa oletusarvonsa: `leveat.varit` on `true`.

## Rakenteiset sidonnat

C++17:n *rakenteinen sidonta* (*structured binding*) purkaa parin,
monikon, taulukon tai rakenteen jäsenet nimetyiksi muuttujiksi. Funktio
voi siten palauttaa useita arvoja ilman tulosparametreja:

```{.cpp tiedosto="esimerkit/03-rakenteet.cpp" osa="pari"}
```

```{.cpp tiedosto="esimerkit/03-rakenteet.cpp" osa="sidonnat"}
```

`Hinnasto` on tyyppialias, joka on määritelty `using`-esittelyllä. Se
korvaa vanhan `typedef`-syntaksin ja on luettavampi:

```{.cpp tiedosto="esimerkit/03-rakenteet.cpp" osa="using"}
```

Muotoilumäärite `{:<6}` tasaa arvon vasemmalle kuuden merkin levyiseen
kenttään ja `{:>5.2f}` oikealle viiden merkin kenttään kahdella
desimaalilla. Koska `std::map` pitää avaimet järjestyksessä, tuotteet
tulostuvat aakkosjärjestyksessä.

## Alustus `if`- ja `switch`-lauseissa

C++17:stä alkaen `if`- ja `switch`-lauseen ehtoon voi liittää
alustuksen. Muuttujan näkyvyys rajoittuu lauseeseen, mukaan lukien
`else`-haara:

```{.cpp tiedosto="esimerkit/03-rakenteet.cpp" osa="ehtoalustus"}
```

## Vahvasti tyypitetyt luettelot

Vanhat `enum`-luettelot muuttuvat huomaamatta kokonaisluvuiksi, ja
niiden nimet vuotavat ympäröivään näkyvyysalueeseen. `enum class`
korjaa molemmat ongelmat:

```{.cpp tiedosto="esimerkit/03-rakenteet.cpp" osa="enum"}
```

Molemmissa luetteloissa voi olla nimi `punainen`, koska nimiin viitataan
aina luettelon kautta: `Vari::punainen`. Arvoja ei voi vertailla
keskenään, eikä niitä voi sijoittaa kokonaislukuun ilman eksplisiittistä
muunnosta:

```{.cpp tiedosto="esimerkit/03-rakenteet.cpp" osa="vertailu"}
```

## `nullptr`

Tyhjä osoitin kirjoitetaan `nullptr`. Vanha `NULL` on kokonaisluku
nolla, mikä voi valita väärän funktion kuormitetuista vaihtoehdoista.
`nullptr` on omaa tyyppiään `std::nullptr_t`, joka muuntuu vain
osoittimiksi.

```{.cpp tiedosto="esimerkit/03-rakenteet.cpp" osa="nullptr"}
```

Koko ohjelma tulostaa:

```{.tuloste tiedosto="esimerkit/03-rakenteet.odotettu"}
```

## Syötteen lukeminen

Syöte luetaan luotettavimmin riveittäin funktiolla `std::getline` ja
jäsennetään sen jälkeen. Muotoiltu luku `std::cin >> x` jättää
virheellisen syötteen virtaan, asettaa virran virhetilaan ja jättää
rivinvaihdon lukematta, minkä vuoksi sen käsittely on hankalaa.

Seuraava ohjelma lukee tilausrivejä muodossa `tuote;määrä;hinta`.
Rivi jaetaan kenttiin `std::string_view`-näkymien avulla kopioimatta
merkkejä, ja luvut muunnetaan funktiolla `std::from_chars`, joka ei
varaa muistia, ei heitä poikkeuksia eikä riipu maa-asetuksista.
Jäsennin palauttaa `std::optional`-arvon, joten virheellinen rivi on
tavallinen paluuarvo eikä poikkeus.

```{.cpp tiedosto="esimerkit/03-syote.cpp" osa="rivi"}
```

```{.cpp tiedosto="esimerkit/03-syote.cpp" osa="luku"}
```

Syötteellä

```{.tuloste tiedosto="esimerkit/03-syote.syote"}
```

ohjelma tulostaa

```{.tuloste tiedosto="esimerkit/03-syote.odotettu"}
```

ja virhevirtaan `std::cerr` ilmoitukset riveistä 4, 5 ja 6. Tulos ja
virheilmoitukset kulkevat eri virroissa, joten tuloksen voi ohjata
tiedostoon tai toiselle ohjelmalle ilman, että virheet sekoittuvat
siihen. C++23:n `std::println` hyväksyy ensimmäisenä argumenttina virran.

## Käytännössä

- **`auto`, kun tyyppi on ilmeinen.** Monet ohjeistot suosittavat
  `auto`a lähes aina (*almost always auto*), koska se estää vahingossa
  tapahtuvat muunnokset ja alustamattomat muuttujat. Tyyppi kirjoitetaan
  auki, kun se kertoo lukijalle jotain olennaista tai kun `auto` päättelisi
  väärän tyypin, kuten merkkijonoliteraalin `const char*`.
- **Aaltosulkualustus oletuksena, kaarisulkeet säiliön koolle.**
  `{}` estää kaventavat muunnokset. Säiliöillä `std::vector<int>(n, x)`
  kirjoitetaan kaarisulkein, koska aaltosulkeet valitsisivat
  alkioluettelon.
- **Pienin mahdollinen näkyvyysalue.** Muuttuja esitellään vasta, kun sille
  on arvo, ja `if`-alustus rajaa apumuuttujan ehtoon. Mitä lyhyempi
  elinaika, sitä vähemmän tilaa virheille.
- **`const` oletuksena.** Arvo, jota ei muuteta, merkitään `const`, ja
  käännösaikaiset vakiot `constexpr`. Makroja ei käytetä vakioihin.
- **`enum class` ja `switch` ilman `default`-haaraa.** Kun jokainen
  luettelon arvo käsitellään erikseen, `-Wall` varoittaa, jos luetteloon
  lisätään arvo, jota jokin `switch` ei käsittele.
- **Syöte luetaan riveittäin ja validoidaan kokonaan.** Jokainen kenttä
  tarkistetaan, virheestä kerrotaan rivinumero, ja virheet kirjoitetaan
  `std::cerr`-virtaan. Ohjelma, joka hyväksyy vain osan rivistä, piilottaa
  virheitä.
- **`std::print` ja `std::format` tulostukseen.** Ne ovat tyyppiturvallisia
  toisin kuin `printf`, ja luettavampia kuin `iostream`-manipulaattorit.
  Jos `iostream`ia käytetään, rivinvaihto kirjoitetaan `'\n'` eikä
  `std::endl`, joka tyhjentää puskurin joka rivillä ja hidastaa suuria
  tulosteita.

## Itsearviointi

- Osaat kertoa, milloin `auto` päättelee eri tyypin kuin odotat.
- Osaat selittää kaventavan muunnoksen ja sen, miksi aaltosulkeet estävät
  sen.
- Osaat purkaa parin tai rakenteen rakenteisella sidonnalla ja käyttää
  `if`-alustusta.
- Osaat lukea ja jäsentää rivimuotoista syötettä niin, että jokainen
  virheellinen rivi havaitaan ja siitä kerrotaan.
