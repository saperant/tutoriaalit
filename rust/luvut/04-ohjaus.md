# Ohjausrakenteet, enum ja match {.runko-ohjaus}

Rustin ohjausrakenteet ovat lausekkeita, ja niistä tärkein on `match`.
Yhdessä `enum`-tyypin kanssa se korvaa C:n merkityt unionit,
`switch`-lauseet, nollaosoittimet ja virhekoodit.

## Lausekkeet ja silmukat

`if` on lauseke, joten sen haarojen on oltava samaa tyyppiä:

```{.rust tiedosto="esimerkit/04-silmukat.rs" osa="lausekkeet"}
```

Silmukoita on kolme: `loop` (ikuinen), `while` ja `for`. `loop` voi
palauttaa arvon `break`-lauseella:

```{.rust tiedosto="esimerkit/04-silmukat.rs" osa="loop"}
```

Sisäkkäisistä silmukoista poistutaan *nimiöllä* (*label*), joka
korvaa C:n `goto`-lauseen ja lippumuuttujat:

```{.rust tiedosto="esimerkit/04-silmukat.rs" osa="nimetty"}
```

`for` käy läpi minkä tahansa iteraattorin. Indeksisilmukkaa
`for (i = 0; i < n; i++)` ei ole; lukuvälit kirjoitetaan `0..n` ja
`1..=10`. `while let` toistaa, niin kauan kuin hahmo täsmää:

```{.rust tiedosto="esimerkit/04-silmukat.rs" osa="whilelet"}
```

```{.tuloste tiedosto="esimerkit/04-silmukat.odotettu"}
```

## Funktiot

Funktion parametrien ja paluuarvon tyypit kirjoitetaan aina näkyviin.
Paluuarvo on funktion viimeinen lauseke, tai se palautetaan
`return`-lauseella aiemmin. Funktioita ei voi kuormittaa (*overload*),
eikä parametreilla ole oletusarvoja. Niiden tilalla käytetään eri
nimiä, `Option`-parametreja tai rakentajaa (luku 7). Funktio, joka ei
palaa koskaan, palauttaa tyypin `!` (esim. `std::process::exit`).

## enum: merkitty unioni

Rustin `enum` on *summatyyppi*: arvo on täsmälleen yksi muunnelmista,
ja kullakin muunnelmalla voi olla omaa dataa. C:ssä sama tehdään
`struct`-rakenteella, jossa on tunniste ja `union`, ja ohjelmoija vastaa
siitä, että tunniste ja data vastaavat toisiaan. Rustissa väärää
muunnelmaa ei voi lukea.

Tilakone on `enum`-tyypin tyypillinen käyttökohde. Yhteyden tila ja
tapahtumat ovat omat tyyppinsä, ja siirtymäfunktio käsittelee
tila–tapahtuma-parit yhdessä `match`-lausekkeessa:

```{.rust tiedosto="esimerkit/04-tilakone.rs" osa="tilat"}
```

- Muunnelmalla voi olla nimettyjä kenttiä (`Yhdistaa { yritykset }`),
  nimettömiä kenttiä (`Onnistui(u64)`) tai ei dataa (`Suljettu`).
- Hahmo voi purkaa dataa (`Tila::Auki { istunto }`), ohittaa sen
  (`{ .. }`, `_`) ja sisältää ehdon (`if yritykset < ...`).
- Haarat käydään läpi järjestyksessä. Viimeinen `(tila, _)` sitoo minkä
  tahansa jäljelle jääneen tilan muuttujaan ja palauttaa sen.
- `siirtyma` ottaa tilan arvona ja palauttaa uuden. Vanhaa tilaa ei voi
  käyttää vahingossa siirtymän jälkeen.

```{.rust tiedosto="esimerkit/04-tilakone.rs" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/04-tilakone.odotettu"}
```

## Kattavuus

`match` on *kattava* (*exhaustive*): kääntäjä hylkää lausekkeen, josta
puuttuu jokin muunnelma. Kun `enum`-tyyppiin lisätään muunnelma, kaikki
sitä käsittelevät `match`-lausekkeet löytyvät käännösvirheistä:

```{.rust tiedosto="esimerkit/04-kattavuus.ei-kaanny.rs"}
```

```
error[E0004]: non-exhaustive patterns: `&Taso::Jaljitys` not covered
```

Tästä syystä jokerihaaraa `_ =>` vältetään omien `enum`-tyyppien
käsittelyssä: se hiljentäisi juuri tämän virheen.

