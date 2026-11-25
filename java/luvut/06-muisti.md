# Muisti, roskienkeruu ja JIT {.runko-muisti}

Luvussa 5 oliot luotiin `new`-lausekkeella, eikä niitä vapautettu
missään. Tämä luku kertoo, missä oliot ovat, mitä muuttuja oikeastaan
sisältää ja kuka muistin vapauttaa. Samalla selviää, mistä Javan
suorituskyky syntyy ja mihin se kuluu: boksaus, roskienkeruu ja
ajonaikainen kääntäminen (JIT) ovat alustan ominaisuuksia, jotka
näkyvät jokaisessa ohjelmassa. Muisti ei ole ainoa resurssi, joten
luku käsittelee myös tiedostojen ja yhteyksien sulkemisen.

## Pino, keko ja viitteet

Jokaisella säikeellä on oma *pinonsa* (*stack*). Metodikutsu varaa
pinosta kehyksen, jossa ovat metodin parametrit ja paikalliset
muuttujat, ja kehys vapautuu metodin palatessa. Kaikki oliot ja
taulukot ovat *keossa* (*heap*), jonka roskienkerääjä hallitsee.
Muuttuja ei koskaan sisällä oliota, vain primitiiviarvon tai viitteen
olioon. Sijoitus `b = a` ja parametrin välitys kopioivat viitteen,
eivät oliota. Pythonissa malli on sama, mutta Javassa primitiivit
ovat poikkeus: `int` on arvo suoraan muuttujassa.

Siksi vertailuoperaattori `==` vertaa viitteitä eli sitä, onko kyse
samasta oliosta. Arvojen yhtäsuuruus kysytään `equals`-metodilla:

```{.java tiedosto="esimerkit/06-vertailu.java" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/06-vertailu.odotettu"}
```

```{.dot otsikko="Esimerkin muuttujat pinossa ja oliot keossa. `a` ja `b` viittaavat eri olioihin, joilla on sama sisältö. Boksaus antaa arvolle 127 välimuistin olion, mutta arvolle 128 joka kerta uuden."}
digraph {
  rankdir=LR; nodesep=0.12; ranksep=1.3;
  node [fontsize=9, height=0.28];
  subgraph cluster_pino { label="pino: main-metodin kehys"; fontsize=10; color="#D9E0E3";
    a [label="a"]; b [label="b"];
    p1 [label="pieni1"]; p2 [label="pieni2"];
    s1 [label="suuri1"]; s2 [label="suuri2"]; }
  subgraph cluster_keko { label="keko"; fontsize=10; color="#D9E0E3";
    node [fillcolor="white"];
    k1 [label="String \"kahvi\""]; k2 [label="String \"kahvi\""];
    i127 [label="Integer 127 (välimuisti)"];
    i128a [label="Integer 128"]; i128b [label="Integer 128"]; }
  a -> k1; b -> k2; p1 -> i127; p2 -> i127; s1 -> i128a; s2 -> i128b;
}
```

`Integer.valueOf` (ja automaattinen boksaus, ks. seuraava osio)
palauttaa välimuistista saman olion arvoille −128…127. Siksi
`127 == 127` on tosi mutta `128 == 128` epätosi. Virhe on salakavala,
koska testit pienillä luvuilla menevät läpi.

Luokan `Object` oletus-`equals` vertaa viitteitä. Luokka, jonka oliot
ovat arvoja, korvaa sen ja samalla `hashCode`n, aina yhdessä ja
samoista kentistä:

```{.java tiedosto="esimerkit/06-vertailu.java" osa="luokka"}
```

`o instanceof Tuotekoodi t` on *kuvio*: jos `o` on oikeaa tyyppiä, se
sidotaan muuttujaan `t`. `record` tuottaa samat metodit
automaattisesti, joten arvoluokat kirjoitetaan `record`eina (luku 8).
Miksi `hashCode` kuuluu mukaan, selviää hajautustaulujen yhteydessä
luvussa 7.

## Boksaus ja `null`

Geneeriset kokoelmat sisältävät vain olioita, joten `List<Integer>`
sisältää viitteitä `Integer`-olioihin. Kääntäjä muuntaa primitiivin
olioksi (*boxing*) ja takaisin (*unboxing*) automaattisesti. Muunnos
olion `null`-arvosta primitiiviksi kaatuu:

