#!/usr/bin/env bash
# Tiivisteet ja HMAC OpenSSL:llä sekä tiedoston eheyden tarkistus.
set -euo pipefail

main() {
    # @alku dgst
    printf 'abc' | openssl dgst -sha256 -r
    printf 'what do ya want for nothing?' \
        | openssl dgst -sha256 -hmac Jefe -r
    # @loppu dgst

    # @alku tarkistus
    printf 'julkaisu 1.4.2\n' > julkaisu.tar
    sha256sum julkaisu.tar > SHA256SUMS
    sha256sum --check SHA256SUMS
    printf 'x' >> julkaisu.tar
    sha256sum --check --quiet SHA256SUMS >/dev/null 2>&1 \
        || echo "julkaisu.tar: tiiviste ei täsmää"
    # @loppu tarkistus
}

main "$@"
