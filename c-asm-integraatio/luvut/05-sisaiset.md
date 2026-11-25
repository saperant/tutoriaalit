# Kääntäjän sisäiset funktiot ja SIMD

Inline-assembly on optimoijalle musta laatikko: se ei tiedä, mitä
käsky laskee, joten se ei voi siirtää, yhdistää eikä laskea sitä
valmiiksi. *Sisäiset funktiot* ratkaisevat tämän. Ne näyttävät
C-funktioilta, mutta kääntäjä tuntee niiden merkityksen ja muuttaa ne
suoraan käskyiksi, tai käskyjonoksi, jos kohdeprosessorilla ei ole
sopivaa käskyä. Rekisterien varaus, ajoitus ja vakioiden laskeminen
toimivat normaalisti. Sisäisiä funktioita on kahta lajia:

- **GCC:n yleiset sisäiset funktiot** (`__builtin_*`): kaikilla
  arkkitehtuureilla toimivat bittioperaatiot, ylivuototarkistukset ja
  vihjeet optimoijalle.
- **Arkkitehtuurin sisäiset funktiot** (*intrinsics*): valmistajan
  määrittelemät funktiot kullekin käskylle, kuten Intelin
  `immintrin.h` ja RISC-V:n `riscv_vector.h`. Ne ovat yhteisiä GCC:lle,
  Clangille ja (x86:lla) MSVC:lle.

## Yleiset sisäiset funktiot

Tavallisimmat bittioperaatiot ovat C:llä hankalia kirjoittaa ja
suorittimilla yksi käsky:

```{.c tiedosto="esimerkit/05-builtinit/bitit.c" osa="bitit"}
```

```{.tuloste tiedosto="esimerkit/05-builtinit/odotettu"}
```

| Funktio | Merkitys | Huomio | C23:n vastine |
|---------|----------|--------|---------------|
| `__builtin_popcountll(x)` | ykkösbittien määrä | | `stdc_count_ones(x)` |
| `__builtin_ctzll(x)` | nollat alimmasta bitistä alkaen | määrittelemätön, kun `x == 0` | `stdc_trailing_zeros(x)` |
| `__builtin_clzll(x)` | nollat ylimmästä bitistä alkaen | määrittelemätön, kun `x == 0` | `stdc_leading_zeros(x)` |
| `__builtin_bswap64(x)` | tavujärjestyksen kääntö | myös 16 ja 32 bittiä | – |
| `__builtin_add_overflow(a, b, &t)` | yhteenlasku ja ylivuototieto | kaikille kokonaislukutyypeille | `ckd_add(&t, a, b)` |
| `__builtin_expect(e, v)` | `e`:n todennäköinen arvo on `v` | vaikuttaa vain koodin järjestykseen | – |
| `__builtin_unreachable()` | tähän ei koskaan tulla | väärin käytettynä määrittelemätön käytös | `unreachable()` |

C23 toi osalle näistä standardinimet: bittifunktiot otsakkeessa
`<stdbit.h>`, tarkistettu aritmetiikka otsakkeessa `<stdckdint.h>` ja
`unreachable()` otsakkeessa `<stddef.h>`. Standardin bittifunktiot
ovat tyyppigeneerisiä ja määriteltyjä myös nollalle
(`stdc_trailing_zeros(0ul)` on 64), joten uudessa koodissa ne ovat
turvallisempi valinta. `__builtin_*`-muotoja tarvitaan yhä, kun koodin
pitää kääntyä vanhemmalla kääntäjällä tai C-kirjastolla: tämän
tutoriaalin RISC-V-ristikääntäjässä (GCC 13) otsaketta
`<stdckdint.h>` ei vielä ole.

Sisäinen funktio ei lupaa yhtä käskyä. Se lupaa oikean tuloksen ja
parhaan toteutuksen, jonka kääntäjä *kohdeprosessorille* tuntee. Kohde
valitaan valitsimilla `-march` ja `-m`, ja ero on suuri:

