# Poikkeukset ja virheenkäsittely {.runko-virheet}

Aiempien lukujen esimerkit ovat heittäneet ja ottaneet kiinni
poikkeuksia selittämättä mekanismia. Tämä luku kokoaa
virheenkäsittelyn: mitä poikkeustyypit tarkoittavat, miten virhe
välitetään kerrokselta toiselle hukkaamatta syytä ja milloin poikkeus
on väärä väline. Syntaksi on Pythonista tuttu (`try`, `catch`,
`finally`, `throw`), mutta kaksi asiaa on toisin: osa poikkeuksista
kuuluu metodin tyyppiin, ja poikkeus on kallis.

## Poikkeushierarkia

Poikkeus on olio, jonka luokka periytyy luokasta `Throwable`
(periytyminen: luku 5). `catch (IOException e)` ottaa kiinni myös
kaikki `IOException`in aliluokat, joten hierarkia määrää, mitä
kukin käsittelijä sieppaa:

```{.dot otsikko="Poikkeushierarkia. Tarkistetut poikkeukset (tummennettu) on käsiteltävä tai ilmoitettava `throws`-määreellä; `RuntimeException` aliluokkineen ja `Error` ovat tarkistamattomia."}
digraph {
  rankdir=BT; nodesep=0.2; ranksep=0.4;
  node [fontsize=8, height=0.3, fillcolor="white"];
  Throwable; Error; RuntimeException;
  oom [label="OutOfMemoryError\nStackOverflowError"];
  rt [label="IllegalArgumentException\nIllegalStateException\nNullPointerException"];
  { node [fillcolor="#D5DEC4"];
    Exception; IOException; muut [label="InterruptedException\nSQLException"];
    io [label="NoSuchFileException\nFileNotFoundException"]; }
  Error -> Throwable; Exception -> Throwable;
  oom -> Error;
  RuntimeException -> Exception; IOException -> Exception; muut -> Exception;
  rt -> RuntimeException; io -> IOException;
}
```

- `Error`: JVM:n tai ympäristön vakava ongelma. Näitä ei yleensä
  käsitellä.
- `Exception` ja sen aliluokat, paitsi `RuntimeException`:
  *tarkistettu* poikkeus (*checked*). Metodin on joko käsiteltävä se
  tai ilmoitettava `throws`-määreellä, ja kääntäjä valvoo tämän.
- `RuntimeException` aliluokkineen: *tarkistamaton* poikkeus
  (*unchecked*), jota ei tarvitse ilmoittaa.

Tarkistetut poikkeukset ovat Javan erikoisuus, eikä mikään myöhempi
valtavirtakieli ole kopioinut niitä. Käytännön sääntö: tarkistettu
poikkeus kuvaa ympäristön ongelmaa, johon kutsuja voi järkevästi
reagoida (tiedosto puuttuu, verkko katkesi). Tarkistamaton poikkeus
kuvaa ohjelmointivirhettä tai sopimuksen rikkomista (virheellinen
argumentti, väärä tila).

## Kääriminen ja syyketju

Jokainen kerros kääntää alemman tason poikkeuksen omalle
abstraktiotasolleen ja säilyttää alkuperäisen syynä (*cause*). Oma
poikkeusluokka on pieni:

```{.java tiedosto="esimerkit/09-asetukset.java" osa="virhe"}
```

`Exception` on `Serializable`, joten `-Xlint:all` vaatii
`serialVersionUID`-kentän. `@Serial`-annotaatio (Java 14) kertoo, että
kenttä kuuluu sarjallistamiseen.

```{.java tiedosto="esimerkit/09-asetukset.java" osa="jasennys"}
```

```{.java tiedosto="esimerkit/09-asetukset.java" osa="ketju"}
```

```{.java tiedosto="esimerkit/09-asetukset.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-asetukset.odotettu"}
```

Huomioita:

- *Monisieppaus* (*multi-catch*) `catch (IOException | IllegalArgumentException e)`
  käsittelee useamman tyypin samalla koodilla.
- Viesti kertoo, mitä oltiin tekemässä (`asetusten lataus: rikki.conf`),
  ja syyketju kertoo miksi. Pinojälki tulostaa ketjun automaattisesti
  (`Caused by:`).
- Kutsuja voi tutkia ketjua (`getCause() instanceof
  NoSuchFileException`) ja valita toimintatavan.

## Tarkistetut poikkeukset ja lambdat

`java.util.function`-rajapintojen metodit eivät heitä tarkistettuja
poikkeuksia, joten lambda, joka kutsuu `IOException`ia heittävää
metodia, ei käänny:

```{.java tiedosto="esimerkit/09-lambda.ei-kaanny.java" osa="koodi"}
```

```
09-lambda.ei-kaanny.java:28: error: unreported exception IOException;
must be caught or declared to be thrown
```

Ratkaisu on kääriä poikkeus tarkistamattomaksi apumetodissa, ja
`UncheckedIOException` on tähän tarkoitettu:

```{.java tiedosto="esimerkit/09-lambda.ei-kaanny.java" osa="apu"}
```

Jos koko putki on I/O:ta, tavallinen silmukka on usein selkeämpi kuin
virta, jossa jokainen vaihe kääritään.

## Poikkeusten hinta

Poikkeusolion luonti on kallis, koska konstruktori kerää pinojäljen
(`fillInStackTrace`) kävelemällä pinon läpi. Heittäminen ja
kiinniottaminen itsessään ovat halvempia, kun JIT näkee molemmat.
Esimerkki tarkistaa merkkijonoja kolmella tavalla:

