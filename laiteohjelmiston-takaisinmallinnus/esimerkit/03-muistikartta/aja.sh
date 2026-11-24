#!/usr/bin/env bash
# Flash-vedoksen muistikartta: käytetyt alueet, vektoritaulut,
# latausosoitteen päättely ja oheislaiteviittaukset.
source ./yhteinen.sh
vedos=$LAITE/flash.bin

otsikko "käytetyt alueet (ei 0xFF)"
# @alku alueet
python3 alueet.py "$vedos"
# @loppu alueet
otsikko "vektoritaulu osoitteessa 0"
# @alku boot
python3 vektorit.py "$vedos" 0 0
# @loppu boot
otsikko "otsake 0x10000 ja vektoritaulu 0x10100"
# @alku sovellus
python3 heksa.py "$vedos" 0x10000 24
python3 vektorit.py "$vedos" 0 0x10100 32 | sed -n '1,4p;/eri/,$p'
# @loppu sovellus
otsikko "päivityspaketin sovellus: latausosoite"
# @alku kanta
python3 lt1.py pura "$LAITE/lt100-2.4.1.lt1" osat
python3 kanta.py osat/osio0.bin
# @loppu kanta
otsikko "oheislaitteet ja RAM: sovellus"
# @alku oheis
loppu=$((0x10100 + $(sana "$vedos" 0x1000c)))
python3 oheislaitteet.py "$vedos" 0 0x10100 "$loppu" mps2.svd
# @loppu oheis
otsikko "oheislaitteet ja RAM: käynnistyslatain"
# @alku boot-oheis
boot_loppu=$(python3 alueet.py "$vedos" | head -1 | cut -c10-16)
python3 oheislaitteet.py "$vedos" 0 0 "$boot_loppu" mps2.svd
# @loppu boot-oheis
