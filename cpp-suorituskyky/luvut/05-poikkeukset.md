# Poikkeukset ja `noexcept`

C++:n poikkeukset ovat nollakustannuksisia siinä mielessä, että
heittämättömällä polulla ei suoriteta yhtään ylimääräistä käskyä.
Heittäminen sen sijaan on kallista, tuhansia käskyjä. Tämä epäsymmetria
määrää, milloin poikkeuksia kannattaa käyttää. Toinen puoli on
`noexcept`: se ei juuri nopeuta kutsua, mutta se muuttaa
standardikirjaston algoritmien valintoja, ja sen puuttuminen voi
kopioida kokonaisen vektorin.

## Nollakustannusmalli

GCC ja Clang toteuttavat poikkeukset taulukoilla. Kääntäjä kirjoittaa
jokaisesta funktiosta *purkutaulun* (engl. unwind table, osio
`.eh_frame`), joka kertoo, miten pinokehys puretaan ja mitkä purkajat on
kutsuttava. Normaali suoritus ei koske tauluihin. Kun poikkeus
heitetään, ajonaikainen kirjasto

1. varaa poikkeusoliolle muistin (`__cxa_allocate_exception`),
2. etsii jokaiselle pinon kehykselle purkutaulun osoitteen perusteella,
3. etsii sopivan `catch`-lohkon tyyppitiedon (RTTI) avulla ja
4. purkaa kehykset ja kutsuu matkalla purkajat.

Vaiheet 2 ja 3 ovat hitaita: haku käy läpi ladattujen kirjastojen
taulut ja vertaa tyyppejä merkkijonoina. Ennen kuin poikkeusta
heitetään, mitään ei tapahdu, mutta heittäminen maksaa jokaiselta
kehykseltä.

## Heittämisen hinta

Jäsennin, joka heittää poikkeuksen virheellisestä syötteestä:

```{.cpp tiedosto="esimerkit/05-jasennys.cpp" osa="poikkeus"}
```

Sama `std::expected`illa (C++23), joka palauttaa joko arvon tai
virheen:

```{.cpp tiedosto="esimerkit/05-jasennys.cpp" osa="expected"}
```

```{.cpp tiedosto="esimerkit/05-jasennys.cpp" osa="summat"}
```

```{.tuloste tiedosto="esimerkit/05-jasennys.odotettu"}
```

