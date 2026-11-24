#!/usr/bin/env bash
# Nimiavaruudet yksi kerrallaan unshare- ja nsenter-komennoilla.
# Sisäkomennot ovat tarkoituksella yksinkertaisissa lainausmerkeissä:
# ne laajennetaan vasta uudessa nimiavaruudessa.
# shellcheck disable=SC2016
set -euo pipefail
if [[ $EUID -ne 0 ]]; then exec sudo -n -- bash "$0" "$@"; fi
export LC_ALL=C
tyo=$(mktemp -d)
tausta=
siivoa() {
    [[ -n $tausta ]] && kill "$tausta" 2>/dev/null
    rm -rf "$tyo"
}
trap siivoa EXIT

# @alku uts
isanta=$(hostname)
unshare --uts sh -c 'hostname vieras; echo "UTS: konenimi $(hostname)"'
[[ $(hostname) == "$isanta" ]] && echo "UTS: isännän nimi ennallaan"
# @loppu uts

# @alku pid
unshare --pid --fork --mount-proc sh -c \
    'echo "PID: oma PID $$, prosessit:" /proc/[0-9]*'
# @loppu pid

# @alku net
unshare --net sh -c \
    'echo "NET: liitännät" $(cut -d: -f1 /proc/net/dev | tail -n +3)'
# @loppu net

# @alku mnt
mkdir "$tyo/liitos"
unshare --mount --propagation private sh -c \
    'mount -t tmpfs none "$1" && touch "$1/sisalla" &&
     echo "MNT: sisällä" "$(ls "$1")"' sh "$tyo/liitos"
echo "MNT: ulkona $(find "$tyo/liitos" -type f | wc -l) tiedostoa"
# @loppu mnt

# @alku nsenter
# Taustaprosessi omassa UTS-nimiavaruudessaan; nsenter liittyy siihen
# kuten "docker exec" liittyy käynnissä olevaan konttiin.
unshare --uts sh -c 'hostname taustalla; exec sleep 60' &
tausta=$!
for _ in $(seq 100); do
    nimi=$(nsenter --target "$tausta" --uts hostname)
    [[ $nimi == taustalla ]] && break
    sleep 0.05
done
echo "nsenter: kohteen konenimi $nimi"
[[ $(readlink /proc/self/ns/uts) != $(readlink "/proc/$tausta/ns/uts") ]] &&
    echo "nsenter: eri UTS-nimiavaruus kuin isännällä"
# @loppu nsenter
