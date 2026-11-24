#!/usr/bin/env bash
# Thumb-2-koodin lukeminen: Reset_Handler, literaalivarannot ja
# AAPCS-kutsu, Capstonella ja radare2:lla.
source ./yhteinen.sh
vedos=$LAITE/flash.bin

otsikko "sovelluksen Reset_Handler (vektori 1: 0x10181)"
# @alku reset
python3 pura.py "$vedos" 0 0x10180 18
# @loppu reset
otsikko "literaalivaranto Reset_Handlerin perässä"
# @alku varanto
python3 sanat.py "$vedos" 0x101b0 0x101c4
# @loppu varanto
otsikko "radare2: funktio 0x104fc"
# @alku r2
r2arm "$vedos" 0 'af @ 0x104fc; pdf @ 0x104fc'
# @loppu r2
otsikko "kutsuttu funktio 0x109c0: alku"
# @alku kutsuttu
python3 pura.py "$vedos" 0 0x109c0 8
# @loppu kutsuttu
