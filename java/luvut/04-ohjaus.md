# Ohjausrakenteet, metodit ja lambdat {.runko-ohjaus}

Kun arvot ja tyypit ovat tuttuja, seuraavaksi tarvitaan tavat ohjata
suoritusta ja jakaa koodi osiin. Silmukat ja ehdot ovat Javassa
C:n kaltaisia, ja Pythonia osaava lukee niitä suoraan. Luvun pääasiat
ovat siksi Javan omat piirteet: `switch`-lauseke, jonka kattavuuden
kääntäjä tarkistaa, metodien parametrinvälitys sekä lambdat, joilla
toiminnon voi välittää arvona.

## Ohjausrakenteet

Javan `if`, `while`, `do`–`while` ja `for` ovat C:n kaltaisia. Ehdon on
oltava `boolean`; luku tai viite ei kelpaa ehdoksi. Kokoelmat ja
taulukot käydään läpi for-each-silmukalla `for (String s : lista)`.
Sisäkkäisistä silmukoista poistutaan nimetyllä `break ulompi;` -lauseella.

Moderni Java käyttää valintaan `switch`-*lauseketta* (Java 14), joka
palauttaa arvon. Nuolisyntaksissa (`case X ->`) haara ei valu
seuraavaan, ja kääntäjä tarkistaa, että kaikki arvot on käsitelty.

Tarkistus edellyttää, että kääntäjä tuntee kaikki mahdolliset arvot.
Sitä varten on *lueteltu tyyppi* `enum`: tyyppi, jonka arvot ovat
kiinteä joukko nimettyjä vakioita, esimerkiksi
`enum Tila { AVOIN, MAKSETTU }`. Arvoon viitataan tyypin nimellä
(`Tila.AVOIN`), ja muuttuja, jonka tyyppi on `Tila`, ei voi sisältää
muuta kuin jonkin luetelluista arvoista (tai `null`in). Pythonissa
vastaava on `enum.Enum`. `enum`in muut piirteet, kuten kentät ja
metodit, esitellään luvussa 5.

Tilakone on luonteva kirjoittaa kahtena `enum`-tyyppinä ja
sisäkkäisinä `switch`-lausekkeina:

```{.java tiedosto="esimerkit/04-tilaus.java" osa="tyypit"}
```

```{.java tiedosto="esimerkit/04-tilaus.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/04-tilaus.odotettu"}
```

Kaikki tila–tapahtuma-parit on käsitelty, ja kielletyt siirtymät
heittävät poikkeuksen. `default`-haaraa ei käytetä, koska se piilottaisi
puuttuvan tapauksen. Kun `enum`iin lisätään arvo, kääntäjä löytää
jokaisen `switch`-lausekkeen, joka on päivitettävä:

```{.java tiedosto="esimerkit/04-kattavuus.ei-kaanny.java" osa="koodi"}
```

```
04-kattavuus.ei-kaanny.java:11: error: the switch expression does not
cover all possible input values
```

Vanha `switch`-*lause* kaksoispisteineen (`case X:`) valuu seuraavaan
haaraan ilman `break`-lausetta, eikä kääntäjä tarkista sen kattavuutta.
Uudessa koodissa käytetään nuolisyntaksia.

## Metodit

Metodi kuuluu aina luokkaan. Staattinen metodi (`static`) ei tarvitse
oliota, instanssimetodi saa olion `this`-viitteenä (luku 5). Tämän
luvun esimerkit käyttävät vain staattisia metodeja, jotka vastaavat
Pythonin moduulitason funktioita. Javassa ei ole
oletusparametreja eikä nimettyjä argumentteja. Niiden sijaan
käytetään ylikuormitusta (samanniminen metodi eri parametreilla),
rakentajaa (luku 8) tai parametrioliota (`record`).

Parametrit välitetään aina arvona. Viitetyypin arvo on viite, joten
metodi voi muuttaa olion tilaa mutta ei kutsujan muuttujaa. Tämä
selittää, miksi `void lisaa(List<String> l)` voi lisätä listaan
mutta ei korvata kutsujan listaa uudella.

## Lambdat ja funktionaaliset rajapinnat

Lambda on lyhyt nimetön funktio. Javassa funktiolla ei ole omaa
tyyppiään, vaan lambdan tyyppi on *funktionaalinen rajapinta*.
Rajapinta (luku 5) on tyyppi, joka luettelee metodit ilman toteutusta,
ja funktionaalisessa rajapinnassa niitä on täsmälleen yksi: lambda on
sen toteutus. Pakkaus `java.util.function` sisältää yleisimmät:

