#!/usr/bin/env bash
# umask määrää uusien tiedostojen oletusoikeudet.
set -euo pipefail
export LC_ALL=C

# @alku umask
for maski in 022 027 077; do
    umask "$maski"
    touch "tiedosto-$maski"
    mkdir "hakemisto-$maski"
    stat -c "umask $maski: %a %n" "tiedosto-$maski" "hakemisto-$maski"
done
umask 027
umask -S
# @loppu umask
