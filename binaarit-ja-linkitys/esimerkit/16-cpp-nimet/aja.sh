#!/usr/bin/env bash
# C++:n nimien koristelu ja extern "C" kielten rajalla.
source ./yhteinen.sh
CXXFLAGS=(-std=c++20 -O2 -Wall -Wextra -Werror)

otsikko "koristellut nimet"
# @alku nimet
"$CXX" "${CXXFLAGS[@]}" -c suodin.cpp
nm suodin.o | awk '$2 == "T" { print $3 }' | sort
nm -C suodin.o | awk '$2 == "T" { $1 = $2 = ""; print substr($0, 3) }' |
    sort
echo _ZN6suodin9keskiarvoEii | c++filt
# @loppu nimet

otsikko "linkitys C-ohjelmaan"
# @alku linkitys
"$CC" "${CFLAGS[@]}" -c main.c
"$CXX" main.o suodin.o -o suodatus   # C++-kääntäjä tuo libstdc++:n
./suodatus
# @loppu linkitys

otsikko "extern \"C\" unohtui"
# @alku unohtui
sed 's/suodin.hpp/unohtunut.hpp/' suodin.cpp > unohtunut.cpp
"$CXX" "${CXXFLAGS[@]}" -c unohtunut.cpp
virherivi "$CXX" main.o unohtunut.o -o rikki
nm unohtunut.o | awk '$2 == "T" && /suodin_keskiarvo/ { print $3 }'
# @loppu unohtui
