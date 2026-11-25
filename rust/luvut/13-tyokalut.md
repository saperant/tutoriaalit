# Työkalut, testaus ja laatu {.runko-tyokalut}

Rustin työkalut ovat yhtenäiset: Cargo kääntää, testaa, dokumentoi,
muotoilee ja tarkistaa koodin samoilla komennoilla jokaisessa
projektissa. Yleiset testauksen ja jatkuvan integraation käytännöt
käsitellään taitopuun taidossa *Käännösjärjestelmät, testaus ja CI*;
tässä luvussa keskitytään Rustin työkaluihin.

## Käännösprofiilit

| | `cargo build` (dev) | `cargo build --release` |
|---|---|---|
| Optimointi | `opt-level = 0` | `opt-level = 3` |
| Debug-tiedot | kyllä | ei |
| Ylivuototarkistukset | kyllä | ei |
| `debug_assert!` | kyllä | ei |
| Nopeus | usein 10–50 kertaa hitaampi | |

Suorituskykyä mitataan aina `--release`-käännöksellä. Profiileja voi
muokata `Cargo.toml`-tiedostossa: `lto = true` (koko ohjelman
optimointi), `codegen-units = 1` (parempi optimointi, hitaampi käännös),
`panic = "abort"` ja `debug = true` julkaisuversion profilointia varten.
Ympäristömuuttuja `RUSTFLAGS="-C target-cpu=native"` sallii
kääntämisen omalle prosessorille.

## Clippy ja rustfmt

`cargo fmt` muotoilee koodin yhteiseen tyyliin, eikä tyylistä tarvitse
keskustella katselmoinneissa. `cargo clippy` tarkistaa koodin noin 700
lintillä, jotka on jaettu ryhmiin: `correctness` (lähes varma virhe),
`suspicious`, `style`, `complexity`, `perf`, sekä oletuksena pois päältä
olevat `pedantic`, `restriction` ja `nursery`. Clippy tuntee idiomit
ja ehdottaa korjausta:

```{.rust tiedosto="esimerkit/13-clippy.ei-kaanny.rs" osa="clippy"}
```

```
error: the loop variable `i` is only used to index `luvut`
help: consider using an iterator: `for <item> in &luvut`
  = note: `-D clippy::needless-range-loop` implied by `-D clippy::all`
```

Tämän tutoriaalin esimerkit käännetään asetuksella
`-D warnings -D clippy::all`, eli jokainen varoitus on virhe. Lintit
valitaan projektikohtaisesti `Cargo.toml`-tiedoston `[lints]`-osiossa,
ja yksittäinen poikkeus merkitään perusteltuna attribuuttina, kuten
`#[allow(clippy::cast_possible_truncation)] // arvo < 256`.

## Testit

Rustin testikehys on kielessä. `#[test]`-attribuutilla merkitty funktio
on testi, joka onnistuu, jos se palaa, ja epäonnistuu, jos se
paniikoi. Yksikkötestit kirjoitetaan samaan tiedostoon modulin
`tests` sisään, joka käännetään vain testejä varten (`#[cfg(test)]`).
Ne näkevät modulin yksityiset funktiot.

Seuraava esimerkki on kirjoitettu niin, että se toimii sekä tavallisena
ohjelmana että testinä. Attribuutti `#[cfg_attr(test, test)]` tekee
funktiosta testin vain, kun ohjelma käännetään testeiksi (`rustc --test`
tai `cargo test`), ja tavallisessa käännöksessä `main` ajaa samat
funktiot. Tavallisessa projektissa attribuutti on suoraan `#[test]` ja
moduli merkitään `#[cfg(test)]`.

```{.rust tiedosto="esimerkit/13-testit.rs" osa="toteutus"}
```

```{.rust tiedosto="esimerkit/13-testit.rs" osa="testit"}
```

```{.rust tiedosto="esimerkit/13-testit.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/13-testit.odotettu"}
```

- *Taulukkotesti* käy läpi syöte–odotus-parit. `assert_eq!` tulostaa
  epäonnistuessaan molemmat arvot ja lisäviestin.
- *Ominaisuustesti* (*property-based test*) tarkistaa invariantin
  suurelle joukolle generoituja syötteitä. Tässä invariantti on
  idempotenttius: normalisoitu polku ei muutu uudessa normalisoinnissa.
  `proptest`-kirjasto generoi syötteet monipuolisemmin ja pienentää
  löydetyn vastaesimerkin.