| Rajapinta | Metodi | Esimerkki |
|-----------|--------|-----------|
| `Supplier<T>` | `T get()` | `() -> new ArrayList<>()` |
| `Consumer<T>` | `void accept(T)` | `s -> System.out.println(s)` |
| `Function<T,R>` | `R apply(T)` | `String::length` |
| `Predicate<T>` | `boolean test(T)` | `String::isBlank` |
| `BiFunction<T,U,R>` | `R apply(T, U)` | `Integer::sum` |
| `UnaryOperator<T>` | `T apply(T)` | `String::strip` |

Primitiiveille on omat versiot (`IntPredicate`, `ToLongFunction`…),
jotka välttävät boksauksen. *Metodiviittaus* (`String::length`,
`Integer::sum`, `ArrayList::new`) on lyhyempi tapa kirjoittaa lambda,
joka vain kutsuu metodia.

Lambdat tekevät säännöistä dataa. Esimerkki tallentaa
validointisäännöt tauluun (`Map`) nimen ja ehdon pareina:

```{.java tiedosto="esimerkit/04-saannot.java" osa="tehdas"}
```

```{.java tiedosto="esimerkit/04-saannot.java" osa="saannot"}
```

```{.java tiedosto="esimerkit/04-saannot.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/04-saannot.odotettu"}
```

`enintaan(12)` on *funktiotehdas*: se palauttaa lambdan, joka *sulkee
sisäänsä* (*closure*) parametrin `pituus`. `andThen` koostaa kaksi
funktiota yhdeksi. `Map.copyOf` tekee taulusta muuttumattoman.

## Sulkeuman rajoitus

Lambda saa käyttää ympäröivän metodin paikallisia muuttujia vain, jos ne
ovat *käytännössä vakioita* (*effectively final*), eli niihin ei
sijoiteta uudelleen. Rajoitus estää kilpailutilanteet, kun lambda
ajetaan toisessa säikeessä, ja pitää lambdan merkityksen yksiselitteisenä:

```{.java tiedosto="esimerkit/04-sulkeuma.ei-kaanny.java" osa="koodi"}
```

```
04-sulkeuma.ei-kaanny.java:13: error: local variables referenced from a
lambda expression must be final or effectively final
```

Jos lambdan pitää päivittää laskuria, se on merkki siitä, että tehtävä
kuuluu virralle (`count()`, `sum()`, `collect`) tai silmukalle.
Kiertotie `int[] laskuri = {0}` toimii, mutta ei ole säieturvallinen.

## Käytännössä

- **`switch`-lauseke ilman `default`-haaraa `enum`- ja
  `sealed`-tyypeille.** Kääntäjä löytää silloin päivitettävät kohdat,
  kun tyyppiin lisätään arvo. Tämä on Javan vastine
  kattavuustarkistetulle `match`ille.
- **Tilakone `enum`illa.** Tila ja tapahtuma ovat `enum`eja ja siirtymä
  yksi puhdas metodi. Kielletty siirtymä on poikkeus, ei hiljainen
  ohitus.
- **Vartiolausekkeet (*guard clauses*).** Tarkista virheelliset
  tapaukset metodin alussa ja palaa heti. Syvä `if`-sisäkkäisyys on
  merkki siitä, että metodi pitää jakaa.
- **Pidä metodit lyhyinä ja parametrit vähissä.** Yli kolme tai neljä
  parametria on merkki puuttuvasta tyypistä: kokoa ne `record`iksi.
- **Säännöt datana.** Kun ehtoja on monta ja ne muuttuvat, kokoa ne
  tauluun tai listaan (`Map<String, Predicate<T>>`). Uusi sääntö on
  yksi rivi, ja säännöt voi testata erikseen.
- **Metodiviittaus, kun lambda vain kutsuu metodia.** `String::strip`
  on selkeämpi kuin `s -> s.strip()`.
- **Hinta.** Lambda, joka ei sulje sisäänsä muuttujia, luodaan kerran.
  Sulkeuma luo olion jokaisella arvioinnilla, mutta JIT poistaa sen
  usein pakoanalyysin avulla. Lambdojen kutsu on rajapintakutsu, joka
  inlinoidaan, kun kutsukohdassa näkyy vain muutama toteutus.

## Itsearviointi

- Osaat kirjoittaa `switch`-lausekkeen nuolisyntaksilla ja kertoa,
  miksi `default`-haara heikentää kattavuustarkistusta.
- Osaat toteuttaa tilakoneen `enum`-tyypeillä.
- Osaat käyttää `java.util.function`-rajapintoja ja metodiviittauksia.
- Osaat kirjoittaa funktiotehtaan ja koostaa funktioita `andThen`illa.
- Osaat kertoa, mitä *effectively final* tarkoittaa ja miksi rajoitus
  on olemassa.
