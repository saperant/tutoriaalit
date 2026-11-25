#!/usr/bin/env bash
# Ensimmäinen istunto: mitä täällä on ja miten liikun.
set -euo pipefail
export LC_ALL=C

# Aineisto, jota istunnossa tutkitaan.
mkdir -p projekti/lahde projekti/dokumentit
printf 'Ostoslista\n- kahvia\n- maitoa\n' > projekti/muistio.txt
touch projekti/lahde/paa.c projekti/dokumentit/ohje.md

# @alku liikkuminen
cd projekti
ls
ls -F
cat muistio.txt
cd lahde
ls
cd ..
# @loppu liikkuminen
