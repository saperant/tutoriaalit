# Standardikirjaston sanastotyypit {.runko-kokoelmat}

*Sanastotyypeillä* (*vocabulary types*) tarkoitetaan yleiskäyttöisiä
tyyppejä, joilla eri kirjastot ja funktiot voivat ilmaista yleisiä
asioita yhteisellä tavalla: "arvo voi puuttua", "yksi monesta
vaihtoehdosta" tai "näkymä yhtenäiseen muistialueeseen".

## `std::string_view`

`std::string_view` on omistamaton näkymä merkkijonoon. Se sisältää vain
osoittimen ja pituuden, joten sen kopioiminen on halpaa eikä se varaa
muistia. Parametrina `std::string_view` korvaa usein tyypin
`const std::string&`, koska se hyväksyy sekä `std::string`-olion että
merkkijonoliteraalin ilman, että väliaikaista merkkijonoa tarvitsee
luoda.

```{.cpp tiedosto="esimerkit/08-merkkijonot.cpp" osa="funktio"}
```

```{.cpp tiedosto="esimerkit/08-merkkijonot.cpp" osa="kaytto"}
```

Metodi `substr` palauttaa uuden näkymän samaan muistiin eikä kopioi
merkkejä. Koska `string_view` ei omista dataa, se ei saa elää pidempään
kuin merkkijono, johon se osoittaa. Esimerkiksi väliaikaisesta
`std::string`-oliosta muodostettu näkymä on roikkuva heti lausekkeen
jälkeen. `string_view` sopii parametreiksi ja paikallisiin muuttujiin,
mutta luokan jäseneksi tai paluuarvoksi vain, kun datan elinikä on
varmasti riittävä, kuten yllä: paluuarvo osoittaa kutsujan antamaan
merkkijonoon.

Merkkijonotyypeille on tullut käteviä metodeja:

```{.cpp tiedosto="esimerkit/08-merkkijonot.cpp" osa="metodit"}
```

Literaalien jälkiliitteet `s` ja `sv` tuottavat suoraan `std::string`-
ja `std::string_view`-olion:

```{.cpp tiedosto="esimerkit/08-merkkijonot.cpp" osa="literaalit"}
```

```{.tuloste tiedosto="esimerkit/08-merkkijonot.odotettu"}
```

## `std::optional`

`std::optional<T>` sisältää joko arvon tyyppiä `T` tai ei mitään. Se on
selkeä tapa ilmaista, että funktio ei aina pysty palauttamaan tulosta,
ilman erikoisarvoja kuten `-1` tai tyhjiä osoittimia.

```{.cpp tiedosto="esimerkit/08-optional.cpp" osa="jasenna"}
```

`std::from_chars` (C++17) muuntaa tekstin luvuksi nopeasti, varaamatta
muistia ja heittämättä poikkeuksia. Tarkistus `loppu` varmistaa, että
koko merkkijono kelpasi.

`optional` muuntuu totuusarvoksi, ja sen arvoon päästään operaattoreilla
`*` ja `->`. Metodi `value_or` palauttaa oletusarvon, jos arvoa ei ole.

```{.cpp tiedosto="esimerkit/08-optional.cpp" osa="kaytto"}
```

C++23 lisäsi *monadiset* operaatiot, joilla käsittelyvaiheet voi ketjuttaa
ilman sisäkkäisiä `if`-lauseita. `and_then` kutsuu funktiota, joka
palauttaa uuden `optional`-arvon, ja `transform` funktiota, joka
palauttaa tavallisen arvon. Jos jokin vaihe tuottaa tyhjän arvon, loput
vaiheet ohitetaan.

```{.cpp tiedosto="esimerkit/08-optional.cpp" osa="ketju"}
```

```{.cpp tiedosto="esimerkit/08-optional.cpp" osa="monadinen"}
```

```{.tuloste tiedosto="esimerkit/08-optional.odotettu"}
```

## `std::variant`

`std::variant<A, B, C>` sisältää täsmälleen yhden arvon luetelluista
tyypeistä. Se on tyyppiturvallinen korvike C:n `union`-rakenteelle: se
tietää, mikä tyyppi on tallessa, ja kutsuu oikeaa hajotinta.

```{.cpp tiedosto="esimerkit/08-variant.cpp" osa="tyypit"}
```

Arvoa käsitellään yleensä funktiolla `std::visit`, joka kutsuu annettua
funktio-oliota varianttiin tallennetulla arvolla. Kätevä tapa koota
jokaiselle tyypille oma lambda on seuraava apurakenne, joka perii
kaikkien lambdojen kutsuoperaattorit:

```{.cpp tiedosto="esimerkit/08-variant.cpp" osa="kuormitus"}
```

