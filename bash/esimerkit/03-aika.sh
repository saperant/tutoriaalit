#!/usr/bin/env bash
# Aikaleimat ja kestot. Esimerkin ajat ovat kiinteitä, jotta tuloste on
# toistettava.
set -euo pipefail
export LC_ALL=C TZ=UTC

# @alku aika
alku=$(date -d '2025-03-10 08:00:00' +%s)     # sekunteja vuodesta 1970
loppu=$(date -d '2025-03-10 09:30:15' +%s)
kesto=$(( loppu - alku ))
printf 'kesto %d min %d s\n' $(( kesto / 60 )) $(( kesto % 60 ))

printf 'alkoi %(%F %T)T\n' "$alku"            # ei käynnistä prosessia
date -d "@$loppu" +%Y-%m-%dT%H:%M:%SZ
date -d '2025-03-10 + 30 days' +%F
# @loppu aika
