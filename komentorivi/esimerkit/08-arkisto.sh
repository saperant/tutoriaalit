#!/usr/bin/env bash
# Varmuuskopio tarilla ja eheyden tarkistus tarkistussummilla.
set -euo pipefail
export LC_ALL=C

mkdir -p sivusto/kuvat
echo '<h1>Etusivu</h1>' > sivusto/index.html
echo 'body { margin: 0 }' > sivusto/tyyli.css
head -c 1000 /dev/zero > sivusto/kuvat/logo.png

# @alku tar
tar -czf sivusto.tar.gz --sort=name sivusto
tar -tzf sivusto.tar.gz
mkdir palautus
tar -xzf sivusto.tar.gz -C palautus
diff -r sivusto palautus/sivusto && echo "palautus vastaa alkuperäistä"
# @loppu tar

# @alku summat
(cd sivusto && find . -type f -print0 | sort -z \
    | xargs -0 sha256sum) > SHA256SUMS
echo 'body { margin: 1em }' > sivusto/tyyli.css
(cd sivusto && sha256sum -c ../SHA256SUMS) || echo "tarkistus epäonnistui"
# @loppu summat
