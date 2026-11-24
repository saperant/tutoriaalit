#!/usr/bin/env bash
# Rekisteri omassa osiossa: linkkeri kokoaa taulukon.
source ./yhteinen.sh

# @alku rakennus
for f in main tila versio; do
    "$CC" "${CFLAGS[@]}" -c "$f.c" -o "$f.o"
done
"$CC" main.o tila.o versio.o -o tyokalu -Wl,-Map=tyokalu.map
./tyokalu
./tyokalu versio
./tyokalu tila
# @loppu rakennus

otsikko "osio linkkerikartassa"
# @alku kartta
# Osion rivi ja sen syötteet: mistä objektitiedostoista se koottiin.
awk '/^komennot / { mukana = 1; print $1, "koko", $3; next }
     mukana && /^ komennot/ { sub(/.*\//, ""); print " ", $NF }
     mukana && /^$/ { exit }' tyokalu.map
# @loppu kartta
