#!/usr/bin/env bash
# CMake-projekti esiasetuksilla: kehitys (Debug ja sanitoijat) ja
# julkaisu (Release). Rakennus erilliseen hakemistoon Ninjalla.
set -euo pipefail

# @alku kehitys
echo "== kehitys: konfigurointi, rakennus ja testit"
cmake --preset kehitys > /dev/null
cmake --build --preset kehitys > /dev/null
ctest --preset kehitys | grep -E 'Test +#|tests passed' \
    | sed -E 's/ +[0-9.]+ sec$//; s/\.{3,}/ ... /'
# @loppu kehitys

# @alku liput
echo "== mitä lippuja kukin lähde sai (compile_commands.json)"
python3 - build/kehitys/compile_commands.json <<'PY'
import json, pathlib, sys
for k in json.load(open(sys.argv[1])):
    nimi = pathlib.Path(k["file"]).name
    liput = k["command"].split()
    print(f"{nimi:18} -Ilahde: {any(l.endswith('/lahde') for l in liput)!s:5}"
          f" -Werror: {'-Werror' in liput}")
PY
# @loppu liput

# @alku julkaisu
echo "== julkaisu"
cmake --preset julkaisu > /dev/null
cmake --build --preset julkaisu > /dev/null
build/julkaisu/tilasto < lahde/mittaukset.txt | tail -n 1
ctest --preset julkaisu | grep 'tests passed'
ls build/julkaisu/libtilasto.a build/julkaisu/tilasto
# @loppu julkaisu

# @alku asennus
echo "== asennus: DESTDIR ja --prefix"
DESTDIR=$PWD/paketti cmake --install build/julkaisu --prefix /usr \
    > /dev/null
(cd paketti && find . -type f | LC_ALL=C sort)
# @loppu asennus
