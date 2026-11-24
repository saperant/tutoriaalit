#!/usr/bin/env bash
# Toistettava build: sama lähdekoodi tuottaa bitilleen saman paketin,
# joten kuka tahansa voi tarkistaa, että julkaisu vastaa lähdekoodia.
set -euo pipefail

mkdir -p src
printf 'print("hei")\n' > src/main.py
printf 'versio = "1.5.0"\n' > src/versio.py

# @alku tavallinen
tavallinen() {   # aikaleimat, omistajat ja järjestys vaihtelevat
    tar -cf - src | gzip > "$1"
}
# @loppu tavallinen

# @alku toistettava
toistettava() {
    tar --sort=name --mtime='2026-01-01 00:00:00Z' --owner=0 --group=0 \
        --numeric-owner --format=gnu -cf - src | gzip -n > "$1"
}
# @loppu toistettava

vertaa() {
    if cmp -s "$1" "$2"; then echo "sama"; else echo "eri"; fi
}

tavallinen a.tar.gz
toistettava b.tar.gz
# "Toinen build myöhemmin toisella koneella": tiedostojen ajat muuttuvat.
touch -d '2026-11-24 12:00' src/main.py src/versio.py
tavallinen c.tar.gz
toistettava d.tar.gz
echo "tavallinen build kahdesti:   $(vertaa a.tar.gz c.tar.gz)"
echo "toistettava build kahdesti:  $(vertaa b.tar.gz d.tar.gz)"