```{.java tiedosto="esimerkit/06-nolla.kaatuu.java" osa="koodi"}
```

```
ruuveja 120
Exception in thread "main" java.lang.NullPointerException: Cannot invoke
"java.lang.Integer.intValue()" because the return value of
"java.util.Map.get(Object)" is null
```

Java 14:stä lähtien `NullPointerException` kertoo, mikä arvo oli
`null`. Korjaus on `saldot.getOrDefault("tulppa", 0)` tai
`Optional` (luku 9).

Boksauksella on myös hinta. `List<Integer>` on taulukko viitteitä
olioihin, joista jokaisella on otsake (12–16 tavua) ja arvo. Läpikäynti
seuraa viitteitä eri puolille kekoa, kun taas `int[]` on yhtenäinen
muistialue, jonka prosessori lukee peräkkäin ja JIT voi vektoroida:

```{.dot otsikko="Neljä lukua taulukkona ja listana. `int[]` on yksi olio, jossa arvot ovat peräkkäin. `ArrayList<Integer>` sisältää taulukon viitteitä, ja jokainen luku on oma olionsa otsakkeineen."}
digraph {
  rankdir=LR; nodesep=0.15; ranksep=0.6;
  node [shape=plain, style="", fontsize=9];
  t [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td bgcolor="#EBEFE3"><b>int[]</b></td><td>otsake</td><td>1000</td><td>1001</td><td>1002</td><td>1003</td></tr></table>>];
  l [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td bgcolor="#EBEFE3"><b>ArrayList</b></td><td>otsake</td><td>size 4</td><td port="e">elementData</td></tr></table>>];
  o [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td bgcolor="#EBEFE3"><b>Object[]</b></td><td>otsake</td><td port="0">●</td><td port="1">●</td><td port="2">●</td><td port="3">●</td></tr></table>>];
  i0 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="3"><tr><td bgcolor="#EBEFE3">Integer</td><td>otsake</td><td>1000</td></tr></table>>];
  i1 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="3"><tr><td bgcolor="#EBEFE3">Integer</td><td>otsake</td><td>1001</td></tr></table>>];
  i2 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="3"><tr><td bgcolor="#EBEFE3">Integer</td><td>otsake</td><td>1002</td></tr></table>>];
  i3 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="3"><tr><td bgcolor="#EBEFE3">Integer</td><td>otsake</td><td>1003</td></tr></table>>];
  l:e -> o; o:0 -> i2; o:1 -> i0; o:2 -> i3; o:3 -> i1;
}
```

```{.java tiedosto="esimerkit/06-hinta.java" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/06-hinta.odotettu"}
```

Tyypillisellä koneella ero on noin 5–10-kertainen, ja `List<Integer>`
vie noin neljä kertaa enemmän muistia. Kuumassa koodissa käytetään siis
primitiivitaulukoita tai primitiivivirtoja (`IntStream`, `mapToInt`).

## Roskienkeruu

Roskienkerääjä (*garbage collector*, GC) vapauttaa oliot, joihin ei
pääse viitteitä seuraamalla mistään *juuresta* (pinojen muuttujat,
staattiset kentät, aktiiviset säikeet). Olion ei siis tarvitse olla
viitteetön, vaan saavuttamaton: kaksi toisiinsa viittaavaa oliota
vapautuu, kun niihin ei enää pääse ulkoa. Viitelaskentaa ei käytetä,
toisin kuin CPythonissa.

Useimmat oliot kuolevat nuorina, joten keko on jaettu sukupolviin.
Uudet oliot luodaan nuoreen sukupolveen (alueet Eden ja survivor),
joka kerätään usein ja
nopeasti kopioimalla elävät oliot talteen; työn määrä riippuu elävien
olioiden määrästä, ei roskan määrästä. Olion luonti on siksi halpaa,
yleensä vain osoittimen siirto säikeen omassa allokointipuskurissa.
Muutaman keruun yli elänyt olio siirretään vanhaan sukupolveen, joka
kerätään harvemmin.

