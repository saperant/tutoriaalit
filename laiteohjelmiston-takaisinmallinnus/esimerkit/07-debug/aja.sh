#!/usr/bin/env bash
# Debug-rajapinnat: sarjakonsoli, gdb QEMU:n gdb-palvelimen kautta ja
# oman laitteen debug-lukituksen tila.
source ./yhteinen.sh

otsikko "sarjakonsoli"
# @alku konsoli
printf 'ohje\nversio\ntila\nsammuta\n' | qemu "$LAITE/flash.bin"
# @loppu konsoli
otsikko "gdb-istunto ilman symboleita"
# @alku gdb
timeout 60 gdb-multiarch -q -batch -nx -x istunto.gdb 2>&1 |
    sed -e '/^warning: No executable/d' -e '/^determining executable/d' \
        -e '/^\[Inferior/d' -e '/^Remote communication/d' | expand
# @loppu gdb
otsikko "asetuslohko: debug-lukituksen kenttä"
# @alku lukitus
python3 sanat.py "$LAITE/flash.bin" 0x3f014 0x3f024
# @loppu lukitus
