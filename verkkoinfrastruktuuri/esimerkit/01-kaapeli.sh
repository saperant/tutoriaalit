#!/usr/bin/env bash
# Kaksi isäntää samassa aliverkossa: pienin mahdollinen laboratorio.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

# @alku verkko
solmu h1
solmu h2
linkki h1 eth0 h2 eth0
ns h1 ip addr add 192.0.2.11/24 dev eth0
ns h2 ip addr add 192.0.2.12/24 dev eth0
# @loppu verkko

tavoittaa h1 192.0.2.12
# Naapurin MAC-osoite opittiin ARPilla.
ns h1 ip -4 neigh show dev eth0 | cut -d' ' -f1-3
