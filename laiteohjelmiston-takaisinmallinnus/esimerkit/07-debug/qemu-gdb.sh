#!/bin/sh
# Käynnistää laitteen QEMU:ssa pysäytettynä (-S) gdb-palvelimena, joka
# puhuu vakiosyötteen ja -tulosteen kautta (-gdb stdio). Sarjaportti
# on pois käytöstä, koska vakiotuloste on varattu gdb:n protokollalle.
exec qemu-system-arm -M mps2-an385 -nographic -monitor none \
    -serial none -semihosting-config enable=on,target=native \
    -icount shift=3,align=off,sleep=off \
    -device loader,file="$1",addr=0 -S -gdb stdio 2>/dev/null
