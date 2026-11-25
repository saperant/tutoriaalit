---
title: Käännösjärjestelmät, testaus ja CI
subtitle: Pikaopas · Make, CMake, kirjastot, testit, sanitoijat, analyysi, CI ja gdb
---

# Käännöksen vaiheet

| Vaihe | Valitsin | Tuloste | Tyypillinen virhe |
|-------|----------|---------|-------------------|
| esikäsittely | `-E -P` | käännösyksikkö | otsake puuttuu |
| käännös | `-S` | `.s` | syntaksi, tyypit |
| kokoaminen | `-c` | `.o` | (harvoin) |
| linkitys | — | ohjelma | `undefined reference` |

- `nm x.o`: `T` määritelty, `U` puuttuu, `t` paikallinen.
- Kirjastot objektien jälkeen: `gcc a.o b.o -lm`.

# Make

| Merkintä | Merkitys |
|----------|----------|
| `$@` `$<` `$^` | kohde, ensimmäinen ja kaikki riippuvuudet |
| `=` `:=` | laiska, välitön sijoitus |
| `?=` `+=` | oletusarvo, lisäys |
| `%.o: %.c` | mallisääntö |
| `x: y` + pystyviiva + `hak` | järjestysriippuvuus (ei aikaleimaa) |
| `.PHONY:` | kohde ei ole tiedosto |
| `-include` | lue, jos on olemassa |

Komennot sisennetään **sarkaimella**. Muuttujat: `CC`, `CFLAGS`,
`CPPFLAGS`, `LDFLAGS`, `LDLIBS`.

```{.makefile tiedosto="esimerkit/04-make-syvemmin/Makefile" osa="saannot"}
```

```text
make -n / -B / --trace / -j$(nproc) / V=1
make CC=clang-20 CFLAGS=-O0
```

- `-MMD -MP` + `-include $(OBJEKTIT:.o=.d)` = otsakeriippuvuudet.
- Alimake aina `$(MAKE) -C hak`.

# Toistettavuus

```text
-ffile-prefix-map=$PWD=.          polut pois debug-tiedosta
SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)
ar rcsD                            arkisto ilman aikaleimoja
tar --sort=name --mtime=@0 --owner=0 --group=0
gzip -n;  LC_ALL=C TZ=UTC;  diffoscope a b
```

# CMake

```{.cmake tiedosto="esimerkit/06-cmake/CMakeLists.txt" osa="kohteet"}
```

| Näkyvyys | Kohde itse | Käyttäjät |
|----------|------------|-----------|
| `PRIVATE` | kyllä | ei |
| `INTERFACE` | ei | kyllä |
| `PUBLIC` | kyllä | kyllä |

```text
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --preset kehitys
cmake --build --preset kehitys
ctest --preset kehitys -j8 --output-on-failure
ctest -R nimi --repeat until-fail:50
find_package(ZLIB REQUIRED) + ZLIB::ZLIB
$<TARGET_FILE:kohde>        generaattorilauseke
```

- `CMAKE_EXPORT_COMPILE_COMMANDS ON` → `compile_commands.json`.
- `CMakePresets.json` versionhallintaan, `CMakeUserPresets.json` ei.
- Release määrittelee `NDEBUG`: `assert` ei tee mitään.

# Kirjastot

```text
ar rcs libx.a x.o                              staattinen
gcc -fPIC -c x.c
gcc -shared -Wl,-soname,libx.so.1 \
    -Wl,--version-script=x.map x.o -o libx.so.1.2.0
readelf -d ohjelma | grep -E 'NEEDED|RUNPATH|SONAME'
nm -D --defined-only libx.so
-Wl,-rpath,'$ORIGIN'                           haku ohjelman vierestä
pkg-config --cflags --libs [--static] x
make install PREFIX=/usr DESTDIR=/tmp/p        asennus
DESTDIR=/tmp/p cmake --install build --prefix /usr
```

- `libx.so.1.2.0` (tiedosto) ← `libx.so.1` (soname) ← `libx.so`
  (kehityspaketti).
