#!/usr/bin/env bash
# find: nimi, tyyppi, koko, ikä ja karsinta.
set -euo pipefail
export LC_ALL=C

mkdir -p projekti/{lahde,rakennus,node_modules/kirjasto,tyhja}
touch projekti/lahde/{paa,apu}.js projekti/node_modules/kirjasto/x.js
head -c 300000 /dev/zero > projekti/rakennus/paketti.zip
touch -d '20 days ago' projekti/rakennus/vanha.o
touch -d '2 days ago' projekti/lahde/apu.js

# @alku nimi
find projekti -name '*.js' | sort
find projekti -path projekti/node_modules -prune -o -name '*.js' -print \
    | sort
# @loppu nimi

# @alku ominaisuudet
find projekti -type f -size +100k
find projekti -type f -mtime +7
find projekti -type f -name '*.js' -mtime -1 | sort
find projekti -type d -empty
# @loppu ominaisuudet