- `#[should_panic(expected = "...")]` testaa, että funktio paniikoi, ja
  testi voi palauttaa `Result`-arvon, jolloin `?` toimii sen sisällä.

| Testityyppi | Sijainti | Näkee |
|-----------------|-------------------------------|----------------------|
| Yksikkötesti | `src/*.rs`, `#[cfg(test)] mod tests` | yksityiset nimet |
| Integraatiotesti | `tests/*.rs`, oma crate | vain julkisen rajapinnan |
| Dokumentaatiotesti | `///`-kommentin koodilohko | julkisen rajapinnan |

Esimerkkipaketti `13-kesto` on oikea Cargo-kirjasto, jossa ovat kaikki
kolme testityyppiä. Yksikkötestit ovat kirjaston lähdetiedoston lopussa
ja integraatiotesti omassa tiedostossaan hakemistossa `tests/`:

```{.rust tiedosto="esimerkit/13-kesto/src/lib.rs" osa="yksikkotestit"}
```

```{.rust tiedosto="esimerkit/13-kesto/tests/edestakaisin.rs" osa="integraatio"}
```

## Dokumentaatio ja doctestit

Rustin dokumentaatio kirjoitetaan lähdekoodiin. Kommentti `///`
dokumentoi sitä seuraavan nimen ja `//!` sen, jonka sisällä kommentti
on, tavallisesti koko craten tiedoston `lib.rs` alussa. Teksti on
Markdownia, ja `cargo doc` tuottaa siitä HTML-sivuston samalla
`rustdoc`-työkalulla, jolla standardikirjaston dokumentaatio on tehty.

```{.rust tiedosto="esimerkit/13-kesto/src/lib.rs" osa="crate"}
```

Dokumentaatiokommentin koodilohko on *dokumentaatiotesti* (*doctest*):
`cargo test` kääntää jokaisen lohkon omaksi ohjelmakseen, joka käyttää
cratea julkisen rajapinnan kautta, ja ajaa sen. Esimerkki ei siis voi
vanhentua huomaamatta. Risuaidalla alkava rivi käännetään mutta
jätetään pois sivulta; yllä se antaa lohkolle paluutyypin, jotta
`?` toimii.

Funktion dokumentaatio alkaa yhden virkkeen tiivistelmällä, joka näkyy
myös modulin sisällysluettelossa. Sen jälkeen tulevat vakiintuneet
osiot: `# Examples`, `# Errors` (milloin funktio palauttaa virheen),
`# Panics` (milloin se paniikoi) ja `unsafe`-funktioilla `# Safety`
(luku 12). Hakasulkeissa oleva nimi, kuten `` [`muotoile`] ``, on linkki
toiseen nimeen, ja rustdoc varoittaa, jos kohdetta ei ole:

```{.rust tiedosto="esimerkit/13-kesto/src/lib.rs" osa="jasenna"}
```

Koodilohkon attribuutti muuttaa testin tulkintaa: `should_panic`
vaatii paniikin, `no_run` kääntää mutta ei aja (esim. verkkoa käyttävä
esimerkki), `compile_fail` vaatii käännösvirheen ja `ignore` ohittaa
lohkon.

```{.rust tiedosto="esimerkit/13-kesto/src/lib.rs" osa="jaa"}
```

`cargo test` ajaa yksikkötestit, integraatiotestit ja
dokumentaatiotestit tässä järjestyksessä. Pelkät dokumentaatiotestit
ajetaan komennolla `cargo test --doc`:

```{.tuloste tiedosto="esimerkit/13-kesto/testit.odotettu"}
```

Lintti `missing_docs` varoittaa jokaisesta julkisesta nimestä, jolla ei
ole dokumentaatiota, myös `enum`-tyypin muunnelmista ja rakenteen
julkisista kentistä. Se kytketään päälle `Cargo.toml`-tiedostossa tai
craten alussa attribuutilla `#![warn(missing_docs)]`:

```{.toml tiedosto="esimerkit/13-kesto/Cargo.toml"}
```

Esimerkkien `Makefile` ajaa samat tarkistukset kuin CI ajaisi:
Clippyn ja rustdocin varoitukset ovat virheitä, ja lopuksi
varmistetaan, että dokumentoimaton julkinen funktio todella pysäyttää
tarkistuksen:

```{.makefile tiedosto="esimerkit/Makefile" osa="kesto"}
```

Dokumentaation suunnittelu lukijan mukaan, rajapintadokumentaation
julkaisu ja dokumentaation testaus yleisemmin käsitellään taidossa
*Tekninen dokumentaatio*.

