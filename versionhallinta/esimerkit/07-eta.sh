#!/usr/bin/env bash
# Etärepositorio: clone, push, fetch ja pull.
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

# @alku olli
olli() {   # komento Ollin nimissä
    GIT_AUTHOR_NAME="Olli Ohjelmoija" GIT_AUTHOR_EMAIL=olli@example.fi \
    GIT_COMMITTER_NAME="Olli Ohjelmoija" \
    GIT_COMMITTER_EMAIL=olli@example.fi "$@"
}
# @loppu olli

# @alku palvelin
git init -q --bare -b main laskuri.git      # "palvelin"
git clone -q laskuri.git aino 2> /dev/null   # tyhjä vielä
cd aino
printf 'Laskuri\n' > README.md
git add . && tallenna -m "README"
git push -q origin main
git branch -a                 # paikallinen ja etähaaran kopio
# @loppu palvelin
# @alku olli-tyo
cd .. && git clone -q laskuri.git olli && cd olli
printf 'MIT\n' > LICENSE
git add . && aika && olli git commit -q -m "Lisenssi"
olli git push -q
# @loppu olli-tyo
# @alku fetch
cd ../aino
git fetch -q                  # hakee, ei muuta omaa haaraa
git status -sb | head -n 1
git log --oneline --all --decorate \
    --decorate-refs-exclude=refs/remotes/origin/HEAD
git merge -q --ff-only origin/main   # sama kuin git pull --ff-only
git status -sb | head -n 1
# @loppu fetch
