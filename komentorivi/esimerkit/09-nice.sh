#!/usr/bin/env bash
# Prosessin prioriteetti ja resurssirajat.
set -euo pipefail
export LC_ALL=C

# @alku nice
nice                           # kuoren oma arvo
nice -n 10 nice                # lapsi alemmalla prioriteetilla
nice -n 10 nice -n 5 nice      # arvot summautuvat
# @loppu nice

# @alku ulimit
( ulimit -v 100000; python3 -c 'b = bytearray(500_000_000)' ) 2>&1 \
    | tail -n 1 || true
# @loppu ulimit
