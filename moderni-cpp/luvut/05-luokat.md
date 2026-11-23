# Luokat {.runko-omat-tyypit}

C++:n luokkamalli on pysynyt pohjimmiltaan samana, mutta uudet
standardit ovat vähentäneet toistuvaa koodia ja tehneet aikeista
näkyvämpiä.

## Vertailut: `operator<=>`

C++20:n *kolmisuuntainen vertailuoperaattori* `<=>` (*spaceship
operator*) korvaa kuusi erillistä vertailuoperaattoria. Kun se
määritellään oletukseksi (`= default`), kääntäjä tuottaa
vertailut, jotka käyvät jäsenet läpi esittelyjärjestyksessä:

```{.cpp tiedosto="esimerkit/05-versio.cpp" osa="luokka"}
```

Oletuksena määritelty `<=>` tuottaa myös yhtäsuuruusvertailun `==`.
Lauseke `a < b` muunnetaan muotoon `(a <=> b) < 0`, ja `a != b`
muotoon `!(a == b)`.

## Omat tyypit `std::format`-muotoilussa

Jotta omaa tyyppiä voi käyttää `std::format`- ja `std::print`-kutsuissa,
sille määritellään `std::formatter`-erikoistus. Helpointa on periä
olemassa oleva muotoilija ja muuntaa arvo ensin merkkijonoksi. Näin
leveys- ja tasausmääreet toimivat kuten merkkijonoille.

```{.cpp tiedosto="esimerkit/05-versio.cpp" osa="muotoilija"}
```

```{.cpp tiedosto="esimerkit/05-versio.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-versio.odotettu"}
```

Versio 1.4.2 on pienempi kuin 1.10.0, koska vertailu tehdään
kokonaislukuina jäsen kerrallaan eikä merkkijonoina.

## Erikoisjäsenfunktiot: `= default` ja `= delete`

Kääntäjä voi tuottaa luokalle oletusmuodostimen, kopio- ja
siirtomuodostimen, kopio- ja siirtosijoituksen sekä hajottimen.
Merkinnällä `= default` pyydetään oletustoteutusta eksplisiittisesti ja
merkinnällä `= delete` estetään funktion käyttö kokonaan:

```{.cpp tiedosto="esimerkit/05-kopiointi.ei-kaanny.cpp"}
```

