---
title: Rust
subtitle: Pikaopas kokeneelle kehittäjälle · Rust 1.80, painos 2021
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Uusi projekti | `cargo new nimi`, kirjasto `cargo new --lib nimi` |
| Käännös, ajo | `cargo build`, `cargo run -- argumentit` |
| Julkaisuversio | `cargo build --release` (aina mittauksiin) |
| Nopea tarkistus | `cargo check` |
| Lint | `cargo clippy --all-targets -- -D warnings` |
| Muotoilu | `cargo fmt`, CI:ssä `cargo fmt --check` |
| Testit | `cargo test`, `cargo test nimi -- --nocapture` |
| Dokumentaatio | `cargo doc --open`, `rustup doc --std` |
| Riippuvuudet | `cargo add serde --features derive`, `cargo tree` |
| Turvallisuus | `cargo audit`, `cargo deny check` |
| UB-tarkistus | `cargo +nightly miri test` |
| Debuggaus | `rust-gdb`, `RUST_BACKTRACE=1`, `dbg!(x)` |
| Profilointi | `perf record`, `cargo flamegraph`, `criterion` |

# Perussyntaksi

```{.rust tiedosto="esimerkit/pikaopas.rs" osa="tyypit"}
```

```{.rust tiedosto="esimerkit/pikaopas.rs" osa="perus"}
```

- Kokonaisluvut `i8`…`i128`, `u8`…`u128`, indeksit `usize`; `f64`,
  `bool`, `char` (4 tavua, Unicode).
- Ei implisiittisiä muunnoksia: `i64::from(x)` (häviötön),
  `u8::try_from(x)?` (tarkistettu), `x as u8` (katkaisee).
- Ylivuoto: paniikki debugissa, kierto releasessa.
  `checked_add`, `wrapping_add`, `saturating_add`.
- Lohko on lauseke; viimeinen lauseke ilman `;` on arvo.

# Omistajuus ja lainaus

| Kirjoitus | Merkitys | C/C++ |
|-----------|----------|-------|
| `fn f(x: String)` | ottaa omistuksen (siirto) | `unique_ptr` arvona |
| `fn f(x: &str)` | lainaa lukemiseen | `const char *`, `string_view` |
| `fn f(x: &mut Vec<T>)` | lainaa muokkaamiseen, yksinoikeus | `T &` |
| `fn f(x: &[T])` | viipale: osoitin + pituus | `std::span<const T>` |
| `x.clone()` | eksplisiittinen (syvä) kopio | kopiomuodostin |
| `#[derive(Clone, Copy)]` | sijoitus kopioi | triviaali tyyppi |

- Joko monta `&T` tai yksi `&mut T`. Laina ei elä omistajaa pidempään.
- `Drop` = hajotin; vapautus käänteisessä järjestyksessä.
- `Option::take()`, `mem::replace`, `mem::swap` siirtävät arvon ulos.

# Omat tyypit ja piirteet

```{.rust tiedosto="esimerkit/pikaopas.rs" osa="omat"}
```

- `impl<T: Piirre>` / `where`: staattinen sidonta (monomorfisaatio).
- `&dyn Piirre`, `Box<dyn Piirre>`: virtuaalitaulu, eri tyypit samaan
  kokoelmaan.
- `impl Iterator<Item = T>` paluutyyppinä piilottaa tyypin ilman varausta.
- Johda `Debug`, `Clone`, `PartialEq`, `Eq`, `Hash`, `Default`.

# Virheet ja ohjausrakenteet

```{.rust tiedosto="esimerkit/pikaopas.rs" osa="virheet"}
```

```{.rust tiedosto="esimerkit/pikaopas.rs" osa="ohjaus"}
```

- `?` palauttaa `Err`/`None` ja muuntaa virheen `From`-piirteellä.
- Kirjasto: oma virhe-`enum` + `Display` + `Error` + `From`
  (`thiserror`). Sovellus: `Box<dyn Error>` tai `anyhow`.
