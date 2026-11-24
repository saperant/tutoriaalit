#!/usr/bin/env bash
# XOR-salattujen merkkijonojen purku staattisesti ja dynaamisesti.
source ./yhteinen.sh

python3 salaa.py > uusi.h
if ! cmp -s uusi.h salaisuudet.h; then
    echo "salaisuudet.h on vanhentunut: aja python3 salaa.py > salaisuudet.h"
    exit 1
fi
"$CC" -std=c23 -O2 -Wall -Wextra -Werror palvelu.c -o palvelu
./palvelu
otsikko "strings ei löydä osoitteita"
strings -n 6 palvelu | grep -cE 'example|/api/' || true
otsikko "purkufunktio"
purku palvelu pura
otsikko "staattinen purku"
# @alku staattinen
python3 pura_xor.py palvelu pura
# @loppu staattinen
otsikko "dynaaminen purku: __printf_chk-kutsun argumentti"
# @alku dynaaminen
gdb_era printf.gdb ./palvelu
# @loppu dynaaminen
