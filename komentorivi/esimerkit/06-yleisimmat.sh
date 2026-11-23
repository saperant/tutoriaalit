#!/usr/bin/env bash
# Verkkopalvelimen pääsyloki: yleisimmät asiakkaat, tilakoodit ja
# virheitä tuottavat polut.
set -euo pipefail
export LC_ALL=C

# @alku aineisto
cat > access.log <<'LOKI'
10.0.0.5 - - [02/Nov/2026:08:15:01 +0200] "GET / HTTP/1.1" 200 5120
10.0.0.9 - - [02/Nov/2026:08:15:03 +0200] "GET /tuotteet HTTP/1.1" 200 812
10.0.0.5 - - [02/Nov/2026:08:15:09 +0200] "GET /kuvat/a.png HTTP/1.1" 404 0
192.0.2.7 - - [02/Nov/2026:08:16:12 +0200] "POST /kirjaudu HTTP/1.1" 401 64
192.0.2.7 - - [02/Nov/2026:08:16:13 +0200] "POST /kirjaudu HTTP/1.1" 401 64
10.0.0.9 - - [02/Nov/2026:08:16:40 +0200] "GET /tilaukset HTTP/1.1" 500 120
10.0.0.5 - - [02/Nov/2026:08:17:02 +0200] "GET /tuotteet HTTP/1.1" 200 812
192.0.2.7 - - [02/Nov/2026:08:17:30 +0200] "POST /kirjaudu HTTP/1.1" 200 64
10.0.0.12 - - [02/Nov/2026:08:18:00 +0200] "GET /tilaukset HTTP/1.1" 500 120
LOKI
# @loppu aineisto

# @alku asiakkaat
cut -d' ' -f1 access.log | sort | uniq -c | sort -k1,1nr -k2 | head -n 3
# @loppu asiakkaat

# @alku tilakoodit
cut -d' ' -f9 access.log | sort | uniq -c
# @loppu tilakoodit

# @alku virhepolut
grep -E '" 5[0-9]{2} ' access.log | cut -d' ' -f7 | sort -u
# @loppu virhepolut
