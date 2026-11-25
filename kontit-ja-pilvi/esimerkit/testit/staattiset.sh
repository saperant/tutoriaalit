#!/usr/bin/env bash
# Tarkistukset, jotka eivät tarvitse Dockeria: kielten tarkistimet,
# yksikkötestit, Dockerfilet, Compose, Kubernetes-manifestit, putki ja
# odotetut tulosteet. Pysähtyy ensimmäiseen virheeseen.
set -euo pipefail
cd "$(dirname "$0")/.."
k8s=1.35.0

# vertaa ODOTETTU KOMENTO...: komennon tuloste (myös virhetuloste ja
# epäonnistuminen) verrataan tiedostoon.
vertaa() {
    local odotettu=$1
    shift
    diff -u "$odotettu" <("$@" 2>&1 || true)
    echo "OK: $odotettu"
}

echo "== Python"
ruff check --no-cache --quiet .
mypy --no-error-summary sovellus/*.py politiikka.py iac/tila.py \
    ci/putki_verkko.py
(cd sovellus && python3 -m unittest -q 2>&1 | tail -n 1)

echo "== kuoriskriptit"
shellcheck nimiavaruudet.sh iac/aja.sh testit/*.sh

echo "== Dockerfilet"
hadolint --no-color sovellus/Dockerfile staattinen/Dockerfile
echo "OK: hadolint, ei huomautettavaa"
hadolint_lyhyt() {
    hadolint -f json "$1" | python3 -c 'import json, sys
for h in json.load(sys.stdin):
    print(h["line"], h["code"], h["level"])'
}
vertaa huono/hadolint.odotettu hadolint_lyhyt huono/Dockerfile

echo "== YAML, Compose ja putki"
yamllint -s compose.yaml k8s k8s-huono ci .yamllint.yaml \
    helm/kaynnit/Chart.yaml helm/kaynnit/values*.yaml
check-jsonschema -q --builtin-schema vendor.compose-spec compose.yaml
check-jsonschema -q --builtin-schema vendor.github-workflows ci/palvelu.yml
echo "OK: compose.yaml ja ci/palvelu.yml vastaavat skeemojaan"
# Luvun 11 kaavio tuotetaan putkitiedostosta.
vertaa ci/putki.dot python3 ci/putki_verkko.py ci/palvelu.yml

echo "== Kubernetes"
kubernetes-validate --quiet -k "$k8s" --strict k8s/*.yaml
echo "OK: k8s/ on kelvollinen Kubernetes $k8s:lle"
kv_lyhyt() {
    kubernetes-validate -k "$k8s" --strict "$1" 2>&1 | sed -E \
        's/^ERROR (\S+) did not validate for resource (\S+) against version [0-9.]+: (.*)$/VIRHE \1: \2\n  \3/'
}
vertaa k8s-huono/kirjoitusvirhe.odotettu kv_lyhyt k8s-huono/kirjoitusvirhe.yaml
python3 politiikka.py k8s/*.yaml
vertaa k8s-huono/politiikka.odotettu python3 politiikka.py \
    k8s-huono/deployment.yaml

echo "== infrastruktuuri koodina"
vertaa iac/aja.odotettu iac/aja.sh

if command -v go >/dev/null; then
    echo "== Go"
    test -z "$(gofmt -l staattinen)"
    (cd staattinen && go vet ./...)
    echo "OK: gofmt ja go vet"
fi
