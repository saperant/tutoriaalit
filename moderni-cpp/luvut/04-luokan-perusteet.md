# Luokan perusteet {.runko-omat-tyypit}

C:ssä tiedot ovat rakenteissa ja niitä käsittelevät funktiot erillään:
`struct tili` ja `tili_talleta(struct tili *t, ...)`. C++:n *luokka*
yhdistää ne. Tässä luvussa esitellään luokan perussyntaksi:
jäsenfunktiot, näkyvyys, muodostin ja hajotin sekä operaattorien
kuormitus. Luokan suunnittelua, periytymistä ja kopioinnin hallintaa
käsittelevät luvut [Luokat](#luokat),
[Resurssienhallinta](#resurssienhallinta) ja
[Siirtosemantiikka](#siirtosemantiikka).

## Jäsenfunktiot

Rakenteen sisään voi kirjoittaa funktioita. *Jäsenfunktio* kutsutaan
olion kautta pisteellä (`s.ala()`), ja se näkee olion jäsenet suoraan:

```{.cpp tiedosto="esimerkit/04-luokka.cpp" osa="rakenne"}
```

Jäsenfunktio saa kutsutun olion osoitteen piiloparametrina `this`.
Rungossa `leveys` tarkoittaa samaa kuin `this->leveys`. Kutsu
`s.skaalaa(2.0)` vastaa siis C:n kutsua `skaalaa(&s, 2.0)`.

Parametriluettelon jälkeinen `const` lupaa, ettei funktio muuta oliota.
Vakio-oliolle ja vakioviittauksen kautta voi kutsua vain
`const`-jäsenfunktioita, joten jokainen lukeva jäsenfunktio merkitään
`const`:

```{.cpp tiedosto="esimerkit/04-luokka.cpp" osa="rakenne-kaytto"}
```

## Näkyvyys ja muodostin

Rakenteen `Suorakulmio` kenttiin voi sijoittaa mitä tahansa. Usein
kenttien välillä on kuitenkin sääntö, jonka on oltava aina voimassa,
eli *invariantti*. Murtoluvun nimittäjä ei saa olla nolla. Silloin
kentät piilotetaan ja niihin päästään käsiksi vain jäsenfunktioiden
kautta:

```{.cpp tiedosto="esimerkit/04-luokka.cpp" osa="luokka"}
```

Osion `public:` jäsenet ovat luokan rajapinta. Osion `private:`
jäseniä voivat käyttää vain luokan omat jäsenfunktiot. Avainsanojen
`class` ja `struct` ainoa ero on oletusnäkyvyys: `class`-luokan jäsenet
ovat oletuksena yksityisiä, `struct`-rakenteen julkisia. Yksityisten
jäsenmuuttujien nimen loppuun kirjoitetaan tässä tutoriaalissa
alaviiva, jotta ne erottuvat parametreista.

*Muodostin* (*constructor*) on luokan niminen jäsenfunktio, jolla ei
ole paluutyyppiä. Se suoritetaan aina, kun olio luodaan, joten oliota
ei voi jättää alustamatta. Jäsenet alustetaan *alustuslistassa*
kaksoispisteen jälkeen, esittelyjärjestyksessä. Rungossa muodostin
tarkistaa invariantin ja heittää poikkeuksen, jos oliota ei voi luoda.
Koska kentät ovat yksityisiä ja jokainen muuttava jäsenfunktio
palauttaa invariantin voimaan, luokan käyttäjä ei voi saada aikaan
virheellistä murtolukua.

```{.cpp tiedosto="esimerkit/04-luokka.cpp" osa="luokka-kaytto"}
```

## Operaattorien kuormitus

Operaattorit ovat funktioita, joiden nimi on `operator+`,
`operator==` ja niin edelleen. Ne voi kuormittaa omille tyypeille,
jolloin murtolukuja voi laskea yhteen ja vertailla kuten lukuja:

```{.cpp tiedosto="esimerkit/04-luokka.cpp" osa="operaattorit"}
```

```{.cpp tiedosto="esimerkit/04-luokka.cpp" osa="operaattorit-kaytto"}
```

Koko ohjelma tulostaa:

```{.tuloste tiedosto="esimerkit/04-luokka.odotettu"}
```

Operaattorit on kirjoitettu luokan ulkopuolelle tavallisina funktioina,
koska ne tarvitsevat vain julkista rajapintaa. Operaattoria kuormitetaan
vain, kun sen merkitys on tyypille luonteva. Vertailuoperaattorit saa
C++20:ssä yleensä kääntäjältä valmiina (luku [Luokat](#luokat)).

## Hajotin ja olion elinkaari

*Hajotin* (*destructor*) on jäsenfunktio `~Luokka()`, jonka kääntäjä
kutsuu automaattisesti, kun olio tuhoutuu. Paikallinen olio tuhoutuu,
kun suoritus poistuu lohkosta, jossa se on määritelty. Hajotin on
paikka vapauttaa se, minkä muodostin hankki. Seuraava luokka käärii
C:n tiedostokahvan:

```{.cpp tiedosto="esimerkit/04-elinkaari.cpp" osa="luokka"}
```

Avainsana `explicit` ja merkintä `= delete` selitetään luvussa
[Luokat](#luokat). Tässä riittää tietää, että jälkimmäinen kieltää
olion kopioinnin.

```{.cpp tiedosto="esimerkit/04-elinkaari.cpp" osa="lohko"}
```

```{.cpp tiedosto="esimerkit/04-elinkaari.cpp" osa="funktio"}
```

```{.cpp tiedosto="esimerkit/04-elinkaari.cpp" osa="kutsut"}
```

```{.tuloste tiedosto="esimerkit/04-elinkaari.odotettu"}
```

Oliot tuhotaan käänteisessä luontijärjestyksessä, ja hajotin
suoritetaan jokaisella poistumisreitillä: lohkon lopussa, ennenaikaisessa
`return`-lauseessa ja poikkeuksen kulkiessa lohkon läpi. C:ssä sama
vaatisi `fclose`-kutsun jokaiseen haaraan tai `goto`-siivouksen.

```{.dot otsikko="Paikallisen olion elinkaari. Muodostin ja hajotin rajaavat ajan, jona invariantti on voimassa ja resurssi olion hallussa."}
digraph {
  rankdir=LR; nodesep=0.2; ranksep=0.3;
  node [shape=box, fontsize=10, margin="0.08,0.05"];
  c [label="muodostin\nhankkii resurssin"];
  k [label="käyttö\njäsenfunktiot"];
  l [label="lohko päättyy\n}, return, poikkeus"];
  d [label="hajotin\nvapauttaa resurssin"];
  c -> k -> l -> d;
}
```

Tätä resurssin sitomista olion elinkaareen kutsutaan nimellä *RAII*.
Se on C++:n tärkein yksittäinen idiomi, ja `std::string` ja
`std::vector` vapauttavat muistinsa juuri näin. Luku
[Resurssienhallinta](#resurssienhallinta) käsittelee aihetta
tarkemmin. Omaa hajotinta tarvitaan harvoin, koska standardikirjaston
tyypeistä koottu luokka siivoaa jäsenensä automaattisesti.

Dynaamisesti luotu olio (`new`) elää, kunnes se tuhotaan
`delete`-lauseella. Modernissa C++:ssa näitä ei kirjoiteta käsin, vaan
olion omistaa älykäs osoitin, jonka hajotin tuhoaa olion.

## Käytännössä

- **Olio on käyttökelpoinen heti muodostimen jälkeen.** Erillistä
  `init`-funktiota ei tehdä. Jos oliota ei voi alustaa kelvolliseksi,
  muodostin heittää poikkeuksen.
- **Jäsenet alustetaan alustuslistassa tai oletusarvolla.** Rungossa
  tehty sijoitus alustaisi jäsenen ensin oletusarvoon ja sijoittaisi
  sitten uudelleen. Vakio- ja viittausjäseniä ei voi alustaa muuten.
- **`const` kaikkiin lukeviin jäsenfunktioihin.** Muuten oliota ei voi
  käyttää vakioviittauksen kautta, joka on tavallisin tapa välittää
  olio funktiolle.
- **Kentät yksityisiksi, kun niillä on invariantti.** Pelkälle
  tietojoukolle riittää `struct` julkisine kenttineen. Hakufunktioita
  (`osoittaja()`) kirjoitetaan vain tiedoille, joita käyttäjä tarvitsee.
- **Hajotin ei heitä poikkeusta.** Hajotinta kutsutaan myös silloin,
  kun toinen poikkeus on jo matkalla, ja kaksi samanaikaista poikkeusta
  päättää ohjelman.
- **Resurssia hallitseva luokka hallitsee yhtä resurssia.** Luokka,
  jolla on oma hajotin, tarvitsee myös päätöksen kopioinnista. Muut
  luokat kootaan tällaisista jäsenistä ilman omaa hajotinta.

## Itsearviointi

- Osaat kirjoittaa luokan, jolla on yksityiset kentät, muodostin
  alustuslistoineen ja `const`-jäsenfunktioita.
- Osaat selittää, mitä `this` on ja mitä jäsenfunktion `const` lupaa.
- Osaat kertoa, milloin paikallisen olion muodostin ja hajotin
  suoritetaan ja missä järjestyksessä oliot tuhotaan.
- Osaat kuormittaa operaattorin omalle tyypille.
- Osaat selittää, miksi resurssi kannattaa vapauttaa hajottimessa.