- Yhteensopimaton muutos → uusi soname.
- `-fvisibility=hidden` tai versioskripti: vain rajapinta näkyy.
- Riippuvuudet: järjestelmä, vendorointi, `FetchContent`, Conan
  (`conan.lock`), vcpkg (`builtin-baseline`).

# Yksikkötestit

```{.c tiedosto="esimerkit/08-testit/testi.h"}
```

- Testikaksonen: sama rajapinta, eri `.c` testilinkitykseen.
- `-Wl,--wrap=f`: kutsut → `__wrap_f`, alkuperäinen `__real_f`.
- Odotetut arvot käsin; virhepolut testeiksi.

# Sanitoijat

| Lippu | Löytää | Yhdistettävissä |
|-------|--------|-----------------|
| `address` | ylivuoto, use-after-free, vuoto | `undefined` |
| `undefined` | UB: ylivuoto, siirto, kohdistus | `address` |
| `thread` | kilpatilanne | ei muiden kanssa |
| `memory` (Clang) | alustamaton luku | ei muiden kanssa |

```text
-g -fno-omit-frame-pointer -fsanitize=address,undefined
-fno-sanitize-recover=all
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
TSAN_OPTIONS=halt_on_error=1  UBSAN_OPTIONS=print_stacktrace=1
clang -g -fsanitize=fuzzer,address kohde.c     sumutus
./a.out -runs=100000 corpus/                   etsintä
./a.out crash-...                              löydöksen toisto
```

# Kattavuus

```text
gcc -O0 --coverage ...   →  .gcno (käännös), .gcda (ajo)
gcovr -r . --filter lahde/ --gcov-executable gcov-14
      --txt-metric branch   --fail-under-line 90
      --html-details kattavuus/index.html
```

- Lue puuttuvat rivit (`Missing`), älä pelkkää prosenttia.
- Rivi < haara < MC/DC (`-fcondition-coverage`).

# Staattinen analyysi

```{.yaml tiedosto="esimerkit/11-analyysi/.clang-tidy"}
```

```text
clang-tidy -p build/kehitys tiedosto.c
run-clang-tidy-20 -p build/kehitys -quiet lahde/
cppcheck --enable=warning,style --error-exitcode=1 --inline-suppr .
// NOLINT(tarkistus): syy       // cppcheck-suppress id
```

- GCC:n `-Warray-bounds` ym. vaativat optimoinnin.
- `-Werror` CI:ssä; julkaisussa `COMPILE_WARNING_AS_ERROR`.

# GitHub Actions

| Avain | Tarkoitus |
|-------|-----------|
| `on:` | laukaisevat tapahtumat |
| `permissions:` | tunnisteen oikeudet (`contents: read`) |
| `concurrency:` | vanhentuneen ajon peruutus |
| `strategy.matrix` | yhdistelmät, `exclude`, `fail-fast` |
| `needs:` | töiden järjestys |
| `timeout-minutes:` | jumiutuneen työn pysäytys |
| `actions/cache` | `key`, `restore-keys` |
| `actions/upload-artifact` | raportit, lokit, `if: failure()` |

```text
check-jsonschema --builtin-schema vendor.github-workflows ci.yml
actionlint                       lausekkeet ja run-komennot
```

# gdb eräajona

```text
gdb -batch -nx -ex 'set debuginfod enabled off' \
    -ex run -ex bt -ex 'print x' --args ./ohjelma argumentit
-ex 'thread apply all bt full'           kaikki säikeet ja muuttujat
-ex 'break 20' -ex run -ex 'watch t.n' -ex continue
rwatch / awatch                          luku / luku ja kirjoitus
gdb ./ohjelma core   ;  gdb -p PID   ;  gdb -batch -x komennot.gdb
```

- Paluuarvo 128 + n = signaali n (139 = `SIGSEGV`).
- `-O0 -g` tai `-Og` debuggaukseen; `RelWithDebInfo` = `-O2 -g`.
