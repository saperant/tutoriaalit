# Virheenkäsittely {.runko-virheet}

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

```{.cpp tiedosto="esimerkit/13-poikkeukset.cpp" osa="tyyppi"}
```

Poikkeus siepataan aina `const`-viittauksena. Arvona sieppaaminen
kopioisi poikkeuksen ja voisi leikata siitä johdetun luokan osan pois.
`catch`-lohkot käydään läpi järjestyksessä, joten tarkimmat tyypit on
lueteltava ensin:

```{.cpp tiedosto="esimerkit/13-poikkeukset.cpp" osa="kaytto"}
```

Standardikirjasto käyttää poikkeuksia esimerkiksi rajatarkistuksissa.
Säiliön metodi `at` tarkistaa indeksin ja heittää `std::out_of_range`,
kun taas `operator[]` ei tarkista mitään:

```{.cpp tiedosto="esimerkit/13-poikkeukset.cpp" osa="vahva"}
```

```{.tuloste tiedosto="esimerkit/13-poikkeukset.odotettu"}
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

```{.cpp tiedosto="esimerkit/13-expected.cpp" osa="tyypit"}
```

```{.cpp tiedosto="esimerkit/13-expected.cpp" osa="jasenna"}
```

Kuten `optional`, myös `expected` muuntuu totuusarvoksi ja sen arvoon
päästään operaattorilla `*`. Virhe luetaan metodilla `error`. Vaiheet
ketjutetaan `and_then`-metodilla, joka kutsuu seuraavaa vaihetta vain,
jos edellinen onnistui:

```{.cpp tiedosto="esimerkit/13-expected.cpp" osa="kaytto"}
```

`transform` muuntaa onnistuneen arvon ja `value_or` antaa oletusarvon
virhetilanteessa. Lisäksi on `or_else`, joka käsittelee virheen, ja
`transform_error`, joka muuntaa virhetyypin toiseksi.

```{.cpp tiedosto="esimerkit/13-expected.cpp" osa="ketju"}
```

```{.tuloste tiedosto="esimerkit/13-expected.odotettu"}
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

## Käytännössä

- **Heitä arvona, sieppaa `const`-viittauksena.** Omat poikkeukset
  periytyvät standardin luokista, jotta yläkerroksen
  `catch (const std::exception&)` sieppaa ne.
- **Poikkeusturvallisuuden tasot.** Funktion takuu dokumentoidaan:
  *perustakuu* (ei vuotoja, olio kelvollinen), *vahva takuu* (operaatio
  onnistuu kokonaan tai ei lainkaan) tai *ei heitä* (`noexcept`).
  Copy-and-swap antaa vahvan takuun, RAII perustakuun.
- **Poikkeus ei ole ohjausvuo.** Heittäminen on C++:ssa kallista (luku
  [C++ kokeneelle](#c-kokeneelle)). Pythonista tuttu tapa siepata
  esimerkiksi puuttuva avain ei ole C++:ssa idiomaattinen. Ensin
  tarkistetaan (`contains`, `find`) tai palautetaan `optional` tai
  `expected`.
- **Virheiden raja.** Poikkeukset siepataan harvoissa paikoissa:
  pääohjelmassa, säikeen tai tehtävän aloitusfunktiossa ja
  tapahtumasilmukassa, jossa virhe kirjataan ja ohjelma jatkaa tai
  lopettaa hallitusti. Säikeestä karkaava poikkeus kutsuu
  `std::terminate`a, mutta `std::async` välittää sen `future`n kautta.
- **Projektin linjaus.** Monissa ympäristöissä, kuten peleissä ja
  sulautetuissa järjestelmissä, poikkeukset on poistettu käytöstä
  (`-fno-exceptions`), ja virheet ilmaistaan `expected`-arvoina tai
  virhekoodeina. Linjaus sovitaan projektin alussa ja sitä noudatetaan
  johdonmukaisesti.
- **Esiehdot ovat eri asia kuin virheet.** Ohjelmointivirhe, kuten
  väärä indeksi, tarkistetaan `assert`illa. C++26:n sopimukset
  (*contracts*) tuovat esi- ja jälkiehdot kielen osaksi.

## Itsearviointi

- Osaat määritellä oman poikkeusluokan ja siepata poikkeukset oikeassa
  järjestyksessä.
- Osaat ketjuttaa `std::expected`-arvoja `and_then`- ja
  `transform`-metodeilla.
- Osaat valita poikkeuksen, `expected`in ja `optional`in välillä ja
  perustella valinnan hinnalla.
- Osaat kertoa, mitä perustakuu, vahva takuu ja `noexcept` lupaavat.
