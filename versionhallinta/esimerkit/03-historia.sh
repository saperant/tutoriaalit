#!/usr/bin/env bash
# Historian tarkastelu: log, show ja haku.
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
printf 'def sanat(t):\n    return len(t.split())\n' >> laskuri.py
git add . && tallenna -m "Sanalaskuri"
printf 'Laskuri\n' > README.md
git add . && tallenna -m "README"
sed -i 's/t.split()/t.split(None)/' laskuri.py
git add . && tallenna -m "Korjaa sanojen erotin" \
    -m "Pelkkä split() jakaa myös rivinvaihdoista; erotin näkyviin."

# @alku loki
git log --oneline
echo "== muotoiltu"
git log --format='%h %ad %an: %s' --date=short -2
echo "== vain laskuri.py"
git log --oneline -- laskuri.py
echo "== milloin 'split' lisättiin tai poistettiin (-S)"
git log --oneline -S 'split()'
# @loppu loki
# @alku show
echo "== viimeisin muutos"
git show --format='%h %s%n%n%b' HEAD
# @loppu show
