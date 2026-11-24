# Relokaatiot

Kun kääntäjä tuottaa objektitiedoston, se ei tiedä, mihin osoitteeseen
koodi lopulta sijoittuu eikä missä muiden tiedostojen funktiot ja
muuttujat ovat. Jokaiseen tällaiseen kohtaan se jättää paikan ja
*relokaation*: ohjeen linkkerille siitä, mikä arvo paikkaan
kirjoitetaan. Relokaatiot ovat osioissa `.rela.text`, `.rela.data`
ja niin edelleen, yksi relokaatio-osio kutakin muutettavaa osiota
kohti.

Relokaatiossa on neljä tietoa:

| Kenttä | Merkitys | Esimerkki |
|--------|----------|-----------|
| siirtymä (*offset*) | paikka osiossa, johon kirjoitetaan | `0x0e` |
| tyyppi | miten arvo lasketaan ja montako tavua | `R_X86_64_PC32` |
| symboli | kenen osoitetta tarvitaan | `saldo` |
| lisäys (*addend*) | vakio, joka lisätään | `-4` |

## Paikat ennen linkitystä

Esimerkin funktio `tilaa` kutsuu toisessa tiedostossa määriteltyä
funktiota ja lukee toisessa tiedostossa määriteltyä muuttujaa:

```{.c tiedosto="esimerkit/04-relokaatiot/varasto.c" osa="varasto"}
```

```{.c tiedosto="esimerkit/04-relokaatiot/main.c" osa="main"}
```

`objdump -dr` purkaa konekielen ja näyttää relokaatiot niiden
kohdalla. Skripti poistaa tulosteesta osoitteet ja tavut ja korvaa
linkityksen jälkeen vaihtelevat siirtymät merkinnällä `SIIRTYMA`:

```{.bash tiedosto="esimerkit/04-relokaatiot/aja.sh" osa="ennen"}
```

```{.bash tiedosto="esimerkit/04-relokaatiot/aja.sh" osa="relokaatiot"}
```

```{.bash tiedosto="esimerkit/04-relokaatiot/aja.sh" osa="jalkeen"}
```

```{.tuloste tiedosto="esimerkit/04-relokaatiot/odotettu"}
```

Ennen linkitystä `call`-käskyn kohde on nolla. `objdump` tulkitsee
nollasiirtymän seuraavaksi käskyksi (`<tilaa+0x12>`), mikä on
merkki täyttämättömästä paikasta. Samoin `add 0x0(%rip),%eax` lukee
"jostain", ja relokaatio kertoo, mistä. Linkityksen jälkeen kutsu
osoittaa funktioon `lisaa` ja lukuoperaatio muuttujaan `saldo`.

## Miten arvo lasketaan

x86-64:n `call`- ja `rip`-suhteelliset käskyt sisältävät 32-bittisen
etäisyyden *seuraavan* käskyn alusta kohteeseen. Relokaatio
`R_X86_64_PC32` laskee arvon kaavalla `S + A - P`:

- `S` on symbolin lopullinen osoite,
- `A` on lisäys (tässä `-4`),
- `P` on paikan oma osoite.

Paikka on käskyn neljä viimeistä tavua, joten seuraava käsky alkaa
osoitteesta `P + 4`. Lisäys `-4` korjaa tämän: `S - 4 - P = S - (P +
4)`, eli etäisyys seuraavan käskyn alusta. Jos käskyn perässä olisi
välitön arvo, lisäys olisi suurempi negatiivinen luku.

Yleisimmät x86-64:n relokaatiotyypit:

| Tyyppi | Arvo | Käyttö |
|--------|------|--------|
| `R_X86_64_64` | `S + A` | 64-bittinen osoite datassa |
| `R_X86_64_PC32` | `S + A - P` | `rip`-suhteellinen data |
| `R_X86_64_PLT32` | `L + A - P` | funktiokutsu, `L` on PLT-merkintä tai funktio |
| `R_X86_64_GOTPCRELX` | `G + GOT + A - P` | osoite GOT-taulusta (luku 8) |
| `R_X86_64_REX_GOTPCRELX` | sama, REX-etuliite | 64-bittinen lataus GOT:sta |
| `R_X86_64_32S` | `S + A` | 32-bittinen osoite, ei PIE:ssä |
| `R_X86_64_RELATIVE` | `B + A` | ajonaikainen, `B` on latausosoite |
| `R_X86_64_GLOB_DAT` | `S` | ajonaikainen GOT-merkintä |
| `R_X86_64_JUMP_SLOT` | `S` | ajonaikainen PLT-paikka |

