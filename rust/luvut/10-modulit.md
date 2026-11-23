# Modulit, paketit ja Cargo {.runko-modulit}

Rustin käännösyksikkö on *crate*: kirjasto tai ohjelma, joka käännetään
kerralla. Crate jaetaan *moduleihin*, jotka muodostavat nimiavaruuden
ja näkyvyysrajat. *Paketti* (*package*) on Cargon hallitsema
kokonaisuus, jossa on `Cargo.toml` ja yksi tai useampi crate.
Otsikkotiedostoja ei ole: kääntäjä lukee kaikki modulit ja tarkistaa
rajapinnat itse.

## Modulit ja näkyvyys

`mod nimi;` ottaa mukaan tiedoston `nimi.rs` tai `nimi/mod.rs`.
Kaikki on oletuksena yksityistä: modulin ulkopuolelle näkyy vain se,
mikä on merkitty `pub`. Rakenteen kentät ovat yksityisiä, vaikka
rakenne olisi julkinen.

| Merkintä | Näkyy |
|----------|-------|
| (ei mitään) | samassa modulissa ja sen alimoduleissa |
| `pub(super)` | yläpuolisessa modulissa |
| `pub(crate)` | koko cratessa, ei ulkoisille käyttäjille |
| `pub` | kaikkialla, minne modulikin näkyy |

Yksityiset kentät ovat Rustin kapselointikeino. Kun kentät ovat
yksityisiä, arvon voi luoda vain modulin omilla funktioilla, ja ne voivat
taata invariantin:

```{.rust tiedosto="esimerkit/10-nakyvyys.ei-kaanny.rs"}
```

```
error[E0451]: field `tunnit` of struct `aika::Kellonaika` is private
```

## Esimerkki: modulijako

Varastokirjanpito on jaettu kolmeen tiedostoon. Juuri (`main.rs`)
esittelee modulit ja tuo niistä tarvittavat nimet `use`-lauseilla:

```{.rust tiedosto="esimerkit/10-varasto/main.rs" osa="juuri"}
```

Modulissa `varasto` on validoitu tuotekoodi. Koska kenttä on
yksityinen, jokainen `Tuotekoodi`-arvo on kelvollinen, eikä muu koodi
tarkista sitä uudelleen:

```{.rust tiedosto="esimerkit/10-varasto/varasto.rs" osa="tuotekoodi"}
```

Varasto pitää saldot ei-negatiivisina, koska ainoa muuttava metodi
tarkistaa ne. `saldot` on `pub(crate)`: raporttimoduli saa käydä saldot
läpi, mutta jos crate olisi kirjasto, metodi ei näkyisi sen
käyttäjille:

```{.rust tiedosto="esimerkit/10-varasto/varasto.rs" osa="varasto"}
```

Raporttimoduli viittaa varastoon polulla `crate::varasto::Varasto`.
Polku voi alkaa `crate`-sanalla (craten juuri), `super`-sanalla
(yläpuolinen moduli) tai `self`-sanalla (nykyinen moduli):

```{.rust tiedosto="esimerkit/10-varasto/raportti.rs" osa="raportti"}
```

Pääohjelma lukee tapahtumat syötteestä. Virheet muunnetaan
merkkijonoiksi, koska ne vain tulostetaan:

```{.rust tiedosto="esimerkit/10-varasto/main.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-varasto.syote"}
```

```{.tuloste tiedosto="esimerkit/10-varasto.odotettu"}
```

## Cargo

Oikea projekti luodaan komennolla `cargo new varasto` (ohjelma) tai
`cargo new --lib varasto` (kirjasto). Cargo olettaa vakiorakenteen:

```
varasto/
├── Cargo.toml        paketin kuvaus ja riippuvuudet
├── Cargo.lock        lukitut versiot (ohjelmissa versionhallintaan)
├── src/
│   ├── main.rs       ohjelman juuri  (tai lib.rs kirjastolle)
│   ├── varasto.rs
│   └── bin/          lisäohjelmat
├── tests/            integraatiotestit (luku 13)
├── benches/          suorituskykytestit
└── examples/         esimerkkiohjelmat
```

`Cargo.toml` kuvaa paketin, sen riippuvuudet ja käännösprofiilit:

```
[package]
name = "varasto"
version = "0.3.1"
edition = "2021"
rust-version = "1.80"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
thiserror = "2"

[dev-dependencies]
proptest = "1"

[profile.release]
overflow-checks = true
lto = "thin"
```

