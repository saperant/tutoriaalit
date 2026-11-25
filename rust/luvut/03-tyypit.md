# Tyypit, lausekkeet ja syöte {.runko-tyypit}

Rust on staattisesti ja vahvasti tyypitetty kieli. Tyypit päätellään
yleensä funktion sisällä, mutta funktioiden allekirjoituksissa ne
kirjoitetaan aina näkyviin. Rust ei tee implisiittisiä tyyppimuunnoksia
lukutyyppien välillä, ei edes laajentavia.

## Perustyypit

| Tyyppi | Kuvaus | C-vastine |
|---------------------|--------------------------------|-----------------|
| `i8` … `i128`, `u8` … `u128` | kiinteän kokoiset kokonaisluvut | `int8_t` … `uint64_t` |
| `isize`, `usize` | osoittimen kokoiset; `usize` indekseille ja pituuksille | `ptrdiff_t`, `size_t` |
| `f32`, `f64` | IEEE 754 -liukuluvut | `float`, `double` |
| `bool` | `true` tai `false`, yksi tavu | `bool` |
| `char` | Unicode-skalaariarvo, neljä tavua | – (`char32_t`) |
| `(A, B)` | monikko | nimetön `struct` |
| `[T; N]` | kiinteän kokoinen taulukko | `T[N]` |
| `()` | yksikkötyyppi, "ei arvoa" | `void` |

Kokonaislukuliteraalin oletustyyppi on `i32` ja liukulukuliteraalin
`f64`. Numeroita voi ryhmitellä alaviivalla (`1_000_000`), ja tyypin voi
liittää literaaliin (`7_i64`, `2.5_f32`).

```{.rust tiedosto="esimerkit/03-tyypit.rs" osa="perustyypit"}
```

```{.tuloste tiedosto="esimerkit/03-tyypit.odotettu" rivit="1-2"}
```

Muuttuja on oletuksena muuttumaton. `let mut` sallii muutokset, ja
kääntäjä varoittaa turhasta `mut`-sanasta. Muuttumattomuus on
oletuksena siksi, että suurin osa muuttujista ei muutu, ja harvat
muuttuvat erottuvat silloin lukijalle.

## Muunnokset

Lukutyyppien väliset muunnokset kirjoitetaan aina näkyviin. Tämä
poistaa C:n yleisimmän virhelähteen, hiljaiset kavennukset ja
etumerkkimuunnokset:

```{.rust tiedosto="esimerkit/03-kavennus.ei-kaanny.rs"}
```

```
error[E0308]: mismatched types
    expected `i64`, found `i32`
```

Muunnoksia on kolmenlaisia:

```{.rust tiedosto="esimerkit/03-tyypit.rs" osa="muunnokset"}
```

```{.tuloste tiedosto="esimerkit/03-tyypit.odotettu" rivit="3-3"}
```

- `From`/`Into` on häviötön muunnos, joka onnistuu aina, esimerkiksi
  `i32` → `i64`. Jos tyyppiä myöhemmin muutetaan niin, ettei muunnos
  enää ole häviötön, koodi lakkaa kääntymästä.
- `TryFrom`/`TryInto` palauttaa `Result`-arvon, joka on käsiteltävä.
- `as` toimii kuten C:n tyyppimuunnos: katkaisee, pyöristää ja vaihtaa
  etumerkin hiljaa. Liukuluvusta kokonaisluvuksi `as` kyllästää
  (`300.0 as u8 == 255`, `NaN as i32 == 0`), toisin kuin C, jossa tulos
  on määrittelemätön.

## Ylivuoto

Kokonaislukujen ylivuoto ei ole Rustissa määrittelemätöntä
käyttäytymistä. Kehitysversiossa (`debug`) se aiheuttaa paniikin, ja
julkaisuversiossa (`--release`) arvo kiertää, ellei
`overflow-checks`-asetusta kytketä päälle:

```{.rust tiedosto="esimerkit/03-ylivuoto.kaatuu.rs"}
```

```{.tuloste tiedosto="esimerkit/03-ylivuoto.virhe"}
```

Kun ylivuoto on mahdollinen, toiminta valitaan metodilla:

```{.rust tiedosto="esimerkit/03-tyypit.rs" osa="ylivuoto"}
```

```{.tuloste tiedosto="esimerkit/03-tyypit.odotettu" rivit="4-7"}
```

## Lausekkeet ja varjostus

Lähes kaikki Rustissa on lauseke. Lohkon arvo on sen viimeinen lauseke
ilman puolipistettä, ja `if` ja `match` palauttavat arvon. Siksi
Rustissa ei ole C:n ehto-operaattoria `?:`.

Samassa näkyvyysalueessa voi esitellä uuden muuttujan vanhan nimellä.
Tätä *varjostusta* (*shadowing*) käytetään, kun arvo muunnetaan
vaiheittain eikä välivaiheita enää tarvita:

```{.rust tiedosto="esimerkit/03-tyypit.rs" osa="varjostus"}
```

