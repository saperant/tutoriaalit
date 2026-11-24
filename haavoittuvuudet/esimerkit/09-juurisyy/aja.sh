#!/usr/bin/env bash
# Juurisyyanalyysi: kaatumiskohdasta juurisyyhyn, korjaus, regressiotesti
# ja samanlaisten virheiden etsintä muualta.
source ./yhteinen.sh

"$CC" "${VAROITUKSET[@]}" -fsanitize=address kuva.c -o kuva-asan
"$CC" "${VAROITUKSET[@]}" "${SANITOIJAT[@]}" kuva.c -o kuva-ubsan
"$CC" "${VAROITUKSET[@]}" "${SANITOIJAT[@]}" -DKORJATTU kuva.c \
    -o kuva-korjattu
echo 'P5 640 480 255' > tavallinen.pgm
echo 'P5 65536 65537 255' > ylisuuri.pgm

otsikko "AddressSanitizer: kaatumiskohta"
./kuva-asan < tavallinen.pgm
kaatuu ./kuva-asan < ylisuuri.pgm
otsikko "raakaraportti siistittynä"
# @alku raaka
python3 siisti.py < ajo.err | head -24
# @loppu raaka
otsikko "UndefinedBehaviorSanitizer: juurisyy"
kaatuu ./kuva-ubsan < ylisuuri.pgm

otsikko "regressiotestit korjatulle versiolle"
# @alku regressio
# tapaus NIMI OTSAKE ODOTUS: ajaa korjatun lukijan ja vertaa tulosta
tapaus() {
    local tulos
    if tulos=$(echo "$2" | ./kuva-korjattu 2>&1); then :; fi
    if [[ $tulos == *"$3"* ]]; then
        echo "ok    $1"
    else
        echo "VIRHE $1: $tulos"
        return 1
    fi
}
tapaus "tavallinen kuva" "P5 640 480 255" "luettu"
tapaus "kertolasku ylivuotaa" "P5 65536 65537 255" "hylätty"
tapaus "negatiivinen leveys" "P5 -640 480 255" "hylätty"
tapaus "nollakorkeus" "P5 640 0 255" "hylätty"
tapaus "yläraja ylittyy" "P5 2000000 1 255" "hylätty"
# @loppu regressio

otsikko "variaatioanalyysi: sama virhe muualla"
# @alku variantit
for tiedosto in koodi/*.c; do
    clang-tidy-20 --quiet "$tiedosto" -- -std=c23 2> /dev/null |
        python3 varoitukset.py | sed "s|^|${tiedosto#koodi/}: |"
done
# @loppu variantit