```{.bash tiedosto="esimerkit/05-builtinit/tarkistus.sh" osa="kohteet"}
```

```{.tuloste tiedosto="esimerkit/05-builtinit/tarkistus.odotettu"}
```

Perustason x86-64 (vuoden 2003 AMD64) ei sisällä `popcnt`-käskyä, joten
`__builtin_popcountll` muuttuu libgcc:n funktion `__popcountdi2`
kutsuksi. Valitsimella `-mpopcnt` (tai `-march=x86-64-v2` ja uudemmat)
siitä tulee yksi käsky. Käskyä edeltävä `xor` nollaa kohderekisterin,
koska monissa Intelin suorittimissa `popcnt` odottaa turhaan
kohderekisterin vanhaa arvoa; kääntäjä tuntee tällaiset
yksityiskohdat, joita käsin kirjoittaja ei useinkaan tunne. RISC-V:n
perustaso (RV64GC) ei sisällä bittioperaatioita lainkaan; ne ovat
laajennuksessa Zbb, jonka kanssa sekä ykkösten laskenta (`cpop`) että
tavujen kääntö (`rev8`) ovat yksittäisiä käskyjä.

`__builtin_expect` ei muuta tulosta vaan koodin järjestystä. Harvinainen
haara siirretään pois kuumasta polusta, jolloin yleinen tapaus suoritetaan
ilman hyppyä ja vie vähemmän välimuistia:

```{.c tiedosto="esimerkit/05-builtinit/bitit.c" osa="odotus"}
```

Linuxin `likely`- ja `unlikely`-makrot ovat juuri tämä. C++20
tarjoaa saman standardina (`[[likely]]` ja `[[unlikely]]`), C ei. Vihjettä kannattaa
käyttää vain virhepoluissa, joiden harvinaisuus on varma;
profiiliohjattu optimointi (`-fprofile-use`) tekee saman mitatuilla
todennäköisyyksillä.

## Arkkitehtuurin sisäiset funktiot

Intelin sisäisten funktioiden nimet kertovat vektorin leveyden,
operaation ja alkion tyypin:

| Osa | Merkitys | Esimerkki |
|-----|----------|-----------|
| `_mm_`, `_mm256_`, `_mm512_` | 128, 256 tai 512 bittiä | `_mm256_add_epi32` |
| `epi8`, `epi16`, `epi32`, `epi64` | etumerkilliset kokonaisluvut | `_mm_cmpeq_epi8` |
| `epu8` … | etumerkittömät | `_mm_max_epu8` |
| `ps`, `pd` | float, double | `_mm_mul_ps` |
| `si128`, `si256` | koko rekisteri bitteinä | `_mm_loadu_si128` |
| `__m128i`, `__m256`, … | vektorityypit | |

RISC-V:n vektorilaajennuksen funktiot alkavat `__riscv_`-etuliitteellä,
ja niiden nimessä on käsky, alkion tyyppi ja *LMUL*, eli montako
vektorirekisteriä yksi arvo käyttää: `__riscv_vle8_v_u8m1` lataa
etumerkittömiä tavuja yhteen rekisteriin. Toisin kuin x86:n kiinteän
levyiset vektorit, RISC-V:n vektorin pituus selviää vasta ajon aikana.
Sama ohjelma toimii 128-bittisellä ja 1024-bittisellä toteutuksella.

## SIMD käytännössä: tavujen laskenta

Ensimmäisen luvun funktio laski tavun esiintymät tavu kerrallaan.
SIMD-versio vertaa 16 tavua kerralla. SSE2 kuuluu x86-64:n
perustasoon, joten tätä versiota ei tarvitse suojata ajonaikaisella
tunnistuksella:

```{.c tiedosto="esimerkit/05-simd/simd.c" osa="sse2"}
```

