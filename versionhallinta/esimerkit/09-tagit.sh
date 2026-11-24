#!/usr/bin/env bash
# Tagit, versiot ja git describe.
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
for v in 1 2 3; do
    printf 'versio %d\n' "$v" > VERSIO
    git add . && tallenna -m "Muutos $v"
done

# @alku tagit
git tag kokeilu HEAD~2                     # kevyt: pelkkä viite
aika
git tag -a v1.0.0 -m "Ensimmäinen julkaisu" HEAD~1   # annotoitu
git cat-file -t kokeilu
git cat-file -t v1.0.0
git cat-file -p v1.0.0
# @loppu tagit
# @alku describe
git describe                       # lähin annotoitu tagi + etäisyys
printf 'versio 4\n' > VERSIO
git describe --dirty
git checkout -q VERSIO
for t in v1.10.0 v1.2.0 v1.9.1; do aika; git tag -a "$t" -m "$t"; done
git tag -l 'v1.*' --sort=v:refname    # versiojärjestys, ei aakkos
# @loppu describe