Funktiokutsu käyttää tyyppiä `PLT32`, vaikka kohde on samassa
ohjelmassa. Jos funktio on jaetussa kirjastossa, linkkeri ohjaa
kutsun PLT-merkintään (luku 8); jos se on ohjelmassa, linkkeri
käyttää suoraa osoitetta. Kääntäjän ei tarvitse tietää, kumpi
tapahtuu.

Muuttujaa `saldo` luetaan suoraan `rip`-suhteellisesti (`PC32`),
vaikka se on toisessa tiedostossa. Ubuntun GCC kääntää ohjelmat
oletuksena valitsimella `-fPIE`, joka olettaa, että ulkoiset muuttujat
ovat samassa ohjelmassa. Jaetun kirjaston koodi (`-fPIC`) ei voi
olettaa sitä, ja se lukee muuttujan osoitteen GOT-taulusta.

## Relokaatiot, jotka jäävät ajoon

Linkkeri ratkaisee kaikki relokaatiot, joiden arvon se tietää.
Ohjelmaan ja jaettuun kirjastoon jää kaksi lajia *dynaamisia
relokaatioita*, jotka lataaja tekee käynnistyksessä
(`readelf -r ohjelma`):

- **`R_X86_64_RELATIVE`**: osoite, joka riippuu latausosoitteesta.
  PIE-ohjelmassa jokainen osoitintaulukon alkio, kuten `const char
  *nimet[] = {"a", "b"};`, tarvitsee oman relokaationsa, koska
  merkkijonojen osoitteet tiedetään vasta, kun ohjelma on ladattu.
- **`GLOB_DAT` ja `JUMP_SLOT`**: jaetun kirjaston symbolien osoitteet
  GOT-tauluun.

Suuret osoitintaulukot hidastavat käynnistystä ja estävät sivujen
jakamisen prosessien kesken, koska taulukon sivut kirjoitetaan.
Vaihtoehto on taulukko, jossa on siirtymiä tai indeksejä osoittimien
sijaan; linkkerin valitsin `-z pack-relative-relocs` (DT_RELR)
pakkaa `RELATIVE`-relokaatiot tiiviiksi bittikartaksi.

## Relokaatiovirheet

Relokaation arvon on mahduttava paikkaansa. Kun se ei mahdu, linkkeri
ilmoittaa esimerkiksi `relocation truncated to fit: R_X86_64_PC32`.
Tavallisimmat syyt:

- **Yli 2 gigatavun data tai koodi.** 32-bittinen etäisyys ei riitä.
  Ratkaisu on muistimalli `-mcmodel=medium` (suuret taulukot omiin
  osioihinsa) tai suurten taulukoiden varaaminen ajon aikana.
- **Ei-PIC-objekti jaetussa kirjastossa.** `relocation R_X86_64_32
  against '.rodata' can not be used when making a shared object;
  recompile with -fPIC`. Kirjastoon linkitettävät objektit (myös
  staattisten kirjastojen sisältö) on käännettävä valitsimella
  `-fPIC`.

## Käytännössä

- **Lue `objdump -dr`, kun epäilet linkitystä.** Relokaatiot
  kertovat, mihin symboleihin koodi todella viittaa, myös silloin,
  kun makrot ja otsakkeet hämärtävät sen lähdekoodissa.
- **Käännä kirjastoihin menevät objektit `-fPIC`:llä**, myös
  staattiset arkistot, jos ne voidaan myöhemmin linkittää jaettuun
  kirjastoon. CMake tekee tämän asetuksella
  `POSITION_INDEPENDENT_CODE`.
- **Vältä suuria osoitintaulukoita PIE-ohjelmissa.** Ne vaativat
  ajonaikaisia relokaatioita ja kirjoitettavia sivuja. Merkkijonojen
  siirtymätaulukko on yhtä nopea ja pysyy `.rodata`-osiossa.

## Itsearviointi

- Osaat kertoa, miksi objektitiedostossa on relokaatioita ja mitä
  relokaation neljä kenttää tarkoittavat.
- Osaat laskea `R_X86_64_PC32`-relokaation arvon ja selittää
  lisäyksen `-4`.
- Osaat lukea `objdump -dr`:n tulosteen ja tunnistaa
  täyttämättömän kutsun ja datan lukemisen.
- Osaat erottaa linkityksessä ratkaistavat ja ajoon jäävät
  relokaatiot ja selittää, miksi PIE tarvitsee `RELATIVE`-relokaatioita.
