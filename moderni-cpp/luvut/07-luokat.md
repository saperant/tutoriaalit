# Luokat {.runko-omat-tyypit}

Luku [Luokan perusteet](#luokan-perusteet) esitteli luokan syntaksin.
Tässä luvussa on kyse luokan suunnittelusta: milloin tyypistä tehdään
luokka, miten kääntäjä saadaan estämään virheellinen käyttö ja mitkä
operaatiot kääntäjä osaa tuottaa itse. Järjestys etenee yksittäisestä
tyypistä luokkahierarkiaan ja lopuksi arvotyyppien vertailuun ja
tulostamiseen.

## Rakenne vai luokka

Tyyppi, jonka kentät voivat saada mitä tahansa arvoja toisistaan
riippumatta, on selkein *rakenteena* (`struct`) julkisine kenttineen:
piste, väri tai asetusjoukko. Jos kenttien välillä on invariantti,
kuten murtoluvun nollasta poikkeava nimittäjä tai puskurin koon ja
osoittimen vastaavuus, tyypistä tehdään *luokka* (`class`): kentät
ovat yksityisiä, muodostin saattaa invariantin voimaan ja jokainen
julkinen jäsenfunktio säilyttää sen (C++ Core Guidelines C.2).

Jako kertoo lukijalle, mitä tyypiltä voi odottaa. Rakenteen voi alustaa
ja muuttaa kenttä kerrallaan. Luokan olio on aina kelvollinen, ja sen
tila muuttuu vain rajapinnan kautta.

## `explicit`

Muodostin, jota voi kutsua yhdellä argumentilla, toimii oletuksena myös
automaattisena tyyppimuunnoksena: funktiolle, joka odottaa `Metrit`-oliota,
kelpaisi pelkkä `double`. Usein se ei ole toivottavaa, koska muunnos
piilottaa virheitä. Avainsana `explicit`
estää automaattisen muunnoksen:

```{.cpp tiedosto="esimerkit/07-explicit.ei-kaanny.cpp"}
```

Hyvä oletus on merkitä yksiparametriset muodostimet aina `explicit`,
ellei automaattiselle muunnokselle ole selvää syytä.

## Erikoisjäsenfunktiot: `= default` ja `= delete`

Kääntäjä voi tuottaa luokalle oletusmuodostimen, kopio- ja
siirtomuodostimen, kopio- ja siirtosijoituksen sekä hajottimen.
*Kopiomuodostin* `T(const T&)` luo uuden olion toisen kopiona, ja
*kopiosijoitus* `operator=(const T&)` korvaa olemassa olevan olion
sisällön. Kääntäjän tuottamat versiot kopioivat jäsenet yksi kerrallaan,
mikä on oikein aina, kun jäsenet ovat itse arvoja.
Merkinnällä `= default` pyydetään oletustoteutusta eksplisiittisesti ja
merkinnällä `= delete` estetään funktion käyttö kokonaan:

```{.cpp tiedosto="esimerkit/07-kopiointi.ei-kaanny.cpp"}
```

Poistettua funktiota kutsuva koodi ei käänny. Tämä on parempi kuin
vanha tapa esitellä kopiomuodostin yksityiseksi ja jättää se
määrittelemättä, sillä virheilmoitus on selkeä ja tulee aina
käännösaikana. Kopioinnin estäminen on luontevaa luokille, jotka
edustavat yksilöllistä resurssia, kuten verkkoyhteyttä. Tällainen luokka
voi silti olla *siirrettävä*; siirtämistä käsitellään luvussa
[Siirtosemantiikka](#siirtosemantiikka).

## Periytyminen: `override` ja `final`

*Periytyminen* ilmaisee, että johdettu luokka on kantaluokan erikoistapaus:
ympyrä on muoto. Kantaluokka esittelee rajapinnan *virtuaalifunktioina*
(`virtual`). Kun virtuaalifunktiota kutsutaan kantaluokan viittauksen tai
osoittimen kautta, suoritettava toteutus valitaan ajon aikana olion
todellisen tyypin mukaan. Tätä kutsutaan *dynaamiseksi sidonnaksi*.
Merkintä `= 0` tekee funktiosta *puhtaan virtuaalifunktion*, jolla ei ole
toteutusta kantaluokassa. Tällaisesta *abstraktista luokasta* ei voi luoda
olioita.

Virtuaalifunktioita käyttävän luokkahierarkian kantaluokalla on oltava
virtuaalinen hajotin, jotta olio tuhoutuu oikein kantaluokan osoittimen
kautta. `= default` riittää toteutukseksi.

```{.cpp tiedosto="esimerkit/07-muodot.cpp" osa="kanta"}
```

Johdettu luokka esitellään muodossa `class Ympyra : public Muoto`, ja
se perii kantaluokan jäsenet. Korvaava funktio merkitään `override`. Jos
nimessä, parametreissa tai `const`-määreessä on virhe eikä funktio
siksi korvaakaan kantaluokan funktiota, kääntäjä ilmoittaa siitä.
Ilman merkintää syntyisi hiljaa uusi, erillinen funktio.

`final` estää periytymisen luokasta tai funktion korvaamisen edelleen.
Esimerkissä on myös *delegoiva muodostin*, joka kutsuu saman luokan
toista muodostinta, ja jäsenten alustuslista aaltosulkein.

```{.cpp tiedosto="esimerkit/07-muodot.cpp" osa="johdetut"}
```

Olioita käsitellään kantaluokan älykkäiden osoittimien kautta.
`std::unique_ptr` vapauttaa olion automaattisesti, kun vektori
tuhoutuu; tähän palataan seuraavassa luvussa. Olioita ei voi tallentaa
vektoriin arvoina, koska kantaluokan tyyppiseen muuttujaan mahtuu vain
kantaluokan osa (viipaloituminen, luku [C++ kokeneelle](#c-kokeneelle)).

```{.cpp tiedosto="esimerkit/07-muodot.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-muodot.odotettu"}
```

Vakio `std::numbers::pi` tulee C++20:n otsikosta `<numbers>`, ja se
korvaa epästandardin makron `M_PI`.

## Vertailut: `operator<=>`

Arvotyypiltä odotetaan, että sen olioita voi vertailla ja järjestää.
Vertailuoperaattorit voi kirjoittaa käsin (luku
[Luokan perusteet](#luokan-perusteet)), mutta useimmiten kääntäjä
tuottaa ne. C++20:n *kolmisuuntainen vertailuoperaattori* `<=>` (*spaceship
operator*) korvaa kuusi erillistä vertailuoperaattoria. Kun se
määritellään oletukseksi (`= default`), kääntäjä tuottaa
vertailut, jotka käyvät jäsenet läpi esittelyjärjestyksessä:

```{.cpp tiedosto="esimerkit/07-versio.cpp" osa="luokka"}
```

Oletuksena määritelty `<=>` tuottaa myös yhtäsuuruusvertailun `==`.
Lauseke `a < b` muunnetaan muotoon `(a <=> b) < 0`, ja `a != b`
muotoon `!(a == b)`.

## Omat tyypit `std::format`-muotoilussa

Jotta omaa tyyppiä voi käyttää `std::format`- ja `std::print`-kutsuissa,
sille määritellään `std::formatter`-erikoistus. Helpointa on periä
olemassa oleva muotoilija ja muuntaa arvo ensin merkkijonoksi. Näin
leveys- ja tasausmääreet toimivat kuten merkkijonoille.

```{.cpp tiedosto="esimerkit/07-versio.cpp" osa="muotoilija"}
```

```{.cpp tiedosto="esimerkit/07-versio.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-versio.odotettu"}
```

Versio 1.4.2 on pienempi kuin 1.10.0, koska vertailu tehdään
kokonaislukuina jäsen kerrallaan eikä merkkijonoina.

## Vahvat tyypit

Kun funktio ottaa useita samantyyppisiä parametreja, kuten metrejä ja
sekunteja `double`-arvoina, ne on helppo antaa väärässä järjestyksessä.
*Vahva tyyppi* (*strong type*) on kääre, joka antaa arvolle merkityksen.
Kääntäjä torjuu sekoittamisen, eikä kääre maksa ajoaikana mitään.

```{.cpp tiedosto="esimerkit/07-vahvat-tyypit.ei-kaanny.cpp" osa="tyypit"}
```

```{.cpp tiedosto="esimerkit/07-vahvat-tyypit.ei-kaanny.cpp" osa="kaytto"}
```

Väärässä järjestyksessä annetut argumentit ovat käännösvirhe. Korjattu
ohjelma tulostaa:

```{.tuloste tiedosto="esimerkit/07-vahvat-tyypit.odotettu"}
```

Tyhjät tunnistetyypit `MetritTagi` ja `SekunnitTagi` erottavat muuten
samanlaiset tyypit toisistaan. Mallia käytetään laajasti esimerkiksi
yksikkökirjastoissa ja tunnisteissa, kuten `Kayttajatunnus` ja
`Tilausnumero`.

## Käytännössä

- **`struct` ilman invariantteja, `class` invarianttien kanssa.** Valinta
  kertoo lukijalle, saako kenttiä muuttaa vapaasti.
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
- **Vahva tyyppi samantyyppisille parametreille.** Kun rajapinnassa on
  useita `double`- tai `int`-parametreja, joilla on eri merkitys,
  yksikölle tai tunnisteelle tehdään oma tyyppi.

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
