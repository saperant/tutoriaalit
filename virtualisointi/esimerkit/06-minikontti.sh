#!/usr/bin/env bash
# Minikontti ilman konttityökaluja: overlay-juuri, omat nimiavaruudet ja
# init, joka on kontin PID 1. Docker ja Podman tekevät pohjimmiltaan
# saman (lisäksi cgroups, kyvyt ja seccomp).
set -euo pipefail
if [[ $EUID -ne 0 ]]; then exec sudo -n -- bash "$0" "$@"; fi
export LC_ALL=C

if [[ ${1-} != sisalla ]]; then
    hak=$(cd "$(dirname "$0")" && pwd)
    tyo=$(mktemp -d)
    trap 'rm -rf "$tyo"' EXIT
    cc=$(command -v gcc-14 || command -v gcc)
    "$cc" -static -O2 -Wall -Wextra -Werror -o "$tyo/init" \
        "$hak/kuva/sbin/init.c"
    # Oma liitosnimiavaruus: mikään liitos ei näy isännälle.
    unshare --mount --propagation private -- bash "$0" sisalla "$tyo"
    exit
fi

cd "$2"
# @alku kerrokset
mkdir fs
mount -t tmpfs tmpfs fs            # kerrokset muistiin
mkdir -p fs/ala/{sbin,proc,data,etc} fs/{yla,tyo,juuri}
cp init fs/ala/sbin/init           # "konttikuva": vain luettava kerros
echo "kuva 1.0" > fs/ala/etc/versio
mount -t overlay overlay \
    -o lowerdir=fs/ala,upperdir=fs/yla,workdir=fs/tyo fs/juuri
# @loppu kerrokset

# @alku kaynnistys
# Uudet PID-, UTS-, IPC-, verkko- ja liitosnimiavaruudet; juureksi
# overlay. --fork: vasta lapsesta tulee uuden PID-nimiavaruuden PID 1.
unshare --pid --fork --uts --ipc --net --mount --root=fs/juuri \
    /sbin/init
# @loppu kaynnistys

# @alku tarkistus
echo "isännän konenimi ennallaan: $(
    [[ $(hostname) != minikontti ]] && echo kyllä || echo ei)"
echo "kirjoitettava kerros:"
(cd fs/yla && find . -type f | sort | sed 's/^/  /')
echo "kuvan kerros koskematon: $(
    [[ ! -e fs/ala/data/terveiset.txt ]] && echo kyllä || echo ei)"
# @loppu tarkistus
