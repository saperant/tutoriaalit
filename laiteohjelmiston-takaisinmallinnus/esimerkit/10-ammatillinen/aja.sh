#!/usr/bin/env bash
# Ammatillisia kayttotapauksia: suorituskykyregression paikannus
# binaarista, rikkoutuneen kaannoksen tunnistus ja oman laitteen
# tietoturva-auditointi.
source ./yhteinen.sh

otsikko "suodatusfunktion prologi: 2.4.1 vs 2.4.0"
# @alku prologi
python3 prologi.py "$LAITE/flash.bin" 0 0x105f8
python3 prologi.py "$LAITE/flash-240.bin" 0 0x105f8
# @loppu prologi
otsikko "kaskymaara emuloimalla"
# @alku mittaa
python3 mittaa.py "$LAITE/flash.bin" "$LAITE/flash-240.bin" 0x105f8
# @loppu mittaa

otsikko "rikkoutunut kaannos: vektoritaulu puuttuu"
# @alku rikki
# sovellus-rikki.ld unohti KEEP(.vektorit), joten linkkeri karsi
# vektoritaulun pois (--gc-sections). Sovellus ei kaynnisty.
python3 vektorit.py "$LAITE/flash-rikki.bin" 0 0x10100 4
echo "QEMU:"
printf 'versio\nsammuta\n' | qemu "$LAITE/flash-rikki.bin"
# @loppu rikki

otsikko "tietoturva-auditointi: lokin siirron NIMI-kehys"
# @alku audit
# kasittele_kehys kopioi NIMI-kehyksen datan 16 tavun pinopuskuriin
# tarkistamatta pituutta (korjattu vain versiossa 2.4.2). Liian pitka
# nimi ylittaa puskurin; pinon suojaus (kanari) havaitsee sen.
pitka=$(python3 -c "print('41' * 24)")
kehys=$(python3 kehys.py 2 "$pitka")
printf 'kehys %s\nsammuta\n' "$kehys" | qemu "$LAITE/flash.bin" |
    grep -i "vika\|sammut\|kehys"
# @loppu audit
otsikko "tietoturva-auditointi: allekirjoittamaton paivitys"
# @alku allekirjoitus
# Otsakkeen allekirjoituskentta on 0: kuva ei ole allekirjoitettu.
# Kaynnistyslatain 1.2 hyvaksyy sen (tarkistaa vain CRC:n). Korjattu
# kaynnistyslatain (-DKORJATTU) hylkaa allekirjoittamattoman kuvan.
echo "otsakkeen allekirjoituskentta (0x10014):"
python3 sanat.py "$LAITE/flash.bin" 0x10014 0x10018
echo "nykyinen kaynnistyslatain:"
printf 'sammuta\n' | qemu "$LAITE/flash.bin"
echo "korjattu kaynnistyslatain + allekirjoittamaton sovellus:"
printf 'sammuta\n' | qemu "$LAITE/flash-korjattu.bin"
# @loppu allekirjoitus
