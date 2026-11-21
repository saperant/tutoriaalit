# Funktiot ja lambdat

## Lambdalausekkeet

*Lambdalauseke* määrittelee nimettömän funktio-olion siihen kohtaan,
jossa sitä tarvitaan. Sen yleinen muoto on

```text
[sieppaukset](parametrit) -> paluutyyppi { runko }
```

Paluutyypin voi yleensä jättää pois, jolloin kääntäjä päättelee sen
`return`-lauseesta. Lambdan voi tallentaa muuttujaan ja kutsua kuten
funktiota:

```{.cpp tiedosto="esimerkit/03-lambdat.cpp" osa="perus"}
```

Lambdojen tärkein käyttötarkoitus on antaa toimintaa parametrina
algoritmeille:

```{.cpp tiedosto="esimerkit/03-lambdat.cpp" osa="algoritmi"}
```

Ensimmäinen lambda on *predikaatti*, joka kertoo, lasketaanko alkio
mukaan. Toinen on vertailufunktio, joka järjestää luvut laskevaan
järjestykseen. `std::ranges`-nimiavaruuden algoritmeja käsitellään
tarkemmin luvussa [Algoritmit ja ranges](#algoritmit-ja-ranges).

### Yleiset lambdat

Kun parametrin tyypiksi kirjoitetaan `auto`, lambdasta tulee *yleinen*:
se toimii kaikilla tyypeillä, joille sen runko kääntyy. Kääntäjä
tuottaa oman versionsa jokaiselle käytetylle tyypille.

```{.cpp tiedosto="esimerkit/03-lambdat.cpp" osa="yleinen"}
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
| `[n = lauseke]` | uusi muuttuja `n` alustetaan lausekkeella |

Kopio ja viittaus käyttäytyvät eri tavoin, jos muuttuja muuttuu lambdan
luomisen jälkeen:

```{.cpp tiedosto="esimerkit/03-sieppaus.cpp" osa="arvo-viittaus"}
```

Viittaussieppaus on vaarallinen, jos lambda elää pidempään kuin
muuttuja, johon se viittaa. Tällainen *roikkuva viittaus* syntyy
helposti, kun lambda palautetaan funktiosta tai annetaan toiselle
säikeelle. Näissä tilanteissa sieppaa arvolla.

Oletuksena arvolla siepatut muuttujat ovat lambdan sisällä vakioita.
Avainsana `mutable` sallii niiden muuttamisen. Seuraava lambda pitää
kirjaa kutsukerroista *alustussieppauksen* `n = 0` avulla:

```{.cpp tiedosto="esimerkit/03-sieppaus.cpp" osa="mutable"}
```

Kutsut on kirjoitettu omille riveilleen, koska funktion argumenttien
laskentajärjestys ei ole määrätty. Kutsu
`std::println("{} {} {}", f(), f(), f())` voi tulostaa luvut missä
järjestyksessä tahansa.

Alustussieppauksella voi myös siirtää lambdaan olion, jota ei voi
kopioida, kuten `std::unique_ptr`:n:

```{.cpp tiedosto="esimerkit/03-sieppaus.cpp" osa="siirto"}
```

```{.tuloste tiedosto="esimerkit/03-sieppaus.odotettu"}
```

## Sulkeumat ja `std::function`

Funktio voi palauttaa lambdan, joka kantaa siepattua tilaa mukanaan.
Tällaista funktio-oliota kutsutaan *sulkeumaksi* (*closure*). Paluutyyppi
on kirjoitettava `auto`, koska jokaisella lambdalla on oma, nimetön
tyyppinsä.

```{.cpp tiedosto="esimerkit/03-lambdat.cpp" osa="tehdas"}
```

```{.cpp tiedosto="esimerkit/03-lambdat.cpp" osa="sulkeuma"}
```

Koska lambdojen tyypit ovat erilaisia, niitä ei voi sellaisenaan
tallentaa samaan säiliöön. `std::function<int(int)>` on tyyppi, johon
voi tallentaa minkä tahansa kutsuttavan olion, joka ottaa `int`:n ja
palauttaa `int`:n:

```{.cpp tiedosto="esimerkit/03-lambdat.cpp" osa="function"}
```

```{.tuloste tiedosto="esimerkit/03-lambdat.odotettu"}
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

```{.cpp tiedosto="esimerkit/03-nodiscard.ei-kaanny.cpp"}
```

Attribuutti sopii erityisesti funktioille, jotka palauttavat
virhekoodin tai uuden resurssin, sekä puhtaille funktioille, joiden
ainoa vaikutus on paluuarvo. Muita hyödyllisiä attribuutteja ovat
`[[maybe_unused]]`, joka vaimentaa käyttämättömän muuttujan varoituksen,
ja `[[fallthrough]]`, joka merkitsee `switch`-lauseen tarkoituksellisen
läpiputoamisen.
