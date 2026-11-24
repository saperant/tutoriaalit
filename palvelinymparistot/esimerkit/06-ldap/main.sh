#!/usr/bin/env bash
# Pieni LDAP-hakemisto: OpenLDAP käynnistetään tilapäishakemistoon
# vapaaseen porttiin, ja sinne lisätään käyttäjät ja ryhmä. Sitten
# haetaan tietoja, tarkistetaan kirjautuminen ja kokeillaan
# pääsynhallintaa. Hakemisto on /var/tmp:ssä, koska Ubuntun
# AppArmor-profiili sallii slapd:lle sen.
set -euo pipefail
export LC_ALL=C
lahde=$(cd "$(dirname "$0")" && pwd)
tyo=$(mktemp -d -p /var/tmp ldap.XXXXXX)
pid=""
siivoa() {
    [[ -n $pid ]] && kill "$pid" 2>/dev/null && wait "$pid" 2>/dev/null
    rm -rf "$tyo"
}
trap siivoa EXIT

# @alku kaynnistys
mkdir "$tyo/tietokanta"
sed "s|TIETOKANTA|$tyo/tietokanta|" "$lahde/slapd.conf" \
    > "$tyo/slapd.conf"
portti=$(python3 -c 'import socket; s = socket.socket(); s.bind(("", 0))
print(s.getsockname()[1])')
url=ldap://127.0.0.1:$portti
slapd -f "$tyo/slapd.conf" -h "$url" -d 0 2> "$tyo/slapd.log" &
pid=$!
for _ in $(seq 50); do
    ldapsearch -x -H "$url" -s base -b '' > /dev/null 2>&1 && break
    sleep 0.1
done
# @loppu kaynnistys

# Salasanat tallennetaan suolattuina tiivisteinä ({SSHA}).
ldif=$(cat "$lahde/hakemisto.ldif")
for nimi in aino olli; do
    tiiviste=$(slappasswd -s "salasana-$nimi")
    ldif=${ldif//SALASANA-${nimi^^}/$tiiviste}
done

# @alku lisays
yllapito=(-x -H "$url" -D "cn=admin,dc=esimerkki,dc=fi"
          -w yllapito-salasana)
ldapadd "${yllapito[@]}" <<< "$ldif" > /dev/null
# @loppu lisays

# @alku haku
echo "== käyttäjät"
ldapsearch "${yllapito[@]}" -LLL -b ou=ihmiset,dc=esimerkki,dc=fi \
    '(objectClass=posixAccount)' uid uidNumber mail
echo "== ylläpitoryhmän jäsenet"
ldapsearch "${yllapito[@]}" -LLL -b dc=esimerkki,dc=fi \
    '(&(objectClass=posixGroup)(cn=yllapito))' memberUid
# @loppu haku

# @alku kirjautuminen
aino=uid=aino,ou=ihmiset,dc=esimerkki,dc=fi
echo "== kirjautuminen"
ldapwhoami -x -H "$url" -D "$aino" -w salasana-aino
ldapwhoami -x -H "$url" -D "$aino" -w vaara 2>&1 | head -n 1 || true
# @loppu kirjautuminen

# @alku oikeudet
echo "== Aino lukee Ollin tiedot"
ldapsearch -x -H "$url" -D "$aino" -w salasana-aino -LLL \
    -b uid=olli,ou=ihmiset,dc=esimerkki,dc=fi mail userPassword
echo "== anonyymi haku"
ldapsearch -x -H "$url" -LLL -b ou=ihmiset,dc=esimerkki,dc=fi uid \
    2>&1 || echo "(haku evätty, paluuarvo $?)"
# @loppu oikeudet
