#!/usr/bin/env bash
# Rivikattavuus gcov-instrumentoinnilla ja gcovr-raportilla.
set -euo pipefail
gcov=$(command -v gcov-14 || command -v gcov)

# @alku kattavuus
# kattavuus [LIPUT]: käännä --coverage-valitsimella, aja testit ja
# raportoi lahde/-hakemiston rivikattavuus.
kattavuus() {
    rm -rf mittaus && mkdir mittaus
    $CC -std=c17 -O0 --coverage "$@" -Ilahde lahde/tilasto.c testit.c \
        -lm -o mittaus/testit
    (cd mittaus && ./testit)
    gcovr --gcov-executable "$gcov" -r . --filter lahde/ \
        --object-directory mittaus --txt - 2> /dev/null \
        | grep -E '^(File|lahde|TOTAL)'
}

echo "== ensimmäiset testit"
kattavuus
# @loppu kattavuus
# @alku gcov
echo "== gcov: suorituskerrat riveittäin, ##### = ei suoritettu"
"$gcov" -o mittaus/testit-tilasto lahde/tilasto.c > /dev/null
grep -B2 -A1 '#####' tilasto.c.gcov
# @loppu gcov
# @alku kattavat
echo "== puuttuvat tapaukset lisätty"
kattavuus -DKATTAVAT
# @loppu kattavat
