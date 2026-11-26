#!/usr/bin/env bash
# Samat yksikkötiedostot ja sama palvelu oikean systemd:n alla.
# Ajetaan vain koneessa, jossa systemd on prosessi 1 ja pääkäyttäjän
# oikeudet saa ilman salasanaa (esim. CI-ajokone tai oma testikone).
# Koe asentaa yksiköt hakemistoon /run/systemd/system ja palvelun
# hakemistoon /opt/mittari ja poistaa ne lopuksi.
set -euo pipefail
export LC_ALL=C.UTF-8
taalla=$(cd "$(dirname "$0")" && pwd)

if [[ $(cat /proc/1/comm) != systemd ]]; then
    echo "OHITETTU: systemd ei ole prosessi 1"
    exit 0
fi
if (( EUID != 0 )); then
    if ! sudo -n true 2> /dev/null; then
        echo "OHITETTU: pääkäyttäjän oikeuksia ei saa ilman salasanaa"
        exit 0
    fi
    exec sudo -n bash "$0" "$@"
fi

yksikot=$taalla/../07-yksikot/yksikot
ajo=/run/systemd/system

siivoa() {
    systemctl stop mittari.socket mittari.service \
        vaatii.service toivoo.service kaatuva.service 2> /dev/null || true
    rm -rf "$ajo"/mittari.service "$ajo"/mittari.socket \
        "$ajo"/mittari.service.d "$ajo"/vaatii.service \
        "$ajo"/toivoo.service "$ajo"/kaatuva.service \
        "$ajo"/esiehto.service /opt/mittari /var/lib/private/mittari
    systemctl daemon-reload
    systemctl reset-failed mittari.service mittari.socket vaatii.service \
        toivoo.service kaatuva.service esiehto.service 2> /dev/null || true
}
trap siivoa EXIT
siivoa

# kysy KOMENTO: yksi pyyntö palvelulle
kysy() {
    local vastaus
    exec 3<> /dev/tcp/127.0.0.1/9108
    echo "$1" >&3
    read -r -t 60 vastaus <&3
    exec 3>&-
    echo "$vastaus"
}

# tila YKSIKKÖ: active, inactive, failed ...
tila() { systemctl is-active "$1" || true; }

# odota YKSIKKÖ TILA UUDELLEENKÄYNNISTYKSIÄ: enintään 60 s
odota() {
    local i
    for (( i = 0; i < 600; i++ )); do
        [[ $(systemctl show "$1" -p NRestarts --value) == "$3" &&
           $(systemctl show "$1" -p ActiveState --value) == "$2" ]] &&
            return 0
        sleep 0.1
    done
    echo "aikaraja: $1 ei päätynyt tilaan $2 ($3 käynnistystä)" >&2
    return 1
}

# @alku asennus
install -D -m 0644 "$taalla/../07-palvelu/mittari.py" /opt/mittari/mittari.py
cp -r "$yksikot"/mittari.service "$yksikot"/mittari.socket \
    "$yksikot"/mittari.service.d "$ajo"/
systemctl daemon-reload
# @loppu asennus

# @alku aktivointi
echo "== sokettiaktivointi"
systemctl start mittari.socket
echo "soketti $(tila mittari.socket), palvelu $(tila mittari.service)"
echo "asiakas sai: $(kysy tila)"
echo "soketti $(tila mittari.socket), palvelu $(tila mittari.service)"
systemctl show mittari.service -p Type -p StatusText -p NRestarts
# @loppu aktivointi

# @alku kovennus
echo "== kovennus palvelun sisältä"
kysy ymparisto
systemctl show mittari.service -p MemoryMax -p TasksMax \
    -p CPUQuotaPerSecUSec
# @loppu kovennus

# @alku loki
echo "== loki"
kysy tilaa > /dev/null
ajokerta=$(systemctl show mittari.service -p InvocationID --value)
systemctl stop mittari.service 2> /dev/null
journalctl --sync
journalctl _SYSTEMD_INVOCATION_ID="$ajokerta" -o json --no-pager |
    python3 -c '
import json, sys
for rivi in sys.stdin:
    t = json.loads(rivi)
    if t.get("_COMM", "").startswith("python"):
        print("PRIORITY=" + t["PRIORITY"], "MESSAGE=" + t["MESSAGE"])'
# @loppu loki

# @alku raja
echo "== kaatuva palvelu ja käynnistysraja"
cat > "$ajo"/kaatuva.service << 'LOPPU'
[Unit]
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
ExecStart=/bin/false
Restart=on-failure
RestartSec=100ms
LOPPU
systemctl daemon-reload
systemctl start kaatuva.service
odota kaatuva.service failed 3
systemctl show kaatuva.service -p ActiveState -p Result -p NRestarts
journalctl --sync
journalctl -u kaatuva.service -o cat --no-pager |
    awk '/too quickly/ && !n++ { print "lokissa: " $0 }'
# @loppu raja

# @alku riippuvuus
echo "== Requires ja Wants, kun riippuvuus ei käynnisty"
cat > "$ajo"/esiehto.service << 'LOPPU'
[Service]
Type=oneshot
ExecStart=/bin/false
LOPPU
for laji in Requires Wants; do
    nimi=$([[ $laji == Requires ]] && echo vaatii || echo toivoo)
    cat > "$ajo/$nimi.service" << LOPPU
[Unit]
$laji=esiehto.service
After=esiehto.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/true
LOPPU
done
systemctl daemon-reload
for nimi in vaatii toivoo; do
    koodi=0
    systemctl start "$nimi.service" 2> /dev/null || koodi=$?
    echo "$nimi.service: systemctl start palautti $koodi," \
        "tila $(tila "$nimi.service")"
done
# @loppu riippuvuus