Käskyt jäsennystä kohden tuhannella rivillä:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-poikkeukset.txt"}
```

```{.tuloste tiedosto="esimerkit/tulokset/05-jasennys.txt"}
```

![Käskyt jäsennystä kohden. Asteikko on logaritminen: epäonnistuva poikkeuspolku on kaksi kertaluokkaa muita kalliimpi.](kuvat/poikkeukset.png){width=68%}

Onnistuvalla polulla tavat ovat yhtä nopeita: poikkeusversio on jopa
hieman nopeampi, koska paluuarvo on pelkkä `int` eikä kutsujan tarvitse
tarkistaa mitään. Epäonnistuvalla polulla jokainen heitto maksaa noin
14 000 käskyä ja ajassa noin mikrosekunnin, yli sata kertaa enemmän
kuin itse jäsennys. Monisäikeisessä ohjelmassa hinta oli vanhemmilla
C-kirjastoilla vielä suurempi, koska purkutaulujen haku otti
globaalin lukon; glibc 2.35:stä alkaen haku on lukoton.

Johtopäätös: poikkeus sopii virheisiin, jotka ovat harvinaisia ja joita
ei voi käsitellä paikallisesti, kuten muistin loppumiseen, rikkinäiseen
asetustiedostoon tai katkenneeseen yhteyteen. Odotettavissa oleviin
"virheisiin", kuten käyttäjän syötteen tarkistukseen tai haun
epäonnistumiseen, sopii paluuarvo: `std::expected`, `std::optional` tai
virhekoodi. Sama päätelmä on luettavuudenkin kannalta perusteltu: kutsuja
näkee tyypistä, että funktio voi epäonnistua.

## Poikkeuksia ilman: `-fno-exceptions`

Pelimoottorit, sulautetut järjestelmät ja osa suurista koodikannoista
(esimerkiksi Googlen ja LLVM:n) kääntävät ilman poikkeuksia
(`-fno-exceptions`). Binääri pienenee, koska purkutauluja ja
`catch`-lohkoja ei tarvita, ja kääntäjä saa järjestellä koodia
vapaammin. Hinta on, että standardikirjaston poikkeukset, kuten
`std::bad_alloc`, kaatavat ohjelman, ja virheet on välitettävä muuten.
Päätös tehdään koko projektille, ei funktiokohtaisesti.

## `noexcept` ja vektorin kasvu

Kun `std::vector` kasvaa, se siirtää vanhat alkiot uuteen puskuriin.
Jos siirto voisi heittää poikkeuksen kesken kaiken, osa alkioista olisi
jo siirretty eikä vanhaa tilaa voisi palauttaa. Siksi vektori siirtää
vain, jos siirtokonstruktori on `noexcept` (tai tyyppiä ei voi
kopioida); muuten se kopioi. Tämä on `std::move_if_noexcept` ja vahva
poikkeustakuu, jotka *Moderni C++* esittelee. Tässä hinta mitataan
muistinvarauksina, ja mukana on kolmas, vielä yleisempi virhe:

```{.cpp tiedosto="esimerkit/05-noexcept.cpp" osa="tyypit"}
```

```{.cpp tiedosto="esimerkit/05-noexcept.cpp" osa="tarkistus"}
```

```{.cpp tiedosto="esimerkit/05-noexcept.cpp" osa="kasvatus"}
```

```{.tuloste tiedosto="esimerkit/05-noexcept.odotettu"}
```

Nollan säännön tyyppi tekee 2 011 varausta: kaksi merkkijonoa
kullekin tuhannelle tilaukselle ja 11 vektorin puskuria. Ilman
`noexcept`ia jokainen kasvu kopioi kaikki merkkijonot, mikä tuplaa
varaukset. Pelkkä tyhjä purkaja on pahin: käyttäjän esittelemä purkaja
estää kääntäjää tuottamasta siirtokonstruktoria, joten myös
väliaikaisen olion `push_back` kopioi. Ohjelma toimii oikein ja
kääntyy varoituksitta, mutta kolminkertaisilla varauksilla.

`static_assert(std::is_nothrow_move_constructible_v<T>)` tyypin
vieressä estää virheen palaamasta, kun joku myöhemmin lisää tyyppiin
purkajan tai jäsenen, jonka siirto ei ole `noexcept`.

`noexcept` muuttaa muitakin valintoja: `std::swap`, `std::optional` ja
säiliöiden sijoitus käyttävät sitä samalla tavalla. Itse
funktiokutsua merkintä nopeuttaa vähän: kääntäjä voi jättää pois
kutsukohdan purkukoodin. Jos `noexcept`-funktiosta kuitenkin
karkaa poikkeus, ohjelma päättyy kutsuun `std::terminate`.

## Käytännössä

- **Heitä vain poikkeuksellisissa tilanteissa.** Jos virhe on
  odotettu osa normaalia toimintaa, palauta `std::expected` tai
  `std::optional`.
- **Merkitse siirto ja `swap` `noexcept`iksi**, tai paremmin: noudata
  nollan sääntöä, jolloin kääntäjä tekee sen itse.
- **Älä kirjoita tyhjää purkajaa.** Jos purkaja tarvitaan, esimerkiksi
  virtuaalinen kantaluokassa, esittele myös siirto ja kopio
  `= default`-merkinnällä (viiden sääntö).
- **Tarkista siirrettävyys `static_assert`illa** tyypeille, joita
  säilytetään vektoreissa.
- **Älä merkitse `noexcept`iksi funktiota, joka voi heittää.**
  Poikkeus muuttuu silloin ohjelman kaatumiseksi.

## Itsearviointi

- Osaat selittää taulukkopohjaisen poikkeusmallin ja sen, miksi
  heittämätön polku on ilmainen mutta heittäminen kallista.
- Osaat valita poikkeuksen ja `std::expected`in välillä virheen
  todennäköisyyden ja käsittelypaikan perusteella.
- Osaat mitata, miten `noexcept`in tai siirtokonstruktorin
  puuttuminen näkyy vektorin kasvaessa.
- Osaat varmistaa tyypin siirron `static_assert`illa ja selittää,
  miksi tyhjä purkaja estää siirron.