Riippuvuudet haetaan crates.io-rekisteristä. Versiot noudattavat
semanttista versiointia: `"1.0"` tarkoittaa "1.0.0 tai uudempi, mutta
alle 2.0.0". `Cargo.lock` kirjaa tarkat versiot, joilla käännös
onnistui. *Ominaisuudet* (*features*) ovat käännösaikaisia valintoja,
jotka kytkevät osia kirjastosta päälle; niiden on oltava additiivisia.

Suuri projekti jaetaan *työtilaksi* (*workspace*), jossa useat paketit
jakavat `Cargo.lock`-tiedoston ja käännöshakemiston. Tyypillinen jako on
kirjastocrate, jossa on logiikka, ja ohut ohjelmacrate, joka käsittelee
komentoriviä ja tulostusta.

| Komento | Tehtävä |
|--------------------------------|--------------------------------------|
| `cargo build`, `cargo build --release` | käännös kehitys- tai julkaisuprofiililla |
| `cargo run -- argumentit` | käännös ja ajo |
| `cargo check` | tyyppitarkistus ilman koodin tuottamista (nopea) |
| `cargo add serde --features derive` | riippuvuuden lisäys |
| `cargo update` | lukittujen versioiden päivitys |
| `cargo tree` | riippuvuuspuu |
| `cargo doc --open` | dokumentaatio, myös riippuvuuksille |
| `cargo publish` | julkaisu crates.io:hon |

## Käytännössä

- **Kirjasto ja ohut pääohjelma.** Logiikka kirjoitetaan `lib.rs`-
  crateen, ja `main.rs` vain jäsentää argumentit ja kutsuu kirjastoa.
  Kirjastoa voi testata integraatiotesteillä ja käyttää muista
  ohjelmista.
- **Pienin näkyvyys.** Aloita yksityisestä ja avaa tarvittaessa.
  `pub(crate)` on oikea valinta sisäisille apufunktioille. Kaikki
  `pub`-nimet ovat kirjaston julkista rajapintaa, jonka muuttaminen
  rikkoo käyttäjät.
- **Validoiva tyyppi kapseloinnilla.** Yksityinen kenttä ja tarkistava
  muodostin takaavat, että arvo on aina kelvollinen (*parse, don't
  validate*). Tarkistus tehdään kerran, ja tyyppi dokumentoi sen.
- **Uudelleenvienti.** `pub use` kokoaa sisäisen rakenteen nimet
  julkiseen rajapintaan: käyttäjä kirjoittaa `varasto::Tuotekoodi` eikä
  `varasto::malli::koodi::Tuotekoodi`, ja sisäistä jakoa voi muuttaa.
- **Riippuvuudet harkiten.** Jokainen riippuvuus tuo mukanaan omat
  riippuvuutensa, käännösaikaa ja toimitusketjun riskin. `cargo tree`,
  `cargo audit` (tunnetut haavoittuvuudet) ja `cargo deny` (lisenssit,
  kielletyt paketit) kuuluvat CI:hin.
- **`Cargo.lock` ohjelmille versionhallintaan.** Ohjelman käännös on
  silloin toistettava. Kirjastoissa se on suositeltavaa myös, mutta
  käyttäjät ratkaisevat versiot omassa projektissaan.
- **Semanttinen versiointi on lupaus.** Julkisen kirjaston `pub`-
  rajapinnan muutos, uuden muunnelman lisäys julkiseen `enum`-tyyppiin
  (ilman `#[non_exhaustive]`) ja `pub`-kentän lisäys rakenteeseen
  rikkovat yhteensopivuuden ja vaativat pääversion noston.
  `cargo-semver-checks` tarkistaa tämän.

## Itsearviointi

- Osaat jakaa ohjelman moduleihin ja tiedostoihin ja viitata niiden
  nimiin `crate`-, `super`- ja `use`-poluilla.
- Osaat valita näkyvyyden `pub`, `pub(crate)` ja yksityinen välillä.
- Osaat taata tyypin invariantin yksityisillä kentillä ja validoivalla
  muodostimella.
- Osaat luoda Cargo-projektin, lisätä riippuvuuden ja selittää
  `Cargo.lock`-tiedoston ja semanttisen versioinnin merkityksen.
- Osaat jakaa projektin kirjastoon ja ohjelmaan sekä tarvittaessa
  työtilaksi.
