#!/usr/bin/env bash
# Funktioiden etsintä, kirjastofunktioiden allekirjoitukset ja
# algoritmien tunnistus vakioista.
source ./yhteinen.sh
vedos=$LAITE/flash.bin
# kanta, vektoritaulu ja koodin loppu (otsakkeen pituuskentästä)
sov=(0 0x10100 $((0x10100 + $(sana "$vedos" 0x1000c))))

otsikko "funktiot vektoritaulusta ja bl-kutsuista"
# @alku kutsut
python3 funktiot.py "$vedos" "${sov[@]}" --vain-kutsut | awk "NR==1"
# @loppu kutsut
otsikko "funktiot, kun mukana ovat myös funktio-osoittimet"
# @alku osoittimet
python3 funktiot.py "$vedos" "${sov[@]}"
# @loppu osoittimet
otsikko "allekirjoitukset viiteohjelmasta"
# @alku allekirjoitukset
arm-none-eabi-gcc -mcpu=cortex-m3 -mthumb -Os -std=c11 -Wall -Werror \
    viite.c --specs=nano.specs --specs=nosys.specs -nostartfiles \
    -Wl,-e,main -Wl,-Ttext=0 -Wl,--gc-sections -o viite.elf 2> /dev/null
python3 allekirjoitus.py tee viite.elf kirjasto.json
python3 allekirjoitus.py etsi kirjasto.json "$vedos" "${sov[@]}"
# @loppu allekirjoitukset
otsikko "tunnetut vakiot"
# @alku vakiot
python3 algoritmit.py "$vedos" "${sov[@]}"
# @loppu vakiot
otsikko "tarkistus symbolitaulusta"
# @alku vastaus
python3 vastaus.py "$LAITE/sovellus.elf" "$vedos" "${sov[@]}" \
    0x10c80=memset 0x10d20=memcpy 0x109fc=crc32 0x105ac=xtea_pura \
    0x10a5c=crc16_ccitt
# @loppu vastaus
