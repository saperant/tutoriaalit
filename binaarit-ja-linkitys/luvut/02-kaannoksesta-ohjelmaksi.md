# Käännöksestä ohjelmaksi

Komento `gcc main.c laskin.c -o laskin` näyttää yhdeltä vaiheelta,
mutta `gcc` on *ohjain*, joka ajaa neljä ohjelmaa peräkkäin:

1. **Esikäsittelijä** (`cc1 -E`) laajentaa `#include`- ja
   `#define`-direktiivit. Tulos on yksi käännösyksikkö (*translation
   unit*): lähdetiedosto ja kaikki sen otsakkeet.
2. **Kääntäjä** (`cc1`) tuottaa käännösyksiköstä assemblyä.
3. **Kokoaja** (`as`) muuntaa assemblyn *objektitiedostoksi* (`.o`).
4. **Linkkeri** (`collect2` ja `ld`) yhdistää objektitiedostot,
   C-kirjaston ja käynnistyskoodin ohjelmaksi.

```{.dot otsikko="Lähdetiedostosta ohjelmaksi: jokainen käännösyksikkö kulkee kolme ensimmäistä vaihetta erikseen, ja linkkeri yhdistää tulokset"}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.4;
  node [shape=box, style="filled", fontsize=10];
  c [label="main.c\n+ otsakkeet", fillcolor="white"];
  i [label="main.i", fillcolor="white"];
  s [label="main.s", fillcolor="white"];
  o [label="main.o", fillcolor="#E4DCF0"];
  o2 [label="laskin.o", fillcolor="#E4DCF0"];
  lib [label="libc, crt*.o", fillcolor="#EEF1F2"];
  ohj [label="laskin", fillcolor="#F1E3CC"];
  c -> i [label="esikäsittelijä"];
  i -> s [label="kääntäjä"];
  s -> o [label="kokoaja"];
  o -> ohj [label="linkkeri"];
  o2 -> ohj; lib -> ohj;
}
```

Valitsin `-v` näyttää ohjaimen ajamat komennot, ja `-save-temps`
jättää välitulokset (`.i`, `.s`, `.o`) talteen. Rakennusjärjestelmät
erottavat vaiheet: jokainen lähdetiedosto käännetään erikseen
valitsimella `-c`, ja linkitys on oma vaiheensa. Näin muuttunut
tiedosto käännetään uudelleen yksin, ja linkitys kokoaa ohjelman
valmiista paloista.

## Kaksi lähdetiedostoa, kaksi objektitiedostoa

Esimerkissä on laskin, joka laskee tilauksen loppusumman sentteinä.
Laskentafunktio on omassa tiedostossaan, ja otsake esittelee sen
muille:

```{.c tiedosto="esimerkit/02-kaanto/laskin.h"}
```

```{.c tiedosto="esimerkit/02-kaanto/laskin.c" osa="laskin"}
```

```{.c tiedosto="esimerkit/02-kaanto/main.c"}
```

Käännös ja linkitys erikseen:

```{.bash tiedosto="esimerkit/02-kaanto/aja.sh" osa="vaiheet"}
```

Kun `main.c` käännetään, kääntäjä tietää otsakkeen ansiosta funktion
`loppusumma` tyypin mutta ei sen osoitetta. Objektitiedostoon jää
merkintä: tässä kohdassa kutsutaan symbolia `loppusumma`, jonka
osoite täytetään myöhemmin. Linkkeri löytää symbolin tiedostosta
`laskin.o` ja täyttää osoitteen. Ennen linkitystä kumpikin
objektitiedosto on keskeneräinen:

```{.tuloste tiedosto="esimerkit/02-kaanto/odotettu"}
```

`nm`:n kirjain kertoo symbolin tyypin: `T` on määritelty koodiosiossa
(*text*), `U` on määrittelemätön (*undefined*), eli sitä käytetään
mutta se määritellään muualla. Tulosteessa on kaksi yllätystä, jotka
kertovat, mitä kääntäjä teki:

- **`alenna` puuttuu.** Funktio on `static`, joten sitä ei voi kutsua
  muista tiedostoista. Optimoiva kääntäjä upotti (*inline*) sen ainoaan
  kutsukohtaansa, eikä erillistä funktiota tarvittu. Ilman
  optimointia (`-O0`) `alenna` näkyisi pienellä kirjaimella `t`.
- **`printf` on `__printf_chk`.** Ubuntu kääntää oletuksena
  valitsimella `-D_FORTIFY_SOURCE=3`, ja silloin otsake `stdio.h`
  ohjaa muotoilufunktiot versioihin, jotka tarkistavat puskurien rajat
  ajon aikana. Linkkeri näkee vain lopullisen nimen.

Symbolinimet ovat linkityksen rajapinta. Lähdekoodin nimi, tyyppi ja
otsake ovat kääntäjän asioita; linkkeri tuntee vain nimet ja niiden
osoitteet.

## Objektitiedoston tyyppi

Sekä objektitiedosto että valmis ohjelma ovat ELF-tiedostoja. Ne
erottaa *ELF-otsakkeen* kenttä `Type`:

