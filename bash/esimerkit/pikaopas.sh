#!/usr/bin/env bash
# Pikaoppaan koodi: skriptipohja ja tiiviit syntaksiesimerkit.
# @alku pohja
set -euo pipefail
shopt -s inherit_errexit nullglob

readonly OHJELMA=${0##*/}
kuole() { printf '%s: %s\n' "$OHJELMA" "$*" >&2; exit 1; }
loki()  { printf '%s %s\n' "$(date +%T)" "$*" >&2; }

tyohak=$(mktemp -d)
trap 'rm -rf -- "$tyohak"' EXIT
# @loppu pohja

# @alku laajennukset
polku=/var/log/nginx/access.log.2.gz
echo "${polku##*/}"         # access.log.2.gz   pisin etuliite pois
echo "${polku%/*}"          # /var/log/nginx    lyhin loppuliite pois
echo "${polku%%.*}"         # /var/log/nginx/access
echo "${polku/log/LOG}"     # ensimmäinen korvaus; // kaikki
echo "${#polku}"            # 30                pituus
echo "${polku:5:3}"         # log               osajono
echo "${PORTTI:-8080}"      # oletus, jos tyhjä tai asettamaton
nimi=Ada; echo "${nimi^^} ${nimi,,}"    # ADA ada
# @loppu laajennukset

# @alku ehdot
tiedosto=$tyohak/data.txt; printf 'x\n' > "$tiedosto"
[[ -f $tiedosto && -s $tiedosto ]] && echo "on tiedosto, ei tyhjä"
[[ $nimi == A* ]] && echo "alkaa A:lla"     # glob-vertailu
kausi=2026-11
[[ $kausi =~ ^([0-9]{4})-([0-9]{2})$ ]] && echo "v. ${BASH_REMATCH[1]}"
(( ${#nimi} > 2 )) && echo "pitkä nimi"     # aritmetiikka
# @loppu ehdot

# @alku taulukot
palvelimet=(web1 "db 1" jono1)
palvelimet+=(valvonta)
echo "${#palvelimet[@]} ${palvelimet[1]} ${palvelimet[*]: -1}"
for p in "${palvelimet[@]}"; do printf '[%s]' "$p"; done; echo
declare -A portti=([http]=80 [https]=443)
portti[ssh]=22
for avain in "${!portti[@]}"; do      # avaimet, järjestys vapaa
    printf '%s=%s\n' "$avain" "${portti[$avain]}"
done | sort
[[ -v portti[ssh] ]] && echo "ssh: ${portti[ssh]}"
# @loppu taulukot
