# Kokoelmat, virrat, tiedostot ja aika {.runko-kokoelmat}

Tähän asti esimerkit ovat käyttäneet listoja ja tauluja selittämättä
niitä. Tämä luku käy läpi standardikirjaston ytimen: kokoelmat ja
niiden valinnan, virrat, merkkijonojen käsittelyn, taulukoiden
apuvälineet, tiedostot ja ajan. Luku nojaa kahteen edelliseen:
kokoelmat ovat rajapintoja ja niiden toteutuksia (luku 5), ja niiden
käyttäytyminen ja hinta seuraavat siitä, että alkiot ovat viitteitä
olioihin (luku 6). Kokoelmien tyyppiparametrit (`List<String>`)
kertovat alkioiden tyypin; geneerisyys käsitellään tarkemmin luvussa 8.

## Kokoelmarajapinnat

Kokoelmakirjasto (`java.util`) erottaa rajapinnan toteutuksesta.
Muuttujan ja parametrin tyyppi on rajapinta (`List`, `Map`), ja
toteutus valitaan luontihetkellä:

```{.dot otsikko="Kokoelmakirjaston tärkeimmät rajapinnat (katkoviiva) ja toteutukset. Nuoli osoittaa yleisempään tyyppiin."}
digraph {
  rankdir=BT; nodesep=0.2; ranksep=0.4;
  node [fontsize=9, height=0.3];
  { node [style="rounded,dashed", fillcolor="white"];
    Iterable; Collection; SequencedCollection; List; Queue; Deque; Set;
    SequencedSet; SortedSet; }
  Collection -> Iterable;
  SequencedCollection -> Collection; Set -> Collection; Queue -> Collection;
  List -> SequencedCollection; Deque -> SequencedCollection; Deque -> Queue;
  SequencedSet -> SequencedCollection; SequencedSet -> Set;
  SortedSet -> SequencedSet;
  ArrayList -> List; ArrayDeque -> Deque; PriorityQueue -> Queue;
  HashSet -> Set; LinkedHashSet -> SequencedSet; TreeSet -> SortedSet;
}
```

```{.dot otsikko="`Map` ei ole `Collection`, vaan oma hierarkiansa."}
digraph {
  rankdir=BT; nodesep=0.2; ranksep=0.4;
  node [fontsize=9, height=0.3];
  { node [style="rounded,dashed", fillcolor="white"];
    Map; SequencedMap; SortedMap; }
  SequencedMap -> Map; SortedMap -> SequencedMap;
  HashMap -> Map; LinkedHashMap -> SequencedMap; TreeMap -> SortedMap;
}
```

| Rajapinta | Toteutus | Ominaisuudet |
|-----------|----------|--------------|
| `List` | `ArrayList` | taulukko; indeksointi O(1), lisäys loppuun tasoitetusti O(1) |
| `List` | `LinkedList` | linkitetty; käytännössä aina hitaampi kuin `ArrayList` |
| `Deque` | `ArrayDeque` | jono ja pino; korvaa `Stack`in ja `LinkedList`in |
| `Set`, `Map` | `HashSet`, `HashMap` | hajautus; O(1), ei järjestystä |
| `Set`, `Map` | `LinkedHashSet`, `LinkedHashMap` | hajautus ja lisäysjärjestys |
| `SortedMap` | `TreeMap`, `TreeSet` | punamusta puu; O(log n), järjestetty, alueet |
| `Queue` | `PriorityQueue` | binäärikeko; pienin ensin |
| `Map` | `EnumMap`, `EnumSet` | `enum`-avaimille; bittivektori, hyvin nopea |

`Vector`, `Hashtable` ja `Stack` ovat Java 1.0:n synkronoituja
luokkia, joita ei käytetä uudessa koodissa. Järjestetyt kokoelmat
(`List`, `Deque`, `LinkedHashMap`, `TreeMap`) toteuttavat Java 21:stä
lähtien `SequencedCollection`-rajapinnan, jossa on `getFirst`,
`getLast` ja `reversed`.

## Muuttumattomat kokoelmat, näkymät ja kopiot

`List.of`, `Set.of`, `Map.of` ja `List.copyOf` (Java 9–10) luovat
muuttumattomia kokoelmia, jotka eivät hyväksy `null`-alkioita.
`Collections.unmodifiableList` on vain *näkymä*: alkuperäisen listan
muutokset näkyvät sen kautta. `Arrays.asList` on taulukon päälle
rakennettu kiinteäkokoinen lista:

