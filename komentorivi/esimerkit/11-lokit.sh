#!/usr/bin/env bash
# sshd:n epäonnistuneet kirjautumiset; aineisto on muotoa
# journalctl -u ssh -o cat.
set -euo pipefail
export LC_ALL=C

# @alku aineisto
cat > auth.log <<'LOKI'
Accepted publickey for kaisa from 10.0.0.5 port 50122 ssh2
Failed password for root from 192.0.2.7 port 51234 ssh2
Failed password for root from 192.0.2.7 port 51234 ssh2
Failed password for invalid user admin from 192.0.2.7 port 51240 ssh2
Failed password for invalid user oracle from 198.51.100.4 port 40022 ssh2
Failed password for kaisa from 10.0.0.5 port 50130 ssh2
LOKI
# @loppu aineisto

# @alku analyysi
grep 'Failed password' auth.log \
    | awk '{ for (i = 1; i < NF; i++) if ($i == "from") print $(i+1) }' \
    | sort | uniq -c | sort -k1,1nr -k2
grep -oE 'invalid user [^ ]+' auth.log | cut -d' ' -f3 | sort -u
# @loppu analyysi
