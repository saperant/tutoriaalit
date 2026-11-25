#!/usr/bin/env bash
# TCP:n uudelleenlähetys kaapattuna: palvelimen palomuurisääntö pudottaa
# ensimmäisen datasegmentin, ja asiakkaan ydin lähettää sen uudelleen.
set -euo pipefail
if [[ $EUID -ne 0 ]]; then exec sudo -n -- bash "$0" "$@"; fi
export LC_ALL=C
# Konteissa /proc/sys on usein vain luettavissa, mutta nimiavaruuksien
# asetukset (sysctl) on voitava kirjoittaa.
if [[ ! -w /proc/sys/net/ipv4/ip_forward ]]; then
    mount -o remount,rw /proc/sys
fi

uusi_ns() {
    ip netns add "$1"
    if [[ -d /proc/sys/net/ipv6 ]]; then
        ip netns exec "$1" sysctl -qw net.ipv6.conf.all.disable_ipv6=1 \
            net.ipv6.conf.default.disable_ipv6=1
    fi
}
HAK=$(cd "$(dirname "$0")" && pwd)
N=tv-havio$$
A=$N-a B=$N-b
T=$(mktemp -d)
siivoa() {
    ip netns del "$A" 2>/dev/null || true
    ip netns del "$B" 2>/dev/null || true
    rm -rf "$T"
}
trap siivoa EXIT

uusi_ns "$A"; uusi_ns "$B"
ip -n "$A" link add eth0 type veth peer name eth0 netns "$B"
ip -n "$A" addr add 192.0.2.1/24 dev eth0
ip -n "$B" addr add 192.0.2.2/24 dev eth0
ip -n "$A" link set eth0 up
ip -n "$B" link set eth0 up
# Aikaleimaoptio pois, jotta kaappaus on joka kerta samanlainen.
ip netns exec "$A" sysctl -qw net.ipv4.tcp_timestamps=0
ip netns exec "$B" sysctl -qw net.ipv4.tcp_timestamps=0

# @alku pudotus
# Palvelimen palomuuri pudottaa ensimmäisen dataa kantavan segmentin.
# numgen laskee sääntöön osuneita paketteja nollasta alkaen, joten vain
# ensimmäinen osuma pudotetaan ja uudelleenlähetys pääsee läpi.
ip netns exec "$B" nft -f - <<'NFT'
table inet labra {
    chain sisaan {
        type filter hook input priority 0;
        tcp dport 8080 tcp flags & psh == psh numgen inc mod 1000 0 drop
    }
}
NFT
# @loppu pudotus

# Kaapataan lähettäjän päässä: siellä näkyvät molemmat lähetykset.
ip netns exec "$A" tcpdump --immediate-mode -Z root -i eth0 -n \
    -w "$T/tcp.pcap" tcp 2> "$T/tcpdump.log" &
TCPDUMP=$!
until grep -q listening "$T/tcpdump.log" 2>/dev/null; do sleep 0.1; done

ip netns exec "$B" python3 "$HAK/07-yhteys.py" palvelin 192.0.2.2 8080 &
PALVELIN=$!
sleep 0.3
# @alku liikenne
ip netns exec "$A" nstat -n                     # nollaa laskurien vertailun
ip netns exec "$A" python3 "$HAK/07-yhteys.py" \
    asiakas 192.0.2.2 8080 "hei" 40000
ip netns exec "$A" nstat -a TcpRetransSegs | awk 'NR > 1 {print $1, $2}'
# @loppu liikenne
wait "$PALVELIN"
sleep 0.3
kill -INT "$TCPDUMP"; wait "$TCPDUMP" || true

# Sama tulkinta kuin esimerkissä 07-kattely.sh. Segmentti, jonka
# järjestysnumero ja pituus on jo nähty, merkitään uudelleenlähetykseksi.
tcpdump -r "$T/tcp.pcap" -n -t -S 2> /dev/null | awk '
function kentta(nimi,    arvo) {
    if (!match($0, nimi " [0-9]+")) return ""
    return substr($0, RSTART + length(nimi) + 1, RLENGTH - length(nimi) - 1)
}
{
    sub(/:$/, "", $4)
    mista = ($2 ~ /40000$/) ? "asiakas" : "palvelin"
    minne = ($4 ~ /40000$/) ? "asiakas" : "palvelin"
    match($0, /Flags \[[^]]*\]/)
    liput = substr($0, RSTART + 6, RLENGTH - 6)
    seq = kentta("seq"); ack = kentta("ack"); pituus = kentta("length")
    if (liput ~ /S/) isn[mista] = seq
    rivi = sprintf("%-8s > %-8s %-5s", mista, minne, liput)
    if (seq != "") rivi = rivi sprintf(" seq %d", seq - isn[mista])
    if (ack != "") rivi = rivi sprintf(" ack %d", ack - isn[minne])
    rivi = rivi " data " pituus
    if (pituus > 0 && nahty[mista, seq]++) rivi = rivi "  uudelleenlähetys"
    rivit[++n] = rivi
    pelkka[n] = (liput == "[.]" && pituus == 0)
}
END {
    for (i = 1; i <= n; i++)
        if (!pelkka[i] || i == 3 || i == n) print rivit[i]
}'