```{.cpp tiedosto="esimerkit/08-variant.cpp" osa="ala"}
```

Jos jokin tyypeistä jää käsittelemättä, `std::visit`-kutsu ei käänny.
Kun varianttiin myöhemmin lisätään uusi tyyppi, kääntäjä osoittaa
kaikki kohdat, joita on päivitettävä.

```{.cpp tiedosto="esimerkit/08-variant.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-variant.odotettu"}
```

`variant` ja virtuaalifunktiot ratkaisevat saman ongelman eri suuntiin.
Variantilla on helppo lisätä uusia *operaatioita* (uusi `visit`-funktio),
mutta uuden tyypin lisääminen koskee kaikkia operaatioita.
Periytymisellä on päinvastoin. Variantti ei myöskään vaadi
dynaamista muistinvarausta.

## Säiliöt ja `std::span`

Standardikirjaston tärkein säiliö on `std::vector`, ja se on hyvä
oletusvalinta lähes aina. Kiinteän kokoiselle taulukolle on
`std::array`, joka korvaa C-tyyliset taulukot ja tietää kokonsa.
Hakurakenteista `std::map` pitää avaimet järjestyksessä ja
`std::unordered_map` on hajautustauluna yleensä nopeampi.

`std::span<T>` (C++20) on omistamaton näkymä yhtenäiseen alkiojonoon,
samaan tapaan kuin `string_view` merkkijonoille. Funktio, joka ottaa
`span`-parametrin, hyväksyy vektorin, `std::array`-taulukon ja C-taulukon
sellaisenaan:

```{.cpp tiedosto="esimerkit/08-sailiot.cpp" osa="span"}
```

```{.cpp tiedosto="esimerkit/08-sailiot.cpp" osa="span-kaytto"}
```

Hajautustaulun läpikäyntijärjestys ei ole määritelty, joten tulokset
kopioidaan tulostusta varten järjestettyyn `std::map`-rakenteeseen:

```{.cpp tiedosto="esimerkit/08-sailiot.cpp" osa="sanat"}
```

Hakurakenteille on tullut useita käteviä lisäyksiä: `contains` (C++20)
tarkistaa avaimen olemassaolon, `try_emplace` (C++17) lisää alkion vain,
jos avainta ei vielä ole, ja `std::erase_if` (C++20) poistaa ehdon
täyttävät alkiot mistä tahansa standardisäiliöstä.

```{.cpp tiedosto="esimerkit/08-sailiot.cpp" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/08-sailiot.odotettu"}
```

## Käytännössä

- **`std::vector` ensin.** Peräkkäinen muisti hyödyntää välimuistia niin
  hyvin, että vektori on usein nopein myös hakuun ja lisäykseen, kun
  alkioita on kohtuullisesti. Muu säiliö valitaan, kun mittaus tai
  vaatimus, kuten vakaat osoitteet, sitä edellyttää.
- **`reserve`, kun koko tiedetään.** Se poistaa toistuvat
  uudelleenvaraukset ja kopiot.
- **Hakurakenteen `operator[]` lisää alkion.** `taulu[avain]` luo
  puuttuvan avaimen oletusarvolla. Pelkkään hakuun käytetään `find`-,
  `contains`- tai `at`-metodia.
- **`string_view` ja `span` parametreiksi, omistavat tyypit jäseniksi.**
  Näkymä on halpa ja yleiskäyttöinen parametri, mutta luokan jäseneksi
  tallennettu näkymä on altis roikkumaan.
- **`optional` puuttuvalle arvolle, `expected` virheelle.** Jos kutsujan
  pitää tietää, *miksi* arvoa ei saatu, `optional` ei riitä (luku
  [Virheenkäsittely](#virheenkäsittely)).
- **Suljettu joukko vaihtoehtoja `variant`illa, avoin periytymisellä.**
  Kun vaihtoehdot tunnetaan, `variant` ja `visit` ovat nopeita, eivät
  varaa muistia ja pakottavat käsittelemään jokaisen vaihtoehdon.
- **Hinnat.** `std::unordered_map` ja `std::map` varaavat muistia
  jokaiselle alkiolle erikseen. `std::vector<bool>` on erikoistettu
  bittivektoriksi, jonka alkioihin ei saa tavallista viittausta.

## Itsearviointi

- Osaat valita parametrin tyypiksi `std::string_view`n tai `std::span`in
  ja tiedät, milloin näkymä voi jäädä roikkumaan.
- Osaat käyttää `std::optional`ia, `std::variant`ia ja `std::visit`iä.
- Osaat valita säiliön ja perustella valinnan.
- Osaat hakea hakurakenteesta lisäämättä sinne vahingossa alkioita.