```{.dot otsikko="Yksi silmukan kierros, kun haetaan merkkiä `a` (periaatekuva). Vertailu tekee jokaisesta tavusta `FF`:n tai `00`:n, `movemask` poimii tavujen ylimmät bitit yhdeksi luvuksi, ja ykkösbittien määrä on osumien määrä."}
digraph {
  rankdir=TB; nodesep=0.2; ranksep=0.35;
  node [shape=plain, style=""];
  v [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="8"><i>v: 16 tavua muistista (8 ensimmäistä)</i></td></tr>
    <tr><td bgcolor="#FFFFFF">b</td><td bgcolor="#F3E2C7">a</td><td bgcolor="#FFFFFF">n</td><td bgcolor="#F3E2C7">a</td><td bgcolor="#FFFFFF">n</td><td bgcolor="#F3E2C7">a</td><td bgcolor="#FFFFFF">a…</td><td bgcolor="#FFFFFF">…</td></tr></table>>];
  y [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="8"><i>yhtasuuret = cmpeq(v, haettava)</i></td></tr>
    <tr><td bgcolor="#FFFFFF">00</td><td bgcolor="#F3E2C7">FF</td><td bgcolor="#FFFFFF">00</td><td bgcolor="#F3E2C7">FF</td><td bgcolor="#FFFFFF">00</td><td bgcolor="#F3E2C7">FF</td><td bgcolor="#FFFFFF">…</td><td bgcolor="#FFFFFF">…</td></tr></table>>];
  m [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left"><i>maski = movemask(yhtasuuret)</i></td></tr>
    <tr><td bgcolor="#EEF1F6">bitit 0–5: 0 1 0 1 0 1 … (bitti i = tavu i)</td></tr></table>>];
  p [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td bgcolor="#EEF1F6">m += popcount(maski)</td></tr></table>>];
  v -> y -> m -> p;
}
```

Vertailu tuottaa jokaiseen tavuun joko `0xFF` tai `0`, ja
`movemask` kokoaa tavujen ylimmät bitit 16-bittiseksi maskiksi, jonka
ykköset lasketaan. Silmukan lopussa jäljelle jäävät alle 16 tavua
käsitellään skalaarisesti. Edellisen osion perusteella
`__builtin_popcount` on perustason x86-64:llä kirjastokutsu; 16-bittiselle
maskille se on silti nopea, ja valitsin `-mpopcnt` tekee siitä käskyn.

RISC-V:n vektoriversiossa erillistä loppuosaa ei tarvita. `vsetvl`
kertoo jokaisella kierroksella, montako alkiota käsitellään: täysi
vektori tai jäljellä oleva määrä, jos se on pienempi.

```{.c tiedosto="esimerkit/05-simd/simd.c" osa="rvv"}
```

RISC-V-versio käännetään valitsimella `-march=rv64gcv`, joka sallii
V-laajennuksen käskyt. Ohjelma toimii vain prosessorilla, jolla
laajennus on; esimerkeissä QEMU emuloi sitä.

## Tarkista skalaariversiota vastaan

SIMD-koodin tavalliset virheet ovat rajoilla: puskurin lopussa,
tasaamattomissa osoitteissa ja pituuksissa, jotka eivät ole vektorin
leveyden monikertoja. Siksi testi käy läpi kaikki pituudet ja kaikki
alkukohdat vertailuversiota vastaan, ei vain muutamaa "tavallista"
syötettä:

```{.c tiedosto="esimerkit/05-simd/main.c" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/05-simd/odotettu"}
```

Vertailuversio on samassa ohjelmassa, ja se on merkitty
`noipa`-attribuutilla, jottei kääntäjä yhdistä sitä testiin. Testin
data tulee kiinteällä siemenellä alustetusta pseudosatunnaisgeneraattorista,
joten jokainen ajo on samanlainen ja virhe toistuu.

## Vektoroiko kääntäjä itse?