## Esimerkki: laskin

Lausekkeen jäsentäminen yhdistää luvun asiat. Ensin syöte muutetaan
*tokeneiksi*, joista osalla on dataa:

```{.rust tiedosto="esimerkit/04-laskin.rs" osa="tokenit"}
```

Hahmo `'0'..='9' | '.'` täsmää merkkiväliin tai pisteeseen.
`peekable()` antaa katsoa seuraavaa merkkiä kuluttamatta sitä, ja
`next_if` kuluttaa merkin vain, jos ehto täyttyy. Haarat palauttavat
`Tokeni`-arvon, tai ne jatkavat silmukkaa (`continue`) tai palaavat
funktiosta (`return`). Jälkimmäiset ovat tyyppiä `!`, joka sopii minkä
tahansa tyypin paikalle.

Jäsennin on *rekursiivisesti laskeutuva*: kutakin kieliopin sääntöä
vastaa yksi metodi, ja laskujärjestys seuraa kieliopista:

```{.rust tiedosto="esimerkit/04-laskin.rs" osa="jasennin"}
```

`op @ (Tokeni::Plus | Tokeni::Miinus)` sekä tarkistaa hahmon että sitoo
täsmänneen arvon muuttujaan `op`. `?` palauttaa virheen heti kutsujalle,
joten virheiden käsittely ei peitä jäsentimen rakennetta.

```{.rust tiedosto="esimerkit/04-laskin.rs" osa="laske"}
```

```{.tuloste tiedosto="esimerkit/04-laskin.odotettu"}
```

## Käytännössä

- **Tee virheelliset tilat mahdottomiksi.** Mallinna tila `enum`-
  tyyppinä, jonka muunnelmissa on vain kyseisessä tilassa kelvollinen
  data (*make illegal states unrepresentable*). C:n tyylinen rakenne,
  jossa on tilakenttä ja kentät kaikille tiloille, sallii ristiriidat,
  kuten avoimen tilan ilman istuntoa.
- **Tilakone arvona.** `fn siirtyma(tila, tapahtuma) -> Tila` on helppo
  testata, ja kaikki siirtymät näkyvät yhdessä `match`-lausekkeessa.
  Kun tilat ovat eri tyyppejä ja siirtymät metodeja, jotka kuluttavat
  `self`-arvon, kääntäjä estää myös väärät siirtymät (*typestate*-malli).
- **Ei jokerihaaraa omille enumeille.** Luettele muunnelmat, jotta
  uuden muunnelman lisääminen näyttää kaikki muutettavat kohdat.
  Kirjaston julkisen `enum`-tyypin voi merkitä
  `#[non_exhaustive]`, jolloin käyttäjien on pakko kirjoittaa jokerihaara
  ja kirjasto voi lisätä muunnelmia rikkomatta yhteensopivuutta.
- **`if let` ja `let ... else` yhdelle hahmolle.** `match`, jossa toinen
  haara on tyhjä, kirjoitetaan `if let` -muotoon. Esiehdon tarkistus
  kirjoitetaan `let ... else` -muotoon, jolloin onnistunut polku jää
  sisentämättä.
- **`enum` on yhtä suuri kuin suurin muunnelma.** Arvon koko on suurimman
  muunnelman koko ja tunniste. Jos yksi muunnelma on suuri, se
  laatikoidaan (`Box<T>`), ettei koko `enum` kasva. Clippyn
  `large_enum_variant` varoittaa tästä.
- **Hinta.** `match` kääntyy hyppytauluksi tai vertailuketjuksi kuten
  `switch`. `Option<&T>` ja `Option<Box<T>>` ovat yhtä suuria kuin
  osoitin, koska `None` esitetään nollana (*niche optimization*).

## Itsearviointi

- Osaat kirjoittaa `match`-lausekkeen, jossa hahmot purkavat dataa,
  yhdistävät vaihtoehtoja ja sisältävät ehtoja.
- Osaat mallintaa tilakoneen `enum`-tyypeillä niin, ettei virheellistä
  tilaa voi esittää.
- Osaat selittää, miksi jokerihaaraa vältetään omien `enum`-tyyppien
  kanssa, ja mitä `#[non_exhaustive]` tekee.
- Osaat käyttää `loop`-, `while let`- ja `for`-silmukoita sekä
  nimiöityä `break`-lausetta.
