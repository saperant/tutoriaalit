#!/usr/bin/env bash
# Revert, reset ja cherry-pick: julkaistun virheen korjaus.
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
printf 'versio = 1\nraja = 100\n' > asetukset.ini
git add . && tallenna -m "Versio 1"
git branch julkaisu-1         # julkaistu versio jatkaa omaa haaraansa
sed -i 's/raja = 100/raja = 10/' asetukset.ini
git add . && tallenna -m "Pienempi raja"
printf 'teema = tumma\n' > ulkoasu.ini
git add . && tallenna -m "Uusi asetus"

# @alku revert
# Jaettu historia: virhe perutaan uudella commitilla.
aika
git revert --no-edit HEAD~1 > /dev/null
git log --oneline
cat asetukset.ini
# @loppu revert
# @alku reset
echo "== reset-tilat"
printf 'kokeilu = 1\n' >> ulkoasu.ini
git add . && tallenna -m "Kokeilu"
git reset -q --soft HEAD~1 && git status --short   # muutos valmisteltu
git reset -q --mixed HEAD && git status --short    # muutos työhakem.
git reset -q --hard HEAD && git status --short     # muutos poissa
echo "(tyhjä)"
# @loppu reset
# @alku cherry-pick
echo "== korjaus julkaisuhaaraan"
printf 'salasanan_pituus = 15\n' > turva.ini
git add . && tallenna -m "Korjaa tietoturva-asetus"
git switch -q julkaisu-1
aika
git cherry-pick -x main > /dev/null
git log --format='%h %s%n%b' -1 | sed '/^$/d'
# @loppu cherry-pick
