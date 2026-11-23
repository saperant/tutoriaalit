#!/usr/bin/env bash
# Omat työkalut PATHiin ja komennon etsintäjärjestys.
set -euo pipefail
export LC_ALL=C

# @alku path
mkdir -p tyokalut/bin
cat > tyokalut/bin/rivit <<'SKRIPTI'
#!/bin/sh
# rivit TIEDOSTO... - tulostaa tiedostojen rivimäärät suurimmasta alkaen
wc -l -- "$@" | grep -v ' total$' | sort -k1,1nr
SKRIPTI
rivit 2> /dev/null || echo "rivit: komentoa ei löydy"
chmod +x tyokalut/bin/rivit
PATH="$PWD/tyokalut/bin:$PATH"
command -v rivit | sed "s|^$PWD/||"
seq 10 > a.txt; seq 3 > b.txt
rivit a.txt b.txt
# @loppu path

# @alku varjostus
printf '#!/bin/sh\necho "väärä ls"\n' > tyokalut/bin/ls
chmod +x tyokalut/bin/ls
hash -r
type -a ls | head -n 2 | sed "s|$PWD/||"
# @loppu varjostus
