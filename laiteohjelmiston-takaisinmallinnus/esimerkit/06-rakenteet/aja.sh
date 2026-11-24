#!/usr/bin/env bash
# Rakenteet konekielessä: komento- ja tehtävätaulut sekä switch-lauseen
# hyppytaulu.
source ./yhteinen.sh
vedos=$LAITE/flash.bin
loppu=$((0x10100 + $(sana "$vedos" 0x1000c)))

otsikko "tietuetaulukot vektoritaulun jälkeen"
# @alku taulut
python3 taulut.py "$vedos" 0 0x10180 "$loppu"
# @loppu taulut
otsikko "hyppytaulut"
# @alku hyppy
python3 hyppytaulut.py "$vedos" 0 0x10100 "$loppu"
# @loppu hyppy
otsikko "tbb ja sitä edeltävä vertailu"
# @alku tbb
python3 pura.py "$vedos" 0 0x10852 8
python3 heksa.py "$vedos" 0x10866 6
# @loppu tbb
otsikko "nimeämisten tarkistus"
# @alku vastaus
python3 vastaus.py "$LAITE/sovellus.elf" "$vedos" 0 0x10100 "$loppu" \
    0x10294=k_ohje 0x10364=k_huolto 0x1030c=k_lue 0x10970=mittaa \
    0x10810=kasittele_kehys | tail -5
# @loppu vastaus
