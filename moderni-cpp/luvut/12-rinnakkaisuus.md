# Rinnakkaisuus

C++11 määritteli kielelle muistimallin ja toi standardikirjastoon säikeet,
lukot ja atomiset muuttujat. Sitä ennen säikeistys oli
alustakohtaisten kirjastojen varassa. C++20 lisäsi muun muassa
`std::jthread`-luokan ja pysäytysmekanismin.

## Säikeet: `std::jthread`

`std::jthread` (C++20) käynnistää säikeen, joka suorittaa annetun
funktion. Toisin kuin vanhempi `std::thread`, se odottaa säikeen
päättymistä hajottimessaan. `std::thread` kaataa ohjelman, jos säiettä
ei ole erikseen odotettu `join`-kutsulla tai irrotettu ennen hajotinta.
`jthread` on siis säikeiden RAII-kääre.

Seuraava ohjelma jakaa summan laskemisen neljälle säikeelle. Jokainen
säie kirjoittaa omaan alkioonsa, joten säikeet eivät käsittele samaa
muistipaikkaa eikä lukitusta tarvita:

```{.cpp tiedosto="esimerkit/12-saikeet.cpp" osa="jthread"}
```

```{.tuloste tiedosto="esimerkit/12-saikeet.odotettu"}
```

Esimerkin ensimmäisessä versiossa muuttuja `pala` oli määritelty
sisemmässä lohkossa säiliön `tyontekijat` *jälkeen*, ja lambda sieppasi
kaiken viittauksena (`[&, i]`). Koska oliot tuhotaan päinvastaisessa
järjestyksessä, `pala` tuhoutui ennen kuin `jthread`-oliot ehtivät
odottaa säikeitä, ja säikeet lukivat jo vapautettua muistia.
AddressSanitizer löysi virheen testeissä. Opetus: säikeille annettavissa
lambdoissa sieppaukset kannattaa luetella eksplisiittisesti ja tarkistaa,
että jokainen viitattu olio elää säiettä pidempään.

## Kilpatilanteet, lukot ja atomiset muuttujat

Jos kaksi säiettä käsittelee samaa muistipaikkaa samanaikaisesti ja
ainakin toinen kirjoittaa, syntyy *kilpatilanne* (*data race*), joka on
määrittelemätöntä käyttäytymistä. Jaettu data suojataan joko lukolla
tai tekemällä siitä atominen.

`std::mutex` on lukko, jonka vain yksi säie voi kerrallaan omistaa.
Sitä ei lukita ja vapauteta käsin, vaan RAII-olion `std::scoped_lock`
avulla, joka vapauttaa lukon myös poikkeustilanteessa. `scoped_lock`
osaa lukita useita mutexeja kerralla ilman lukkiutumisvaaraa.

```{.cpp tiedosto="esimerkit/12-lukitus.cpp" osa="mutex"}
```

Lukko on `mutable`, jotta sen voi lukita myös `const`-metodissa:
lukitseminen ei muuta olion havaittavaa tilaa.

Yksinkertaiselle laskurille lukko on raskas. `std::atomic<int>` takaa,
että esimerkiksi `++laskuri` suoritetaan jakamattomana operaationa:

```{.cpp tiedosto="esimerkit/12-lukitus.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/12-lukitus.odotettu"}
```

Ilman lukkoa tai atomisuutta laskurin lopputulos olisi satunnainen ja
ohjelman toiminta määrittelemätön. Tämän luvun esimerkit on testattu
myös ThreadSanitizerilla (`-fsanitize=thread`), joka havaitsee
kilpatilanteet ajon aikana.

## Pysäyttäminen

Säikeen pysäyttäminen ulkopuolelta on perinteisesti vaatinut oman
lippumuuttujan. `std::jthread` sisältää valmiin mekanismin: jos säikeen
funktio ottaa ensimmäisenä parametrinaan `std::stop_token`-olion, säie
voi kysyä siltä, onko lopettamista pyydetty. `jthread` pyytää
lopettamista automaattisesti hajottimessaan ennen odottamista.

```{.cpp tiedosto="esimerkit/12-pysaytys.cpp" osa="pysaytys"}
```

```{.tuloste tiedosto="esimerkit/12-pysaytys.odotettu"}
```

`std::latch` (C++20) on kertakäyttöinen laskuri, jonka avulla säikeet
voivat odottaa toisiaan. Tässä pääsäie odottaa, että työntekijä on
ehtinyt käynnistyä, ennen kuin se pyytää lopettamista. Näin ohjelman
tuloste on aina sama.

## Tehtävät: `std::async`

Usein säiettä ei tarvita sinänsä, vaan halutaan laskea jotain
taustalla ja saada tulos myöhemmin. `std::async` käynnistää tehtävän ja
palauttaa `std::future`-olion, jonka `get`-metodi odottaa tulosta. Jos
tehtävä heittää poikkeuksen, `get` heittää sen uudelleen kutsujan
säikeessä.

```{.cpp tiedosto="esimerkit/12-async.cpp" osa="funktiot"}
```

```{.cpp tiedosto="esimerkit/12-async.cpp" osa="async"}
```

```{.tuloste tiedosto="esimerkit/12-async.odotettu"}
```

Käynnistystapa `std::launch::async` vaatii, että tehtävä suoritetaan
omassa säikeessään. Ilman sitä toteutus saa lykätä suorituksen
`get`-kutsuun asti, jolloin rinnakkaisuutta ei synny.

Standardikirjaston algoritmeista on myös rinnakkaiset versiot, joille
annetaan suoritusmääre kuten `std::execution::par`. GCC:n toteutus
käyttää niihin Intelin TBB-kirjastoa, joka on asennettava erikseen.
C++26 tuo laajemman, *sender/receiver*-malliin perustuvan
`std::execution`-kirjaston.
