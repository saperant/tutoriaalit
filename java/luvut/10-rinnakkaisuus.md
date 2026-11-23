# Säikeet, virtuaalisäikeet ja java.util.concurrent {.runko-rinnakkaisuus}

Tämä luku käsittelee Javan rinnakkaisuuden välineet. Yleiset käsitteet,
kuten kilpailutilanne, lukkiutuminen ja muistimallit, käsitellään
taidossa *Rinnakkaisohjelmointi*.

## Säikeet ja suorittajat

Javan säie (`Thread`) on perinteisesti käyttöjärjestelmän säie, jolla on
oma pino (oletuksena 1 Mt varattua muistia). Säikeitä ei luoda
tehtäväkohtaisesti, vaan tehtävät annetaan *suorittajalle*
(`ExecutorService`), joka hallitsee säiealtaan ja palauttaa
`Future`-olion tulosta varten.

Java 21:n *virtuaalisäie* on JVM:n hallitsema kevyt säie. Kun se odottaa
I/O:ta, lukkoa tai `sleep`-kutsua, JVM irrottaa sen käyttöjärjestelmän
säikeestä, joka voi sillä välin ajaa muita virtuaalisäikeitä.
Virtuaalisäikeitä voi olla miljoonia, joten tavallista, peräkkäin
kirjoitettua estävää koodia voi ajaa säie pyyntöä kohden:

```{.java tiedosto="esimerkit/10-virtuaali.java" osa="haku"}
```

```{.java tiedosto="esimerkit/10-virtuaali.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-virtuaali.odotettu"}
```

Kymmenentuhatta 50 millisekunnin odotusta valmistuu noin sekunnissa.
Perinteisellä 200 säikeen altaalla sama veisi 2,5 sekuntia, ja
10 000 käyttöjärjestelmän säiettä veisi gigatavuja varattua muistia.
`ExecutorService` on Java 19:stä lähtien `AutoCloseable`, ja `close`
odottaa tehtävien valmistumista.

Virtuaalisäikeet eivät nopeuta laskentaa: CPU-sidonnainen työ
tarvitsee edelleen enintään ytimien määrän verran säikeitä
(`Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors())`
tai `parallel()`-virta). Java 21:ssä `synchronized`-lohkossa odottava
virtuaalisäie sitoo käyttöjärjestelmän säikeen (*pinning*). Siksi
pitkät odotukset lukon sisällä tehdään `ReentrantLock`illa; Java 24
poisti tämän rajoituksen.

## Jaettu tila

Kun useampi säie muuttaa samaa muuttujaa, `arvo++` (lue, kasvata,
kirjoita) menettää päivityksiä. Lisäksi Javan muistimalli ei takaa, että
toisen säikeen kirjoitus näkyy lainkaan, ellei kirjoituksen ja lukemisen
välillä ole *happens-before*-suhdetta. Suhde syntyy lukosta
(`synchronized`, `Lock`), `volatile`-kentästä, säikeen käynnistyksestä
ja `join`ista sekä `java.util.concurrent`-rakenteista. Kolme oikeaa
laskuria:

```{.java tiedosto="esimerkit/10-laskurit.java" osa="laskurit"}
```

```{.java tiedosto="esimerkit/10-laskurit.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-laskurit.odotettu"}
```

| Väline | Milloin |
|--------|---------|
| `synchronized` | invariantti, joka koskee useaa kenttää; lyhyet kriittiset alueet |
| `ReentrantLock` | aikakatkaisu (`tryLock`), keskeytettävä odotus, useampi ehto |
| `AtomicLong`, `AtomicReference` | yksi arvo; vertaa ja vaihda (`compareAndSet`, `updateAndGet`) |
| `LongAdder` | laskuri, jota monet säikeet kasvattavat ja harvoin luetaan |
| `volatile` | lippu tai julkaistu muuttumaton olio; ei yhdistettyjä operaatioita |
| `ConcurrentHashMap` | jaettu taulu; `merge` ja `computeIfAbsent` ovat atomisia |

`LongAdder` jakaa laskurin säiekohtaisiin soluihin, joten se ei kilpaile
välimuistirivistä kuten `AtomicLong`. Paras jaettu tila on kuitenkin
muuttumaton tila: `record`, `List.copyOf` ja säikeen sisäiset tulokset,
jotka yhdistetään lopuksi.

## Jonot: tuottaja ja kuluttaja

