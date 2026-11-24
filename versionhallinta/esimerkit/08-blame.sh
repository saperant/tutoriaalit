#!/usr/bin/env bash
# Kuka muutti rivin ja miksi: blame ja log -L.
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

olli() {
    GIT_AUTHOR_NAME="Olli Ohjelmoija" GIT_AUTHOR_EMAIL=olli@example.fi \
    GIT_COMMITTER_NAME="Olli Ohjelmoija" \
    GIT_COMMITTER_EMAIL=olli@example.fi "$@"
}
git init -q -b main palvelu
cd palvelu
printf 'portti = 8080\naikakatkaisu = 30\nyrityksia = 3\n' > asetukset.ini
git add . && tallenna -m "Asetukset"
sed -i 's/= 30/= 5/' asetukset.ini
git add . && aika && olli git commit -q -m "Lyhyempi aikakatkaisu" \
    -m "Asiakkaat odottivat 30 s jumittuneen taustapalvelun takia."
sed -i 's/= 3$/= 5/' asetukset.ini
git add . && tallenna -m "Enemmän yrityksiä"

# @alku blame
git blame --date=short asetukset.ini
# @loppu blame
# @alku miksi
rivi=$(git blame -L 2,2 --porcelain asetukset.ini | head -c 40)
git show -s --format='%an: %s%n%b' "$rivi"
# @loppu miksi
