#!/usr/bin/env bash
# Konfliktin kanta näkyviin ja toisen puolen valinta.
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
sed -i 's/8080/80/; s/30/60/' asetukset.ini
git add . && tallenna -m "Tuotannon asetukset"
git switch -q main
sed -i 's/8080/8000/; s/30/10/' asetukset.ini
git add . && tallenna -m "Kehityksen asetukset"

# @alku zdiff3
git config merge.conflictStyle zdiff3
aika
git merge -q tuotanto > /dev/null || true
cat asetukset.ini
# @loppu zdiff3
# @alku valinta
git checkout -q --theirs asetukset.ini  # koko tiedosto toisesta haarasta
cat asetukset.ini
git merge --abort                     # tai luovu koko yhdistämisestä
git status --short
git log --oneline -1
# @loppu valinta
