#!/usr/bin/env bash
# Riippuvuussekaannus (dependency confusion) kahdella paikallisella
# pakettilähteellä: sisäinen ja "julkinen". Ei verkkoa.
set -euo pipefail

# Tekee minimaalisen wheel-paketin: nimi, versio ja yksi moduli.
tee_paketti() {   # hakemisto nimi versio viesti
    python3 - "$@" <<'PY'
import sys, zipfile
hak, nimi, versio, viesti = sys.argv[1:]
mod = nimi.replace("-", "_")
dist = f"{mod}-{versio}.dist-info"
with zipfile.ZipFile(f"{hak}/{mod}-{versio}-py3-none-any.whl", "w") as z:
    z.writestr(f"{mod}.py", f"print({viesti!r})\n")
    z.writestr(f"{dist}/METADATA", "Metadata-Version: 2.1\n"
               f"Name: {nimi}\nVersion: {versio}\n")
    z.writestr(f"{dist}/WHEEL", "Wheel-Version: 1.0\nGenerator: esim\n"
               "Root-Is-Purelib: true\nTag: py3-none-any\n")
    z.writestr(f"{dist}/RECORD", "")
PY
}

hae() {   # tulostaa ladatun tiedoston nimen
    rm -rf lataus
    python3 -m pip download -q --no-index --no-deps --dest lataus \
        --find-links sisainen --find-links julkinen "$@" 2>/dev/null \
        && ls lataus || echo "lataus hylätty"
}

mkdir sisainen julkinen
# @alku lahteet
tee_paketti sisainen yritys-laskutus 1.2.0 "yrityksen oma koodi"
tee_paketti julkinen yritys-laskutus 99.0.0 "hyokkaajan koodi"
# @loppu lahteet

# @alku haku
echo "ilman kiinnitystä:"
hae yritys-laskutus

echo "versio ja tiiviste kiinnitetty:"
tiiviste=$(sha256sum sisainen/*.whl | cut -d' ' -f1)
printf 'yritys-laskutus==1.2.0 --hash=sha256:%s\n' "$tiiviste" \
    > requirements.txt
hae --require-hashes -r requirements.txt

echo "sisäinen lähde ei vastaa, julkisessa sama versio:"
rm julkinen/*.whl sisainen/*.whl
tee_paketti julkinen yritys-laskutus 1.2.0 "hyokkaajan koodi"
hae --require-hashes -r requirements.txt
# @loppu haku