```{.dot otsikko="Olion kulku sukupolvien läpi. Suurin osa olioista ei selviä ensimmäisestä nuoren sukupolven keruusta."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.55;
  node [fontsize=9, height=0.45];
  uusi [label="new", shape=plain, style=""];
  eden [label="Eden\nuudet oliot"];
  surv [label="survivor\nkeruusta selvinneet"];
  old [label="vanha sukupolvi\npitkäikäiset oliot"];
  roska [label="saavuttamaton:\nmuisti vapautuu", style="rounded,dashed", fillcolor="white"];
  uusi -> eden;
  eden -> surv [label="elossa"];
  surv -> old [label="elossa usean\nkeruun jälkeen"];
  { rank=same; surv; roska; }
  eden -> roska [style=dashed, constraint=false];
  surv -> roska [style=dashed];
  old -> roska [style=dashed, constraint=false];
}
```

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

```{.java tiedosto="esimerkit/06-valimuisti.java" osa="lru"}
```

```{.java tiedosto="esimerkit/06-valimuisti.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-valimuisti.odotettu"}
```

`LinkedHashMap` pitää alkiot käyttöjärjestyksessä, kun konstruktorin
kolmas parametri on `true`, ja `removeEldestEntry` poistaa vanhimman.
Esimerkki korvaa metodin nimettömässä aliluokassa (luku 5). Luokka on
`Serializable`, joten `-Xlint:all` vaatii nimettömälle aliluokalle
`serialVersionUID`-kentän. Tuotannossa käytetään valmista
kirjastoa, kuten Caffeine, joka on myös säieturvallinen.

## Resurssit: `try`-with-resources

Roskienkerääjä vapauttaa muistin, mutta ei sulje tiedostoja, yhteyksiä
tai lukkoja, eikä keruun ajankohtaa voi ennustaa. Muut resurssit
suljetaan deterministisesti `try`-lohkolla, jonka otsakkeessa luodut
`AutoCloseable`-oliot suljetaan lohkon lopussa käänteisessä
järjestyksessä:

```{.java tiedosto="esimerkit/06-resurssit.java" osa="resurssi"}
```

```{.java tiedosto="esimerkit/06-resurssit.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-resurssit.odotettu"}
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

```{.dot otsikko="Metodin elinkaari JVM:ssä. Sama metodi voi kulkea kierroksen useasti, kun ohjelman käytös muuttuu."}
digraph {
  rankdir=LR; nodesep=0.4; ranksep=0.9;
  node [fontsize=9, height=0.45];
  t [label="tulkki\nkerää profiilia"];
  c1 [label="C1\nnopea käännös"];
  c2 [label="C2\noptimoitu konekieli"];
  t -> c1 [label="kuuma"];
  c1 -> c2 [label="hyvin kuuma"];
  c2 -> t [label="oletus rikkoutui\n(deoptimointi)", constraint=false];
}
```

Siksi mittaus ilman lämmittelyä mittaa tulkkia. `06-hinta.java`
toistaa mittauksen 25 kertaa ja käyttää parasta aikaa. Luotettavaan
mittaukseen tarvitaan silti JMH (*Java Microbenchmark Harness*), joka
hoitaa lämmittelyn, haarukoinnin erillisiin JVM:iin ja kuolleen koodin
poiston estämisen (luku 12).

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
  (Java 19), `Stream` tiedostoista (`Files.lines`, luku 7) ja
  JDBC-oliot.
- **Älä optimoi arvaamalla.** Mittaa JFR:llä tai JMH:lla. JIT poistaa
  usein juuri sen, mitä yrität optimoida käsin.
- **Hinta.** Allokaatio on halpaa, mutta roskienkeruun työ kasvaa
  elävien olioiden määrän mukana. Suuret, pitkäikäiset rakenteet
  (välimuistit) maksavat eniten.

## Itsearviointi

- Osaat piirtää, mitä pinossa ja keossa on sijoituksen ja
  metodikutsun jälkeen, ja kertoa, milloin `==` ja `equals` antavat
  eri tuloksen.
- Osaat selittää boksauksen hinnan ja `null`-purun vaaran.
- Osaat nimetä roskienkerääjät ja tavallisimmat muistivuotojen syyt.
- Osaat sulkea resurssit `try`-with-resources-lohkolla ja tulkita
  tukahdutetut poikkeukset.
- Osaat kertoa, miksi mikrovertailu ilman lämmittelyä on harhaanjohtava.
