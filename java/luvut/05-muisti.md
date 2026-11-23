# Muisti, roskienkeruu ja JIT {.runko-muisti}

## Pino, keko ja viitteet

Jokaisella säikeellä on oma pinonsa, jossa ovat metodien paikalliset
muuttujat: primitiivit ja viitteet. Kaikki oliot ovat keossa (*heap*),
jonka roskienkerääjä hallitsee. Muuttuja ei koskaan sisällä oliota,
vain viitteen siihen. Sijoitus `b = a` kopioi viitteen, ei oliota.

Siksi vertailuoperaattori `==` vertaa viitteitä eli sitä, onko kyse
samasta oliosta. Arvojen yhtäsuuruus kysytään `equals`-metodilla:

```{.java tiedosto="esimerkit/05-vertailu.java" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/05-vertailu.odotettu"}
```

`Integer.valueOf` (ja automaattinen boksaus) palauttaa välimuistista
saman olion arvoille −128…127. Siksi `127 == 127` on tosi mutta
`128 == 128` epätosi. Virhe on salakavala, koska testit pienillä
luvuilla menevät läpi. Luokan `equals` ja `hashCode` toteutetaan aina
yhdessä samoista kentistä:

```{.java tiedosto="esimerkit/05-vertailu.java" osa="luokka"}
```

`record` tuottaa samat metodit automaattisesti, joten arvoluokat
kirjoitetaan `record`eina (luku 7).

## Boksaus ja `null`

Geneeriset kokoelmat sisältävät vain olioita, joten `List<Integer>`
sisältää viitteitä `Integer`-olioihin. Kääntäjä muuntaa primitiivin
olioksi (*boxing*) ja takaisin (*unboxing*) automaattisesti. Muunnos
olion `null`-arvosta primitiiviksi kaatuu:

```{.java tiedosto="esimerkit/05-nolla.kaatuu.java" osa="koodi"}
```

```
ruuveja 120
Exception in thread "main" java.lang.NullPointerException: Cannot invoke
"java.lang.Integer.intValue()" because the return value of
"java.util.Map.get(Object)" is null
```

Java 14:stä lähtien `NullPointerException` kertoo, mikä arvo oli
`null`. Korjaus on `saldot.getOrDefault("tulppa", 0)` tai
`Optional` (luku 8).

Boksauksella on myös hinta. `List<Integer>` on taulukko viitteitä
olioihin, joista jokaisella on otsake (12–16 tavua) ja arvo. Läpikäynti
seuraa viitteitä eri puolille kekoa, kun taas `int[]` on yhtenäinen
muistialue, jonka prosessori lukee peräkkäin ja JIT voi vektoroida:

```{.java tiedosto="esimerkit/05-hinta.java" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/05-hinta.odotettu"}
```

Tyypillisellä koneella ero on noin 5–10-kertainen, ja `List<Integer>`
vie noin neljä kertaa enemmän muistia. Kuumassa koodissa käytetään siis
primitiivitaulukoita tai primitiivivirtoja (`IntStream`, `mapToInt`).

## Roskienkeruu

Roskienkerääjä vapauttaa oliot, joihin ei pääse mistään *juuresta*
(pinon muuttujat, staattiset kentät, aktiiviset säikeet). Useimmat
oliot kuolevat nuorina, joten keko on jaettu sukupolviin: nuori
sukupolvi kerätään usein ja nopeasti kopioimalla elävät oliot talteen.
Olion luonti on siksi halpaa, yleensä vain osoittimen siirto säikeen
omassa allokointipuskurissa.

| Kerääjä | Valitsin | Tavoite |
|---------|----------|---------|
| G1 | oletus | tasapaino läpäisykyvyn ja taukojen välillä (tavoite 200 ms) |
| ZGC | `-XX:+UseZGC` | alle millisekunnin tauot suurillakin keoilla |
| Parallel | `-XX:+UseParallelGC` | suurin läpäisykyky eräajoissa |
| Serial | `-XX:+UseSerialGC` | pienet keot ja kontit, joissa on yksi prosessori |

Keon koko asetetaan valitsimilla `-Xms` ja `-Xmx` tai kontissa
suhteellisesti (`-XX:MaxRAMPercentage=75`). JVM tunnistaa kontin
muistirajan.

## Muistivuodot Javassa

Roskienkeruu ei estä vuotoja: olio, johon viitataan, ei vapaudu, vaikka
sitä ei enää tarvita. Tavallisimmat syyt ovat rajaton välimuisti
staattisessa taulussa, kuuntelijat, joita ei poisteta, ja
`ThreadLocal`-arvot säiealtaissa. Välimuistille annetaan aina koko- tai
aikaraja:

