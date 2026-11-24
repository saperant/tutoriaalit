#!/usr/bin/env bash
# Historian siistiminen ennen jakamista: fixup ja interaktiivinen rebase.
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
printf 'def sanat(t):\n    return len(t.split)\n' > sanat.py
git add . && tallenna -m "Sanalaskuri"
printf 'print("debug")\n' > roska.py
git add . && tallenna -m "WIP väliaikainen tuloste"
printf 'def merkit(t):\n    return len(t)\n' > merkit.py
git add . && tallenna -m "Merkkilaskuri"

# @alku fixup
# Virhe huomattiin: split ilman sulkeita. Korjaus merkitään
# korjaukseksi commitille, jota se koskee.
sed -i 's/t.split)/t.split())/' sanat.py
git add . && tallenna --fixup=":/Sanalaskuri"
git log --oneline
# @loppu fixup
# @alku interaktiivinen
# Interaktiivinen rebase avaa muokattavan tehtävälistan. Skriptissä
# listaa muokataan sedillä: WIP-commit pudotetaan (drop), ja
# --autosquash on jo siirtänyt fixup-rivin paikalleen.
wip=$(git rev-parse --short ':/WIP')
aika
GIT_SEQUENCE_EDITOR="sed -i 's/^pick $wip /drop $wip /'" \
    git rebase -q -i --autosquash main
git log --oneline
git show --format= HEAD~1 -- sanat.py | tail -n 2
ls
# @loppu interaktiivinen
