#!/usr/bin/env bash
# .gitignore: tiedostot, joita ei versioida.
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

# Ohjelman ajo ja editori jättävät jälkeensä tiedostoja.
mkdir __pycache__
touch __pycache__/laskuri.cpython-312.pyc ajo.log .env

# @alku ignore
git status --short
printf '__pycache__/\n*.log\n.env\n' > .gitignore
echo "== .gitignoren jälkeen"
git status --short
git add .gitignore && tallenna -m "Ohita käännöstuotteet ja salaisuudet"
echo "muutoksia commitin jälkeen: $(git status --short | wc -l)"
# @loppu ignore
