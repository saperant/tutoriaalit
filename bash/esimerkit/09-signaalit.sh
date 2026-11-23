#!/usr/bin/env bash
# Pitkäkestoinen silmukka lopettaa hallitusti TERM- tai INT-signaalin
# saatuaan: kesken oleva kierros viedään loppuun ja tila tallennetaan.
set -euo pipefail

# @alku ansa
kasittele_jono() {
    local lopeta=0
    # Ansa asetetaan taustatyön sisällä: alikuori ei peri isäntänsä
    # ansoja.
    trap 'lopeta=1' TERM INT
    while (( ! lopeta )); do
        sleep 0.1                   # yksi työkierros
    done
    echo "pysäytetty hallitusti, tila tallennettu"
}
# @loppu ansa

# @alku lahetys
kasittele_jono > tuloste.txt &
pid=$!
sleep 0.35
kill -TERM "$pid"
wait "$pid"
cat tuloste.txt
# @loppu lahetys

# @alku timeout
tila=0
timeout 0.2 sleep 5 || tila=$?
if (( tila == 124 )); then
    echo "aikakatkaisu (tila 124)"
fi
# @loppu timeout
