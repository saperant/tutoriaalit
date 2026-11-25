# shellcheck shell=bash
# Esimerkkien yhteiset asetukset. Jokainen aja.sh lukee tämän.
set -euo pipefail
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

# Valmistajan tuotteet: flash-kuvat, päivityspaketti ja vertailuun
# ELF-tiedostot (ks. laite/Makefile). testaa.sh rakentaa ne.
# shellcheck disable=SC2034  # käytetään aja.sh-skripteissä
LAITE=../laite

# otsikko TEKSTI: tulosteen väliotsikko
otsikko() { printf '== %s\n' "$*"; }

# sana TIEDOSTO SIIRTYMÄ: 32-bittinen luku (little endian) desimaalina
sana() { od -An -tu4 -j "$(($2))" -N4 "$1" | tr -d ' '; }

# @alku qemu
# qemu KUVA: ajaa koko laitteen QEMU:ssa (mps2-an385). Sarjaportti on
# vakiosyöte ja -tuloste. -icount tekee ajosta käsky käskyltä
# toistettavan. Lopuksi tulostetaan paluuarvo (semihosting). Jos ajo
# lukittuu, QEMU tulostaa "fatal" ja rekisterivedoksen; vedos jätetään
# pois ja tulostetaan "paluuarvo lukittui".
qemu() {
    local tuloste koodi=0
    tuloste=$(timeout 60 qemu-system-arm -M mps2-an385 -nographic \
        -monitor none -serial stdio \
        -semihosting-config enable=on,target=native \
        -icount shift=3,align=off,sleep=off \
        -device loader,file="$1",addr=0 2>&1) || koodi=$?
    printf '%s\n' "$tuloste" |
        grep -vE '^(qemu|timeout|R[0-9]| *$|XPSR|FPSCR)'
    if printf '%s' "$tuloste" | grep -q fatal; then
        echo "paluuarvo lukittui"
    else
        echo "paluuarvo $koodi"
    fi
}

# qemu_raw KUVA: kuten qemu, mutta tuloste menee suoraan ja
# muokkaamatta (binääriturvallinen, esim. sarjaliikenteen tallennukseen).
qemu_raw() {
    timeout 60 qemu-system-arm -M mps2-an385 -nographic -monitor none \
        -serial stdio -semihosting-config enable=on,target=native \
        -icount shift=3,align=off,sleep=off \
        -device loader,file="$1",addr=0 2>/dev/null
}
# @loppu qemu

# @alku r2arm
# r2arm KUVA KANTA KOMENNOT: radare2 eräajona raa'alle Thumb-koodille,
# joka on ladattu osoitteeseen KANTA.
r2arm() {
    command r2 -q -a arm -b 16 -m "$2" -e scr.color=0 -e scr.utf8=false \
        -e asm.bytes=false -e asm.cpu=cortex -e scr.interactive=false \
        -c "$3" "$1" 2> /dev/null | sed -E 's/ {3,};/  ;/; s/ +$//'
}
# @loppu r2arm
