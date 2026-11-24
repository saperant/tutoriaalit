#!/usr/bin/env bash
# x86-64-assemblyn lukeminen: kutsukonventio, pinokehys ja syntaksit.
source ./yhteinen.sh

# @alku kaanna
"$CC" -std=c17 -O1 -fno-inline -fno-omit-frame-pointer -Wall -Wextra \
    -Werror laske.c -o laske
./laske
# @loppu kaanna

otsikko "summa (-O0)"
# @alku o0
"$CC" -std=c17 -O0 -Wall -Wextra -Werror laske.c -o laske0
purku laske0 summa
# @loppu o0
otsikko "summa (-O1)"
purku laske summa
otsikko "painotettu: argumentit 7 ja 8 pinossa"
purku laske painotettu
otsikko "keskipiste: liukuluvut xmm-rekistereissä"
purku laske keskipiste
otsikko "suurin_numero: pinokehys ja kanarialintu"
# @alku kanarialintu
"$CC" -std=c17 -O1 -fno-inline -fstack-protector-strong -Wall -Wextra \
    -Werror laske.c -o suojattu
purku suojattu suurin_numero | grep -E 'fs:|sub +rsp|__stack_chk_fail'
# @loppu kanarialintu
otsikko "AT&T-syntaksi"
# @alku att
objdump -d --no-show-raw-insn --no-addresses --disassemble=summa laske |
    normalisoi | head -6
# @loppu att
