---
title: Kotlin
subtitle: Pikaopas Java-kehittäjälle · Kotlin 2.4, JDK 21
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Käännös | `kotlinc -Werror -include-runtime -d app.jar *.kt` |
| Ajo | `java -jar app.jar` |
| Skripti | `kotlin x.main.kts` |
| Gradle | `./gradlew build`, `run`, `test --continuous` |
| Tyyli, analyysi | `ktlint --format`, `detekt` |
| Kattavuus | Kover: `./gradlew koverHtmlReport` |
| Dokumentaatio | KDoc `/** [Nimi] @param @return */`, Dokka |
| Tavukoodi | `javap -c -p Luokka.class`, IntelliJ *Show Kotlin Bytecode* |

# Perussyntaksi

```{.kotlin tiedosto="esimerkit/pikaopas.kt" osa="perus"}
```

- `val` muuttumaton, `var` muuttuva; tyyppi päätellään.
- `if`, `when`, `try` ovat lausekkeita; ei ternääriä `a ? b : c`.
- Ei implisiittisiä muunnoksia: `n.toLong()`. Ylivuoto kiertää.
- Välit: `1..10`, `0..<n`, `10 downTo 0 step 2`, `x in a..b`.
- Pohjat: `"$x ${a.b}"`, raaka `"""..."""`.`trimIndent()`.

# Null

```{.kotlin tiedosto="esimerkit/pikaopas.kt" osa="null"}
```

| Rakenne | Merkitys |
|---------|----------|
| `x?.f()` | kutsu tai `null` |
| `x ?: y` | oletus; `?: return`, `?: throw` |
| `x?.let { }` | lohko ei-null-arvolle |
| `x as? T` | turvallinen muunnos |
| `requireNotNull(x) { }` | väite viestillä; `!!` vain perustellusti |
| `T!` | Javan alustatyyppi: ilmoita `T?` |

# Tyypit

```{.kotlin tiedosto="esimerkit/pikaopas.kt" osa="tyypit"}
```

- Luokat `final`; `open` sallii periytymisen, `override` pakollinen.
- `data class`: `equals`, `hashCode`, `toString`, `copy`, purku.
- `sealed` + `when` ilman `else`: kattavuus käännösajassa.
- `companion object` staattisten tilalla, `object` singleton.
- Näkyvyys: `public`, `internal` (moduuli), `protected`, `private`.
- Varianssi: `out T` tuottaa, `in T` kuluttaa; `List<*>`.

# Funktiot

```{.kotlin tiedosto="esimerkit/pikaopas.kt" osa="funktiot"}
```

| Scope | Olio | Palauttaa | Käyttö |
|-------|------|-----------|--------|
| `let` | `it` | lohkon arvo | nullable, muunnos |
| `run` | `this` | lohkon arvo | laske olion jäsenistä |
| `apply` | `this` | olio | alustus |
| `also` | `it` | olio | loki, tarkistus ketjussa |
| `with(x)` | `this` | lohkon arvo | monta kutsua |

# Kokoelmat

```{.kotlin tiedosto="esimerkit/pikaopas.kt" osa="kokoelmat"}
```

| Tarve | Funktio |
|-------|---------|
| muunnos, suodatus | `map`, `filter`, `mapNotNull`, `flatMap` |
| kooste | `sumOf`, `fold`, `count`, `maxByOrNull` |
| ryhmittely | `groupBy`, `groupingBy { }.eachCount()` |
| Map | `associate`, `associateBy`, `getOrPut`, `getValue` |
| jako | `partition`, `chunked`, `windowed`, `zip` |
| järjestys | `sortedBy`, `sortedWith(compareBy { }.thenBy { })` |
| laiska | `asSequence()`, `generateSequence`, `sequence { }` |
| kokoaminen | `buildList`, `buildMap`, `buildString` |

# Virheet ja muut

```{.kotlin tiedosto="esimerkit/pikaopas.kt" osa="muut"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

- `require` argumentille, `check` tilalle, `error` mahdottomalle.
- Odotettu virhe arvona (`T?`, suljettu tulos); `runCatching` reunalla.
- `use { }` jokaiselle `AutoCloseable`-oliolle.

# Korutiinit

| Rakenne | Tehtävä |
|---------|---------|
| `suspend fun` | voi keskeytyä varaamatta säiettä |
| `coroutineScope { }` | odottaa lapset, virhe peruu sisarukset |
| `launch`, `async`/`await` | käynnistä; tulos myöhemmin |
| `withContext(Dispatchers.IO)` | estävä I/O pois pääaltaasta |
| `withTimeoutOrNull(ms) { }` | aikaraja |
| `Mutex.withLock`, atomit | jaettu tila; ei `synchronized` |
| `Channel` | työjono korutiinien välillä, vastapaine |
| `Flow`, `StateFlow` | kylmä virta, tila |

# Hinnat

| Halpaa | Kallista |
|--------|----------|
| ylätason ja laajennusfunktiot | ei-inline-lambda (olio) |
| `inline`-kokoelmafunktiot | välilistat suurella datalla |
| `value class`, `IntArray` | `Int?`, `List<Int>` (laatikointi) |
| `data class`, `when` | poikkeus ohjausrakenteena |
| korutiini (pieni olio) | `runBlocking` korutiinissa |

# Sudenkuopat

- `List` on vain luku, ei muuttumaton; tee puolustava kopio.
- `==` on `equals`, `===` viittaus.
- Laajennus valitaan staattisen tyypin mukaan.
- `copy` on matala; `data class` -rungon kentät eivät ole `equals`-
  vertailussa.
- `catch (e: Exception)` nielee korutiinin peruutuksen.
- `"%.2f".format(x)` käyttää oletuslokaalia.
