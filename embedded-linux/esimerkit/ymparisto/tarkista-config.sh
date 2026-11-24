#!/bin/sh
# Tarkistaa, että jokainen fragmenttien pyytämä asetus päätyi lopulliseen
# .config-tiedostoon. Kconfig hylkää asetuksen hiljaa, jos sen
# riippuvuudet eivät täyty, joten tämä on käännöksen ensimmäinen testi.
#
# Käyttö: tarkista-config.sh .config fragmentti...

set -eu
config=$1
shift
virheet=0
# @alku silmukka
for fragmentti in "$@"; do
    grep -E '^(CONFIG_[A-Z0-9_]+=|# CONFIG_[A-Z0-9_]+ is not set)' \
        "$fragmentti" | while IFS= read -r rivi; do
        if ! grep -qxF "$rivi" "$config"; then
            nimi=$(printf '%s\n' "$rivi" | grep -oE 'CONFIG_[A-Z0-9_]+')
            saatu=$(grep -E "^$nimi=|^# $nimi is not set" "$config" ||
                echo "puuttuu")
            echo "pyydetty: $rivi"
            echo "  saatu:  $saatu"
        fi
    done
done > "$config.erot"
# @loppu silmukka
if [ -s "$config.erot" ]; then
    echo "Kconfig ei ottanut kaikkia asetuksia:"
    cat "$config.erot"
    virheet=1
fi
rm -f "$config.erot"
exit "$virheet"
