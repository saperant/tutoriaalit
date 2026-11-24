# shellcheck shell=bash
# Verkkolaboratorion apufunktiot. Esimerkit ottavat tämän käyttöön
# komennolla `source "$(dirname "$0")/labra.sh"`.
#
# Jokainen solmu (isäntä, kytkin tai reititin) on oma verkkonimiavaruutensa,
# ja solmut yhdistetään veth-pareilla kuin kaapeleilla. Nimiavaruuksien
# nimissä on ajokohtainen etuliite, joten useaa laboratoriota voi ajaa
# rinnakkain. Kaikki poistetaan, kun skripti päättyy.
set -euo pipefail

LABRA="vi$$"
LABRA_HAK=$(mktemp -d)
LABRA_SOLMUT=()
LABRA_LINKIT=0

# @alku juuri
# Verkon asetukset vaativat pääkäyttäjän oikeudet. Tavallinen käyttäjä
# käyttää sudoa, joka ei saa kysyä salasanaa (-n).
juuri() {
    if [[ $EUID -eq 0 ]]; then "$@"; else sudo -n "$@"; fi
}
# @loppu juuri

# @alku solmu
# solmu NIMI: uusi nimiavaruus, jossa loopback on ylhäällä.
solmu() {
    juuri ip netns add "$LABRA-$1"
    LABRA_SOLMUT+=("$LABRA-$1")
    juuri ip -n "$LABRA-$1" link set lo up
}

# ns NIMI KOMENTO...: ajaa komennon solmun nimiavaruudessa.
ns() {
    local nimi=$1
    shift
    juuri ip netns exec "$LABRA-$nimi" "$@"
}

# linkki A LIITÄNTÄ B LIITÄNTÄ: kaapeli kahden solmun välille.
# MAC-osoitteet ovat ennustettavia: 02:00:00:00:<linkki>:01 ja :02.
linkki() {
    LABRA_LINKIT=$((LABRA_LINKIT + 1))
    local n
    n=$(printf '%02x' "$LABRA_LINKIT")
    juuri ip link add name "$2" netns "$LABRA-$1" \
        address "02:00:00:00:$n:01" \
        type veth peer name "$4" netns "$LABRA-$3" \
        address "02:00:00:00:$n:02"
    juuri ip -n "$LABRA-$1" link set dev "$2" up
    juuri ip -n "$LABRA-$3" link set dev "$4" up
}
# @loppu solmu

# tavoittaa SOLMU OSOITE: tulostaa "ok" tai "ei yhteyttä" yhdellä pingillä.
tavoittaa() {
    if ns "$1" ping -c 1 -W 1 "$2" > /dev/null 2>&1; then
        echo "$1 -> $2: ok"
    else
        echo "$1 -> $2: ei yhteyttä"
    fi
}

# odota SEKUNNIT KOMENTO...: toistaa komentoa, kunnes se onnistuu.
odota() {
    local raja=$1
    shift
    local i
    for ((i = 0; i < raja * 5; i++)); do
        if "$@" > /dev/null 2>&1; then return 0; fi
        sleep 0.2
    done
    echo "aikaraja: $*" >&2
    return 1
}

# lopeta SIGNAALI: lähettää signaalin kaikille laboratorion prosesseille.
lopeta() {
    local s pids
    for s in "${LABRA_SOLMUT[@]}"; do
        pids=$(juuri ip netns pids "$s" 2> /dev/null || true)
        if [[ -n $pids ]]; then
            # shellcheck disable=SC2086 # pidit ovat erillisiä sanoja
            juuri kill "-$1" $pids 2> /dev/null || true
        fi
    done
}

labra_siivoa() {
    local s
    lopeta TERM
    sleep 0.3
    lopeta KILL
    for s in "${LABRA_SOLMUT[@]}"; do
        juuri ip netns del "$s" 2> /dev/null || true
    done
    # wireguard-go:n hallintasoketit (liitäntöjen nimet alkavat etuliitteellä)
    juuri rm -f "/var/run/wireguard/$LABRA"*.sock
    juuri rm -rf "$LABRA_HAK"
}
trap labra_siivoa EXIT
