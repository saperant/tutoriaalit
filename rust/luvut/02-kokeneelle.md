# Rust kokeneelle {.runko-kokeneelle}

Tämä luku on tarkoitettu kehittäjälle, joka osaa C:tä tai C++:aa ja
haluaa päästä Rustissa nopeasti tuottavaksi. Luku kokoaa Rustin
ajattelutavan, vastaavuudet tuttuihin kieliin, hinnat ja tärkeimmät
sudenkuopat.

## Ajattelutapa

- **Omistajuus on tyypissä.** C:ssä sovitaan kommentissa, kuka
  vapauttaa muistin. C++:ssa RAII ja `unique_ptr` ilmaisevat saman, mutta
  kääntäjä ei estä käyttämästä siirrettyä tai vapautettua oliota.
  Rustissa sijoitus ja arvoparametri *siirtävät* omistuksen, ja kääntäjä
  hylkää siirretyn arvon käytön (esimerkki alla).
- **Viite on lainaus, jolla on sääntö.** Samaan aikaan voi olla joko
  monta jaettua lainausta (`&T`) *tai* yksi muokkaava lainaus
  (`&mut T`), ei molempia. Tämä yksi sääntö estää iteraattorin
  mitätöitymisen, roikkuvat viitteet ja datakilpailut (luku 5).
- **Ei nollaosoitinta, ei poikkeuksia.** Puuttuva arvo on `Option<T>`
  ja epäonnistuminen `Result<T, E>`. Molemmat ovat tavallisia
  `enum`-tyyppejä, joiden käsittely on pakollista.
- **Turvallinen oletus, `unsafe` poikkeuksena.** Taulukon rajat
  tarkistetaan, kokonaislukujen ylivuoto havaitaan kehitysversiossa, ja
  määrittelemätön käyttäytyminen on mahdollista vain
  `unsafe`-lohkoissa (luku 12).
- **Lausekekieli.** `if`, `match` ja lohkot ovat lausekkeita, joilla on
  arvo. Funktion viimeinen lauseke ilman puolipistettä on sen
  paluuarvo.
- **Koostaminen periytymisen sijaan.** Luokkia ja periytymistä ei ole.
  Data on rakenteissa ja `enum`-tyypeissä, käyttäytyminen `impl`-
  lohkoissa ja yhteiset rajapinnat *piirteissä* (*trait*, luku 7).

Siirretyn arvon käyttö on käännösvirhe:

```{.rust tiedosto="esimerkit/02-siirto.ei-kaanny.rs"}
```

```
error[E0382]: borrow of moved value: `rivi`
```

Korjaus on lainata (`&rivi`), kloonata (`rivi.clone()`) tai käyttää
arvoa ennen siirtoa. Rustin siirto on aina bittikopio, eikä alkuperäistä
jätetä "kelvolliseen mutta määrittelemättömään" tilaan kuten C++:ssa.
Kääntäjä vain kieltää sen käytön. Tämän kirjan `.ei-kaanny`-esimerkeissä
virheellinen rivi on merkitty kommentilla `@virhe`; testeissä
varmistetaan, että tiedosto ei käänny sellaisenaan mutta kääntyy, kun
merkityt rivit poistetaan.

## Vastaavuudet

| Asia | C | C++ | Rust |
|---------------|---------------|--------------------|--------------------|
| Omistava osoitin | `malloc`/`free` | `std::unique_ptr<T>` | `Box<T>` |
| Jaettu omistus | viitelaskenta käsin | `std::shared_ptr<T>` | `Rc<T>`, säikeissä `Arc<T>` |
| Lukuviite | `const T *` | `const T &` | `&T` |
| Muokkaava viite | `T *` | `T &` | `&mut T` (yksinoikeus) |
| Viipale | osoitin + pituus | `std::span<T>` | `&[T]`, `&mut [T]` |
| Merkkijono | `char *` + `'\0'` | `std::string`, `string_view` | `String`, `&str` (UTF-8) |
| Dynaaminen taulukko | `realloc` | `std::vector<T>` | `Vec<T>` |
| Puuttuva arvo | `NULL` | `std::optional<T>` | `Option<T>` |
| Virhe | paluuarvo, `errno` | poikkeus, `std::expected` | `Result<T, E>` ja `?` |
| Merkitty unioni | `struct` + `union` | `std::variant` | `enum` ja `match` |
| Rajapinta | funktio-osoitintaulu | virtuaalifunktiot, konseptit | piirre: `dyn` tai geneerinen |
| Mallit | makrot | `template` | geneeriset tyypit ja makrot |
| Hajotin | `_tuhoa`-funktio | hajotin | `Drop`-piirre |
| Modulit | otsikkotiedostot | otsikot, modulit | `mod`, `use`, crate-paketit |
| Kääntäjä ja paketit | make, CMake | CMake, vcpkg, Conan | Cargo ja crates.io |

