# Virheenkäsittely {.runko-virheet}

Kotlinissa ei ole tarkistettuja poikkeuksia. Funktio voi heittää minkä
tahansa poikkeuksen ilman `throws`-määrettä, eikä kutsujaa pakoteta
käsittelemään sitä. Kielen suunnittelijat perustelivat valintaa
Javan kokemuksella: tarkistetut poikkeukset johtivat tyhjiin
`catch`-lohkoihin ja käärimiseen, eivät parempaan virheenkäsittelyyn.
Tämän vuoksi virheet jaetaan Kotlinissa kahteen ryhmään:

- **Ohjelmointivirheet ja ympäristön häiriöt** ovat poikkeuksia:
  rikottu sopimus, puuttuva tiedosto, katkennut yhteys.
- **Odotetut, toimialaan kuuluvat virheet** ovat arvoja: haku ei
  löytänyt, syöte ei kelpaa, saldo ei riitä. Ne ilmaistaan tyypillä
  (`T?` tai suljettu tulostyyppi), jolloin kääntäjä valvoo niiden
  käsittelyn.

## Poikkeukset ja sopimukset

| Funktio | Poikkeus | Käyttö |
|---------|----------|--------|
| `require(ehto) { "viesti" }` | `IllegalArgumentException` | kutsujan virhe: argumentti ei kelpaa |
| `check(ehto) { "viesti" }` | `IllegalStateException` | olion tila ei salli operaatiota |
| `error("viesti")` | `IllegalStateException` | mahdoton tilanne; tyyppi `Nothing` |
| `requireNotNull`, `checkNotNull` | samat | null-väite selkeällä viestillä |
| `TODO("syy")` | `NotImplementedError` | keskeneräinen haara |

`try` on lauseke, ja `catch`-haarat ovat tyyppikohtaisia kuten
Javassa. Poikkeus käärii alkuperäisen syyn (`cause`), kun matalan
tason virhe muunnetaan sovelluksen virheeksi.

```{.kotlin tiedosto="esimerkit/09-virheet.kt"}
```

```{.tuloste tiedosto="esimerkit/09-virheet.odotettu"}
```

- `runCatching { }` palauttaa `Result<T>`-arvon, jolla on
  `getOrNull`, `getOrElse`, `map`, `fold` ja `onFailure`. Se sopii
  ohjelman reunalle, jossa kaikki virheet muutetaan raportiksi.
- `runCatching` sieppaa **kaikki** poikkeukset, myös ohjelmointivirheet
  ja korutiinien peruutuksen (`CancellationException`, luku 12).
  Sovelluslogiikan sisällä siksi siepataan nimetyt poikkeustyypit.

Käsittelemätön poikkeus kaataa ohjelman ja tulostaa pinon. Hyvin
kirjoitettu `require`-viesti kertoo, mikä sopimus rikkoutui:

```{.kotlin tiedosto="esimerkit/09-ehto.kaatuu.kt"}
```

```
1700
Exception in thread "main" java.lang.IllegalArgumentException:
    alennusprosentti 150 ei ole 0..100
	at _09_ehto_kaatuuKt.alennus(09-ehto.kaatuu.kt:5)
	at _09_ehto_kaatuuKt.main(09-ehto.kaatuu.kt:13)
```

## Virheet tyyppeinä

Kun virheitä on useita lajeja ja kutsujan on reagoitava niihin eri
tavoin, suljettu tulostyyppi kertoo vaihtoehdot tyypissä. Kääntäjä
valvoo `when`-lausekkeella, että jokainen vaihtoehto käsitellään.

```{.kotlin tiedosto="esimerkit/09-tulos.kt"}
```

```{.tuloste tiedosto="esimerkit/09-tulos.odotettu"}
```

`Sahkoposti`-arvoluokan konstruktori on yksityinen, joten
`Sahkoposti`-arvo on olemassa vain, jos jäsennys onnistui. Tätä mallia
kutsutaan nimellä *parse, don't validate*: syöte jäsennetään kerran
reunalla tyypiksi, jonka olemassaolo takaa kelvollisuuden, eikä sitä
tarvitse tarkistaa uudelleen syvemmällä.

## Käytännössä

- **Valitse virheen esitys kutsujan tarpeen mukaan.** Jos syy ei
  kiinnosta, `T?` riittää. Jos syitä on useita ja niihin reagoidaan eri
  tavoin, suljettu tulostyyppi. Jos virhe on ohjelmointivirhe tai
  harvinainen ympäristön häiriö, poikkeus.
- **`require` argumenteille, `check` tilalle.** Viestissä kerrotaan arvo
  ja odotus. Ne dokumentoivat sopimuksen koodissa.
- **Kääri matalan tason poikkeus omaksi ja säilytä syy.** Ylempi kerros
  näkee `AsetusVirhe`-tyypin eikä tiedostojärjestelmän yksityiskohtia,
  mutta pino säilyy vianetsintää varten.
- **`runCatching` vain reunalla.** Pääohjelmassa, pyyntökäsittelijässä
  tai komentorivityökalun ylimmällä tasolla. Älä niele poikkeusta
  hiljaa.
- **Hinta:** JVM:n poikkeuksen luonti tallentaa pinon, mikä on kallista
  syvässä kutsupinossa. Siksi odotettu virhe on arvo eikä poikkeus,
  ja poikkeuksia ei käytetä ohjausrakenteena.
- **Sudenkuoppa:** `@Throws(IOException::class)` tarvitaan, jos
  Java-koodi kutsuu Kotlin-funktiota ja haluaa siepata tarkistetun
  poikkeuksen. Muuten Javan kääntäjä ei salli `catch (IOException e)`
  -lohkoa.

## Itsearviointi

- Osaat valita poikkeuksen, nullable-paluuarvon ja suljetun tulostyypin
  välillä ja perustella valinnan.
- Osaat käyttää funktioita `require`, `check`, `error` ja
  `requireNotNull` sopimusten ilmaisemiseen.
- Osaat kääriä poikkeuksen syineen ja käsitellä virheet ohjelman
  reunalla `runCatching`-funktiolla.
- Osaat toteuttaa *parse, don't validate* -mallin yksityisellä
  konstruktorilla ja tehdasfunktiolla.
