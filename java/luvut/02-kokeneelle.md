# Java kokeneelle {.runko-kokeneelle}

Tämä luku on kehittäjälle, joka osaa jonkin toisen kielen, kuten
Pythonin, C++:n, C#:n tai Go:n, ja haluaa päästä Javassa nopeasti
tuottavaksi. Luku kokoaa ajattelutavan, vastaavuudet, hinnat ja
sudenkuopat. Yksityiskohdat ovat luvuissa 3–11.

## Ajattelutapa

- **Kaikki on luokassa, ja tyypit ovat nimellisiä.** Tyyppi toteuttaa
  rajapinnan vain, jos se sanoo `implements`. Rajapinta on sopimus, jonka
  kääntäjä tarkistaa.
- **Primitiivit ja viitteet.** `int`, `long`, `double`, `boolean`,
  `char` ja muut kuusi primitiivityyppiä ovat arvoja. Kaikki muu on
  olio, ja muuttuja sisältää viitteen olioon. Viite voi olla `null`.
- **Roskienkeruu.** Muistia ei vapauteta itse. Roskienkerääjä vapauttaa
  oliot, joihin ei enää viitata. Muut resurssit (tiedostot, yhteydet,
  lukot) suljetaan `try`-with-resources-lohkolla.
- **JVM kääntää kuuman koodin ajon aikana.** Tavukoodi tulkataan ensin, ja
  JIT-kääntäjä optimoi usein ajetut metodit konekieleksi ajonaikaisen
  profiilin perusteella. Java on pitkään käynnissä olevissa palveluissa
  nopea, mutta lyhyt ajo ei koskaan lämpene.
- **Poikkeukset ovat virheenkäsittelyn päämekanismi.** Tarkistetut
  poikkeukset (*checked exceptions*) ovat osa metodin tyyppiä.
- **Moderni Java on arvopainotteista.** `record`, `sealed`, kuvioiden
  sovitus ja muuttumattomat kokoelmat tekevät algebrallisista
  tietotyypeistä luontevia. Vanhaa Javaa (gettereitä, settereitä ja
  syviä periytymishierarkioita) näkee yhä paljon, mutta uutta koodia ei
  kannata kirjoittaa niin.
- **Taaksepäin yhteensopivuus on pyhää.** Java 1.0:n koodi kääntyy
  edelleen. Siksi kielessä on vanhoja kerroksia (`Vector`, `Date`,
  raakatyypit), joita ei poisteta mutta joita ei pidä käyttää.

## Vastaavuudet

| Asia | Python | C++ | C# | Java |
|------|--------|-----|----|------|
| Dynaaminen taulukko | `list` | `std::vector` | `List<T>` | `ArrayList<E>` |
| Hajautustaulu | `dict` | `unordered_map` | `Dictionary` | `HashMap<K,V>` |
| Järjestetty taulu | – | `std::map` | `SortedDictionary` | `TreeMap<K,V>` |
| Tietue | `@dataclass(frozen)` | `struct` | `record` | `record` |
| Summatyyppi | `Union` + `match` | `std::variant` | – | `sealed` + `switch` |
| Puuttuva arvo | `None` | `std::optional` | `T?` | `null`, `Optional<T>` |
| Resurssien vapautus | `with` | RAII | `using` | `try` (resurssit) |
| Lambda | `lambda x: x+1` | `[](int x){...}` | `x => x+1` | `x -> x + 1` |
| Iteraattoriketju | generaattorit | ranges | LINQ | `Stream` |
| Kevyt rinnakkaisuus | `asyncio` | korutiinit | `async`/`await` | virtuaalisäikeet |
| Paketinhallinta | pip | Conan, vcpkg | NuGet | Maven, Gradle |

## Hinnat

