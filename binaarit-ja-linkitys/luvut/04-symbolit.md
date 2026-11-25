# Symbolit

Symboli on nimi, jolla on osoite: funktio, muuttuja tai osion kohta.
Jokaisella objektitiedostolla on symbolitaulu (`.symtab`), jossa on
kaksi listaa: symbolit, jotka tiedosto *määrittelee*, ja symbolit,
joihin se *viittaa* mutta joita se ei määrittele. Linkkerin
päätehtävä on yhdistää jokainen viittaus täsmälleen yhteen
määrittelyyn.

Jokaisella symbolilla on kolme ominaisuutta:

| Ominaisuus | Arvot | Mistä tulee |
|------------|-------|-------------|
| sidonta (*binding*) | `LOCAL`, `GLOBAL`, `WEAK` | `static`, oletus, `__attribute__((weak))` |
| tyyppi | `FUNC`, `OBJECT`, `SECTION`, `FILE` | funktio, muuttuja, osio, lähdetiedosto |
| näkyvyys (*visibility*) | `DEFAULT`, `HIDDEN`, `PROTECTED` | `__attribute__((visibility))`, `-fvisibility` |

Sidonta ratkaisee, näkyykö symboli muille objektitiedostoille.
Näkyvyys ratkaisee, näkyykö se jaetun kirjaston ulkopuolelle (luku 8).
`readelf -s` näyttää kaikki kolme, `nm` tiivistää ne yhteen kirjaimeen.

## Paikallinen, globaali ja heikko

Esimerkin lokikirjasto numeroi rivit ja kirjoittaa ne kohteeseen,
jonka sovellus voi halutessaan korvata:

```{.c tiedosto="esimerkit/04-symbolit/loki.c" osa="loki"}
```

`static` tekee sekä muuttujasta `rivinro` että funktiosta `muotoile`
paikallisia: nimet ovat symbolitaulussa (virheenjäljitystä varten),
mutta linkkeri ei yhdistä niitä muiden tiedostojen viittauksiin.
Toinen tiedosto voi määritellä oman `rivinro`-muuttujansa ilman
törmäystä. Attribuutti `noipa` estää tässä esimerkissä kääntäjää
upottamasta funktiota, jotta se näkyy symbolitaulussa.

Heikko symboli (`weak`) on oletus, jonka vahva määrittely korvaa.
Sovellus antaa oman kohteensa tavallisena funktiona:

```{.c tiedosto="esimerkit/04-symbolit/oma_kohde.c" osa="oma"}
```

```{.bash tiedosto="esimerkit/04-symbolit/aja.sh" osa="linkitys"}
```

```{.tuloste tiedosto="esimerkit/04-symbolit/odotettu"}
```

Pienet kirjaimet `t` ja `b` ovat paikallisia symboleita, isot
globaaleja. `W` on heikko määritelty symboli. Ensimmäisessä
linkityksessä ainoa määrittely on heikko, ja se valitaan. Toisessa
`oma_kohde.o` antaa vahvan määrittelyn, ja linkkeri hylkää heikon
ilman virheilmoitusta. Kirjaston koodi ei muutu: `loki` kutsuu nimeä
`loki_kohde`, ja linkkeri päättää, mihin nimi osoittaa.

`nm`:n yleisimmät kirjaimet:

| Kirjain | Merkitys | Esimerkki |
|---------|----------|-----------|
| `T` / `t` | koodi (`.text`) | funktio |
| `D` / `d` | alustettu data (`.data`) | `int n = 5;` |
| `B` / `b` | nollattu data (`.bss`) | `static int n;` |
| `R` / `r` | vain luettava data (`.rodata`) | `const int t[3]` |
| `U` | määrittelemätön, haetaan muualta | kutsuttu kirjastofunktio |
| `W` / `w` | heikko, määritelty / määrittelemätön | oletustoteutus |
| `V` / `v` | heikko objekti | heikko muuttuja |
| `A` | absoluuttinen arvo, ei osoite | linkkeriskriptin vakio |
| `i` | epäsuora funktio (IFUNC) | `memcpy` glibc:ssä |

Heikkoja symboleita käytetään kolmeen tarkoitukseen. *Korvattava
oletus*, kuten tässä: sulautettujen järjestelmien
keskeytysvektoreissa jokainen käsittelijä on heikko alias
oletuskäsittelijälle, ja sovellus määrittelee vain tarvitsemansa.
*Valinnainen riippuvuus*: heikko viittaus (`extern void f(void)
__attribute__((weak));`) saa arvon nolla, jos määrittelyä ei ole,
joten koodi voi tarkistaa `if (f) f();`. *Kirjastojen sisäinen
yhteensopivuus*: glibc määrittelee monet funktiot heikkoina
aliaksina sisäisille nimille.

