#!/usr/bin/env bash
# Idempotentti asennusskripti: toinen ajo ei muuta mitään, ja jokainen
# vaihe kertoo, tekikö se jotain. Polut ovat suhteellisia, jotta
# esimerkki toimii ilman pääkäyttäjän oikeuksia.
set -euo pipefail

# @alku apu
varmista_hakemisto() {
    [[ -d $1 ]] && return 0
    mkdir -p -- "$1"
    echo "luotu hakemisto $1"
}

varmista_rivi() {               # varmista_rivi TIEDOSTO RIVI
    local tiedosto=$1 rivi=$2
    [[ -f $tiedosto ]] && grep -qxF -- "$rivi" "$tiedosto" && return 0
    printf '%s\n' "$rivi" >> "$tiedosto"
    echo "lisätty rivi '$rivi' tiedostoon $tiedosto"
}

varmista_linkki() {             # varmista_linkki KOHDE LINKKI
    [[ -L $2 && $(readlink -- "$2") == "$1" ]] && return 0
    ln -sfn -- "$1" "$2"
    echo "linkki $2 -> $1"
}
# @loppu apu

# @alku asennus
asenna() {
    varmista_hakemisto etc/sovellus
    varmista_hakemisto var/log/sovellus
    varmista_rivi etc/sovellus/ymparisto 'LOKI_HAKEMISTO=/var/log/sovellus'
    varmista_rivi etc/sovellus/ymparisto 'TYOLAISIA=4'
    varmista_linkki ../etc/sovellus/ymparisto var/ymparisto
}

echo "== ensimmäinen ajo"; asenna
echo "== toinen ajo";      asenna
echo "== valmis"
# @loppu asennus
