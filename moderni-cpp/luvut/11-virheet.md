# Virheenkäsittely

C++:ssa on kaksi pääasiallista tapaa käsitellä virheitä: poikkeukset ja
virheen palauttaminen arvona. C++23:n `std::expected` teki
jälkimmäisestä huomattavasti käytännöllisemmän.

## Poikkeukset

Poikkeus sopii tilanteisiin, joissa funktio ei pysty täyttämään
tehtäväänsä eikä välitön kutsuja todennäköisesti osaa korjata tilannetta.
Poikkeusta ei voi vahingossa jättää huomiotta, ja RAII huolehtii siitä,
että resurssit vapautetaan matkalla `catch`-lohkoon.

Omat poikkeusluokat kannattaa periä standardikirjaston luokista, kuten
`std::runtime_error`. Esittely `using std::runtime_error::runtime_error`
perii kantaluokan muodostimet, joten niitä ei tarvitse kirjoittaa
uudelleen.

```{.cpp tiedosto="esimerkit/11-poikkeukset.cpp" osa="tyyppi"}
```

Poikkeus siepataan aina `const`-viittauksena. Arvona sieppaaminen
kopioisi poikkeuksen ja voisi leikata siitä johdetun luokan osan pois.
`catch`-lohkot käydään läpi järjestyksessä, joten tarkimmat tyypit on
lueteltava ensin:

```{.cpp tiedosto="esimerkit/11-poikkeukset.cpp" osa="kaytto"}
```

Standardikirjasto käyttää poikkeuksia esimerkiksi rajatarkistuksissa.
Säiliön metodi `at` tarkistaa indeksin ja heittää `std::out_of_range`,
kun taas `operator[]` ei tarkista mitään:

```{.cpp tiedosto="esimerkit/11-poikkeukset.cpp" osa="vahva"}
```

```{.tuloste tiedosto="esimerkit/11-poikkeukset.odotettu"}
```

### `noexcept`

Funktio, joka ei voi heittää poikkeusta, merkitään `noexcept`.
Merkintä on lupaus: jos `noexcept`-funktiosta kuitenkin karkaa poikkeus,
ohjelma lopetetaan kutsumalla `std::terminate`. Merkinnästä on hyötyä
erityisesti siirtomuodostimille ja `swap`-funktioille, kuten luvussa
[Siirtosemantiikka](#siirtosemantiikka) nähtiin. Hajottimet ovat
oletuksena `noexcept`.

## `std::expected`

Kaikki virheet eivät ole poikkeuksellisia. Käyttäjän syötteen
jäsentäminen epäonnistuu usein, ja kutsuja haluaa käsitellä virheen
heti. Tällöin virhe kannattaa palauttaa arvona.

`std::expected<T, E>` (C++23) sisältää joko onnistuneen tuloksen tyyppiä
`T` tai virheen tyyppiä `E`. Se muistuttaa `std::optional`-tyyppiä,
mutta kertoo myös, miksi tulosta ei saatu. Virhe palautetaan
käärimällä se `std::unexpected`-olioon.

```{.cpp tiedosto="esimerkit/11-expected.cpp" osa="tyypit"}
```

```{.cpp tiedosto="esimerkit/11-expected.cpp" osa="jasenna"}
```

Kuten `optional`, myös `expected` muuntuu totuusarvoksi ja sen arvoon
päästään operaattorilla `*`. Virhe luetaan metodilla `error`. Vaiheet
ketjutetaan `and_then`-metodilla, joka kutsuu seuraavaa vaihetta vain,
jos edellinen onnistui:

```{.cpp tiedosto="esimerkit/11-expected.cpp" osa="kaytto"}
```

`transform` muuntaa onnistuneen arvon ja `value_or` antaa oletusarvon
virhetilanteessa. Lisäksi on `or_else`, joka käsittelee virheen, ja
`transform_error`, joka muuntaa virhetyypin toiseksi.

```{.cpp tiedosto="esimerkit/11-expected.cpp" osa="ketju"}
```

```{.tuloste tiedosto="esimerkit/11-expected.odotettu"}
```

## Kumpi valita?

Yleinen linjaus on seuraava:

- Käytä **poikkeuksia**, kun virhe on harvinainen ja se käsitellään
  kaukana virheen syntykohdasta, esimerkiksi muistin loppuminen,
  rikkoutunut tiedosto tai muodostimen epäonnistuminen. Muodostin ei voi
  palauttaa arvoa, joten poikkeus on sen ainoa luonteva tapa ilmaista
  virhe.
- Käytä **`std::expected`-tyyppiä**, kun virhe on odotettava osa
  normaalia toimintaa ja kutsuja käsittelee sen heti, esimerkiksi syötteen
  jäsentäminen tai validointi.
- Käytä **`std::optional`-tyyppiä**, kun puuttuva arvo ei ole virhe
  vaan tavallinen lopputulos, esimerkiksi haku, joka ei löytänyt mitään.
- Ohjelmointivirheet, kuten rikotut esiehdot, eivät ole ajonaikaisia
  virheitä, joista toivutaan. Niitä varten on `assert` ja testaus.

Projektissa kannattaa sopia yhtenäinen käytäntö ja noudattaa sitä
johdonmukaisesti.
