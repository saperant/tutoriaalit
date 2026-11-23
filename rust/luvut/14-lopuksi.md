# Lopuksi {.runko-kaytannot .runko-lahteet}

## Mallit ja idiomit

Tutoriaalissa esitellyt mallit ovat Rust-kehittäjien yhteistä sanastoa.
Monet niistä ovat C:n ja C++:n malleja, jotka Rustissa kääntäjä
tarkistaa.

| Malli | Ongelma, jonka se ratkaisee | Luku |
|------------------------------|----------------------------------|------|
| `Option` ja `Result` paluuarvona | puuttuva arvo ja virhe ilman NULL-arvoa ja poikkeuksia | 2, 8 |
| Tilakone `enum`-tyyppinä | virheelliset tilat mahdottomiksi | 4 |
| *Typestate* | väärät siirtymät käännösvirheiksi | 4 |
| Lainaava parametri, omistava kenttä | joustavat ja kopioimattomat rajapinnat | 5 |
| RAII-vartija (`Drop`) | resurssin vapautus kaikilla poluilla | 5, 11 |
| `Option::take`, `mem::replace` | omistuksen siirto ulos rakenteesta | 5 |
| Iteraattoriketju | silmukat ilman indeksejä ja välitaulukoita | 6 |
| `entry`-rajapinta | haku ja lisäys yhdellä haulla | 6 |
| Newtype | yksiköt, tunnisteet ja vieraat piirteet | 7 |
| Rakentaja | monta valinnaista asetusta | 7 |
| Virhe-`enum` ja `From` | kirjaston virheet ja `?`-muunnos | 8 |
| Parse, don't validate | validointi kerran tyypitetyksi arvoksi | 8, 10 |
| `Weak`-takaisinviittaus | viitesyklien välttäminen | 9 |
| Areena ja indeksit | graafit ilman jaettua omistusta | 9 |
| Nollakopioinen jäsennin | näkymät syötteeseen elinaikaparametrilla | 9 |
| Kirjasto ja ohut pääohjelma | testattava logiikka | 10 |
| `scope`-säikeet ja yhdistäminen lopuksi | rinnakkaisuus ilman lukkoja | 11 |
| Lukko omistaa datan | lukon ottamista ei voi unohtaa | 11 |
| Turvallinen kääre `unsafe`-koodille | muistiturvallisuuden kapselointi | 12 |
| `-sys`-crate ja kääre-crate | C-kirjaston käyttö Rustista | 12 |

## Nyrkkisäännöt

1. Käännä Clippyn kanssa varoitukset virheinä ja muotoile `cargo fmt`
   -komennolla.
2. Mallinna data niin, ettei virheellistä tilaa voi esittää: `enum`,
   newtype ja yksityiset kentät.
3. Ota parametrit lainana (`&str`, `&[T]`), ellei funktio säilytä arvoa.
4. Älä tyynnytä lainaustarkistinta `clone()`-, `Rc<RefCell>`- tai
   `unsafe`-ratkaisulla ennen kuin olet miettinyt omistusrakenteen.
5. Palauta virheet `Result`-arvona ja välitä ne `?`-operaattorilla.
   Paniikki on ohjelmointivirheitä varten.
6. Käytä iteraattoreita indeksisilmukoiden sijaan.
7. Luettele omien `enum`-tyyppien muunnelmat `match`-lausekkeessa
   jokerihaaran sijaan.
8. Johda `Debug` ja muut tavalliset piirteet julkisille tyypeille.
9. Käytä geneerisiä funktioita oletuksena ja `dyn`-piirreolioita, kun
   tarvitset eri tyyppejä samassa kokoelmassa.
10. Pidä `unsafe`-lohkot pieninä, perustele ne `SAFETY`-kommentilla ja
    kapseloi turvalliseen rajapintaan.
11. Mittaa suorituskyky `--release`-käännöksellä ennen optimointia.
12. Valitse ylivuotokäyttäytyminen tarkoituksella `checked_`-,
    `wrapping_`- tai `saturating_`-metodilla.

## Hinnat lyhyesti

