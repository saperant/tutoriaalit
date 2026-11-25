# Syöte, tuloste ja tiedostot {.runko-tyypit}

Ohjelma saa tietonsa komentoriviltä, vakiosyötteestä ja tiedostoista ja
kirjoittaa tuloksensa virtoihin. C:n standardikirjasto käsittelee näitä
kaikkia saman `FILE`-rajapinnan kautta. Tässä luvussa luetaan
argumentteja ja rivejä, kirjoitetaan teksti- ja binääritiedostoja ja
tarkistetaan jokaisen vaiheen onnistuminen.

## Komentoriviargumentit

`main`-funktio voi ottaa kaksi parametria: argumenttien määrän `argc` ja
taulukon `argv`, jonka alkiot ovat argumentteja merkkijonoina.
`argv[0]` on ohjelman nimi, ja `argv[argc]` on tyhjä osoitin.

```{.c tiedosto="esimerkit/10-argumentit.c" osa="argumentit"}
```

Ajettuna komennolla

```text
./summa 1.5 2 kolme --tarkka 4.25
```

ohjelma tulostaa:

```{.tuloste tiedosto="esimerkit/10-argumentit.odotettu"}
```

Lisäksi virheviesti `ohitetaan virheellinen luku: kolme` menee
*virhevirtaan* `stderr`. Ohjelmalla on kolme valmiiksi avattua
virtaa: `stdin` (syöte), `stdout` (tuloste) ja `stderr` (virheet).
Virheet kannattaa kirjoittaa `stderr`-virtaan, jotta ne eivät sekoitu
tulosteeseen, kun tuloste ohjataan tiedostoon tai toiselle ohjelmalle.
Paluuarvo `EXIT_FAILURE` kertoo kutsujalle, että ohjelma epäonnistui.

Muotoilumääre `%.*f` ottaa tarkkuuden argumenttina.

## Rivien lukeminen

Syöte kannattaa lukea riveittäin funktiolla `fgets`, joka lukee
enintään puskurin koon verran merkkejä eikä siksi voi ylivuotaa.
Se jättää rivinvaihdon merkkijonoon, ja se poistetaan usein
`strcspn`-funktion avulla. Luettu rivi jäsennetään sitten erikseen,
esimerkiksi `sscanf`-funktiolla, jonka paluuarvo kertoo, montako kenttää
onnistuttiin lukemaan:

```{.c tiedosto="esimerkit/10-rivit.c" osa="rivit"}
```

Syötteellä

```{.tuloste tiedosto="esimerkit/10-rivit.syote"}
```

ohjelma tulostaa:

```{.tuloste tiedosto="esimerkit/10-rivit.odotettu"}
```

Merkkijonomääreeseen `%s` on aina annettava enimmäispituus (`%63s`),
muuten pitkä sana ylivuotaa puskurin. `scanf`-funktion käyttöä suoraan
syötteeseen kannattaa välttää: virheellinen syöte jää lukematta
puskuriin, ja ohjelma voi juuttua silmukkaan. Lukeminen riveittäin
ja jäsentäminen erikseen on vankempaa.

## Tekstitiedostot

Tiedosto avataan funktiolla `fopen`, joka palauttaa `FILE *`-osoittimen
tai tyhjän osoittimen, jos avaaminen epäonnistuu. Toinen argumentti on
*tila*: `"r"` lukemiseen, `"w"` kirjoittamiseen (vanha sisältö
poistetaan) ja `"a"` loppuun lisäämiseen. Tiedostoon kirjoitetaan
samoilla funktioilla kuin päätteelle: `fprintf`, `fputs` ja `fputc`.

```{.c tiedosto="esimerkit/10-tiedostot.c" osa="kirjoita"}
```

Kun kirjastofunktio epäonnistuu, se asettaa yleensä muuttujan `errno`
(`<errno.h>`) kertomaan syyn. `perror` tulostaa syyn selväkielisenä
`stderr`-virtaan, ja `strerror` palauttaa sen merkkijonona.

`fgetc` palauttaa merkin `int`-tyyppisenä, koska sen on voitava
palauttaa kaikkien merkkien lisäksi erikoisarvo `EOF`. Paluuarvon
tallentaminen `char`-muuttujaan on klassinen virhe. `EOF` voi tarkoittaa
tiedoston loppua tai lukuvirhettä; ne erotetaan funktioilla `feof` ja
`ferror`.

```{.c tiedosto="esimerkit/10-tiedostot.c" osa="lue"}
```

```{.c tiedosto="esimerkit/10-tiedostot.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-tiedostot.odotettu"}
```

