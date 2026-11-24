#!/usr/bin/env bash
# Virheen etsintä puolittamalla: git bisect run.
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
# Kymmenen committia; yksi niistä rikkoo sanalaskurin.
printf 'def sanat(t):\n    return len(t.split())\n' > laskuri.py
git add . && tallenna -m "Sanalaskuri"
for i in $(seq 1 9); do
    printf '# muutos %d\n' "$i" >> laskuri.py
    if [ "$i" -eq 6 ]; then
        sed -i 's/t.split()/t.split(" ")/' laskuri.py
    fi
    git add . && tallenna -m "Muutos $i"
done

# @alku testi
cat > testi.sh <<'TESTI'
#!/bin/sh
# 0 = hyvä, 1 = huono (125 = ohita, esim. ei käänny)
export PYTHONDONTWRITEBYTECODE=1
python3 -c 'import laskuri; assert laskuri.sanat("a  b\n") == 2'
TESTI
chmod +x testi.sh
# @loppu testi
# @alku bisect
git bisect start HEAD "HEAD~9" > /dev/null   # huono, hyvä
git bisect run ./testi.sh > /dev/null 2>&1
echo "ensimmäinen huono: $(git log -1 --format=%s refs/bisect/bad)"
git bisect log | grep '^# \(good\|bad\|first\)' \
    | sed 's/\[\(.......\)[0-9a-f]*\]/\1/'
git bisect reset > /dev/null 2>&1   # takaisin lähtöhaaraan
# @loppu bisect
