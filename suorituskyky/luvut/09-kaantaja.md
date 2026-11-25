# Kääntäjän optimoinnit

Kääntäjä on tehokkain optimointityökalu, mutta vain jos sille antaa
oikeat liput ja tarpeeksi tietoa. Tässä luvussa käydään läpi
optimointitasot, kohdesuorittimen valinta, funktioiden sisällyttäminen
(engl. inlining) käännösyksiköiden yli linkitysaikaisella
optimoinnilla sekä profiiliohjattu optimointi.

## Optimointitasot

| Taso | Mitä tekee | Käyttö |
|----------|----------------------------------------|--------------------|
| `-O0` | Ei optimointeja; jokainen muuttuja muistissa | Debuggaus |
| `-Og` | Optimoinnit, jotka eivät haittaa debuggausta | Kehitys |
| `-O1` | Perusoptimoinnit: rekisterit, vakioiden laskenta, kuolleen koodin poisto | Harvoin |
| `-O2` | Lähes kaikki, jotka eivät kasvata koodia paljon; kevyt vektorointi | Tuotannon oletus |
| `-O3` | Lisäksi aggressiivinen vektorointi, silmukoiden avaus ja kloonaus | Laskentaydin |
| `-Os`, `-Oz` | Pieni koodi | Sulautetut, käskyvälimuisti |
| `-Ofast` | `-O3` ja `-ffast-math` | Vain, kun liukulukusemantiikka saa muuttua |

Tasojen ero näkyy parhaiten laskentaytimessä. Esimerkkinä on luvun 11
tapaustutkimuksen laatikkosumennus, jossa kuvan jokainen pikseli
korvataan ympäristönsä keskiarvolla. Tässä riittää tietää, että sen
viimeinen vaihe on kaksi sisäkkäistä silmukkaa kokonaislukutaulukoiden
yli. Sama lähdekoodi käännettynä eri tasoilla:

```{.makefile tiedosto="esimerkit/Makefile" osa="tasot"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tasot.txt"}
```

Taso `-O0` on moninkertaisesti hitaampi kuin `-O2`, joten
optimoimatonta koodia ei koskaan mitata. Taso `-O3` vektoroi sisimmän
silmukan ja on tässä selvästi nopeampi, mutta koodi kasvaa puolella.
Suuressa ohjelmassa kasvu voi hidastaa käskyvälimuistin ja
haarautumisen ennustimen takia, joten `-O3` ei ole automaattisesti
parempi: se valitaan mittaamalla, ja usein vain kuumille tiedostoille.

`-march=native` sallii kaikki käännöskoneen käskyt, kuten AVX-512:n.
Ohjelma ei silloin välttämättä käynnisty vanhemmalla koneella.
Jakelukelpoinen vaihtoehto on x86-64-mikroarkkitehtuuritaso
(`-march=x86-64-v2`, `v3` AVX2:lla, `v4` AVX-512:lla) tai ajonaikainen
valinta (luku 8). `-mtune=native` järjestää käskyt koneen mukaan
käyttämättä uusia käskyjä, ja se on aina turvallinen.

## Sisällyttäminen ja käännösyksiköt

Funktiokutsun hinta on muutama jakso, mutta suurempi hinta on se, mitä
kutsu estää: kääntäjä ei voi vektoroida silmukkaa, laskea vakioita
etukäteen tai poistaa turhia latauksia kutsun yli, jos se ei näe
funktion sisään. Kääntäjä näkee vain yhden käännösyksikön kerrallaan.
Seuraavassa funktio on omassa tiedostossaan, ja muut näkevät siitä
vain esittelyn:

```{.c tiedosto="esimerkit/09-lto/geometria.h"}
```

```{.c tiedosto="esimerkit/09-lto/geometria.c" osa="etaisyys"}
```

```{.c tiedosto="esimerkit/09-lto/main.c" osa="lahin"}
```

```{.tuloste tiedosto="esimerkit/09-lto.odotettu"}
```

Lähimmän pisteen haku kutsuu toisen tiedoston funktiota joka
kierroksella, eikä kääntäjä voi sisällyttää sitä. Ratkaisuja on
kaksi. Pieni ja kuuma funktio voidaan siirtää otsikkotiedostoon
`static inline` -funktioksi, jolloin jokainen käyttäjä näkee sen.
Vaihtoehtoisesti *linkitysaikainen optimointi* (engl. link-time
optimization, LTO) tallentaa objektitiedostoihin kääntäjän välikielen
ja tekee optimoinnit vasta linkityksessä, kun koko ohjelma on näkyvissä:

```{.makefile tiedosto="esimerkit/Makefile" osa="lto"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-lto.txt"}
```

LTO-käännöksessä kutsuja ei ole lainkaan, koska `etaisyys2` on
sisällytetty silmukkaan. Makefile tarkistaa tämän konekoodista.
Mittaus:

```{.tuloste tiedosto="esimerkit/tulokset/09-lto.txt"}
```

