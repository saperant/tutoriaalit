#!/usr/bin/env bash
# Gitin tietomalli: blobit, puut, commitit ja viittaukset.
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
mkdir src
printf 'Laskuri\n' > README.md
printf 'print("hei")\n' > src/main.py
git add . && tallenna -m "Ensimmäinen versio"

# @alku commit
echo "== commit"
git cat-file -p HEAD
# @loppu commit
# @alku puu
puu=$(git rev-parse 'HEAD^{tree}')
echo "== puu ${puu:0:7}"
git cat-file -p "$puu"
echo "== alipuu src"
git cat-file -p HEAD:src
echo "== blob"
git cat-file -p HEAD:README.md
# @loppu puu
# @alku tunniste
# Tunniste on sisällön tiiviste: sama sisältö, sama blob.
git hash-object README.md
printf 'Laskuri\n' | git hash-object --stdin
git rev-parse HEAD:README.md
# @loppu tunniste
# @alku viitteet
echo "== viitteet"
cat .git/HEAD
git rev-parse --short main
git cat-file -t main
git count-objects | cut -d, -f1
# @loppu viitteet
