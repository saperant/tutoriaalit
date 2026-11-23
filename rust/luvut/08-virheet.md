# Virheenkäsittely {.runko-virheet}

Rust jakaa virheet kahteen luokkaan. *Palautettavat virheet*, kuten
puuttuva tiedosto tai virheellinen syöte, ilmaistaan
`Result<T, E>`-arvolla, ja kutsuja päättää, mitä niille tehdään.
*Palauttamattomat virheet* eli ohjelmointivirheet, kuten rikkoutunut
invariantti, aiheuttavat paniikin. Poikkeuksia ei ole.

## Result ja ?-operaattori

Standardikirjasto määrittelee `Result`-tyypin muodossa
`enum Result<T, E> { Ok(T), Err(E) }`. Se on tavallinen `enum`, joten
sen voi käsitellä `match`-lausekkeella. Useimmiten
käytetään kuitenkin operaattoria `?`: `lauseke?` purkaa `Ok`-arvon tai
palauttaa `Err`-arvon heti kutsujalle. Ennen palautusta virhe muunnetaan
kutsujan virhetyypiksi `From`-piirteellä. Operaattori vastaa C:n
`if (virhe) goto siivous;` -mallia, mutta siivouksen hoitaa `Drop`.

## Oma virhetyyppi

Kirjaston virhetyyppi on `enum`, jonka muunnelmat ovat kutsujalle
merkitykselliset virhetilanteet. Muunnelmiin talletetaan virheen
tiedot, kuten rivinumero, ja alkuperäinen syy:

```{.rust tiedosto="esimerkit/08-asetukset.rs" osa="virhetyyppi"}
```

Virhetyyppi toteuttaa kolme piirrettä:

- `Display` muotoilee käyttäjälle näytettävän viestin. Viesti kuvaa vain
  tämän tason virheen, ei syytä.
- `std::error::Error` tekee tyypistä virheen, jota muu koodi voi
  käsitellä yleisesti. Sen `source`-metodi palauttaa alkuperäisen syyn,
  jolloin syyketju säilyy.
- `From<io::Error>` antaa `?`-operaattorin muuntaa I/O-virheen
  automaattisesti.

Jäsennin palauttaa virheen jokaisesta ongelmasta. Jokainen `?` ja
`ok_or` on kohta, jossa funktio voi palata, ja se näkyy koodissa:

```{.rust tiedosto="esimerkit/08-asetukset.rs" osa="jasennys"}
```

Funktio `hae` on geneerinen kaikille kokonaislukutyypeille, joiden
jäsennysvirhe on `ParseIntError`. Paluutyyppi
`Result<Option<T>, AsetusVirhe>` erottaa kolme tapausta: arvo löytyi,
avain puuttuu (mikä ei ole virhe valinnaiselle avaimelle) ja arvo on
virheellinen.

Ylimmällä tasolla virhe raportoidaan syyketjuineen:

```{.rust tiedosto="esimerkit/08-asetukset.rs" osa="raportti"}
```

```{.rust tiedosto="esimerkit/08-asetukset.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-asetukset.syote"}
```

```{.tuloste tiedosto="esimerkit/08-asetukset.odotettu"}
```

## Option-yhdistimet

`Option` ja `Result` tarjoavat *yhdistimiä* (*combinators*), jotka
korvaavat sisäkkäiset tarkistukset. `?` toimii myös `Option`-arvoille
funktiossa, joka palauttaa `Option`-arvon:

```{.rust tiedosto="esimerkit/08-option.rs" osa="yhdistimet"}
```

| Metodi | Tekee |
|-----------------------------------|-----------------------------------|
| `map(f)` | muuntaa arvon, jos se on olemassa |
| `and_then(f)` | jatkaa funktiolla, joka voi itse epäonnistua |
| `filter(p)` | hylkää arvon, joka ei täytä ehtoa |
| `unwrap_or(x)`, `unwrap_or_else(f)`, `unwrap_or_default()` | oletusarvo |
| `ok_or(e)`, `ok_or_else(f)` | `Option` → `Result` |
| `ok()`, `err()` | `Result` → `Option` |
| `map_err(f)` | muuntaa virheen |
| `as_deref()` | `Option<String>` → `Option<&str>` |

`*_else`-muodot ottavat sulkeuman, joka lasketaan vain tarvittaessa.
`unwrap_or(format!(...))` muotoilisi merkkijonon joka kerta.

```{.rust tiedosto="esimerkit/08-option.rs" osa="muunnos"}
```

