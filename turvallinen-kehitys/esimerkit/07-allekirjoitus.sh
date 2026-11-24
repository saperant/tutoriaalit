#!/usr/bin/env bash
# Git-committien allekirjoitus SSH-avaimella ja tarkistus luotettujen
# allekirjoittajien listalla. Ajetaan tilapäisessä repositoriossa.
set -euo pipefail
# Käyttäjän omat git-asetukset (esim. commit.gpgsign) eivät vaikuta.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

ssh-keygen -q -t ed25519 -N '' -C aino@example.fi -f aino
ssh-keygen -q -t ed25519 -N '' -C eve@example.org -f eve

git init -q -b main repo
cd repo
git config user.name "Aino Kehittäjä"
git config user.email "aino@example.fi"

# @alku asetukset
git config gpg.format ssh
git config user.signingkey ../aino.pub
# Kuka saa allekirjoittaa: sähköposti, nimiavaruus ja julkinen avain.
printf 'aino@example.fi namespaces="git" %s\n' "$(cat ../aino.pub)" \
    > ../luotetut
git config gpg.ssh.allowedSignersFile ../luotetut
# @loppu asetukset

# @alku commitit
echo "versio 1" > LUEMINUT
git add -A && git commit -q -S -m "Allekirjoitettu muutos"

echo "versio 2" > LUEMINUT
git add -A && git commit -q -m "Allekirjoittamaton muutos"

echo "versio 3" > LUEMINUT
git add -A
git -c user.signingkey=../eve.pub commit -q -S -m "Vieraan avaimen muutos"

# G = hyvä, U = hyvä mutta allekirjoittaja ei luotettu, N = ei allekirjoitusta
git log --format='%G? %s'
# @loppu commitit

# @alku tarkistus
for c in HEAD~2 HEAD~1 HEAD; do
    if git verify-commit "$c" 2>/dev/null; then
        echo "$c: hyväksytty"
    else
        echo "$c: hylätty"
    fi
done
# @loppu tarkistus
