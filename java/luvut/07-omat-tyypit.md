# Luokat, recordit, rajapinnat ja geneerisyys {.runko-omat-tyypit}

## Arvotyypit: `record`

`record` (Java 16) on muuttumaton tietue, jolle kääntäjä tuottaa
konstruktorin, lukumetodit, `equals`-, `hashCode`- ja
`toString`-metodit. Se on oikea valinta arvoille: rahasummille,
tunnisteille, viesteille ja tuloksille. *Kompakti konstruktori*
validoi tai normalisoi parametrit ennen kenttien asettamista, joten
virheellistä oliota ei voi olla olemassa:

```{.java tiedosto="esimerkit/07-raha.java" osa="raha"}
```

```{.java tiedosto="esimerkit/07-raha.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-raha.odotettu"}
```

Malleja esimerkissä:

- **Staattinen tehdasmetodi** (`Raha.euroa`). Sillä on kuvaava nimi, se
  voi jäsentää ja validoida, ja se voi palauttaa välimuistissa olevan
  olion (`NOLLA`).
- **Muuttumattomuus.** `plus` palauttaa uuden olion. Muuttumaton olio on
  säieturvallinen ja kelpaa hajautusavaimeksi.
- **Vahva tyyppi primitiivin sijaan.** Metodi `maksa(Raha summa)` ei
  hyväksy vahingossa tuotemäärää, toisin kuin `maksa(long summa)`.

Recordin kentät ovat `final`, mutta kentässä oleva lista voi silti
muuttua. Siksi kokoelmakentät kopioidaan kompaktissa konstruktorissa
(`List.copyOf`), kuten rakentajaesimerkissä alla.

## Suljetut hierarkiat ja kuvioiden sovitus

`sealed`-rajapinta (Java 17) luettelee sallitut toteutuksensa. Yhdessä
recordien ja `switch`-kuvioiden (Java 21) kanssa se on Javan
*algebrallinen tietotyyppi*: arvo on täsmälleen yksi tunnetuista
muodoista, ja kääntäjä tarkistaa, että jokainen muoto käsitellään:

```{.java tiedosto="esimerkit/07-maksut.java" osa="tyypit"}
```

```{.java tiedosto="esimerkit/07-maksut.java" osa="kulut"}
```

```{.java tiedosto="esimerkit/07-maksut.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-maksut.odotettu"}
```

*Record-kuvio* `Kortti(long s, String verkko)` purkaa recordin kentät
muuttujiksi, ja `when` lisää ehdon. Haarat tarkistetaan järjestyksessä,
joten tarkempi haara kirjoitetaan ensin. Kun hierarkiaan lisätään uusi
tyyppi, jokainen `switch` ilman `default`-haaraa lakkaa kääntymästä:

```{.java tiedosto="esimerkit/07-kattavuus.ei-kaanny.java" osa="koodi"}
```

```
07-kattavuus.ei-kaanny.java:22: error: the switch expression does not
cover all possible input values
```

Kun `permits` puuttuu, sallitut tyypit ovat samassa tiedostossa
määritellyt toteutukset.

Suljettu hierarkia ja kuvioiden sovitus on vaihtoehto
*vierailijamallille* (*visitor*) ja virtuaalimetodeille. Valinta riippuu
siitä, kumpi muuttuu useammin (*lausekeongelma*, *expression problem*):
jos tyyppejä lisätään usein ja operaatiot pysyvät, operaatio kuuluu
rajapinnan metodiksi. Jos operaatioita lisätään usein ja tyyppijoukko on
vakaa, kuten tapahtumissa, viesteissä ja syntaksipuussa, käytetään
`sealed`-tyyppiä ja `switch`iä.

## Luokat, kapselointi ja periytyminen

Tavallinen luokka on oikea valinta, kun oliolla on muuttuvaa tilaa ja
invariantteja: yhteys, välimuisti, tilakone, laskuri. Kentät ovat
`private` ja mieluiten `final`; tilaa muutetaan vain metodeilla, jotka
säilyttävät invariantit. Näkyvyysmääreet ovat `private`, pakkauksen
sisäinen (ei määrettä), `protected` ja `public`.

Periytyminen (`extends`) kytkee aliluokan yliluokan toteutukseen.
Yliluokan muutos voi rikkoa aliluokan (*fragile base class*), ja
konstruktorista kutsuttu ylikirjoitettava metodi näkee keskeneräisen
olion (`-Xlint:this-escape` varoittaa). Siksi luokat tehdään `final`iksi,
ellei niitä ole suunniteltu perittäviksi, ja toiminnallisuutta
yhdistetään *koostamalla*: olio sisältää toisen olion ja delegoi sille.

## Rajapinnat ja koostaminen

Rajapinta määrittää käyttäytymisen. Oletusmetodi (`default`, Java 8)
antaa rajapinnalle toteutuksen, joka rakentuu abstraktien metodien
päälle. *Koristelija* (*decorator*) toteuttaa saman rajapinnan ja lisää
toiminnallisuutta delegoimalla:

```{.java tiedosto="esimerkit/07-koostaminen.java" osa="rajapinta"}
```

```{.java tiedosto="esimerkit/07-koostaminen.java" osa="koristelija"}
```

```{.java tiedosto="esimerkit/07-koostaminen.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-koostaminen.odotettu"}
```

