# Tietoverkot

Tiivis suomenkielinen tutoriaali Internetin protokollista ohjelmoijalle
ja ylläpitäjälle. Protokollat opitaan kahdesta suunnasta: viestit
rakennetaan ja jäsennetään tavu tavulta Pythonilla, ja niiden toiminta
nähdään oikeassa verkossa, joka rakennetaan Linuxin
verkkonimiavaruuksilla. Valmiit dokumentit:
[tietoverkot.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietoverkot.pdf) ja pikaopas
[tietoverkot-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietoverkot-pikaopas.pdf).

## Sisältö

1. Johdanto – rajaukset, verkkonimiavaruudet laboratoriona, työkalut
2. Kerrokset ja kapselointi – OSI ja TCP/IP, kehys tavu tavulta,
   tarkistussumma
3. Ethernet, ARP ja kytkentä – MAC-osoitteet, naapuritaulu, oppiva
   kytkin, Linux-silta
4. IPv4 ja aliverkot – CIDR, erityisosoitteet, aliverkkosuunnitelma
5. Reititys ja NAT – pisin etuliite, reititin, paluureitti, NAT
6. IPv6 – osoitteet, SLAAC, NDP
7. TCP, UDP ja portit – `ss`, viestirajat, kättely kaapattuna, MTU ja
   pilkkominen
8. DHCP – DORA, viestin rakenne, dnsmasq ja oma asiakas
9. DNS ja mDNS – viestin koodaus ja purku, oma vyöhyke, mDNS
10. HTTP ja TLS – HTTP/1.1 tekstinä, HTTP/2 ja /3, varmenneketju
11. Liikenteen analyysi ja vianetsintä – tcpdump, pcap, vianetsintä
    kerros kerrallaan
12. Lopuksi – nyrkkisäännöt, lähteet

## Esimerkit

`make testaa` tarkistaa rakenteen ja ajaa kaikki esimerkit
(Python: ruff ja mypy --strict; Bash: ShellCheck). Verkkonimiavaruuksia
käyttävät esimerkit vaativat pääkäyttäjän oikeudet ja käynnistävät
itsensä tarvittaessa `sudo -n`:llä. Kehityskontissa
(`.devcontainer/tietoverkot`) on kaikki työkalut, ja se ajetaan
etuoikeutettuna (`--privileged`), koska nimiavaruudet vaativat
liitostoimintoja, joita isännän AppArmor muuten estää.

Lisenssi: CC BY-SA 4.0.
