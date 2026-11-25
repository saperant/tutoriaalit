#!/usr/bin/env bash
# Toistettava rakennus: sama lähde ja samat työkalut tuottavat bitilleen
# saman tuloksen riippumatta hakemistosta ja kellonajasta.
set -euo pipefail

# @alku polut
# rakenna HAKEMISTO [kuvaa]: kääntää tilasto.c:n annetussa hakemistossa;
# "kuvaa" korvaa debug-tiedossa hakemiston polun pisteellä.
rakenna() {
    mkdir -p "$1"
    cp lahde/tilasto.c lahde/tilasto.h "$1/"
    (
        cd "$1"
        liput=(-g -O2)
        [[ ${2:-} == kuvaa ]] && liput+=("-ffile-prefix-map=$PWD=.")
        $CC "${liput[@]}" -c tilasto.c -o tilasto.o
    )
    sha256sum "$1/tilasto.o" | cut -c1-16
}
vertaa() {
    if [[ $1 == "$2" ]]; then echo "samat"; else echo "eri"; fi
}

echo "== debug-tieto sisältää käännöshakemiston"
a=$(rakenna koti/aino/projekti)
b=$(rakenna /tmp/ci-ajo-4711/projekti)
echo "ilman polkujen kuvausta: $(vertaa "$a" "$b")"
a=$(rakenna koti/aino/projekti2 kuvaa)
b=$(rakenna /tmp/ci-ajo-4712/projekti kuvaa)
echo "-ffile-prefix-map: $(vertaa "$a" "$b")"
# @loppu polut
rm -rf /tmp/ci-ajo-4711 /tmp/ci-ajo-4712

# @alku aika
echo "== __DATE__ ja __TIME__ kiinnitetään SOURCE_DATE_EPOCH-muuttujalla"
SOURCE_DATE_EPOCH=1767225600 $CC versio.c -o versio
./versio
# @loppu aika

# @alku arkisto
echo "== ar kirjoittaa arkistoon nolla-aikaleimat (D-tila)"
$CC -c lahde/tilasto.c -o tilasto.o
ar rcsD libtilasto.a tilasto.o
ar tv libtilasto.a
# @loppu arkisto