```{.tuloste tiedosto="esimerkit/03-tyypit.odotettu" rivit="8-8"}
```

## Tulostus ja muotoilu

Muotoilumakrot `println!`, `print!`, `eprintln!`, `format!` ja
`write!` tarkistavat muotoilujonon käännösaikana. Muuttujan voi
kirjoittaa suoraan aaltosulkeisiin (`{nimi}`), ja kaksoispisteen jälkeen
tulevat leveys, tasaus, tarkkuus ja muoto:

```{.rust tiedosto="esimerkit/03-muotoilu.rs" osa="muotoilu"}
```

| Määre | Merkitys |
|-----------------------------|-----------------------------------------|
| `{:<10}` `{:>10}` `{:^10}` | tasaus kymmenen merkin kenttään |
| `{:08.3}` | nollilla täyttö, kolme desimaalia |
| `{:x}` `{:#x}` `{:b}` `{:e}` | heksa, `0x`-etuliite, binääri, eksponentti |
| `{:?}` `{:#?}` | `Debug`-muoto, monirivinen |
| `{:.*}` | tarkkuus argumenttina |

Omat tyypit käsitellään luvussa 7, mutta tulostus tarvitsee niistä
kolme käsitettä jo nyt. *Rakenne* (`struct`) kokoaa nimettyjä kenttiä
kuten C:ssä. *Piirre* (*trait*) on nimetty joukko metodeja, jotka tyyppi
voi toteuttaa; C:ssä lähin vastine on funktio-osoitintaulu ja C++:ssa
abstrakti kantaluokka. Lohko `impl Piirre for Tyyppi { ... }` kirjoittaa
piirteen metodit tyypille, ja metodin ensimmäinen parametri `&self` on
viite arvoon, jolle metodia kutsutaan. Attribuutti `#[derive(...)]`
pyytää kääntäjää tuottamaan toteutuksen itse.

Tyyppi tulostuu `{}`-muodossa, jos se toteuttaa `Display`-piirteen, ja
`{:?}`-muodossa, jos se toteuttaa `Debug`-piirteen. `Debug` johdetaan
yleensä automaattisesti attribuutilla `#[derive(Debug)]`:

```{.rust tiedosto="esimerkit/03-muotoilu.rs" osa="debug"}
```

`Display` kirjoitetaan käsin, koska se on käyttäjälle näkyvä muoto.
Hyvä toteutus kunnioittaa kutsujan antamia määreitä:

```{.rust tiedosto="esimerkit/03-muotoilu.rs" osa="display"}
```

```{.tuloste tiedosto="esimerkit/03-muotoilu.odotettu"}
```

`eprintln!` kirjoittaa virhevirtaan (stderr), joten sen tuloste ei näy
yllä. Tuloste ja diagnostiikka pidetään erillään samasta syystä kuin
C:ssä: ohjelman tulosteen voi ohjata putkeen ilman virheilmoituksia.

## Syötteen lukeminen

Standardisyöte luetaan rivi kerrallaan `BufRead::lines()`-metodilla.
Rivin jäsentäminen erotetaan omaksi funktiokseen, joka palauttaa
`Result`-arvon. Näin virheellinen rivi raportoidaan eikä ohjelma kaadu:

```{.rust tiedosto="esimerkit/03-syote.rs" osa="jasenna"}
```

`let ... else` (*let-else*) purkaa arvon hahmon mukaan tai poistuu
lohkosta. Tässä hahmo vaatii täsmälleen kaksi kenttää: kolmas
`osat.next()` on oltava `None`. Pääohjelma laskee keskiarvon kelvollisista
riveistä:

```{.rust tiedosto="esimerkit/03-syote.rs" osa="lue"}
```

```{.tuloste tiedosto="esimerkit/03-syote.syote"}
```

```{.tuloste tiedosto="esimerkit/03-syote.odotettu"}
```

`stdin().lock()` lukitsee syötteen kerran koko silmukan ajaksi.
Lukitsematon `stdin().read_line()` ottaa lukon jokaisella kutsulla.

## Tiedostot ja argumentit

Komentoriviargumentit saadaan iteraattorista `std::env::args_os()`.
Polut ovat tyyppiä `Path` (lainattu) ja `PathBuf` (omistava), koska
käyttöjärjestelmän tiedostonimi ei välttämättä ole kelvollista UTF-8:aa.
`std::env::args()` palauttaa `String`-arvoja ja aiheuttaa paniikin,
jos argumentti ei ole UTF-8:aa.

```{.rust tiedosto="esimerkit/03-tiedosto.rs" osa="argumentit"}
```

Tiedosto avataan funktiolla `File::open` tai luodaan funktiolla
`File::create`. Kumpikin palauttaa `io::Result`-arvon, ja `File`
sulkeutuu itsestään, kun arvo poistuu näkyvyysalueelta. `File` ei
puskuroi: jokainen luku ja kirjoitus on järjestelmäkutsu. Siksi tiedosto
kääritään lähes aina `BufReader`- tai `BufWriter`-tyyppiin:

