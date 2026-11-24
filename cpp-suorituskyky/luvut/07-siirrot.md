# Siirrot ja kopioiden poisto

Siirtosemantiikka tekee arvojen palauttamisesta ja säiliöön
lisäämisestä halpaa, ja kopioiden poisto (engl. copy elision) tekee
siitä usein ilmaista. Säännöt ovat kuitenkin hienovaraisia: yksi
`std::move` väärässä paikassa estää kopion poiston, ja yksi
väliaikainen merkkijono rajapinnassa varaa muistia jokaisessa
kutsussa. Siirtojen perusteet ja viiden sääntö ovat taidossa *Moderni
C++*; tässä luvussa lasketaan, montako oliota todella syntyy.

Laskeva tyyppi kirjaa rakentamiset, kopiot ja siirrot:

```{.cpp tiedosto="esimerkit/seuranta.hpp" osa="seurattava"}
```

## Paluuarvot

C++17:stä alkaen *prvalue*, eli väliaikainen arvo kuten
`Seurattava{"raportti"}`, ei ole olio ennen kuin se sijoitetaan
johonkin. Palautettu prvalue rakennetaan suoraan kutsujan muuttujaan:
kopion poisto on pakollinen eikä vaadi edes kopio- tai
siirtokonstruktoria.

```{.cpp tiedosto="esimerkit/07-paluuarvot.cpp" osa="prvalue"}
```

Nimetty paikallinen muuttuja on eri asia. *NRVO* (named return value
optimization) on sallittu mutta ei pakollinen: kääntäjä saa rakentaa
muuttujan suoraan kutsujan tilaan, jos palautettava muuttuja on
yksikäsitteinen.

```{.cpp tiedosto="esimerkit/07-paluuarvot.cpp" osa="nrvo"}
```

Kun NRVO ei ole mahdollinen, paluu siirtää automaattisesti
(*implisiittinen siirto*): paikallinen muuttuja tai parametri
käsitellään paluulausekkeessa rvalue-arvona.

```{.cpp tiedosto="esimerkit/07-paluuarvot.cpp" osa="kaksi"}
```

Paikallisen olion jäsen ei kuitenkaan ole paikallinen muuttuja, joten
se kopioidaan:

```{.cpp tiedosto="esimerkit/07-paluuarvot.cpp" osa="jasen"}
```

```{.cpp tiedosto="esimerkit/07-paluuarvot.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-paluuarvot.odotettu"}
```

Jäsenen tapauksessa siirto syntyy parin rakentamisesta ja kopio
paluusta. Sen voi korjata kirjoittamalla `return
std::move(pari.first);`, koska jäsenen siirtäminen on nyt
tarkoituksellista. Viimeinen rivi muistuttaa, että sijoitus olemassa
olevaan muuttujaan ei ole kopion poistoa vaan siirtosijoitus: vanha
arvo vapautetaan ja uusi siirretään.

## `return std::move(x)` estää NRVO:n

Yleinen virhe on "auttaa" kääntäjää siirtämällä paluuarvo itse:

```{.cpp tiedosto="esimerkit/07-pessimointi.ei-kaanny.cpp" osa="pessimointi"}
```

`std::move(tulos)` on lauseke, ei muuttujan nimi, joten NRVO ei ole
enää mahdollinen, ja tuloksena on siirto siellä, missä ilman sitä ei
olisi mitään. GCC ja Clang varoittavat (`-Wpessimizing-move`, mukana
`-Wall`issa), ja tämän tutoriaalin `-Werror` estää käännöksen.
Korjattu versio:

```{.tuloste tiedosto="esimerkit/07-pessimointi.odotettu"}
```

Sama koskee paluutyyppiä `T&&`: funktion, joka palauttaa paikallisen
muuttujan rvalue-viittauksena, tulos on roikkuva viittaus. Palauta aina
arvo.

## `emplace` ja `try_emplace`

`push_back(T{...})` rakentaa väliaikaisen olion ja siirtää sen.
`emplace_back(argumentit)` rakentaa olion suoraan vektorin muistiin:

```{.cpp tiedosto="esimerkit/07-emplace.cpp" osa="vektori"}
```

```{.cpp tiedosto="esimerkit/07-emplace.cpp" osa="kartta"}
```

```{.tuloste tiedosto="esimerkit/07-emplace.odotettu"}
```

