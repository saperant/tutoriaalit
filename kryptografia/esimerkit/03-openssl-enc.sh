#!/usr/bin/env bash
# Tiedoston salaus salasanalla OpenSSL:n komentorivillä.
set -euo pipefail

main() {
    printf 'Luottamuksellinen raportti\n' > raportti.txt
    printf 'Pitkä-ja-satunnainen-salalause-42\n' > salasana.txt

    # @alku enc
    openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt \
        -pass file:salasana.txt -in raportti.txt -out raportti.1.enc
    openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt \
        -pass file:salasana.txt -in raportti.txt -out raportti.2.enc
    openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 \
        -pass file:salasana.txt -in raportti.1.enc -out purettu.txt
    # @loppu enc

    if cmp -s raportti.1.enc raportti.2.enc; then
        echo "salatut tiedostot ovat samat"
    else
        echo "salatut tiedostot eroavat (satunnainen suola)"
    fi
    cmp -s raportti.txt purettu.txt && echo "purku palautti alkuperäisen"
    printf 'otsake: %s\n' "$(head -c 8 raportti.1.enc)"
}

main "$@"
