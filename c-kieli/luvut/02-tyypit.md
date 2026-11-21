# Tyypit ja lausekkeet

## Perustyypit

C:n perustyypit ovat kokonaislukutyypit (`char`, `short`, `int`,
`long`, `long long`), liukulukutyypit (`float`, `double`,
`long double`) ja totuusarvotyyppi `bool`. Kokonaislukutyypeistä on
etumerkillinen (`signed`, oletus) ja etumerkitön (`unsigned`) versio.

Standardi määrää tyypeille vain vähimmäiskoot: esimerkiksi `int` on
vähintään 16 ja `long` vähintään 32 bittiä. Todelliset koot riippuvat
alustasta. Operaattori `sizeof` kertoo tyypin koon tavuina:

```{.c tiedosto="esimerkit/02-tyypit.c" osa="koot"}
```

Tuloste 64-bittisellä Linuxilla:

```{.tuloste tiedosto="esimerkit/02-tyypit.odotettu"}
```

64-bittisessä Windowsissa `long` on 4 tavua, joten `long`-tyyppiin ei
pidä luottaa, jos tarvitaan tietty koko. Otsikko `<limits.h>`
määrittelee kunkin tyypin rajat, kuten `INT_MAX`.

## Kiinteänkokoiset kokonaisluvut

Otsikko `<stdint.h>` (C99) määrittelee tyypit, joiden koko on taattu:
`int8_t`, `int16_t`, `int32_t`, `int64_t` ja niiden etumerkittömät
vastineet `uint8_t` jne. Niitä kannattaa käyttää aina, kun koolla on
merkitystä, esimerkiksi tiedostomuodoissa ja verkkoprotokollissa.
Otsikon `<inttypes.h>` makrot, kuten `PRId32`, antavat oikean
`printf`-muunnosmääreen:

```{.c tiedosto="esimerkit/02-kokonaisluvut.c" osa="stdint"}
```

Pitkiin lukuihin voi C23:sta alkaen kirjoittaa erottimeksi heittomerkin.

### Ylivuoto

Etumerkittömät kokonaisluvut lasketaan aina modulo $2^n$, missä $n$ on
bittien määrä. Ylivuoto on siis määritelty ja "kiertää" nollaan:

```{.c tiedosto="esimerkit/02-kokonaisluvut.c" osa="kierto"}
```

Etumerkillisen kokonaisluvun ylivuoto taas on määrittelemätöntä
käyttäytymistä. Kääntäjä saa olettaa, ettei sitä tapahdu, ja voi
optimoida koodin sen mukaan. Ylivuotoon ja sen tarkistamiseen palataan
luvussa [Virheenkäsittely](#virheenkäsittely).

### Kokonaislukujako

Kokonaislukujen jakolasku katkaisee tuloksen kohti nollaa, ja
jakojäännöksellä on jaettavan etumerkki. Jos jompikumpi operandi on
liukuluku, lasketaan liukulukujako:

```{.c tiedosto="esimerkit/02-kokonaisluvut.c" osa="jako"}
```

`printf`-merkkijonossa `%%` tulostaa prosenttimerkin.

### Literaalit

Kokonaislukuliteraalin voi kirjoittaa kymmen-, heksadesimaali- (`0x`),
oktaali- (`0`) tai C23:sta alkaen binäärimuodossa (`0b`). Etunolla on
ansa: `017` on oktaaliluku 15.

```{.c tiedosto="esimerkit/02-kokonaisluvut.c" osa="literaalit"}
```

```{.tuloste tiedosto="esimerkit/02-kokonaisluvut.odotettu"}
```

## Tyyppimuunnokset

Lausekkeissa C muuntaa operandit automaattisesti yhteiseen tyyppiin.
Ensin `int`-tyyppiä pienemmät tyypit, kuten `char` ja `uint8_t`,
*ylennetään* `int`-tyypiksi. Sitten, jos operandit ovat edelleen eri
tyyppiä, pienempi muunnetaan suuremmaksi. Edellä `laskuri + 1`
laskettiin siksi `int`-tyyppisenä (tulos 256), ja arvo katkesi vasta,
kun se sijoitettiin takaisin `uint8_t`-muuttujaan.

Vaarallisin sääntö koskee etumerkillisen ja etumerkittömän luvun
vertailua: etumerkillinen luku muunnetaan etumerkittömäksi. Silloin
`-1` muuttuu suurimmaksi mahdolliseksi etumerkittömäksi luvuksi, ja
vertailu `-1 < 1u` on epätosi. Valitsin `-Wextra` varoittaa tästä:

```{.c tiedosto="esimerkit/02-etumerkki.ei-kaanny.c"}
```

Eksplisiittinen muunnos kirjoitetaan muodossa `(tyyppi)lauseke`. Sitä
kannattaa käyttää säästeliäästi, sillä se vaientaa kääntäjän
tarkistukset.

## Liukuluvut

`double` on 64-bittinen IEEE 754 -liukuluku, jossa on noin 15–16
merkitsevää numeroa. `float` on puolet pienempi ja epätarkempi, joten
oletuksena kannattaa käyttää `double`-tyyppiä. Useimpia
desimaalilukuja ei voi esittää binäärisesti tarkasti, minkä vuoksi
liukulukuja ei pidä vertailla operaattorilla `==`:

```{.c tiedosto="esimerkit/02-liukuluvut.c" osa="tarkkuus"}
```

Matemaattiset funktiot ovat otsikossa `<math.h>`:

```{.c tiedosto="esimerkit/02-liukuluvut.c" osa="math"}
```

```{.tuloste tiedosto="esimerkit/02-liukuluvut.odotettu"}
```

Rahasummat ja muut tarkkuutta vaativat arvot kannattaa tallentaa
kokonaislukuina, esimerkiksi sentteinä.

## Vakiot, `bool` ja tyyppipäättely

Vakiot on perinteisesti määritelty esikääntäjän makroina. C23:n
`constexpr` luo tyypitetyn vakion, jonka arvo tunnetaan käännösaikana.
Toisin kuin makrolla, sillä on tyyppi ja näkyvyysalue, ja se näkyy
debuggerissa.

```{.c tiedosto="esimerkit/02-vakiot.c" osa="vakiot"}
```

`const` puolestaan tarkoittaa vain, ettei muuttujaa saa muuttaa. Sen
arvo voi selvitä vasta ajoaikana:

```{.c tiedosto="esimerkit/02-vakiot.c" osa="const"}
```

C23:ssa `bool`, `true` ja `false` ovat avainsanoja. Aiemmissa
standardeissa ne otettiin käyttöön otsikolla `<stdbool.h>`. Tyhjät
aaltosulkeet `{}` alustavat muuttujan tai taulukon nolliksi
(aiemmin kirjoitettiin `{0}`):

```{.c tiedosto="esimerkit/02-vakiot.c" osa="bool"}
```

C23 toi myös tyyppipäättelyn: `auto` päättelee muuttujan tyypin
alustuslausekkeesta ja `typeof` antaa lausekkeen tyypin. Ne ovat
hyödyllisimpiä makroissa; tavallisessa koodissa tyypin kirjoittaminen
auki on yleensä selkeämpää.

```{.c tiedosto="esimerkit/02-vakiot.c" osa="paattely"}
```