```{.java tiedosto="esimerkit/05-valimuisti.java" osa="lru"}
```

```{.java tiedosto="esimerkit/05-valimuisti.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-valimuisti.odotettu"}
```

`LinkedHashMap` pitää alkiot käyttöjärjestyksessä, kun konstruktorin
kolmas parametri on `true`, ja `removeEldestEntry` poistaa vanhimman.
Luokka on `Serializable`, joten `-Xlint:all` vaatii nimettömälle
aliluokalle `serialVersionUID`-kentän. Tuotannossa käytetään valmista
kirjastoa, kuten Caffeine, joka on myös säieturvallinen.

## Resurssit: `try`-with-resources

Roskienkerääjä vapauttaa muistin, mutta ei sulje tiedostoja, yhteyksiä
tai lukkoja, eikä keruun ajankohtaa voi ennustaa. Muut resurssit
suljetaan deterministisesti `try`-lohkolla, jonka otsakkeessa luodut
`AutoCloseable`-oliot suljetaan lohkon lopussa käänteisessä
järjestyksessä:

```{.java tiedosto="esimerkit/05-resurssit.java" osa="resurssi"}
```

```{.java tiedosto="esimerkit/05-resurssit.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-resurssit.odotettu"}
```

Kun sekä lohko että `close` heittävät poikkeuksen, lohkon poikkeus
säilyy ja sulkemisen poikkeus liitetään siihen *tukahdutettuna*
(`getSuppressed`). Näin alkuperäinen syy ei katoa. `finalize`-metodia
ei pidä käyttää; se on vanhentunut ja poistumassa.

## JIT ja lämpeneminen

JVM tulkkaa tavukoodia aluksi ja laskee, mitä metodeja ja silmukoita
ajetaan paljon. Kuumat metodit käännetään ensin nopeasti (C1) ja sitten
profiilin perusteella optimoiden (C2). Optimoinnit perustuvat
havaittuun käytökseen: rajapintakutsu, jolla on yksi toteutus,
inlinoidaan, ja olio, joka ei pakene metodista, voidaan purkaa
kentiksi rekistereihin (*escape analysis*). Jos oletus myöhemmin
rikkoutuu, koodi palautetaan tulkattavaksi (*deoptimization*).

Siksi mittaus ilman lämmittelyä mittaa tulkkia. `05-hinta.java`
toistaa mittauksen 25 kertaa ja käyttää parasta aikaa. Luotettavaan
mittaukseen tarvitaan silti JMH (*Java Microbenchmark Harness*), joka
hoitaa lämmittelyn, haarukoinnin erillisiin JVM:iin ja kuolleen koodin
poiston estämisen (luku 11).

## Käytännössä

- **`equals` olioille, `==` primitiiveille ja `enum`eille.** IDE:t ja
  staattinen analyysi varoittavat `==`-vertailusta merkkijonoille ja
  kääreille.
- **Arvoluokat `record`eina.** Käsin kirjoitetut `equals` ja `hashCode`
  ovat yleinen virhelähde, ja ne unohtuu päivittää, kun kenttä lisätään.
- **Vältä boksausta kuumassa koodissa.** `int[]`, `IntStream`,
  `mapToInt`, `LongAdder`. Muualla selkeys voittaa.
- **Jokaisella välimuistilla on raja.** Rajaton `static Map` on
  muistivuoto, joka ilmenee vasta tuotannossa viikkojen päästä.
- **Kaikki `AutoCloseable` `try`-lohkoon.** Myös `ExecutorService`
  (Java 19), `Stream` tiedostoista (`Files.lines`) ja JDBC-oliot.
- **Älä optimoi arvaamalla.** Mittaa JFR:llä tai JMH:lla. JIT poistaa
  usein juuri sen, mitä yrität optimoida käsin.
- **Hinta.** Allokaatio on halpaa, mutta roskienkeruun työ kasvaa
  elävien olioiden määrän mukana. Suuret, pitkäikäiset rakenteet
  (välimuistit) maksavat eniten.

## Itsearviointi

- Osaat kertoa, mitä muuttuja sisältää, ja milloin `==` ja `equals`
  antavat eri tuloksen.
- Osaat selittää boksauksen hinnan ja `null`-purun vaaran.
- Osaat nimetä roskienkerääjät ja tavallisimmat muistivuotojen syyt.
- Osaat sulkea resurssit `try`-with-resources-lohkolla ja tulkita
  tukahdutetut poikkeukset.
- Osaat kertoa, miksi mikrovertailu ilman lämmittelyä on harhaanjohtava.
