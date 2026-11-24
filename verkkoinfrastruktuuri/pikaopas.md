---
title: Verkkoinfrastruktuuri
subtitle: Pikaopas · iproute2 · nftables · BIRD 2 · dnsmasq · tc · WireGuard
---

# Laboratorio

| Tehtävä | Komento |
|---------|---------|
| Nimiavaruus | `ip netns add r1`, `ip netns exec r1 komento`, `ip -n r1 …` |
| Kaapeli | `ip link add a netns r1 type veth peer name b netns r2` |
| Liitäntä ylös | `ip -n r1 link set dev a up` |
| Osoite | `ip -n r1 addr add 10.0.0.1/24 dev a` |
| Välitys päälle | `ip netns exec r1 sysctl -w net.ipv4.ip_forward=1` |
| Siivous | prosessit `ip netns pids r1`, sitten `ip netns del r1` |

# Tila ja vianetsintä

| Kysymys | Komento |
|---------|---------|
| Liitännät ja osoitteet | `ip -br link`, `ip -br addr` |
| Mitä reittiä käytetään? | `ip route get 10.2.0.10 from 10.1.0.5` |
| Naapurit (ARP/ND) | `ip neigh` |
| Kytkimen välitystaulu | `bridge fdb show br br0 dynamic` |
| STP-tilat | `bridge link show` |
| Kuuntelevat palvelut | `ss -ltnup` |
| Kaappaus | `tcpdump -ni eth0 -e host 10.0.0.5` |
| Palomuurin seuranta | `nft monitor trace`, `nft list ruleset` |

# Kytkentä

```{.bash tiedosto="esimerkit/03-kytkin.sh" osa="silta"}
```

- VLAN-tietoinen silta: `type bridge vlan_filtering 1`, sitten
  `bridge vlan add dev p1 vid 20 pvid untagged` (pääsy) ja
  `bridge vlan add dev up1 vid 20` (runko).
- STP: `type bridge stp_state 1 priority 4096`; juuri valitaan käsin.
- VXLAN: `type vxlan id 100 dstport 4789 local A remote B dev runko`.

# Reititys

| Tehtävä | Komento |
|---------|---------|
| Staattinen | `ip route add 10.2.0.0/24 via 172.16.12.2` |
| Oletusreitti | `ip route add default via 10.1.0.1` |
| Oma taulu | `ip route add default via X table 100` |
| Sääntö | `ip rule add from 10.30.0.0/24 lookup 100 priority 1000` |
| BIRD | `bird -c conf -s ctl`, `birdc -s ctl show protocols` |
| BIRD-reitit | `birdc -s ctl show route [filtered] protocol nimi` |

```{.bash tiedosto="esimerkit/04-bgp.sh" osa="operaattori"}
```

# Palomuuri (nftables)

```{.bash tiedosto="esimerkit/05-palomuuri.sh" osa="saannot"}
```

- Lataus atomisesti: `nft -f säännöt.nft`, tarkistus `nft -c -f`.
- Joukko: `nft add element inet t joukko '{ 10.0.0.5 }'`.
- Lokitus: `log prefix "esto: " limit rate 5/second`.

# Verkkopalvelut

| Palvelu | Asetus (dnsmasq) |
|---------|------------------|
| Alue ja vuokra | `dhcp-range=10.40.0.100,10.40.0.199,255.255.255.0,12h` |
| Optiot | `dhcp-option=option:router,10.40.0.1` |
| Varaus | `dhcp-host=02:00:00:00:03:01,tulostin,10.40.0.20` |
| PXE | `dhcp-boot=ipxe.efi`, `enable-tftp`, `tftp-root=…` |
| Paikallinen nimi | `address=/nas.toimisto.lan/10.40.0.30` |

# Palvelun laatu (tc)

```{.bash tiedosto="esimerkit/07-qos.sh" osa="htb"}
```

- Laskurit: `tc -s class show dev wan`; AQM: `fq_codel`, `cake`.
- DSCP: EF = 46 (ToS 0xb8), AF41 = 34, CS0 = 0.

# RADIUS ja 802.1X

- Testi: `radtest käyttäjä salasana palvelin 0 salaisuus`.
- Dynaaminen VLAN: `Tunnel-Type = VLAN`, `Tunnel-Medium-Type = IEEE-802`,
  `Tunnel-Private-Group-Id = "20"`.
- Asiakkaalle `require_message_authenticator = yes` (BlastRADIUS).

# WireGuard

| Tehtävä | Komento |
|---------|---------|
| Avaimet | `wg genkey > k.key`, `wg pubkey < k.key > k.pub` (umask 077) |
| Liitäntä | `ip link add wg0 type wireguard` |
| Vastapää | `wg set wg0 peer PUB endpoint IP:51820 allowed-ips VERKKO` |
| Tila | `wg show wg0 latest-handshakes`, `wg show wg0 transfer` |

# SSH hyppykoneen kautta

```{.bash tiedosto="esimerkit/09-hyppykone.sh" osa="asiakas"}
```

# Valvonta

| Tehtävä | Komento |
|---------|---------|
| SNMPv3 | `snmpget -v3 -l authPriv -u K -a SHA-256 -A … -x AES -X … IP OID` |
| Nimi, sijainti | `.1.3.6.1.2.1.1.5.0`, `.1.3.6.1.2.1.1.6.0` |
| Liitännät | `snmpwalk … .1.3.6.1.2.1.2.2.1.2` |
| Virrat | `nfdump -R hak -A proto,srcip,dstip,dstport 'dst port < 1024'` |
