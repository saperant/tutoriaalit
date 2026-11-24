#!/usr/bin/env bash
# Rebase siirtää haaran uuden kannan päälle.
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
printf 'Laskuri\n' > README.md
git add . && tallenna -m "README"
git switch -q -c sanat
printf 'def sanat(t):\n    return len(t.split())\n' > sanat.py
git add . && tallenna -m "Sanalaskuri"
printf 'def merkit(t):\n    return len(t)\n' > merkit.py
git add . && tallenna -m "Merkkilaskuri"
git switch -q main
printf 'MIT\n' > LICENSE
git add . && tallenna -m "Lisenssi"

# @alku ennen
git log --oneline --graph --all
vanha=$(git rev-parse --short sanat)
# @loppu ennen
# @alku rebase
git switch -q sanat
aika
git rebase -q main
echo "== rebasen jälkeen (sanat: $vanha -> $(git rev-parse --short HEAD))"
git log --oneline --graph --all
# @loppu rebase
# @alku pikakelaus
git switch -q main
git merge -q --ff-only sanat
git log --oneline
# @loppu pikakelaus
