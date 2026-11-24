# Käännösprosessi

Komento `gcc main.c tilasto.c -lm` näyttää yhdeltä vaiheelta, mutta
kääntäjäajuri ajaa neljä erillistä ohjelmaa: esikäsittelijän,
varsinaisen kääntäjän, assemblerin ja linkkerin. Rakennusjärjestelmät
ohjaavat juuri näitä vaiheita, ja useimmat rakennusvirheet kuuluvat
selvästi yhteen niistä. Kun tietää, mikä vaihe valittaa, tietää myös,
mistä korjaus löytyy.

| Vaihe | Ohjelma | Valitsin | Syöte → tuloste |
|-------|---------|----------|-----------------|
| esikäsittely | `cpp` | `-E` | `.c` → käännösyksikkö |
| käännös | `cc1` | `-S` | käännösyksikkö → `.s` |
| kokoaminen | `as` | `-c` | `.s` → `.o` |
| linkitys | `ld` | (oletus) | `.o`, `.a`, `.so` → ohjelma |

## Esikäsittely

Esikäsittelijä liittää `#include`-tiedostot, laajentaa makrot ja
poistaa kommentit. Sen tuloste on *käännösyksikkö*: yksi pitkä
C-tiedosto, jossa ei enää ole esikäsittelijän direktiivejä. Esimerkin
pieni funktio käyttää kahta makroa:

```{.c tiedosto="esimerkit/01-vaiheet/pinta.c"}
```

Esimerkkien komentosarja ajaa vaiheet yksi kerrallaan. Valitsin `-E`
pysäyttää esikäsittelyn jälkeen, ja `-P` jättää pois rivinumeromerkinnät,
joita kääntäjä tarvitsee virheilmoituksiin:

```{.bash tiedosto="esimerkit/01-vaiheet/aja.sh" osa="esikasittely"}
```

Makrojen sulut näkyvät sellaisinaan: `NELIO(sivu)` on muuttunut
lausekkeeksi `((sivu) * (sivu))`. Kun käännösvirhe on makron sisällä tai
otsakkeet määrittelevät jotain odottamatonta, `-E` näyttää, mitä
kääntäjä todella näki. Oikeassa ohjelmassa käännösyksikkö on usein
kymmeniätuhansia rivejä, koska jokainen `#include <stdio.h>` tuo
mukanaan kaikki sen omat otsakkeet. Tämä on syy siihen, että
otsakkeiden muutos on rakennusjärjestelmälle tärkeä tieto: otsake on
osa jokaista sen lukevaa käännösyksikköä.

## Käännös ja kokoaminen

Varsinainen kääntäjä tuottaa käännösyksiköstä assemblyä. Valitsin `-S`
pysäyttää tähän vaiheeseen; esimerkki suodattaa tulosteesta pois
assemblerin direktiivit (`.cfi_*` ja muut), jotta funktion käskyt
näkyvät:

```{.bash tiedosto="esimerkit/01-vaiheet/aja.sh" osa="kaannos"}
```

Optimoinnin (`-O2`) jälkeen funktiossa on yksi vertailu, ehdollinen
hyppy ja kertolasku. Ensimmäinen käsky `endbr64` on Ubuntun
oletuksena käyttämän ohjausvuon suojauksen (`-fcf-protection`) merkki.
Assemblyn lukeminen ei kuulu tämän tutoriaalin aiheisiin, mutta sen
tuottaminen kuuluu: kun kaksi rakennusta käyttäytyy eri tavalla, `-S`
ja eri valitsimien vertailu kertovat, tuottiko kääntäjä eri koodin.

Assembler muuttaa assemblyn konekieliseksi *objektitiedostoksi*.
Valitsin `-c` ajaa kaikki vaiheet kokoamiseen asti, ja juuri sitä
rakennusjärjestelmät käyttävät: jokainen `.c`-tiedosto käännetään
erikseen omaksi `.o`-tiedostokseen. Objektitiedoston symbolitaulu
kertoo, mitä se määrittelee ja mitä se tarvitsee muualta:

```{.bash tiedosto="esimerkit/01-vaiheet/aja.sh" osa="objektit"}
```

## Linkitys

Linkkeri yhdistää objektitiedostot ja kirjastot ohjelmaksi. Se etsii
jokaiselle puuttuvalle (`U`) symbolille määrittelyn. `main.o`
tarvitsee tilastofunktiot, jotka `tilasto.o` määrittelee, ja
`tilasto.o` tarvitsee `qsort`- ja `sqrt`-funktiot. Ensimmäinen löytyy
C-kirjastosta, joka linkitetään aina, jälkimmäinen matematiikkakirjastosta
`libm`, joka on pyydettävä erikseen:

