#!/usr/bin/env bash
# Komennon aikaraja ja signaalin valinta.
set -euo pipefail
export LC_ALL=C

# @alku timeout
timeout 0.2 sleep 10 || echo "aikaraja ylittyi, paluuarvo $?"
timeout --preserve-status 0.2 sleep 10 || echo "paluuarvo $?"
timeout 5 true && echo "valmistui ajoissa, paluuarvo $?"
# @loppu timeout
