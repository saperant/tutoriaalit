# Tyypit, lausekkeet ja syöte {.runko-tyypit}

Kotlinin perustyypit vastaavat Javan primitiivityyppejä, mutta ne
näkyvät ohjelmoijalle olioina, joilla on metodeja. Kääntäjä käyttää
primitiivejä aina, kun voi, ja laatikoi arvon vain silloin, kun tyyppi
on nullable tai geneerinen.

## Perustyypit ja muunnokset

| Kotlin | JVM | Huomio |
|--------|-----|--------|
| `Byte`, `Short`, `Int`, `Long` | `byte` ... `long` | etumerkillisiä; `UInt`, `ULong` erikseen |
| `Float`, `Double` | `float`, `double` | IEEE 754 |
| `Boolean` | `boolean` | |
| `Char` | `char` | UTF-16-koodiyksikkö, ei luku |
| `String` | `java.lang.String` | muuttumaton |
| `Any`, `Unit`, `Nothing` | `Object`, `void`, — | `Nothing`: ei palaa koskaan |

Muuttuja esitellään sanalla `val` (muuttumaton viite) tai `var`.
Tyyppi päätellään alustuksesta, ja se kirjoitetaan näkyviin, kun se
selkeyttää rajapintaa. Kotlin ei tee implisiittisiä numeerisia
muunnoksia, ei edes levennystä `Int` → `Long`:

```{.kotlin tiedosto="esimerkit/03-leveneminen.ei-kaanny.kt"}
```

```
error: argument type mismatch: actual type is
'List<Number & Comparable<*>>', but 'List<Long>' was expected.
```

Muunnos tehdään metodilla (`toLong()`, `toInt()`, `toDouble()`).
Sääntö estää Javan hiljaiset virheet, joissa `int`-kertolasku vuotaa
yli ennen tuloksen levennystä `long`-tyyppiin. Numeroliteraaliin voi
lisätä alaviivoja (`1_500_000`), `L` tekee siitä `Long`-tyyppisen ja
`u` etumerkittömän.

```{.kotlin tiedosto="esimerkit/03-tyypit.kt"}
```

```{.tuloste tiedosto="esimerkit/03-tyypit.odotettu"}
```

- Ylivuoto kiertää kuten Javassa. `Math.addExact` ja
  `Math.multiplyExact` heittävät poikkeuksen.
- Merkkijonopohja `"$nimi"` tai `"${lauseke}"` kootaan
  `StringBuilder`-olion avulla. `String.format` ja sen Kotlin-muoto
  `"%.2f".format(x)` käyttävät oletuslokaalia; koneluettavaan
  tulosteeseen anna lokaali (`String.format(Locale.ROOT, ...)`).
- Raakamerkkijonossa `"""..."""` ei ole pakomerkkejä, ja
  `trimIndent()` poistaa yhteisen sisennyksen. Pohjat toimivat silti.
- `String.length` on UTF-16-koodiyksiköiden määrä. Merkkien laskemiseen
  tarvitaan koodipisteet (`codePointCount`) tai graafeemiklusterit
  (`java.text.BreakIterator`).

## Lausekkeet

`if`, `when` ja `try` ovat lausekkeita, joten Javan ehto-operaattoria
`a ? b : c` ei ole. `when` korvaa sekä `switch`-lauseen että
`if-else`-ketjun; sen haaramuodot käydään läpi luvussa 5. Tässä
olennaista on, että rakenne tuottaa arvon:

```{.kotlin tiedosto="esimerkit/03-lausekkeet.kt"}
```

```{.tuloste tiedosto="esimerkit/03-lausekkeet.odotettu"}
```

Virheenkäsittely käsitellään luvussa 9. Lausekkeena käytetyn `if`- ja
`when`-rakenteen on oltava kattava: `else`-haara tarvitaan, ellei
kääntäjä voi todeta kaikkia vaihtoehtoja käsitellyiksi (luku 8).

## Syötteen lukeminen

`readln()` lukee rivin ja heittää poikkeuksen syötteen loputtua.
`readlnOrNull()` palauttaa tällöin `null`. Jäsennysfunktioilla on
kaksi muotoa: `toInt()` heittää `NumberFormatException`-poikkeuksen,
`toIntOrNull()` palauttaa `null`. Käyttäjän syötteelle `OrNull`-muoto
on oikea valinta, koska virheellinen syöte on odotettu tilanne.

```{.kotlin tiedosto="esimerkit/03-syote.kt"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/03-syote.syote"}
```

```{.tuloste tiedosto="esimerkit/03-syote.odotettu"}
```

`const val` on käännösaikainen vakio: sen arvo kopioidaan
käyttökohtiin, ja se voi olla vain perustyyppi tai merkkijono.
Suuria tiedostoja luetaan `File.useLines`- tai
`BufferedReader.lineSequence()`-funktiolla (luku 6), joka ei lue koko
tiedostoa muistiin.

## Käytännössä

- **Kirjoita tyyppi rajapintaan, päättele se toteutuksessa.** Julkisen
  funktion paluutyyppi kannattaa kirjoittaa näkyviin, jotta toteutuksen
  muutos ei muuta rajapintaa huomaamatta. Paikallisissa muuttujissa
  päättely on idiomaattista.
- **`val` ensin.** Vaihda `var`-muuttujaksi vain, kun arvoa todella
  muutetaan. Useimmat silmukkamuuttujat katoavat, kun silmukan korvaa
  kokoelmafunktiolla.
- **Rahaa ei lasketa liukuluvuilla.** Käytä sentteinä `Long`-tyyppiä
  tai `BigDecimal`-tyyppiä, mieluiten arvoluokan sisällä (luku 6).
- **Hinta:** perustyypit ovat primitiivejä, kunnes ne laatikoidaan
  (`Int?`, `List<Int>`, `Any`). Kuumassa silmukassa `IntArray` on
  moninkertaisesti tiiviimpi kuin `List<Int>`.
- **Sudenkuoppa:** `"%.2f".format(x)` tuottaa suomalaisella lokaalilla
  pilkun ja amerikkalaisella pisteen. Tiedostoihin ja rajapintoihin
  kirjoitettaessa lokaali annetaan aina.
- **Sudenkuoppa:** tulosteen merkistö tulee lokaalista, ei
  lähdekoodista. Ilman UTF-8-lokaalia `println("ä")` tulostaa `?`.
  Aseta `System.out` UTF-8:ksi (luku 1) tai anna JVM:lle valitsin
  `-Dstdout.encoding=UTF-8`.
- **Sudenkuoppa:** `Char`-tyypin aritmetiikka on rajattua: `'a' + 1` on
  `'b'`, mutta `'7' - '0'` on `Int`. Numeroarvo saadaan
  `digitToInt()`-funktiolla.

## Itsearviointi

- Osaat selittää, miksi Kotlin ei levennä `Int`-arvoa `Long`-tyypiksi
  automaattisesti, ja tehdä muunnokset oikein.
- Osaat käyttää `if`- ja `when`-rakenteita lausekkeina.
- Osaat lukea ja validoida syötettä `readlnOrNull`- ja
  `toIntOrNull`-funktioilla ilman poikkeuksia.
- Osaat kertoa, milloin `Int` on JVM:n primitiivi ja milloin olio.
- Osaat muotoilla tulosteen ja tiedät, milloin lokaali on annettava.
