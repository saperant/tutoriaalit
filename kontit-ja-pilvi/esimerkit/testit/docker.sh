#!/usr/bin/env bash
# Rakentaa kuvat ja ajaa ne oikeasti: testit-vaihe, kuvien ominaisuudet,
# cgroupin muistiraja, Compose-sovellus ja Helm-kaavion renderöinti.
# Tuloste verrataan tiedostoon docker.odotettu.
set -euo pipefail
cd "$(dirname "$0")/.."

HELM_KUVA="alpine/helm:3.19.0@sha256:\
aef9b56f64e866207d9591d0abd8f6d767b36aadd12edf68f8a719716d9d29c9"
projekti="kp-testi-$$"
export API_PORTTI
API_PORTTI=$(python3 -c 'import socket; s=socket.socket(); \
s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
tmp=$(mktemp -d)
siivoa() {
    docker compose -p "$projekti" down -v >/dev/null 2>&1 || true
    rm -rf "$tmp"
}
trap siivoa EXIT

echo "== testit-vaihe"
docker build -q --target testit sovellus >/dev/null && echo "testit läpi"

echo "== kuvat"
docker build -q --target ajo --build-arg VERSIO=1.0.0 \
    -t kaynnit:1.0.0 sovellus >/dev/null
docker build -q -t staattinen:1.0.0 staattinen >/dev/null
muoto='käyttäjä {{.Config.User}}, terveys {{.Config.Healthcheck.Test}}'
for kuva in kaynnit:1.0.0 staattinen:1.0.0; do
    echo "$kuva: $(docker image inspect --format "$muoto" "$kuva")"
done
koko() { docker image inspect --format '{{.Size}}' "$1"; }
pieni=$(koko staattinen:1.0.0)
suuri=$(koko kaynnit:1.0.0)
echo "staattinen alle 20 Mt: $( ((pieni < 20000000)) && echo kyllä)"
echo "Python-kuva yli 5 kertaa suurempi: $( ((suuri > 5 * pieni)) \
    && echo kyllä)"

echo "== muistiraja cgroupissa (--memory 64m)"
docker run --rm --memory 64m --entrypoint sh kaynnit:1.0.0 -c \
    'cat /sys/fs/cgroup/memory.max 2>/dev/null ||
     cat /sys/fs/cgroup/memory/memory.limit_in_bytes'

echo "== compose"
# @alku compose
docker compose -p "$projekti" up -d --wait --wait-timeout 90 >/dev/null 2>&1
osoite="http://127.0.0.1:$API_PORTTI"
curl -fsS "$osoite/"; echo
curl -fsS "$osoite/"; echo
echo "laskuri käynnistetään uudelleen: arvo säilyy volyymissa"
docker compose -p "$projekti" restart laskuri >/dev/null 2>&1
docker compose -p "$projekti" up -d --wait --wait-timeout 90 >/dev/null 2>&1
curl -fsS "$osoite/"; echo
echo "api pysäytetään (SIGTERM): viimeinen lokirivi"
docker compose -p "$projekti" stop api >/dev/null 2>&1
docker compose -p "$projekti" logs --no-log-prefix api | tail -n 1
# @loppu compose

echo "== helm"
helm() {
    docker run --rm -v "$PWD/helm:/helm:ro" "$HELM_KUVA" "$@"
}
helm lint /helm/kaynnit -f /helm/kaynnit/values-tuotanto.yaml --quiet \
    >/dev/null && echo "lint läpi"
helm template kaynnit /helm/kaynnit --namespace kaynnit \
    -f /helm/kaynnit/values-tuotanto.yaml > "$tmp/tuotanto.yaml"
helm template kaynnit /helm/kaynnit --namespace kaynnit \
    -f /helm/kaynnit/values-tuotanto.yaml \
    --show-only templates/hpa.yaml > "$tmp/hpa.yaml"
diff -u helm/tuotanto.odotettu "$tmp/tuotanto.yaml" \
    && echo "renderöinti vastaa tiedostoa helm/tuotanto.odotettu"
diff -u helm/hpa.odotettu "$tmp/hpa.yaml" \
    && echo "HPA vastaa tiedostoa helm/hpa.odotettu"
kubernetes-validate --quiet -k 1.35.0 --strict "$tmp/tuotanto.yaml" \
    && echo "renderöity kaavio on kelvollinen Kubernetes 1.35:lle"
python3 politiikka.py "$tmp/tuotanto.yaml" | tail -n 1
