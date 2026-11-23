# Null-turvallisuus {.runko-tyypit}

Tony Hoare kutsui `null`-viittausta "miljardin dollarin virheeksi".
Javassa mikä tahansa viittaus voi olla `null`, ja virhe näkyy vasta
ajonaikana `NullPointerException`-poikkeuksena kaukana siitä kohdasta,
jossa arvo jäi asettamatta. Kotlin siirtää tarkistuksen kääntäjälle:
tyyppi `String` ei voi olla `null`, tyyppi `String?` voi.

## Nullable-tyypit ja operaattorit

Nullable-arvon jäseniin ei pääse suoraan:

```{.kotlin tiedosto="esimerkit/04-nullkutsu.ei-kaanny.kt"}
```

```
error: only safe (?.) or non-null asserted (!!.) calls are allowed on
a nullable receiver of type 'String?'.
```

| Rakenne | Merkitys |
|---------|----------|
| `x?.f()` | kutsu, jos `x` ei ole `null`; muuten tulos on `null` |
| `x ?: y` | `x`, jos se ei ole `null`; muuten `y` (*elvis*) |
| `x ?: return`, `x ?: throw ...` | varhainen poistuminen |
| `if (x != null) x.f()` | älykäs tyyppimuunnos: `x` on haarassa `String` |
| `x?.let { ... }` | lohko vain ei-null-arvolle |
| `x!!` | väite: heittää `NullPointerException`-poikkeuksen, jos `null` |
| `requireNotNull(x)`, `checkNotNull(x)` | väite selkeällä virheellä |
| `as?` | turvallinen tyyppimuunnos: `null`, jos tyyppi ei täsmää |

```{.kotlin tiedosto="esimerkit/04-null.kt"}
```

```{.tuloste tiedosto="esimerkit/04-null.odotettu"}
```

- `?.`-ketju (`k.osoite?.postinumero`) pysähtyy ensimmäiseen
  `null`-arvoon. Elvis antaa oletusarvon ketjun lopussa.
- `?: return` on Kotlinin vartijalauseke (*guard clause*): loppuosa
  funktiosta käsittelee vain kelvollista arvoa, ja sisennys pysyy
  matalana.
- Älykäs tyyppimuunnos (*smart cast*) toimii, kun kääntäjä voi todeta,
  ettei arvo muutu tarkistuksen jälkeen: paikallinen `val` tai
  `val`-ominaisuus samassa moduulissa. `var`-ominaisuus tai toisen
  moduulin ominaisuus on kopioitava ensin paikalliseen muuttujaan.
- `mapNotNull`, `filterNotNull`, `firstOrNull` ja `getOrNull`
  yhdistävät kokoelmat ja nullable-tyypit.

## Alustatyypit

Javan koodilla ei ole null-tietoa tyypeissään. Kotlin käsittelee Javan
paluuarvot *alustatyyppeinä* (`String!`), joille kääntäjä sallii
molemmat käyttötavat. Turvallisuus palautuu, kun arvon tyyppi
ilmoitetaan rajapinnassa:

- `val x: String? = javaMetodi()` pakottaa tarkistuksen.
- `val x: String = javaMetodi()` lisää ajonaikaisen tarkistuksen ja
  kaatuu heti, jos arvo on `null` (luku 2).
- Jos Java-koodissa on `@Nullable`- ja `@NonNull`-annotaatiot (JSpecify,
  JetBrains, Android, Jakarta), Kotlin käyttää niitä ja tyyppi on
  tarkka.

## Käytännössä

- **Puuttuva arvo on tyyppi, ei poikkeus.** Funktio, jonka tulos voi
  odotetusti puuttua (haku, jäsennys), palauttaa `T?`. Kutsuja näkee
  tämän tyypistä, ja kääntäjä pakottaa käsittelyn.
- **Vartijalauseke `?: return`.** Käsittele puuttuvat arvot funktion
  alussa ja kirjoita loppu ei-null-tyypeillä.
- **`!!` vain, kun voit todistaa arvon olevan olemassa**, ja silloinkin
  mieluummin `requireNotNull(x) { "syy" }` tai `checkNotNull`, joiden
  virheilmoitus kertoo, mikä oletus rikkoutui.
- **Ilmoita Javan arvot rajapinnassa.** Käärii Java-kirjaston
  Kotlin-rajapinnaksi, jossa tyypit ovat tarkkoja; muu koodi ei näe
  alustatyyppejä.
- **`lateinit var`** sopii kenttiin, jotka kehys (riippuvuusinjektio,
  testien alustus, Androidin elinkaari) asettaa konstruktorin jälkeen.
  Lukeminen ennen asetusta heittää selkeän poikkeuksen. Muualla
  `lateinit` on piilotettu `!!`.
- **Hinta:** `T?` primitiivityypille (`Int?`) on laatikoitu olio.
  Viittaustyypeille `?` ei maksa mitään: se on vain kääntäjän tieto.
- **Sudenkuoppa:** `x?.let { ... } ?: oletus` ajaa myös oletuksen, jos
  lohko palauttaa `null`. Kun haaroja on kaksi, `if (x != null)` on
  selkeämpi.

## Itsearviointi

- Osaat käyttää operaattoreita `?.`, `?:` ja `as?` sekä älykästä
  tyyppimuunnosta ja tiedät, milloin muunnos ei toimi.
- Osaat kirjoittaa vartijalausekkeen `?: return` ja `?: throw`.
- Osaat selittää alustatyypit ja käsitellä Javasta tulevat arvot
  turvallisesti.
- Osaat perustella, milloin `!!`, `requireNotNull` tai `lateinit` on
  hyväksyttävä.
