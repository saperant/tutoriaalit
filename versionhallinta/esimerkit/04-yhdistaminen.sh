#!/usr/bin/env bash
# Erkaantuneet haarat ja kolmen osapuolen yhdistäminen.
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
printf 'def rivit(t):\n    return t.count("\\n")\n\n\n' > laskuri.py
printf 'def main():\n    pass\n' >> laskuri.py
git add . && tallenna -m "Rivilaskuri"

# @alku erkaantuminen
git switch -q -c sanat
sed -i '4i def sanat(t):\n    return len(t.split())\n' laskuri.py
git add . && tallenna -m "Sanalaskuri"
git switch -q main
sed -i 's/    pass/    print(rivit(input()))/' laskuri.py
git add . && tallenna -m "Pääohjelma"
echo "yhteinen kanta: $(git merge-base main sanat | cut -c1-7)"
# @loppu erkaantuminen
# @alku yhdistaminen
aika
git merge -q --no-edit sanat > /dev/null
git log --oneline --graph
echo "== tulos"
cat laskuri.py
# @loppu yhdistaminen
