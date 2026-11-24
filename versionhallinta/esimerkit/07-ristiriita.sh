#!/usr/bin/env bash
# Hylätty push, rebase-pull ja turvallinen pakotus.
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

olli() {
    GIT_AUTHOR_NAME="Olli Ohjelmoija" GIT_AUTHOR_EMAIL=olli@example.fi \
    GIT_COMMITTER_NAME="Olli Ohjelmoija" \
    GIT_COMMITTER_EMAIL=olli@example.fi "$@"
}
git init -q --bare -b main laskuri.git
git clone -q laskuri.git aino 2> /dev/null
(cd aino && printf 'Laskuri\n' > README.md && git add . \
    && tallenna -m "README" && git push -q origin main)
git clone -q laskuri.git olli

# @alku hylatty
cd olli
printf 'MIT\n' > LICENSE
git add . && aika && olli git commit -q -m "Lisenssi"
olli git push -q
cd ../aino
printf 'def rivit(t):\n    return t.count("\\n")\n' > laskuri.py
git add . && tallenna -m "Rivilaskuri"
git push -q origin main 2> /dev/null \
    || echo "push hylättiin: etäpää on edellä"
# @loppu hylatty
# @alku pull-rebase
aika
git pull -q --rebase
git push -q origin main
git log --oneline --graph
# @loppu pull-rebase
# @alku lease
# Oma haara uudelleenkirjoitetaan (amend) ja pakotetaan. Jos joku
# muu ehti pushata välissä, --force-with-lease kieltäytyy.
git switch -q -c kokeilu && git push -q -u origin kokeilu 2> /dev/null
(cd ../olli && git fetch -q && git switch -q kokeilu \
    && printf 'x\n' > olli.txt && git add . && aika \
    && olli git commit -q -m "Ollin lisäys" && olli git push -q)
aika && git commit -q --amend -m "Rivilaskuri (korjattu viesti)"
git push -q --force-with-lease 2> /dev/null \
    || echo "force-with-lease kieltäytyi: Ollin commit olisi kadonnut"
# @loppu lease
