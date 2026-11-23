# Kotlin kokeneelle {.runko-kokeneelle}

Tämä luku on tarkoitettu Java-kehittäjälle. Se kokoaa Kotlinin
ajattelutavan, vastaavuudet Javaan, hinnat ja tärkeimmät sudenkuopat.
Kotlin ei vaihda ajonaikaista ympäristöä: oliot, roskienkeruu, säikeet ja
kirjastot ovat JVM:n. Muutos on kielessä ja siinä, mitä kääntäjä
tarkistaa.

## Ajattelutapa

- **Null on osa tyyppiä.** `String` ei voi olla `null`, `String?` voi.
  Kääntäjä pakottaa käsittelemään puuttuvan arvon ennen käyttöä (luku 4).
  `NullPointerException` syntyy enää rajapinnassa Javaan tai
  `!!`-operaattorista.
- **Muuttumattomuus on oletus.** `val` on muuttumaton viite, `var`
  muuttuva. `List` ja `Map` ovat vain luku -rajapintoja, `MutableList`
  ja `MutableMap` muokattavia.
- **Lausekkeet lauseiden sijaan.** `if`, `when` ja `try` palauttavat
  arvon, joten tilapäisiä muuttujia ja `return`-ketjuja tarvitaan
  vähemmän.
- **Luokat ovat oletuksena `final`.** Periytyminen sallitaan erikseen
  sanalla `open`. Koostaminen ja delegointi (`by`) ovat ensisijaisia.
- **Funktiot ovat ensimmäisen luokan arvoja.** Funktion voi kirjoittaa
  tiedoston ylätasolle, välittää parametrina ja palauttaa. Laajennus-
  funktiot lisäävät operaatioita valmiisiin tyyppeihin ilman apuluokkia.
- **Ei tarkistettuja poikkeuksia.** Kaikki poikkeukset ovat Javan
  `RuntimeException`-tyyppisiä kutsujan kannalta. Odotetut virheet
  ilmaistaan usein tyypillä (`null`, suljettu tulostyyppi).
- **Korutiinit säikeiden päällä.** `suspend`-funktiot ja kirjasto
  `kotlinx.coroutines` tekevät asynkronisesta koodista peräkkäisen
  näköistä (luku 12).

Seuraava ohjelma näyttää tyypillisen Kotlin-koodin: arvoluokat,
suljettu hierarkia, kattava `when`, laajennusfunktio ja null-
turvalliset operaattorit.

```{.kotlin tiedosto="esimerkit/02-vastaavuudet.kt"}
```

```{.tuloste tiedosto="esimerkit/02-vastaavuudet.odotettu"}
```

## Vastaavuudet

| Java | Kotlin |
|----------------------------|----------------------------------|
| `final String s = "a";` | `val s = "a"` |
| `String s = null;` | `var s: String? = null` |
| `record P(int x, int y)` | `data class P(val x: Int, val y: Int)` |
| `sealed interface` + `permits` | `sealed interface` (samassa paketissa) |
| `switch`-lauseke ja hahmot | `when`-lauseke ja `is` |
| `static`-metodi | ylätason funktio tai `companion object` |
| singleton-malli | `object` |
| `Optional<T>` | `T?` ja `?.`, `?:`, `let` |
| `Stream`-ketju | kokoelmafunktiot, laiskasti `Sequence` |
| `try (r) { }` | `r.use { }` |
| `instanceof` + cast | `is` ja älykäs tyyppimuunnos |
| `? extends T` / `? super T` | `out T` / `in T` |
| getter ja setter | ominaisuus (`val`/`var`) |
| `Runnable`, `Function<A,B>` | funktiotyyppi `() -> Unit`, `(A) -> B` |
| `CompletableFuture` | `suspend`-funktio, `async`/`await` |
| `String.format` | merkkijonopohja `"$x ${y + 1}"` |

## Hinnat

Kotlin käyttää samaa JVM:ää kuin Java, joten samat asiat ovat kalliita
(luku 6 käsittelee ne tarkemmin):

