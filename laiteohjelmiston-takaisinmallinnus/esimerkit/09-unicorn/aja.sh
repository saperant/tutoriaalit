#!/usr/bin/env bash
# Yksittaisten funktioiden emulointi Unicornilla: tarkistefunktion,
# purkufunktion ja tulostuksen ajaminen ilman koko laitetta.
source ./yhteinen.sh

# @alku aja
python3 emuloi.py "$LAITE/flash.bin"
# @loppu aja
