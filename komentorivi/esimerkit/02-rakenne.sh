#!/usr/bin/env bash
# Hakemistorakenne, aaltosulkulaajennus, glob ja polkujen käsittely.
set -euo pipefail
export LC_ALL=C

# @alku luonti
mkdir -p projekti/{lahde,dokumentit,rakennus}
touch projekti/lahde/{paa,apu}.c projekti/lahde/apu.h
touch projekti/dokumentit/{ohje,muutokset}.md
# @loppu luonti

# @alku glob
echo projekti/*/
echo projekti/lahde/*.c
echo projekti/lahde/[a-j]*
echo projekti/lahde/*.{c,h}
# @loppu glob

# @alku polut
polku=projekti/lahde/paa.c
basename "$polku"
basename "$polku" .c
dirname "$polku"
realpath --relative-to=projekti/dokumentit "$polku"
# @loppu polut