- `unwrap`/`expect` vain ohjelmointivirheille; paniikki ei ole poikkeus.
- `match` on kattava: ei `_ =>` omille `enum`-tyypeille.

# Kokoelmat ja iteraattorit

```{.rust tiedosto="esimerkit/pikaopas.rs" osa="kokoelmat"}
```

| Tarve | Tyyppi |
|-----------------|-----------------------------------------------------|
| oletus | `Vec<T>` |
| avain → arvo | `HashMap` (satunnainen järjestys), `BTreeMap` (järjestetty) |
| jono, pino | `VecDeque<T>`, `Vec<T>` |
| prioriteetti | `BinaryHeap<T>` |
| merkkijono | `String` omistaa, `&str` lainaa; UTF-8, `len()` tavuja |

- `iter()` → `&T`, `iter_mut()` → `&mut T`, `into_iter()` → `T`.
- `map filter enumerate zip take skip chain flat_map windows chunks`
  → `collect sum count fold any all find max_by_key`.
- `collect::<Result<Vec<_>, _>>()` pysähtyy ensimmäiseen virheeseen.

# Älykkäät osoittimet ja säikeet

```{.rust tiedosto="esimerkit/pikaopas.rs" osa="osoittimet"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

| Tyyppi | Käyttö |
|-------------------------|---------------------------------------------|
| `Box<T>` | keko, rekursiiviset tyypit, `dyn` |
| `Rc<T>` / `Weak<T>` | jaettu omistus yhdessä säikeessä, syklien katkaisu |
| `RefCell<T>` | muokkaus `&`-viitteen kautta, ajonaikainen tarkistus |
| `Arc<T>` | jaettu omistus säikeiden välillä |
| `Mutex<T>`, `RwLock<T>` | lukko omistaa datan |
| `AtomicUsize` … | lukoton laskuri (`Relaxed`, `Acquire`/`Release`) |
| `thread::scope` | säikeet, jotka lainaavat pinon dataa |
| `mpsc::channel` | viestit, omistus siirtyy |

# unsafe ja FFI

```{.rust tiedosto="esimerkit/pikaopas.rs" osa="raaka"}
```

- `extern "C" { fn strlen(s: *const c_char) -> usize; }`, kutsu
  `unsafe`-lohkossa; `CString`/`CStr`, `#[repr(C)]`.
- Jokaiseen lohkoon `// SAFETY:`-perustelu; kapseloi turvalliseen
  funktioon.

# Hinnat

| Halpaa | Maksullista |
|-------------------------------|---------------------------------------|
| siirto, lainaus, `Copy` | `clone()`, `to_string()`, `format!` |
| iteraattorit, sulkeumat | `collect()` välivaiheena |
| geneerinen funktio | `dyn` (ei upotusta), binäärin kasvu monomorfisaatiosta |
| `Option<&T>` (osoittimen kokoinen) | `Box::new`, `Vec`-kasvatus |
| `Rc::clone` | `Arc::clone` (atominen), kilpailtu `Mutex` |
| viipaleen läpikäynti | `v[i]` (rajatarkistus) |

# Sudenkuopat

- Debug ja release eroavat: ylivuoto, `debug_assert!`, nopeus 10–50×.
- `s[0]` ei käänny merkkijonolle; `&s[a..b]` paniikoi merkin keskellä.
- `RefCell`: kaksi lainaa samaan aikaan → paniikki ajon aikana.
- `Rc`-sykli vuotaa; takaisinviittaus `Weak`.
- `HashMap`-järjestys vaihtelee ajosta toiseen.
- Lukon vartija elää lohkon loppuun: lyhennä näkyvyysaluetta.
- `drop` kanavan lähettäjistä, muuten vastaanotto odottaa ikuisesti.
- Estävä kutsu async-tehtävässä pysäyttää suorittajan.
