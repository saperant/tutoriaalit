---
title: Objektitiedostot, linkitys ja ABI
subtitle: Pikaopas · ELF, GNU binutils ja glibc:n ld.so · Linux x86-64
---

# Tutkiminen

| Kysymys | Komento |
|---------|---------|
| tiedoston tyyppi, kone | `readelf -h f`, `file f` |
| osiot | `readelf -SW f` |
| segmentit ja osioiden sijoittuminen | `readelf -lW f` |
| symbolit | `nm f`, `nm -C f`, `readelf -sW f` |
| puuttuvat / määritellyt | `nm -u f.o`, `nm --defined-only f.o` |
| kirjaston rajapinta | `nm -D --defined-only libx.so` |
| relokaatiot | `readelf -rW f.o`, `objdump -dr f.o` |
| konekieli | `objdump -d --no-show-raw-insn f` |
| riippuvuudet, soname, RUNPATH, liput | `readelf -d f` |
| symboliversiot | `readelf -V f`, `objdump -T f` |
| arkiston jäsenet | `ar t liba.a`, `nm -A liba.a` |
| ajonaikainen haku | `ldd f` (ajaa lataajan), `LD_DEBUG=libs ./f` |
| sidonnat | `LD_DEBUG=bindings ./f` |
| koot | `size f`, `nm -S --size-sort f` |
| osoite riviksi | `addr2line -f -i -e f 0x1234` |

# nm:n kirjaimet

| Kirjain | Merkitys | Kirjain | Merkitys |
|---------|----------|---------|----------|
| `T` `t` | koodi | `U` | määrittelemätön |
| `D` `d` | alustettu data | `W` `w` | heikko funktio |
| `B` `b` | nollattu data | `V` `v` | heikko objekti |
| `R` `r` | vain luettava | `A` | absoluuttinen |
| `C` | yhteinen (`-fcommon`) | `i` | IFUNC |

Iso kirjain on globaali, pieni paikallinen.

# Osiot

| Osio | Sisältö | Segmentti |
|------|---------|-----------|
| `.text` | koodi | `R E` |
| `.rodata` | vakiot | `R` |
| `.data` | alustetut muuttujat | `RW` |
| `.bss` | nollatut muuttujat, ei tilaa tiedostossa | `RW` |
| `.init_array` `.fini_array` | konstruktorit, destruktorit | `RW`, RELRO |
| `.got` `.plt` | ulkoisten symbolien osoitteet ja hypyt | `RW` / `R E` |
| `.dynsym` `.dynamic` | lataajan tiedot | `R` / `RW` |
| `.symtab` `.debug_*` | symbolit, DWARF | ei ladata, `strip` poistaa |

# Linkitys

| Tarkoitus | Valitsin |
|-----------|----------|
| arkisto | `ar rcs libx.a a.o b.o`, kirjasto objektien jälkeen |
| keskenään riippuvat arkistot | `-Wl,--start-group -la -lb -Wl,--end-group` |
| kaikki jäsenet | `-Wl,--whole-archive -lx -Wl,--no-whole-archive` |
| jaettu kirjasto | `-fPIC -shared -Wl,-soname,libx.so.1` |
| hakupolku ohjelmaan | `-Wl,-rpath,'$ORIGIN/../lib'` |
| kaikki viittaukset ratkaistava | `-Wl,-z,defs` |
| välitön sidonta, RELRO | `-Wl,-z,now -Wl,-z,relro` |
| linkkerikartta | `-Wl,-Map=f.map`, `-Wl,--print-memory-usage` |
| käyttämättömän poisto | `-ffunction-sections -fdata-sections -Wl,--gc-sections` |
| versioskripti | `-Wl,--version-script=x.map` |
| linkkeriskripti / lisäys | `-Wl,-T,f.ld` |
| käännösaikainen kääre | `-Wl,--wrap=f` (`__wrap_f`, `__real_f`) |
| ohjelman symbolit liitännäisille | `-rdynamic` |

# Lataajan hakujärjestys

1. `DT_RPATH` (vain jos `DT_RUNPATH` puuttuu)
2. `LD_LIBRARY_PATH` (ei setuid-ohjelmissa)
3. `DT_RUNPATH` (vain tiedoston omat riippuvuudet)
4. `/etc/ld.so.cache` (`ldconfig`)
5. `/lib`, `/usr/lib`

Symbolin sidonta: `LD_PRELOAD`, ohjelma, `NEEDED`-kirjastot
leveyssuuntaisesti. Ensimmäinen määrittely voittaa.

# Attribuutit

| Attribuutti | Vaikutus |
|-------------|----------|
| `static` | paikallinen symboli |
| `__attribute__((weak))` | korvattava oletus, tai heikko viittaus (arvo 0) |
| `__attribute__((visibility("hidden")))` | ei näy kirjaston ulkopuolelle |
| `__attribute__((visibility("default")))` | vienti `-fvisibility=hidden`:n kanssa |
| `__attribute__((section("nimi"), used))` | omaan osioon, `__start_nimi`, `__stop_nimi` |
| `__attribute__((constructor(101)))` | ajetaan ennen `main`:ia, pienin ensin |
| `__attribute__((destructor))` | ajetaan `exit`:ssä |
| `__attribute__((symver("f@@V_2")))` | symbolin versio, `@@` on oletus |
| `extern "C"` | C-nimi C++:ssa |

Rekisteri omaan osioon:

```{.c tiedosto="esimerkit/11-osiorekisteri/komento.h" osa="makro"}
```

Versioskripti kahdelle versiolle:

```{.text tiedosto="esimerkit/09-versiointi/tunnus-v2.map" osa="kartta"}
```

# ABI

| Asia | Linux x86-64 |
|------|--------------|
| koot | `int` 4, `long` 8, osoitin 8, `long double` 16 |
| tasaus | tyypin koko (enintään 16), rakenne = suurin kenttä |
| kentät | kirjoitusjärjestyksessä, täyte tasaukseen |
| tarkistus | `_Static_assert(sizeof(struct s) == 16, "...")` |
| C++-nimet | Itanium-koristelu, `c++filt`, `nm -C` |
| ABI-rikko | kentän lisäys/siirto, tyypin muutos, poisto, `enum`-arvot |
| soname | `libx.so.PÄÄ`; vaihtuu, kun ABI rikkoutuu |

# Virheenjäljitys

```text
gcc -O2 -g ...                                     # sama koodi, DWARF mukaan
objcopy --only-keep-debug f f.debug
strip --strip-debug --strip-unneeded f
objcopy --add-gnu-debuglink=f.debug f
readelf -n f                                       # koontitunniste
readelf --debug-dump=info f | grep DW_AT_name
```

# Vianetsintä

| Ilmoitus | Syy |
|----------|-----|
| `undefined reference` | kirjasto puuttuu, järjestys, `extern "C"` |
| `multiple definition` | määrittely otsakkeessa, `-fno-common` |
| `cannot open shared object file` | hakupolku: `ldd`, `LD_DEBUG=libs` |
| `version 'GLIBC_x' not found` | linkitetty uudempaa glibc:tä vasten |
| `recompile with -fPIC` | ei-PIC-objekti jaetussa kirjastossa |
| `relocation truncated to fit` | etäisyys yli 2 Gt, `-mcmodel` |
| `No such file or directory` (tiedosto on) | `INTERP`-polku puuttuu |
| väärät arvot päivityksen jälkeen | ABI muuttui, soname ei |
