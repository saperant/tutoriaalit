#!/usr/bin/env bash
# Synteesi ja sijoittelu yhdelle suunnitelmalle iCE40 UP5K -piirille.
# Käyttö: vuo.sh NIMI YLIN "LÄHTEET" "SYNTEESIVALINNAT" "PNR-VALINNAT"
#                [PARAMETRI=ARVO ...]
# Tulokset hakemistoon rakennus/: NIMI.json (netlista), NIMI.stat.json
# (Yosysin tilastot), NIMI.pnr.json (nextpnr:n raportti), NIMI.asc.
# Ympäristömuuttuja SIEMEN valitsee sijoittelun satunnaissiemenen.
set -euo pipefail
nimi=$1 ylin=$2 lahteet=$3 synteesi=$4 pnr=$5
shift 5
parametrit=""
for p in "$@"; do
  parametrit+="chparam -set ${p%%=*} ${p#*=} $ylin; "
done
r=rakennus
mkdir -p "$r"
# @alku vuo
yosys -q -l "$r/$nimi.yosys.log" -p "
  read_verilog -sv $lahteet
  $parametrit
  synth_ice40 $synteesi -top $ylin -json $r/$nimi.json
  tee -q -o $r/$nimi.stat.json stat -json"
# shellcheck disable=SC2086  # valinnat sanoiksi tarkoituksella
nextpnr-ice40 --up5k --package sg48 --seed "${SIEMEN:-1}" -q \
  --json "$r/$nimi.json" --report "$r/$nimi.pnr.json" \
  --asc "$r/$nimi.asc" $pnr 2> "$r/$nimi.pnr.log"
# @loppu vuo
