#!/usr/bin/env bash
# 802.1X:n taustajärjestelmä: tukiasema tai kytkin (NAS) kysyy RADIUS-
# palvelimelta, saako käyttäjä verkkoon, ja vastauksessa tulee käyttäjän
# VLAN. NAS:ia jäljittelee radtest.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

solmu nas
solmu radius
linkki nas eth0 radius eth0
ns nas ip addr add 10.70.0.2/24 dev eth0
ns radius ip addr add 10.70.0.10/24 dev eth0

R=$LABRA_HAK
# FreeRADIUSin oma $INCLUDE-direktiivi (ei kuoren muuttuja).
# shellcheck disable=SC2016
echo '$INCLUDE /usr/share/freeradius/dictionary' > "$R/dictionary"
# @alku kayttajat
cat > "$R/kayttajat" <<'KAYTTAJAT'
liisa   Cleartext-Password := "Kesa-2026"
        Tunnel-Type = VLAN,
        Tunnel-Medium-Type = IEEE-802,
        Tunnel-Private-Group-Id = "20"
vieras  Cleartext-Password := "Tervetuloa"
        Tunnel-Type = VLAN,
        Tunnel-Medium-Type = IEEE-802,
        Tunnel-Private-Group-Id = "90"
KAYTTAJAT
# @loppu kayttajat

# @alku palvelin
cat > "$R/radiusd.conf" <<KONF
prefix = /usr
raddbdir = $R
confdir = $R
logdir = $R
run_dir = $R
db_dir = $R
libdir = /usr/lib/freeradius
pidfile = $R/radiusd.pid
name = freeradius
max_request_time = 30
cleanup_delay = 5
max_requests = 1024
hostname_lookups = no
log {
    destination = stdout
}
# Kytkimet ja tukiasemat, jotka saavat kysyä. Jaettu salaisuus ja
# Message-Authenticator suojaavat väärennetyiltä vastauksilta.
client kytkimet {
    ipaddr = 10.70.0.0/24
    secret = Jaettu-Salaisuus-Tamakin
    require_message_authenticator = yes
}
modules {
    files {
        filename = $R/kayttajat
    }
    pap {
    }
}
server default {
    listen {
        type = auth
        ipaddr = *
        port = 1812
    }
    authorize {
        files
        pap
    }
    authenticate {
        Auth-Type PAP {
            pap
        }
    }
    post-auth {
        # Hylkäykseen ei saa vuotaa valtuutustietoja.
        Post-Auth-Type REJECT {
            update reply {
                &Tunnel-Type !* ANY
                &Tunnel-Medium-Type !* ANY
                &Tunnel-Private-Group-Id !* ANY
            }
        }
    }
}
KONF
ns radius freeradius -f -d "$R" > "$R/radius.log" 2>&1 &
# @loppu palvelin
valmis() { grep -q 'Ready to process requests' "$R/radius.log"; }
if ! odota 30 valmis; then cat "$R/radius.log" >&2; exit 1; fi

# @alku kysely
# NAS:n osoite annetaan itse (viimeinen argumentti): oletuksena radtest
# selvittää sen koneen nimestä, eikä nimiavaruudessa ole nimipalvelua.
kysy() {   # kysy KÄYTTÄJÄ SALASANA
    echo "$1:"
    { ns nas radtest "$1" "$2" 10.70.0.10 0 Jaettu-Salaisuus-Tamakin \
        0 10.70.0.2 2> /dev/null || true; } |
        awk '/^Received/ {print "  " $2}
             /Tunnel-Private-Group-Id/ {gsub(/"/, ""); print "  VLAN " $3}'
}
kysy liisa Kesa-2026
kysy vieras Tervetuloa
kysy liisa arvaus
# @loppu kysely
# Vianetsintää varten: jos palvelin ei vastaa, radtestin tuloste ja
# palvelimen loki tulostetaan, jolloin ne näkyvät testin erotuksessa.
if ! ns nas radtest liisa Kesa-2026 10.70.0.10 0 Jaettu-Salaisuus-Tamakin \
        0 10.70.0.2 > "$R/radtest.log" 2>&1 ||
        ! grep -q '^Received' "$R/radtest.log"; then
    echo "--- radtest"; cat "$R/radtest.log"
    echo "--- radius.log"; cat "$R/radius.log"
fi
