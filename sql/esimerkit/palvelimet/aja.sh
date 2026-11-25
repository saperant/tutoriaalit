#!/usr/bin/env bash
# Ajaa palvelintietokantojen esimerkit oikeilla palvelimilla.
#
# Käynnistää PostgreSQL:n ja MariaDB:n väliaikaishakemistoon (vain
# Unix-soketit, ei TCP-portteja), ajaa jokaisen esimerkin ja vertaa
# tulosteen odotettuun. Palvelimet pysäytetään aina lopuksi.
#
#   *.pg              ajetaan psql:llä PostgreSQL:ssä
#   *.maria           ajetaan mariadb-asiakkaalla MariaDB:ssä
#   ../12-sama.sql    ajetaan sellaisenaan molemmissa
#   ../14-tyypit.py   ajetaan psycopg-ajurilla PostgreSQL:ää vasten
#                     (odotettu tuloste 14-tyypit.pg.odotettu)
#   ../15-orm.py      ajetaan SQLAlchemyllä molempia vasten; tulosteen on
#                     oltava sama kuin SQLitellä (../15-orm.odotettu)
#
# Odotettu tuloste on tiedostossa <nimi>.odotettu (esim. 13-osiot.pg ->
# 13-osiot.pg.odotettu). PAIVITA=1 kirjoittaa odotetut tulosteet.
set -euo pipefail
cd "$(dirname "$0")"

TYO=$(mktemp -d)
chmod 755 "$TYO"       # postgres-käyttäjän on päästävä hakemistoon
PG_DATA=$TYO/pg
MARIA_DATA=$TYO/maria
MARIA_SOKETTI=$TYO/maria.sock

# PostgreSQL ei käynnisty pääkäyttäjänä, joten kontissa se ajetaan
# käyttäjänä postgres. MariaDB taas vaatii pääkäyttäjänä --user=root.
if [[ $EUID -eq 0 ]]; then
    PG_AS=(runuser -u postgres --)
    MARIA_KAYTTAJA=(--user=root)
else
    PG_AS=()
    MARIA_KAYTTAJA=()
fi
PG_BIN=$(dirname "$(find /usr/lib/postgresql -name pg_ctl | sort | tail -1)")

lopeta() {
    "${PG_AS[@]}" "$PG_BIN/pg_ctl" -D "$PG_DATA" -m immediate -w stop \
        > /dev/null 2>&1 || true
    if [[ -f $TYO/maria.pid ]]; then
        kill "$(cat "$TYO/maria.pid")" 2> /dev/null || true
        for _ in $(seq 50); do
            [[ -e $MARIA_SOKETTI ]] || break
            sleep 0.1
        done
    fi
    rm -rf "$TYO"
}
trap lopeta EXIT

# --- PostgreSQL ------------------------------------------------------
mkdir -m 700 "$PG_DATA"
[[ $EUID -eq 0 ]] && chown postgres:postgres "$PG_DATA"
"${PG_AS[@]}" "$PG_BIN/initdb" -D "$PG_DATA" -U tutoriaali \
    --auth=trust -E UTF8 --locale=C.UTF-8 --no-sync > /dev/null
"${PG_AS[@]}" "$PG_BIN/pg_ctl" -D "$PG_DATA" -l "$PG_DATA/loki" -w \
    -o "-c listen_addresses='' -k $PG_DATA -c fsync=off -c TimeZone=UTC" \
    start > /dev/null || { cat "$PG_DATA/loki" >&2; exit 1; }
"${PG_AS[@]}" "$PG_BIN/createdb" -h "$PG_DATA" -U tutoriaali kanta

psql_aja() {
    psql -X -q -v ON_ERROR_STOP=1 -P pager=off -P null=NULL -h "$PG_DATA" \
        -U tutoriaali -d kanta -f "$1" 2>&1
}

# --- MariaDB ------------------------------------------------------------
mkdir "$MARIA_DATA"
mariadb-install-db --no-defaults --datadir="$MARIA_DATA" \
    "${MARIA_KAYTTAJA[@]}" --auth-root-authentication-method=normal \
    --skip-test-db > "$TYO/maria-asennus.loki" 2>&1 \
    || { cat "$TYO/maria-asennus.loki" >&2; exit 1; }
mariadbd --no-defaults --datadir="$MARIA_DATA" "${MARIA_KAYTTAJA[@]}" \
    --socket="$MARIA_SOKETTI" --skip-networking --pid-file="$TYO/maria.pid" \
    --log-error="$TYO/maria.loki" --default-time-zone=+00:00 \
    --innodb-flush-log-at-trx-commit=0 > /dev/null 2>&1 &
for _ in $(seq 300); do
    [[ -S $MARIA_SOKETTI ]] && break
    sleep 0.1
done
[[ -S $MARIA_SOKETTI ]] || { cat "$TYO/maria.loki" >&2; exit 1; }
mariadb --no-defaults -S "$MARIA_SOKETTI" -u root \
    -e "CREATE DATABASE kanta"

maria_aja() {
    mariadb --no-defaults --table -S "$MARIA_SOKETTI" -u root kanta \
        < "$1" 2>&1
}

# --- Esimerkit ----------------------------------------------------------
virheet=0
vertaa() {   # vertaa NIMI: stdin verrataan tiedostoon NIMI.odotettu
    local saatu
    saatu=$(cat)
    if [[ ${PAIVITA:-} == 1 ]]; then
        printf '%s\n' "$saatu" > "$1.odotettu"
    elif ! diff -u "$1.odotettu" <(printf '%s\n' "$saatu"); then
        echo "palvelimet: $1 poikkeaa odotetusta" >&2
        virheet=$((virheet + 1))
    fi
}

for f in *.pg; do psql_aja "$f" | vertaa "$f"; done
for f in *.maria; do maria_aja "$f" | vertaa "$f"; done
psql_aja ../12-sama.sql | vertaa 12-sama.pg
maria_aja ../12-sama.sql | vertaa 12-sama.maria

PG_URL="postgresql+psycopg://tutoriaali@/kanta?host=$PG_DATA"
MARIA_URL="mysql+pymysql://root@localhost/kanta?unix_socket=$MARIA_SOKETTI"
PG_DSN="host=$PG_DATA user=tutoriaali dbname=kanta" \
    python3 ../14-tyypit.py | vertaa 14-tyypit.pg
TIETOKANTA=$PG_URL python3 ../15-orm.py | vertaa ../15-orm
TIETOKANTA=$MARIA_URL python3 ../15-orm.py | vertaa ../15-orm

if [[ $virheet -gt 0 ]]; then
    echo "palvelimet: $virheet esimerkkiä poikkesi" >&2
    exit 1
fi
echo "OK: palvelinesimerkit (PostgreSQL ja MariaDB)"
