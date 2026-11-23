# unsafe ja C-rajapinta

Turvallinen Rust ei voi ilmaista kaikkea: käyttöjärjestelmän ja
C-kirjastojen kutsut, laitteistorekisterit ja jotkin tietorakenteet
tarvitsevat toimintoja, joiden oikeellisuutta kääntäjä ei voi
tarkistaa. Ne kirjoitetaan `unsafe`-lohkoihin. `unsafe` on lupaus
kääntäjälle: ohjelmoija on tarkistanut ehdot, joita kääntäjä ei voi.

## Mitä unsafe sallii

`unsafe`-lohkossa saa tehdä viisi asiaa, jotka ovat muuten kiellettyjä:

1. dereferoida raa'an osoittimen (`*const T`, `*mut T`)
2. kutsua `unsafe fn` -funktion, myös vieraan kielen funktion
3. käyttää tai muuttaa `static mut` -muuttujaa
4. toteuttaa `unsafe trait` -piirteen (esim. `Send`, `Sync`)
5. lukea `union`-kentän.

Muut säännöt pysyvät voimassa: lainaustarkistin, tyyppitarkistus ja
rajatarkistukset toimivat myös `unsafe`-lohkossa. Raa'an osoittimen
luonti on turvallista; vain sen dereferointi vaatii `unsafe`-lohkon.
Ilman lohkoa rivi `*osoitin += 1` olisi käännösvirhe E0133
(*dereference of raw pointer is unsafe*):

```{.rust tiedosto="esimerkit/pikaopas.rs" osa="raaka"}
```

`unsafe`-koodin on noudatettava samoja sääntöjä kuin turvallisen
koodin: viite ei saa olla roikkuva eikä nolla, `&mut`-viitteitä ei saa
olla kahta samaan dataan, arvojen on oltava tyyppinsä kelvollisia
(esim. `bool` on 0 tai 1) eikä datakilpailuja saa olla. Rikkomus on
määrittelemätöntä käyttäytymistä samassa merkityksessä kuin C:ssä.

## Turvallinen rajapinta unsafe-toteutukselle

`unsafe` kapseloidaan funktioon, jonka rajapinta on turvallinen: funktio
tarkistaa kaikki ehdot, joista sen sisällä oleva `unsafe`-koodi riippuu.
Luvun 5 `split_at_mut` on tällainen funktio. Lainaustarkistin ei näe,
että kaksi muokkaavaa viipaletta eivät mene päällekkäin, mutta funktio
voi taata sen tarkistamalla jakokohdan:

```{.rust tiedosto="esimerkit/12-unsafe.rs" osa="jaa"}
```

Jokaisen `unsafe`-lohkon edellä on `SAFETY:`-kommentti, joka perustelee,
miksi ehdot täyttyvät. Clippyn `undocumented_unsafe_blocks`-lintti
vaatii sen. Kommentti on tarkastajalle tärkein rivi: koko ohjelman
muistiturvallisuus riippuu siitä, että perustelut pitävät.

## C-rajapinta

Rust kutsuu C-funktioita esittelemällä ne `extern "C"` -lohkossa. Rust
käyttää C:n kutsukäytäntöä ja linkittää funktiot kuten C. Kääntäjä ei
näe C:n otsikkotiedostoa, joten allekirjoitusten oikeellisuus on
ohjelmoijan vastuulla (Rust 2024 -painos vaatii siksi muodon
`unsafe extern "C"`):

```{.rust tiedosto="esimerkit/12-ffi.rs" osa="esittely"}
```

Tyypit vastaavat toisiaan seuraavasti:

| C | Rust |
|-----------------------------|-----------------------------------------|
| `int`, `long`, `char` | `c_int`, `c_long`, `c_char` (`std::ffi`) |
| `size_t`, `int32_t` | `usize`, `i32` |
| `const T *`, `T *` | `*const T`, `*mut T` |
| `void *` | `*mut c_void` |
| `const char *` (NUL-päätteinen) | `*const c_char`; omistettuna `CString`, lainattuna `&CStr` |
| funktio-osoitin | `extern "C" fn(...)`, nollattavana `Option<extern "C" fn(...)>` |
| `struct` | `#[repr(C)] struct` |

C-funktiot kääritään turvallisiin Rust-funktioihin. Kääre muuntaa tyypit,
tarkistaa ehdot ja muuntaa virheet `Result`-arvoiksi, joten muu ohjelma
ei näe `unsafe`-koodia lainkaan:

```{.rust tiedosto="esimerkit/12-ffi.rs" osa="kaareet"}
```

```{.rust tiedosto="esimerkit/12-ffi.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/12-ffi.odotettu"}
```

- `CString::new` lisää NUL-päätteen ja hylkää merkkijonon, jonka keskellä
  on NUL-tavu, koska C tulkitsisi sen merkkijonon loppumiseksi.
  `c"..."`-literaali (Rust 1.77) on valmiiksi `&CStr`.
