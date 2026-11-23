# Rakenteet, piirteet ja geneerisyys {.runko-omat-tyypit}

Rustissa ei ole luokkia eikä periytymistä. Data määritellään
rakenteina (`struct`) ja luettelotyyppeinä (`enum`), metodit
`impl`-lohkoissa ja yhteiset rajapinnat *piirteinä* (*trait*). Piirre
on lähinnä C++20:n konseptin ja abstraktin kantaluokan yhdistelmä: sitä
voi käyttää sekä käännösaikaisena rajana että ajonaikaisena
rajapintana.

## Rakenteet ja metodit

```{.rust tiedosto="esimerkit/07-rakenteet.rs" osa="tili"}
```

- Muodostimia ei ole. Konventio on liitännäisfunktio `new`, joka
  palauttaa valmiin arvon. Rakenteen voi luoda vain, jos kaikki kentät
  näkyvät (luku 10), joten `new` on myös kapseloinnin keino.
- Metodin ensimmäinen parametri kertoo, mitä metodi tekee oliolle:
  `&self` lukee, `&mut self` muokkaa ja `self` kuluttaa.
- `Self` on toteutettavan tyypin nimi.

### Uusi tyyppi

*Newtype*-mallissa olemassa oleva tyyppi kääritään yksikenttäiseen
rakenteeseen. Kääre ei maksa mitään ajon aikana, mutta kääntäjä erottaa
tyypit, joten metrejä ja sekunteja ei voi sekoittaa:

```{.rust tiedosto="esimerkit/07-rakenteet.rs" osa="newtype"}
```

```{.rust tiedosto="esimerkit/07-rakenteet.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-rakenteet.odotettu"}
```

Operaattorit kuormitetaan toteuttamalla `std::ops`-modulin piirteitä
(`Add`, `Mul`, `Index`, `Neg` …). Vertailut tulevat piirteistä
`PartialEq`, `Eq`, `PartialOrd` ja `Ord`, jotka voi yleensä johtaa
`derive`-attribuutilla.

## Piirteet

Piirre luettelee metodit, jotka tyypin on toteutettava. Metodilla voi
olla oletustoteutus:

```{.rust tiedosto="esimerkit/07-piirteet.rs" osa="piirre"}
```

Piirrettä käytetään kahdella tavalla. *Staattisessa sidonnassa*
funktio on geneerinen, ja kääntäjä tuottaa siitä oman version kullekin
tyypille (*monomorfisaatio*), kuten C++:n malleista:

```{.rust tiedosto="esimerkit/07-piirteet.rs" osa="staattinen"}
```

*Dynaamisessa sidonnassa* piirreolio `dyn Muoto` on osoitin dataan ja
virtuaalitauluun (*fat pointer*). Sitä käytetään aina osoittimen takana
(`&dyn`, `Box<dyn>`), koska sen kokoa ei tunneta käännösaikana:

```{.rust tiedosto="esimerkit/07-piirteet.rs" osa="dynaaminen"}
```

```{.rust tiedosto="esimerkit/07-piirteet.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-piirteet.odotettu"}
```

| | Geneerinen `<T: Piirre>` | Piirreolio `dyn Piirre` |
|---|---|---|
| Sidonta | käännösaikana | ajon aikana virtuaalitaulusta |
| Upotus (*inline*) | mahdollinen | ei yleensä |
| Koodin koko | kopio jokaiselle tyypille | yksi kopio |
| Eri tyypit samassa kokoelmassa | ei | kyllä |
| Rajoitukset | ei | piirteen oltava *dyn-yhteensopiva* |

Piirreoliona käytettävän piirteen metodit eivät saa olla geneerisiä
eivätkä palauttaa `Self`-tyyppiä, koska niitä ei voisi kutsua
virtuaalitaulun kautta.

Tärkeimmät standardipiirteet:

| Piirre | Merkitys |
|------------------------------------|----------------------------------|
| `Debug`, `Display` | tulostus `{:?}`- ja `{}`-muodossa |
| `Clone`, `Copy` | eksplisiittinen ja implisiittinen kopio |
| `PartialEq`, `Eq`, `PartialOrd`, `Ord`, `Hash` | vertailu, järjestys ja hajautus |
| `Default` | oletusarvo |
| `From`, `Into`, `TryFrom` | muunnokset |
| `Iterator`, `IntoIterator` | läpikäynti ja `for` |
| `Drop` | vapautus |
| `Deref`, `AsRef` | älykkäät osoittimet ja lainaavat muunnokset |
| `Send`, `Sync` | säieturvallisuus (luku 11) |

## Geneeriset tyypit

Geneerinen tyyppi parametrisoidaan tyypillä. `impl`-lohko voi
asettaa tyyppiparametrille rajoja, ja metodit ovat silloin käytettävissä
vain tyypeille, jotka rajat täyttävät:

