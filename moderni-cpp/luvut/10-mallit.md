# Mallit ja konseptit {.runko-omat-tyypit}

*Mallit* (*templates*) ovat C++:n tapa kirjoittaa yleiskäyttöistä koodia,
joka toimii monella tyypillä. Kääntäjä tuottaa mallista erillisen
version jokaiselle käytetylle tyypille, joten yleiskäyttöisyydestä ei
makseta ajoaikana. Koko standardikirjaston säiliöistä algoritmeihin
voi ajatella mallikirjastona.

## Funktio- ja luokkamallit

Funktiomallissa tyyppiparametri esitellään sanoilla
`template <typename T>`:

```{.cpp tiedosto="esimerkit/10-mallit.cpp" osa="funktio"}
```

Kääntäjä päättelee `T`:n argumenteista. Jos argumentit ovat eri
tyyppiä, kuten `suurin(2, 2.5)`, päättely epäonnistuu, ja tyyppi on
annettava itse: `suurin<double>(2, 2.5)`.

Luokkamalli toimii samoin. Seuraava pino on rakennettu vektorin päälle,
ja sen `ota`-metodi palauttaa `std::optional`-arvon, koska pino voi olla
tyhjä:

```{.cpp tiedosto="esimerkit/10-mallit.cpp" osa="luokka"}
```

C++17:stä alkaen luokkamallin tyyppiparametrit voidaan päätellä
muodostimen argumenteista (*class template argument deduction*, CTAD).
Siksi voi kirjoittaa `Pino luvut{std::vector{1, 2, 3}}` ilman
merkintää `<int>`. Samasta syystä kelpaa myös `std::vector v{1, 2, 3}`.

## `if constexpr`

`if constexpr` valitsee haaran käännösaikana. Valitsematta jääneitä
haaroja ei käännetä kyseiselle tyypille lainkaan, joten niissä saa olla
koodia, joka ei kelpaisi kyseiselle tyypille. Esimerkiksi
`std::string{arvo}` ei käänny, kun `arvo` on kokonaisluku, mutta koska
haara hylätään, virhettä ei synny.

```{.cpp tiedosto="esimerkit/10-mallit.cpp" osa="constexpr-if"}
```

Ehdoissa käytetään otsikon `<type_traits>` *tyyppipiirteitä*, kuten
`std::is_integral_v<T>`, jotka kertovat tyypin ominaisuuksista
käännösaikana.

## Lyhennetty mallisyntaksi

C++20:ssa funktion parametrin tyypiksi voi kirjoittaa `auto`, jolloin
funktiosta tulee malli ilman erillistä `template`-esittelyä. Jokainen
`auto` on oma tyyppiparametrinsa.

```{.cpp tiedosto="esimerkit/10-mallit.cpp" osa="lyhennetty"}
```

```{.cpp tiedosto="esimerkit/10-mallit.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-mallit.odotettu"}
```

## Variadiset mallit ja fold-lausekkeet

*Variadinen malli* ottaa vaihtelevan määrän tyyppiparametreja.
Merkintä `typename... Arvot` esittelee *parametripaketin*, ja
`arvot...` purkaa sen. C++17:n *fold-lauseke* soveltaa binäärioperaattoria
paketin kaikkiin alkioihin:

```{.cpp tiedosto="esimerkit/10-variadiset.cpp" osa="summa"}
```

Lauseke `(arvot + ... + 0)` laajenee muotoon `a1 + (a2 + (… + 0))`.
Alkuarvo `0` tekee tyhjästä paketista kelvollisen. Loogisille
operaattoreille alkuarvoa ei tarvita, koska tyhjän paketin arvo on
määritelty (`&&`: tosi, `||`: epätosi):

```{.cpp tiedosto="esimerkit/10-variadiset.cpp" osa="kaikki"}
```

Pilkkuoperaattorin avulla lausekkeen voi suorittaa jokaiselle
argumentille järjestyksessä. `sizeof...` kertoo paketin koon:

```{.cpp tiedosto="esimerkit/10-variadiset.cpp" osa="tulosta"}
```

```{.cpp tiedosto="esimerkit/10-variadiset.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-variadiset.odotettu"}
```

## Konseptit

Perinteisten mallien heikkous on, että vaatimuksia tyyppiparametrille
ei voi ilmaista. Jos tyyppi ei kelpaa, virheilmoitus syntyy syvältä
mallin sisältä ja voi olla satoja rivejä pitkä. C++20:n *konseptit*
ovat nimettyjä, käännösaikana tarkistettavia vaatimuksia tyypeille.

Standardikirjaston valmiita konsepteja (`<concepts>`) voi käyttää
suoraan `typename`-sanan paikalla. Rajoitetut mallit voivat myös
kuormittaa toisiaan:

