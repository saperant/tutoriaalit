# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Suunnitelma ennen kaapeleita.** Segmentit luottamuksen mukaan,
   hierarkkinen osoitteistus kasvuvaroineen ja sallittujen virtojen
   luettelo.
2. **Oletuksena esto.** Palomuurit, reitityspolitiikat ja pääsynhallinta
   luettelevat sallitun; kaikki muu estetään.
3. **Vähimmät oikeudet.** Segmentit, säännöt, SNMP-oikeudet ja
   VPN-verkot rajataan siihen, mitä tarvitaan.
4. **Hallintaverkko erillään.** Hallintaliitännät hallintaverkossa,
   pääsy VPN:n ja hyppykoneen kautta, ei koskaan internetistä.
5. **Pienet vikaantumisalueet.** L2 pieneksi, reititys niiden väliin,
   kahdennus kriittisiin palveluihin (DHCP, DNS, RADIUS, yhteydet).
6. **Suodata reitit molempiin suuntiin.** BGP-istunto ilman
   suodattimia on onnettomuus.
7. **Muutokset koodina.** Kuvaus versionhallinnassa on totuuden lähde;
   asetukset tuotetaan siitä, ja muutokset katselmoidaan ja testataan.
8. **Varmenna joka muutos.** Hyväksymistestit sallituille ja estetyille
   virroille ajetaan jokaisen muutoksen jälkeen.
9. **Valvo oireita.** Hälytys kertoo käyttäjiin vaikuttavasta
   oireesta, ja sillä on ohje.
10. **Dokumentoitu osoitesuunnitelma.** Jos suunnitelma on vain
    jonkun päässä, sitä ei ole.

## Mallit ja niiden tarkoitus

| Malli | Tarkoitus |
|-------|-----------|
| Pääsy–jakelu–runko, spine–leaf | rajattu vikaantumisalue, ennustettava kapasiteetti |
| Segmentointi ja vyöhykkeet | tietoturvaraja, valvottavat virrat |
| Hallintaverkko ja hyppykone | infrastruktuurin suojaaminen käyttäjäverkon vaarantuessa |
| Tilallinen palomuuri, oletuksena esto | vain luetellut virrat |
| Luottamusraja (QoS, DHCP snooping) | verkon reunalla tarkistetaan, sisällä luotetaan |
| Dynaaminen VLAN (802.1X + RADIUS) | pääsy käyttäjän ja laitteen mukaan, ei portin |
| Kuvaus, generaattori, varmennus | toistettavat ja katselmoitavat muutokset |

## Jatko taitopuussa

- *Palvelinympäristöt*: palvelimet, tallennus, varmuuskopiointi ja
  käyttäjähallinta tämän verkon päällä.
- *Tietoliikennetekniikka*: siirtotiet, kanavanvaraus ja
  matkaviestinverkot fyysiseltä puolelta.
- *Kontit ja pilvi*: verkot pilvessä ja konttiympäristöissä, joissa samat
  käsitteet ovat ohjelmallisia.
- *Palveluarkkitehtuurin tietoturva*: nollaluottamus, palvelujen
  identiteetit ja segmentointi palvelutasolla.

## Lähteet ja lisälukemista

- IETF:n RFC-dokumentit, <https://www.rfc-editor.org/>: esimerkiksi
  RFC 1918 (yksityiset osoitteet), RFC 2328 (OSPFv2), RFC 4271 (BGP-4),
  RFC 7938 (BGP konesaleissa), RFC 2474 (DSCP), RFC 8290 (fq_codel),
  RFC 2865 (RADIUS), RFC 7348 (VXLAN), RFC 7011 (IPFIX) ja
  RFC 3414 (SNMPv3:n käyttäjäpohjainen turvamalli).
- Linuxin ohjesivut: `ip(8)`, `bridge(8)`, `tc(8)`, `tc-htb(8)`,
  `nft(8)` ja `ip-netns(8)`.
- nftables-wiki, <https://wiki.nftables.org/>.
- BIRD-käyttöopas, <https://bird.network.cz/>.
- dnsmasqin ohjesivu ja esimerkit, <https://thekelleys.org.uk/dnsmasq/doc.html>.
- FreeRADIUS-dokumentaatio, <https://www.freeradius.org/documentation/>,
  ja BlastRADIUS-tiedote, <https://www.blastradius.fail/>.
- WireGuard, <https://www.wireguard.com/>, ja Jason A. Donenfeldin
  artikkeli *WireGuard: Next Generation Kernel Network Tunnel* (NDSS
  2017).
- strongSwanin dokumentaatio, <https://docs.strongswan.org/>.
- MANRS-ohjelma reititysturvallisuudelle, <https://manrs.org/>.
- Kirjat: Russ White ja Ethan Banks, *Computer Networking Problems and
  Solutions* (Addison-Wesley, 2017); Ivan Pepelnjak, *ipSpace.net*-blogi
  ja -materiaalit; Christian Adell, Scott S. Lowe ja Matt Oswalt,
  *Network Programmability and Automation* (O'Reilly, 2. p. 2023).
- Kyberturvallisuuskeskuksen ohjeet verkkojen suojaamiseen,
  <https://www.kyberturvallisuuskeskus.fi/>.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkien koodi kuuluu
samaan lisenssiin.
