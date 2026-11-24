#!/usr/bin/env bash
# Haarat ovat siirtyviä viitteitä; pikakelaus.
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

# @alku haara
git switch -q -c sanat        # uusi haara ja siirtyminen siihen
printf 'def sanat(t):\n    return len(t.split())\n' > sanat.py
git add . && tallenna -m "Sanalaskuri"
git branch                    # * = nykyinen haara
cat .git/HEAD
git log --oneline --all --decorate
# @loppu haara
# @alku pikakelaus
git switch -q main
git merge --ff-only sanat > /dev/null
git log --oneline --decorate
git branch -d sanat           # yhdistetty haara voidaan poistaa
# @loppu pikakelaus
