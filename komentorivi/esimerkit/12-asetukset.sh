#!/usr/bin/env bash
# ~/.ssh/config: isäntäkohtaiset asetukset ja hyppykone. ssh -G
# näyttää lopulliset asetukset ottamatta yhteyttä.
set -euo pipefail
export LC_ALL=C

# @alku config
cat > config <<'ASETUKSET'
Host bastioni
    HostName bastioni.example.com
    User yllapito

Host rakennus-*
    HostName %h.sisainen.example.com
    User ci
    ProxyJump bastioni
    IdentityFile ~/.ssh/rakennus_ed25519

Host *
    ServerAliveInterval 30
    IdentitiesOnly yes
ASETUKSET
# @loppu config

# @alku tulkinta
ssh -T -F config -G rakennus-01 < /dev/null 2> /dev/null \
    | grep -wE '^(hostname|user|port|proxyjump|identityfile)' | sort
# @loppu tulkinta