```{.java tiedosto="esimerkit/09-hinta.java" osa="tavat"}
```

```{.java tiedosto="esimerkit/09-hinta.java" osa="kevyt"}
```

```{.tuloste tiedosto="esimerkit/09-hinta.odotettu"}
```

Tyypillisellä koneella `parseInt` poikkeuksineen on 30–60 kertaa
hitaampi kuin tarkistus, kun puolet syötteistä on virheellisiä.
Pinojäljettömän poikkeuksen ero on pieni, koska JIT voi poistaa sen
kokonaan. Tämä on päinvastoin kuin Pythonissa, jossa poikkeus on
idiomaattinen ja halpa tapa ilmaista tavallisiakin tilanteita
(*EAFP*). Javassa poikkeus on poikkeustilanteita varten: jos virhe on
odotettu ja yleinen, kuten käyttäjän syötteen validoinnissa, se
ilmaistaan paluuarvolla.

## Odotettavat puutteet: `Optional`

`Optional<T>` (Java 8) on paluuarvon tyyppi, joka kertoo, että arvo voi
puuttua. Kutsuja ei voi unohtaa käsitellä puuttumista samalla tavalla
kuin `null`-paluuarvon:

```{.java tiedosto="esimerkit/09-optional.java" osa="haku"}
```

```{.java tiedosto="esimerkit/09-optional.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-optional.odotettu"}
```

`map` muuntaa `null`-tuloksen tyhjäksi, joten ketju ei kaadu
puuttuvaan alennuskoodiin. `orElseThrow()` kertoo lukijalle, että arvon
odotetaan olevan olemassa. `get()`-metodia ei käytetä, koska se piilottaa
saman oletuksen. `Optional` on tarkoitettu paluuarvoksi: sitä ei
käytetä kenttänä, parametrina eikä kokoelman alkiona.

## Odotettavat virheet: tulostyyppi

Kun kutsuja tarvitsee tiedon *kaikista* virheistä, kuten lomakkeen
validoinnissa, virheet palautetaan arvona. Suljettu tulostyyppi pakottaa
käsittelemään molemmat tapaukset:

```{.java tiedosto="esimerkit/09-tulos.java" osa="tulos"}
```

```{.java tiedosto="esimerkit/09-tulos.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-tulos.odotettu"}
```

## `NullPointerException`

Selittävä viesti (Java 14) kertoo, mikä lausekkeen osa oli `null`:

```{.java tiedosto="esimerkit/09-npe.kaatuu.java" osa="koodi"}
```

```
Exception in thread "main" java.lang.NullPointerException: Cannot invoke
"Main$Osoite.postinumero()" because the return value of
"Main$Asiakas.osoite()" is null
```

Paras puolustus on estää `null` rajalla: validoi konstruktorissa
`Objects.requireNonNull`illa, palauta tyhjiä kokoelmia ja `Optional`eja
ja käytä staattista analyysiä (`@Nullable`-annotaatiot, NullAway).

## Käytännössä

- **Heitä aikaisin, ota kiinni myöhään.** Validoi argumentit metodin
  alussa (`IllegalArgumentException`, `Objects.requireNonNull`) ja käsittele
  poikkeukset kerroksessa, joka voi tehdä niille jotain: käyttöliittymä,
  pyynnön käsittelijä, eräajon silmukka.
- **Kääri syyn kanssa.** `throw new X("mitä tehtiin", e)`. Syyn
  pudottaminen hävittää diagnostiikan.
- **Älä niele poikkeuksia.** Tyhjä `catch`-lohko on virhe. Jos poikkeus
  on oikeasti merkityksetön, kirjoita kommentti, miksi.
- **Älä ota kiinni `Exception`ia tai `Throwable`a** muualla kuin ylimmällä
  tasolla, joka kirjaa virheen ja jatkaa seuraavaan pyyntöön.
- **`InterruptedException`:** joko välitä eteenpäin tai palauta
  keskeytyslippu (`Thread.currentThread().interrupt()`), älä niele.
- **Poikkeukset poikkeustilanteille.** Odotettu ja yleinen virhe on
  paluuarvo (`Optional`, `boolean`, tulostyyppi). Ohjausvuota ei
  toteuteta poikkeuksilla.
- **Omat poikkeukset harkiten.** Valmiit `IllegalArgumentException`,
  `IllegalStateException` ja `UnsupportedOperationException` riittävät
  usein. Oma tyyppi kannattaa, kun kutsuja haluaa käsitellä sen erikseen.
- **Hinta.** `try` ilman heittoa on käytännössä ilmainen. Poikkeuksen
  luonti maksaa mikrosekunteja, ja pinojäljen syvyys kasvattaa hintaa.

## Itsearviointi

- Osaat kertoa tarkistetun ja tarkistamattoman poikkeuksen eron ja valita
  niiden välillä.
- Osaat kääriä poikkeuksen syyn kanssa ja tutkia syyketjua.
- Osaat käyttää `IOException`ia heittävää koodia lambdassa.
- Osaat perustella, miksi Javassa ei käytetä poikkeuksia odotettujen
  virheiden ilmaisemiseen.
- Osaat käyttää `Optional`ia oikein ja nimetä sen väärät käyttötavat.
- Osaat palauttaa virheet arvona suljetulla tulostyypillä.
