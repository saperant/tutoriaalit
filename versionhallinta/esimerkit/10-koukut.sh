#!/usr/bin/env bash
# Koukut: pre-commit ja commit-msg, jaettuna core.hooksPathilla.
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

# @alku koukut
mkdir .githooks
cat > .githooks/pre-commit <<'KOUKKU'
#!/bin/sh
# Hylkää commitin, jos valmistellussa muutoksessa on rivin lopun
# välilyöntejä tai ratkaisemattomia konfliktimerkkejä.
exec git diff --cached --check
KOUKKU
cat > .githooks/commit-msg <<'KOUKKU'
#!/bin/sh
# Otsikkorivi: iso alkukirjain, enintään 50 merkkiä, ei pistettä.
otsikko=$(head -n 1 "$1")
if ! printf '%s' "$otsikko" | grep -qE '^[[:upper:]].{0,49}$' \
   || [ "${otsikko%.}" != "$otsikko" ]; then
    echo "commit-viesti: huono otsikko: $otsikko" >&2
    exit 1
fi
KOUKKU
chmod +x .githooks/*
git config core.hooksPath .githooks   # koukut versionhallintaan
git add .githooks && tallenna -m "Yhteiset koukut"
# @loppu koukut
# @alku kokeilu
printf 'def rivit(t):  \n    return t.count("\\n")\n' > laskuri.py
git add laskuri.py
tallenna -m "Rivilaskuri" 2>&1 || echo "=> hylätty (pre-commit)"
sed -i 's/  $//' laskuri.py && git add laskuri.py
tallenna -m "lisää rivilaskuri." 2>&1 || echo "=> hylätty (commit-msg)"
tallenna -m "Lisää rivilaskuri" && git log --oneline -1
# @loppu kokeilu
