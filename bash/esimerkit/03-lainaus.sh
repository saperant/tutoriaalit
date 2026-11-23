#!/usr/bin/env bash
# Sanojen jako ja polkunimilaajennus lainaamattomassa muuttujassa.
# Tiedosto näyttää tarkoituksella virheellisiä tapoja, joista ShellCheck
# varoittaisi; varoitukset on siksi vaimennettu.
# shellcheck disable=SC2086,SC2016
set -euo pipefail

touch 'kesän raportti.txt' 'muistio.txt'
tiedosto='kesän raportti.txt'

# @alku jako
printf '[%s]\n' $tiedosto        # lainaamaton: jaetaan sanoiksi
printf '[%s]\n' "$tiedosto"      # lainattu: yksi argumentti
# @loppu jako

# @alku glob
kuvio='*.txt'
printf '<%s>\n' $kuvio           # lainaamaton: laajenee tiedostoiksi
printf '<%s>\n' "$kuvio"         # lainattu: kirjaimellinen merkkijono
# @loppu glob

# @alku lainaukset
nimi='Ada'
printf '%s\n' 'yksinkertaiset: $nimi ja \n pysyvät sellaisinaan'
printf '%s\n' "kaksinkertaiset: $nimi, $((1 + 2)), $(basename /bin/ls)"
printf '%s\n' $'ANSI-C-lainaus: sarkain\tja rivinvaihto\n(loppui)'
# @loppu lainaukset
