# Rakenteet, piirteet ja geneerisyys {.runko-omat-tyypit}

Rustissa ei ole luokkia eikä periytymistä. Data määritellään
rakenteina (`struct`) ja luettelotyyppeinä (`enum`), metodit
`impl`-lohkoissa ja yhteiset rajapinnat *piirteinä* (*trait*). Piirre
on lähinnä C++20:n konseptin ja abstraktin kantaluokan yhdistelmä: sitä
voi käyttää sekä käännösaikaisena rajana että ajonaikaisena
rajapintana. Aiemmat luvut ovat käyttäneet rakenteita ja piirteitä
valmiina; tässä luvussa ne määritellään itse.

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

```{.dot otsikko="Vektori `muodot` esimerkistä. Jokainen `Box<dyn Muoto>` on kaksi osoitinta: dataan ja tyypin virtuaalitauluun. Kutsu `m.ala()` hakee funktion osoitteen taulusta. Geneerisessä funktiossa `tulosta_ala` taulua ei ole, vaan kääntäjä tuottaa funktiosta oman kopion kummallekin tyypille."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=1.0;
  node [shape=plain, style=""];
  v [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" colspan="2" align="left"><i>muodot: Vec&lt;Box&lt;dyn Muoto&gt;&gt;</i></td></tr>
    <tr><td port="d0" bgcolor="#EEF1F6">data</td><td port="t0" bgcolor="#EEF1F6">vtable</td></tr>
    <tr><td port="d1" bgcolor="#EEF1F6">data</td><td port="t1" bgcolor="#EEF1F6">vtable</td></tr></table>>];
  y [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left"><i>Ympyra (keko)</i></td></tr>
    <tr><td bgcolor="#FFFFFF">sade: 2.0</td></tr></table>>];
  r [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left"><i>Suorakulmio (keko)</i></td></tr>
    <tr><td bgcolor="#FFFFFF">leveys: 4.0</td></tr><tr><td bgcolor="#FFFFFF">korkeus: 0.5</td></tr></table>>];
  ty [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left"><i>virtuaalitaulu: Muoto for Ympyra</i></td></tr>
    <tr><td bgcolor="#FFFFFF" align="left">drop, koko, tasaus</td></tr>
    <tr><td bgcolor="#FFFFFF" align="left">ala → Ympyra::ala</td></tr>
    <tr><td bgcolor="#FFFFFF" align="left">nimi → Ympyra::nimi</td></tr></table>>];
  tr [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left"><i>virtuaalitaulu: Muoto for Suorakulmio</i></td></tr>
    <tr><td bgcolor="#FFFFFF" align="left">drop, koko, tasaus</td></tr>
    <tr><td bgcolor="#FFFFFF" align="left">ala → Suorakulmio::ala</td></tr>
    <tr><td bgcolor="#FFFFFF" align="left">nimi → Muoto::nimi (oletus)</td></tr></table>>];
  y -> v:d0:w [dir=back]; v:t0:e -> ty;
  r -> v:d1:w [dir=back]; v:t1:e -> tr;
}
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
iteraattori päättyy.

Rivi `type Item = u64;` määrittelee piirteen *liitännäistyypin*
(*associated type*). Tyyppiparametrin valitsee kutsuja, ja sama tyyppi
voi toteuttaa geneerisen piirteen monta kertaa (`From<i32>` ja
`From<u8>`). Liitännäistyypin valitsee toteutus, ja niitä on yksi:
tyypillä on vain yksi `Iterator`-toteutus, joten alkion tyyppiä ei
tarvitse kertoa käyttöpaikassa. Rajoissa se kirjoitetaan muodossa
`Iterator<Item = u64>`.

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

## Makrot lyhyesti

Huutomerkkiin päättyvät nimet, kuten `println!` ja `vec!`, ovat
*makroja*: ne saavat syötteekseen koodin palasia ja tuottavat
käännösaikana uutta koodia. Makro voi tehdä sen, mihin funktio ei
pysty: ottaa vaihtelevan määrän argumentteja, tarkistaa muotoilujonon
tai tuottaa `impl`-lohkon. Makroja on kahta päälajia.

*Deklaratiivinen makro* kirjoitetaan `macro_rules!`-määrittelyllä, joka
on joukko hahmoja ja niitä vastaavia koodipohjia. Toisin kuin C:n
esikääntäjän makrot, se käsittelee jäsennettyjä lausekkeita eikä
tekstiä, ja sen sisäiset muuttujat eivät sekoitu kutsujan muuttujiin
(*hygienia*):

```{.rust tiedosto="esimerkit/07-makrot.rs" osa="makro"}
```

*Proseduraalinen makro* on erilliseen crateen kirjoitettu Rust-funktio,
jonka kääntäjä ajaa. Niitä käytetään kolmessa muodossa: `derive`-makro
tuottaa piirteen toteutuksen tyypin määrittelystä, attribuuttimakro
(`#[test]`, Tokion `#[tokio::main]`) muokkaa funktiota tai tyyppiä, ja
funktiomainen makro näyttää kutsulta. Useimmat kehittäjät käyttävät
proseduraalisia makroja päivittäin mutta kirjoittavat niitä harvoin.

```{.rust tiedosto="esimerkit/07-makrot.rs" osa="derive"}
```

```{.rust tiedosto="esimerkit/07-makrot.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-makrot.odotettu"}
```

Makro on viimeinen keino. Funktio tai geneerinen tyyppi on helpompi
lukea, tyyppitarkistetaan määrittelykohdassaan ja antaa paremmat
virheilmoitukset. Makron tuottaman koodin näkee komennolla
`cargo expand` (erillinen asennettava työkalu).

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
- Osaat kertoa, mitä `derive` ja muut makrot tekevät, lukea
  yksinkertaisen `macro_rules!`-määrittelyn ja perustella, milloin
  makro on funktiota parempi.
