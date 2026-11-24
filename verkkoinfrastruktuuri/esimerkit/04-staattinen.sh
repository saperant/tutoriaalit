#!/usr/bin/env bash
# Kaksi toimipistettä ja niiden välinen yhteys staattisin reitein.
#   h1 (10.1.0.0/24) — r1 — 172.16.12.0/30 — r2 — h2 (10.2.0.0/24)
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

for s in h1 r1 r2 h2; do solmu "$s"; done
linkki h1 eth0 r1 lan
linkki r1 r2 r2 r1
linkki r2 lan h2 eth0

# @alku reitit
ns h1 ip addr add 10.1.0.10/24 dev eth0
ns h1 ip route add default via 10.1.0.1
ns r1 ip addr add 10.1.0.1/24 dev lan
ns r1 ip addr add 172.16.12.1/30 dev r2
ns r1 sysctl -qw net.ipv4.ip_forward=1
ns r1 ip route add 10.2.0.0/24 via 172.16.12.2

ns r2 ip addr add 10.2.0.1/24 dev lan
ns r2 ip addr add 172.16.12.2/30 dev r1
ns r2 sysctl -qw net.ipv4.ip_forward=1
ns r2 ip route add 10.1.0.0/24 via 172.16.12.1
ns h2 ip addr add 10.2.0.10/24 dev eth0
ns h2 ip route add default via 10.2.0.1
# @loppu reitit

tavoittaa h1 10.2.0.10
# @alku haku
# Mitä reittiä r1 käyttää? Reititystaulusta valitaan pisin vastaava
# etuliite.
reitti() {
    ns "$1" ip route get "$2" 2>&1 | head -1 | sed 's/ *uid .*//' || true
}
reitti r1 10.2.0.10
reitti r1 192.0.2.1
# @loppu haku
