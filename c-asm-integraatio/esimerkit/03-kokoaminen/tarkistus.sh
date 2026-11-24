#!/usr/bin/env bash
set -euo pipefail
hak=$(dirname "$0")
# @alku pieni-s
# Sama lähde pienellä s:llä: esikääntäjä ei aja, #include on
# kommentti ja makrot jäävät avaamatta.
cp "$hak/x86.S" "$RAK/sama.s"
echo "sama.s (ei esikääntäjää):"
if "$CC_X86" -c -o "$RAK/sama.o" "$RAK/sama.s" 2> "$RAK/sama.err"; then
    echo "koottiin?"
fi
grep -o 'Error: .*' "$RAK/sama.err"
# @loppu pieni-s
# @alku merkinta
# Ilman .note.GNU-stack-osiota linkkeri olettaa, että pinon pitää
# olla suoritettava.
pinon_oikeudet() { # READELF OHJELMA
    "$1" -lW "$2" | awk '$1 == "GNU_STACK" { print "GNU_STACK", $7 }'
}
grep -v PINO_EI_SUORITETTAVA "$hak/x86.S" > "$RAK/ilman.S"
echo "merkinnän kanssa:"
pinon_oikeudet readelf "$RAK/x86"
echo "ilman merkintää:"
# shellcheck disable=SC2086
"$CC_X86" $CFLAGS -static -I "$hak" -o "$RAK/ilman" "$hak/main.c" \
    "$RAK/ilman.S" 2> "$RAK/ilman.err"
grep -o 'missing .note.GNU-stack.*' "$RAK/ilman.err"
pinon_oikeudet readelf "$RAK/ilman"
# @loppu merkinta
