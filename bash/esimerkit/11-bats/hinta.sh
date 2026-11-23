# Hinnoittelukirjasto. Rahamäärät käsitellään sentteinä, koska Bashin
# aritmetiikka on kokonaislukuaritmetiikkaa.
# shellcheck shell=bash

# @alku kirjasto
# euroiksi SENTIT -> "12,34"
euroiksi() {
    local s=$1 etumerkki=
    (( s < 0 )) && { etumerkki=-; s=$(( -s )); }
    printf '%s%d,%02d\n' "$etumerkki" $(( s / 100 )) $(( s % 100 ))
}

# senteiksi "12,34" | "12" -> 1234; virheellinen syöte palauttaa 1
senteiksi() {
    [[ $1 =~ ^([0-9]+)([.,]([0-9]{1,2}))?$ ]] || {
        printf 'virheellinen summa: %s\n' "$1" >&2
        return 1
    }
    local senttiosa=${BASH_REMATCH[3]:-0}
    (( ${#senttiosa} == 1 )) && senttiosa+=0
    echo $(( 10#${BASH_REMATCH[1]} * 100 + 10#$senttiosa ))
}

# alennus SENTIT PROSENTTI -> alennettu hinta pyöristettynä
alennus() {
    echo $(( ($1 * (100 - $2) + 50) / 100 ))
}
# @loppu kirjasto