```{.rust tiedosto="esimerkit/03-tiedosto.rs" osa="kirjoita"}
```

```{.rust tiedosto="esimerkit/03-tiedosto.rs" osa="lue"}
```

Pienen tiedoston voi lukea kerralla funktiolla `fs::read_to_string`
(tai `fs::read` tavuina) ja kirjoittaa funktiolla `fs::write`. Kun
ohjelma ajetaan argumentilla `mittaukset.txt`, se kirjoittaa tiedoston,
lukee sen kahdella tavalla ja poistaa sen:

```{.rust tiedosto="esimerkit/03-tiedosto.rs" osa="aja"}
```

```{.tuloste tiedosto="esimerkit/03-tiedosto.odotettu"}
```

Viimeinen rivi on `io::Error`-arvon `Display`-muoto. Virheen lajin saa
metodilla `kind()` (esim. `io::ErrorKind::NotFound`), jos ohjelman pitää
reagoida siihen. Oikean komentoriviohjelman valitsimet jäsennetään
yleensä `clap`-kirjastolla, joka tuottaa myös käyttöohjeen.

## Käytännössä

- **Oikea kokonaislukutyyppi.** Indeksit, pituudet ja koot ovat
  `usize`. Muut luvut valitaan arvoalueen mukaan; `i32` on hyvä oletus,
  `u64` tavumäärille ja aikaleimoille. Älä käytä etumerkitöntä tyyppiä
  vain siksi, ettei arvo voi olla negatiivinen, jos sitä vähennetään:
  kun `b > a`, `a - b` aiheuttaa kehitysversiossa paniikin ja kiertää
  julkaisuversiossa hiljaa valtavaksi luvuksi.
- **`From` ennen `as`-muunnosta.** `i64::from(x)` dokumentoi, että
  muunnos on häviötön, ja lakkaa kääntymästä, jos tyypit muuttuvat.
  Clippyn `cast_lossless`- ja `cast_possible_truncation`-lintit
  löytävät vaaralliset `as`-muunnokset.
- **Ylivuodon käsittely tarkoituksella.** Ulkoisesta syötteestä
  lasketut koot tarkistetaan `checked_*`-metodeilla. Tiivisteissä ja
  laskureissa, joissa kierto on tarkoitus, käytetään `wrapping_*`-
  metodeja tai `std::num::Wrapping`-tyyppiä. Turvallisuuskriittisessä
  koodissa julkaisuversion ylivuototarkistukset kytketään päälle
  (`overflow-checks = true` Cargo.toml-tiedostossa).
- **Varjostus vaiheittaiseen muunnokseen.** `let syote =
  syote.trim();` on idiomaattista. Varjostus samassa lohkossa eri
  merkityksellä on sen sijaan hämmentävää.
- **`Display` käyttäjälle, `Debug` kehittäjälle.** Johda `Debug`
  kaikille julkisille tyypeille. Kirjoita `Display` vain, kun tyypillä on
  yksi luonteva tekstimuoto.
- **Jäsennys erilliseen funktioon.** `fn jasenna(&str) -> Result<T, E>`
  on testattava ilman syötevirtaa, ja kutsuja päättää, mitä virheelle
  tehdään.
- **Puskuroitu tuloste.** `println!` lukitsee stdoutin joka kutsulla,
  ja stdout on rivipuskuroitu. Suuria tulostemääriä varten
  otetaan `io::stdout().lock()` ja kääritään se `BufWriter`-tyyppiin.
- **`flush` ennen sulkemista.** `BufWriter` tyhjentää puskurinsa myös
  vapautuessaan, mutta silloin kirjoitusvirhe katoaa. Kutsu
  `flush()` itse ja käsittele sen tulos.
- **`Path` poluille, ei `String`.** `Path::join`, `with_extension` ja
  `file_name` käsittelevät erottimet oikein kaikilla alustoilla.

## Itsearviointi

- Osaat valita kokonaislukutyypin ja perustella, miksi indeksit ovat
  `usize`-tyyppisiä.
- Osaat muuntaa lukutyyppejä `From`-, `TryFrom`- ja `as`-muunnoksilla ja
  kertoa, mitä kukin tekee arvoalueen ulkopuolella.
- Osaat kertoa, miten ylivuoto käyttäytyy kehitys- ja julkaisuversiossa,
  ja valita oikean `checked_`-, `wrapping_`- tai `saturating_`-metodin.
- Osaat toteuttaa `Display`-piirteen ja käyttää muotoilumääreitä.
- Osaat lukea ja jäsentää rivipohjaista syötettä niin, että virheelliset
  rivit raportoidaan.
- Osaat lukea komentoriviargumentit sekä lukea ja kirjoittaa tiedoston
  puskuroidusti niin, että I/O-virheet välittyvät kutsujalle.
