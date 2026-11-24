#!/usr/bin/env bash
# Ed25519-avainpari ja tiedoston allekirjoitus OpenSSL:llä.
set -euo pipefail

main() {
    printf 'laiteohjelmisto v3.2\n' > paivitys.bin

    # @alku allekirjoitus
    openssl genpkey -algorithm ed25519 -out salainen.pem
    openssl pkey -in salainen.pem -pubout -out julkinen.pem
    openssl pkeyutl -sign -rawin -inkey salainen.pem \
        -in paivitys.bin -out paivitys.sig
    openssl pkeyutl -verify -rawin -pubin -inkey julkinen.pem \
        -in paivitys.bin -sigfile paivitys.sig
    # @loppu allekirjoitus

    printf 'takaovi\n' >> paivitys.bin
    if ! openssl pkeyutl -verify -rawin -pubin -inkey julkinen.pem \
        -in paivitys.bin -sigfile paivitys.sig > /dev/null 2>&1; then
        echo "muutettu tiedosto hylättiin"
    fi
    printf 'allekirjoitus: %s tavua\n' "$(wc -c < paivitys.sig)"
}

main "$@"
