#!/usr/bin/env bash
# Ensimmäinen löydös: AddressSanitizer havaitsee ylivuodon.
source ./yhteinen.sh

# @alku kaanna
"$CC" "${VAROITUKSET[@]}" "${SANITOIJAT[@]}" vieraskirja.c -o vieraskirja
# @loppu kaanna
otsikko "tavallinen syöte"
printf 'Aino\nVeikko\nAino\n' | ./vieraskirja
otsikko "pitkä nimi"
# @alku pitka
printf 'Aino\nMaria-Kristiina Virtanen\n' > pitka.txt
kaatuu ./vieraskirja < pitka.txt
# @loppu pitka
otsikko "korjattu versio"
"$CC" "${VAROITUKSET[@]}" "${SANITOIJAT[@]}" -DKORJATTU vieraskirja.c \
    -o korjattu
./korjattu < pitka.txt