## Virheenjäljitys ja profilointi

- `dbg!(lauseke)` tulostaa tiedoston, rivin, lausekkeen ja arvon
  stderr-virtaan ja palauttaa arvon. Se on `printf`-debuggauksen
  idiomaattinen muoto, ja Clippy (`dbg_macro`) löytää unohtuneet kutsut.
- `RUST_BACKTRACE=1` tulostaa paniikin yhteydessä kutsupinon.
- `rust-gdb` ja `rust-lldb` ovat GDB:n ja LLDB:n kääreitä, jotka
  näyttävät `Vec`-, `String`- ja `Option`-arvot luettavasti.
- `perf record` ja `cargo flamegraph` profiloivat kuten C-ohjelmia,
  kun julkaisuversioon lisätään debug-tiedot (`debug = true`).
- `cargo bench` ja `criterion`-kirjasto mittaavat suorituskykyä
  tilastollisesti. `std::hint::black_box` estää kääntäjää poistamasta
  mitattavaa koodia.
- Miri (`cargo +nightly miri test`) havaitsee määrittelemättömän
  käyttäytymisen `unsafe`-koodissa (luku 12).

Mittaamisen ja optimoinnin menetelmät käsitellään taitopuun taidossa
*Suorituskyvyn analyysi ja optimointi*.

## Käytännössä

- **CI:n vähimmäistarkistukset.** `cargo fmt --check`,
  `cargo clippy --all-targets -- -D warnings`, `cargo test` ja
  `cargo doc` (ympäristömuuttujalla `RUSTDOCFLAGS="-D warnings"`)
  jokaisessa muutoksessa. Lisäksi `cargo audit`
  riippuvuuksien haavoittuvuuksille ja tarvittaessa Miri.
- **Kirjaston julkinen rajapinta dokumentoidaan kokonaan.**
  `missing_docs` pitää huolen kattavuudesta, ja jokaisen julkisen
  funktion esimerkki on dokumentaatiotesti. Dokumentaatio kertoo sen,
  mitä allekirjoitus ei kerro: virheet, paniikit ja invariantit.
- **Pienin tuettu versio.** Kirjasto ilmoittaa `rust-version`-kentässä
  vanhimman kääntäjäversion, jolla se toimii, ja CI testaa sen.
- **Testit rajapinnan kautta.** Yksikkötestit testaavat yksittäisiä
  funktioita, integraatiotestit kirjaston julkista rajapintaa kuten
  käyttäjä sitä käyttää. Julkisen funktion dokumentaatiossa on
  ajettava esimerkki.
- **Invariantit ominaisuustesteinä.** Jäsentimille, tiivisteille ja
  muunnoksille kirjoitetaan edestakaisuustesti
  (`jasenna(muotoile(x)) == x`) ja idempotenttiustesti.
  Fuzzaus (`cargo fuzz`) löytää paniikit syötteistä, joita kukaan ei
  keksinyt.
- **Clippyn lisäryhmät harkiten.** `clippy::pedantic` on hyödyllinen
  kirjastoille, mutta siinä on vääriä hälytyksiä. Valitse lintit
  `[lints]`-osiossa ja perustele poikkeukset koodissa.
- **Käännösajan hallinta.** `cargo check` on nopein palaute.
  Käännösaikaa lyhentävät jakaminen useaan crateen, turhien
  ominaisuuksien poisto riippuvuuksista ja dynaamisen sidonnan käyttö
  harvoin kutsutussa koodissa. `cargo build --timings` näyttää, mikä
  hidastaa.

## Itsearviointi

- Osaat selittää kehitys- ja julkaisuprofiilin erot ja muokata
  profiilia `Cargo.toml`-tiedostossa.
- Osaat käyttää Clippyä ja rustfmt:tä ja kirjoittaa perustellun
  poikkeuksen lintille.
- Osaat kirjoittaa yksikkö-, integraatio- ja dokumentaatiotestejä sekä
  yksinkertaisen ominaisuustestin.
- Osaat dokumentoida craten ja sen julkiset nimet `//!`- ja
  `///`-kommenteilla vakiintuneine osioineen ja tarkistaa
  dokumentaation `cargo doc`- ja `cargo test --doc` -komennoilla.
- Osaat jäljittää virheen `dbg!`-makrolla, kutsupinolla ja
  debuggerilla sekä profiloida julkaisuversion.
- Osaat koota Rust-projektin CI-tarkistukset.
