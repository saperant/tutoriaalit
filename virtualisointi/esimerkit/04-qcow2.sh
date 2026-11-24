#!/usr/bin/env bash
# qcow2-levykuvat: kopioi kirjoitettaessa (copy-on-write) -kerrokset ja
# sisäiset tilannevedokset. Yksi peruskuva voi palvella monta konetta.
set -euo pipefail
export LC_ALL=C
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT
cd "$tyo"

# @alku kerrokset
# Peruskuva (esim. asennettu käyttöjärjestelmä) ja sen päälle kerros.
qemu-img create -q -f qcow2 perus.qcow2 64M
qemu-io -c "write -P 0xaa 0 1M" perus.qcow2 > /dev/null
qemu-img create -q -f qcow2 -b perus.qcow2 -F qcow2 kone1.qcow2
qemu-io -c "write -P 0xbb 1M 1M" kone1.qcow2 > /dev/null

# Kerroksessa on vain muuttunut data; lukeminen kulkee peruskuvaan asti.
qemu-img info --backing-chain kone1.qcow2 | grep -E '^(image|backing file):'
qemu-img map -f qcow2 kone1.qcow2 |
    awk 'NR > 1 { print "  alkaen", $1 ", pituus", $2 ": tiedostossa", $4 }'
qemu-io -c "read -P 0xaa 0 1M" -c "read -P 0xbb 1M 1M" kone1.qcow2 |
    grep -c 'read 1048576' | sed 's/^/onnistuneita lukuja: /'
# @loppu kerrokset

# @alku vedokset
# Sisäinen tilannevedos tallentaa levyn tilan kuvatiedoston sisään.
qemu-img snapshot -c ennen-paivitysta kone1.qcow2
qemu-io -c "write -P 0xcc 0 1M" kone1.qcow2 > /dev/null
qemu-img snapshot -l kone1.qcow2 | awk 'NR > 2 { print "vedos:", $2 }'
qemu-img snapshot -a ennen-paivitysta kone1.qcow2
qemu-io -c "read -P 0xaa 0 1M" kone1.qcow2 | grep -q 'read 1048576' &&
    echo "palautettu: alku on taas peruskuvan dataa"
# @loppu vedokset

# @alku yhdista
# Kerroksen muutokset yhdistetään peruskuvaan (commit).
qemu-img commit -q kone1.qcow2
qemu-io -c "read -P 0xbb 1M 1M" perus.qcow2 | grep -q 'read 1048576' &&
    echo "commit: kerroksen data on nyt peruskuvassa"
# @loppu yhdista
