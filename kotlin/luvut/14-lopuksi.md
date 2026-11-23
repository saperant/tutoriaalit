# Lopuksi {.runko-kaytannot .runko-lahteet}

## Mallit ja idiomit

| Malli | Ongelma, jonka se ratkaisee | Luku |
|------------------------------|----------------------------------|------|
| Nullable-paluuarvo ja elvis | puuttuva arvo ilman poikkeusta | 3, 4 |
| Vartijalauseke `?: return` | matala sisennys, kelvollinen arvo loppuun | 4 |
| Oletus- ja nimetyt argumentit | ylikuormitusketjut ja rakentajat | 5 |
| Laajennusfunktio | apuluokat valmiille tyypeille | 5 |
| `apply`-alustus, `also`-loki | olion asetukset ja sivuvaikutukset ketjussa | 5 |
| `use` | resurssin sulkeminen kaikilla poluilla | 6 |
| Arvoluokka (`value class`) | tunnisteiden ja yksiköiden sekoittaminen | 6 |
| `inline` + `reified` | lambdojen hinta, tyyppien poisto | 6 |
| Puolustava kopio, vain luku -rajapinta | kapseloidun tilan muuttaminen ulkoa | 7 |
| `asSequence` | välilistat pitkissä ketjuissa | 7 |
| Suljettu hierarkia + kattava `when` | unohtunut tapaus käännösvirheeksi | 8, 9 |
| Yksityinen konstruktori + tehdasfunktio | virheellinen olio mahdottomaksi | 8, 9 |
| Parse, don't validate | validointi kerran tyypiksi | 9 |
| Tyyppiturvallinen rakentaja (DSL) | rakenteinen konfiguraatio | 10 |
| Luokan delegointi `by` | koristelija ilman periytymistä | 10 |
| Ohut pääohjelma, `internal`-toteutus | testattava ja vaihdettava logiikka | 11 |
| Rakenteinen rinnakkaisuus | vuotavat ja peruuttamattomat tehtävät | 12 |

## Nyrkkisäännöt

1. `val` ja vain luku -kokoelmat ensin; muuttuvuus on poikkeus, joka
   perustellaan.
2. Puuttuva arvo on `T?`, ei `null`-tarkistus kommentissa. `!!` on
   merkki suunnitteluvirheestä.
3. Kun arvolla on rajattu joukko muotoja, mallinna se suljettuna
   hierarkiana äläkä kirjoita `else`-haaraa.
4. Odotettu virhe on arvo, ohjelmointivirhe on poikkeus.
5. Validoi syöte reunalla ja kuljeta sisällä tyyppejä, jotka takaavat
   kelvollisuuden.
6. Funktioketju silmukan tilalle, kun vaiheet ovat nimettyjä
   operaatioita; sekvenssi, kun aineisto on suuri.
7. Scope-funktio vain, kun se lyhentää koodia selkeyttä menettämättä.
8. Julkinen rajapinta pieneksi, tyypit siinä näkyviin, toteutus
   `internal`.
9. Korutiinit aina näkyvyysalueessa, estävä I/O `Dispatchers.IO`-
   altaaseen, peruutusta ei niellä.
10. Javan rajalla nullable-tiedot ja annotaatiot kuntoon, jotta
    kumpikin puoli on luontevaa.

## Hinnat lyhyesti

| Rakenne | Hinta |
|---------|-------|
| ylätason ja laajennusfunktio | staattinen kutsu |
| `inline`-funktion lambda | ei olioita; koodi kopioituu |
| muu lambda | olio, kaappaava luodaan joka kutsulla |
| `Int?`, `List<Int>`, geneerinen `T` | laatikointi |
| `value class` | ei mitään, paitsi nullable- ja geneerisenä |
| listan `map`/`filter` | uusi lista joka vaiheessa |
| `Sequence` | ei välilistoja; vaihe on olio ja virtuaalikutsu |
| `by lazy` | apuolio ja oletuksena synkronointi |
| poikkeus | pinon tallennus; ei ohjausrakenteeksi |
| korutiini | pieni olio, tila kekoon joka keskeytyksessä |

## Yleiset kirjastot

| Tarve | Kirjasto |
|-------|----------|
| Korutiinit, `Flow` | [kotlinx.coroutines](https://github.com/Kotlin/kotlinx.coroutines) |
| Serialisointi (JSON, CBOR) | [kotlinx.serialization](https://github.com/Kotlin/kotlinx.serialization) |
| Päivämäärät monialustaisesti | [kotlinx-datetime](https://github.com/Kotlin/kotlinx-datetime) |
| Verkkopalvelin ja -asiakas | [Ktor](https://ktor.io/) |
| Palvelinsovellukset | [Spring Boot ja Kotlin](https://spring.io/guides/tutorials/spring-boot-kotlin) |
| SQL | [Exposed](https://github.com/JetBrains/Exposed) |
| Testaus | [Kotest](https://kotest.io/), [MockK](https://mockk.io/) |
| Funktionaaliset tyypit | [Arrow](https://arrow-kt.io/) |
| Android-käyttöliittymä | [Jetpack Compose](https://developer.android.com/compose) |

Taitopuussa jatkotaitoja ovat *Android-sovellukset* (Compose,
elinkaari, korutiinit käyttöliittymässä) ja *Taustapalvelut*
(rajapinnat, tietokannat ja palvelujen rakenne).

## Lähteet ja jatkolukeminen

- *Kotlin documentation*, JetBrains:
  [kotlinlang.org/docs](https://kotlinlang.org/docs/home.html). Kielen
  virallinen opas ja vakiokirjaston API.
- *Kotlin Language Specification*:
  [kotlinlang.org/spec](https://kotlinlang.org/spec/).
- *Kotlin coding conventions*:
  [kotlinlang.org/docs/coding-conventions.html](https://kotlinlang.org/docs/coding-conventions.html).
- *Coroutines guide*:
  [kotlinlang.org/docs/coroutines-guide.html](https://kotlinlang.org/docs/coroutines-guide.html).
- Roman Elizarov: *Structured concurrency* (2018), blogikirjoitus
  rakenteisen rinnakkaisuuden perusteista.
- Sebastian Aigner, Roman Elizarov, Svetlana Isakova, Dmitry Jemerov:
  *Kotlin in Action*, 2. painos. Manning 2024.
- Marcin Moskała: *Effective Kotlin*, 2. painos. Kt. Academy 2024.
- Marcin Moskała: *Kotlin Coroutines: Deep Dive*. Kt. Academy 2022.
- Bruce Eckel, Svetlana Isakova: *Atomic Kotlin*. Mindview 2021.
- Joshua Bloch: *Effective Java*, 3. painos. Addison-Wesley 2018.
  Monet Kotlinin oletukset (muuttumattomuus, `final`, koostaminen)
  ovat tämän kirjan suosituksia.

Tämän tutoriaalin teksti ja esimerkit on kirjoitettu itse; lähteistä ei
ole kopioitu tekstiä tai koodia. Teos on lisensoitu CC BY-SA 4.0
-lisenssillä.
