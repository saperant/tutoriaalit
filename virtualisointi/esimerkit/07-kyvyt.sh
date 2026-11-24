#!/usr/bin/env bash
# Kyvyt (capabilities): rootin kaikkivoipuus pilkottuna osiin. Kontin
# root on yleensä vain osittainen root, koska osa kyvyistä on poistettu.
set -euo pipefail
if [[ $EUID -ne 0 ]]; then exec sudo -n -- bash "$0" "$@"; fi
export LC_ALL=C
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT
touch "$tyo/tiedosto"

# @alku pudotus
# Root ilman CAP_CHOWN-kykyä ei voi vaihtaa tiedoston omistajaa.
chown 65534 "$tyo/tiedosto" && echo "root: chown onnistui"
{ capsh --drop=cap_chown -- -c "chown 0 '$tyo/tiedosto'" 2>&1 || true; } |
    sed "s|$tyo/||; s/^/ilman CAP_CHOWN: /"
# @loppu pudotus

# @alku lisays
# Tavallinen käyttäjä ja etuoikeutettu portti (< 1024). Ambient-kyky
# periytyy ohjelmalle, joten palvelu ei tarvitse rootia lainkaan.
sido='import socket
s = socket.socket()
try:
    s.bind(("", 80))
    print("portti 80: sidottu")
except PermissionError:
    print("portti 80: lupa evätty")'
kayttaja=(setpriv --reuid=65534 --regid=65534 --clear-groups)
unshare --net "${kayttaja[@]}" python3 -c "$sido"
unshare --net "${kayttaja[@]}" --inh-caps=+net_bind_service \
    --ambient-caps=+net_bind_service python3 -c "$sido"
# @loppu lisays
