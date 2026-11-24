# SIMD-käskyjen perusteet

SIMD-käsky (*single instruction, multiple data*) tekee saman
operaation usealle arvolle kerralla. 128-bittinen rekisteri sisältää
neljä 32-bittistä kokonaislukua, ja yksi yhteenlaskukäsky laskee neljä
summaa. Kuvan- ja äänenkäsittely, kryptografia, tiivistefunktiot,
merkkijonojen haku ja matriisilaskenta nojaavat SIMD-käskyihin. Tämä
luku esittelee käsitteet yhden esimerkin avulla. Tuotantokoodissa SIMD
kirjoitetaan yleensä kääntäjän sisäisillä funktioilla (*intrinsics*,
taito *C ja assembly yhteen*) tai jätetään kääntäjän automaattisen
vektoroinnin varaan.

## Kaksi mallia

x86-64:n SIMD-laajennukset ovat kiinteän levyisiä:

| Laajennus | Rekisterit | Leveys | 32-bittisiä kaistoja |
|-----------|------------|--------|----------------------|
| SSE2 (kaikissa x86-64-suorittimissa) | `xmm0`–`xmm15` | 128 b | 4 |
| AVX2 | `ymm0`–`ymm15` | 256 b | 8 |
| AVX-512 | `zmm0`–`zmm31` | 512 b | 16 |

Jokainen leveys on oma käskyjoukkonsa, ja ohjelman on valittava ajon
aikana, mitä suoritin tukee. RISC-V:n vektorilaajennus V on
*pituusagnostinen*: vektorirekisterin pituus (VLEN) riippuu
toteutuksesta, ja sama ohjelma toimii kaikilla pituuksilla. Käsky
`vsetvli` kertoo, montako alkiota tällä kierroksella käsitellään.

## Esimerkki: taulukon summa

Skalaariversio laskee yhden alkion kerrallaan:

```{.gnuassembler tiedosto="esimerkit/10-simd/x86.S" osa="skalaari"}
```

SSE2-versio pitää neljää osasummaa yhdessä `xmm`-rekisterissä. Silmukan
jälkeen osasummat lasketaan yhteen *horisontaalisesti*: puoliskot
vaihdetaan keskenään (`pshufd`) ja lasketaan yhteen kahdesti:

```{.gnuassembler tiedosto="esimerkit/10-simd/x86.S" osa="sse2"}
```

`movdqu` lataa 16 tavua kohdistamattomasta osoitteesta. Kohdistettu
`movdqa` kaatuu, jos osoite ei ole 16:n monikerta: sama virhe kuin
luvun 5 pinon tasauksessa. AVX2-versio tekee saman kahdeksalla
kaistalla, ja `vpaddd` voi lukea muistioperandin suoraan:

```{.gnuassembler tiedosto="esimerkit/10-simd/x86.S" osa="avx2"}
```

`vzeroupper` nollaa `ymm`-rekisterien ylemmät puoliskot ennen paluuta.
Ilman sitä myöhemmät SSE-käskyt voivat hidastua merkittävästi joillakin
suorittimilla, koska suoritin joutuu säilyttämään ylempien puoliskojen
tilan. Kääntäjä lisää käskyn automaattisesti, käsin kirjoittaessa sen
joutuu muistamaan itse.

RISC-V:n vektoriversio ei tiedä vektorin pituutta. `vsetvli t0, a1,
e32, m1` pyytää käsittelemään jäljellä olevat `a1` alkiota
32-bittisinä ja kertoo `t0`:ssa, montako niistä mahtuu yhteen
rekisteriin. Viimeinen, vajaa kierros käsitellään samalla koodilla.
Erillistä hännän käsittelyä ei tarvita:

```{.gnuassembler tiedosto="esimerkit/10-simd/rv.S" osa="rvv"}
```

Valitsin `tu` (*tail undisturbed*) säilyttää käsittelemättömät kaistat,
jolloin vajaa viimeinen kierros ei nollaa aiempia osasummia.
`vredsum.vs` laskee lopuksi kaistojen summan yhdellä käskyllä.
Esimerkki ajetaan QEMU:lla, jossa vektorilaajennus on päällä
(`QEMU_CPU=rv64,v=true,vlen=128`). Sama binääri toimisi suorittimella,
jonka VLEN on 256 tai 1024.

