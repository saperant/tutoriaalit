#!/usr/bin/env bash
# Mitä funktioita koodissa kutsutaan eniten? Tyypillinen
# grep | sort | uniq -c | sort -putki.
set -euo pipefail
export LC_ALL=C

cat > palvelin.c <<'KOODI'
int kasittele(int fd) {
    char *rivi = lue_rivi(fd);
    if (!rivi) { kirjaa("lukuvirhe"); return -1; }
    int tila = jasenna(rivi);
    kirjaa("jasennetty");
    vapauta(rivi);
    if (tila < 0) { kirjaa("virheellinen pyynto"); return -1; }
    return vastaa(fd, tila);
}
KOODI

# @alku tunnisteet
grep -oE '\b[a-z_]+\(' palvelin.c | tr -d '(' \
    | grep -vxE 'if|while|for|return' \
    | sort | uniq -c | sort -k1,1nr -k2 | head -n 3
# @loppu tunnisteet