```{.bash tiedosto="esimerkit/02-kaanto/aja.sh" osa="tyypit"}
```

Tiedostotyyppejä on neljä:

| Tyyppi | Tiedosto | Käyttö |
|--------|----------|--------|
| `REL` | `.o` | linkkerin syöte, osoitteet avoimia |
| `EXEC` | ohjelma kiinteään osoitteeseen | `-no-pie`, sulautetut |
| `DYN` | jaettu kirjasto tai PIE-ohjelma | ladataan mihin tahansa |
| `CORE` | muistivedos | kaatuneen prosessin tila |

Ubuntun GCC linkittää oletuksena paikkariippumattoman ohjelman
(*position-independent executable*, PIE), joka on tyypiltään sama
kuin jaettu kirjasto: se voidaan ladata mihin tahansa osoitteeseen.
Tämä mahdollistaa osoiteavaruuden satunnaistuksen (ASLR) myös
ohjelman omalle koodille. Valitsin `-no-pie` tuottaa tyypin `EXEC`,
jonka osoitteet on päätetty linkityksessä.

## ELF-otsake

Jokainen ELF-tiedosto alkaa 64-tavuisella otsakkeella, jonka
`readelf -h` näyttää. Sen kentät kertovat, miten tiedoston muu sisältö
tulkitaan:

| Kenttä | Esimerkkiarvo | Merkitys |
|--------|---------------|----------|
| `Magic` | `7f 45 4c 46` | tunniste: `\x7f` ja `ELF` |
| `Class` | `ELF64` | 32- vai 64-bittinen muoto |
| `Data` | little endian | tavujärjestys |
| `OS/ABI` | `UNIX - System V` | käyttöjärjestelmän ABI |
| `Type` | `REL`, `DYN` | tiedostotyyppi |
| `Machine` | `X86-64` | käskykanta |
| `Entry point` | `0x10d0` | ensimmäinen suoritettava käsky |
| `Start of program headers` | tavusiirtymä | segmenttitaulu (lataajalle) |
| `Start of section headers` | tavusiirtymä | osiotaulu (linkkerille) |

Objektitiedostossa aloitusosoite on nolla ja ohjelmaotsakkeita ei
ole, koska objektitiedostoa ei ladata sellaisenaan. Osiotaulu ja
ohjelmaotsakkeet ovat ELF:n kaksi näkymää samaan sisältöön, ja niistä
kertoo seuraava luku.

Työkalujen roolit kannattaa erottaa heti alussa:

| Työkalu | Näyttää | Tyypillinen käyttö |
|---------|---------|--------------------|
| `readelf` | ELF-rakenteet sellaisinaan | otsakkeet, osiot, dynaaminen osio |
| `objdump` | puretut käskyt, relokaatiot | `-d`, `-dr`, `-t`, `-s` |
| `nm` | symbolitaulu tiiviisti | mitä määritellään, mitä puuttuu |
| `ldd` | ajonaikaiset riippuvuudet | mistä kirjastot löytyvät |
| `file` | tiedoston tyyppi yhdellä rivillä | pikatarkistus |

`readelf` lukee vain ELF:ää eikä käytä BFD-kirjastoa, joten se näyttää
tiedoston rakenteen tarkasti. `objdump` tukee monia muotoja ja osaa
purkaa konekielen. `ldd` *ajaa* dynaamisen linkkerin, joten sitä ei
pidä käyttää epäluotettaviin tiedostoihin; turvallinen vaihtoehto on
`readelf -d`, joka vain lukee.

## Käytännössä

- **Käännä erikseen, linkitä erikseen.** Kun linkitys epäonnistuu,
  aja `nm` kullekin objektitiedostolle: virheilmoituksen symboli on
  jossakin `U`-rivinä, ja sen pitäisi olla jossakin muualla `T`-,
  `D`- tai `B`-rivinä.
- **Katso välitulokset.** `gcc -save-temps -c f.c` jättää
  esikäsitellyn tiedoston ja assemblyn talteen. Esikäsitelty tiedosto
  ratkaisee kysymykset, kuten "mikä makro tämä on" ja "mistä otsakkeesta
  tämä esittely tulee".
- **Muista oletukset.** Jakelun GCC lisää valitsimia, joita
  komentorivillä ei näy (PIE, fortify, pinon suojaus). `gcc -Q
  --help=common` ja `gcc -v` näyttävät todelliset asetukset.
- **Käytä `readelf`:iä epäluotettaviin tiedostoihin.** `ldd` voi
  suorittaa koodia; `readelf -d` ja `objdump -p` eivät.

## Itsearviointi

- Osaat nimetä käännöksen neljä vaihetta ja sen, mikä ohjelma kunkin
  tekee.
- Osaat tulkita `nm`:n tulosteen kirjaimet `T`, `t` ja `U` ja kertoa,
  miksi optimoitu `static`-funktio voi puuttua symbolitaulusta.
- Osaat erottaa tiedostotyypit `REL`, `EXEC` ja `DYN` sekä kertoa,
  miksi PIE-ohjelma on tyypiltään `DYN`.
- Osaat valita työkalun (`readelf`, `objdump`, `nm`, `ldd`)
  kysymyksen mukaan.