```{.java tiedosto="esimerkit/07-nakymat.java" osa="kaytto"}
```

```{.java tiedosto="esimerkit/07-nakymat.java" osa="jarjestys"}
```

```{.tuloste tiedosto="esimerkit/07-nakymat.odotettu"}
```

Kun luokka palauttaa sisäisen listansa, se palauttaa kopion
(`List.copyOf`), ei näkymää. Muuten kutsuja näkee myöhemmät muutokset,
ja säikeiden välillä syntyy kilpailutilanne.

## Hajautus ja avaimet

Hajautustaulu jakaa alkiot lokeroihin avaimen `hashCode`-arvon mukaan
ja vertaa lokeron sisällä avaimia `equals`-metodilla. `HashMap` ja
`HashSet` luottavat siksi kahteen sääntöön. Ensimmäinen on luvussa 6
nähty sopimus: oliot, jotka ovat `equals`-mielessä samat, antavat
saman `hashCode`n; muuten sama avain päätyy kahteen lokeroon. Toinen
on, että avaimen hajautusarvo ei muutu sen ollessa taulussa. Toisen
säännön rikkominen hukkaa alkion:

```{.java tiedosto="esimerkit/07-avain.java" osa="luokka"}
```

```{.java tiedosto="esimerkit/07-avain.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-avain.odotettu"}
```

Alkio on tallessa lokerossa, joka vastaa vanhaa sähköpostiosoitetta,
mutta haku laskee uuden osoitteen lokeron. Ratkaisu on, että avaimet
ovat muuttumattomia: `record`, `String`, `Integer` tai pysyvä tunniste.

## Kokoelman muuttaminen läpikäynnin aikana

For-each-silmukka käyttää iteraattoria. Jos kokoelmaa muutetaan muuten
kuin iteraattorin kautta, iteraattori heittää
`ConcurrentModificationException`in, kun se huomaa muutoksen:

```{.java tiedosto="esimerkit/07-muutos.kaatuu.java" osa="koodi"}
```

```
Exception in thread "main" java.util.ConcurrentModificationException
```

Nimestään huolimatta virhe ei liity säikeisiin. Tarkistus tehdään
parhaan yrityksen periaatteella: jos poistettava alkio on toiseksi
viimeinen, silmukka päättyy hiljaa, ja viimeinen alkio jää käsittelemättä.
Oikeat tavat ovat `removeIf(t -> t.endsWith("peruttu"))`,
`Iterator.remove()` tai uuden kokoelman rakentaminen virralla.

## Virrat (*streams*)

`Stream` on laiska alkioiden jono, jota muunnetaan välivaiheilla
(`filter`, `map`, `flatMap`, `sorted`, `distinct`, `limit`) ja joka
kootaan päätösoperaatiolla (`collect`, `toList`, `reduce`, `count`,
`forEach`). `Collectors` sisältää ryhmittelyn ja koosteet:

```{.java tiedosto="esimerkit/07-myynti.java" osa="ryhmittely"}
```

```{.java tiedosto="esimerkit/07-myynti.java" osa="paras"}
```

`toMap` tarvitsee yhdistämisfunktion, kun sama avain voi esiintyä
useasti; ilman sitä se heittää `IllegalStateException`in. Saman voi
kirjoittaa silmukalla ja `Map.merge`llä:

```{.java tiedosto="esimerkit/07-myynti.java" osa="tomap"}
```

```{.java tiedosto="esimerkit/07-myynti.java" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/07-myynti.odotettu"}
```

Kumpi on parempi? Virta on selkeä, kun käsittely on putki
suodatuksesta koosteeseen. Silmukka on selkeämpi, kun käsittelyssä on
monta tilaa, aikainen poistuminen, poikkeuksia tai sivuvaikutuksia.
Virta on kuumassa silmukassa yleensä hieman hitaampi kuin silmukka,
koska siinä on lambdoja ja välitason olioita, ja `parallel()` auttaa
vain suurilla, CPU-sidonnaisilla aineistoilla.

## Merkkijonot

Merkkijonon käsittelyssä toistuvat samat sudenkuopat:

