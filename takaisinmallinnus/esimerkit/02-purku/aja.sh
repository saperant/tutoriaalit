#!/usr/bin/env bash
# Lineaarinen ja rekursiivinen purku, radare2:n analyysikomennot.
source ./yhteinen.sh

"$CC" -std=c17 -O1 -Wall -Werror testi.c sekaannus.S -o sekaannus
./sekaannus
otsikko "objdump: lineaarinen purku"
# @alku lineaarinen
purku sekaannus tarkista
# @loppu lineaarinen
otsikko "radare2: rekursiivinen purku"
# @alku rekursiivinen
r2 sekaannus 'aaa; pdf @ sym.tarkista'
# @loppu rekursiivinen

"$CC" -std=c17 -O0 -Wall -Wextra -Werror varasto.c -o varasto
./varasto
otsikko "funktiot (afl): lohkoja, koko, nimi"
# @alku afl
r2 varasto 'aaa; afl' | awk '$NF ~ /^(sym\.(etsi|ota|raportoi)|main)$/ {
    print $2, $3, $NF }'
# @loppu afl
otsikko "merkkijonot (iz)"
# @alku iz
r2 varasto 'iz' | awk 'NR > 3 { $1 = $2 = $3 = ""; print substr($0, 4) }'
# @loppu iz
otsikko "ristiviittaukset (axt)"
# @alku axt
r2 varasto 'aaa; axt @ str.TILAA:__s__saldo__d__n; axt @ sym.etsi;
    axt @ obj.varasto'
# @loppu axt
otsikko "pseudokoodi (pdc), alku"
# @alku pdc
r2 varasto 'aaa; pdc @ sym.etsi' | head -14
# @loppu pdc