```{.rust tiedosto="esimerkit/08-option.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-option.odotettu"}
```

## Paniikki

Paniikki (`panic!`, `unwrap`, `expect`, `assert!`, rajojen ylitys)
purkaa säikeen pinon ja ajaa `Drop`-toteutukset. Pääsäikeen paniikki
lopettaa ohjelman paluuarvolla 101. Paniikki on oikea reaktio
tilanteeseen, jota ei pitäisi voida tapahtua ja jota kutsuja ei voi
korjata. `expect` kertoo, miksi arvon pitäisi olla olemassa:

```{.rust tiedosto="esimerkit/08-paniikki.kaatuu.rs" osa="paniikki"}
```

```{.tuloste tiedosto="esimerkit/08-paniikki.virhe"}
```

Upotettu asetus on ohjelman osa, joten virhe siinä on ohjelmointivirhe,
ja paniikki on perusteltu. Jos sama teksti luettaisiin tiedostosta,
funktion pitäisi palauttaa `Result`.

Paniikin voi pysäyttää funktiolla `std::panic::catch_unwind`, mutta sitä
käytetään vain rajoilla: säiepoolin työläinen, C-rajapinta (paniikki ei
saa ylittää `extern "C"` -funktion rajaa) tai testiajuri. Julkaisun voi
kääntää asetuksella `panic = "abort"`, jolloin paniikki lopettaa
prosessin heti ja binääri pienenee.

## Käytännössä

- **Kirjasto: oma virhe-`enum`.** Kirjaston virhetyyppi on `enum`, joka
  toteuttaa `Display`-, `Error`- ja `From`-piirteet. Kutsuja voi tutkia
  muunnelmaa ja reagoida siihen. `thiserror`-kirjasto tuottaa saman
  koodin makrolla (`#[derive(Error)]`, `#[error("...")]`, `#[from]`).
- **Sovellus: yksi yleinen virhetyyppi.** Sovelluksen ylätasolla
  virheitä ei yleensä tutkita vaan raportoidaan.
  `Box<dyn Error + Send + Sync>` tai `anyhow::Error` kelpaa mihin tahansa
  virheeseen, ja `anyhow`-kirjaston `context("...")` lisää ketjuun
  tiedon siitä, mitä oltiin tekemässä.
- **Viesti ei toista syytä.** `Display` kuvaa vain oman tasonsa, ja syy
  on `source`-ketjussa. Muuten sama teksti tulostuu ketjussa
  useaan kertaan.
- **`unwrap` vain, kun epäonnistuminen on ohjelmointivirhe.** Testeissä
  ja esimerkeissä `unwrap` on hyväksyttävä. Tuotantokoodissa suositaan
  `expect("miksi tämä ei voi epäonnistua")`-muotoa. Clippyn
  `unwrap_used`-lintin voi kytkeä päälle kirjastoissa.
- **Ei virheiden nielemistä.** `let _ = tiedosto.write_all(...)` hylkää
  virheen hiljaa. `Result` on merkitty `#[must_use]`-attribuutilla, joten
  kääntäjä varoittaa käyttämättömästä tuloksesta. Merkitse omat
  tärkeät paluuarvosi samoin.
- **Validoi kerran rajalla.** Syöte jäsennetään ja tarkistetaan
  ohjelman reunalla tyypitetyksi arvoksi (*parse, don't validate*).
  Sisemmät funktiot ottavat jo validoidun tyypin eivätkä tarkista
  uudelleen.
- **Hinta.** `Result` on tavallinen paluuarvo, eikä onnistunut polku
  maksa juuri mitään. Suuri virhetyyppi kasvattaa kuitenkin jokaista
  `Result`-arvoa; Clippyn `result_large_err` varoittaa, ja ratkaisu on
  laatikoida virheen tiedot. Paniikin purku on kallis kuten C++:n
  poikkeus, mutta se on harvinainen.

## Itsearviointi

- Osaat käyttää `?`-operaattoria ja kertoa, miten se muuntaa virheen
  `From`-piirteellä.
- Osaat määritellä kirjastolle virhe-`enum`-tyypin, joka toteuttaa
  `Display`-, `Error`- ja `From`-piirteet ja säilyttää syyketjun.
- Osaat käsitellä `Option`- ja `Result`-arvoja yhdistimillä ja muuntaa
  niitä toisikseen.
- Osaat päättää, milloin virhe palautetaan ja milloin paniikki on
  oikea reaktio.
- Osaat kertoa, milloin käyttäisit `thiserror`- tai `anyhow`-kirjastoa.
