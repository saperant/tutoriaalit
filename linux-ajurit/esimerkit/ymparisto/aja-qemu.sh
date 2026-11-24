#!/bin/sh
# Käynnistää ARM64-järjestelmän QEMU:n virt-koneessa ja palauttaa QEMU:n
# paluuarvon. Konsoli on sarjaportti, joka ohjataan vakiotulosteeseen.
#
# Käyttö: aja-qemu.sh [valitsimet] [-- QEMU:n omat valitsimet]
#   -k Image      ydin (suora käynnistys ilman käynnistintä)
#   -i initrd     initramfs-arkisto
#   -a "rivi"     ytimen komentorivi
#   -d dtb        oma laitepuu QEMU:n generoiman sijaan
#   -l levy.img   virtio-levy (/dev/vda), vain luku
#   -b u-boot.bin käynnistin (firmware) ytimen sijaan
#   -t sekunnit   aikaraja (oletus 60)
#
# Kone on aina sama: -M virt -cpu cortex-a53 -m 256 -smp 1. Laitepuun
# purku (dumpdtb) on tehtävä samoilla arvoilla.

set -eu
# @alku kone
KONE="-M virt -cpu cortex-a53 -m 256 -smp 1"
# @loppu kone
aikaraja=60
valinnat=""
while [ $# -gt 0 ]; do
    case $1 in
        --) shift; break ;;
        -k) valinnat="$valinnat -kernel $2" ;;
        -i) valinnat="$valinnat -initrd $2" ;;
        -d) valinnat="$valinnat -dtb $2" ;;
        -b) valinnat="$valinnat -bios $2" ;;
        -l) levy="if=none,format=raw,readonly=on,id=levy,file=$2"
            valinnat="$valinnat -drive $levy"
            valinnat="$valinnat -device virtio-blk-device,drive=levy" ;;
        -a) komentorivi=$2 ;;
        -t) aikaraja=$2 ;;
        *) echo "aja-qemu.sh: tuntematon valitsin $1" >&2; exit 2 ;;
    esac
    shift 2
done
# @alku ajo
# -no-reboot: ytimen uudelleenkäynnistys (myös paniikki, panic=-1)
# päättää QEMU:n. Sammutus (PSCI SYSTEM_OFF) päättää sen paluuarvolla 0.
# shellcheck disable=SC2086
exec timeout --foreground "$aikaraja" qemu-system-aarch64 $KONE \
    -nographic -monitor none -serial stdio -no-reboot -nic none \
    $valinnat ${komentorivi+-append "$komentorivi"} "$@"
# @loppu ajo