```{.rust tiedosto="esimerkit/07-geneerinen.rs" osa="rengas"}
```

`impl Iterator<Item = &T>` paluutyyppinä tarkoittaa "jokin iteraattori",
jonka tarkan tyypin kääntäjä tietää mutta jota kutsujan ei tarvitse
kirjoittaa. Kääre ei maksa mitään; ketjutettujen sovittimien
oikea tyyppi olisi pitkä ja toteutukseen sidottu.

Rajat kirjoitetaan tyyppiparametrin perään (`<T: Display>`) tai
`where`-lauseeseen. Toisin kuin C++:n malleissa, geneerinen funktio
tarkistetaan määrittelykohdassaan: rungossa saa käyttää vain rajojen
lupaamia metodeja, ja virhe raportoidaan kutsukohdassa ymmärrettävänä
rajavirheenä.

```{.rust tiedosto="esimerkit/07-geneerinen.rs" osa="rajat"}
```

Oma iteraattori toteuttaa yhden metodin, `next`, ja saa kaikki
sovittimet ja kuluttajat oletustoteutuksina. `?` toimii myös
`Option`-arvolle: `checked_add` palauttaa `None` ylivuodossa, ja
iteraattori päättyy:

```{.rust tiedosto="esimerkit/07-geneerinen.rs" osa="iterator"}
```

```{.rust tiedosto="esimerkit/07-geneerinen.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-geneerinen.odotettu"}
```

## Rakentaja

Koska kuormitettuja funktioita ja oletusparametreja ei ole, olio,
jolla on monta valinnaista asetusta, luodaan *rakentajalla* (*builder*).
Pakolliset tiedot annetaan muodostimelle, valinnaiset ketjutettavilla
metodeilla, jotka ottavat ja palauttavat `self`-arvon:

```{.rust tiedosto="esimerkit/07-rakentaja.rs" osa="rakentaja"}
```

```{.rust tiedosto="esimerkit/07-rakentaja.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-rakentaja.odotettu"}
```

Yksinkertaisemmissa tapauksissa riittää `Default`-piirre ja
rakennepäivitys: `Asetukset { portti: 8080, ..Default::default() }`.

## Käytännössä

- **Johda tavalliset piirteet.** Julkisille tyypeille johdetaan
  `Debug` ja tarpeen mukaan `Clone`, `PartialEq`, `Eq`, `Hash` ja
  `Default` (*C-COMMON-TRAITS* Rustin API-ohjeissa). Käyttäjä ei voi
  lisätä niitä jälkikäteen vieraaseen tyyppiin.
- **Geneerinen oletuksena, `dyn` tarvittaessa.** Geneerinen koodi on
  nopeampaa. `dyn` valitaan, kun eri tyyppejä säilytetään samassa
  kokoelmassa, kun toteutus valitaan ajon aikana (liitännäiset) tai kun
  monomorfisaatio kasvattaa binääriä ja käännösaikaa liikaa.
- **`impl Trait` parametrissa ja paluuarvossa.** `fn f(x: impl
  AsRef<str>)` on lyhyt muoto geneeriselle parametrille. Paluuarvona se
  piilottaa iteraattorin ja sulkeuman tyypin ilman `Box`-varausta.
- **Newtype yksiköille ja tunnisteille.** `struct KayttajaId(u64)` estää
  sekoittamasta tunnisteita, ja validoiva muodostin takaa invariantin
  (luku 10). Newtype on myös tapa toteuttaa vieras piirre vieraalle
  tyypille (*orphan rule* kieltää sen suoraan).
- **Rakentaja tai `Default`.** Yli kolmen valinnaisen parametrin
  funktiot korvataan rakentajalla. Jos rakentaminen voi epäonnistua,
  `rakenna` palauttaa `Result`-arvon.
- **Piirre kuvaa kykyä, ei hierarkiaa.** Periytymishierarkian sijaan
  tehdään pieniä piirteitä ja koostetaan ne (`T: Read + Seek`).
  Yhteinen data jaetaan kenttänä, ei kantaluokkana.
- **`From`-toteutus muunnoksille.** Kun `From<A> for B` on toteutettu,
  `Into<B> for A` saadaan ilmaiseksi, ja `?` osaa muuntaa virheet
  (luku 8).

## Itsearviointi

- Osaat määritellä rakenteen, sen metodit ja `new`-muodostimen sekä
  valita `self`-, `&self`- ja `&mut self`-vastaanottajan.
- Osaat määritellä piirteen oletustoteutuksineen ja toteuttaa sen
  omalle tyypille.
- Osaat valita geneerisen funktion ja piirreolion välillä ja kertoa
  valinnan hinnan.
- Osaat kirjoittaa geneerisen tyypin, jonka metodeilla on piirrerajoja,
  ja oman iteraattorin.
- Osaat käyttää newtype- ja rakentajamallia.