```{.java tiedosto="esimerkit/07-merkkijonot.java" osa="split"}
```

`split` ottaa säännöllisen lausekkeen, joten piste on mikä tahansa
merkki ja on suojattava (`"\\."`). Ilman negatiivista rajaa tyhjät
loppukentät poistetaan. Merkkijonon kokoaminen silmukassa `+`-operaattorilla
luo joka kierroksella uuden olion, joten käytetään `StringBuilder`iä,
`String.join`ia tai `Collectors.joining`ia:

```{.java tiedosto="esimerkit/07-merkkijonot.java" osa="kokoaminen"}
```

```{.java tiedosto="esimerkit/07-merkkijonot.java" osa="muut"}
```

```{.tuloste tiedosto="esimerkit/07-merkkijonot.odotettu"}
```

## Algoritmit kirjastossa

`Collections.sort` ja `List.sort` ovat vakaita (TimSort, O(n log n)).
`Arrays.sort` primitiiveille on epävakaa kahden pivotin pikalajittelu.
Vertailijat kootaan ketjuksi: `Comparator.comparing(Tilaus::asiakas)
.thenComparing(Tilaus::summa, Comparator.reverseOrder())`. Tyyppi,
jolla on yksi luonteva järjestys (versio, päivämäärä, rahasumma),
toteuttaa rajapinnan `Comparable<T>` ja sen metodin `compareTo`;
silloin `sort(null)`, `TreeMap` ja `Collections.max` toimivat ilman
vertailijaa. `Collections.binarySearch` vaatii lajitellun listan.
`PriorityQueue` on keko, jonka iterointijärjestys ei ole lajiteltu:
alkiot otetaan järjestyksessä `poll`illa. Yleiset algoritmit ja
tietorakenteet käsitellään taidoissa *Tietorakenteet* ja *Algoritmit*.

## Taulukot kirjastossa

Luku 3 esitteli taulukon. Apuluokka `Arrays` tarjoaa taulukoille
lajittelun, puolitushaun, kopioinnin ja virran:

```{.java tiedosto="esimerkit/07-taulukot.java" osa="arrays"}
```

```{.tuloste tiedosto="esimerkit/07-taulukot.odotettu" rivit="1-2"}
```

Taulukon ja kokoelman välillä muunnetaan usein, koska vanhat
rajapinnat käyttävät taulukoita. `Arrays.asList` on näkymä, jonka
kautta taulukon muutokset näkyvät; `List.of(taulukko)` kopioi:

```{.java tiedosto="esimerkit/07-taulukot.java" osa="muunnos"}
```

```{.tuloste tiedosto="esimerkit/07-taulukot.odotettu" rivit="3-4"}
```

Taulukot ovat *kovariantteja*: `String[]` kelpaa `Object[]`-tyyppiseen
muuttujaan. Kääntäjä ei siksi voi estää väärän tyyppistä sijoitusta,
vaan JVM tarkistaa jokaisen viitetaulukkoon kirjoituksen ajon aikana:

```{.java tiedosto="esimerkit/07-taulukot.java" osa="kovarianssi"}
```

```{.tuloste tiedosto="esimerkit/07-taulukot.odotettu" rivit="5-5"}
```

Geneeriset kokoelmat korjaavat tämän: `List<String>` ei kelpaa
`List<Object>`-tyyppiseen muuttujaan, joten sama virhe on
käännösvirhe (luku 8). Tämä on yksi syy suosia listoja
viitetyyppisten alkioiden säiliönä.

## Tiedostot: `java.nio.file`

Tiedostoja käsitellään kahdella tyypillä: `Path` on polku ja `Files`
kokoelma staattisia metodeja, jotka tekevät polulle jotain. Vanhaa
`java.io.File`-luokkaa ei käytetä uudessa koodissa, koska sen metodit
palauttavat virheestä `false`-arvon eivätkä kerro syytä. `Path` on
muuttumaton arvo, eikä sen luominen koske levyyn:

```{.java tiedosto="esimerkit/07-tiedostot.java" osa="polku"}
```

```{.tuloste tiedosto="esimerkit/07-tiedostot.odotettu" rivit="1-1"}
```

