#!/usr/bin/env bash
# gdb eräajona: kaatumiskohdan pinolistaus ja vahtipiste. Tulosteesta
# poistetaan osoitteet ja ympäristön ilmoitukset, jotka vaihtelevat.
set -euo pipefail
$CC -g -O0 -o kaatuu kaatuu.c
$CC -g -O0 -o vahti vahti.c

# @alku gdb
# gdb ilman käyttäjän asetuksia ja verkosta haettavia symboleja.
gdb_era() {
    gdb -batch -nx -ex 'set debuginfod enabled off' "$@" 2>&1
}
# @loppu gdb
# @alku siisti
# Osoitteet, säiekirjaston ilmoitukset ja tyhjät rivit pois.
siisti() {
    grep -vE 'libthread_db|^warning: Error disabling|^$' \
        | sed -E 's/^(#[0-9]+ +)0x[0-9a-f]+ in /\1/;
                  s/ at 0x[0-9a-f]+: / at /; s/0x[0-9a-f]{5,}/0x.../g;
                  s/^Hardware w/W/' | expand -t 8
}
# @loppu siisti

# @alku kaatuminen
echo "== kaatuminen"
# Kuoren oma kaatumisilmoitus sisältää prosessinumeron: se ohjataan pois.
sh -c './kaatuu > /dev/null' 2> /dev/null || echo "paluuarvo $?"
gdb_era -ex run -ex bt -ex 'print nimi' -ex 'print hae(nimi)' \
    ./kaatuu | siisti
# @loppu kaatuminen

# @alku vahtipiste
echo "== vahtipiste"
./vahti
gdb_era -ex 'break 20' -ex run -ex 'watch t.laskuri' -ex continue \
    -ex bt -ex 'print i' -ex 'print t->nimi' ./vahti | siisti
# @loppu vahtipiste
