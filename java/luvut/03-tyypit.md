# Tyypit, lausekkeet ja syöte {.runko-tyypit}

Java on staattisesti tyypitetty: jokaisella muuttujalla on
käännösaikana tunnettu tyyppi, ja lukutyypeillä on kiinteä koko. Tämä
luku käy läpi arvot, joista ohjelmat rakentuvat – luvut, merkit,
merkkijonot ja taulukot – sekä niiden tulostamisen ja lukemisen.
Pythonista tulevalle uutta ovat ylivuoto, kieliasetuksen ja merkistön
vaikutus tulosteeseen ja se, että merkkijonon pituus ei ole merkkien
määrä. Nämä ovat yleisiä virhelähteitä, joten ne käsitellään heti.

## Primitiivityypit ja viitetyypit

Javassa on kahdeksan primitiivityyppiä. Niiden koko ja käyttäytyminen
ovat samat kaikilla alustoilla:

| Tyyppi | Koko | Arvoalue | Huomio |
|--------|------|----------|--------|
| `boolean` | – | `true`, `false` | ei muunnu luvuksi |
| `byte` | 8 bittiä | −128…127 | etumerkillinen |
| `short` | 16 bittiä | −32 768…32 767 | |
| `char` | 16 bittiä | 0…65 535 | UTF-16-koodiyksikkö, ei merkki |
| `int` | 32 bittiä | noin ±2,1 · 10^9^ | oletuskokonaisluku |
| `long` | 64 bittiä | noin ±9,2 · 10^18^ | literaali `10L` |
| `float` | 32 bittiä | IEEE 754 | literaali `1.5f`; vältä |
| `double` | 64 bittiä | IEEE 754 | oletusliukuluku |

Kaikki muut tyypit ovat viitetyyppejä: taulukoita, luokkia ja
rajapintoja sekä luokan erikoismuotoja `enum` ja `record` (luvut 5 ja
8). Viitetyyppinen muuttuja sisältää viitteen olioon tai arvon `null`.
Jokaisella primitiivillä on kääreluokka (`Integer`, `Long`, `Double` …),
jota tarvitaan kokoelmissa, koska geneeriset tyypit eivät hyväksy
primitiivejä (luku 6).

Paikallisen muuttujan tyypin voi jättää kääntäjän pääteltäväksi
sanalla `var` (Java 10), esimerkiksi `var summa = 0L;` (tyyppi `long`).
Tyyppi on silti staattinen. `var` sopii, kun tyyppi näkyy oikealta
puolelta. Kun oikea puoli on
metodikutsu, kirjoita tyyppi näkyviin, jotta lukija ei joudu arvaamaan.

## Kokonaisluvut ja ylivuoto

Kokonaislukujen aritmetiikka kiertää hiljaa ympäri, kuten C:ssä, mutta
käyttäytyminen on määritelty. Jakolasku pyöristää kohti nollaa, ja
nollalla jakaminen heittää `ArithmeticException`in. `Math.addExact`,
`multiplyExact` ja `toIntExact` heittävät poikkeuksen ylivuodosta:

```{.java tiedosto="esimerkit/03-ylivuoto.kaatuu.java"}
```

```
int:  -1018167296
long: 3276800000
Exception in thread "main" java.lang.ArithmeticException: integer overflow
```

Huomaa, että `(long) tiedostoja * koko` muuntaa ensin vasemman
operandin, jolloin kertolasku tehdään `long`-tyypillä. Muoto
`(long) (tiedostoja * koko)` muuntaisi vasta valmiiksi ylivuotaneen
tuloksen.

## Liukuluvut ja raha

`double` on binäärinen liukuluku, joka ei pysty esittämään useimpia
desimaalilukuja tarkasti. Rahalle, verolle ja muille kymmenjärjestelmän
summille käytetään `BigDecimal`ia tai kokonaislukuja (sentit):

```{.java tiedosto="esimerkit/03-lasku.java" osa="double"}
```

```{.java tiedosto="esimerkit/03-lasku.java" osa="lasku"}
```

```{.tuloste tiedosto="esimerkit/03-lasku.odotettu"}
```

`BigDecimal` luodaan merkkijonosta (`new BigDecimal("6.95")`), ei
`double`sta, koska `new BigDecimal(6.95)` säilyttää binääriluvun virheen.
Pyöristys tehdään aina eksplisiittisesti `setScale`-metodilla ja
`RoundingMode`lla. `BigDecimal`-olio on muuttumaton, joten `add` palauttaa
uuden olion.

