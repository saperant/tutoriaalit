#!/usr/bin/env bash
# Oma pieni varmentaja (CA) ja palvelinvarmenne OpenSSL:llä.
set -euo pipefail

main() {
    # @alku ca
    # Juurivarmentaja: EC-avain ja itse allekirjoitettu varmenne.
    openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 \
        -nodes -keyout ca.key -out ca.crt -days 3650 \
        -subj "/O=Esimerkki Oy/CN=Esimerkki Oy Root CA" \
        -addext "basicConstraints=critical,CA:TRUE" \
        -addext "keyUsage=critical,keyCertSign,cRLSign" 2> /dev/null
    # @loppu ca

    # @alku palvelin
    # Palvelin luo avaimen ja varmennepyynnön (CSR); CA allekirjoittaa.
    openssl req -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
        -keyout palvelu.key -out palvelu.csr \
        -subj "/CN=palvelu.example" 2> /dev/null
    printf '%s\n' "subjectAltName=DNS:palvelu.example" \
        "extendedKeyUsage=serverAuth" > laajennukset.ext
    openssl x509 -req -in palvelu.csr -CA ca.crt -CAkey ca.key \
        -days 90 -extfile laajennukset.ext -out palvelu.crt 2> /dev/null
    # @loppu palvelin

    # @alku tarkistus
    openssl x509 -in palvelu.crt -noout -subject -issuer -ext subjectAltName
    openssl verify -CAfile ca.crt palvelu.crt
    openssl verify -CAfile ca.crt -verify_hostname palvelu.example \
        palvelu.crt
    # @loppu tarkistus

    # Väärän CA:n allekirjoittama varmenne ei kelpaa.
    openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
        -keyout toinen.key -out toinen.crt -days 1 \
        -subj "/CN=Toinen CA" 2> /dev/null
    if ! openssl verify -CAfile toinen.crt palvelu.crt > /dev/null 2>&1; then
        echo "palvelu.crt: ei kelpaa toisen CA:n kanssa"
    fi
}

main "$@"