Pienen tiedoston voi kirjoittaa ja lukea yhdellä kutsulla
(`writeString`, `readString`, `readAllLines`). Suuri tiedosto
käsitellään virtana: `newBufferedWriter` ja `newBufferedReader`
puskuroivat, ja `Files.lines` lukee rivit laiskasti. Kaikki kolme
pitävät tiedoston auki, joten ne avataan `try`-with-resources-lohkossa
(luku 6):

```{.java tiedosto="esimerkit/07-tiedostot.java" osa="kirjoitus"}
```

```{.java tiedosto="esimerkit/07-tiedostot.java" osa="luku"}
```

```{.tuloste tiedosto="esimerkit/07-tiedostot.odotettu" rivit="2-4"}
```

Hakemistoja luetaan metodeilla `Files.list` (yksi taso) ja
`Files.walk` (koko puu). Nekin palauttavat suljettavan virran.
Virheet ovat `IOException`in aliluokkia, jotka kertovat syyn ja polun:

```{.java tiedosto="esimerkit/07-tiedostot.java" osa="hakemisto"}
```

```{.tuloste tiedosto="esimerkit/07-tiedostot.odotettu" rivit="5-7"}
```

Huomioita:

- Merkistö annetaan aina. `Files`-metodien oletus on UTF-8, mutta
  eksplisiittinen `UTF_8` kertoo lukijalle, että asia on mietitty.
- Älä tarkista ensin, onko tiedosto olemassa (`Files.exists`), ja avaa
  sitä sitten: tiedosto voi kadota välissä. Avaa tiedosto ja käsittele
  `NoSuchFileException`.
- `Files.move` valitsimella `ATOMIC_MOVE` on tapa julkaista tiedosto
  kerralla: kirjoita väliaikaiseen tiedostoon samaan hakemistoon ja
  siirrä se lopuksi paikalleen.
- Binääridata luetaan ja kirjoitetaan metodeilla `readAllBytes`,
  `newInputStream` ja `newOutputStream`.

## Aika: `java.time`

Pakkaus `java.time` (Java 8) erottaa toisistaan asiat, jotka vanhat
luokat `Date` ja `Calendar` sekoittivat: hetken aikajanalla,
kalenteripäivän ja kellonajan ilman aikavyöhykettä sekä näiden
yhdistelmän vyöhykkeen kanssa. Kaikki tyypit ovat muuttumattomia,
joten `plus`-metodit palauttavat uuden olion.

| Tyyppi | Mitä kuvaa | Käyttö |
|--------|------------|--------|
| `Instant` | hetki aikajanalla (UTC) | aikaleimat, lokit, tietokannan sarakkeet |
| `Duration` | aikaväli sekunteina ja nanosekunteina | aikarajat, kestot |
| `LocalDate`, `LocalTime`, `LocalDateTime` | päivä ja kellonaika ilman vyöhykettä | syntymäpäivä, eräpäivä, aukioloaika |
| `Period` | kalenteriväli vuosina, kuukausina ja päivinä | "kolmen kuukauden kuluttua" |
| `ZonedDateTime`, `ZoneId` | paikallinen aika ja aikavyöhyke | tapaamiset, aikataulut, näyttö käyttäjälle |

Koneen aika on `Instant` ja kesto `Duration`. Laskenta on tarkkaa,
koska kalenteri ei vaikuta siihen:

```{.java tiedosto="esimerkit/07-aika.java" osa="hetki"}
```

```{.tuloste tiedosto="esimerkit/07-aika.odotettu" rivit="1-1"}
```

Kalenterilaskenta tehdään `LocalDate`lla. Kuukauden lisäys tammikuun
31. päivään antaa helmikuun viimeisen päivän, ei virhettä:

```{.java tiedosto="esimerkit/07-aika.java" osa="paiva"}
```

```{.tuloste tiedosto="esimerkit/07-aika.odotettu" rivit="2-2"}
```

Aikavyöhyke tarvitaan, kun paikallinen aika muunnetaan hetkeksi tai
toisin päin. Vyöhyke on nimi (`Europe/Helsinki`), ei kiinteä siirtymä,
koska siirtymä vaihtuu kesäaikaan siirryttäessä. Esimerkissä kuuden
tunnin matkan aikana kelloja siirretään, joten paikallinen kello
näyttää perillä seitsemän tuntia enemmän:

```{.java tiedosto="esimerkit/07-aika.java" osa="vyohyke"}
```

