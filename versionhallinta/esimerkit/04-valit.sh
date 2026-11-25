#!/usr/bin/env bash
# Revisiovälit: mitä toisessa haarassa on, mitä toisessa ei.
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


git init -q -b main laskuri
cd laskuri
printf 'def rivit(t):\n    return t.count("\\n")\n' > laskuri.py
git add . && tallenna -m "Rivilaskuri"
git switch -q -c sanat
printf 'def sanat(t):\n    return len(t.split())\n' > sanat.py
git add . && tallenna -m "Sanalaskuri"
printf 'Sanat lasketaan välilyönneistä.\n' > OHJE.md
git add . && tallenna -m "Ohje"
git switch -q main
printf 'MIT\n' > LICENSE
git add . && tallenna -m "Lisenssi"

# @alku valit
echo "== main..sanat: sanat-haaran omat commitit"
git log --oneline main..sanat
echo "== sanat..main: mitä main-haarassa on uutta"
git log --oneline sanat..main
echo "== main...sanat: molempien omat, < main ja > sanat"
git log --oneline --left-right main...sanat
echo "== diff main...sanat: haaran muutokset yhteisestä kannasta"
git diff --stat main...sanat
# @loppu valit