- `strlen` laskee tavut, ei merkkejä: "Ääkköset" on UTF-8:na 11 tavua.
- Vaihtelevan parametrimäärän funktiot, kuten `snprintf`, esitellään
  `...`-merkinnällä. Rust ei tarkista muotoilujonoa, joten virhe siinä
  on määrittelemätöntä käyttäytymistä, kuten C:ssä.
- C:lle annettu takaisinkutsu on `extern "C" fn`. Paniikki ei saa
  ylittää C-rajaa; takaisinkutsu, joka voi paniikoida, kääritään
  `catch_unwind`-kutsuun.

Toiseen suuntaan Rust-funktio julkaistaan C:lle attribuutilla
`#[no_mangle]` ja kutsukäytännöllä `extern "C"`, ja crate käännetään
staattiseksi tai jaetuksi kirjastoksi (`crate-type = ["staticlib"]` tai
`"cdylib"`). `cbindgen` tuottaa tästä C-otsikkotiedoston, ja `bindgen`
tuottaa C-otsikoista Rust-esittelyt `build.rs`-skriptissä.

## Muistiasettelu

Rust saa järjestää rakenteen kentät uudelleen täytteen
minimoimiseksi, eikä sen asettelua ole määritelty. C:lle välitettävät
rakenteet merkitään `#[repr(C)]`, jolloin kenttien järjestys ja täyte
noudattavat alustan C-ABI:a:

```{.rust tiedosto="esimerkit/12-unsafe.rs" osa="asettelu"}
```

```{.rust tiedosto="esimerkit/12-unsafe.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/12-unsafe.odotettu"}
```

C-järjestyksessä `u32`-kenttä on tasattava neljään tavuun, joten
rakenteeseen tulee kuusi tavua täytettä. Rust järjestää kentät niin,
että täytettä tarvitaan vain kaksi tavua. Binäärirajapinnat ja
linkitys käsitellään tarkemmin taitopuun taidossa *Objektitiedostot,
linkitys ja ABI*.

## Käytännössä

- **Pieni `unsafe`, turvallinen rajapinta.** `unsafe`-lohkot pidetään
  lyhyinä ja kapseloidaan moduliin, jonka julkinen rajapinta on
  turvallinen. Tarkastus kohdistuu silloin muutamaan riviin.
  `#![forbid(unsafe_code)]` kieltää `unsafe`-koodin kokonaan craten
  sisällä, jossa sitä ei tarvita.
- **`SAFETY`-kommentti jokaiseen lohkoon** ja `# Safety`-osio jokaisen
  `unsafe fn` -funktion dokumentaatioon. Ensimmäinen perustelee, miksi
  ehdot täyttyvät, jälkimmäinen kertoo kutsujalle, mitkä ehdot hänen
  on täytettävä.
- **`-sys`-crate ja kääre-crate.** C-kirjaston raakaesittelyt tehdään
  `bindgen`illä omaan `foo-sys`-crateensa, ja turvallinen rajapinta
  `foo`-crateen. Malli on vakiintunut (esim. `openssl-sys` ja `openssl`).
- **Omistus rajan yli.** C:n varaama muisti vapautetaan C:n funktiolla
  ja Rustin varaama Rustilla. `Box::into_raw` antaa omistuksen C:lle ja
  `Box::from_raw` ottaa sen takaisin. C:n resurssi kääritään
  Rust-tyyppiin, jonka `Drop` kutsuu C:n vapautusfunktiota.
- **Miri ja sanitoijat.** `cargo +nightly miri test` tulkitsee ohjelman
  ja havaitsee määrittelemättömän käyttäytymisen, kuten lainasääntöjen
  rikkomukset raakojen osoittimien kautta. AddressSanitizer toimii
  Rustissa nightly-kääntäjällä (`-Zsanitizer=address`).
- **Ensin turvallinen vaihtoehto.** Monelle "tarvitsen unsafea"
  -tilanteelle on turvallinen standardikirjaston funktio:
  `split_at_mut`, `chunks_exact`, `copy_from_slice`, `from_le_bytes`.
  `unsafe` pelkän rajatarkistuksen poistamiseksi kannattaa vain, jos
  mittaus osoittaa sen tarpeelliseksi.

## Itsearviointi

- Osaat luetella, mitä `unsafe` sallii ja mitkä säännöt pysyvät
  voimassa.
- Osaat kirjoittaa turvallisen rajapinnan `unsafe`-toteutukselle ja
  perustella sen `SAFETY`-kommentilla.
- Osaat kutsua C-funktiota, välittää merkkijonoja `CString`- ja
  `CStr`-tyypeillä ja antaa C:lle takaisinkutsun.
- Osaat kertoa, milloin rakenne tarvitsee `#[repr(C)]`-merkinnän.
- Osaat kertoa, mihin `bindgen`, `cbindgen` ja Miri ovat tarkoitettuja.
