#!/usr/bin/env bash
# Sama sovellus ELF-, raaka-, Intel HEX- ja S-record-muodossa sekä
# muotojen tunnistus.
source ./yhteinen.sh

# @alku muunnos
elf=$LAITE/sovellus.elf
arm-none-eabi-objcopy -O binary "$elf" sovellus.bin
arm-none-eabi-objcopy -O ihex "$elf" sovellus.hex
arm-none-eabi-objcopy -O srec "$elf" sovellus.srec
# @loppu muunnos
otsikko "koot tavuina"
wc -c sovellus.bin sovellus.hex sovellus.srec |
    awk '$2 != "total" { sub(".*/", "", $2); print $2, $1 }'
otsikko "tunnistus"
# @alku tunnistus
python3 tunnista.py "$elf" sovellus.bin sovellus.hex sovellus.srec \
    "$LAITE/lt100-2.4.1.lt1" "$LAITE/flash.bin"
# @loppu tunnistus
otsikko "Intel HEX: alku ja loppu"
# objcopyn HEX- ja S-record-tulosteessa on CRLF-rivinvaihdot; tr poistaa
# CR:n, jotta tuloste on deterministinen riippumatta siitä, miten
# tiedosto on tallennettu.
# @alku hex
head -3 sovellus.hex | tr -d '\r'
tail -2 sovellus.hex | tr -d '\r'
python3 ihex.py sovellus.hex
# @loppu hex
otsikko "S-record: alku ja loppu"
# @alku srec
head -2 sovellus.srec | tr -d '\r'
tail -1 sovellus.srec | tr -d '\r'
# @loppu srec
