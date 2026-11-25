# Verkkoinfrastruktuuri

Tiivis suomenkielinen tutoriaali verkkojen suunnitteluun ja ylläpitoon.
Esimerkit rakentavat oikeita verkkoja Linuxin verkkonimiavaruuksiin:
kytkimiä, reitittimiä (OSPF ja BGP BIRDillä), palomuureja (nftables),
DHCP-, DNS-, TFTP- ja RADIUS-palvelimia, QoS-jonotusta, WireGuard-tunneleita,
SSH-hyppykoneen sekä SNMP- ja NetFlow-valvonnan.

Valmis dokumentti: [verkkoinfrastruktuuri.pdf](https://saperant.github.io/tutoriaalit/materiaalit/verkkoinfrastruktuuri.pdf),
pikaopas: [verkkoinfrastruktuuri-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/verkkoinfrastruktuuri-pikaopas.pdf).

## Sisältö

1. Johdanto ja laboratorio
2. Suunnittelu, osoitteet ja segmentointi (kerrokset, kahdennettu
   yhdyskäytävä)
3. Kytkentä, VLANit ja silmukat (STP, linkkien yhdistäminen, VXLAN)
4. Reitityksen suunnittelu (staattinen, OSPF, BGP, politiikkareititys)
5. Palomuurit ja osoitteenmuunnos
6. Verkkopalvelut: DHCP, DNS ja verkkokäynnistys
7. Palvelun laatu
8. Langattomat verkot ja pääsynhallinta (802.1X, RADIUS)
9. VPN ja etäkäyttö (WireGuard, IPsec, hyppykone)
10. Valvonta ja vianetsintä (SNMPv3, NetFlow, tarkistuslista)
11. Verkko koodina
12. Lopuksi: nyrkkisäännöt, jatkotaidot ja lähteet

## Esimerkit

Esimerkit tarvitsevat pääkäyttäjän oikeudet (tai salasanattoman
`sudo`n) ja ytimen nimiavaruustuen. Kehityskontissa
(`.devcontainer/verkkoinfrastruktuuri`) kaikki tarvittava on valmiina.

```text
make testaa     # rakenne, ShellCheck, ruff, mypy ja kaikkien esimerkkien ajo
make pdf        # PDF ja pikaopas
bash esimerkit/05-palomuuri.sh   # yksittäinen laboratorio
```

Laboratorioiden topologiat on piirretty lukuihin Graphviz-kaavioina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.