## Muotoilu ja kieliasetus

`printf`, `String.format` ja `formatted` käyttävät C:n tyylisiä
muotoilukoodeja (`%d`, `%s`, `%.2f`, `%-16s`, `%n` rivinvaihto). Ilman
`Locale`-parametria lukujen muotoilu riippuu koneen kieliasetuksesta:
sama ohjelma tulostaa suomalaisella koneella `1234,50` ja palvelimella
`1234.50`. Koneelle luettava tuloste muotoillaan aina `Locale.ROOT`illa:

```{.java tiedosto="esimerkit/03-lasku.java" osa="muotoilu"}
```

Esimerkin kaksi viimeistä riviä näyttävät `BigDecimal`in sudenkuopan:
`equals` vertaa myös desimaalien määrää (`2.50` ja `2.5` eivät ole `equals`-mielessä samat), `compareTo`
vain arvoa.

## Merkistö ja tulostevirta

Java 18:sta lähtien tiedostojen oletusmerkistö on UTF-8, mutta
konsolivirtojen (`System.out`, `System.in`) merkistö tulee yhä
käyttöjärjestelmän kieliasetuksesta. Jos ympäristömuuttujaa `LANG` ei
ole asetettu, esimerkiksi kontissa tai CI-palvelimella, `ä` tulostuu
kysymysmerkkinä. Tämän tutoriaalin esimerkit, jotka tulostavat ääkkösiä,
alkavat siksi rivillä

```{.java tiedosto="esimerkit/03-lasku.java" osa="utf"}
```

ja lukevat syötteen `InputStreamReader`illa, jolle merkistö annetaan.
Vaihtoehto on ajaa ohjelma valitsimella `-Dstdout.encoding=UTF-8`.
Kirjoita tiedostoja käsittelevä koodi aina niin, että merkistö annetaan
eksplisiittisesti; näin ohjelma ei riipu ajoympäristöstä.

## Merkit ja merkkijonot

`String` on muuttumaton UTF-16-koodiyksiköiden jono. `char` on yksi
koodiyksikkö, ei merkki: Unicode-merkit perustason (BMP) ulkopuolelta,
kuten useimmat emojit, vievät kaksi `char`ia (*surrogaattipari*):

```{.java tiedosto="esimerkit/03-merkit.java"}
```

```{.tuloste tiedosto="esimerkit/03-merkit.odotettu"}
```

`length()` palauttaa siis koodiyksiköiden määrän. Kun käsitellään
käyttäjän tekstiä merkki kerrallaan, käytetään `codePoints()`-virtaa.
Merkkijonojen käsittely jatkuu luvussa 7.

## Taulukot

Taulukko on kiinteän kokoinen jono samantyyppisiä alkioita. Tyyppi
kirjoitetaan `int[]`, `String[]` tai `double[][]`, ja koko annetaan
luotaessa eikä muutu sen jälkeen. Pythonin `list`iä vastaa lähinnä
kokoelma `ArrayList` (luku 7); taulukko on sen alla oleva matalan tason
rakenne, jota käytetään suoraan, kun koko tiedetään tai suorituskyky
ratkaisee (luku 6).

```{.java tiedosto="esimerkit/03-taulukot.java" osa="perus"}
```

```{.tuloste tiedosto="esimerkit/03-taulukot.odotettu" rivit="1-3"}
```

`new` täyttää taulukon oletusarvoilla (`0`, `false` tai `null`).
Pituus on kenttä `length`, ei metodi. Indeksit alkavat nollasta, ja
jokainen indeksointi tarkistetaan: virheellinen indeksi heittää
poikkeuksen eikä lue viereistä muistia. Negatiivisia indeksejä ja
viipaleita (`a[-1]`, `a[1:3]`) ei ole; osataulukko kopioidaan metodilla
`Arrays.copyOfRange`.

Taulukko on olio, ja muuttuja sisältää viitteen siihen. Sijoitus ei
kopioi alkioita, ja `equals` vertaa viitteitä. Tulostus, vertailu ja
kopiointi tehdään apuluokalla `java.util.Arrays`:

```{.java tiedosto="esimerkit/03-taulukot.java" osa="viite"}
```

```{.tuloste tiedosto="esimerkit/03-taulukot.odotettu" rivit="4-5"}
```

Moniulotteinen taulukko on taulukko taulukoita, joten rivit voivat
olla eripituisia:

```{.java tiedosto="esimerkit/03-taulukot.java" osa="moni"}
```

