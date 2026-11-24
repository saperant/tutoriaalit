#!/usr/bin/env bash
# Alimoduli: toinen repositorio tarkassa versiossa.
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

# Paikallisista poluista kloonaaminen alimoduleiksi on oletuksena
# estetty (tietoturvasyistä); esimerkissä se sallitaan.
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=protocol.file.allow
export GIT_CONFIG_VALUE_0=always

git init -q -b main kirjasto
(cd kirjasto && printf 'def sanat(t):\n    return len(t.split())\n' \
    > sanat.py && git add . && tallenna -m "Kirjasto 1")

# @alku lisays
git init -q -b main sovellus
cd sovellus
git submodule add -q ../kirjasto ulkoiset/kirjasto
aika && git commit -q -m "Kirjasto alimoduliksi"
cat .gitmodules
git ls-tree HEAD ulkoiset/ | awk '{ print $1, $2, substr($3, 1, 7), $4 }'
# @loppu lisays
# @alku paivitys
(cd ../kirjasto && printf '# v2\n' >> sanat.py && git add . \
    && tallenna -m "Kirjasto 2")
git submodule update -q --remote ulkoiset/kirjasto 2> /dev/null
git status --short            # alimodulin osoitin muuttui
git add ulkoiset/kirjasto && aika && git commit -q -m "Kirjasto 2"
git log --oneline
# @loppu paivitys
# @alku kloonaus
cd .. && git clone -q --recurse-submodules sovellus kopio 2> /dev/null
ls kopio/ulkoiset/kirjasto
# @loppu kloonaus
