# Rinnakkaisuus {.runko-rinnakkaisuus}

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

```{.cpp tiedosto="esimerkit/16-saikeet.cpp" osa="jthread"}
```

```{.tuloste tiedosto="esimerkit/16-saikeet.odotettu"}
```

Lambda sieppaa vektorit `luvut` ja `osasummat` viittauksina, joten
niiden on elettävä säikeitä pidempään. Siksi ne on määritelty ennen
säiliötä `tyontekijat`: oliot tuhotaan käänteisessä
määrittelyjärjestyksessä, joten `jthread`-oliot odottavat säikeensä
loppuun ennen kuin vektorit tuhoutuvat. Jos viitattu muuttuja
määriteltäisiin säiliön jälkeen, se tuhoutuisi ensin ja säikeet
lukisivat vapautettua muistia. Säikeelle annettavan lambdan sieppaukset
luetellaan siksi yksitellen, ja jokaisen viittauksen kohdalla
tarkistetaan, että kohde elää säiettä pidempään.

## Kilpatilanteet, lukot ja atomiset muuttujat

Jos kaksi säiettä käsittelee samaa muistipaikkaa samanaikaisesti ja
ainakin toinen kirjoittaa, syntyy *kilpatilanne* (*data race*), joka on
määrittelemätöntä käyttäytymistä. Jaettu data suojataan joko lukolla
tai tekemällä siitä atominen.

`std::mutex` on lukko, jonka vain yksi säie voi kerrallaan omistaa.
Sitä ei lukita ja vapauteta käsin, vaan RAII-olion `std::scoped_lock`
avulla, joka vapauttaa lukon myös poikkeustilanteessa. `scoped_lock`
osaa lukita useita mutexeja kerralla ilman lukkiutumisvaaraa.

```{.cpp tiedosto="esimerkit/16-lukitus.cpp" osa="mutex"}
```

Lukko on `mutable`, jotta sen voi lukita myös `const`-metodissa:
lukitseminen ei muuta olion havaittavaa tilaa.

Yksinkertaiselle laskurille lukko on raskas. `std::atomic<int>` takaa,
että esimerkiksi `++laskuri` suoritetaan jakamattomana operaationa:

