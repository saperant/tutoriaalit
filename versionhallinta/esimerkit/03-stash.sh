#!/usr/bin/env bash
# Keskeneräinen työ talteen: stash.
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

# @alku stash
printf '# TODO: sanat\n' >> laskuri.py       # keskeneräinen muutos
printf 'muistiinpano\n' > muistio.txt        # uusi, seuraamaton tiedosto
git status --short
aika
git stash push -q -u -m "sanalaskuri kesken"  # -u: myös seuraamattomat
git status --short                            # puhdas: voi vaihtaa haaraa
git stash list
# @loppu stash
# @alku pop
echo "== pop"
git stash pop -q
git status --short
git stash list | wc -l
# @loppu pop
# @alku clean
echo "== clean"
touch ajo.tmp
git clean -n                  # näyttää, mitä poistettaisiin
git clean -q -f ajo.tmp       # poistaa
git status --short
# @loppu clean
