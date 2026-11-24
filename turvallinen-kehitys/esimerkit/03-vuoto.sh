#!/usr/bin/env bash
# Vuotanut salaisuus: poistaminen ei riitä, historian siivous ei riitä.
# Ajetaan tilapäisessä repositoriossa.
set -euo pipefail
# Käyttäjän omat git-asetukset (esim. commit.gpgsign) eivät vaikuta.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export FILTER_BRANCH_SQUELCH_WARNING=1

git init -q -b main repo
cd repo
git config user.name "Aino Kehittäjä"
git config user.email "aino@example.fi"

# @alku vuoto
printf 'MAKSU_AVAIN=tk_live_51Hq8rT2\n' > .env
git add .env && git commit -q -m "Lisää asetukset"
git rm -q .env && git commit -q -m "Poista vahingossa lisätty .env"
# @loppu vuoto

# @alku etsi
loytyy() {   # montako historian kohtaa sisältää avaimen
    git log --all -p | grep -c 'tk_live_' || true
}
echo "poiston jälkeen historiassa: $(loytyy)"
git clone -q . ../kollegan-kopio
# @loppu etsi

# @alku siivous
git filter-branch --index-filter \
    'git rm -q --cached --ignore-unmatch .env' -- --all >/dev/null
echo "uudelleenkirjoituksen jälkeen: $(loytyy)"
git for-each-ref --format='%(refname)' refs/original/ \
    | xargs -r -n1 git update-ref -d
git reflog expire --expire=now --all
git gc -q --prune=now
echo "varmuuskopioviitteiden ja gc:n jälkeen: $(loytyy)"
echo "kollegan kopiossa: $(git -C ../kollegan-kopio log --all -p \
    | grep -c 'tk_live_' || true)"
# @loppu siivous