## Ajonaikainen tarkistus

AVX2 ei ole kaikissa x86-64-suorittimissa, ja tukemattoman käskyn
suoritus kaataa ohjelman (`SIGILL`). Pääohjelma tarkistaa tuen ennen
käyttöä:

```{.c tiedosto="esimerkit/10-simd/main.c"}
```

x86-64:llä:

```{.tuloste tiedosto="esimerkit/10-simd/odotettu-x86"}
```

RISC-V:llä:

```{.tuloste tiedosto="esimerkit/10-simd/odotettu-rv"}
```

`__builtin_cpu_supports` lukee CPUID-käskyn tiedot. Kirjastot, kuten
glibc:n `memcpy` ja `strlen`, valitsevat toteutuksen samalla tavalla
ohjelman käynnistyessä (*ifunc*). RISC-V-versio testaa myös
taulukon, jonka koko (1000) ei ole vektorin pituuden monikerta, joten
vajaa viimeinen kierros tulee testatuksi.

Kaikki versiot laskevat 32-bittisin kaistoin, joten ylivuoto kiertää
kaikissa samalla tavalla ja tulokset ovat bitilleen samat.
Liukuluvuilla näin ei olisi: osasummien eri järjestys muuttaa
pyöristystä, ja vektoroitu summa voi erota skalaarisummasta (taito
*Miten tietokone laskee*). Siksi kääntäjä vektoroi
liukulukusummia vain luvalla (`-ffast-math` tai
`-fassociative-math`).

## Automaattinen vektorointi

Kääntäjä vektoroi yksinkertaiset silmukat itse. GCC 12:sta lähtien
`-O2` tekee sen, kun hyöty on selvä, ja `-O3` aggressiivisemmin.
Valitsin `-march=x86-64-v3` sallii AVX2:n, mutta ohjelma ei silloin
toimi suorittimella, jossa sitä ei ole. `-fopt-info-vec` kertoo, mitkä
silmukat vektoroitiin ja miksi muita ei. Ennen kuin kirjoitat SIMD-koodia
käsin, katso kääntäjän tulos: usein se on jo vektoroitu.

## Käytännössä

- **Tarkista tuki ajon aikana.** Käytä AVX2:ta ja AVX-512:ta vain
  CPUID-tarkistuksen takana, tai käännä erilliset versiot ja valitse
  niistä käynnistyksessä.
- **Kirjoita skalaariviite ja vertaa.** SIMD-koodi on helppo saada
  melkein oikeaksi. Vertaa tulosta skalaariversioon, myös pituuksilla,
  jotka eivät ole vektorin pituuden monikertoja.
- **Huomioi häntä.** Kiinteän levyisellä SIMD:llä viimeiset alkiot
  käsitellään erikseen (skalaarisilmukka tai peitetty lataus).
  RISC-V:n `vsetvli` hoitaa hännän rakenteellisesti.
- **Kohdistus.** Käytä kohdistamattomia latauksia (`movdqu`,
  `vmovdqu`), ellei kohdistus ole taattu. Nykysuorittimilla
  kohdistamaton lataus kohdistetusta osoitteesta ei maksa lisää.
- **`vzeroupper` AVX-koodin lopussa.** Unohdus ei kaada mitään,
  mutta voi hidastaa kaikkea sen jälkeen ajettavaa SSE-koodia.

## Itsearviointi

- Osaat selittää SIMD:n periaatteen sekä kaistojen ja rekisterin
  leveyden suhteen.
- Osaat kirjoittaa SSE2:lla summan, joka käsittelee neljä alkiota
  kerrallaan ja laskee osasummat yhteen horisontaalisesti.
- Osaat kertoa, miten RISC-V:n pituusagnostinen vektorimalli eroaa
  x86-64:n kiinteän levyisistä laajennuksista.
- Osaat tarkistaa suorittimen tuen ajon aikana ja testata SIMD-koodin
  skalaariviitettä vastaan.
