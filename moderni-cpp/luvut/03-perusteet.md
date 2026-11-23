# Kielen perusteet modernisti

Tässä luvussa käydään läpi pieniä mutta jokapäiväisiä parannuksia,
jotka tekevät koodista lyhyempää ja turvallisempaa.

## Tyyppipäättely: `auto`

Avainsana `auto` antaa kääntäjän päätellä muuttujan tyypin
alustuslausekkeesta. Tyyppi on edelleen staattinen ja kiinteä; se
vain jätetään kirjoittamatta.

```{.cpp tiedosto="esimerkit/02-auto.cpp" osa="paattely"}
```

Merkkijonoliteraali `"C++"` on tyypiltään merkkitaulukko, joka
muuttuu osoittimeksi `const char*`. Jos tarvitaan `std::string`, tyyppi
kannattaa kirjoittaa näkyviin.

`auto` pudottaa pois viittaukset ja `const`-määreen. Jos alkiota halutaan
muokata tai sen kopioimista välttää, viittaus on kirjoitettava itse:

```{.cpp tiedosto="esimerkit/02-auto.cpp" osa="viittaus"}
```

```{.tuloste tiedosto="esimerkit/02-auto.odotettu"}
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

```{.cpp tiedosto="esimerkit/02-alustus.cpp" osa="aaltosulut"}
```

Tyhjät aaltosulkeet *arvoalustavat* muuttujan: perustyypit saavat arvon
nolla. Tämä on hyvä oletus, sillä alustamattoman muuttujan lukeminen on
määrittelemätöntä käyttäytymistä.

Aaltosulkujen tärkein etu on, että ne kieltävät *kaventavat
muunnokset*, joissa tietoa voi kadota:

```{.cpp tiedosto="esimerkit/02-kaventaminen.ei-kaanny.cpp"}
```

Standardin mukaan aaltosulkeissa tapahtuva kaventaminen on virhe.
Clang antaa siitä käännösvirheen. GCC antaa muuttujan tapauksessa
oletuksena vain varoituksen, joka muuttuu virheeksi valitsimella
`-Werror` (kuten tämän tutoriaalin testeissä).

Yksi sudenkuoppa on syytä tuntea. Jos luokalla on
`std::initializer_list`-muodostin, kuten säiliöillä, aaltosulkeet
valitsevat sen:

```{.cpp tiedosto="esimerkit/02-alustus.cpp" osa="sudenkuoppa"}
```

### Jäsenten oletusarvot ja nimetyt alustimet

Rakenteen jäsenille voi antaa oletusarvot suoraan esittelyssä. C++20:n
*nimetyillä alustimilla* (*designated initializers*) voi asettaa vain
halutut jäsenet. Jäsenet on lueteltava esittelyjärjestyksessä.

```{.cpp tiedosto="esimerkit/02-alustus.cpp" osa="jasenet"}
```

```{.cpp tiedosto="esimerkit/02-alustus.cpp" osa="nimetyt"}
```

Jäsen, jota ei mainita, saa oletusarvonsa: `leveat.varit` on `true`.

## Rakenteiset sidonnat

C++17:n *rakenteinen sidonta* (*structured binding*) purkaa parin,
monikon, taulukon tai rakenteen jäsenet nimetyiksi muuttujiksi. Funktio
voi siten palauttaa useita arvoja ilman tulosparametreja:

```{.cpp tiedosto="esimerkit/02-rakenteet.cpp" osa="pari"}
```

```{.cpp tiedosto="esimerkit/02-rakenteet.cpp" osa="sidonnat"}
```

`Hinnasto` on tyyppialias, joka on määritelty `using`-esittelyllä. Se
korvaa vanhan `typedef`-syntaksin ja on luettavampi:

```{.cpp tiedosto="esimerkit/02-rakenteet.cpp" osa="using"}
```

Muotoilumäärite `{:<6}` tasaa arvon vasemmalle kuuden merkin levyiseen
kenttään ja `{:>5.2f}` oikealle viiden merkin kenttään kahdella
desimaalilla. Koska `std::map` pitää avaimet järjestyksessä, tuotteet
tulostuvat aakkosjärjestyksessä.

## Alustus `if`- ja `switch`-lauseissa

C++17:stä alkaen `if`- ja `switch`-lauseen ehtoon voi liittää
alustuksen. Muuttujan näkyvyys rajoittuu lauseeseen, mukaan lukien
`else`-haara:

```{.cpp tiedosto="esimerkit/02-rakenteet.cpp" osa="ehtoalustus"}
```

## Vahvasti tyypitetyt luettelot

Vanhat `enum`-luettelot muuttuvat huomaamatta kokonaisluvuiksi, ja
niiden nimet vuotavat ympäröivään näkyvyysalueeseen. `enum class`
korjaa molemmat ongelmat:

```{.cpp tiedosto="esimerkit/02-rakenteet.cpp" osa="enum"}
```

Molemmissa luetteloissa voi olla nimi `punainen`, koska nimiin viitataan
aina luettelon kautta: `Vari::punainen`. Arvoja ei voi vertailla
keskenään, eikä niitä voi sijoittaa kokonaislukuun ilman eksplisiittistä
muunnosta:

```{.cpp tiedosto="esimerkit/02-rakenteet.cpp" osa="vertailu"}
```

## `nullptr`

Tyhjä osoitin kirjoitetaan `nullptr`. Vanha `NULL` on kokonaisluku
nolla, mikä voi valita väärän funktion kuormitetuista vaihtoehdoista.
`nullptr` on omaa tyyppiään `std::nullptr_t`, joka muuntuu vain
osoittimiksi.

```{.cpp tiedosto="esimerkit/02-rakenteet.cpp" osa="nullptr"}
```

Koko ohjelma tulostaa:

```{.tuloste tiedosto="esimerkit/02-rakenteet.odotettu"}
```
