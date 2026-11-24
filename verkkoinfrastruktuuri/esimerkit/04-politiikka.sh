#!/usr/bin/env bash
# Politiikkareititys: toimiston liikenne kulkee kuituyhteyttä pitkin ja
# vierasverkon liikenne 4G-yhteyttä pitkin, vaikka kohde on sama.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

for s in r kuitu mobiili; do solmu "$s"; done
linkki r kuitu kuitu r
linkki r mobiili mobiili r
ns r ip addr add 100.64.1.2/30 dev kuitu
ns r ip addr add 100.64.2.2/30 dev mobiili
ns kuitu ip addr add 100.64.1.1/30 dev r
ns mobiili ip addr add 100.64.2.1/30 dev r
# Lähiverkot sillan päällä: toimisto 10.20.0.0/24, vieraat 10.30.0.0/24
ns r ip link add lan type bridge
ns r ip link set dev lan up
ns r ip addr add 10.20.0.1/24 dev lan
ns r ip addr add 10.30.0.1/24 dev lan

# @alku politiikka
# Päätaulun oletusreitti: kuitu.
ns r ip route add default via 100.64.1.1
# Oma taulu 100 vierasverkolle: oletusreitti 4G:n kautta.
ns r ip route add default via 100.64.2.1 table 100
# Sääntö: vierasverkosta lähtevä liikenne käyttää taulua 100.
ns r ip rule add from 10.30.0.0/24 lookup 100 priority 1000
# @loppu politiikka

# @alku tarkistus
ns r ip rule show | grep -v -e local -e default
for lahde in 10.20.0.1 10.30.0.1; do
    ns r ip route get 192.0.2.1 from "$lahde" |
        awk -v l="$lahde" 'NR == 1 {print l, "via", $5}'
done
# @loppu tarkistus
