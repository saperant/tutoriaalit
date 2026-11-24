# Säikeet ja tehtävät

Säie on käyttöjärjestelmän vuorontama suoritusvirta, joka jakaa prosessin
muistin muiden säikeiden kanssa. C++:n `std::thread` ja `std::jthread`
ovat ohuita kääreitä käyttöjärjestelmän säikeiden päällä: Linuxissa
jokainen niistä on POSIX-säie ja ytimen kannalta oma tehtävänsä. Tämä
luku käsittelee säikeiden käytännön yksityiskohdat, jotka *Moderni C++*
ohittaa: argumenttien välityksen, säiekohtaiset muuttujat, poikkeukset,
pysäytyksen ja `std::async`in käynnistyspolitiikat.

## Argumentit ja elinajat

Säikeen konstruktori kopioi tai siirtää funktion ja argumentit säikeen
omaan tallennustilaan. Näin säie ei viittaa kutsujan pinoon, joka voi
kadota ennen kuin säie ehtii alkaa. Jos funktio ottaa viittauksen,
viittaus on pyydettävä erikseen `std::ref`illä. Siirrettävät, kopioimattomat
oliot kuten `std::unique_ptr` siirretään `std::move`lla:

```{.cpp tiedosto="esimerkit/02-argumentit.cpp" osa="funktiot"}
```

```{.cpp tiedosto="esimerkit/02-argumentit.cpp" osa="valitys"}
```

Ilman `std::ref`iä koodi ei kääntyisi lainkaan, koska kopio (oikea arvo)
ei sido ei-vakioon viittaukseen. Kääntäjä estää siis yleisimmän virheen.
Lambdat ovat vaarallisempia, koska ne sieppaavat viittauksen
kysymättä: `[&]` kelpaa kääntäjälle, vaikka viitattu olio tuhoutuisi ennen
säiettä. *Moderni C++* kertoo tällaisesta virheestä, ja luvussa
*Atomiset operaatiot* on toinen. Säännöt:

- Säikeelle annettavan lambdan sieppaukset luetellaan nimeltä.
- Jokaisen viitatun olion on elettävä säiettä pidempään. `jthread`-oliot
  määritellään siksi *viittamiensa olioiden jälkeen*, jolloin ne
  tuhoutuvat (ja odottavat säikeensä) ensin.
- Arvot, joita säie vain lukee ja jotka ovat pieniä, siepataan arvoina.

### Säiekohtaiset muuttujat

`thread_local`-muuttujasta on jokaisella säikeellä oma kopionsa, joka
luodaan säikeen alkaessa (tai ensimmäisellä käytöllä) ja tuhotaan sen
päättyessä:

```{.cpp tiedosto="esimerkit/02-argumentit.cpp" osa="saiekohtainen"}
```

```{.cpp tiedosto="esimerkit/02-argumentit.cpp" osa="tl-kaytto"}
```

```{.tuloste tiedosto="esimerkit/02-argumentit.odotettu"}
```

Säiekohtaiset muuttujat sopivat välimuisteihin, satunnaislukugeneraattoreihin
ja tilastolaskureihin, jotka yhdistetään lopuksi. Niiden käyttö maksaa
hieman enemmän kuin tavallisen globaalin muuttujan (osoite haetaan
säikeen tallennuslohkosta), ja dynaamisesti ladattavissa kirjastoissa
hieman lisää. Säiepoolissa säiekohtainen tila säilyy tehtävästä toiseen,
mikä on joko etu tai virhelähde.

## Poikkeukset säikeissä

Jos poikkeus karkaa säikeen funktiosta, ohjelma päättyy kutsuun
`std::terminate`. Poikkeus ei siis siirry automaattisesti säikeen
luojalle. Sen voi siirtää käsin kolmella tavalla:

```{.cpp tiedosto="esimerkit/02-poikkeukset.cpp" osa="exception-ptr"}
```

`std::exception_ptr` on viittauslaskettu kahva poikkeusolioon.
`std::current_exception` ottaa käsiteltävän poikkeuksen talteen, ja
`std::rethrow_exception` heittää sen uudelleen toisessa säikeessä.
`std::promise` tekee saman valmiiksi: arvo tai poikkeus asetetaan
lupaukseen, ja vastaava `std::future` palauttaa arvon tai heittää
poikkeuksen, kun sitä kysytään:

```{.cpp tiedosto="esimerkit/02-poikkeukset.cpp" osa="promise"}
```

`std::packaged_task` käärii funktion niin, että sen paluuarvo tai
poikkeus menee automaattisesti futureen. Se on säiepoolin rakennuspala:

```{.cpp tiedosto="esimerkit/02-poikkeukset.cpp" osa="paketti"}
```

```{.tuloste tiedosto="esimerkit/02-poikkeukset.odotettu"}
```

Future on kertakäyttöinen: `get` siirtää arvon ulos, ja toinen kutsu on
virhe. Jos tulosta tarvitsee useampi säie, `share()` tekee siitä
`std::shared_future`n, jota voi kopioida ja lukea monta kertaa.

## Pysäyttäminen

Säiettä ei voi turvallisesti tappaa ulkoapäin: se voi pitää lukkoa,
olla kesken tietorakenteen päivityksen tai omistaa resursseja. Ainoa
turvallinen tapa on pyytää säiettä lopettamaan ja antaa sen tehdä se
hallitusti. C++20:n `std::stop_source` ja `std::stop_token` ovat tällainen
yhteistyöhön perustuva pysäytysmekanismi, ja `std::jthread` tarjoaa
sellaisen jokaiselle säikeelleen. Hajotin pyytää pysäytystä ennen kuin
odottaa säikeen loppuun.