`BlockingQueue` siirtää työn säikeeltä toiselle ja hoitaa odotuksen.
Rajattu jono (`ArrayBlockingQueue`) antaa *vastapainetta*: kun
kuluttajat eivät ehdi, tuottaja odottaa `put`issa eikä muisti kasva.
Kuluttajat lopetetaan lähettämällä jokaiselle lopetusviesti (*poison
pill*):

```{.java tiedosto="esimerkit/10-jono.java" osa="tyypit"}
```

```{.java tiedosto="esimerkit/10-jono.java" osa="kuluttaja"}
```

```{.java tiedosto="esimerkit/10-jono.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-jono.odotettu"}
```

Viesti on suljettu tyyppi, joten lopetusviesti ei ole erikoisarvo
(esim. `-1`) vaan oma tapauksensa, jonka `switch` pakottaa käsittelemään.

## `CompletableFuture` ja atomiset taulut

`CompletableFuture` yhdistää asynkronisia tuloksia: `thenApply` muuntaa,
`thenCombine` yhdistää kaksi, `exceptionally` korvaa virheen ja
`orTimeout` asettaa aikarajan. Ketju ei estä säiettä ennen
viimeistä `join`ia:

```{.java tiedosto="esimerkit/10-yhdistelma.java" osa="palvelut"}
```

```{.java tiedosto="esimerkit/10-yhdistelma.java" osa="ketju"}
```

`ConcurrentHashMap.computeIfAbsent` laskee puuttuvan arvon atomisesti:
vaikka sata tehtävää pyytää kahta avainta yhtä aikaa, kumpikin arvo
lasketaan vain kerran. Ehto "jos puuttuu, laske ja lisää" kahtena
erillisenä kutsuna (`containsKey` + `put`) laskisi arvon useasti:

```{.java tiedosto="esimerkit/10-yhdistelma.java" osa="muisti"}
```

```{.tuloste tiedosto="esimerkit/10-yhdistelma.odotettu"}
```

Virtuaalisäikeiden myötä moni `CompletableFuture`-ketju on
yksinkertaisempi kirjoittaa estävänä koodina virtuaalisäikeessä.
*Rakenteinen rinnakkaisuus* (`StructuredTaskScope`) ja *scoped values*
ovat Java 21:ssä esikatseluominaisuuksia; jälkimmäinen valmistui Java
25:ssä.

## Käytännössä

- **Suorittaja, ei `new Thread`.** Tehtävät annetaan
  `ExecutorService`lle, joka suljetaan `try`-lohkossa. I/O-työ:
  `newVirtualThreadPerTaskExecutor()`. CPU-työ: kiinteä allas ytimien
  mukaan.
- **Muuttumaton data säikeiden välillä.** Jaa `record`eja ja
  muuttumattomia kokoelmia. Kun tila on jaettava, kapseloi se yhteen
  luokkaan, jonka kaikki metodit synkronoidaan.
- **Valmiit rakenteet omien sijaan.** `ConcurrentHashMap`,
  `BlockingQueue`, `CountDownLatch`, `Semaphore`, `LongAdder`.
  `wait`/`notify` ovat matalan tason primitiivejä, joita ei tarvita.
- **Rajattu jono ja vastapaine.** Rajaton jono siirtää ylikuorman
  muistiin ja lopulta `OutOfMemoryError`iin.
- **Aikaraja jokaiseen odotukseen.** `future.get(1, SECONDS)`,
  `orTimeout`, `awaitTermination`. Ilman aikarajaa jumittunut palvelu
  jumittaa kutsujankin.
- **Keskeytys on peruutus.** Käsittele `InterruptedException` lopettamalla
  työ, ei jatkamalla.
- **Hinta.** Kilpailematon lukko maksaa kymmeniä nanosekunteja;
  kilpailtu lukko pysäyttää säikeen ja vaihtaa kontekstia
  (mikrosekunteja). Virtuaalisäikeen luonti on halvempaa kuin
  altaan käyttö, joten virtuaalisäikeitä ei kierrätetä altaassa.

## Itsearviointi

- Osaat ajaa tuhansia I/O-tehtäviä virtuaalisäikeillä ja kertoa, miksi
  ne eivät nopeuta laskentaa.
- Osaat selittää *happens-before*-suhteen ja nimetä tavat, joilla se
  syntyy.
- Osaat valita jaetulle laskurille tai taululle oikean välineen.
- Osaat toteuttaa tuottaja–kuluttaja-mallin rajatulla jonolla ja
  lopetusviestillä.
- Osaat yhdistää asynkronisia tuloksia `CompletableFuture`lla ja käsitellä
  niiden virheet ja aikarajat.
