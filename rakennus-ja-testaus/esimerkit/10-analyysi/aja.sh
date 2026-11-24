#!/usr/bin/env bash
# Kääntäjän varoitukset, clang-tidy ja cppcheck samaan tiedostoon.
# Tulosteesta näytetään tiedosto, rivi ja tarkistuksen nimi.
set -euo pipefail
tidy=$(command -v clang-tidy-20 || command -v clang-tidy)
lyhenna() {
    sed -E 's|^.*/||; s/^([^:]+:[0-9]+):[0-9]+:.*\[([^],]*).*\]$/\1: \2/'
}

# analysoi TIEDOSTO: kolme työkalua peräkkäin.
analysoi() {
    echo "-- kääntäjä: -Wall -Wextra -O2"
    $CC -std=c17 -Wall -Wextra -O2 -c "$1" -o /dev/null 2>&1 \
        | grep 'warning:' | lyhenna || true
    echo "-- clang-tidy (.clang-tidy)"
    "$tidy" "$1" -- -std=c17 2> /dev/null | grep -E 'warning:|error:' \
        | lyhenna || true
    echo "-- cppcheck"
    cppcheck --enable=warning,style --quiet --error-exitcode=0 \
        --template='{file}:{line}: {id}' "$1" 2>&1 || true
}

# @alku ajo
echo "== asetus.c"
analysoi asetus.c
echo "== korjattu.c"
analysoi korjattu.c
# @loppu ajo
