# Luokat, suljetut hierarkiat ja geneerisyys {.runko-omat-tyypit}

## Luokat ja ominaisuudet

Kotlinin luokan pääkonstruktori kirjoitetaan luokan nimen perään, ja
sen `val`- ja `var`-parametrit ovat suoraan ominaisuuksia. Ominaisuus
korvaa kentän, getterin ja setterin: ulkoa katsoen se on arvo, mutta
sille voi kirjoittaa oman `get`- ja `set`-toteutuksen ja rajata setterin
näkyvyyden.

```{.kotlin tiedosto="esimerkit/08-luokat.kt"}
```

```{.tuloste tiedosto="esimerkit/08-luokat.odotettu"}
```

- `init`-lohko ajetaan konstruktorissa. Siinä tarkistetaan
  invariantit, joiden on oltava voimassa koko olion eliniän.
- `private constructor` ja `companion object` -tehdasfunktio
  (`Tili.avaa`) normalisoivat ja validoivat syötteen ennen olion
  luontia.
- `private set` tekee ominaisuudesta ulospäin vain luettavan. Saldoa
  voi muuttaa vain metodien kautta, jotka valvovat sääntöjä.
- `object` on singleton, jonka JVM alustaa laiskasti ja
  säieturvallisesti luokan latauksessa. Jaettu muuttuva tila siinä
  (kuten laskuri) ei silti ole säieturvallinen.
- Näkyvyydet: `public` (oletus), `internal` (moduuli), `protected` ja
  `private`. Javan pakettinäkyvyyttä ei ole.

## Data- ja suljetut luokat

`data class` on arvo-olio: `equals`, `hashCode`, `toString`, `copy` ja
purku (`componentN`) generoidaan pääkonstruktorin ominaisuuksista.
`sealed interface` tai `sealed class` rajaa alatyypit samaan pakettiin
ja moduuliin, joten kääntäjä tuntee ne kaikki. `when` suljetun tyypin
yli on silloin kattava ilman `else`-haaraa.

```{.kotlin tiedosto="esimerkit/08-sealed.kt"}
```

```{.tuloste tiedosto="esimerkit/08-sealed.odotettu"}
```

Kattavuuden hyöty näkyy, kun hierarkiaan lisätään tyyppi: jokainen
`when`, joka ei käsittele sitä, on käännösvirhe.

```{.kotlin tiedosto="esimerkit/08-kattavuus.ei-kaanny.kt"}
```

```
error: 'when' expression must be exhaustive. Add the 'Poistettu'
branch or an 'else' branch.
```

`else`-haara kumoaisi tämän suojan, joten suljetun tyypin `when`-
lausekkeeseen sitä ei kirjoiteta. `data object` on `object`, jolla on
luettava `toString`. Suljettu hierarkia ja `data class` vastaavat
funktionaalisten kielten algebrallisia tietotyyppejä.

## Rajapinnat, periytyminen ja enum

Luokat ja metodit ovat oletuksena `final`. Periytyminen sallitaan
sanalla `open`, ja ylikirjoitus merkitään aina sanalla `override`.
Rajapinnoissa voi olla oletustoteutuksia ja abstrakteja ominaisuuksia.

```{.kotlin tiedosto="esimerkit/08-rajapinnat.kt"}
```

```{.tuloste tiedosto="esimerkit/08-rajapinnat.odotettu"}
```

`enum class` on Javan `enum`. `entries` (Kotlin 1.9) palauttaa arvot
muuttumattomana listana, ja se korvaa `values()`-metodin, joka luo
uuden taulukon joka kutsulla.

## Geneerisyys ja varianssi

Javassa varianssi ilmaistaan käyttöpaikassa jokerimerkeillä
(`? extends T`, `? super T`). Kotlinissa se ilmaistaan yleensä
esittelypaikassa: `out T` tarkoittaa, että tyyppi vain tuottaa T:tä
(kovariantti), ja `in T`, että se vain kuluttaa T:tä (kontravariantti).
Kääntäjä tarkistaa, ettei `out`-parametria käytetä parametrin
tyyppinä eikä `in`-parametria paluutyyppinä.

```{.kotlin tiedosto="esimerkit/08-geneerisyys.kt"}
```

```{.tuloste tiedosto="esimerkit/08-geneerisyys.odotettu"}
```

Vakiokirjaston `List<out E>` on kovariantti, koska siihen ei voi
kirjoittaa. `MutableList<E>` on invariantti, koska muuten `Double`-arvon
voisi lisätä `Int`-listaan:

```{.kotlin tiedosto="esimerkit/08-varianssi.ei-kaanny.kt"}
```

```
error: argument type mismatch: actual type is 'MutableList<Int>', but
'MutableList<Number>' was expected.
```

Ylärajoite kirjoitetaan `T : Comparable<T>`, useampi rajoite
`where`-lauseella. Tähtiprojektio `List<*>` vastaa Javan `List<?>`-tyyppiä.
`fun interface` on SAM-rajapinta, jonka voi toteuttaa lambdalla.

## Käytännössä

- **Suljettu hierarkia tiloille ja tuloksille.** Kun arvolla on rajattu
  joukko muotoja (tila, viesti, komento, tulos), `sealed interface` ja
  kattava `when` tekevät unohtuneen tapauksen käännösvirheeksi.
  Javan vastaava on `sealed` ja `switch`-hahmot.
- **`data class` arvoille, tavallinen luokka identiteetille.** Tili,
  yhteys tai käsittelijä ei ole arvo: kaksi tiliä samalla saldolla ovat
  eri tilejä. Älä tee niistä `data class` -luokkia.
- **Invariantit konstruktoriin.** `require` `init`-lohkossa tai
  yksityinen konstruktori ja tehdasfunktio takaavat, ettei virheellistä
  oliota ole olemassa.
- **Koostaminen periytymisen sijaan.** `final` oletuksena pitää
  hierarkiat matalina. Kun tarvitset toisen olion toiminnot, delegoi
  (`by`, luku 10).
- **Varianssi rajapintaan.** Tuottajarajapinta merkitään `out`,
  kuluttaja `in`. Silloin kutsujan ei tarvitse kirjoittaa jokerimerkkejä.
- **Hinta:** `data class` generoi `componentN`- ja `copy`-metodit, jotka
  kasvattavat tavukoodia; Androidissa suurissa määrissä tällä on
  merkitystä. Suorituskykyyn sillä ei ole vaikutusta.
- **Sudenkuoppa:** `data class` -luokan rungossa esitellyt ominaisuudet
  eivät ole mukana `equals`-, `hashCode`- ja `copy`-metodeissa.
- **Sudenkuoppa:** `open`-luokan konstruktori, joka kutsuu `open`-metodia,
  näkee alaluokan alustamattomat kentät kuten Javassa.

## Itsearviointi

- Osaat kirjoittaa luokan, jonka invariantit tarkistetaan
  konstruktorissa ja jonka tilaa muutetaan vain metodien kautta.
- Osaat mallintaa vaihtoehdot suljettuna hierarkiana ja käsitellä ne
  kattavalla `when`-lausekkeella.
- Osaat valita `data class`, tavallisen luokan, `object`-singletonin ja
  `enum`-luokan välillä.
- Osaat selittää `out`- ja `in`-varianssin ja sen, miksi `MutableList`
  on invariantti.
