#!/usr/bin/env bash
# Putken paluuarvo on oletuksena viimeisen komennon. pipefail tekee
# siitä viimeisen epäonnistuneen komennon paluuarvon.
set -eu

# @alku vertailu
set +o pipefail
false | sort > /dev/null
echo "ilman pipefailia: $?"

set -o pipefail
if ! false | sort > /dev/null; then
    echo "pipefailin kanssa putki epäonnistui"
fi
# @loppu vertailu

# @alku pipestatus
tilat=()
printf 'a\nb\n' | grep x | sort || tilat=("${PIPESTATUS[@]}")
echo "komentojen tilat: ${tilat[*]}"
# @loppu pipestatus

# @alku sigpipe
# head lopettaa lukemisen aikaisin, jolloin yes saa SIGPIPE-signaalin.
# pipefailin kanssa tämä on virhe, vaikka tulos on oikea.
if ! yes | head -n 2 > /dev/null; then
    echo "SIGPIPE: tila ${PIPESTATUS[0]}"
fi
# @loppu sigpipe
