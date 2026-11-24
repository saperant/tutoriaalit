#!/usr/bin/env bash
# dnsmasq jakaa lähiverkolle osoitteet, nimipalvelun ja verkkokäynnistyksen
# (PXE) tiedot. Asiakkaana on busyboxin udhcpc ja tftp.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

solmu reititin
solmu asiakas
solmu tulostin
solmu kytkin
ns kytkin ip link add br0 type bridge
ns kytkin ip link set dev br0 up
for s in reititin asiakas tulostin; do
    linkki "$s" eth0 kytkin "$s"
    ns kytkin ip link set dev "$s" master br0
done
ns reititin ip addr add 10.40.0.1/24 dev eth0

# @alku dnsmasq
mkdir -p "$LABRA_HAK/tftp"
echo "käynnistyslataimen sisältö" > "$LABRA_HAK/tftp/ipxe.efi"
cat > "$LABRA_HAK/dnsmasq.conf" <<KONF
interface=eth0
bind-interfaces
domain=toimisto.lan
# Dynaaminen alue ja vuokra-aika
dhcp-range=10.40.0.100,10.40.0.199,255.255.255.0,12h
dhcp-option=option:router,10.40.0.1
dhcp-option=option:dns-server,10.40.0.1
# Kiinteä varaus tulostimelle MAC-osoitteen perusteella
dhcp-host=02:00:00:00:03:01,tulostin,10.40.0.20
# Verkkokäynnistys: käynnistystiedosto TFTP:llä
dhcp-boot=ipxe.efi
enable-tftp
tftp-root=$LABRA_HAK/tftp
# Nimipalvelu: paikalliset nimet, ei kyselyitä eteenpäin
no-resolv
local=/toimisto.lan/
address=/nas.toimisto.lan/10.40.0.30
dhcp-leasefile=$LABRA_HAK/vuokrat
KONF
ns reititin dnsmasq -C "$LABRA_HAK/dnsmasq.conf" \
    -x "$LABRA_HAK/dnsmasq.pid" --user=root
# @loppu dnsmasq

# @alku asiakas
# udhcpc ajaa skriptin, jolle tarjouksen tiedot välitetään muuttujina.
cat > "$LABRA_HAK/dhcp-skripti" <<'SKRIPTI'
#!/bin/sh
[ "$1" = bound ] || exit 0
ip addr add "$ip/$mask" dev "$interface"
echo "osoite $ip/$mask, yhdyskäytävä $router, nimipalvelin $dns"
echo "verkkotunnus $domain, vuokra $lease s"
echo "käynnistys: palvelin $siaddr, tiedosto $boot_file"
SKRIPTI
chmod +x "$LABRA_HAK/dhcp-skripti"
hae() {   # hae SOLMU: pyytää osoitteen kerran ja lopettaa
    ns "$1" busybox udhcpc -i eth0 -q -n -f -t 5 -T 1 \
        -s "$LABRA_HAK/dhcp-skripti" 2> /dev/null
}
# @loppu asiakas
echo "asiakas:"
hae asiakas
echo "tulostin:"
hae tulostin | head -1

# @alku pxe
ns asiakas busybox tftp -g -r ipxe.efi -l "$LABRA_HAK/ladattu" \
    10.40.0.1 > /dev/null 2>&1
cat "$LABRA_HAK/ladattu"
# @loppu pxe

# @alku nimet
for nimi in nas.toimisto.lan tulostin.toimisto.lan; do
    echo "$nimi: $(ns asiakas dig +short @10.40.0.1 "$nimi")"
done
# @loppu nimet
