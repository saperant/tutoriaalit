#!/usr/bin/env bash
# Toimipisteiden välinen WireGuard-tunneli (site-to-site). Yhdyskäytävät
# gwa ja gwb ovat julkisessa verkossa; lähiverkot 10.1.0.0/24 ja
# 10.2.0.0/24 näkevät toisensa vain tunnelin kautta.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

for s in ha gwa gwb hb; do solmu "$s"; done
linkki ha eth0 gwa lan
linkki gwa wan gwb wan
linkki gwb lan hb eth0
ns ha ip addr add 10.1.0.10/24 dev eth0
ns ha ip route add default via 10.1.0.1
ns hb ip addr add 10.2.0.10/24 dev eth0
ns hb ip route add default via 10.2.0.1
ns gwa ip addr add 10.1.0.1/24 dev lan
ns gwb ip addr add 10.2.0.1/24 dev lan
ns gwa ip addr add 198.51.100.1/24 dev wan
ns gwb ip addr add 198.51.100.2/24 dev wan
for g in gwa gwb; do ns "$g" sysctl -qw net.ipv4.ip_forward=1; done

# @alku avaimet
# Kumpikin pää luo avainparin; vain julkiset avaimet vaihdetaan.
(
    umask 077
    for g in gwa gwb; do
        wg genkey > "$LABRA_HAK/$g.key"
        wg pubkey < "$LABRA_HAK/$g.key" > "$LABRA_HAK/$g.pub"
    done
)
# @loppu avaimet

# @alku tunneli
# tunneli SOLMU LIITÄNTÄ TUNNELIOSOITE VASTAPÄÄ VASTAPÄÄN-IP ETÄVERKKO
tunneli() {
    # Laboratoriossa käytetään käyttäjätilan toteutusta (wireguard-go);
    # tuotannossa ytimen WireGuard-moduulia (ip link add ... type wireguard).
    ns "$1" env WG_I_PREFER_BUGGY_USERSPACE_TO_POLISHED_KMOD=1 \
        wireguard-go -f "$2" > /dev/null 2>&1 &
    odota 10 ns "$1" ip link show "$2"
    ns "$1" wg set "$2" private-key "$LABRA_HAK/$1.key" listen-port 51820 \
        peer "$(cat "$LABRA_HAK/$4.pub")" endpoint "$5:51820" \
        allowed-ips "$6" persistent-keepalive 25
    ns "$1" ip addr add "$3" dev "$2"
    ns "$1" ip link set dev "$2" up
    ns "$1" ip route add "$6" dev "$2"
}
tunneli gwa "${LABRA}a" 10.255.0.1/30 gwb 198.51.100.2 10.2.0.0/24
tunneli gwb "${LABRA}b" 10.255.0.2/30 gwa 198.51.100.1 10.1.0.0/24
# @loppu tunneli

tavoittaa ha 10.2.0.10
# @alku tila
# Sallitut osoitteet (allowed-ips) ovat samalla reititys- ja suodatus-
# sääntö: vastapäältä hyväksytään vain sen verkon lähdeosoitteet.
ns gwa wg show "${LABRA}a" allowed-ips | cut -f2
if ns gwa wg show "${LABRA}a" latest-handshakes | awk '{exit !($2 > 0)}'
then echo "kättely tehty"; fi
# @loppu tila
