# Virheenjäljitystieto

Konekielestä ei näe, mikä lähdekoodin rivi tuotti minkäkin käskyn,
missä paikallinen muuttuja on tai mitä tyyppiä rakenne on. Tämä tieto
on *virheenjäljitystiedossa* (*debug information*), jonka kääntäjä
tuottaa valitsimella `-g`. ELF-tiedostoissa sen muoto on *DWARF*.
Debuggeri (`gdb`), profiloijat (`perf`), kaatumisraportit ja
ABI-vertailu (`abidiff`) lukevat sitä.

Virheenjäljitystieto ei muuta konekieltä. `-O2 -g` tuottaa saman
koodin kuin `-O2`; tiedosto vain kasvaa. Siksi julkaisuversiotkin
käännetään yleensä valitsimella `-g`, ja tieto erotetaan omaan
tiedostoonsa ennen jakelua.

## DWARF-osiot

Esimerkin ohjelma kaatuu, kun sille annetaan argumentti: tyhjän jonon
alkiot ovat `NULL`.

```{.c tiedosto="esimerkit/17-virheenjaljitys/jono.c"}
```

```{.bash tiedosto="esimerkit/17-virheenjaljitys/aja.sh" osa="kaanto"}
```

DWARF jakautuu osioihin:

| Osio | Sisältö |
|------|---------|
| `.debug_info` | tyypit, muuttujat, funktiot ja niiden sijainnit (DIE-puu) |
| `.debug_abbrev` | `.debug_info`:n tietueiden rakenteet |
| `.debug_line` | osoitteesta riviksi -taulu |
| `.debug_str`, `.debug_line_str` | nimet ja polut |
| `.debug_loclists` | muuttujan sijainti osoitteen mukaan (rekisteri, pino) |
| `.debug_rnglists` | osoitealueet, kun funktio ei ole yhtenäinen |
| `.debug_aranges` | nopea haku osoitteesta käännösyksikköön |
| `.debug_frame` / `.eh_frame` | pinon purku: miten kutsuja löydetään |

`.debug_info` on puu, jonka solmut (*DIE*, *debugging information
entry*) ovat tunnisteita, kuten `DW_TAG_subprogram` (funktio),
`DW_TAG_variable` ja `DW_TAG_structure_type`, ja niiden ominaisuuksia,
kuten `DW_AT_name` ja `DW_AT_decl_line`. Skripti poimii puusta omassa
tiedostossa esitellyt funktiot ja niiden rivit.

Optimoidussa koodissa muuttujan sijainti vaihtelee: osan aikaa se on
rekisterissä, osan aikaa ei missään. Siksi debuggeri näyttää
optimoidussa ohjelmassa `<optimized out>`. `.debug_loclists`
kertoo jokaiselle osoitealueelle, missä muuttuja on.

`.eh_frame` ei ole virheenjäljitystietoa vaan osa ajonaikaista
ohjelmaa: C++:n poikkeukset ja `backtrace()` purkavat pinoa sen
avulla, eikä `strip` poista sitä.

## Osoitteesta riviksi

```{.bash tiedosto="esimerkit/17-virheenjaljitys/aja.sh" osa="kaatuminen"}
```

Paluuarvo 139 on 128 + signaalin numero 11 (`SIGSEGV`). Kaatumisesta
tiedetään tuotannossa usein vain osoite: ytimen lokirivi (`segfault
at 0 ip 000055d1c8a0a1f4 ... in jono[1f4,...]`), kaatumisraportin
pinojälki tai profiloijan näyte. `addr2line` muuntaa osoitteen
funktioksi ja riviksi. PIE-ohjelmassa annetaan osoite suhteessa
ohjelman alkuun: ytimen lokirivin hakasuluissa oleva siirtymä tai
ajonaikainen osoite, josta on vähennetty latausosoite
(`/proc/PID/maps`).

Skripti antaa funktion `viimeinen` alkuosoitteen, ja `addr2line`
kertoo, että funktion ensimmäinen käsky tulee riviltä 11, joka lukee
`j->alkiot[j->koko - 1]`. Valitsin `-i` näyttää myös upotetut funktiot,
joiden sisällä osoite on: optimoidussa koodissa yksi käsky voi kuulua
kolmeen sisäkkäiseen funktioon.

Ilman virheenjäljitystietoa saman tiedon saa `objdump -d`:llä ja
symbolitaululla, mutta vain funktion tarkkuudella. Kun symbolitaulukin
on riisuttu, jäljellä on osoite, ja se on takaisinmallinnuksen alue.

## Erillinen debug-tiedosto

