# Muuttumaton data ja hahmontunnistus

Funktionaalisessa ohjelmassa dataa ei muuteta, vaan siitä luodaan uusia
versioita. Tämä kuulostaa tuhlaavalta, mutta käytännössä se on usein
halpaa, koska muuttumattomat rakenteet voivat jakaa osansa. Hyöty on
suuri: arvo ei muutu kenenkään selän takana, joten koodin voi
ymmärtää paikallisesti ja dataa voi jakaa säikeiden kesken ilman
lukkoja.

## Tietueet

`struct` määrittelee tietuetyypin ja luo samalla konstruktorin,
predikaatin ja kenttien lukijat. Kentät ovat **oletuksena
muuttumattomia**. `#:transparent` tekee kentistä näkyviä tulostuksessa
ja `equal?`-vertailussa.

```{.scheme tiedosto="esimerkit/05-muodot.rkt" osa="tyypit"}
```

Määrittely `(struct ympyra (sade))` luo funktiot `ympyra`, `ympyra?` ja
`ympyra-sade`. Asettajaa ei synny, ja sen käyttö on käännösaikainen
virhe:

```{.scheme tiedosto="esimerkit/05-muuttumaton.ei-kaanny.rkt" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/05-muuttumaton.odotettu"}
```

`struct-copy` luo kopion, jossa osa kentistä on vaihdettu. Muuttuva
kenttä on mahdollinen (`#:mutable`), mutta se on poikkeus, joka
perustellaan.

## Hahmontunnistus

`match` vertaa arvoa hahmoihin järjestyksessä ja sitoo osat nimiin.
Kolme tietuetyyppiä ja `match` muodostavat **summatyypin**: muoto on
ympyrä *tai* suorakulmio *tai* kolmio, ja funktiossa on haara kutakin
vaihtoehtoa kohti. Tämä on luvun 3 suunnittelureseptiä useammalle
datan lajille.

```{.scheme tiedosto="esimerkit/05-muodot.rkt" osa="ala"}
```

Hahmo voi vaatia saman muuttujan toistuvan, tarkistaa ehdon (`?`),
purkaa sisäkkäisiä rakenteita ja ohittaa osia (`_`):

```{.scheme tiedosto="esimerkit/05-muodot.rkt" osa="kuvaus"}
```

```{.scheme tiedosto="esimerkit/05-muodot.rkt" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-muodot.odotettu"}
```

Vertaa oliokielen ratkaisuun, jossa `Muoto`-luokalla on abstraktit
metodit `ala` ja `kuvaus`. Oliomallissa uuden *muodon* lisääminen on
helppoa (uusi aliluokka), mutta uuden *operaation* lisääminen vaatii
muutoksen jokaiseen luokkaan. Summatyypeissä ja hahmontunnistuksessa
tilanne on päinvastainen. Tätä kutsutaan **lausekeongelmaksi**
(*expression problem*). Kumpikin malli on oikea eri tilanteissa.

## Lausekepuut

Hahmontunnistus on vahvimmillaan puiden muuntamisessa. Symbolinen
derivointi käsittelee lauseketta, joka on tavallinen lista.
Puolilainaushahmo `` `(+ ,a ,b) `` tunnistaa kolmialkioisen listan,
jonka ensimmäinen alkio on symboli `+`, ja sitoo loput nimiin `a` ja
`b`.

```{.scheme tiedosto="esimerkit/05-derivaatta.rkt" osa="derivoi"}
```

Tulos sievennetään jo rakennettaessa. **Älykäs konstruktori**
(`summa`, `tulo`) tarkistaa erikoistapaukset, kuten nollalla
kertomisen, ennen kuin se rakentaa uuden solmun:

```{.scheme tiedosto="esimerkit/05-derivaatta.rkt" osa="sievenna"}
```

```{.scheme tiedosto="esimerkit/05-derivaatta.rkt" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-derivaatta.odotettu"}
```

Sama rakenne toistuu kääntäjissä: jäsennin tuottaa syntaksipuun, ja
optimointivaiheet ovat hahmontunnistukseen perustuvia
puunmuunnoksia, kuten vakioiden laskeminen ja algebralliset
sievennykset.

## Pysyvät tietorakenteet

Muuttumaton hajautustaulu (`hash`, `hash-set`, `hash-update`) ja lista
ovat **pysyviä** (*persistent*): muutos tuottaa uuden version, ja vanha
säilyy. Uusi versio jakaa suurimman osan rakenteestaan vanhan kanssa,
joten muutos maksaa O(log n), ei O(n).

Pysyvyydestä saadaan kumoaminen ilmaiseksi. Historia on lista
versioita, ja kumoaminen on listan ensimmäisen alkion pudottaminen.

```{.scheme tiedosto="esimerkit/05-historia.rkt" osa="ostoskori"}
```

```{.scheme tiedosto="esimerkit/05-historia.rkt" osa="historia"}
```

```{.tuloste tiedosto="esimerkit/05-historia.odotettu"}
```

Viimeinen rivi osoittaa jakamisen: alennuksen muuttaminen ei kopioinut
rivejä, vaan molemmat versiot viittaavat samaan tauluun.

## Käytännössä

- **Summatyypit ja hahmontunnistus ovat tulleet valtavirtaan.** Rustin
  `enum` ja `match`, Kotlinin `sealed class` ja `when`, Javan
  `sealed`-rajapinnat ja `switch`-hahmot (Java 21), Pythonin
  `match`-lause (3.10), C#:n hahmot ja TypeScriptin erotellut unionit
  ovat kaikki ML-perheen kielistä peräisin. Staattisesti tyypitetyissä
  kielissä kääntäjä myös tarkistaa, että jokainen vaihtoehto on
  käsitelty.
- **Arvo-oliot kannattaa tehdä muuttumattomiksi.** Javan `record`,
  Kotlinin `data class`, Pythonin `@dataclass(frozen=True)` ja C#:n
  `record` tarjoavat saman kuin `struct`: konstruktorin,
  yhtäsuuruuden ja kopion muutoksella (`copy`, `with`,
  `dataclasses.replace`). Muuttumaton olio on turvallinen
  hajautustaulun avain ja jaettavissa säikeiden kesken.
- **Pysyviä rakenteita on kirjastoina.** Clojuren ja Scalan
  oletuskokoelmat ovat pysyviä, ja JavaScriptiin ja Javaan on omat
  kirjastonsa (Immutable.js, Vavr, PCollections). Reactin ja Reduxin
  tilanhallinta ja Gitin versiomalli perustuvat samaan ajatukseen.
  Vanhaa versiota ei muuteta, joten muutoksen havaitseminen on
  viitevertailu.
- **Muuttumattomuuden hinta on allokaatioissa.** Tiukassa
  silmukassa uusien versioiden luominen kuormittaa roskienkeruuta.
  Paikallinen muuttuva puskuri, jota kukaan muu ei näe, on silloin
  hyväksyttävä optimointi (ks. luku 9). Muuttuvuus on ongelma vasta,
  kun tila on jaettu.

## Itsearviointi

- Osaat määritellä tietuetyypit ja käsitellä niitä `match`-lausekkeella
  niin, että jokaiselle vaihtoehdolle on haara.
- Osaat selittää lausekeongelman ja valita summatyypin ja
  luokkahierarkian välillä tilanteen mukaan.
- Osaat muuntaa lausekepuuta hahmontunnistuksella ja sieventää tulosta
  älykkäillä konstruktoreilla.
- Osaat selittää, miksi pysyvän rakenteen päivitys ei kopioi kaikkea,
  ja käyttää pysyvyyttä kumoamisen tai versiohistorian toteuttamiseen.
