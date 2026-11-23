#!/usr/bin/env bash
# Kenttien poimiminen säännöllisillä lausekkeilla.
set -euo pipefail
export LC_ALL=C

cat > sovellus.log <<'LOKI'
08:15:01 INFO  [auth] kirjautuminen onnistui kayttaja=kaisa ip=10.0.0.5
08:16:22 ERROR [auth] kirjautuminen epaonnistui kayttaja=olli ip=10.0.0.51
08:16:30 ERROR [auth] kirjautuminen epaonnistui kayttaja=olli ip=10.0.0.51
08:16:41 ERROR [auth] kirjautuminen epaonnistui kayttaja=root ip=192.0.2.7
08:17:02 INFO  [auth] kirjautuminen onnistui kayttaja=matti ip=10.0.0.9
08:17:15 ERROR [auth] kirjautuminen epaonnistui kayttaja=admin ip=192.0.2.7
LOKI

# @alku poiminta
grep 'epaonnistui' sovellus.log \
    | grep -oE 'ip=[0-9.]+' \
    | cut -d= -f2 \
    | sort | uniq -c | sort -k1,1nr -k2
# @loppu poiminta

# @alku tarkka
grep -c 'ip=10.0.0.5' sovellus.log       # osuu myös 10.0.0.51:een
grep -cw 'ip=10\.0\.0\.5' sovellus.log   # vain kokonainen sana
grep -cFw 'ip=10.0.0.5' sovellus.log     # kiinteä merkkijono, sana
# @loppu tarkka
