#!/usr/bin/env bash
# Windowsin rivinvaihdot (CRLF) rikkovat vertailut ja skriptit.
set -euo pipefail
export LC_ALL=C

printf 'kaisa\r\nmatti\r\n' > windows.txt

# @alku nakyviin
cat -A windows.txt
grep -c '^kaisa$' windows.txt || true
# @loppu nakyviin

# @alku korjaus
tr -d '\r' < windows.txt > unix.txt
cat -A unix.txt
grep -c '^kaisa$' unix.txt
# @loppu korjaus