| Halpaa | Maksullista |
|-----------------------------------|-----------------------------------|
| siirto (bittikopio), lainaus, `Copy` | `clone()` (usein syvä kopio) |
| iteraattoriketju, sulkeuma | `collect()` välivaiheena, `format!`, `to_string()` |
| geneerinen funktio (staattinen sidonta) | `dyn Trait` (virtuaalikutsu, ei upotusta) |
| `Option<&T>`, `Option<Box<T>>` (osoittimen kokoisia) | suuri `enum`-muunnelma kasvattaa kaikkia arvoja |
| `Result` onnistuneella polulla | paniikin purku |
| `Box<T>` olemassa olevana | `Box::new`, `Vec`-kasvatus (varaus) |
| `Rc::clone` | `Arc::clone` (atominen), `RefCell` (ajonaikainen tarkistus) |
| viipaleen iterointi | indeksointi `v[i]` (rajatarkistus) |
| `Mutex` ilman kilpailua | kilpailtu lukko, *false sharing* |

## Yleiset kirjastot

Standardikirjasto on tarkoituksella suppea, ja moni perustoiminto on
vakiintuneessa ulkoisessa kirjastossa. Kirjastoja voi selata osoitteissa
<https://crates.io> ja <https://lib.rs>.

| Tarve | Kirjasto |
|-------|----------|
| sarjallistus (JSON, TOML …) | `serde`, `serde_json`, `toml` |
| virheet | `thiserror` (kirjastot), `anyhow` (sovellukset) |
| komentorivi | `clap` |
| asynkroninen ajoympäristö | `tokio` |
| HTTP | `reqwest` (asiakas), `axum` (palvelin) |
| datan rinnakkaisuus | `rayon` |
| kanavat ja lukottomat rakenteet | `crossbeam` |
| lokitus ja jäljitys | `tracing`, `log` |
| testaus ja mittaus | `proptest`, `criterion`, `insta` |
| C-rajapinnat | `bindgen`, `cbindgen`, `cc` |
| satunnaisluvut | `rand` |
| säännölliset lausekkeet | `regex` |

## Lähteet ja jatkolukeminen

- **The Rust Programming Language** ("The Book"), Steve Klabnik ja
  Carol Nichols: <https://doc.rust-lang.org/book/>. Kielen virallinen
  johdatus. Lisenssi MIT/Apache-2.0.
- **Rust by Example**: <https://doc.rust-lang.org/rust-by-example/>.
  Esimerkkipohjainen läpikäynti kielen ominaisuuksista.
- **Standardikirjaston dokumentaatio**: <https://doc.rust-lang.org/std/>.
  Jokaisen tyypin ja piirteen dokumentaatio esimerkkeineen. Myös
  paikallisesti komennolla `rustup doc --std`.
- **The Rust Reference**: <https://doc.rust-lang.org/reference/>. Kielen
  tarkka kuvaus.
- **The Rustonomicon**: <https://doc.rust-lang.org/nomicon/>. `unsafe`-
  koodi, muistimalli ja C-rajapinnat.
- **Rust API Guidelines**:
  <https://rust-lang.github.io/api-guidelines/>. Kirjastorajapintojen
  suunnittelun ohjeet, kuten nimeäminen ja tavalliset piirteet.
- **Clippyn lintit**:
  <https://rust-lang.github.io/rust-clippy/master/>. Jokaisen lintin
  perustelu ja esimerkki.
- **Rust Design Patterns**: <https://rust-unofficial.github.io/patterns/>.
  Idiomit, mallit ja vastamallit.
- **Asynchronous Programming in Rust**:
  <https://rust-lang.github.io/async-book/> ja Tokion opas
  <https://tokio.rs/tokio/tutorial>.
- **The Cargo Book**: <https://doc.rust-lang.org/cargo/>. Cargo,
  profiilit, ominaisuudet ja työtilat.
- **Mara Bos: Rust Atomics and Locks** (O'Reilly 2023), vapaasti
  luettavissa: <https://marabos.nl/atomics/>. Atomiset operaatiot,
  muistimalli ja lukkojen toteutus.
- **Jon Gjengset: Rust for Rustaceans** (No Starch Press 2021).
  Jatkokurssi kokeneelle Rust-ohjelmoijalle.

Taitopuussa Rustia hyödyntävät muun muassa taidot *Rinnakkaisohjelmointi*,
*Suorituskyvyn analyysi ja optimointi*, *Verkko-ohjelmointi* ja
*Mikrokontrollerit ja bare-metal-ohjelmointi* (`no_std`-ympäristö).
