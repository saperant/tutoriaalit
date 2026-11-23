#!/usr/bin/env bash
# Hakemistopuun läpikäynti: missä asetustiedostoissa on vanha osoite?
set -euo pipefail
export LC_ALL=C

mkdir -p palvelut/{web,api,vanha} palvelut/web/node_modules/kirjasto
echo 'tietokanta=db1.sisainen:5432' > palvelut/web/asetukset.conf
echo 'tietokanta=db2.sisainen:5432' > palvelut/api/asetukset.conf
echo 'varmuuskopio=db1.sisainen' > palvelut/api/varmistus.conf
echo 'db1.sisainen' > palvelut/api/muistiinpanot.txt
echo 'tietokanta=db1.sisainen' > palvelut/web/node_modules/kirjasto/x.conf

# @alku rekursiivinen
grep -rn --include='*.conf' --exclude-dir=node_modules \
    'db1\.sisainen' palvelut | sort
echo "--"
grep -rL --include='*.conf' --exclude-dir=node_modules \
    'db1\.sisainen' palvelut
# @loppu rekursiivinen
