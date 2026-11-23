# Omistajuus ja lainaus {.runko-muisti}

Omistajuus on Rustin tapa hallita muistia ilman roskienkeruuta ja
ilman käsin kutsuttavaa `free`-funktiota. Säännöt tarkistetaan
käännösaikana, eikä niillä ole ajonaikaista hintaa.

## Muistimalli

Rustin muistimalli on sama kuin C:n: pino, keko ja staattinen muisti.
Paikalliset muuttujat ovat pinossa. `Box`, `Vec`, `String` ja muut
kokoelmat varaavat datansa keosta, ja niiden pinossa oleva osa on pieni
otsake (osoitin, pituus ja kapasiteetti). Merkkijonoliteraalit ja
`static`-muuttujat ovat ohjelman datasegmentissä, ja niihin viittaavien
viitteiden elinaika on `'static`.

## Omistajuuden säännöt

1. Jokaisella arvolla on yksi omistaja.
2. Kun omistaja poistuu näkyvyysalueelta, arvo vapautetaan
   (*drop*).
3. Sijoitus, arvoparametri ja paluuarvo *siirtävät* omistuksen. Siirron
   jälkeen vanhaa nimeä ei voi käyttää.

```{.rust tiedosto="esimerkit/05-omistajuus.rs" osa="funktiot"}
```

Funktion allekirjoitus kertoo kutsujalle, mitä funktio tekee arvolle:
`String` ottaa omistuksen, `&str` lainaa lukemista varten ja `&mut
String` lainaa muokkaamista varten. C:ssä sama tieto on parhaimmillaan
kommentissa.

```{.rust tiedosto="esimerkit/05-omistajuus.rs" osa="kaytto"}
```

`clone()` tekee syvän kopion. Se on aina näkyvä, joten kalliit kopiot
löytyvät koodista hakemalla. Pienet arvotyypit, jotka eivät omista
resursseja, toteuttavat `Copy`-piirteen. Niiden sijoitus kopioi, eikä
alkuperäinen muutu käyttökelvottomaksi:

```{.rust tiedosto="esimerkit/05-omistajuus.rs" osa="copy"}
```

```{.tuloste tiedosto="esimerkit/05-omistajuus.odotettu"}
```

## Lainaussäännöt

Viite eli *lainaus* antaa käyttää arvoa ottamatta omistusta. Lainoja
koskee kaksi sääntöä:

1. Samaan aikaan voi olla **joko** mielivaltainen määrä jaettuja
   lainauksia `&T` **tai** yksi muokkaava lainaus `&mut T`.
2. Lainaus ei voi elää pidempään kuin lainattu arvo.

Ensimmäinen sääntö estää C++:sta tutun iteraattorin ja viitteen
mitätöitymisen. Vektoriin lisääminen voi siirtää sen datan uuteen
paikkaan, jolloin viite vanhaan alkioon jäisi roikkumaan:

```{.rust tiedosto="esimerkit/05-lainaus.ei-kaanny.rs"}
```

```
error[E0502]: cannot borrow `jono` as mutable because it is also
              borrowed as immutable
```

Lainaus kestää sen viimeiseen käyttöön asti, ei näkyvyysalueen loppuun
(*non-lexical lifetimes*). Siksi jälkimmäinen `push` on sallittu.

Toinen sääntö estää roikkuvat viitteet. Viite paikalliseen muuttujaan
ei voi palata funktiosta:

```{.rust tiedosto="esimerkit/05-roikkuva.ei-kaanny.rs"}
```

```
error[E0515]: cannot return reference to local variable `viesti`
```

`pisin_rivi` sen sijaan saa palauttaa viitteen, koska viite osoittaa
parametrina saatuun dataan. Kääntäjä päättelee tämän allekirjoituksesta:
kun funktio saa yhden viitteen ja palauttaa viitteen, palautettu viite
lainaa samaa dataa. Monimutkaisemmat tapaukset kirjoitetaan
elinaikamerkinnöin (luku 9).

## Viipaleet

*Viipale* (*slice*) `&[T]` on lainaus yhtenäiseen jonoon alkioita:
osoitin ja pituus. Se on Rustin tapa välittää taulukoita, ja sama
funktio toimii taulukoille, vektoreille ja niiden osille. `&str` on
vastaava viipale UTF-8-merkkijonoon.

```{.rust tiedosto="esimerkit/05-viipaleet.rs" osa="tilastot"}
```