- **Lambda, joka ei ole `inline`.** Kaappaava lambda on olio, joka
  luodaan joka kutsulla. Vakiokirjaston kokoelmafunktiot (`map`,
  `filter`, `forEach`) ovat `inline`-funktioita, joten niissä lambdasta
  ei synny oliota. Omat korkeamman asteen apufunktiot kannattaa tehdä
  `inline`-funktioiksi.
- **Välilistat.** Jokainen `map` ja `filter` listalla luo uuden listan.
  Pitkä ketju suurelle aineistolle kannattaa tehdä `Sequence`-tyypillä
  (luku 7).
- **Laatikointi.** `Int` on JVM:n `int`, mutta `Int?`, `List<Int>` ja
  geneerinen `T` ovat `java.lang.Integer`-olioita.
- **Delegoidut ominaisuudet ja `lazy`.** `by lazy` luo apuolion ja
  synkronoi oletuksena ensimmäisen käytön.
- **Korutiini on halpa, mutta ei ilmainen.** Jokainen keskeytyskohta on
  tilakoneen tila, ja keskeytetty korutiini on kekoon tallennettu olio.

Halpoja ovat sen sijaan `data class`, `val`-ominaisuudet (getteri
inlinataan JIT:ssä), `when`, laajennusfunktiot (staattisia metodeja),
`value class` (ei oliota useimmissa käytöissä) ja merkkijonopohjat
(`StringBuilder`).

## Sudenkuopat

- **Alustatyypit.** Javan metodin paluuarvo on tyyppiä `String!`:
  kääntäjä ei tiedä, voiko se olla `null`, eikä vaadi tarkistusta. Jos
  sen sijoittaa ei-null-tyyppiin, tarkistus siirtyy ajonaikaiseksi:

```{.kotlin tiedosto="esimerkit/02-platform.kaatuu.kt"}
```

```
Exception in thread "main" java.lang.NullPointerException:
    getProperty(...) must not be null
	at _02_platform_kaatuuKt.main(02-platform.kaatuu.kt:7)
```

  Ilmoita Javasta tuleva arvo nullable-tyypiksi (`String?`), ellei
  Java-koodi ole merkitty `@NonNull`-annotaatiolla.
- **`!!` on väite, ei korjaus.** `x!!` heittää poikkeuksen, jos `x` on
  `null`. Jokainen `!!` on paikka, jossa tyyppijärjestelmä on ohitettu.
- **`List` ei ole muuttumaton.** Vain luku -näkymän takana voi olla
  `MutableList`, joka muuttuu (luku 7).
- **`==` vertaa sisältöä.** Kotlinin `==` kutsuu `equals`-metodia, ja
  `===` vertaa viittauksia. Javan tottumus kääntyy toisin päin.
- **Laajennusfunktio ei ole virtuaalinen.** Se valitaan muuttujan
  staattisen tyypin mukaan (luku 5).
- **Scope-funktioiden ketjut.** `let`, `run`, `apply`, `also` ja `with`
  ovat hyödyllisiä, mutta sisäkkäin ne hämärtävät, mihin `this` ja `it`
  viittaavat.
- **`data class` ja periytyminen.** `data class` on `final`, eikä sen
  automaattinen `equals` ota huomioon yliluokan kenttiä.
- **Kokonaisluvun ylivuoto kiertää** kuten Javassa. `Math.addExact`
  ja muut `*Exact`-funktiot tarkistavat ylivuodon.

## Lukuohje

Kokenut Java-kehittäjä voi lukea luvut 4 (null-turvallisuus), 5
(funktiot ja laajennukset), 8 (luokat ja suljetut hierarkiat) ja 12
(korutiinit) ja käyttää muita lukuja hakuteoksena. Jokaisen luvun
lopussa on *Itsearviointi*: jos hallitset sen väitteet, voit ohittaa
luvun. Pikaopas (`kotlin-pikaopas.pdf`) kokoaa syntaksin, idiomit ja
työkalukomennot muutamalle sivulle.
