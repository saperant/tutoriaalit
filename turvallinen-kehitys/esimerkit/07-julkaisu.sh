#!/usr/bin/env bash
# Julkaisun tiivisteet ja allekirjoitus SSH-avaimella (ssh-keygen -Y).
# Käyttäjä tarkistaa ladatun paketin ennen kuin ajaa sitä.
set -euo pipefail

ssh-keygen -q -t ed25519 -N '' -C julkaisu@example.fi -f julkaisuavain
mkdir dist
printf 'tilauspalvelu 1.5.0\n' > dist/tilauspalvelu-1.5.0.tar.gz

# @alku allekirjoita
# Julkaisijan puolella: tiivistelista ja sen allekirjoitus.
(cd dist && sha256sum ./*.tar.gz > SHA256SUMS)
ssh-keygen -q -Y sign -f julkaisuavain -n julkaisu dist/SHA256SUMS
# @loppu allekirjoita

# @alku tarkista
# Käyttäjän puolella: luotettu avain on haettu erikseen, ei latauksen
# mukana (muuten hyökkääjä vaihtaa avaimen ja allekirjoituksen yhdessä).
printf 'julkaisu@example.fi %s\n' "$(cat julkaisuavain.pub)" > luotetut
tarkista() {
    if ssh-keygen -Y verify -f luotetut -I julkaisu@example.fi \
            -n julkaisu -s dist/SHA256SUMS.sig \
            < dist/SHA256SUMS >/dev/null 2>&1 \
        && (cd dist && sha256sum --quiet --check SHA256SUMS) \
            >/dev/null 2>&1; then
        echo "$1: kelpaa"
    else
        echo "$1: HYLÄTTY"
    fi
}
tarkista "alkuperäinen"
printf 'takaovi\n' >> dist/tilauspalvelu-1.5.0.tar.gz
tarkista "paketti muutettu"
(cd dist && sha256sum ./*.tar.gz > SHA256SUMS)
tarkista "paketti ja tiivistelista muutettu"
# @loppu tarkista