LTO kaksinkertaisti nopeuden muuttamatta riviäkään koodia. Hinta on
pidempi linkitys, ja suurissa projekteissa käytetään siksi rinnakkaista
tai inkrementaalista muotoa (`-flto=auto`, Clangin ThinLTO
`-flto=thin`). Jaetuissa kirjastoissa kääntäjä ei saa sisällyttää
julkisia funktioita, koska ne voidaan korvata ajon aikana
(`LD_PRELOAD`, ks. *Objektitiedostot, linkitys ja ABI*). Lippu
`-fno-semantic-interposition` tai piilotettu näkyvyys
(`-fvisibility=hidden`) antaa luvan.

## Profiiliohjattu optimointi

Kääntäjä arvaa, mitkä haarat ovat todennäköisiä, mitkä funktiot
kuumia ja mitkä silmukat pitkiä. *Profiiliohjattu optimointi* (engl.
profile-guided optimization, PGO) korvaa arvaukset mittauksilla:

1. Ohjelma käännetään instrumentoituna (`-fprofile-generate`).
2. Ohjelma ajetaan edustavalla kuormalla, ja se kirjoittaa
   haarojen ja kutsujen laskurit profiilitiedostoihin.
3. Ohjelma käännetään uudelleen profiilin kanssa (`-fprofile-use`).

```{.makefile tiedosto="esimerkit/Makefile" osa="pgo"}
```

Kääntäjä käyttää profiilia haarojen järjestämiseen niin, että yleinen
polku on peräkkäin, kuumien funktioiden sisällyttämiseen, kylmän
koodin siirtämiseen erilleen (`.text.unlikely`), `switch`-lauseiden
järjestämiseen ja silmukoiden avaamiseen todellisten kierrosmäärien
mukaan. Lokianalyysin nopea versio ilman profiilia ja profiilin
kanssa:

```{.tuloste tiedosto="esimerkit/tulokset/04-lokit.txt"}
```

```{.tuloste tiedosto="esimerkit/tulokset/04-lokit-pgo.txt"}
```

Viimeisen rivin ero oli kirjoittajan koneella muutaman prosentin
luokkaa, ja sen suunta vaihteli ajosta toiseen kohinan mukana. Suurissa
ohjelmissa, joissa on paljon haaroja ja kutsuja, kuten kääntäjissä,
tietokannoissa ja selaimissa, PGO tuo tyypillisesti 10–20 %; GCC,
Clang, Chromium ja Firefox käännetään jakeluissa PGO:lla. Profiili on
kerättävä kuormalla, joka vastaa todellista käyttöä: väärällä
kuormalla kerätty profiili optimoi väärät polut ja voi hidastaa
ohjelmaa. Makefile tarkistaa myös, että PGO-käännös antaa saman
tuloksen kuin tavallinen:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-pgo.txt"}
```

Pidemmälle vietyjä työkaluja ovat AutoFDO, joka kerää profiilin
tuotannosta `perf`-näytteillä ilman instrumentointia, ja BOLT, joka
järjestää valmiin binäärin koodin uudelleen profiilin mukaan.

## Kääntäjän tutkiminen

Kääntäjän tekemiset näkee konekoodista. `gcc -O2 -S tiedosto.c`
kirjoittaa assemblyn, `objdump -d -S ohjelma` näyttää konekoodin
lähdekoodirivien kanssa, ja Compiler Explorer (godbolt.org) näyttää
saman selaimessa monella kääntäjällä rinnakkain. Optimointiraportit
(`-fopt-info`, `-Rpass`) kertovat, mitkä muunnokset tehtiin ja miksi
jotkin jäivät tekemättä. Ennen kuin kirjoittaa koodin uudelleen
nopeuden takia, kannattaa katsoa, mitä kääntäjä jo teki.

## Käytännössä

- **Mittaa aina optimoitu käännös**, sama taso kuin tuotannossa.
- **Käytä tuotannossa `-O2`:ta ja kokeile `-O3`:a** kuumille
  tiedostoille. Pidä muutos vain, jos mittaus puoltaa.
- **Valitse kohdesuoritin tietoisesti.** `-march=native` omalle
  koneelle, mikroarkkitehtuuritaso jaettavalle binäärille.
- **Ota LTO käyttöön** julkaisukäännöksissä. Se on halpa tapa saada
  sisällyttäminen käännösyksiköiden yli.
- **Käytä PGO:ta suurissa ja haaraisissa ohjelmissa**, ja kerää
  profiili edustavalla kuormalla osana julkaisuputkea.
- **Lue konekoodi** ennen käsin optimointia ja sen jälkeen.

## Itsearviointi

- Osaat valita optimointitason ja kohdesuorittimen ja perustella
  valinnan.
- Osaat selittää, miksi funktiokutsu toiseen käännösyksikköön estää
  optimointeja, ja korjata sen otsikkotiedostolla tai LTO:lla.
- Osaat rakentaa ohjelman profiiliohjatusti kolmessa vaiheessa ja
  kertoa, mitä kääntäjä profiililla tekee.
- Osaat tarkistaa konekoodista, sisällyttikö kääntäjä funktion.