```{.tuloste tiedosto="esimerkit/03-taulukot.odotettu" rivit="6-6"}
```

Pelkkä `System.out.println(taulukko)` tulostaa tyypin ja hajautusarvon
(`[I@1b6d3586`), ei alkioita. Lajittelu, haku ja muunnokset
kokoelmiksi ovat luvussa 7.

## Syötteen lukeminen

Rivipohjainen syöte luetaan `BufferedReader`illa. `Scanner` on
kätevä pienissä harjoituksissa, mutta se on hidas, ja sen virheiden
käsittely on hankalaa. Esimerkki lukee varastorivejä, jäsentää ne ja
raportoi virheelliset rivit rivinumeron kanssa:

```{.java tiedosto="esimerkit/03-syote.java" osa="jasenna"}
```

```{.java tiedosto="esimerkit/03-syote.java" osa="main"}
```

```{.tuloste tiedosto="esimerkit/03-syote.odotettu"}
```

Huomioita:

- `split(";", -1)` säilyttää tyhjät loppukentät. Ilman toista
  parametria `"a;;".split(";")` palauttaa vain yhden kentän.
- `strip()` poistaa Unicode-välilyönnit, `trim()` vain ASCII-merkit
  `≤ U+0020`.
- Jäsennin heittää `IllegalArgumentException`in ja säilyttää alkuperäisen
  `NumberFormatException`in syynä (*cause*). Kutsuja päättää, mitä
  virheelle tehdään: tässä rivi ohitetaan ja virhe raportoidaan.
- Tekstilohko (`"""`, Java 15) poistaa yhteisen sisennyksen, ja
  `formatted` on `String.format` metodina.
- `Rivi` on tietue `record Rivi(String tuote, int maara)`: muuttumaton
  arvo, jolla on nimetyt kentät ja lukumetodit `tuote()` ja `maara()`
  (luku 8). `try`–`catch` ja poikkeukset käsitellään luvussa 9.

## Käytännössä

- **Valitse oikea numerotyyppi.** `int` laskureille ja indekseille,
  `long` aikaleimoille, tavumäärille ja tunnisteille, `BigDecimal` tai
  `long`-sentit rahalle, `double` mittauksille. Älä käytä `float`ia
  ilman erityistä syytä.
- **Laske ylivuotoherkät asiat `long`illa tai `*Exact`-metodeilla.**
  Kokoja, aikaleimoja ja rahaa kertovissa lausekkeissa ylivuoto on
  todellinen virhe, ei teoreettinen.
- **Anna `Locale` ja merkistö aina.** Koneelle tarkoitettu tuloste
  (`Locale.ROOT`), tiedostot ja virrat (`UTF_8`). Käyttäjälle näkyvä
  muotoilu tehdään käyttäjän kieliasetuksella tarkoituksella.
- **Jäsennä rajalla.** Muunna syöte heti tyypitetyksi arvoksi
  (`record Rivi`) ja raportoi virheet kontekstin kanssa. Ohjelman
  sisäosat eivät käsittele merkkijonoja.
- **`var` paikallisiin muuttujiin, kun tyyppi on ilmeinen.** Kenttien,
  parametrien ja paluuarvojen tyypit kirjoitetaan aina.
- **Taulukko vai lista?** Oletus on `List` (luku 7). Taulukko sopii
  primitiiveille kuumassa koodissa, kiinteän kokoisille puskureille ja
  rajapintoihin, jotka vaativat sen (`main(String[] args)`).
- **Hinta.** Primitiivit ovat pinossa tai olion kentissä ilman
  allokaatiota. `BigDecimal`-laskutoimitus luo uuden olion ja on
  kymmeniä kertoja hitaampi kuin `long`, mikä merkitsee vain hyvin
  kuumissa silmukoissa.

## Itsearviointi

- Osaat valita numerotyypin käyttötarkoituksen mukaan ja kertoa, miksi
  raha ei ole `double`.
- Osaat estää ja havaita kokonaislukujen ylivuodon.
- Osaat muotoilla tulosteen kieliasetuksesta riippumatta ja kertoa,
  miksi tulostevirran merkistö on annettava erikseen.
- Osaat kertoa, miksi `String.length()` ei ole merkkien määrä.
- Osaat luoda, kopioida, verrata ja tulostaa taulukon ja kertoa, miten
  se eroaa Pythonin listasta.
- Osaat lukea rivipohjaisen syötteen, jäsentää sen ja raportoida virheet.
