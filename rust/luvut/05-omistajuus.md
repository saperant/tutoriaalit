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

```{.dot otsikko="`String` on pinossa kolmen sanan otsake, ja teksti on keossa. `&str` on osoitin ja pituus samaan puskuriin: funktion `otsikko` paluuarvo ei kopioi merkkejä."}
digraph {
  rankdir=TB; nodesep=0.6; ranksep=0.6;
  node [shape=plain, style=""];
  s [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>raportti: String (pino)</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus 31</td><td port="c" bgcolor="#EEF1F6">kapasiteetti 31</td></tr></table>>];
  v [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="2"><i>otsikko(&amp;raportti): &amp;str (pino)</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus 14</td></tr></table>>];
  keko [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td port="a" bgcolor="#FFFFFF">Viikkoraportti</td><td bgcolor="#FFFFFF">\nKaikki kunnossa.</td></tr>
    <tr><td border="0" align="left" colspan="2"><i>keko: 31 tavua</i></td></tr></table>>];
  s:p:s -> keko:a:n;
  v:p:s -> keko:a:n;
}
```

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

```{.tuloste tiedosto="esimerkit/05-omistajuus.odotettu" rivit="1-6"}
```

```{.dot otsikko="Kopio: `let kopio = raportti.clone();` varaa uuden puskurin ja kopioi tekstin. Kummallakin puskurilla on oma omistajansa."}
digraph {
  rankdir=TB; nodesep=0.6; ranksep=0.5;
  node [shape=plain, style=""];
  a1 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>raportti</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus</td><td port="c" bgcolor="#EEF1F6">kapasiteetti</td></tr></table>>];
  a2 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>kopio</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus</td><td port="c" bgcolor="#EEF1F6">kapasiteetti</td></tr></table>>];
  b1 [shape=box, style=filled, fillcolor="#FFFFFF", label="Viikkoraportti…"];
  b2 [shape=box, style=filled, fillcolor="#FFFFFF", label="Viikkoraportti…"];
  a1:p:s -> b1; a2:p:s -> b2;
}
```

```{.dot otsikko="Siirto: `arkistoi(raportti);` kopioi vain otsakkeen funktion parametriin. Puskurilla on yhä yksi omistaja, ja kääntäjä kieltää vanhan nimen käytön."}
digraph {
  rankdir=TB; nodesep=0.6; ranksep=0.5;
  node [shape=plain, style=""];
  c1 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><font color="#9AA3AF"><i>raportti kutsujassa: siirretty</i></font></td></tr>
    <tr><td port="p" bgcolor="#FFFFFF"><font color="#9AA3AF">osoitin</font></td><td port="l" bgcolor="#FFFFFF"><font color="#9AA3AF">pituus</font></td><td port="c" bgcolor="#FFFFFF"><font color="#9AA3AF">kapasiteetti</font></td></tr></table>>];
  c2 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>parametri raportti</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus</td><td port="c" bgcolor="#EEF1F6">kapasiteetti</td></tr></table>>];
  b3 [shape=box, style=filled, fillcolor="#FFFFFF", label="Viikkoraportti…"];
  c2:p:s -> b3;
  c1:p:s -> b3 [style=dotted, arrowhead=none];
}
```

`clone()` tekee syvän kopion. Se on aina näkyvä, joten kalliit kopiot
löytyvät koodista hakemalla. Pienet arvotyypit, jotka eivät omista
resursseja, toteuttavat `Copy`-piirteen. Niiden sijoitus kopioi, eikä
alkuperäinen muutu käyttökelvottomaksi:

```{.rust tiedosto="esimerkit/05-omistajuus.rs" osa="copy"}
```

```{.tuloste tiedosto="esimerkit/05-omistajuus.odotettu" rivit="7-7"}
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

```{.ajoituskaavio otsikko="Lainojen voimassaolo esimerkin riveillä. Jaettu laina `ensimmainen` on voimassa riviltä 3 viimeiseen käyttöönsä rivillä 5. Rivin 4 `push` tarvitsee muokkaavan lainan samaan aikaan, joten se hylätään; rivillä 6 jaettu laina on jo päättynyt."}
{"signal": [
  {"name": "rivi", "wave": "======",
   "data": ["2", "3", "4", "5", "6", "7"]},
  {"name": "&jono[0] (ensimmainen)", "wave": "01..0."},
  {"name": "&mut jono (push)", "wave": "0.1010"}
]}
```

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

```{.tuloste tiedosto="esimerkit/05-drop.odotettu" rivit="1-10"}
```

```{.rust tiedosto="esimerkit/05-drop.rs" osa="take"}
```

```{.tuloste tiedosto="esimerkit/05-drop.odotettu" rivit="11-14"}
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