Poistettua funktiota kutsuva koodi ei käänny. Tämä on parempi kuin
vanha tapa esitellä kopiomuodostin yksityiseksi ja jättää se
määrittelemättä, sillä virheilmoitus on selkeä ja tulee aina
käännösaikana. Kopioinnin estäminen on luontevaa luokille, jotka
edustavat yksilöllistä resurssia, kuten verkkoyhteyttä. Tällainen luokka
voi silti olla *siirrettävä*; siirtämistä käsitellään luvussa
[Siirtosemantiikka](#siirtosemantiikka).

## `explicit`

Yksiparametrinen muodostin toimii oletuksena myös automaattisena
tyyppimuunnoksena. Usein se ei ole toivottavaa. Avainsana `explicit`
estää automaattisen muunnoksen:

```{.cpp tiedosto="esimerkit/05-explicit.ei-kaanny.cpp"}
```

Hyvä oletus on merkitä yksiparametriset muodostimet aina `explicit`,
ellei automaattiselle muunnokselle ole selvää syytä.

## Periytyminen: `override` ja `final`

Virtuaalifunktioita käyttävän luokkahierarkian kantaluokalla on oltava
virtuaalinen hajotin, jotta olio tuhoutuu oikein kantaluokan osoittimen
kautta. `= default` riittää toteutukseksi.

```{.cpp tiedosto="esimerkit/05-muodot.cpp" osa="kanta"}
```

Johdetussa luokassa korvaava funktio merkitään `override`. Jos
nimessä, parametreissa tai `const`-määreessä on virhe eikä funktio
siksi korvaakaan kantaluokan funktiota, kääntäjä ilmoittaa siitä.
Ilman merkintää syntyisi hiljaa uusi, erillinen funktio.

`final` estää periytymisen luokasta tai funktion korvaamisen edelleen.
Esimerkissä on myös *delegoiva muodostin*, joka kutsuu saman luokan
toista muodostinta, ja jäsenten alustuslista aaltosulkein.

```{.cpp tiedosto="esimerkit/05-muodot.cpp" osa="johdetut"}
```

Olioita käsitellään kantaluokan älykkäiden osoittimien kautta.
`std::unique_ptr` vapauttaa olion automaattisesti, kun vektori
tuhoutuu; tähän palataan seuraavassa luvussa.

```{.cpp tiedosto="esimerkit/05-muodot.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-muodot.odotettu"}
```

Vakio `std::numbers::pi` tulee C++20:n otsikosta `<numbers>`, ja se
korvaa epästandardin makron `M_PI`.

## Käytännössä

- **`struct` ilman invariantteja, `class` invarianttien kanssa.** Jos
  kentät voivat saada mitä tahansa arvoja, rakenne julkisine kenttineen on
  selkein. Jos arvojen välillä on sääntö, kuten "nimittäjä ei ole nolla",
  kentät ovat yksityisiä ja muodostin varmistaa säännön (Core Guidelines
  C.2).
- **Pieni julkinen rajapinta.** Operaatio, joka ei tarvitse yksityisiä
  kenttiä, kirjoitetaan tavalliseksi funktioksi luokan ulkopuolelle. Se
  vahvistaa kapselointia: mitä vähemmän koodia näkee kentät, sitä
  helpompi niitä on muuttaa.
- **Monimuotoisen kantaluokan kopiointi estetään.** Virtuaalisen
  hajottimen lisäksi kantaluokka merkitsee kopiomuodostimen ja
  -sijoituksen poistetuiksi, jolloin olion viipaloituminen (luku
  [C++ kokeneelle](#c-kokeneelle)) on käännösvirhe.
- **Koostaminen ennen periytymistä.** Periytyminen kytkee luokat
  tiukasti. Jos tarkoituksena on käyttää toisen luokan toteutusta, se
  otetaan jäseneksi. Periytyminen on tarkoitettu monimuotoisuuteen.
- **Arvotyypeille `<=>` ja muotoilija.** Oletuksena määritelty `<=>`
  tekee tyypistä järjestettävän ja vertailtavan, ja `std::formatter`
  tekee siitä tulostettavan ja lokitettavan.

### Vahvat tyypit

Kun funktio ottaa useita samantyyppisiä parametreja, kuten metrejä ja
sekunteja `double`-arvoina, ne on helppo antaa väärässä järjestyksessä.
*Vahva tyyppi* (*strong type*) on kääre, joka antaa arvolle merkityksen.
Kääntäjä torjuu sekoittamisen, eikä kääre maksa ajoaikana mitään.

```{.cpp tiedosto="esimerkit/05-vahvat-tyypit.ei-kaanny.cpp" osa="tyypit"}
```

```{.cpp tiedosto="esimerkit/05-vahvat-tyypit.ei-kaanny.cpp" osa="kaytto"}
```

Väärässä järjestyksessä annetut argumentit ovat käännösvirhe. Korjattu
ohjelma tulostaa:

```{.tuloste tiedosto="esimerkit/05-vahvat-tyypit.odotettu"}
```

Tyhjät tunnistetyypit `MetritTagi` ja `SekunnitTagi` erottavat muuten
samanlaiset tyypit toisistaan. Mallia käytetään laajasti esimerkiksi
yksikkökirjastoissa ja tunnisteissa, kuten `Kayttajatunnus` ja
`Tilausnumero`.

## Itsearviointi

- Osaat päättää, tuleeko tyypistä rakenne julkisine kenttineen vai
  luokka yksityisine kenttineen.
- Osaat määritellä arvotyypin vertailut `<=>`-operaattorilla ja
  muotoilijan `std::format`ia varten.
- Osaat estää kopioinnin ja automaattiset muunnokset (`= delete`,
  `explicit`).
- Osaat kirjoittaa monimuotoisen luokkahierarkian, jossa on virtuaalinen
  hajotin, `override` ja estetty kopiointi.
- Osaat tehdä vahvan tyypin, joka estää samantyyppisten parametrien
  sekoittamisen.
