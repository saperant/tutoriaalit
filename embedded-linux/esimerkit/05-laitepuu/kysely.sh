#!/bin/sh
# Lukee käännetystä laitepuusta (DTB) valitut ominaisuudet fdtgetillä.
# Tyyppi s on merkkijono ja x 32-bittisiä soluja heksadesimaaleina.
#
# Käyttö: kysely.sh virt.dtb
set -eu
dtb=$1
# @alku kyselyt
while read -r tyyppi solmu ominaisuus; do
    printf '%-16s %-18s ' "$solmu" "$ominaisuus"
    fdtget -t "$tyyppi" "$dtb" "$solmu" "$ominaisuus"
done <<'LOPPU'
s /                model
x /                #address-cells
x /                interrupt-parent
x /intc@8000000    phandle
x /intc@8000000    #interrupt-cells
s /pl011@9000000   compatible
x /pl011@9000000   reg
x /pl011@9000000   interrupts
x /memory@40000000 reg
s /chosen          stdout-path
LOPPU
# @loppu kyselyt
echo "juuren alisolmuja: $(fdtget -l "$dtb" / | wc -l)"
