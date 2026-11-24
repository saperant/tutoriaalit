#!/usr/bin/env bash
# Jokainen commit on tilannekuva; muuttumaton sisältö jaetaan.
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
printf 'MIT\n' > LICENSE
git add . && tallenna -m "Ensimmäinen versio"

# @alku nimeaminen
git mv README.md LUEMINUT.md
tallenna -m "Suomenkielinen nimi"
printf 'Laskuri laskee rivit.\n' > LUEMINUT.md
git add . && tallenna -m "Tarkempi kuvaus"

for c in HEAD~2 HEAD~1 HEAD; do
    echo "== $(git log -1 --format=%s "$c")"
    git ls-tree "$c" | awk '{ print substr($3, 1, 7), $4 }'
done
# @loppu nimeaminen
