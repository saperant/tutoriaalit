#!/usr/bin/env bash
# Muistivirheiden seuranta: Linuxin EDAC-ajuri laskee korjatut (CE) ja
# korjaamattomat (UE) virheet muistiohjaimittain ja -kammoittain.
# Skripti lukee laskurit ja nostaa esiin kammat, joiden virheet
# kasvavat. Oikealla koneella juuri on /sys; testissä rakennetaan
# samanlainen hakemistopuu.
set -euo pipefail
export LC_ALL=C

# @alku testipuu
juuri=$(mktemp -d)
trap 'rm -rf "$juuri"' EXIT
mc=$juuri/devices/system/edac/mc
luo() {  # luo <ohjain> <kampa> <nimi> <CE> <UE>
    local d=$mc/$1/$2
    mkdir -p "$d"
    echo "$3" > "$d/dimm_label"
    echo "$4" > "$d/dimm_ce_count"
    echo "$5" > "$d/dimm_ue_count"
}
luo mc0 dimm0 CPU0_DIMM_A1 0 0
luo mc0 dimm1 CPU0_DIMM_B1 2 0
luo mc1 dimm0 CPU1_DIMM_A1 1873 0
luo mc1 dimm1 CPU1_DIMM_B1 0 1
# @loppu testipuu

# @alku raportti
raportoi() {  # raportoi <sys-juuri> <CE-raja>
    local kampa nimi ce ue tila
    for kampa in "$1"/devices/system/edac/mc/mc*/dimm*; do
        nimi=$(<"$kampa/dimm_label")
        ce=$(<"$kampa/dimm_ce_count")
        ue=$(<"$kampa/dimm_ue_count")
        if (( ue > 0 )); then
            tila="VAIHDA HETI (korjaamaton virhe)"
        elif (( ce >= $2 )); then
            tila="vaihda huollossa (korjattuja $ce)"
        else
            tila="ok"
        fi
        printf '%-14s CE=%-5s UE=%-2s %s\n' "$nimi" "$ce" "$ue" "$tila"
    done
}
raportoi "$juuri" 100
# @loppu raportti