`Option` ja `Result` korvaavat C:n paluuarvokäytännöt. Funktio, joka voi
jättää arvon palauttamatta tai epäonnistua, ilmaisee sen tyypissään:

```{.rust tiedosto="esimerkit/02-vastaavuudet.rs" osa="option"}
```

```{.rust tiedosto="esimerkit/02-vastaavuudet.rs" osa="result"}
```

```{.rust tiedosto="esimerkit/02-vastaavuudet.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/02-vastaavuudet.odotettu"}
```

## Hinnat

Rustin abstraktiot ovat pääosin nollakustanteisia: iteraattoriketju,
`Option<&T>`, geneerinen funktio ja `Box<T>` kääntyvät samaksi
konekieleksi kuin käsin kirjoitettu C. Maksullisia ovat

- **Kekovaraukset.** `String`, `Vec`, `Box`, `format!` ja `to_string()`
  varaavat muistia. Kuumissa silmukoissa käytetään lainauksia (`&str`,
  `&[T]`) ja uudelleenkäytettäviä puskureita.
- **`clone()`.** Kloonaus on näkyvä, mutta usein syvä kopio. Clone
  lainaustarkistimen tyynnyttämiseksi on yleisin aloittelijan
  suorituskykyvirhe.
- **Rajatarkistukset.** `v[i]` tarkistaa indeksin. Iteraattorit
  ja viipaleet antavat kääntäjälle tiedon, jolla tarkistukset
  poistuvat.
- **Dynaaminen sidonta.** `dyn Trait` kutsuu virtuaalitaulun kautta,
  eikä kääntäjä voi upottaa kutsua. Geneerinen koodi on nopeaa, mutta
  *monomorfisaatio* kasvattaa binääriä ja käännösaikaa.
- **Viitelaskenta.** `Rc` maksaa laskurin päivityksen, `Arc` atomisen
  päivityksen, `RefCell` ajonaikaisen lainatarkistuksen.
- **Käännösaika.** Rust kääntää hitaasti, erityisesti makrojen ja
  geneerisen koodin osalta. Kehitysversio on myös selvästi hitaampi
  kuin `--release`.

## Tärkeimmät sudenkuopat

1. **Kehitys- ja julkaisuversio käyttäytyvät eri tavoin.**
   Kokonaislukujen ylivuoto aiheuttaa kehitysversiossa paniikin, mutta
   julkaisuversiossa luku kiertää hiljaa. Käytä tarkoituksella
   `checked_*`-, `wrapping_*`- tai `saturating_*`-metodeja (luku 3).
2. **Paniikki ei ole poikkeus.** `unwrap()`, `expect()`, ylivuoto ja
   indeksi rajojen ulkopuolella kaatavat säikeen. Paniikki on
   ohjelmointivirhe, ei virheenkäsittelyn keino (luku 8).
3. **`String` ei ole merkkitaulukko.** Merkkijonot ovat UTF-8:aa, joten
   `s[0]` ei käänny ja `len()` on tavuja eikä merkkejä (luku 6).
4. **Lainaustarkistimen kanssa ei kannata taistella.** Jos rakenne ei
   käänny, se on usein merkki siitä, että omistus on epäselvä. Ratkaisu
   on yleensä selkeämpi omistusrakenne, ei `clone()`, `Rc<RefCell<T>>`
   tai `unsafe` (luvut 5 ja 9).
5. **Syklit vuotavat.** `Rc`-sykli ei vapaudu koskaan. Muistivuoto on
   Rustissa turvallista mutta silti virhe; sykli katkaistaan `Weak`-
   viitteellä (luku 9).
6. **`unsafe` ei kytke tarkistuksia pois.** Se sallii viisi lisätoimintoa,
   kuten raa'an osoittimen dereferoinnin. Lainaustarkistin toimii yhä,
   ja ohjelmoija vastaa siitä, ettei koodi riko Rustin sääntöjä (luku 12).

Rajatarkistus muuttaa C:n määrittelemättömän käyttäytymisen hallituksi
paniikiksi, jonka viesti kertoo paikan ja syyn:

```{.rust tiedosto="esimerkit/02-rajat.kaatuu.rs"}
```

```{.tuloste tiedosto="esimerkit/02-rajat.virhe"}
```

## Lukuohje

1. Lue jokaisen luvun lopusta ensin *Itsearviointi*. Jos osaat kaikki
   väitteet, siirry seuraavaan lukuun.
2. Luvut 4 (`enum` ja `match`), 5 (omistajuus) ja 8 (virheet) kannattaa
   lukea kokonaan, sillä niissä Rust eroaa C:stä ja C++:sta eniten.
3. Lue *Käytännössä*-osiot kaikista luvuista: niissä ovat Rust-
   kehittäjien mallit ja hintatieto.
4. Pikaopas (`rust-pikaopas.pdf`) kokoaa syntaksin, idiomit, hinnat ja
   työkalukomennot muutamalle sivulle.
