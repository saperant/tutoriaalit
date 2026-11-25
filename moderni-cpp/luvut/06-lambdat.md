# Funktiot ja lambdat {.runko-ohjaus}

Funktio on C++:ssakin ohjelman perusrakennuspala, mutta moderni tyyli
poikkeaa C:stä kahdessa asiassa. Tulokset palautetaan paluuarvoina eikä
osoitinparametrien kautta, ja toimintaa välitetään toisille funktioille
*lambdalausekkeina* funktio-osoittimien sijaan. Luku käsittelee ensin
parametrit ja paluuarvot ja sitten lambdat.

## Parametrit ja paluuarvot

Parametrin tyyppi kertoo, mitä funktio argumentille tekee: `T` kopioi,
`const T&` lukee ja `T&` muuttaa (taulukko luvussa
[C:stä C++:aan](#cstä-caan)). Tulos palautetaan paluuarvona silloinkin,
kun se on suuri. Kääntäjä rakentaa palautettavan olion suoraan kutsujan
muuttujaan (*kopion poisto*, *copy elision*) tai siirtää sen, joten
vektorin palauttaminen ei kopioi alkioita. Useita arvoja palautetaan
rakenteena, jonka kutsuja voi purkaa rakenteisella sidonnalla:

```{.cpp tiedosto="esimerkit/06-funktiot.cpp" osa="tulos"}
```

```{.cpp tiedosto="esimerkit/06-funktiot.cpp" osa="paluutyyppi"}
```

```{.cpp tiedosto="esimerkit/06-funktiot.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-funktiot.odotettu"}
```

Paluutyypiksi kirjoitettu `auto` päätellään `return`-lauseesta. Se
sopii lyhyille apufunktioille; julkisessa rajapinnassa tyyppi
kirjoitetaan näkyviin. Nuolimuotoa `auto f() -> T` käytetään, kun
paluutyyppi riippuu parametreista, ja se on myös lambdan paluutyypin
merkintätapa.

## Lambdalausekkeet

*Lambdalauseke* määrittelee nimettömän funktio-olion siihen kohtaan,
jossa sitä tarvitaan. Sen yleinen muoto on

```text
[sieppaukset](parametrit) -> paluutyyppi { runko }
```

Paluutyypin voi yleensä jättää pois, jolloin kääntäjä päättelee sen
`return`-lauseesta. Lambdan voi tallentaa muuttujaan ja kutsua kuten
funktiota:

```{.cpp tiedosto="esimerkit/06-lambdat.cpp" osa="perus"}
```

Lambdojen tärkein käyttötarkoitus on antaa toimintaa parametrina
algoritmeille:

```{.cpp tiedosto="esimerkit/06-lambdat.cpp" osa="algoritmi"}
```

Ensimmäinen lambda on *predikaatti*, joka kertoo, lasketaanko alkio
mukaan. Toinen on vertailufunktio, joka järjestää luvut laskevaan
järjestykseen. `std::ranges`-nimiavaruuden algoritmeja käsitellään
tarkemmin luvussa [Algoritmit ja ranges](#algoritmit-ja-ranges).

### Yleiset lambdat

Kun parametrin tyypiksi kirjoitetaan `auto`, lambdasta tulee *yleinen*:
se toimii kaikilla tyypeillä, joille sen runko kääntyy. Kääntäjä
tuottaa oman versionsa jokaiselle käytetylle tyypille.

```{.cpp tiedosto="esimerkit/06-lambdat.cpp" osa="yleinen"}
```

## Sieppaukset

Hakasulkeissa luetellaan, mitkä ympäröivän näkyvyysalueen muuttujat
lambda *sieppaa* (*capture*) käyttöönsä:

| Sieppaus | Merkitys |
|----------|----------|
| `[]` | ei sieppauksia |
| `[x]` | `x` kopioidaan lambdan luontihetkellä |
| `[&x]` | `x`:ään viitataan |
| `[=]` | kaikki käytetyt muuttujat kopioidaan |
| `[&]` | kaikkiin käytettyihin muuttujiin viitataan |
| `[this]` | olion jäseniin viitataan osoittimen kautta |
| `[*this]` | olio kopioidaan lambdaan |
| `[n = lauseke]` | uusi muuttuja `n` alustetaan lausekkeella |

Kopio ja viittaus käyttäytyvät eri tavoin, jos muuttuja muuttuu lambdan
luomisen jälkeen:

```{.cpp tiedosto="esimerkit/06-sieppaus.cpp" osa="arvo-viittaus"}
```

Viittaussieppaus on vaarallinen, jos lambda elää pidempään kuin
muuttuja, johon se viittaa. Tällainen *roikkuva viittaus* syntyy
helposti, kun lambda palautetaan funktiosta tai annetaan toiselle
säikeelle. Näissä tilanteissa sieppaa arvolla.

Oletuksena arvolla siepatut muuttujat ovat lambdan sisällä vakioita.
Avainsana `mutable` sallii niiden muuttamisen. Seuraava lambda pitää
kirjaa kutsukerroista *alustussieppauksen* `n = 0` avulla:

```{.cpp tiedosto="esimerkit/06-sieppaus.cpp" osa="mutable"}
```

Kutsut on kirjoitettu omille riveilleen, koska funktion argumenttien
laskentajärjestys ei ole määrätty. Kutsu
`std::println("{} {} {}", f(), f(), f())` voi tulostaa luvut missä
järjestyksessä tahansa.

Alustussieppauksella voi myös siirtää lambdaan olion, jota ei voi
kopioida, kuten `std::unique_ptr`:n:

```{.cpp tiedosto="esimerkit/06-sieppaus.cpp" osa="siirto"}
```

Jäsenfunktiossa luotu lambda käyttää jäsenmuuttujia `this`-osoittimen
kautta. Sieppaus `[this]` tallentaa osoittimen, joten lambda näkee
olion myöhemmät muutokset ja roikkuu, jos olio tuhoutuu ensin.
`[*this]` tallentaa kopion koko oliosta:

```{.cpp tiedosto="esimerkit/06-sieppaus.cpp" osa="this"}
```

```{.cpp tiedosto="esimerkit/06-sieppaus.cpp" osa="this-kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-sieppaus.odotettu"}
```

## Sulkeumat ja `std::function`

Funktio voi palauttaa lambdan, joka kantaa siepattua tilaa mukanaan.
Tällaista funktio-oliota kutsutaan *sulkeumaksi* (*closure*). Paluutyyppi
on kirjoitettava `auto`, koska jokaisella lambdalla on oma, nimetön
tyyppinsä.

```{.cpp tiedosto="esimerkit/06-lambdat.cpp" osa="tehdas"}
```

```{.cpp tiedosto="esimerkit/06-lambdat.cpp" osa="sulkeuma"}
```

Koska lambdojen tyypit ovat erilaisia, niitä ei voi sellaisenaan
tallentaa samaan säiliöön. `std::function<int(int)>` on tyyppi, johon
voi tallentaa minkä tahansa kutsuttavan olion, joka ottaa `int`:n ja
palauttaa `int`:n:

```{.cpp tiedosto="esimerkit/06-lambdat.cpp" osa="function"}
```

```{.tuloste tiedosto="esimerkit/06-lambdat.odotettu"}
```

`std::function` maksaa joustavuudestaan: kutsu kulkee epäsuoran
hypyn kautta, ja suuri sulkeuma voi vaatia muistinvarauksen. Kun
funktio-olio annetaan parametrina ja tyyppi tunnetaan käännösaikana,
mallipohjainen parametri (`auto` tai konsepti, ks. luku
[Mallit ja konseptit](#mallit-ja-konseptit)) on tehokkaampi.

## `[[nodiscard]]`

*Attribuutti* `[[nodiscard]]` kertoo, että funktion paluuarvon
huomiotta jättäminen on luultavasti virhe. Kääntäjä varoittaa, jos
arvoa ei käytetä:

```{.cpp tiedosto="esimerkit/06-nodiscard.ei-kaanny.cpp"}
```

Attribuutti sopii erityisesti funktioille, jotka palauttavat
virhekoodin tai uuden resurssin, sekä puhtaille funktioille, joiden
ainoa vaikutus on paluuarvo. Muita hyödyllisiä attribuutteja ovat
`[[maybe_unused]]`, joka vaimentaa käyttämättömän muuttujan varoituksen,
ja `[[fallthrough]]`, joka merkitsee `switch`-lauseen tarkoituksellisen
läpiputoamisen.

## Käytännössä

- **Algoritmi ja lambda nimeävät tarkoituksen.** `std::ranges::count_if`
  tai `any_of` kertoo lukijalle heti, mitä silmukka tekee. Käsin
  kirjoitettu silmukka on paikallaan, kun mikään algoritmi ei kuvaa
  tehtävää selvästi.
- **Sieppaukset luetellaan.** `[&]` on turvallinen vain lambdassa, joka
  suoritetaan heti ja paikallisesti, kuten algoritmin argumenttina.
  Lambda, joka tallennetaan, palautetaan tai annetaan säikeelle, sieppaa
  eksplisiittisesti ja mieluiten arvolla. Jäsenmuuttujiin viitataan
  `this`-osoittimen kautta, joten `[=]` ei kopioi niitä. C++20 merkitsi
  `this`-osoittimen implisiittisen sieppauksen `[=]`:llä vanhentuneeksi:
  GCC ja Clang varoittavat siitä, ja tarkoitus kirjoitetaan näkyviin
  muodossa `[=, this]` tai `[*this]`.
- **Heti kutsuttu lambda alustaa vakion.** Kun arvon laskeminen vaatii
  useita lauseita, `const auto arvo = [&] { ... }();` pitää tuloksen
  vakiona ilman muuttuvia apumuuttujia. Mallia kutsutaan nimellä *IIFE*
  (*immediately invoked function expression*).
- **Takaisinkutsun tyyppi valitaan käytön mukaan.** Malliparametri
  (`auto` tai konsepti) on nopein, koska kutsu voidaan sisällyttää.
  `std::function` tarvitaan, kun eri lambdoja tallennetaan samaan
  säiliöön tai luokan jäseneksi. Joka kutsussa maksetaan epäsuora hyppy, ja
  suuri sulkeuma voi varata muistia.
- **Tulos palautetaan, ei tulosparametrissa.** Paluuarvon kopio poistetaan
  tai se siirretään, joten `Tulos laske(...)` on yhtä tehokas kuin
  `void laske(..., Tulos& ulos)` ja selvempi. Useampi arvo palautetaan
  rakenteena tai parina (C++ Core Guidelines F.20, F.21).
- **Tallennettava parametri otetaan arvona ja siirretään.** Lukemiseen
  riittää `const T&`, mutta jos funktio tallentaa argumentin, se ottaa
  parametrin arvona ja siirtää sen paikalleen (luku
  [Siirtosemantiikka](#siirtosemantiikka)).
- **`[[nodiscard]]` virheille ja resursseille.** Funktio, jonka
  paluuarvon unohtaminen on lähes varmasti virhe, merkitään. Merkinnän voi
  antaa myös tyypille, jolloin se koskee kaikkia sen palauttavia
  funktioita.

## Itsearviointi

- Osaat valita funktion parametrien ja paluuarvon tyypit ja perustella,
  miksi suuren olion palauttaminen arvona on tehokasta.
- Osaat kirjoittaa lambdan, joka sieppaa muuttujia arvolla, viittauksella
  ja alustussieppauksella, ja valita näistä oikean.
- Osaat tunnistaa roikkuvan viittaussieppauksen vaaran.
- Osaat valita takaisinkutsulle tyypin: malliparametri tai
  `std::function`.
- Osaat palauttaa useita arvoja ilman tulosparametreja.
