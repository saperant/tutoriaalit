#!/usr/bin/env bash
# SSH-avainparin luonti ja julkisen avaimen rajoitettu käyttö.
set -euo pipefail
export LC_ALL=C

# @alku avain
ssh-keygen -q -t ed25519 -N '' -C 'kaisa@kannettava' -f tunnus_ed25519
stat -c '%a %n' tunnus_ed25519 tunnus_ed25519.pub
cut -d' ' -f1,3 tunnus_ed25519.pub
ssh-keygen -l -f tunnus_ed25519.pub | awk '{ print $1, $3, $4 }'
# @loppu avain

# @alku rajoitettu
avain=$(cut -d' ' -f1,2 tunnus_ed25519.pub)
printf 'from="10.0.0.0/8",command="/usr/local/bin/varmuuskopioi",%s %s\n' \
    'no-port-forwarding,no-pty' "$avain varmistus" > authorized_keys
ssh-keygen -l -f authorized_keys | awk '{ print $1, $3, $NF }'
# @loppu rajoitettu
