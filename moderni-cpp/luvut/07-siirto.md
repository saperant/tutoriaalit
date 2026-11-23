# Siirtosemantiikka

Ennen C++11:tä olion välittäminen arvona tarkoitti aina kopiointia.
Suuren vektorin palauttaminen funktiosta saattoi kopioida koko sisällön,
vaikka alkuperäinen tuhottiin heti perään. *Siirtosemantiikka* antaa
olion luovuttaa resurssinsa toiselle oliolle, kun alkuperäistä ei enää
tarvita.

## Lvalue- ja rvalue-arvot

Lausekkeet jaetaan karkeasti kahteen ryhmään:

- *lvalue* on nimetty olio, jolla on pysyvä sijainti, esimerkiksi
  muuttuja `x`. Sitä voi käyttää lausekkeen jälkeenkin.
- *rvalue* on väliaikainen arvo, esimerkiksi `x + 1` tai funktion
  palauttama olio. Sitä ei voi käyttää enää lausekkeen jälkeen, joten
  sen resurssit voi turvallisesti ottaa.

*Rvalue-viittaus* `T&&` sitoutuu vain rvalue-arvoihin. Sen avulla luokka
voi tarjota erillisen siirtomuodostimen, jota kutsutaan, kun lähde on
väliaikainen. `std::move` ei itse siirrä mitään: se on tyyppimuunnos,
joka merkitsee lvalue-arvon rvalue-arvoksi ja kertoo, että sen
resurssit saa ottaa.

## Viiden sääntö

Luokka, joka hallitsee resurssia itse, tarvitsee tavallisesti viisi
erikoisjäsenfunktiota: hajottimen, kopiomuodostimen, kopiosijoituksen,
siirtomuodostimen ja siirtosijoituksen. Tätä kutsutaan *viiden
säännöksi* (*rule of five*). Seuraava luokka hallitsee dynaamista
taulukkoa ja tulostaa, mitä tapahtuu:

```{.cpp tiedosto="esimerkit/06-puskuri.cpp" osa="luokka"}
```

Siirtomuodostin ei varaa muistia, vaan ottaa lähteen osoittimen ja
asettaa lähteen tyhjäksi. Funktio `std::exchange` asettaa uuden arvon ja
palauttaa vanhan. Lähde jää kelvolliseen tilaan, joten sen hajotin toimii
oikein.

Sijoitusoperaattori ottaa parametrinsa arvona. Kopio tai siirto
tehdään jo parametria alustettaessa, minkä jälkeen operaattori vain
vaihtaa sisällön. Tämä *copy-and-swap*-tekniikka hoitaa sekä kopio- että
siirtosijoituksen ja on turvallinen myös itseen sijoittaessa.

```{.cpp tiedosto="esimerkit/06-puskuri.cpp" osa="tehdas"}
```

```{.cpp tiedosto="esimerkit/06-puskuri.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-puskuri.odotettu"}
```

Kohdissa 4 ja 5 ei kutsuta kopio- eikä siirtomuodostinta. C++17 takaa
*kopion poiston* (*copy elision*): kun olio alustetaan samantyyppisestä
väliaikaisesta arvosta, olio rakennetaan suoraan lopulliseen
paikkaansa. Kun funktio palauttaa nimetyn paikallisen muuttujan
(`Puskuri p{100}; return p;`), poisto on sallittu muttei pakollinen;
käytännössä kääntäjät tekevät sen, ja muussa tapauksessa käytetään
siirtoa. Siksi paluuarvoon ei pidä kirjoittaa `std::move`, sillä se
estäisi kopion poiston.

Siirron jälkeen lähdeolio on standardikirjaston tyypeillä
"kelvollisessa mutta määrittelemättömässä tilassa". Sen voi tuhota tai
sille voi sijoittaa uuden arvon, mutta sen sisältöön ei pidä luottaa.

## Nollan sääntö

Viiden säännön toteuttaminen on työlästä ja virhealtista. Siksi
tavoitteena on *nollan sääntö* (*rule of zero*): luokan jäsenet ovat
tyyppejä, jotka hoitavat resurssinsa itse (`std::string`,
`std::vector`, `std::unique_ptr`), jolloin kääntäjän tuottamat
erikoisjäsenfunktiot toimivat oikein eikä yhtäkään tarvitse kirjoittaa.

Edellinen `Puskuri` olisi käytännössä vain `std::vector<int>`. Itse
toteutettu resurssinhallinta kannattaa rajata pieniin, yhden asian
luokkiin, joita muut luokat käyttävät jäseninään.

```{.cpp tiedosto="esimerkit/06-nollasaanto.cpp" osa="nolla"}
```

Metodi `lisaa` ottaa merkkijonon arvona ja siirtää sen vektoriin. Jos
kutsuja antaa nimetyn muuttujan, se kopioidaan parametriin kerran. Jos
kutsuja antaa väliaikaisen arvon, kopiota ei tehdä lainkaan. Yksi
funktio palvelee siis molempia tapauksia lähes optimaalisesti.

```{.cpp tiedosto="esimerkit/06-nollasaanto.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-nollasaanto.odotettu"}
```

Vektorin siirtäminen siirtää vain sisäisen osoittimen: alkiot pysyvät
samassa muistissa, ja siirto on vakioaikainen alkioiden määrästä
riippumatta.

## Siirto ja `noexcept`

Siirtomuodostin kannattaa merkitä `noexcept`, jos se ei voi heittää
poikkeusta. Merkinnällä on käytännön merkitystä: kun `std::vector`
joutuu kasvattamaan muistiaan, se siirtää alkiot uuteen muistiin vain,
jos siirto ei voi epäonnistua. Muuten se kopioi alkiot, jotta
poikkeuksen sattuessa alkuperäinen vektori säilyy ehjänä.

```{.cpp tiedosto="esimerkit/06-noexcept.cpp" osa="tyypit"}
```

```{.cpp tiedosto="esimerkit/06-noexcept.cpp" osa="kasvatus"}
```

```{.cpp tiedosto="esimerkit/06-noexcept.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-noexcept.odotettu"}
```

Kääntäjän tuottama siirtomuodostin on automaattisesti `noexcept`, jos
kaikkien jäsenten siirtomuodostimet ovat. Tämäkin puoltaa nollan
sääntöä.
