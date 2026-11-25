# Symbolien sidonta ajon aikana

Dynaaminen linkkeri sitoo jokaisen viittauksen nimen perusteella.
Kun sama nimi on määritelty usealla ladatulla tiedostolla, se valitsee
ensimmäisen *hakujärjestyksessä* (*global scope*). Järjestys on:

1. kirjastot ympäristömuuttujasta `LD_PRELOAD`,
2. ohjelma itse,
3. ohjelman `NEEDED`-kirjastot linkitysjärjestyksessä, sitten niiden
   riippuvuudet leveyssuuntaisesti.

Sääntö koskee myös kirjaston omia viittauksia omiin globaaleihin
symboleihinsa, koska ne kulkevat PLT:n ja GOT:n kautta (luku 8).
Saman säännön kaksi seurausta ovat tämän luvun aihe: vahingossa
tapahtuva törmäys ja tarkoituksellinen korvaaminen.

## Kaksi kirjastoa, sama sisäinen nimi

Kuvakirjasto ja äänikirjasto ovat eri tekijöiden, ja kummassakin on
sisäinen apufunktio `tarkista`, joka jäi vahingossa julkiseksi:

```{.c tiedosto="esimerkit/10-tormays/kuva.c" osa="kuva"}
```

```{.c tiedosto="esimerkit/10-tormays/aani.c"}
```

```{.c tiedosto="esimerkit/10-tormays/main.c"}
```

```{.bash tiedosto="esimerkit/10-tormays/aja.sh" osa="tormays"}
```

```{.tuloste tiedosto="esimerkit/10-tormays/odotettu"}
```

Molemmat kirjastot linkittyvät ilman varoitusta, ja ohjelma toimii
väärin: äänikirjasto kutsuu kuvakirjaston funktiota, koska
`libkuva.so` on hakujärjestyksessä ensin. Kun järjestys vaihdetaan,
vika siirtyy toiseen kirjastoon. Linkkeri ei varoita, koska
kaksoismäärittely jaettujen kirjastojen välillä on ELF:ssä sallittua:
juuri se mahdollistaa korvaamisen.

Korjaus on piilottaa sisäinen funktio (luku 8), jolloin kirjaston oma
viittaus sidotaan suoraan omaan määrittelyyn:

```{.c tiedosto="esimerkit/10-tormays/aani-piilo.c" osa="piilo"}
```

```{.bash tiedosto="esimerkit/10-tormays/aja.sh" osa="korjattu"}
```

Ohjelmaa ei tarvinnut linkittää uudelleen. Korjatun kirjaston
dynaamisessa symbolitaulussa on vain `lataa_aani`. Törmäykset ovat
yleisiä, kun kaksi kirjastoa sisältää saman kolmannen kirjaston
staattisesti linkitettynä (esimerkiksi eri versiot zlibistä tai
OpenSSL:stä): kumpikin vie sen symbolit, ja vain toinen versio voittaa.
Piilottaminen (`-Wl,--exclude-libs,ALL` piilottaa staattisten
arkistojen symbolit) ratkaisee sen.

## Tarkoituksellinen korvaus: LD_PRELOAD

`LD_PRELOAD` lisää kirjaston hakujärjestyksen alkuun. Sen symbolit
voittavat ohjelman ja kaikkien muiden kirjastojen symbolit. Tällä
tehdään *kääreitä* (*interposer*), jotka tarkkailevat tai muuttavat
kirjastokutsuja ilman lähdekoodia: muistinhallinnan vaihto
(`jemalloc`, `tcmalloc`), muistivirheiden etsintä, verkkoliikenteen
ohjaus ja testien vikojen simulointi.

Esimerkin ohjelma lukee asetukset ensimmäisestä löytyvästä
tiedostosta:

```{.c tiedosto="esimerkit/10-preload/main.c"}
```

Kääre määrittelee oman `fopen`-funktion. Se hakee alkuperäisen
funktion `dlsym(RTLD_NEXT, ...)`-kutsulla, joka etsii nimeä
hakujärjestyksessä *kääreen jälkeen*, eli C-kirjastosta:

```{.c tiedosto="esimerkit/10-preload/tiedostomittari.c" osa="kaare"}
```

```{.bash tiedosto="esimerkit/10-preload/aja.sh" osa="preload"}
```

```{.tuloste tiedosto="esimerkit/10-preload/odotettu"}
```