```{.bash tiedosto="esimerkit/01-vaiheet/aja.sh" osa="linkitys"}
```

Koko ajo tulostaa vaiheet järjestyksessä:

```{.tuloste tiedosto="esimerkit/01-vaiheet.odotettu"}
```

Linkkerin virhe `undefined reference` tarkoittaa aina samaa: jokin
objektitiedosto käyttää symbolia, jota mikään linkitettävä tiedosto ei
määrittele. Syy on lähes aina yksi kolmesta: kirjasto puuttuu
komentoriviltä, kirjasto on komentorivillä väärässä kohdassa (ennen sitä
käyttävää objektitiedostoa, jolloin staattisesta kirjastosta ei vielä
tarvittu mitään) tai määrittely on käännetty eri nimellä (C++:n
nimenmuunnos tai puuttuva `extern "C"`). Kääntäjän virheet taas
koskevat yhtä käännösyksikköä kerrallaan. Kun virheilmoitus mainitsee
`.o`-tiedoston tai `ld`:n, vika ei ole lähdekoodin syntaksissa vaan
siinä, mitä linkitetään.

Linkkerin toimintaa, symbolien näkyvyyttä ja objektitiedostojen
rakennetta käsitellään syvemmin taidossa *Objektitiedostot, linkitys
ja ABI*. Tässä riittää, että linkitys on oma vaiheensa, jolla on omat
syötteensä: kirjastot ja niiden järjestys kuuluvat rakennusjärjestelmän
kuvaukseen samoin kuin lähdetiedostot.

## Erillinen käännös

Koska jokainen `.c`-tiedosto käännetään erikseen objektitiedostoksi, vain
muuttuneet tiedostot tarvitsee kääntää uudelleen. Linkitys tehdään joka
kerta, mutta se on nopea verrattuna kääntämiseen. Tämä on
rakennusjärjestelmien perusajatus. Sillä on myös hintansa: kääntäjä näkee
vain yhden käännösyksikön kerrallaan, joten se ei voi tarkistaa, että
`main.c` kutsuu funktiota samalla tavalla kuin `tilasto.c` sen
määrittelee. Tarkistuksen tekee yhteinen otsake, jonka molemmat
lukevat. Siksi toteutustiedoston on luettava oma otsakkeensa
ensimmäisenä (`#include "tilasto.h"` tiedoston `tilasto.c` alussa):
ristiriita otsakkeen ja määrittelyn välillä on silloin käännösvirhe eikä
linkityksen jälkeen ilmenevä outo käytös.

## Käytännössä

- **Lue virheilmoituksesta vaihe.** Esikäsittelijä valittaa
  puuttuvasta otsakkeesta, kääntäjä syntaksista ja tyypeistä, linkkeri
  puuttuvista ja kahdesti määritellyistä symboleista. Linkkerivirhettä
  ei korjata lähdekoodia muokkaamalla vaan linkitettäviä tiedostoja
  ja niiden järjestystä muuttamalla.
- **Kirjastot objektitiedostojen jälkeen.** `-lm` ja muut kirjastot
  kirjoitetaan komentorivin loppuun. Make tarjoaa tähän muuttujan
  `LDLIBS`, joka on oletussäännöissä oikeassa kohdassa.
- **`-E` ja `-S` ovat diagnostiikkatyökaluja.** Makro-ongelmat
  ratkeavat esikäsitellyn tulosteen avulla, optimointiongelmat
  assemblyn avulla. Kumpaakaan ei tarvitse arvata.
- **Toteutustiedosto lukee oman otsakkeensa ensin.** Näin otsake on
  todistetusti itsenäinen (se ei tarvitse muita `#include`-rivejä
  ennen itseään), ja määrittelyn ja esittelyn ristiriita on
  käännösvirhe.

## Itsearviointi

- Osaat ajaa käännöksen vaiheet erikseen valitsimilla `-E`, `-S` ja
  `-c` ja kertoa, mitä kukin vaihe tuottaa.
- Osaat lukea `nm`-komennon tulosteesta, mitä objektitiedosto
  määrittelee ja mitä se tarvitsee.
- Osaat päätellä virheilmoituksesta, kuuluuko se kääntäjälle vai
  linkkerille, ja korjata puuttuvan kirjaston aiheuttaman
  `undefined reference` -virheen.
- Osaat perustella, miksi erillinen käännös nopeuttaa rakentamista ja
  miksi otsakkeen muutos koskee kaikkia sitä lukevia tiedostoja.
