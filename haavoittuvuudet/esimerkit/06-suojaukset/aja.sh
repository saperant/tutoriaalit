#!/usr/bin/env bash
# Kääntäjän ja käyttöjärjestelmän suojaukset: tarkistus ja laukeaminen.
source ./yhteinen.sh

otsikko "suojausten tarkistus"
# @alku liput
HEIKKO=(-O0 -fno-stack-protector -fcf-protection=none -U_FORTIFY_SOURCE
        -fno-pie -no-pie "-Wl,-z,norelro" "-Wl,-z,execstack")
VAHVA=(-O2 -D_FORTIFY_SOURCE=3 -fstack-protector-strong
       -fcf-protection=full -fPIE -pie "-Wl,-z,relro,-z,now")
"$CC" -std=c23 "${HEIKKO[@]}" palvelu.c -o heikko 2> /dev/null
"$CC" -std=c23 palvelu.c -o oletus
"$CC" -std=c23 "${VAHVA[@]}" palvelu.c -o vahva
python3 tarkista.py heikko oletus vahva
# @loppu liput

otsikko "ASLR"
"$CC" -std=c23 -O2 -fPIE -pie osoitteet.c -o osoitteet-pie
"$CC" -std=c23 -O2 -fno-pie -no-pie osoitteet.c -o osoitteet-kiintea
# @alku aslr
# vertaa OHJELMA [ETULIITE...]: ajaa ohjelman kolmesti ja kertoo, mitkä
# osoitteet vaihtuvat ajosta toiseen
vertaa() {
    # shellcheck disable=SC2016  # awk-ohjelma
    local tapa='{ n[$1]++ } END { for (k in n) print k, n[k] }'
    for _ in 1 2 3; do "$@"; done | sort -u | awk "$tapa" | sort |
        while read -r alue maara; do
            if ((maara > 1)); then tulos=vaihtelee; else tulos=kiinteä; fi
            echo "  $alue: $tulos"
        done
}
echo "PIE-ohjelma:"
vertaa ./osoitteet-pie
echo "kiinteäosoitteinen ohjelma:"
vertaa ./osoitteet-kiintea
# @loppu aslr

otsikko "NX"
# @alku nx
"$CC" -std=c23 -O0 nx.c -o nx
"$CC" -std=c23 -O0 -Wl,-z,execstack nx.c -o nx-suoritettava 2> /dev/null
kaatuu ./nx
./nx-suoritettava
# @loppu nx

otsikko "FORTIFY_SOURCE"
# @alku fortify
"$CC" -std=c23 -O2 -D_FORTIFY_SOURCE=2 fortify.c -o fortify
./fortify aino
kaatuu ./fortify tunnus-on-liian-pitka
# @loppu fortify