```{.cpp tiedosto="esimerkit/16-lukitus.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/16-lukitus.odotettu"}
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

```{.cpp tiedosto="esimerkit/16-pysaytys.cpp" osa="pysaytys"}
```

```{.tuloste tiedosto="esimerkit/16-pysaytys.odotettu"}
```

`std::latch` (C++20) on kertakäyttöinen laskuri, jonka avulla säikeet
voivat odottaa toisiaan. Tässä pääsäie odottaa, että työntekijä on
ehtinyt käynnistyä, ennen kuin se pyytää lopettamista. Näin ohjelman
tuloste on aina sama.

## Ehtomuuttujat ja työjono

Lukko suojaa jaettua tilaa, mutta sillä ei voi odottaa, että tila
muuttuu. Säie, joka odottaa työtä tyhjästä jonosta, tarvitsee
*ehtomuuttujan* (`std::condition_variable`). Sen `wait`-funktio
vapauttaa lukon, nukkuu, kunnes toinen säie kutsuu funktiota
`notify_one` tai `notify_all`, ja ottaa lukon takaisin ennen paluuta.
`wait` voi herätä myös ilman ilmoitusta (*spurious wakeup*), joten sille
annetaan predikaatti, jonka se tarkistaa lukon alla jokaisen heräämisen
jälkeen. Ehtomuuttuja vaatii lukoksi `std::unique_lock`in, jonka voi
vapauttaa ja lukita uudelleen.

Yleisin rinnakkaisen ohjelman rakenne on *työjono* (*tuottaja–kuluttaja*):
tuottajat lisäävät töitä, ja kiinteä joukko kuluttajasäikeitä käsittelee
niitä. Seuraava jono voidaan sulkea, jolloin kuluttajat käsittelevät
jäljellä olevat työt ja lopettavat:

```{.cpp tiedosto="esimerkit/16-tyojono.cpp" osa="jono"}
```

```{.cpp tiedosto="esimerkit/16-tyojono.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/16-tyojono.odotettu"}
```

Jonon tila on yhden lukon takana, ja ehtomuuttuja herättää kuluttajat.
Funktion `ota` predikaatti päästää säikeen jatkamaan, kun jonossa on
työ tai jono on suljettu. Sulkeminen on ainoa tapa kertoa kuluttajille,
että töitä ei enää tule, ja se ratkaisee siistin lopetuksen ilman
erillisiä lippuja. Ilmoitus annetaan lukon ulkopuolella, jottei herätetty
säie joudu heti odottamaan lukkoa. Esimerkki on testattu myös
ThreadSanitizerilla.

## Tehtävät: `std::async`

Usein säiettä ei tarvita sinänsä, vaan halutaan laskea jotain
taustalla ja saada tulos myöhemmin. `std::async` käynnistää tehtävän ja
palauttaa `std::future`-olion, jonka `get`-metodi odottaa tulosta. Jos
tehtävä heittää poikkeuksen, `get` heittää sen uudelleen kutsujan
säikeessä.

```{.cpp tiedosto="esimerkit/16-async.cpp" osa="funktiot"}
```

```{.cpp tiedosto="esimerkit/16-async.cpp" osa="async"}
```

```{.tuloste tiedosto="esimerkit/16-async.odotettu"}
```

Käynnistystapa `std::launch::async` vaatii, että tehtävä suoritetaan
omassa säikeessään. Ilman sitä toteutus saa lykätä suorituksen
`get`-kutsuun asti, jolloin rinnakkaisuutta ei synny.

Standardikirjaston algoritmeista on myös rinnakkaiset versiot, joille
annetaan suoritusmääre kuten `std::execution::par`. GCC:n toteutus
käyttää niihin Intelin TBB-kirjastoa, joka on asennettava erikseen.
C++26 tuo laajemman, *sender/receiver*-malliin perustuvan
`std::execution`-kirjaston.

## Käytännössä

- **Ensin korkean tason välineet.** Rinnakkaiset algoritmit,
  `std::async` ja säiepoolit kirjoitetaan ennen omia säikeitä. Säikeen
  luominen on kallis operaatio, joten pitkäikäiset työntekijät ja
  työjonot ovat tavallisin rakenne.
- **Jaa olemalla jakamatta.** Paras synkronointi on se, jota ei tarvita:
  jokainen säie käsittelee omaa dataansa, ja tulokset yhdistetään
  lopuksi, kuten luvun summaesimerkissä.
- **Lukko mahdollisimman lyhyeksi ajaksi.** Lukon pitäen ei kutsuta
  tuntematonta koodia, kuten takaisinkutsuja, koska se voi yrittää ottaa
  saman tai toisen lukon. Useat lukot otetaan yhdellä
  `std::scoped_lock`illa lukkiutumisen välttämiseksi.
- **Ehtomuuttuja aina ehdon kanssa.** Odotukselle annetaan aina
  predikaatti, ja ehdon muuttava säie tekee muutoksen lukon alla ennen
  ilmoitusta. Muuten ilmoitus voi mennä ohi juuri ennen odotuksen alkua.
- **Atomiset muuttujat laskureille ja lipuille.** Monimutkaisempi jaettu
  tila suojataan lukolla. Muistijärjestys jätetään oletukseksi
  (`seq_cst`), ellei sen heikentämiselle ole mitattua syytä.
- **Väärä jakaminen.** Kaksi säiettä, jotka kirjoittavat eri muuttujiin
  samalla välimuistirivillä, hidastavat toisiaan (*false sharing*).
  Kuumat laskurit sijoitetaan eri riveille, esimerkiksi
  `alignas(std::hardware_destructive_interference_size)`. Ilmiön
  mittaamista käsittelevät taidot *C++:n suorituskyky* ja
  *Rinnakkaisohjelmointi*.
- **ThreadSanitizer jatkuvaan integraatioon.** Kilpatilanteet ilmenevät
  satunnaisesti, joten testit ajetaan säännöllisesti ThreadSanitizerin
  kanssa.

## Itsearviointi

- Osaat käynnistää säikeitä `std::jthread`illä ja pysäyttää ne
  `stop_token`illa.
- Osaat suojata jaetun tilan `std::scoped_lock`illa ja tunnistaa, milloin
  atominen muuttuja riittää.
- Osaat toteuttaa työjonon ehtomuuttujalla ja sulkea sen hallitusti.
- Osaat käynnistää taustatehtävän `std::async`illa ja käsitellä sen
  tuloksen ja poikkeuksen `std::future`n kautta.
- Osaat perustella, miksi säikeen käyttämien olioiden on elettävä säiettä
  pidempään, ja varmistaa sen määrittelyjärjestyksellä.
