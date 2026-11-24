---
title: Tietoverkot
subtitle: Pikaopas · iproute2 · tcpdump · dig · Ubuntu 24.04
---

# Kerrokset

| Kerros | Protokollat | Osoite | Työkalu |
|--------|-------------|--------|---------|
| Sovellus | HTTP, DNS, DHCP, TLS | nimi, URL | `curl -v`, `dig` |
| Kuljetus | TCP, UDP, QUIC | portti | `ss -tlnp` |
| Verkko | IPv4, IPv6, ICMP | IP-osoite | `ip route get`, `ping` |
| Linkki | Ethernet, WLAN, ARP, NDP | MAC | `ip link`, `ip neigh` |

- EtherType: `0x0800` IPv4, `0x86dd` IPv6, `0x0806` ARP.
- IP-protokolla: 1 ICMP, 6 TCP, 17 UDP, 58 ICMPv6.
- Otsakkeet: Ethernet 14, IPv4 20–60, IPv6 40, UDP 8, TCP 20–60 tavua.

# iproute2

| Tehtävä | Komento |
|---------|---------|
| Liitännät | `ip -br link`, `ip link set eth0 up`, `… mtu 1400` |
| Osoitteet | `ip -br addr`, `ip addr add 192.0.2.10/24 dev eth0` |
| Reitit | `ip route`, `ip route add default via 192.0.2.1` |
| Reittipäätös | `ip route get 198.51.100.20` |
| Naapurit | `ip neigh` (ARP/NDP), tilat REACHABLE, STALE, FAILED |
| Nimiavaruus | `ip netns add x`, `ip -n x …`, `ip netns exec x cmd` |
| veth-pari | `ip -n a link add eth0 type veth peer name eth0 netns b` |
| Silta | `ip link add br0 type bridge`, `… master br0`, `bridge fdb` |
| Välitys | `sysctl -w net.ipv4.ip_forward=1` |
| Soketit | `ss -tln`, `ss -uan`, `ss -tnp state established` |

# IPv4

| Etuliite | Maski | Koneita |
|----------|-------|---------|
| /30 | 255.255.255.252 | 2 |
| /29 | 255.255.255.248 | 6 |
| /28 | 255.255.255.240 | 14 |
| /27 | 255.255.255.224 | 30 |
| /26 | 255.255.255.192 | 62 |
| /25 | 255.255.255.128 | 126 |
| /24 | 255.255.255.0 | 254 |
| /23 | 255.255.254.0 | 510 |
| /22 | 255.255.252.0 | 1022 |
| /16 | 255.255.0.0 | 65 534 |

- Yksityiset: `10/8`, `172.16/12`, `192.168/16`; CGNAT `100.64/10`.
- `169.254/16` = DHCP ei vastannut. `127/8` silmukka.
- Dokumentaatio: `192.0.2/24`, `198.51.100/24`, `203.0.113/24`.

# IPv6

- `2000::/3` julkinen, `fd00::/8` ULA, `fe80::/10` linkki, `ff00::/8`
  ryhmä, `::1` silmukka, `2001:db8::/32` dokumentaatio.
- Aliverkko `/64`. Linkkiosoite tarvitsee vyöhykkeen: `fe80::1%eth0`.
- URL: `http://[2001:db8::1]:8080/`. ICMPv6:ta ei saa estää kokonaan.

# Portit

| Portti | Palvelu | Portti | Palvelu |
|--------|---------|--------|---------|
| 22 | SSH | 123/udp | NTP |
| 25, 587 | SMTP | 443 | HTTPS, QUIC/udp |
| 53 | DNS | 3389 | RDP |
| 67/68 udp | DHCP | 5353/udp | mDNS |
| 80 | HTTP | 5432 | PostgreSQL |

# TCP

- Kättely `S`, `S.`, `.`; lopetus `F.` kumpaankin suuntaan.
- RST = portti kiinni; aikakatkaisu = suodatettu tai reitti puuttuu.
- `TIME_WAIT` 60 s sulkevalla puolella. MSS ≈ MTU − 40.
- MTU-oire: pienet pyynnöt toimivat, suuret jumittuvat.
  Testi: `ping -M do -s 1472 kohde`, `tracepath kohde`.

# tcpdump

| Tarve | Komento |
|-------|---------|
| Perus | `tcpdump -i eth0 -n` |
| Tiedostoon | `tcpdump -i any -n -w k.pcap 'port 53'` |
| Luku | `tcpdump -n -r k.pcap` |
| Suodattimia | `host x`, `net 10.0.0.0/8`, `port 443`, `icmp`, `not port 22` |
| Avaukset | `'tcp[tcpflags] & tcp-syn != 0'` |
| DHCP | `port 67 or port 68` |

# DNS

| Tarve | Komento |
|-------|---------|
| Osoite | `dig +short www.esim.fi A` |
| Tietyltä palvelimelta | `dig @192.0.2.53 nimi` |
| Polku juuresta | `dig +trace nimi` |
| Käänteinen | `dig -x 192.0.2.20` |
| Mitä ohjelma näkee | `getent hosts nimi` |
| Koneen asetukset | `resolvectl status`, `/etc/resolv.conf` |

- `NXDOMAIN` nimeä ei ole; `SERVFAIL` selvitys epäonnistui.
- Laske TTL ennen muutosta. CNAME ei vyöhykkeen juureen.

# HTTP ja TLS

- `curl -v https://x/` näyttää kättelyn ja otsakkeet.
- `curl --cacert ca.crt --resolve x:443:192.0.2.80 https://x/`.
- `openssl s_client -connect x:443 -servername x` näyttää ketjun.
- 4xx asiakkaan virhe, 5xx palvelimen; 502/504 = tausta ei vastaa.
- Varmenteen nimi on SAN-kentässä. Älä koskaan käytä `-k`:ta tuotannossa.

# Vianetsintä

1. `ip -br link` – UP ja LOWER_UP?
2. `ip -br addr` – osoite ja maski?
3. `ip route get KOHDE` – reitti ja lähdeosoite?
4. `ip neigh` – vastaako yhdyskäytävä?
5. `ping`, `tracepath` – mihin asti?
6. `ss -tln` / `curl -v` / `nc -vz` – portti?
7. `dig`, `getent hosts` – nimi?
8. Kaappaus molemmista päistä.
