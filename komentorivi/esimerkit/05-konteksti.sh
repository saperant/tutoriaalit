#!/usr/bin/env bash
# Virheen ympäristö: rivit ennen ja jälkeen osuman.
set -euo pipefail
export LC_ALL=C

cat > rakennus.log <<'LOKI'
[1/4] kaannetaan jasennin.c
[2/4] kaannetaan apu.c
apu.c:42: warning: unused variable 'koko'
[3/4] kaannetaan paa.c
paa.c:17: error: 'puskuri' undeclared
paa.c:17: note: each undeclared identifier is reported only once
[4/4] linkitetaan
make: *** [Makefile:12: paa.o] Error 1
LOKI

# @alku konteksti
grep -B1 -A1 'error:' rakennus.log
echo "--"
grep -m1 -n -E 'error|warning' rakennus.log
# @loppu konteksti