Virheenjäljitystieto voi olla moninkertainen koodin kokoon nähden.
Jakelut ja tuotantoasennukset riisuvat sen ohjelmasta mutta
säilyttävät sen erillisessä tiedostossa, joka asennetaan tarvittaessa
(Debianin `-dbgsym`-paketit) tai haetaan verkosta (`debuginfod`):

```{.bash tiedosto="esimerkit/17-virheenjaljitys/aja.sh" osa="erillinen"}
```

```{.tuloste tiedosto="esimerkit/17-virheenjaljitys/odotettu"}
```

Vaiheet:

1. `objcopy --only-keep-debug` kopioi DWARF-osiot ja symbolitaulun
   omaan tiedostoonsa.
2. `strip --strip-debug --strip-unneeded` poistaa ohjelmasta
   virheenjäljitystiedon ja symbolit, joita ei tarvita ajossa.
   `.dynsym` säilyy, koska lataaja tarvitsee sen.
3. `objcopy --add-gnu-debuglink` lisää ohjelmaan osion
   `.gnu_debuglink`: debug-tiedoston nimen ja tarkistussumman.

`gdb` löytää debug-tiedoston kahdella tavalla. *Koontitunniste*
(*build ID*, osio `.note.gnu.build-id`) on linkkerin laskema tiiviste,
ja `gdb` etsii tiedostoa polusta
`/usr/lib/debug/.build-id/ab/cdef....debug`. `.gnu_debuglink`-nimeä
etsitään ohjelman hakemistosta ja sen alihakemistosta `.debug`.
Koontitunniste on luotettavampi: se yksilöi täsmälleen yhden
linkityksen tuloksen, ja `debuginfod`-palvelut hakevat tiedostot sen
perusteella.

`strip`-tasot:

| Komento | Poistaa | Jää |
|---------|---------|-----|
| `strip --strip-debug` | DWARF | `.symtab`: funktioiden nimet pinojäljissä |
| `strip --strip-unneeded` | DWARF, ajossa tarpeettomat symbolit | `.dynsym` |
| `strip` (`--strip-all`) | kaikki symbolit ja DWARF | `.dynsym` |
| `-Wl,-s` linkityksessä | sama kuin `--strip-all` | `.dynsym` |

## Koon hallinta

Suurissa C++-projekteissa virheenjäljitystieto hidastaa linkitystä.
Keinoja:

- **`-gsplit-dwarf`**: kääntäjä kirjoittaa suurimman osan tiedosta
  `.dwo`-tiedostoihin, joita linkkeri ei käsittele.
- **Pakkaus**: `-Wl,--compress-debug-sections=zlib` (tai `zstd`)
  pakkaa DWARF-osiot. Työkalut purkavat ne lukiessaan.
- **Taso**: `-g1` tuottaa vain rivitaulun ja funktiot, mikä riittää
  pinojälkiin ja profilointiin. `-g3` lisää makrojen määrittelyt.
- **Tyyppien jakaminen**: `-fdebug-types-section` (DWARF 4) ja DWARF
  5:n tyyppiyksiköt poistavat toistuvat tyyppikuvaukset.

## Käytännössä

- **Käännä julkaisut `-g`:llä ja riisu ne erikseen.** Koodi on sama,
  ja kaatumisraportit voi tulkita jälkikäteen. Säilytä debug-tiedostot
  koontitunnisteen mukaan, esimerkiksi omalla `debuginfod`-palvelimella.
- **Tulkitse osoitteet `addr2line -f -i -e`:llä**, ja muista
  vähentää PIE-ohjelman latausosoite.
- **Käytä `-Og`:tä kehityksessä.** Se optimoi, mutta pitää muuttujat
  debuggerin nähtävillä paremmin kuin `-O2`.
- **Tarkista riisuminen.** `readelf -S ohjelma | grep debug` ei saa
  näyttää mitään jaetussa paketissa, ja `readelf -n` näyttää
  koontitunnisteen.

## Itsearviointi

- Osaat kertoa, mitä DWARF-osiot sisältävät, ja etsiä
  `readelf --debug-dump`:lla funktion esittelyrivin.
- Osaat muuntaa kaatumisosoitteen funktioksi ja riviksi
  `addr2line`:lla, myös PIE-ohjelmassa.
- Osaat erottaa virheenjäljitystiedon omaan tiedostoonsa ja liittää
  sen ohjelmaan `.gnu_debuglink`:llä.
- Osaat valita sopivan `strip`-tason ja kertoa, mitä kukin jättää.
- Osaat selittää, miksi `-g` ei muuta tuotettua koodia.
