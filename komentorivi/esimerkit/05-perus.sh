#!/usr/bin/env bash
# grepin perusvalitsimet sovelluslokin tutkimiseen.
set -euo pipefail
export LC_ALL=C

# @alku aineisto
cat > sovellus.log <<'LOKI'
08:15:01 INFO  [auth] kirjautuminen onnistui kayttaja=kaisa
08:15:07 WARN  [db] hidas kysely 1840 ms
08:16:22 ERROR [auth] kirjautuminen epaonnistui kayttaja=olli
08:16:23 INFO  [api] GET /tuotteet 200
08:17:40 error [mail] SMTP-yhteys katkesi
08:18:02 ERROR [db] yhteyspooli taynna
08:18:05 INFO  [api] GET /tilaukset 500
LOKI
# @loppu aineisto

# @alku perus
grep -c 'ERROR' sovellus.log
grep -ci 'error' sovellus.log
grep -n '\[db\]' sovellus.log
grep -v 'INFO' sovellus.log | grep -vi 'error'
# @loppu perus

# @alku sana
grep -w 'GET' sovellus.log | grep -E ' (4|5)[0-9]{2}$'
# @loppu sana
