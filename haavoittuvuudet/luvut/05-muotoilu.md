# Muotoilumerkkijonovirheet

`printf`-perheen ensimmäinen argumentti on *muotoilumerkkijono*: pieni
ohjelma, joka kertoo, montako argumenttia luetaan ja miten ne
tulkitaan. Jos käyttäjän syöte päätyy siihen, syöte ohjelmoi
tulostuksen. Virhe on yksinkertainen ja sen korjaus vielä
yksinkertaisempi, mutta se on hyvä esimerkki laajemmasta periaatteesta:
**data ei saa päätyä paikkaan, jossa se tulkitaan koodina tai
ohjeina**. Sama periaate on SQL-injektion, komentoinjektion ja
Log4Shellin (luku 10) taustalla.

## Haavoittuva loki

Tapahtumaloki kirjaa käyttäjän viestin:

```{.c tiedosto="esimerkit/05-muotoilu/loki.c" osa="kirjaa"}
```

Kääntäjä varoittaa heti, koska muotoilumerkkijono ei ole vakio eikä
muita argumentteja ole:

```{.tuloste tiedosto="esimerkit/05-muotoilu/odotettu" osa="t1"}
```

Ubuntun GCC kääntää oletuksena valitsimilla `-Wformat
-Wformat-security`, ja esimerkiksi Debianin ja Fedoran pakettien
käännösasetukset tekevät jälkimmäisestä virheen.
Varoitusta ei siis pidä vaientaa. Tässä se ohitetaan, jotta virheen
vaikutus voidaan näyttää:

```{.bash tiedosto="esimerkit/05-muotoilu/aja.sh" osa="kaanna"}
```

```{.tuloste tiedosto="esimerkit/05-muotoilu/odotettu" osa="t2"}
```

## Tietovuoto

Kun viestissä on muotoilumerkkejä, `printf` lukee argumentteja, joita
ei annettu. x86-64:llä ensimmäiset argumentit ovat rekistereissä ja
loput pinossa, joten `%lx` tulostaa rekisterien ja pinon sisältöä.
Kutsuva funktio pitää pinossa istuntoavainta:

```{.c tiedosto="esimerkit/05-muotoilu/loki.c" osa="kasittele"}
```

Skripti kokeilee sijainnit 1–40 numeroiduilla muotoilumerkeillä
(`%7$lx` lukee seitsemännen argumentin) ja katsoo, näkyykö avain
tulosteessa. Arvoja ei tulosteta; testi kertoo vain, vuotiko avain:

```{.bash tiedosto="esimerkit/05-muotoilu/aja.sh" osa="vuoto"}
```

```{.tuloste tiedosto="esimerkit/05-muotoilu/odotettu" osa="t3"}
```

Avain vuoti lokiin. Sama vuoto paljastaisi myös pinokanarin ja
osoitteita, joiden satunnaistus (luku 6) on muuten suojaus: siksi
muotoilumerkkijonovirhe arvioidaan vakavaksi, vaikka se ei itse
kirjoita mihinkään. Pelkkä luku on CVSS-luokituksessa
luottamuksellisuuden menetys (luku 11).

## Kirjoittava muotoilumerkki ja FORTIFY_SOURCE

Muotoilumerkki `%n` ei tulosta mitään vaan *kirjoittaa* siihen
mennessä tulostettujen merkkien määrän argumenttina annettuun
osoitteeseen. Hallitsemattomassa muotoilumerkkijonossa se on
kirjoitusoperaatio, jonka kohde tulee pinosta. Siksi glibc:n
FORTIFY_SOURCE-tila tarkistaa, että `%n` esiintyy vain kirjoitussuojatussa
muotoilumerkkijonossa, eli vakiossa:

```{.bash tiedosto="esimerkit/05-muotoilu/aja.sh" osa="fortify"}
```

```{.tuloste tiedosto="esimerkit/05-muotoilu/odotettu" osa="t4"}
```

Viesti tuli muuttuvasta puskurista, joten tarkistus lopetti ohjelman
ennen kirjoitusta. FORTIFY_SOURCE vaatii optimoinnin (`-O1` tai
enemmän), ja tasot 2 ja 3 lisäävät myös puskurien kokotarkistuksia
(luku 6).

## Korjaus

Viesti annetaan aina argumenttina, ei muotoilumerkkijonona:
`printf("%s", viesti)` tai `fputs(viesti, stdout)`. Korjattu versio
tulostaa muotoilumerkit sellaisinaan, eikä avain enää vuoda:

```{.tuloste tiedosto="esimerkit/05-muotoilu/odotettu" osa="t5"}
```

Omat tulostusfunktiot, jotka välittävät muotoilun eteenpäin
(`vprintf`-tyyliset), merkitään GCC:n attribuutilla
`__attribute__((format(printf, 1, 2)))`. Silloin kääntäjä tarkistaa
myös niiden kutsut samoin kuin `printf`:n.

## Käytännössä

- **Muotoilumerkkijono on aina vakio.** `printf("%s", x)`, ei
  `printf(x)`. Sama koskee `syslog`-, `snprintf`- ja omia
  lokifunktioita.
- **Merkitse omat muotoilufunktiot** `format`-attribuutilla, jotta
  varoitukset kattavat ne.
- **Pidä `-Wformat=2 -Werror=format-security` päällä** ja
  FORTIFY_SOURCE julkaisukäännöksessä.
- **Älä kirjaa salaisuuksia** edes oikein muotoiltuna: avaimet,
  salasanat ja istuntotunnisteet eivät kuulu lokiin.

## Itsearviointi

- Osaat selittää, miksi käyttäjän syöte muotoilumerkkijonona voi lukea
  pinoa ja rekistereitä.
- Osaat perustella, miksi pelkkä tietovuoto voi heikentää muita
  suojauksia.
- Osaat selittää `%n`:n vaaran ja sen, miten FORTIFY_SOURCE pysäyttää
  sen.
- Osaat korjata virheen ja merkitä oman lokifunktion
  `format`-attribuutilla.
