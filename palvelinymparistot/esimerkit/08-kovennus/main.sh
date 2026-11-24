#!/usr/bin/env bash
# Tarkastuksen testi: rakennetaan kaksi järjestelmää, joista toinen on
# kovennettu, ja ajetaan tarkastus molemmille.
set -euo pipefail
export LC_ALL=C
cd "$(dirname "$0")"
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT

# @alku testi
rakenna() {  # rakenna <hakemisto> <kovennettu: 0/1>
    mkdir -p "$1/etc/ssh" "$1/etc/apt/apt.conf.d"
    if (( $2 )); then
        printf 'PermitRootLogin no\nPasswordAuthentication no\n' \
            > "$1/etc/ssh/sshd_config"
        echo 'MaxAuthTries 3' >> "$1/etc/ssh/sshd_config"
        echo 'APT::Periodic::Unattended-Upgrade "1";' \
            > "$1/etc/apt/apt.conf.d/20auto-upgrades"
        install -m 640 /dev/null "$1/etc/shadow"
    else
        printf 'PermitRootLogin yes\nMaxAuthTries 6\n' \
            > "$1/etc/ssh/sshd_config"
        touch "$1/etc/apt/apt.conf.d/20auto-upgrades"
        install -m 644 /dev/null "$1/etc/shadow"
        install -m 666 /dev/null "$1/etc/hosts"
    fi
}
rakenna "$tyo/vanha" 0
rakenna "$tyo/uusi" 1
for kone in vanha uusi; do
    echo "== $kone"
    if bash tarkastus.sh "$tyo/$kone"; then
        echo "tulos: hyväksytty"
    else
        echo "tulos: hylätty (paluuarvo $?)"
    fi
done
# @loppu testi
