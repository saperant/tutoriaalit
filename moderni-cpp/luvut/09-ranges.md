# Algoritmit ja ranges

Otsikon `<algorithm>` algoritmit, kuten `sort`, `find` ja `count_if`,
ovat olleet C++:ssa alusta asti. Ne ottivat kuitenkin parametreikseen
iteraattoriparin, mikä teki kutsuista pitkiä:
`std::sort(v.begin(), v.end())`. C++20:n *ranges*-kirjasto toi
algoritmeista versiot, jotka ottavat koko säiliön, sekä *näkymät*, joilla
käsittelyvaiheita voi ketjuttaa.

## Algoritmit ja projektiot

Nimiavaruuden `std::ranges` algoritmit ottavat säiliön suoraan.
Lisäksi niille voi antaa *projektion*: funktion tai jäsenosoittimen,
joka poimii alkiosta vertailtavan arvon.

```{.cpp tiedosto="esimerkit/08-algoritmit.cpp" osa="tyyppi"}
```

```{.cpp tiedosto="esimerkit/08-algoritmit.cpp" osa="projektio"}
```

Kutsun `std::ranges::sort(ihmiset, {}, &Henkilo::ika)` toinen argumentti
`{}` on vertailufunktio, joka jätetään oletukseksi (`std::ranges::less`),
ja kolmas on projektio. Vertailufunktiota ei tarvitse kirjoittaa itse
vain siksi, että halutaan järjestää jonkin jäsenen mukaan.

```{.cpp tiedosto="esimerkit/08-algoritmit.cpp" osa="muut"}
```

```{.tuloste tiedosto="esimerkit/08-algoritmit.odotettu"}
```

Valmiin algoritmin käyttö on lähes aina parempi kuin oma silmukka:
nimi kertoo tarkoituksen, eikä rajaehtoihin pääse syntymään virheitä.

## Näkymät

*Näkymä* (*view*) on kevyt olio, joka esittää toisen alkiojonon
muunnettuna, suodatettuna tai rajattuna kopioimatta alkioita. Näkymiä
yhdistellään putkioperaattorilla `|`:

```{.cpp tiedosto="esimerkit/08-nakymat.cpp" osa="putki"}
```

Putki luetaan vasemmalta oikealle: otetaan luvut, valitaan parilliset ja
korotetaan ne toiseen. Näkymiä voi myös tuottaa tyhjästä.
`std::views::iota(1)` on päättymätön jono 1, 2, 3, …, josta
`take(5)` ottaa viisi ensimmäistä:

```{.cpp tiedosto="esimerkit/08-nakymat.cpp" osa="tehtaat"}
```

C++23:n `std::ranges::to` kokoaa näkymän alkiot säiliöön. Säiliön
alkiotyyppi päätellään näkymästä:

```{.cpp tiedosto="esimerkit/08-nakymat.cpp" osa="to"}
```

### Laiska laskenta

Näkymät ovat *laiskoja*: alkiot lasketaan vasta, kun niitä luetaan, ja
vain niin monta kuin tarvitaan. Siksi päättymätön jono on mahdollinen.

```{.cpp tiedosto="esimerkit/08-laiska.cpp" osa="laiska"}
```

```{.tuloste tiedosto="esimerkit/08-laiska.odotettu"}
```

Näkymän luominen ei laske mitään. Muunnos suoritetaan kunkin alkion
kohdalla vasta, kun silmukka pyytää sitä, ja neljättä alkiota ei lasketa
lainkaan.

Laiskuudella on hintansa: näkymä viittaa alkuperäiseen dataan. Jos
näkymä on olemassa pidempään kuin säiliö, johon se viittaa, se on
roikkuva samaan tapaan kuin `string_view`. Näkymä kannattaa käyttää
heti tai muuttaa säiliöksi `std::ranges::to`-funktiolla.

### C++23:n uudet näkymät

C++23 lisäsi useita käytännöllisiä näkymiä. `enumerate` liittää
alkioihin järjestysnumeron, `zip` kulkee useamman jonon läpi rinnakkain
ja `chunk` jakaa jonon kiinteän kokoisiin paloihin:

```{.cpp tiedosto="esimerkit/08-nakymat.cpp" osa="cpp23"}
```

`split` jakaa jonon erottimen kohdalta. Kukin pala on alijono, josta
voi muodostaa `string_view`-olion:

```{.cpp tiedosto="esimerkit/08-nakymat.cpp" osa="split"}
```

Koko esimerkin tuloste:

```{.tuloste tiedosto="esimerkit/08-nakymat.odotettu"}
```

Muita hyödyllisiä näkymiä ovat esimerkiksi `drop`, `take_while`,
`keys`, `values`, `join`, `slide` ja `adjacent`.