Ennen sisäisiä funktioita kannattaa kysyä, tarvitaanko niitä.
GCC vektoroi silmukoita automaattisesti, ja skalaariversio on juuri
sellainen silmukka, jonka se tunnistaa. Tarkistus kääntää sen eri
tasoilla ja laskee vektorikäskyt:

```{.bash tiedosto="esimerkit/05-simd/tarkistus.sh" osa="automaattinen"}
```

```{.tuloste tiedosto="esimerkit/05-simd/tarkistus.odotettu"}
```

Tulos on opettavainen kahdella tavalla. GCC 14 vektoroi x86-64:llä
silmukan `-O3`:lla mutta ei `-O2`:lla: `-O2`:n kustannusmalli sallii
vain vektoroinnin, joka ei tarvitse erillistä loppuosaa, ja tämän
silmukan pituus on tuntematon. Lisäksi käskyjä on kymmenkertainen
määrä, koska kääntäjä laajentaa tavuvertailun tulokset 64-bittisiksi
summiksi useassa vaiheessa. RISC-V-ristikääntäjä (GCC 13) ei vektoroi
silmukkaa lainkaan, vaikka V-laajennus on sallittu. Automaattinen
vektorointi riippuu siis kääntäjäversiosta, arkkitehtuurista ja
optimointitasosta, ja sen tuloksen voi tarkistaa vain katsomalla
käskyjä. Valitsin `-fopt-info-vec-missed` kertoo, miksi silmukkaa ei
vektoroitu.

## Käytännössä

- **Sisäinen funktio ennen inline-assemblyä.** Jos käskylle on
  sisäinen funktio, käytä sitä. Optimoija ajoittaa sen, varaa sille
  rekisterit ja voi laskea sen valmiiksi vakioilla.
- **Automaattinen vektorointi ensin.** Kirjoita silmukka
  yksinkertaisesti (`restrict`-osoittimet, tunnettu alkiotyyppi, ei
  haaroja silmukan sisällä) ja tarkista käskyt. Sisäisiin funktioihin
  siirrytään, kun kääntäjä ei vektoroi tai tekee sen huonosti, ja
  mittaus osoittaa sen merkitykselliseksi.
- **Säilytä skalaariversio.** Se on testien vertailukohta, varapolku
  prosessoreille ilman laajennusta ja dokumentaatio siitä, mitä
  SIMD-koodi laskee.
- **Testaa rajat.** Kaikki pituudet nollasta muutamaan vektorin
  leveyteen, kaikki tasaukset ja ääriarvot (`0x00`, `0x80`, `0xFF`).
- **`loadu` eikä `load`.** Tasaamaton lataus on nykyprosessoreilla
  yhtä nopea, kun data sattuu olemaan tasattu, eikä kaadu, kun se ei
  ole.
- **Tiedä kohdetaso.** `-march=x86-64-v2`, `-v3` ja `-v4` ovat
  nimettyjä x86-64-tasoja (v3 sisältää AVX2:n), ja RISC-V:n
  profiilit (RVA22, RVA23) kokoavat laajennukset vastaavasti. Jos
  jakelu käyttää perustasoa, uudempia käskyjä käytetään vain
  ajonaikaisen tunnistuksen takana (seuraava luku).

## Itsearviointi

- Osaat käyttää bittioperaatioiden sisäisiä funktioita ja kertoa,
  miten niiden toteutus riippuu kohdeprosessorista.
- Osaat lukea Intelin sisäisten funktioiden nimistä vektorin
  leveyden ja alkion tyypin ja kirjoittaa SSE2-silmukan loppuosineen.
- Osaat kirjoittaa RISC-V:n vektorisilmukan `vsetvl`-kutsulla ja
  selittää, miksi se ei tarvitse erillistä loppuosaa.
- Osaat testata SIMD-toteutuksen skalaariversiota vastaan kaikilla
  pituuksilla ja tasauksilla.
- Osaat tarkistaa, vektoroiko kääntäjä silmukan, ja selittää, miksi
  tulos vaihtelee optimointitason ja kääntäjän mukaan.