Kääre näyttää, että ohjelma etsi ensin tiedostoa `oma.conf` ja
käytti sitten tiedostoa `yleinen.conf`. Sama tieto saadaan
`strace`:llä järjestelmäkutsujen tasolla, mutta kääre näkee
kirjastotason kutsut ja voi muuttaa niiden tulosta.

Kääreen säännöt:

- **Säilytä `errno`.** Kääreen omat kutsut (tässä `fprintf`) voivat
  muuttaa sitä, ja kutsuja lukee sen virheen syynä.
- **Varo rekursiota.** Jos kääreen käyttämä funktio kutsuu
  käärittyä funktiota, syntyy ikuinen silmukka. `malloc`-kääre ei
  voi käyttää `printf`:ää, joka varaa muistia.
- **Säikeet.** Alkuperäisen funktion haku ja laskurit on suojattava,
  jos ohjelma on monisäikeinen (`pthread_once`, atomiset laskurit).
- **Kaikki kutsut eivät kulje PLT:n kautta.** C-kirjaston sisäiset
  kutsut käyttävät piilotettuja nimiä, eikä kääre näe niitä.
  Staattisesti linkitetty ohjelma ei käytä `LD_PRELOAD`:ia lainkaan.

Linkkeri tukee myös käännösaikaista käärettä: `-Wl,--wrap=fopen`
ohjaa ohjelman `fopen`-viittaukset funktioon `__wrap_fopen` ja nimen
`__real_fopen` alkuperäiseen. Tämä toimii staattisessakin
linkityksessä ja sopii yksikkötesteihin.

## Ajonaikainen lataus: dlopen

`dlopen` lataa kirjaston ajon aikana, ja `dlsym` hakee siitä symbolin
osoitteen. Näin toteutetaan liitännäiset: ohjelma ei tiedä
linkityksessä, mitkä kirjastot se lataa.

| Lippu | Vaikutus |
|-------|----------|
| `RTLD_NOW` | sido kaikki symbolit heti, virhe palautetaan heti |
| `RTLD_LAZY` | sido funktiot ensimmäisessä kutsussa |
| `RTLD_LOCAL` | kirjaston symbolit eivät tule hakujärjestykseen (oletus) |
| `RTLD_GLOBAL` | symbolit tulevat myöhemmin ladattavien käyttöön |
| `RTLD_DEEPBIND` | kirjasto etsii symboleita ensin itsestään |

Liitännäisen rajapinta kannattaa tehdä yhdestä `extern "C"`
-funktiosta, joka palauttaa funktio-osoitinrakenteen. Liitännäinen
tarvitsee usein ohjelman omia symboleita, ja ne on silloin vietävä
ohjelman dynaamiseen symbolitauluun valitsimella `-rdynamic`
(`-Wl,--export-dynamic`) tai tarkemmin `--dynamic-list`-tiedostolla.

## Käytännössä

- **Piilota kaikki, mikä ei ole rajapintaa.** Törmäyksen voi aiheuttaa
  kuka tahansa muu ladattu kirjasto, eikä mikään työkalu varoita.
- **Linkitä kirjastot valitsimella `-Wl,-z,defs`.** Se vaatii, että
  kirjaston kaikki viittaukset ratkeavat sen riippuvuuksista, ja
  paljastaa puuttuvat `-l`-valitsimet kirjaston eikä sen käyttäjän
  linkityksessä.
- **Etsi törmäyksiä `LD_DEBUG=bindings`:llä.** Se kertoo jokaisen
  sidonnan: `binding file libaani.so to libkuva.so: normal symbol
  'tarkista'` paljastaa väärän kohteen heti.
- **Käytä `LD_PRELOAD`:ia diagnostiikkaan ja testeihin**, ei
  tuotantologiikan korjaamiseen. Kääre on näkymätön lähdekoodin
  lukijalle.

## Itsearviointi

- Osaat kuvata dynaamisen linkkerin hakujärjestyksen ja kertoa, miksi
  kirjaston oma viittaus voi sitoutua toiseen kirjastoon.
- Osaat tunnistaa symbolitörmäyksen oireet ja korjata sen
  näkyvyydellä.
- Osaat kirjoittaa `LD_PRELOAD`-kääreen, joka kutsuu alkuperäistä
  funktiota `dlsym(RTLD_NEXT, ...)`:lla ja säilyttää `errno`n.
- Osaat valita `LD_PRELOAD`:n, linkkerin `--wrap`-valitsimen ja
  `dlopen`:n välillä.
