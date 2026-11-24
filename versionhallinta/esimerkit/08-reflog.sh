#!/usr/bin/env bash
# Kadonneen commitin palautus reflogista.
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
printf 'def sanat(t):\n    return len(t.split())\n' > sanat.py
git add . && tallenna -m "Sanalaskuri"

# @alku vahinko
git reset -q --hard HEAD~1    # vahinko: commit katoaa haarasta
git log --oneline
ls
# @loppu vahinko
# @alku reflog
git reflog --format='%h %gd %gs' | head -n 3
git branch pelastus 'HEAD@{1}'
git log --oneline pelastus
# @loppu reflog