| Asia | Hinta | Lisää |
|------|-------|-------|
| Olion luonti | halpa: allokaatio on osoittimen siirto, nuori sukupolvi kerätään nopeasti | luku 5 |
| Boksattu luku (`Integer`) | olio keossa, osoitin, välimuistihukka; `List<Integer>` summa noin 5–10 × hitaampi kuin `int[]` | luku 5 |
| Poikkeus | pinojäljen keruu: mikrosekunteja, kymmeniä kertoja kalliimpi kuin tarkistus | luku 8 |
| Rajapintakutsu | yleensä ilmainen: JIT inlinoi, jos kutsukohdassa näkyy 1–2 toteutusta | luku 5 |
| Stream | pieni kiinteä yleiskustannus; kuumissa silmukoissa tavallinen silmukka on usein nopeampi | luku 6 |
| `synchronized` ilman kilpailua | halpa; kilpailtu lukko pysäyttää säikeen | luku 10 |
| Merkkijonon `+` silmukassa | uusi olio joka kierroksella; käytä `StringBuilder`iä | luku 6 |
| Virtuaalisäie | muutama sata tavua kekoa; voi luoda miljoonia | luku 10 |
| JVM:n käynnistys | 50–200 ms ja lämpeneminen sekunteja; ei sovellu lyhyisiin skripteihin | luku 1 |
| Reflektio | hidas ensimmäisellä kerralla, estää osan optimoinneista | luku 11 |

## Tärkeimmät sudenkuopat

1. **`==` vertaa viitteitä.** Merkkijonot ja muut oliot verrataan
   `equals`-metodilla. `Integer`-olioiden `==` toimii vain välillä
   −128…127 (luku 5).
2. **`null`.** Mikä tahansa viite voi olla `null`, ja
   `NullPointerException` on Javan yleisin virhe. Älä palauta `null`ia
   kokoelmasta tai `Optional`ista.
3. **`equals` ja `hashCode` yhdessä.** Jos ylikirjoitat toisen,
   ylikirjoita toinenkin, ja älä muuta hajautustaulun avaimena olevaa
   oliota (luku 6). `record` hoitaa molemmat.
4. **Kokonaislukujen ylivuoto kiertää hiljaa.** Käytä `long`ia tai
   `Math.addExact`-metodeja (luku 3).
5. **Raha `double`na.** Käytä `long`-senttejä tai `BigDecimal`ia (luku 3).
6. **Oletusmerkistö ja -kieliasetus.** `String.format("%.2f")` käyttää
   koneen kieliasetusta ja tulostevirta koneen merkistöä. Anna
   `Locale.ROOT` ja `UTF_8` eksplisiittisesti (luku 3).
7. **Muuttumattomat kokoelmat heittävät poikkeuksen.** `List.of` ei salli
   muutoksia eikä `null`-alkioita (luku 6).
8. **Tarkistetut poikkeukset ja lambdat.** `Function` ei voi heittää
   `IOException`ia, joten se on käärittävä (luku 8).
9. **Mikrovertailu ilman lämmittelyä.** Ensimmäiset kierrokset mittaavat
   tulkkia, eivät optimoitua koodia (luku 5). Käytä JMH:ta.
10. **Jaettu muuttuva tila säikeiden välillä.** Ilman `synchronized`-,
    `volatile`- tai `java.util.concurrent`-rakenteita toisen säikeen
    kirjoitus ei välttämättä näy lainkaan (luku 10).

## Lukuohje

- **C#-kehittäjä:** kieli on hyvin samankaltainen. Lue luvut 5
  (boksaus, `==`), 8 (tarkistetut poikkeukset) ja 10 (virtuaalisäikeet
  `async`/`await`in sijaan).
- **C++-kehittäjä:** lue luvut 5 (viitteet, roskienkeruu, JIT) ja 7
  (geneerisyys toteutetaan tyyppien poistolla, ei malleilla).
- **Python-kehittäjä:** lue luvut 3 (staattiset tyypit, kokonaislukujen
  ylivuoto), 6 (kokoelmarajapinnat) ja 8 (poikkeusten hinta on
  päinvastainen kuin Pythonissa).
- **Go-kehittäjä:** lue luvut 7 (periytyminen ja nimelliset rajapinnat) ja
  8 (poikkeukset virhearvojen sijaan).

Jokaisen luvun lopussa on itsearviointi. Jos hallitset sen väitteet,
voit siirtyä seuraavaan lukuun.
