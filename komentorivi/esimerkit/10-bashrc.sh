#!/usr/bin/env bash
# Esimerkki tiedostosta ~/.bashrc. Testi tarkistaa ShellCheckillä ja
# lataa sen kuoreen.
set -euo pipefail

# @alku bashrc
# ~/.bashrc: vain vuorovaikutteiselle kuorelle
export EDITOR=vim
export PATH="$HOME/.local/bin:$PATH"

HISTSIZE=50000
HISTCONTROL=ignoreboth:erasedups   # ei duplikaatteja eikä
                                   # välilyönnillä alkavia
shopt -s histappend                # monta päätettä, yksi historia

alias ll='ls -lh'
alias gs='git status --short'

# Funktio, kun argumentti tarvitaan keskelle komentoa
mkcd() { mkdir -p -- "$1" && cd -- "$1"; }
# @loppu bashrc

mkcd uusi/hakemisto
basename "$PWD"
echo "$HISTSIZE"
