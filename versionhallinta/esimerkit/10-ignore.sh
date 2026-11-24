#!/usr/bin/env bash
# Mitä ei versioida: .gitignore ja jo seurattu tiedosto.
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
mkdir -p build src logs
touch src/main.py build/main.o logs/a.log logs/.keep .env .env.esimerkki

# @alku ignore
cat > .gitignore <<'IGNORE'
# käännöstuotteet ja lokit
build/
*.log
# paikalliset salaisuudet, mutta esimerkkitiedosto mukaan
.env
!.env.esimerkki
IGNORE
git status --short --untracked-files=all
git check-ignore -v build/main.o logs/a.log .env
# @loppu ignore
# @alku seurattu
# Jo seurattuun tiedostoon .gitignore ei vaikuta.
printf 'debug\n' > asetukset.local
git add asetukset.local && tallenna -m "Vahinko"
printf 'asetukset.local\n' >> .gitignore
printf 'muutos\n' >> asetukset.local
git status --short asetukset.local
git rm -q --cached asetukset.local      # pois versionhallinnasta
git status --short asetukset.local
ls asetukset.local                      # tiedosto jää levylle
# @loppu seurattu
