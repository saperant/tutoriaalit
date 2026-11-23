# Johdanto {.runko-johdanto}

Rust on järjestelmäohjelmointikieli, jonka tavoite on C:n ja C++:n
suorituskyky ilman niiden muistivirheitä. Graydon Hoare aloitti kielen
henkilökohtaisena projektina vuonna 2006, Mozilla otti sen hoitoonsa
vuonna 2009, ja versio 1.0 julkaistiin vuonna 2015. Nykyään kieltä
kehittää avoin projekti, jota tukee Rust Foundation.

Rustin keskeinen ajatus on *omistajuus*: jokaisella arvolla on yksi
omistaja, ja kääntäjä tarkistaa käännösaikana, ettei viitteitä käytetä
arvon vapauttamisen jälkeen eikä samaa dataa muuteta kahdesta paikasta
yhtä aikaa. Tarkistuksen tekee kääntäjän osa nimeltä *lainaustarkistin*
(*borrow checker*). Sen ansiosta Rustissa ei ole roskienkeruuta eikä
käsin kutsuttavaa `free`-funktiota, ja silti vapautetun muistin käyttö,
roikkuvat osoittimet ja datakilpailut (*data race*) ovat turvallisessa
Rust-koodissa mahdottomia.

## Mihin Rust sopii ja mihin ei

Rust sopii tehtäviin, joissa tarvitaan C:n ja C++:n tehokkuutta ja
ennustettavuutta, mutta joissa muistivirheet olisivat kalliita:

- verkkopalvelut, välityspalvelimet ja tietokannat, joissa käsitellään
  vihamielistä syötettä (esim. Cloudflaren Pingora, AWS Firecracker)
- komentorivityökalut ja kehitystyökalut (ripgrep, uv, ruff)
- käyttöjärjestelmän osat ja ajurit: Linux-ydin hyväksyy Rust-ajureita
  versiosta 6.1 alkaen, ja Android ja Windows käyttävät Rustia
  uusissa komponenteissa
- sulautetut järjestelmät (`no_std`-ympäristö ilman käyttöjärjestelmää)
- WebAssembly-moduulit ja kirjastot, joita kutsutaan muista kielistä.

Rust ei ole paras valinta, kun

- tarvitaan nopea prototyyppi tai kertakäyttöinen skripti: Python tai
  komentotulkki on nopeampi kirjoittaa
- kohdealustalle ei ole LLVM-taustaa tai sertifioitua kääntäjää
  (osa turvallisuuskriittisistä aloista ja harvinaisista
  mikrokontrollereista)
- tiimi ei ehdi opetella kieltä: Rustin oppimiskynnys on korkeampi kuin
  useimpien kielten, ja ensimmäiset viikot kuluvat lainaustarkistimen
  kanssa
- ohjelma koostuu pääasiassa syklisistä, toisiinsa viittaavista
  olioista (graafit, GUI-oliopuut). Ne onnistuvat Rustissakin, mutta
  vaativat erityisrakenteita (luku 9).

## Versiot ja painokset

Rust julkaisee uuden vakaan version kuuden viikon välein. Versiot ovat
taaksepäin yhteensopivia. Kielen yhteensopimattomat muutokset tehdään
*painoksina* (*edition*): 2015, 2018, 2021 ja 2024. Painos valitaan
paketeittain, ja eri painoksia käyttävät paketit toimivat yhdessä.

Tämän tutoriaalin esimerkit on testattu Rust 1.80:llä ja painoksella
2021, jotka ovat Ubuntu 24.04:n pakettivarastossa. Uudemmat versiot
kääntävät esimerkit sellaisinaan. Kun teksti mainitsee uudemman version
ominaisuuden, se kerrotaan.

Kieltä ei ole standardoitu ISO-standardiksi. Viitetoteutus on `rustc`,
jonka taustana on LLVM. Kieliviite (*The Rust Reference*) ja
standardikirjaston dokumentaatio määrittelevät kielen. Ferrocene on
turvallisuuskriittisiin järjestelmiin sertifioitu `rustc`-jakelu, ja
GCC:hen kehitetään vaihtoehtoista `gccrs`-toteutusta.

## Työkalut

Rust asennetaan tavallisesti `rustup`-työkalulla, joka hallitsee
kääntäjäversioita ja kohdealustoja. Mukana tulevat

