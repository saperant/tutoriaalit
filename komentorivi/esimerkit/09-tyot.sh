#!/usr/bin/env bash
# Taustaprosessi, sen tila ja lopettaminen signaalilla.
set -euo pipefail
export LC_ALL=C

# @alku tausta
sleep 300 &
pid=$!
kill -0 "$pid" && echo "prosessi on käynnissä"
ps -o comm=,args= -p "$pid"
tr '\0' ' ' < "/proc/$pid/cmdline"; echo
# @loppu tausta

# @alku lopetus
kill "$pid"                    # oletus on TERM (15)
wait "$pid" || tila=$?
echo "paluuarvo $tila = 128 + $(( tila - 128 )) ($(kill -l "$tila"))"
kill -0 "$pid" 2> /dev/null || echo "prosessi on päättynyt"
# @loppu lopetus