Olemassa olevan olion kanssa `emplace_back` ja `push_back` ovat samat:
molemmat kopioivat. Ero on vain silloin, kun annetaan
rakentimen argumentit. Kartoissa `try_emplace` on vielä parempi: se ei
rakenna mitään, jos avain on jo olemassa, kun taas `insert` ja
`emplace` saavat rakentaa parin ensin ja hylätä sen.

`emplace_back` kutsuu rakenninta suoraan, myös `explicit`-rakenninta,
joten se ohittaa tyyppitarkistuksen: `std::vector<std::vector<int>>
v; v.emplace_back(1000000);` kääntyy ja varaa miljoonan alkion
vektorin. `push_back` on siksi turvallisempi oletus, kun lisättävä arvo
on jo olemassa.

## Näkymät rajapinnoissa

Funktio, joka ottaa parametrin `const std::string&`, pakottaa kutsujan
rakentamaan `std::string`in, vaikka kutsujalla olisi merkkijonoliteraali,
`std::string_view` tai osa toisesta merkkijonosta. Sama koskee
`const std::vector<T>&` -parametria ja `std::array`ta:

```{.cpp tiedosto="esimerkit/07-nakymat.cpp" osa="merkkijono"}
```

```{.cpp tiedosto="esimerkit/07-nakymat.cpp" osa="span"}
```

```{.cpp tiedosto="esimerkit/07-nakymat.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-nakymat.odotettu"}
```

`std::string_view` ja `std::span` ovat kaksi sanaa: osoitin ja pituus.
Ne välitetään arvona rekistereissä, eikä niiden kautta lukeminen maksa
mitään viittaukseen verrattuna. Ne sopivat parametreiksi, jotka vain
luetaan. Jos funktio tallentaa merkkijonon, parametrin kannattaa olla
`std::string` arvona ja tallennuksen `std::move`: kutsuja voi silloin
siirtää oman merkkijononsa ilman kopiota.

## Elinaika

Näkymä ei omista dataa, joten sen on elettävä lyhyemmän aikaa kuin
data. *Moderni C++* näytti näkymän väliaikaiseen merkkijonoon. Hankalampi
tapaus syntyy optimoinnista: näkymät tallennetaan vektorin
merkkijonoihin, ja vektori kasvaa.

```{.cpp tiedosto="esimerkit/07-elinaika.kaatuu.cpp" osa="roikkuva"}
```

```{.tuloste tiedosto="esimerkit/07-elinaika.virhe"}
```

Kasvaessaan vektori siirtää merkkijonot uuteen puskuriin. Pitkän
merkkijonon siirto siirtää vain osoittimen, joten näkymä sen merkkeihin
pysyisi kelvollisena, mutta lyhyt merkkijono on olion sisällä, ja sen
merkit kopioidaan. Vanha puskuri vapautetaan, ja näkymä osoittaa
vapautettuun muistiin. Ohjelma toimii tai ei toimi merkkijonojen
pituuden mukaan, mikä tekee virheestä vaikean löytää. AddressSanitizer
löytää sen heti. Samat säännöt koskevat `std::span`ia ja
iteraattoreita: vektorin kasvu mitätöi kaiken, mikä osoittaa sen
alkioihin.

## Käytännössä

- **Palauta arvona**, älä viittauksena tai osoittimena ulostuloparametriin.
  Pakollinen kopion poisto ja NRVO tekevät paluusta ilmaisen.
- **Älä kirjoita `return std::move(paikallinen)`.** Kirjoita
  `std::move` vain, kun palautat jäsentä tai muuta, joka ei ole
  paikallinen muuttuja.
- **`emplace_back` rakentimen argumenteilla, `try_emplace` karttoihin.**
  Olemassa olevalle arvolle `push_back(std::move(x))`.
- **Lukuparametrit `std::string_view` ja `std::span`**, tallennettavat
  parametrit arvona ja `std::move`.
- **Älä säilytä näkymiä säiliön alkioihin**, jos säiliö voi muuttua.
  Tallenna indeksi tai käytä säiliötä, joka ei siirrä alkioitaan,
  kuten `std::deque`.

## Itsearviointi

- Osaat erottaa pakollisen kopion poiston, NRVO:n ja implisiittisen
  siirron ja ennustaa, montako kopiota ja siirtoa paluu tekee.
- Osaat selittää, miksi `return std::move(x)` hidastaa, ja tunnistaa
  varoituksen `-Wpessimizing-move`.
- Osaat valita `push_back`in, `emplace_back`in ja `try_emplace`n
  välillä.
- Osaat suunnitella rajapinnan näkymillä niin, ettei kutsuja joudu
  kopioimaan, ja tunnistaa näkymän elinaikavirheet.