| Työkalu | Tehtävä |
|---------|---------|
| `rustc` | kääntäjä |
| `cargo` | projektinhallinta: käännös, riippuvuudet, testit, julkaisu |
| `clippy` | lint-työkalu, joka tuntee satoja idiomeja ja virhemalleja |
| `rustfmt` | koodin muotoilija |
| `rust-analyzer` | kielipalvelin editoreille |
| `rustdoc` | dokumentaation tuottaja |

Oikeassa projektissa käytetään aina Cargoa (luku 10). Tämän tutoriaalin
esimerkit ovat yksittäisiä tiedostoja, jotka käännetään suoraan
Clippyn kautta, varoitukset virheinä:

```
clippy-driver --edition 2021 -D warnings -D clippy::all \
    01-lokiyhteenveto.rs -o lokiyhteenveto
./lokiyhteenveto < 01-lokiyhteenveto.syote
```

Cargo-projektissa sama tehdään komennoilla `cargo clippy -- -D warnings`
ja `cargo run`. Kehityskontissa (`.devcontainer/rust`) työkalut ovat
valmiina.

## Ensimmäinen ohjelma

Ensimmäinen ohjelma lukee lokirivejä syötteestä ja laskee, montako
riviä kullakin tasolla on. Siinä näkyy jo useimmat Rustin perusasiat:

```{.rust tiedosto="esimerkit/01-lokiyhteenveto.rs"}
```

Syöte:

```{.tuloste tiedosto="esimerkit/01-lokiyhteenveto.syote"}
```

Tuloste:

```{.tuloste tiedosto="esimerkit/01-lokiyhteenveto.odotettu"}
```

- `use` tuo nimiä standardikirjastosta (`std`). `BTreeMap` on
  järjestetty hakemisto, jonka avaimet tulostuvat aakkosjärjestyksessä.
- `fn main() -> io::Result<()>` voi palauttaa virheen. Jos `main`
  palauttaa `Err`-arvon, ohjelma tulostaa virheen ja päättyy
  paluuarvoon 1.
- `let` esittelee muuttujan. Muuttujat ovat oletuksena muuttumattomia;
  `mut` sallii muutokset. Tyypit päätellään, ja ne kirjoitetaan
  näkyviin vain tarvittaessa.
- `lines()` palauttaa iteraattorin, jonka alkiot ovat tyyppiä
  `io::Result<String>`: jokainen rivin luku voi epäonnistua.
  Operaattori `?` palauttaa virheen kutsujalle tai purkaa onnistuneen
  arvon (luku 8).
- `match` käsittelee `split_once`-metodin palauttaman `Option`-arvon
  molemmat tapaukset. Kääntäjä ei hyväksy, jos jokin tapaus puuttuu.
- `entry(...).or_insert(0)` hakee avaimen paikan ja lisää sen
  tarvittaessa. `*` viittaa paikan arvoon, jota kasvatetaan.
- `println!` on makro (huutomerkki), joka tarkistaa muotoilujonon
  käännösaikana. `{taso:<6}` tulostaa muuttujan vasemmalle tasattuna
  kuuden merkin levyiseen kenttään.

Ohjelmassa ei varata eikä vapauteta muistia käsin, vaikka merkkijonot ja
hakemisto ovat keossa: arvot vapautuvat, kun niiden omistaja poistuu
näkyvyysalueelta.

## Tutoriaalin rakenne

Luku 2 on tarkoitettu kokeneelle C- tai C++-kehittäjälle, joka haluaa
nopean kuvan kielestä. Luvut 3 ja 4 käsittelevät tyypit, ohjausrakenteet
ja Rustin tärkeimmän rakenteen, `enum`-tyypin ja `match`-lausekkeen.
Luku 5 opettaa omistajuuden ja lainaamisen, joihin kaikki muu perustuu.
Luvuissa 6–9 käsitellään kokoelmat, piirteet, virheenkäsittely ja
älykkäät osoittimet, luvuissa 10–12 modulit, säikeet ja `unsafe`-koodi
C-rajapintoineen ja luvussa 13 työkalut. Luku 14 kokoaa idiomit ja
lähteet.

Taitopuussa Rustin esitieto on *C-kieli*. Tutoriaali vertaa Rustia
jatkuvasti C:hen ja C++:aan, koska Rustin säännöt on helpointa
ymmärtää niiden virheiden kautta, jotka säännöt estävät.
