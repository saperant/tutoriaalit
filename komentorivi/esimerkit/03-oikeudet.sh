#!/usr/bin/env bash
# Oikeuksien lukeminen ja muuttaminen.
set -euo pipefail
export LC_ALL=C
umask 022

# @alku luonti
touch raportti.txt
mkdir julkaisu
printf '#!/bin/sh\necho "julkaistaan"\n' > julkaise.sh
stat -c '%a %A %n' raportti.txt julkaisu julkaise.sh
# @loppu luonti

# @alku muutos
chmod u+x julkaise.sh          # omistaja saa suorittaa
chmod go-r raportti.txt        # muut eivät saa lukea
chmod 750 julkaisu             # rwx omistajalle, r-x ryhmälle
stat -c '%a %A %n' raportti.txt julkaisu julkaise.sh
./julkaise.sh
# @loppu muutos
