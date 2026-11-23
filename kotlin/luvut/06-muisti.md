# Muisti, resurssit ja abstraktioiden hinta {.runko-muisti}

Kotlin/JVM:n muistimalli on Javan: oliot ovat keossa, muuttujat ovat
viittauksia, ja roskienkeruu vapauttaa saavuttamattomat oliot. Taito
*Java* käsittelee keon, roskienkeruun ja JIT-kääntäjän. Tämä luku
käsittelee sen, minkä Kotlin lisää: resurssien sulkemisen idiomin,
arvoluokat ja kielen abstraktioiden hinnan tavukoodissa.

## Resurssit: use

Roskienkeruu vapauttaa muistin, mutta ei tiedostoja, yhteyksiä eikä
lukkoja. Kotlinissa ei ole `try-with-resources`-lausetta. Sen sijaan
`use` on `AutoCloseable`-tyypin laajennusfunktio, joka sulkee
resurssin kaikilla poluilla. Lohkon poikkeus säilyy, ja sulkemisen
poikkeus lisätään siihen tukahdutettuna (*suppressed*) kuten Javassa.

```{.kotlin tiedosto="esimerkit/06-use.kt"}
```

```{.tuloste tiedosto="esimerkit/06-use.odotettu"}
```

`useLines` avaa tiedoston, antaa sen rivit laiskana sekvenssinä ja
sulkee tiedoston lohkon jälkeen. Sekvenssiä ei saa palauttaa lohkosta,
koska tiedosto on silloin jo suljettu.

## Yhtäsuuruus ja kopiot

- `a == b` kutsuu `a?.equals(b)`-metodia ja hoitaa `null`-arvon. `a === b`
  vertaa viittauksia.
- `data class` vertaa pääkonstruktorin ominaisuuksia. `copy` tekee
  matalan kopion: muuttuvat kokoelmat jaetaan kopioiden kesken. Siksi
  `data class` -luokan kentät kannattaa pitää muuttumattomina (`val`,
  `List`).
- Laatikoitujen lukujen `===`-vertailu riippuisi JVM:n välimuistista
  (arvot −128...127 jaetaan). Kääntäjä varoittaa perustyyppien
  `===`-vertailusta, ja `-Werror` tekee varoituksesta virheen.

## Arvoluokat

`value class` käärii yhden arvon omaksi tyypikseen. Kääntäjä käyttää
ajonaikana suoraan käärittyä arvoa, joten tyyppiturvallisuus ei maksa
oliota. JVM:ssä annotaatio `@JvmInline` on pakollinen.

```{.kotlin tiedosto="esimerkit/06-arvoluokka.kt"}
```

```{.tuloste tiedosto="esimerkit/06-arvoluokka.odotettu"}
```

- `TuoteId` ja `Sentit` estävät sekoittamasta tunnisteita ja summia,
  vaikka molemmat olisivat ajonaikana `String` ja `long`.
- Arvoluokka laatikoidaan, kun sitä käytetään nullable-, geneerisenä tai
  rajapintatyyppinä. Tällöin se maksaa kuten tavallinen olio.
- Funktioiden nimet sekoitetaan (*name mangling*), jotta
  `f(Sentit)` ja `f(Long)` eivät törmää tavukoodissa. Java ei siksi
  voi kutsua niitä suoraan ilman `@JvmName`-annotaatiota.

## inline ja reified

`inline`-funktion runko ja sen lambdaparametrit kopioidaan
kutsukohtaan. Lambdasta ei synny oliota eikä virtuaalikutsua, `return`
lambdassa palaa ympäröivästä funktiosta, ja tyyppiparametri voi olla
`reified`, jolloin se on tiedossa ajonaikana.

```{.kotlin tiedosto="esimerkit/06-inline.kt"}
```

```{.tuloste tiedosto="esimerkit/06-inline.odotettu"}
```

JVM:n geneerisyys perustuu tyyppien poistoon (*type erasure*): `List<String>`
ja `List<Int>` ovat ajonaikana samaa luokkaa, eikä `x is T` ole
mahdollinen tavallisessa funktiossa. `reified` kiertää rajoituksen,
koska jokainen kutsukohta saa oman kopion konkreettisella tyypillä.
Parametreja voi rajata: `noinline` estää yksittäisen lambdan
inlinauksen ja `crossinline` kieltää ei-paikallisen `return`-lauseen.

## Mitä abstraktiot maksavat

| Rakenne | Tavukoodi | Hinta |
|---------|-----------|-------|
| ylätason funktio, laajennus | staattinen metodi | ei mitään |
| `val`/`var`-ominaisuus | yksityinen kenttä + getteri/setteri | JIT inlinaa |
| `data class` | luokka ja generoidut metodit | kuten Javan record |
| `object`, `companion object` | singleton, laiska alustus luokan latauksessa | ei mitään |
| lambda `inline`-funktiolle | kopioitu koodi | ei mitään, koodi kasvaa |
| lambda muulle funktiolle | olio (kaappaava: uusi joka kutsulla) | allokaatio |
| `value class` | käärityn arvon tyyppi | ei mitään, ellei laatikoida |
| `Int?`, `List<Int>`, `T` | `java.lang.Integer` | laatikointi, välimuistin ohi |
| `by lazy` | apuolio + synkronointi | pieni, kerran |
| `vararg` | taulukko | allokaatio, `*`-levitys kopioi |
| merkkijonopohja | `StringBuilder` tai `invokedynamic` | kuten Javassa |

## Käytännössä

- **`use` jokaiselle `AutoCloseable`-oliolle**, jota ei anneta eteenpäin.
  Funktio, joka avaa resurssin, myös sulkee sen. Lohkosta palautetaan
  valmis tulos, ei laiskaa sekvenssiä tai virtaa.
- **Arvoluokka domainin tunnisteille ja yksiköille.** `UserId`,
  `Sentit`, `Metrit` ja `Sekunnit` estävät argumenttien sekoittamisen
  ilman ajonaikaista hintaa. Validoi arvo `init`-lohkossa tai
  tehdasfunktiossa (luku 9).
- **`inline` omille korkeamman asteen apufunktioille**, joita kutsutaan
  usein (ajoitus, lukitus, kirjaus, uudelleenyritys), ja kun tarvitaan
  `reified`-tyyppiä. Ei suurille funktioille: jokainen kutsukohta saa
  kopion.
- **Hinta:** kuumassa silmukassa vältä laatikointia: `IntArray` ja
  `LongArray` listojen sijaan, primitiiviset parametrit geneeristen
  sijaan.
- **Sudenkuoppa:** `copy` on matala. `data class`, jonka kentässä on
  `MutableList`, jakaa listan kaikkien kopioiden kesken.
- **Sudenkuoppa:** `object` ja `companion object` alustetaan
  ensimmäisellä käytöllä. Alustuksen sivuvaikutukset ja keskinäiset
  riippuvuudet tekevät käynnistysjärjestyksestä vaikean ennustaa.

## Itsearviointi

- Osaat sulkea resurssit `use`- ja `useLines`-funktioilla ja selittää,
  miksi laiskaa sekvenssiä ei saa palauttaa lohkosta.
- Osaat kirjoittaa arvoluokan ja kertoa, milloin se laatikoidaan.
- Osaat kirjoittaa `inline`-funktion ja `reified`-tyyppiparametrin ja
  selittää tyyppien poiston rajoitukset.
- Osaat arvioida, mitkä Kotlinin abstraktiot maksavat ajonaikana ja
  mitkä eivät.
