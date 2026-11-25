#!/bin/sh
# Buildroot- ja Yocto-asetuksia ei ajeta testeissä (rakennus kestää
# tunteja), mutta niiden viittaukset tarkistetaan: lisenssin
# tarkistussumma ja lähteet.
set -eu
cd "$(dirname "$0")"
resepti=meta-tutoriaali/recipes-core/minit/minit_1.0.bb
odotettu=$(sed -n 's/^md5=\([0-9a-f]*\)"$/\1/p' "$resepti")
laskettu=$(sed -n 1,4p ../07-palvelut/minit.c | md5sum | cut -c1-32)
if [ "$odotettu" = "$laskettu" ]; then
    echo "yocto: LIC_FILES_CHKSUM vastaa minit.c:n riveja 1-4"
else
    echo "yocto: LIC_FILES_CHKSUM $odotettu, laskettu $laskettu"
fi
for tiedosto in minit.c palvelu.c palvelut.conf; do
    if [ -f "../07-palvelut/$tiedosto" ]; then
        echo "buildroot ja yocto: $tiedosto loytyy"
    fi
done
grep -c 'BR2_EXTERNAL_TUT_PATH' external/*.mk external/Config.in \
    tutoriaali_defconfig | sed 's/^/BR2_EXTERNAL_TUT_PATH: /'
