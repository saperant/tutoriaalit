#!/usr/bin/env bash
# set -e ei laukea ehdon sisällä: jos funktiota kutsutaan if-, &&- tai
# ||-yhteydessä, sen sisällä epäonnistuvat komennot eivät pysäytä sitä.
set -euo pipefail

# @alku ansa
kopioi_ja_ilmoita() {
    cp puuttuva.txt kopio.txt 2> /dev/null     # epäonnistuu
    echo "kopioitu"                           # ...mutta tämä ajetaan
}

if kopioi_ja_ilmoita; then
    echo "funktio palautti onnistumisen"
fi
# @loppu ansa

# @alku korjaus
kopioi_varmasti() {
    cp puuttuva.txt kopio.txt 2> /dev/null || return
    echo "kopioitu"
}

if ! kopioi_varmasti; then
    echo "kopiointi epäonnistui"
fi
# @loppu korjaus
