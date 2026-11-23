#!/usr/bin/env bash
# Bashin aritmetiikka on kokonaislukuaritmetiikkaa. Desimaalit hoidetaan
# kiinteällä pilkulla tai ulkoisella työkalulla.
set -euo pipefail
export LC_ALL=C          # printf:n desimaalierotin ei riipu kielestä

# @alku kokonaisluvut
tavut=7340032
echo "MiB (katkaistu): $(( tavut / 1024 / 1024 ))"
(( tavut > 5 * 1024 * 1024 )) && echo "yli 5 MiB"
# @loppu kokonaisluvut

# @alku kiintea
# Prosenttiosuus yhdellä desimaalilla: lasketaan kymmenyksinä.
onnistuneet=377
kaikki=412
promille=$(( (onnistuneet * 1000 + kaikki / 2) / kaikki ))
printf 'onnistumisaste %d.%d %%\n' $(( promille / 10 )) $(( promille % 10 ))
# @loppu kiintea

# @alku awk
awk -v a="$onnistuneet" -v b="$kaikki" \
    'BEGIN { printf "awk: %.2f %%\n", 100 * a / b }'
# @loppu awk

# @alku printf
printf '%-12s|%6s|\n' palvelu tila
printf '%-12s|%6d|\n' verkko 200 tietokanta 503
printf '%05.1f\n' 3.14159
# @loppu printf
