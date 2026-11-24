#!/usr/bin/env bash
# Reitittimen valvonta SNMPv3:lla: käyttäjäkohtainen todennus ja salaus.
# Yhteisönimellä (SNMPv1/v2c) kysely ei onnistu.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

solmu reititin
solmu valvonta
linkki valvonta eth0 reititin hallinta
ns valvonta ip addr add 10.99.0.5/24 dev eth0
ns reititin ip addr add 10.99.0.1/24 dev hallinta

# @alku agentti
cat > "$LABRA_HAK/snmpd.conf" <<'KONF'
# Kuunnellaan vain hallintaverkossa.
agentAddress udp:10.99.0.1:161
sysName reititin-1
sysLocation Konesali A, kaappi 4
# SNMPv3-käyttäjä: SHA-256-todennus ja AES-salaus, vain luku.
createUser valvonta SHA-256 "Valvonta-Todennus-1" AES "Valvonta-Salaus-1"
rouser valvonta priv
KONF
ns reititin env SNMP_PERSISTENT_DIR="$LABRA_HAK" snmpd -f -Lo -C \
    -c "$LABRA_HAK/snmpd.conf" > /dev/null 2>&1 &
# @loppu agentti
kuuntelee() { ns reititin ss -lun | grep -q '10.99.0.1:161 '; }
odota 10 kuuntelee

# @alku kysely
V3=(-v3 -l authPriv -u valvonta -a SHA-256 -A Valvonta-Todennus-1
    -x AES -X Valvonta-Salaus-1 -t 2 -r 1)
SYS=.1.3.6.1.2.1.1       # system-ryhmä: 5 = nimi, 6 = sijainti
IFDESCR=.1.3.6.1.2.1.2.2.1.2
snmp() {   # snmp KOMENTO ARGUMENTIT...: tulostaa pelkät arvot
    ns valvonta env SNMP_PERSISTENT_DIR="$LABRA_HAK/asiakas" \
        "$@" -Oqv 2>&1 | tr -d '"'
}
mkdir -p "$LABRA_HAK/asiakas/cert_indexes"
snmp snmpget "${V3[@]}" 10.99.0.1 "$SYS.5.0" "$SYS.6.0"
echo "liitännät:"
snmp snmpwalk "${V3[@]}" 10.99.0.1 "$IFDESCR"
echo "v2c ja yhteisönimi public:"
snmp snmpget -v2c -c public -t 1 -r 0 10.99.0.1 "$SYS.5.0" || true
# @loppu kysely