Koska `Hinnoittelu` on funktionaalinen rajapinta, perustoteutus on
lambda. Kirjaus, alennus, välimuisti ja uudelleenyritys voidaan
lisätä koristelijoina muuttamatta perustoteutusta.

## Rakentaja

Kun oliolla on monta valinnaista kenttää, konstruktori, jolla on
kymmenen parametria, on altis virheille. *Rakentaja* (*builder*)
kerää arvot nimetyillä metodeilla ja validoi kokonaisuuden lopuksi:

```{.java tiedosto="esimerkit/07-rakentaja.java" osa="pyynto"}
```

```{.java tiedosto="esimerkit/07-rakentaja.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-rakentaja.odotettu"}
```

Pakolliset arvot annetaan tehdasmetodille (`Pyynto.get(osoite)`), joten
niitä ei voi unohtaa. Rakentajan konstruktori on yksityinen.
`HttpClient`, `HttpRequest` ja `Thread.ofVirtual()` käyttävät samaa mallia.

## Geneerisyys

Geneeriset tyypit ja metodit (`List<T>`, `<T> T suurin(...)`)
tarkistetaan käännösaikana, mutta ajonaikana tyyppiparametrit
poistetaan (*type erasure*): `List<Integer>` ja `List<String>` ovat sama
luokka. Siksi `new T()`, `T[]` ja `instanceof List<String>` eivät ole
mahdollisia, eikä primitiivi kelpaa tyyppiparametriksi.

```{.java tiedosto="esimerkit/07-geneerinen.java" osa="suurin"}
```

```{.java tiedosto="esimerkit/07-geneerinen.java" osa="pecs"}
```

```{.java tiedosto="esimerkit/07-geneerinen.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-geneerinen.odotettu"}
```

Jokerit (*wildcards*) tekevät rajapinnasta joustavan. Sääntö on *PECS*:
*producer extends, consumer super*. Lista, josta luetaan T:itä, on
`List<? extends T>`, ja kokoelma, johon kirjoitetaan T:itä, on
`Collection<? super T>`. Siksi `muunna` hyväksyy `List<Integer>`in
lähteeksi, `Function<Number, Double>`in muunnokseksi ja
`List<Number>`in kohteeksi. `Comparable<? super T>` sallii luokan, joka
perii vertailun yliluokaltaan.

Raakatyyppejä (`List` ilman tyyppiparametria) ei käytetä; ne ovat
olemassa vain yhteensopivuuden vuoksi, ja `-Xlint:rawtypes` varoittaa
niistä.

## `enum`

`enum` on luokka, jolla on kiinteä joukko instansseja. Sillä voi olla
kenttiä, konstruktori ja metodeja, ja se on oikea tapa toteuttaa
*singleton* (`enum Asetukset { INSTANSSI; }`). `EnumMap` ja `EnumSet`
ovat nopeimmat kokoelmat `enum`-avaimille. `ordinal()`-arvoa ei
tallenneta tiedostoon tai tietokantaan, koska se muuttuu, kun arvojen
järjestys muuttuu; tallennetaan `name()`.

## Käytännössä

- **Data `record`eiksi, tila luokiksi.** Recordin ja tavallisen luokan
  raja on muuttuva tila. Getterit ja setterit jokaiselle kentälle ovat
  vanhan Javan (JavaBeans) perintöä.
- **Tee virheellisistä tiloista mahdottomia.** Validoi konstruktorissa,
  käytä vahvoja tyyppejä (`Raha`, `Sahkoposti`) primitiivien sijaan ja
  mallinna vaihtoehdot `sealed`-tyypeillä nollattavien kenttien sijaan.
- **`final` oletuksena.** Luokat, kentät ja mieluiten paikalliset
  muuttujat. Periytyminen on suunniteltu ominaisuus, ei oletus.
- **Koostaminen periytymisen sijaan.** Koristelija, strategia
  (funktionaalinen rajapinta) ja delegointi.
- **Staattiset tehdasmetodit ja rakentajat** konstruktorien sijaan, kun
  luonnissa on logiikkaa tai valinnaisia parametreja. Nimeämiskäytäntö:
  `of`, `from`, `parse`, `copyOf`, `newX`.
- **Rajapinnat pieniksi.** Asiakas riippuu vain metodeista, joita se
  käyttää (*interface segregation*). Funktionaalinen rajapinta on pienin
  mahdollinen.
- **Hinta.** Record on tavallinen olio, ei arvotyyppi: sillä on otsake
  ja se on keossa. Project Valhalla tuo Javaan oikeat arvotyypit
  tulevaisuudessa. Kuvioiden sovitus `switch`issä käännetään tehokkaaksi
  tyyppitarkistukseksi.

## Itsearviointi

- Osaat kirjoittaa `record`in, joka validoi kenttänsä ja kopioi
  kokoelmakentät.
- Osaat mallintaa vaihtoehdot `sealed`-rajapinnalla ja käsitellä ne
  kattavasti `switch`-kuvioilla.
- Osaat perustella, milloin käytät `sealed`-tyyppiä ja milloin
  rajapinnan metodia.
- Osaat toteuttaa koristelijan ja rakentajan.
- Osaat kirjoittaa geneerisen metodin rajatuilla tyyppiparametreilla ja
  jokereilla PECS-säännön mukaan.
- Osaat kertoa, mitä tyyppien poisto estää.
