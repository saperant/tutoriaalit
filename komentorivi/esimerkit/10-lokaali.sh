#!/usr/bin/env bash
# Lokaali vaikuttaa lajitteluun, merkkien laskentaan ja viesteihin.
set -euo pipefail

# @alku lokaali
printf '%s\n' banaani Omena appelsiini Ananas \
    | LC_ALL=C sort | paste -sd' '
printf '%s\n' banaani Omena appelsiini Ananas \
    | LC_ALL=C sort -f | paste -sd' '
printf 'Äänestys' | LC_ALL=C wc -m
printf 'Äänestys' | LC_ALL=C.UTF-8 wc -m
# @loppu lokaali

# @alku versiot
printf '%s\n' v1.10.0 v1.9.2 v1.2.0 v2.0.0 | LC_ALL=C sort | paste -sd' '
printf '%s\n' v1.10.0 v1.9.2 v1.2.0 v2.0.0 | sort -V | paste -sd' '
# @loppu versiot
