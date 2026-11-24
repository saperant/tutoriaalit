#!/usr/bin/env bash
# Runkopohjainen kehitys: lyhyet haarat ja päähaaran historia.
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

git init -q -b main palvelu
cd palvelu
printf 'Palvelu\n' > README.md
git add . && tallenna -m "README"

# @alku lyhyet
yhdista() {   # haara -> main yhdistämiscommitilla, haara pois
    git switch -q main && aika
    git merge -q --no-ff --no-edit "$1" && git branch -q -d "$1"
}
for tehtava in kirjautuminen haku raportti; do
    git switch -q -c "$tehtava"
    printf '%s\n' "$tehtava" > "$tehtava.txt"
    git add . && tallenna -m "Lisää $tehtava (osa 1)"
    printf 'valmis\n' >> "$tehtava.txt"
    git add . && tallenna -m "Lisää $tehtava (osa 2)"
    yhdista "$tehtava"
done
echo "== päähaaran historia (--first-parent)"
git log --oneline --first-parent
echo "== kaikki commitit: $(git rev-list --count HEAD)"
# @loppu lyhyet
# @alku julkaisu
aika && git tag -a v1.0 -m "Julkaisu 1.0"
git branch julkaisu/1.0 v1.0   # vain korjauksia varten
git branch --list 'julkaisu/*'
# @loppu julkaisu
