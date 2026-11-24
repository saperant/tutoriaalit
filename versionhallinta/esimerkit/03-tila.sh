#!/usr/bin/env bash
# Työhakemisto, valmistelualue ja commit.
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
printf 'def rivit(teksti):\n    return teksti.count("\\n")\n' > laskuri.py
printf 'Laskuri\n' > README.md
git add . && tallenna -m "Rivilaskuri"

# @alku muutokset
printf 'def sanat(teksti):\n    return len(teksti.split())\n' >> laskuri.py
printf 'Laskee rivit ja sanat.\n' >> README.md
git add laskuri.py            # vain laskuri.py seuraavaan committiin
printf '# TODO: merkit\n' >> laskuri.py
git status --short
# @loppu muutokset
# @alku diffit
echo "== git diff --staged (valmisteltu)"
git diff --staged --stat
echo "== git diff (valmistelematon)"
git diff
# @loppu diffit
# @alku palautus
git restore laskuri.py        # hylkää valmistelemattoman muutoksen
git restore --staged laskuri.py   # poista valmistelusta, muutos jää
git status --short
git add -A && tallenna -m "Sanalaskuri ja tarkempi README"
git show --stat --format='%h %s' HEAD
# @loppu palautus
