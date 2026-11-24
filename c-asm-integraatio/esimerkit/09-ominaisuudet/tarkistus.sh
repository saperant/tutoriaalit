#!/usr/bin/env bash
# Molemmat polut testiin: sama ohjelma QEMU:ssa kahdella emuloidulla
# prosessorimallilla, joista vain uudemmassa on AVX2 (noTSX: ilman
# transaktiomuistia, jota QEMU ei emuloi).
set -euo pipefail
# @alku mallit
for malli in Nehalem Haswell-noTSX; do
    echo "qemu-x86_64 -cpu $malli:"
    NAYTA_AVX2=1 qemu-x86_64 -cpu "$malli" "$RAK/x86" | sed 's/^/  /'
done
# @loppu mallit
