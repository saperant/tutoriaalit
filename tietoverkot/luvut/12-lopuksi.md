# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Kerros kerrallaan.** Linkki, osoite, reitti, naapuri, portti, nimi,
   sovellus. Jokainen tarkistus rajaa vian.
2. **`ip route get` ennen arvailua.** Ydin kertoo, mitä se tekisi.
3. **Kaappaus kertoo totuuden.** Kun lokit ja oletukset ovat ristiriidassa,
   katso langalta. Kaappaa molemmista päistä.
4. **Torjunta ei ole aikakatkaisu.** RST tai ICMP-virhe tarkoittaa, että
   joku vastasi; hiljaisuus, että joku nieli paketin.
5. **Paluusuunta unohtuu.** Reitti, NAT ja palomuuri on mietittävä
   molempiin suuntiin.
6. **TCP on tavuvirta.** Kehystä viestit itse ja lue silmukassa.
7. **Kaikella verkossa on aikaraja.** Ilman sitä jumitus on vain ajan
   kysymys.
8. **Älä oleta IPv4:ää**, äläkä yhtä osoitetta per nimi. Käytä
   `getaddrinfo`a ja kokeile kaikki osoitteet.
9. **DNS-muutokset näkyvät TTL:n viiveellä.** Suunnittele muutokset sen
   mukaan.
10. **Älä kytke TLS:n tarkistuksia pois.** Korjaa luottamus.
11. **Jäsennä verkon data puolustavasti.** Se on hyökkääjän
    hallinnassa.

## Mihin tästä eteenpäin

- *Verkkoinfrastruktuuri*: VLANit, dynaaminen reititys, palomuurit,
  QoS, WLAN, RADIUS ja VPN:t.
- *Verkko-ohjelmointi*: soketit, protokollien suunnittelu,
  moniasiakaspalvelimet ja asynkroninen I/O.
- *Tietoturvan perusteet* ja *Kryptografia*: uhkat ja TLS:n
  rakennuspalikat.
- *Tietoliikennetekniikka*: siirtotiet, kapasiteetti ja kanavanvaraus.
- *Kontit ja pilvi* sekä *Hajautetut järjestelmät*: verkot konttien ja
  palveluiden välissä.

## Lähteet ja lisämateriaali

### Standardit

Internetin protokollat on määritelty RFC-dokumenteissa, jotka ovat
vapaasti luettavissa: <https://www.rfc-editor.org/>.

- RFC 791 (IPv4), RFC 8200 (IPv6), RFC 4861 (NDP), RFC 4862 (SLAAC)
- RFC 768 (UDP), RFC 9293 (TCP), RFC 9000 (QUIC)
- RFC 2131 (DHCP), RFC 1034 ja 1035 (DNS), RFC 6762 (mDNS)
- RFC 9110 (HTTP-semantiikka), RFC 9112 (HTTP/1.1), RFC 8446 (TLS 1.3)
- RFC 1918 (yksityiset osoitteet), RFC 5737 (dokumentaatio-osoitteet)

### Dokumentaatio ja työkalut

- Linuxin man-sivut: `ip(8)`, `ip-netns(8)`, `ss(8)`, `tcpdump(1)`,
  `pcap-filter(7)`, `dig(1)`, `dnsmasq(8)`.
- Wiresharkin käyttöopas: <https://www.wireshark.org/docs/>.
- Pythonin `socket`-, `ipaddress`- ja `ssl`-modulien dokumentaatio:
  <https://docs.python.org/3/library/>.
- IANA:n porttinumerot ja protokollanumerot:
  <https://www.iana.org/protocols>.

### Kirjat

- Kevin R. Fall ja W. Richard Stevens: *TCP/IP Illustrated, Volume 1*
  (2. painos). Protokollat kaappausten kautta.
- James F. Kurose ja Keith W. Ross: *Computer Networking: A Top-Down
  Approach*. Laaja oppikirja.
- Larry L. Peterson ja Bruce S. Davie: *Computer Networks: A Systems
  Approach*. Avoimesti verkossa (CC BY 4.0):
  <https://book.systemsapproach.org/>.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
