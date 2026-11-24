#!/usr/bin/env bash
# Konflikti: sama rivi muuttui molemmissa haaroissa.
set -euo pipefail
# @alku vakiot
# Esimerkkien vakioympäristö: ei käyttäjän omia asetuksia, kiinteä
# tekijä ja kello, joten commit-tunnisteet ovat joka ajolla samat.
export LC_ALL=C.UTF-8 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME="Aino Kehittäjä" GIT_AUTHOR_EMAIL=aino@example.fi
export GIT_COMMITTER_NAME=$GIT_AUTHOR_NAME
export GIT_COMMITTER_EMAIL=$GIT_AUTHOR_EMAIL
kello=1767261600              # 1.1.2026 klo 12.00 Suomen aikaa
aika() {                      # kello etenee minuutin
    kello=$((kello + 60))
    export GIT_AUTHOR_DATE="$kello +0200" GIT_COMMITTER_DATE="$kello +0200"
}
tallenna() { aika; git commit -q "$@"; }   # commit, kello etenee
aika
# @loppu vakiot

git init -q -b main palvelu
cd palvelu
printf 'portti = 8080\naikakatkaisu = 30\n' > asetukset.ini
git add . && tallenna -m "Asetukset"
git switch -q -c tuotanto
sed -i 's/8080/80/' asetukset.ini
git add . && tallenna -m "Tuotannon portti"
git switch -q main
sed -i 's/8080/8000/' asetukset.ini
git add . && tallenna -m "Kehityksen portti"

# @alku konflikti
aika
if ! git merge -q tuotanto > /dev/null; then
    echo "yhdistäminen pysähtyi konfliktiin"
fi
git status --short            # UU = molemmat muuttivat
cat asetukset.ini
# @loppu konflikti
# @alku ratkaisu
# Ratkaisu on päätös: portti tulee ympäristömuuttujasta.
printf 'portti = %s\naikakatkaisu = 30\n' "\${PORTTI}" > asetukset.ini
git add asetukset.ini         # merkitsee konfliktin ratkaistuksi
git commit -q --no-edit
git log --oneline --graph
# @loppu ratkaisu
