# Kokoelmat ja merkkijonot {.runko-kokoelmat}

Kotlinin kokoelmat ovat Javan kokoelmia (`ArrayList`, `LinkedHashMap`,
`HashSet`), mutta kieli näyttää ne kahden rajapinnan kautta: vain luku
(`List`, `Set`, `Map`) ja muokattava (`MutableList`, `MutableSet`,
`MutableMap`). Kokoelmien käsittely tehdään satojen valmiiden
laajennusfunktioiden avulla. Ne ovat `inline`-funktioita, joten
lambdoista ei synny olioita.

## Vain luku ei ole muuttumaton

| Luonti | Tyyppi | Toteutus |
|--------|--------|----------|
| `listOf(1, 2)` | `List<Int>` | Javan `Arrays.asList`, kiinteä koko |
| `mutableListOf()`, `ArrayList()` | `MutableList<T>` | `ArrayList` |
| `setOf`, `mutableSetOf` | `Set`, `MutableSet` | `LinkedHashSet`: lisäysjärjestys säilyy |
| `mapOf(a to 1)`, `mutableMapOf` | `Map`, `MutableMap` | `LinkedHashMap` |
| `buildList { add(...) }` | `List<T>` | rakennetaan muokattavana, palautetaan vain luku |
| `arrayOf`, `IntArray(n)` | `Array<T>`, `IntArray` | JVM:n taulukko; `IntArray` on `int[]` |

`List` on rajapinta, josta puuttuvat muokkausmetodit. Sama olio voi
silti muuttua toisen viittauksen kautta, ja Java-koodi voi muuttaa sitä
suoraan.

```{.kotlin tiedosto="esimerkit/07-kokoelmat.kt"}
```

```{.tuloste tiedosto="esimerkit/07-kokoelmat.odotettu"}
```

- Puolustava kopio (`toList()`, `toMap()`) tarvitaan, kun luokka
  tallentaa kutsujan antaman kokoelman eikä luota siihen, ettei sitä
  muuteta.
- `groupBy` palauttaa `Map<K, List<V>>`, `associateBy` avaimen ja olion
  parit ja `associate` vapaat parit. `partition` jakaa kahteen listaan.
- `compareBy { }.thenByDescending { }` kokoaa monen avaimen vertailijan
  ilman käsin kirjoitettua `compareTo`-logiikkaa.
- `maxBy` heittää poikkeuksen tyhjälle kokoelmalle; `maxByOrNull`
  palauttaa `null`. Sama pätee `first`/`firstOrNull`- ja
  `single`/`singleOrNull`-pareihin.
- `map[avain]` palauttaa nullable-arvon. `getValue` heittää poikkeuksen
  puuttuvasta avaimesta, `getOrDefault` ja `getOrElse` antavat
  oletuksen, `getOrPut` lisää puuttuvan.

## Käsittelyketjut

Raportointi on tyypillinen kokoelmafunktioiden käyttökohde. Seuraava
ohjelma jäsentää lokirivit säännöllisellä lausekkeella ja laskee
koosteet `groupingBy`-funktiolla, joka ei luo välilistoja ryhmille.

```{.kotlin tiedosto="esimerkit/07-lokit.kt"}
```

```{.tuloste tiedosto="esimerkit/07-lokit.syote"}
```

```{.tuloste tiedosto="esimerkit/07-lokit.odotettu"}
```

`destructured` purkaa säännöllisen lausekkeen ryhmät muuttujiksi.
`Regex` käännetään kerran tiedoston tason vakioksi, ei joka kutsulla.

## Sequence vs. List

Listan funktiot ovat innokkaita: jokainen vaihe käsittelee kaikki
alkiot ja tuottaa uuden listan. `Sequence` on laiska kuten Javan
`Stream`: alkio kulkee koko ketjun läpi ennen seuraavaa, ja päättävä
operaatio (`first`, `toList`, `count`) käynnistää laskennan.

```{.kotlin tiedosto="esimerkit/07-sekvenssit.kt"}
```

```{.tuloste tiedosto="esimerkit/07-sekvenssit.odotettu"}
```

Sekvenssi kannattaa, kun aineisto on suuri tai ääretön, ketju on pitkä
tai lopetetaan aikaisin (`first`, `take`). Pienellä listalla lista on
nopeampi, koska sekvenssin jokainen vaihe on olio ja virtuaalikutsu.
Sekvenssi lasketaan uudelleen jokaisella päättävällä operaatiolla, kuten
`collatz.count()` ja `collatz.max()` yllä.

## Merkkijonot

`String` on Javan muuttumaton merkkijono, jota Kotlin laajentaa
funktioilla `substringBefore/After`, `split`, `lines`, `trim`,
`padStart`, `removePrefix`, `toIntOrNull` ja monilla muilla.

```{.kotlin tiedosto="esimerkit/07-merkkijonot.kt"}
```

```{.tuloste tiedosto="esimerkit/07-merkkijonot.odotettu"}
```

`buildString` kokoaa merkkijonon `StringBuilder`-oliolla. `==` vertaa
sisältöä, ja `compareTo` vertaa UTF-16-arvoja, joten `ö` tulee `z`:n
jälkeen mutta ei suomen aakkosjärjestyksessä. Kieliherkkä järjestys
tarvitsee `java.text.Collator`-luokan.

## Käytännössä

- **Funktioketju silmukan tilalle**, kun jokainen vaihe on nimetty
  operaatio (`filter`, `map`, `groupBy`). Kun silmukassa on useita
  sivuvaikutuksia tai varhainen poistuminen monessa kohdassa, `for` on
  selkeämpi.
- **Julkinen rajapinta palauttaa vain luku -tyypin** (`List`, `Map`).
  Sisäinen tila voi olla `MutableList`, mutta sitä ei paljasteta:
  `val tapahtumat: List<T> get() = _tapahtumat` tai kopio.
- **`OrNull`-muodot ja elvis** tyhjien kokoelmien ja puuttuvien avainten
  käsittelyyn. Poikkeava muoto (`first`, `getValue`) vain, kun puute on
  ohjelmointivirhe.
- **Hinta:** jokainen listafunktio luo uuden listan. Kolmen vaiheen ketju
  miljoonalle alkiolle on kolme miljoonan alkion listaa; `asSequence()`
  poistaa välilistat.
- **Hinta:** `List<Int>` laatikoi jokaisen alkion. Numeerinen data
  kuuluu `IntArray`-, `LongArray`- ja `DoubleArray`-taulukoihin, joilla on
  samat kokoelmafunktiot.
- **Sudenkuoppa:** kokoelman muuttaminen sitä läpikäytäessä kaataa
  ohjelman. Käytä `removeAll { }`, `retainAll { }` tai uutta listaa:

```{.kotlin tiedosto="esimerkit/07-muokkaus.kaatuu.kt"}
```

```
Exception in thread "main" java.util.ConcurrentModificationException
	at java.base/java.util.ArrayList$Itr.checkForComodification(...)
```

## Itsearviointi

- Osaat selittää vain luku -rajapinnan ja muuttumattoman kokoelman
  eron ja tehdä puolustavan kopion.
- Osaat ryhmitellä, koostaa ja järjestää dataa kokoelmafunktioilla
  (`groupBy`, `groupingBy`, `associate`, `partition`, `compareBy`).
- Osaat valita listan ja sekvenssin välillä ja selittää, miten laiska
  arviointi etenee.
- Osaat jäsentää merkkijonoja `substringBefore`-, `split`- ja
  `Regex`-funktioilla ja koota tulosteen `buildString`-funktiolla.
