#!/usr/bin/env bash
# Kontti on tavallinen prosessi omissa nimiavaruuksissaan. unshare luo
# uudet PID-, UTS- ja mount-nimiavaruudet ilman konttiajoympäristöä.
set -euo pipefail
if [[ $EUID -ne 0 ]]; then
    exec sudo -n "$0" "$@"
fi

# @alku unshare
# shellcheck disable=SC2016  # $-lausekkeet laajennetaan nimiavaruudessa
unshare --pid --uts --mount --fork --mount-proc bash -c '
    hostname kontti
    echo "isäntänimi nimiavaruudessa: $(hostname)"
    echo "kuoren PID: $$"
    echo "PID 1 on: $(ps -o comm= -p 1)"
    echo "isännän prosessit näkyvissä: $(
        [[ $(ps -e --no-headers | wc -l) -lt 10 ]] && echo ei || echo kyllä)"
'
# @loppu unshare
if [[ $(hostname) != kontti ]]; then
    echo "isännän isäntänimi ennallaan: kyllä"
fi
