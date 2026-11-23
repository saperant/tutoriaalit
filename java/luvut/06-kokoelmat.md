# Kokoelmat, merkkijonot ja virrat {.runko-kokoelmat}

## Kokoelmarajapinnat

Kokoelmakirjasto (`java.util`) erottaa rajapinnan toteutuksesta.
Muuttujan ja parametrin tyyppi on rajapinta (`List`, `Map`), ja
toteutus valitaan luontihetkellä:

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

```{.java tiedosto="esimerkit/06-nakymat.java" osa="kaytto"}
```

```{.java tiedosto="esimerkit/06-nakymat.java" osa="jarjestys"}
```

```{.tuloste tiedosto="esimerkit/06-nakymat.odotettu"}
```

Kun luokka palauttaa sisäisen listansa, se palauttaa kopion
(`List.copyOf`), ei näkymää. Muuten kutsuja näkee myöhemmät muutokset,
ja säikeiden välillä syntyy kilpailutilanne.

## Hajautus ja avaimet

`HashMap` ja `HashSet` luottavat kahteen sääntöön: samat oliot
(`equals`) antavat saman `hashCode`n, ja avaimen hajautusarvo ei muutu
sen ollessa taulussa. Toisen säännön rikkominen hukkaa alkion:

```{.java tiedosto="esimerkit/06-avain.java" osa="luokka"}
```

```{.java tiedosto="esimerkit/06-avain.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-avain.odotettu"}
```

Alkio on tallessa lokerossa, joka vastaa vanhaa sähköpostiosoitetta,
mutta haku laskee uuden osoitteen lokeron. Ratkaisu on, että avaimet
ovat muuttumattomia: `record`, `String`, `Integer` tai pysyvä tunniste.

## Kokoelman muuttaminen läpikäynnin aikana

For-each-silmukka käyttää iteraattoria. Jos kokoelmaa muutetaan muuten
kuin iteraattorin kautta, iteraattori heittää
`ConcurrentModificationException`in, kun se huomaa muutoksen:

```{.java tiedosto="esimerkit/06-muutos.kaatuu.java" osa="koodi"}
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

```{.java tiedosto="esimerkit/06-myynti.java" osa="ryhmittely"}
```

```{.java tiedosto="esimerkit/06-myynti.java" osa="paras"}
```

`toMap` tarvitsee yhdistämisfunktion, kun sama avain voi esiintyä
useasti; ilman sitä se heittää `IllegalStateException`in. Saman voi
kirjoittaa silmukalla ja `Map.merge`llä:

```{.java tiedosto="esimerkit/06-myynti.java" osa="tomap"}
```

```{.java tiedosto="esimerkit/06-myynti.java" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/06-myynti.odotettu"}
```

Kumpi on parempi? Virta on selkeä, kun käsittely on putki
suodatuksesta koosteeseen. Silmukka on selkeämpi, kun käsittelyssä on
monta tilaa, aikainen poistuminen, poikkeuksia tai sivuvaikutuksia.
Virta on kuumassa silmukassa yleensä hieman hitaampi kuin silmukka,
koska siinä on lambdoja ja välitason olioita, ja `parallel()` auttaa
vain suurilla, CPU-sidonnaisilla aineistoilla.

## Merkkijonot

Merkkijonon käsittelyssä toistuvat samat sudenkuopat:

```{.java tiedosto="esimerkit/06-merkkijonot.java" osa="split"}
```

`split` ottaa säännöllisen lausekkeen, joten piste on mikä tahansa
merkki ja on suojattava (`"\\."`). Ilman negatiivista rajaa tyhjät
loppukentät poistetaan. Merkkijonon kokoaminen silmukassa `+`-operaattorilla
luo joka kierroksella uuden olion, joten käytetään `StringBuilder`iä,
`String.join`ia tai `Collectors.joining`ia:

```{.java tiedosto="esimerkit/06-merkkijonot.java" osa="kokoaminen"}
```

```{.java tiedosto="esimerkit/06-merkkijonot.java" osa="muut"}
```

```{.tuloste tiedosto="esimerkit/06-merkkijonot.odotettu"}
```

## Algoritmit kirjastossa

`Collections.sort` ja `List.sort` ovat vakaita (TimSort, O(n log n)).
`Arrays.sort` primitiiveille on epävakaa kahden pivotin pikalajittelu.
Vertailijat kootaan ketjuksi: `Comparator.comparing(Tilaus::asiakas)
.thenComparing(Tilaus::summa, Comparator.reverseOrder())`.
`Collections.binarySearch` vaatii lajitellun listan. `PriorityQueue`
on keko, jonka iterointijärjestys ei ole lajiteltu: alkiot otetaan
järjestyksessä `poll`illa. Yleiset algoritmit ja tietorakenteet
käsitellään taidoissa *Tietorakenteet* ja *Algoritmit*.

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
  atomisia (luku 10).
- **Virta putkille, silmukka logiikalle.** Älä tee sivuvaikutuksia
  `map`issa tai `filter`issä. `forEach` on päätösoperaatio tulostukselle
  ja vastaavalle, ei tilan keräämiselle.
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
