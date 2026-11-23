#!/usr/bin/env bash
# Poistaa annetun hakemiston vanhat lokit. Lainaamaton muuttuja jakaisi
# välilyönnin sisältävän nimen kahdeksi argumentiksi.
set -euo pipefail

mkdir -p 'vanhat lokit'
touch 'vanhat lokit/a.log' 'vanhat lokit/b.log'
hakemisto='vanhat lokit'

rm -r $hakemisto            # @virhe
rm -r -- "$hakemisto"
[[ -e $hakemisto ]] || echo "poistettu: $hakemisto"