C++:ssa heikot symbolit ovat arkea, vaikka niitä ei kirjoiteta itse.
`inline`-funktio, mallin instanssi ja luokan virtuaalitaulu käännetään
jokaiseen käännösyksikköön, joka niitä käyttää, koska kääntäjä ei
tiedä, mikä muu tiedosto tekee saman. Määrittelyt ovat heikkoja (`nm`
näyttää `W` ja `V`), ja jokainen on omassa *COMDAT-ryhmässään*:
linkkeri pitää samannimisistä ryhmistä yhden ja hylkää muut. Tämä
toimii, kun kaikki kopiot ovat samat, minkä C++:n *yhden määrittelyn
sääntö* (ODR) vaatii. Linkkeri ei tarkista sitä. Jos kaksi tiedostoa
määrittelee samannimisen `inline`-funktion eri sisällöllä, toinen
katoaa hiljaa, ja se, kumpi jää, riippuu linkitysjärjestyksestä.

> Heikko symboli jaetussa kirjastossa ei toimi kuten
> objektitiedostossa. Dynaaminen linkkeri ei oletuksena tee eroa
> heikon ja vahvan välillä, vaan valitsee ensimmäisen löytämänsä
> määrittelyn hakujärjestyksessä (luku 10). Korvattava oletus kuuluu
> staattiseen linkitykseen.

## Yhteiset symbolit ja `-fno-common`

C sallii *alustavat määrittelyt* (*tentative definition*): `int n;`
tiedoston tasolla ilman `extern`-sanaa. Vanhat kääntäjät tallensivat
ne *yhteisinä symboleina* (`COMMON`, `nm`:ssä `C`), ja linkkeri
yhdisti saman nimen eri tiedostoista yhdeksi muuttujaksi. Kahdessa
tiedostossa määritelty `int koontinumero;` linkittyi siis ilman
virhettä, vaikka kyseessä oli todennäköisesti vahinko.

GCC 10:stä alkaen oletus on `-fno-common`: alustava määrittely on
tavallinen `.bss`-muuttuja, ja kaksoismäärittely on virhe (luku 6).
Oikea tapa jakaa muuttuja tiedostojen kesken on määritellä se yhdessä
tiedostossa ja esitellä otsakkeessa `extern`-sanalla:

```text
/* asetukset.h */   extern int koontinumero;
/* asetukset.c */   int koontinumero = 0;
```

Vanhan koodin voi kääntää valitsimella `-fcommon`, mutta parempi on
korjata esittelyt.

## Symbolitaulun lukeminen

`nm` on nopea, `readelf -s` on tarkka. Hyödyllisiä valitsimia:

| Komento | Näyttää |
|---------|---------|
| `nm -u f.o` | vain määrittelemättömät symbolit |
| `nm --defined-only f.o` | vain määritellyt |
| `nm -g f.o` | vain globaalit (ja heikot) |
| `nm -C f.o` | C++-nimet purettuina (luku 13) |
| `nm -D libx.so` | dynaaminen symbolitaulu (`.dynsym`) |
| `nm -S --size-sort f.o` | koot, suurimmat viimeisenä |
| `readelf -sW f.o` | sidonta, tyyppi, näkyvyys, osion numero |

Jaetuissa kirjastoissa ja ohjelmissa on kaksi symbolitaulua.
`.symtab` sisältää kaikki symbolit, ja `strip` poistaa sen.
`.dynsym` sisältää vain symbolit, joita dynaaminen linkkeri tarvitsee
(viedyt ja tuodut), eikä sitä voi poistaa. Riisutun kirjaston
rajapinnan näkee siksi aina komennolla `nm -D`.

## Käytännössä

- **Tee kaikesta `static`, mikä ei ole rajapintaa.** Paikallinen
  symboli ei voi törmätä, kääntäjä voi optimoida sen vapaammin, ja
  lukija näkee heti, ettei sitä käytetä muualla.
- **Esittele jaetut muuttujat otsakkeessa `extern`-sanalla** ja
  määrittele ne täsmälleen yhdessä tiedostossa. Älä nojaa
  `-fcommon`-käytökseen.
- **Käytä heikkoja symboleita harkiten.** Ne sopivat staattisesti
  linkitettäviin oletustoteutuksiin ja keskeytysvektoreihin. Jos vahva
  määrittely puuttuu kirjoitusvirheen vuoksi, heikko oletus valitaan
  hiljaa, joten testaa, että korvaus todella tapahtuu.
- **Tarkista rajapinta riisutusta tiedostosta.** `nm -D --defined-only
  libx.so` näyttää, mitä kirjasto todella vie.

## Itsearviointi

- Osaat selittää symbolin sidonnan, tyypin ja näkyvyyden ja kertoa,
  mikä C:n rakenne kunkin määrää.
- Osaat lukea `nm`:n tulosteen ja erottaa paikalliset, globaalit,
  heikot ja määrittelemättömät symbolit.
- Osaat käyttää heikkoa symbolia korvattavana oletuksena ja kertoa,
  miksi se ei toimi samoin jaetuissa kirjastoissa.
- Osaat selittää, mitä `-fno-common` muutti ja miten jaettu muuttuja
  esitellään oikein.