```{.cpp tiedosto="esimerkit/10-konseptit.cpp" osa="vakio"}
```

Oma konsepti määritellään `requires`-lausekkeella, joka luettelee,
minkä lausekkeiden on käännyttävä. Vaatimus
`{ x.size() } -> std::convertible_to<std::size_t>` edellyttää myös, että
tuloksen tyyppi täyttää annetun konseptin. Konseptia voi käyttää
lyhennetyssä syntaksissa `auto`-sanan edessä:

```{.cpp tiedosto="esimerkit/10-konseptit.cpp" osa="oma"}
```

Monimutkaisempi ehto kirjoitetaan `requires`-lauseeseen mallin
esittelyn perään:

```{.cpp tiedosto="esimerkit/10-konseptit.cpp" osa="requires"}
```

```{.cpp tiedosto="esimerkit/10-konseptit.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-konseptit.odotettu"}
```

Kun ehto ei täyty, virheilmoitus kertoo suoraan, mikä vaatimus jäi
täyttymättä:

```{.cpp tiedosto="esimerkit/10-konsepti.ei-kaanny.cpp"}
```

GCC ilmoittaa tässä tapauksessa muun muassa
`constraints not satisfied` ja tarkentaa, että listan iteraattori ei ole
hajasaanti-iteraattori. Konseptit toimivat siis myös dokumentaationa:
mallin esittely kertoo, millaisia tyyppejä se hyväksyy.

## Käytännössä

- **Mallit rajataan konsepteilla.** Rajaamaton malli hyväksyy minkä
  tahansa tyypin ja tuottaa virheilmoituksen syvältä toteutuksen sisältä.
  Standardin valmiit konseptit, kuten `std::integral` ja
  `std::ranges::range`, ovat ensisijaisia (Core Guidelines T.10, T.11).
- **Staattinen vai dynaaminen monimuotoisuus.** Mallit ratkaistaan
  käännösaikana: ne ovat nopeimpia, mutta jokainen tyyppi tuottaa oman
  koodinsa, ja tyyppien on oltava tiedossa käännösaikana.
  Virtuaalifunktiot sallivat eri tyyppien olioiden käsittelyn samassa
  säiliössä ja liitännäiset, mutta vaativat periytymisen ja yleensä
  dynaamisen muistin.
- **CRTP harkiten.** Mallissa *curiously recurring template pattern*
  luokka periytyy mallista, jolle se antaa itsensä parametrina, jolloin
  kantaluokka voi kutsua johdetun luokan funktioita ilman virtuaalikutsuja.
  Sitä käytetään sekoiteluokissa (*mixin*). C++23:n *deducing this*
  korvaa monet sen käyttötarkoitukset.
- **Mallit ovat otsikkotiedostoissa.** Kääntäjä tarvitsee mallin
  määrittelyn jokaisessa käännösyksikössä, joka käyttää sitä. Raskas
  mallikoodi pidentää käännösaikoja, mikä on suurissa projekteissa
  todellinen kustannus.

### Tyyppien pyyhintä

*Tyyppien pyyhintä* (*type erasure*) yhdistää arvosemantiikan ja
ajonaikaisen monimuotoisuuden. Käyttäjän tyyppien ei tarvitse periä
mitään; riittää, että ne täyttävät konseptin. Kääreluokka piilottaa
virtuaalisen rajapinnan toteutukseensa. Standardikirjaston
`std::function` ja `std::any` on toteutettu samalla mallilla.

```{.cpp tiedosto="esimerkit/10-tyyppipyyhinta.cpp" osa="muodot"}
```

```{.cpp tiedosto="esimerkit/10-tyyppipyyhinta.cpp" osa="pyyhinta"}
```

```{.cpp tiedosto="esimerkit/10-tyyppipyyhinta.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-tyyppipyyhinta.odotettu"}
```

Verrattuna luvun [Luokat](#luokat) periytymiseen tässä ratkaisussa
`Muoto` on tavallinen arvo, joka kopioituu ja tallentuu vektoriin ilman
älykkäitä osoittimia. Muodot taas ovat yksinkertaisia rakenteita, jotka
eivät tiedä mitään `Muoto`-luokasta. Hinta on yksi muistinvaraus oliota
kohti ja virtuaalikutsu.

## Itsearviointi

- Osaat kirjoittaa funktio- ja luokkamallin ja käyttää tyyppien päättelyä
  (CTAD).
- Osaat määritellä oman konseptin `requires`-lausekkeella ja rajata sillä
  mallin.
- Osaat kirjoittaa variadisen mallin fold-lausekkeella.
- Osaat valita mallien, virtuaalifunktioiden ja tyyppien pyyhinnän
  välillä.
