#!/usr/bin/env bash
# set -u pysäyttää skriptin, kun asettamatonta muuttujaa käytetään.
# Ilman sitä kirjoitusvirhe muuttujan nimessä tuottaisi tyhjän
# merkkijonon, ja komento kohdistuisi väärään polkuun.
#
# ShellCheck huomaa kirjoitusvirheen jo ennen ajoa (SC2154). Varoitukset
# vaiennetaan, jotta set -u:n toiminta nähdään ajon aikana.
# shellcheck disable=SC2034,SC2154
set -euo pipefail

julkaisuhakemisto=/srv/sovellus/julkaisut
vanha=2026-10-01
echo "poistetaan ${julkaisuhakemsito}/$vanha"