Jokainen avattu tiedosto on suljettava `fclose`-funktiolla. Tuloste on
puskuroitu, joten data kirjoitetaan levylle viimeistään sulkemisen
yhteydessä, ja kirjoitusvirhe voi paljastua vasta silloin.

## Binääritiedostot

`fwrite` ja `fread` kirjoittavat ja lukevat muistin sisällön
sellaisenaan. Tila `"b"` (`"wb"`, `"rb"`) estää rivinvaihtojen
muunnokset alustoilla, joilla tekstitiedostoja käsitellään eri tavoin
(Windows). `fseek` siirtää lukukohtaa ja `ftell` kertoo sen.

```{.c tiedosto="esimerkit/10-binaari.c" osa="tyyppi"}
```

```{.c tiedosto="esimerkit/10-binaari.c" osa="kirjoitus"}
```

```{.c tiedosto="esimerkit/10-binaari.c" osa="luku"}
```

```{.tuloste tiedosto="esimerkit/10-binaari.odotettu"}
```

Rakenteiden kirjoittaminen sellaisinaan on nopeaa, mutta tiedosto on
sidottu alustaan: kenttien koko, täyte ja tavujärjestys voivat olla
toisella koneella erilaiset. Siirrettävissä tiedostomuodoissa kentät
kirjoitetaan yksitellen kiinteänkokoisina ja sovitussa
tavujärjestyksessä.

## Omat muotoilufunktiot

`printf` ottaa vaihtelevan määrän argumentteja. Oman vastaavan funktion
voi kirjoittaa otsikon `<stdarg.h>` makroilla: parametriluettelon lopun
`...` hyväksyy loput argumentit, `va_start` alustaa niiden läpikäynnin
ja `va_end` päättää sen. Tavallisin käyttö on lokifunktio, joka
välittää argumentit edelleen `printf`-perheen `v`-alkuiselle
funktiolle:

```{.c tiedosto="esimerkit/10-loki.c" osa="loki"}
```

```{.c tiedosto="esimerkit/10-loki.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-loki.odotettu"}
```

Kääntäjä ei tiedä vaihtuvien argumenttien tyyppejä, joten väärä
muotoilumääre on määrittelemätöntä käyttäytymistä. GCC:n ja Clangin
attribuutti `format` palauttaa tarkistuksen: sen ansiosta
`loki(VIRHE, "%s", 42)` antaa saman varoituksen kuin vastaava
`printf`-kutsu. Todellinen lokifunktio kirjoittaisi `stderr`-virtaan
(`vfprintf`); tässä käytetään vakiotulostetta, jotta tuloste näkyy
esimerkissä.

## Käytännössä

- **Lue rivi, jäsennä erikseen.** `fgets` ja sen jälkeen `sscanf`,
  `strtol` tai oma jäsennin. `scanf` suoraan syötteeseen jättää
  virheellisen syötteen puskuriin.
- **Ohjelma putken osana.** Tulos `stdout`iin, virheet `stderr`iin ja
  paluuarvona `EXIT_SUCCESS` tai `EXIT_FAILURE`. Silloin ohjelmaa voi
  käyttää skripteissä ja yhdistää muihin työkaluihin.
- **Turvallinen tallennus.** Tiedosto kirjoitetaan ensin
  väliaikaistiedostoon, tarkistetaan `fclose`n paluuarvo ja vaihdetaan
  tiedosto paikalleen `rename`-kutsulla. Kaatuminen kesken kirjoituksen
  ei silloin tuhoa vanhaa versiota.
- **Komentorivi.** Laajemmissa ohjelmissa valitsimet jäsennetään POSIX:n
  `getopt`illa tai GNU:n `getopt_long`illa, joten ohjelma käyttäytyy kuten
  muut komentorivityökalut.
- **Binäärimuodot** kirjoitetaan kenttä kerrallaan kiinteänkokoisina ja
  sovitussa tavujärjestyksessä, ja muodolle annetaan versionumero.
- **Puskurointi.** `stdout` on päätteellä rivipuskuroitu mutta putkessa
  täysin puskuroitu. Jos tulosteen on näyttävä heti, esimerkiksi ennen
  pitkää laskentaa, kutsutaan `fflush(stdout)`.

## Itsearviointi

- Osaat lukea syötteen riveittäin ja jäsentää rivit niitä validoiden.
- Osaat käsitellä komentoriviargumentit ja palauttaa oikean paluuarvon.
- Osaat kirjoittaa ja lukea tiedoston niin, että kaikki virhetilanteet
  tarkistetaan, myös `fclose`.
- Osaat selittää, miksi rakenteen kirjoittaminen tiedostoon sellaisenaan
  ei ole siirrettävää.
