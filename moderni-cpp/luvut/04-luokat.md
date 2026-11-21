# Luokat

C++:n luokkamalli on pysynyt pohjimmiltaan samana, mutta uudet
standardit ovat vähentäneet toistuvaa koodia ja tehneet aikeista
näkyvämpiä.

## Vertailut: `operator<=>`

C++20:n *kolmisuuntainen vertailuoperaattori* `<=>` (*spaceship
operator*) korvaa kuusi erillistä vertailuoperaattoria. Kun se
määritellään oletukseksi (`= default`), kääntäjä tuottaa
vertailut, jotka käyvät jäsenet läpi esittelyjärjestyksessä:

```{.cpp tiedosto="esimerkit/04-versio.cpp" osa="luokka"}
```

Oletuksena määritelty `<=>` tuottaa myös yhtäsuuruusvertailun `==`.
Lauseke `a < b` muunnetaan muotoon `(a <=> b) < 0`, ja `a != b`
muotoon `!(a == b)`.

## Omat tyypit `std::format`-muotoilussa

Jotta omaa tyyppiä voi käyttää `std::format`- ja `std::print`-kutsuissa,
sille määritellään `std::formatter`-erikoistus. Helpointa on periä
olemassa oleva muotoilija ja muuntaa arvo ensin merkkijonoksi. Näin
leveys- ja tasausmääreet toimivat kuten merkkijonoille.

```{.cpp tiedosto="esimerkit/04-versio.cpp" osa="muotoilija"}
```

```{.cpp tiedosto="esimerkit/04-versio.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/04-versio.odotettu"}
```

Versio 1.4.2 on pienempi kuin 1.10.0, koska vertailu tehdään
kokonaislukuina jäsen kerrallaan eikä merkkijonoina.

## Erikoisjäsenfunktiot: `= default` ja `= delete`

Kääntäjä voi tuottaa luokalle oletusmuodostimen, kopio- ja
siirtomuodostimen, kopio- ja siirtosijoituksen sekä hajottimen.
Merkinnällä `= default` pyydetään oletustoteutusta eksplisiittisesti ja
merkinnällä `= delete` estetään funktion käyttö kokonaan:

```{.cpp tiedosto="esimerkit/04-kopiointi.ei-kaanny.cpp"}
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

```{.cpp tiedosto="esimerkit/04-explicit.ei-kaanny.cpp"}
```

Hyvä oletus on merkitä yksiparametriset muodostimet aina `explicit`,
ellei automaattiselle muunnokselle ole selvää syytä.

## Periytyminen: `override` ja `final`

Virtuaalifunktioita käyttävän luokkahierarkian kantaluokalla on oltava
virtuaalinen hajotin, jotta olio tuhoutuu oikein kantaluokan osoittimen
kautta. `= default` riittää toteutukseksi.

```{.cpp tiedosto="esimerkit/04-muodot.cpp" osa="kanta"}
```

Johdetussa luokassa korvaava funktio merkitään `override`. Jos
nimessä, parametreissa tai `const`-määreessä on virhe eikä funktio
siksi korvaakaan kantaluokan funktiota, kääntäjä ilmoittaa siitä.
Ilman merkintää syntyisi hiljaa uusi, erillinen funktio.

`final` estää periytymisen luokasta tai funktion korvaamisen edelleen.
Esimerkissä on myös *delegoiva muodostin*, joka kutsuu saman luokan
toista muodostinta, ja jäsenten alustuslista aaltosulkein.

```{.cpp tiedosto="esimerkit/04-muodot.cpp" osa="johdetut"}
```

Olioita käsitellään kantaluokan älykkäiden osoittimien kautta.
`std::unique_ptr` vapauttaa olion automaattisesti, kun vektori
tuhoutuu; tähän palataan seuraavassa luvussa.

```{.cpp tiedosto="esimerkit/04-muodot.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/04-muodot.odotettu"}
```

Vakio `std::numbers::pi` tulee C++20:n otsikosta `<numbers>`, ja se
korvaa epästandardin makron `M_PI`.