Muokkaavia lainauksia samaan vektoriin voi olla vain yksi, mutta
`split_at_mut` jakaa viipaleen kahdeksi erilliseksi muokattavaksi
osaksi. Lainaustarkistin ei voi itse päätellä, että indekseillä
valitut osat eivät mene päällekkäin, joten tähän tarvitaan
kirjastofunktio (sen toteutus on luvussa 12).

```{.rust tiedosto="esimerkit/05-viipaleet.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-viipaleet.odotettu"}
```

## Drop ja RAII

Kun arvo vapautetaan, Rust kutsuu sen `Drop`-toteutusta ja sitten sen
kenttien `Drop`-toteutuksia. Malli on sama kuin C++:n RAII: resurssi
sidotaan olion elinaikaan, ja tiedostot, lukot ja yhteydet vapautuvat
kaikilla poluilla, myös virheen ja paniikin sattuessa.

```{.rust tiedosto="esimerkit/05-drop.rs" osa="vartija"}
```

Paikalliset muuttujat vapautetaan käänteisessä esittelyjärjestyksessä.
Funktio `drop(x)` siirtää arvon itselleen ja vapauttaa sen heti.
`Option::take()` siirtää arvon ulos rakenteesta ja jättää tilalle
`None`-arvon. Se on tavallinen tapa siirtää omistus ulos kentästä, kun
koko rakennetta ei voi kuluttaa:

```{.rust tiedosto="esimerkit/05-drop.rs" osa="jarjestys"}
```

```{.rust tiedosto="esimerkit/05-drop.rs" osa="take"}
```

```{.tuloste tiedosto="esimerkit/05-drop.odotettu"}
```

`std::mem::replace` ja `std::mem::swap` ovat yleisempiä muotoja samasta
ajatuksesta: ne vaihtavat arvon paikkaa ilman, että mikään kohta jää
hetkeksikään alustamattomaksi.

## Käytännössä

- **Lainaa parametrit, omista kentät.** Funktio, joka vain lukee,
  ottaa `&str`- tai `&[T]`-parametrin (ei `&String` tai `&Vec<T>`),
  jolloin sitä voi kutsua myös literaaleilla ja viipaleilla. Rakenteet
  omistavat datansa (`String`, `Vec<T>`), ellei niiden kuulu olla
  lyhytikäisiä näkymiä (luku 9).
- **Ota omistus, kun säilytät arvon.** Jos funktio tallettaa arvon
  rakenteeseen, se ottaa parametrin arvona (`String`). Kutsuja päättää,
  siirtääkö arvon vai kloonaako sen, eikä funktio kopioi turhaan.
- **`clone()` on viimeinen keino.** Jos lainaustarkistin valittaa,
  järjestä koodi ensin uudelleen: lyhennä lainan elinaikaa, kerää
  muutokset ja tee ne silmukan jälkeen, tai käsittele indekseillä.
  Clone on oikea ratkaisu, kun kahden osapuolen todella on omistettava
  oma kopionsa.
- **RAII-vartija.** Resurssi, joka on vapautettava tai palautettava
  (lukko, tilapäistiedosto, mittauksen ajastin), kääritään tyyppiin,
  joka toteuttaa `Drop`-piirteen. Standardikirjaston `MutexGuard`,
  `File` ja `TcpStream` toimivat näin.
- **Drop ei saa epäonnistua.** `Drop::drop` ei voi palauttaa virhettä,
  ja paniikki sen sisällä paniikin aikana kaataa prosessin. Jos
  vapautus voi epäonnistua (esim. puskurin tallennus levylle), tarjoa
  erillinen `sulje(self) -> Result<...>` ja käytä `Drop`-toteutusta vain
  varmistuksena.
- **Vuoto on turvallista.** `std::mem::forget` ja `Rc`-syklit voivat
  jättää arvon vapauttamatta. Turvallinen koodi ei siis voi luottaa
  siihen, että `Drop` ajetaan aina.

## Itsearviointi

- Osaat selittää omistajuuden kolme sääntöä ja kertoa, mitkä tyypit
  ovat `Copy` ja miksi.
- Osaat valita parametrin tyypiksi `T`, `&T`, `&mut T` tai viipaleen ja
  perustella valinnan.
- Osaat tulkita virheet E0382, E0502 ja E0515 ja korjata koodin ilman
  turhaa `clone()`-kutsua.
- Osaat toteuttaa `Drop`-piirteen RAII-vartijaksi ja ennustaa
  vapautusjärjestyksen.
- Osaat siirtää arvon ulos rakenteesta `Option::take`- ja
  `mem::replace`-funktioilla.