Säie, joka odottaa työtä ehtomuuttujalla, ei kuitenkaan huomaa pyyntöä,
ellei odotus herää siihen. `std::condition_variable_any` osaa odottaa
myös `stop_token`ia:

```{.cpp tiedosto="esimerkit/02-pysaytys.cpp" osa="tyontekija"}
```

Odotus palauttaa predikaatin arvon. Jos pysäytystä on pyydetty mutta
töitä on vielä jonossa, `wait` palauttaa `true`, ja käsittelijä jatkaa,
kunnes jono on tyhjä. Näin pysäytys ei hukkaa töitä.

`std::stop_callback` rekisteröi funktion, joka ajetaan, kun pysäytystä
pyydetään. Sillä voi esimerkiksi sulkea soketin, jonka lukemiseen säie on
jumittunut:

```{.cpp tiedosto="esimerkit/02-pysaytys.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/02-pysaytys.odotettu"}
```

Esimerkin ensimmäisessä versiossa kutsua `request_stop()` ei ollut. Silloin
`ilmoitus` tuhoutui ensin, koska se oli määritelty säikeen jälkeen, ja
takaisinkutsu poistui ennen kuin `jthread`in hajotin ehti pyytää
pysäytystä. Testi huomasi, että takaisinkutsua ei ajettu.

## Tehtävät: `std::async`

`std::async` ajaa funktion ja palauttaa futuren. Käynnistyspolitiikka
määrää, miten:

```{.cpp tiedosto="esimerkit/02-async.cpp" osa="politiikat"}
```

- `std::launch::async` ajaa funktion "kuin uudessa säikeessä". Toteutus
  saa käyttää poolia, mutta säiekohtaisten muuttujien on käyttäydyttävä
  kuin säie olisi uusi. libstdc++ luo aina uuden säikeen.
- `std::launch::deferred` ei luo säiettä. Funktio ajetaan vasta, kun
  futurelta kysytään tulosta, ja silloin kysyjän säikeessä.
- Oletus `async | deferred` antaa toteutuksen valita. Sitä ei kannata
  käyttää, koska ohjelman käytös (rinnakkainen vai ei, mikä säie,
  `wait_for`in tulos) riippuu valinnasta.

`std::async`illa on myös erikoisuus, joka yllättää:

```{.cpp tiedosto="esimerkit/02-async.cpp" osa="sudenkuoppa"}
```

```{.tuloste tiedosto="esimerkit/02-async.odotettu"}
```

`async`in palauttaman futuren hajotin odottaa tehtävän loppuun. Jos
futurea ei tallenneta, väliaikainen olio tuhoutuu heti, ja "taustalle"
lähetetty tehtävä ajetaan itse asiassa synkronisesti. Muualta saatujen
futurejen (esimerkiksi `promise`n) hajotin ei odota.

## Säikeen hinta

Säikeen luominen ja odottaminen maksaa Linuxissa tyypillisesti
kymmeniä mikrosekunteja, ja jokainen säie varaa pinolle oletuksena
8 MiB virtuaalimuistia (fyysistä muistia vain käytetyille sivuille).
Lyhyet tehtävät eivät siksi kannata omaa säiettä, vaan ne annetaan
pitkäikäisille työntekijöille. Seuraava luku rakentaa sellaisen poolin.

`std::thread::hardware_concurrency()` kertoo laitteistosäikeiden määrän.
Se on vihje, ei lupaus: arvo voi olla 0 (tuntematon), ja kontissa tai
cgroupin rajoittamana prosessi saa usein vähemmän suoritinaikaa kuin
ytimiä on. Testit eivät saa olettaa mitään tiettyä ydinmäärää.

## Käytännössä

- **`std::jthread` on oletus.** Se odottaa ja pysäyttää säikeensä
  hajottimessa. Pelkkää `std::thread`iä ei käytetä uudessa koodissa,
  ja `detach` on lähes aina virhe: irrotettu säie voi elää pidempään kuin
  data, jota se käyttää, ja ohjelman lopussa se katkeaa kesken.
- **Määrittelyjärjestys on elinaikojen järjestys.** Säikeet ja
  pysäytystakaisinkutsut määritellään viimeisinä, jotta ne tuhoutuvat
  ensimmäisinä. Sama pätee luokan jäseniin.
- **Virheet kulkevat futureissa.** Säikeen poikkeus otetaan kiinni
  säikeessä ja välitetään `promise`n, `packaged_task`in tai
  `exception_ptr`n kautta. Säikeen funktiosta karkaava poikkeus kaataa
  ohjelman.
- **Pysäytys on yhteistyötä.** Pitkään odottavan säikeen on odotettava
  myös pysäytyspyyntöä (`condition_variable_any` ja `stop_token`) tai
  takaisinkutsun on herätettävä se.
- **Tallenna `async`in future.** Muuten tehtävä ajetaan peräkkäin.
  Käytä politiikkaa `std::launch::async` eksplisiittisesti.

## Itsearviointi

- Osaat välittää säikeelle arvon, viittauksen ja siirrettävän olion ja
  tunnistat sieppauksen, joka elää säiettä lyhyemmän ajan.
- Osaat siirtää säikeen poikkeuksen kutsujalle `std::exception_ptr`llä,
  `std::promise`lla ja `std::packaged_task`illa.
- Osaat pysäyttää ehtomuuttujaa odottavan säikeen `stop_token`illa ja
  kertoa, milloin `stop_callback` ajetaan.
- Osaat kertoa `std::async`in käynnistyspolitiikkojen erot ja miksi
  tallentamaton future tekee tehtävästä synkronisen.
