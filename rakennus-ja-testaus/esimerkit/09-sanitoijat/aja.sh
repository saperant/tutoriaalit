#!/usr/bin/env bash
# Sama ohjelma ilman sanitoijaa ja sen kanssa sekä sumutus. Tulosteesta
# jätetään osoitteet ja prosessinumerot pois, jotta se on sama joka
# ajolla.
set -euo pipefail
# @alku siisti
siisti() {
    sed -E 's/==[0-9]+==//; s/ on address 0x[0-9a-f]+.*//;
            s/ at 0x[0-9a-f]+.*//; s/^0x[0-9a-f]+ (is located)/\1/;
            s/ \[0x.*//; s/#([0-9]+) 0x[0-9a-f]+ in /#\1 /;
            s/ \(.*\+0x[0-9a-f]+\).*//; s/ \(pid=[0-9]+\)//;
            s|/[^ ]*/||g; s/: runtime error: /:\n  runtime error: /;
            s/ cannot be represented/\n  cannot be represented/'
}
# @loppu siisti

# @alku asan
echo "== ylivuoto.c, -fsanitize=address"
$CC -g -fsanitize=address ylivuoto.c -o ylivuoto
./ylivuoto 2>&1 \
    | grep -E 'ERROR:|WRITE|#[0-9].*ylivuoto\.c|located|allocated' \
    | siisti || true
# @loppu asan

# @alku ubsan
echo "== summa.c ilman sanitoijaa: väärä tulos, ei virhettä"
$CC -g summa.c -o summa && ./summa
echo "== summa.c, -fsanitize=undefined"
$CC -g -fsanitize=undefined -fno-sanitize-recover=all summa.c -o summa
./summa 2>&1 | siisti || true
# @loppu ubsan

# @alku tsan
echo "== kilpa.c, -fsanitize=thread"
$CC -g -fsanitize=thread kilpa.c -o kilpa
TSAN_OPTIONS=halt_on_error=1 ./kilpa 2>&1 \
    | grep -E 'WARNING:|Location|SUMMARY' | siisti || true
# @loppu tsan

# @alku sumutus
echo "== sumutus.c, -fsanitize=fuzzer,address (Clang)"
clang-20 -std=c23 -g -fsanitize=fuzzer,address sumutus.c -o sumutus
# Kiinteä siemen ja ajojen yläraja: ajo on toistettava ja päättyy aina.
./sumutus -seed=1 -max_len=32 -runs=1000000 2>&1 \
    | grep -E 'ERROR:|^WRITE' | siisti || true
echo "löydöksiä tallennettu: $(find . -name 'crash-*' | wc -l)"
echo "== löydöksen syöte uudelleen: virhe toistuu"
./sumutus crash-* 2>&1 | grep -E 'ERROR:' | siisti || true
# @loppu sumutus