```{.tuloste tiedosto="esimerkit/07-aika.odotettu" rivit="3-4"}
```

Muotoilu ja jäsennys tehdään `DateTimeFormatter`illa, joka on
säieturvallinen toisin kuin vanha `SimpleDateFormat`. Koneelle
tarkoitettu aika kirjoitetaan ISO 8601 -muodossa, käyttäjälle näkyvä
aika käyttäjän kieliasetuksella:

```{.java tiedosto="esimerkit/07-aika.java" osa="muotoilu"}
```

```{.tuloste tiedosto="esimerkit/07-aika.odotettu" rivit="5-7"}
```

Nykyhetki luetaan metodilla `Instant.now()` tai `LocalDate.now(vyohyke)`.
Koodi, jonka toiminta riippuu ajasta, ottaa kellon parametrina
(`Clock`), jotta testi voi asettaa ajan (luku 10). Kestojen
mittaamiseen käytetään `System.nanoTime()`a, koska seinäkello voi
siirtyä.

## Käytännössä

- **Rajapinta tyypiksi, toteutus luontiin.** `List<Tilaus> t = new
  ArrayList<>()`. Parametrin tyypiksi riittävä yleinen rajapinta
  (`Collection`, `Iterable`).
- **Oletusvalinnat:** `ArrayList`, `HashMap`, `ArrayDeque`. `TreeMap`,
  kun tarvitaan järjestys tai aluehaku, `LinkedHashMap`, kun
  lisäysjärjestyksellä on väliä. `LinkedList`iä ei juuri koskaan.
- **Palauta muuttumattomia kokoelmia.** `List.copyOf`, `toList()` (Java
  16, muuttumaton) ja `Map.copyOf`. Palauta tyhjä kokoelma, älä
  `null`ia.
- **Avaimet muuttumattomiksi.** Hajautustaulun avain on `record`,
  merkkijono tai tunniste.
- **`Map.merge`, `computeIfAbsent` ja `getOrDefault`.** Ne korvaavat
  "hae, tarkista, aseta" -kuvion ja ovat `ConcurrentHashMap`issa
  atomisia (luku 11).
- **Virta putkille, silmukka logiikalle.** Älä tee sivuvaikutuksia
  `map`issa tai `filter`issä. `forEach` on päätösoperaatio tulostukselle
  ja vastaavalle, ei tilan keräämiselle.
- **Tallenna hetket UTC:nä, näytä vyöhykkeessä.** `Instant`
  tietokantaan ja lokiin; `ZonedDateTime` vasta, kun aika näytetään
  ihmiselle tai kun sääntö on sidottu paikalliseen aikaan (kauppa
  aukeaa kello 9). `Date` ja `Calendar` vain vanhojen rajapintojen
  rajalla (`Date.from(instant)`, `date.toInstant()`).
- **`Path` ja `Files`, merkistö mukana.** Tiedostot ja hakemistovirrat
  `try`-lohkoon.
- **Hinta.** `HashMap` kasvaa tuplaamalla; anna kapasiteetti, jos koko
  tiedetään. Jokainen `Integer`-avain on olio. Hajautustaulun haku
  kutsuu `hashCode`a ja `equals`ia, joten ne pidetään halpoina.

## Itsearviointi

- Osaat valita kokoelman toteutuksen tehtävän ja aikavaativuuden mukaan.
- Osaat kertoa eron muuttumattoman kokoelman, näkymän ja kopion välillä.
- Osaat selittää, miksi muuttuva hajautusavain hukkaa alkion.
- Osaat poistaa alkioita kokoelmasta läpikäynnin aikana oikein.
- Osaat kirjoittaa ryhmittelyn ja koosteen sekä virralla että
  silmukalla ja perustella valinnan.
- Osaat välttää `split`in ja merkkijonojen kokoamisen sudenkuopat.
- Osaat kertoa, miksi `String[]` kelpaa `Object[]`-muuttujaan mutta
  `List<String>` ei `List<Object>`-muuttujaan.
- Osaat lukea ja kirjoittaa tekstitiedoston ja käydä hakemistopuun
  läpi niin, että tiedostot suljetaan.
- Osaat valita tyypin hetkelle, kestolle, päivämäärälle ja
  vyöhykkeelliselle ajalle ja kertoa, miksi vyöhyke ei ole kiinteä
  siirtymä.
