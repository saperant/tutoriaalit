# Johdanto {.runko-johdanto}

Verkkoinfrastruktuuri on se osa tietojärjestelmää, jonka huomaa vasta
kun se ei toimi. Kytkimet, reitittimet, palomuurit, langattomat
tukiasemat, nimi- ja osoitepalvelut, etäyhteydet ja valvonta muodostavat
alustan, jonka päällä kaikki muu ajetaan. Huonosti suunniteltu verkko ei
yleensä kaadu kerralla, vaan se kerää vuosien mittaan poikkeuksia,
käsin tehtyjä muutoksia ja dokumentoimattomia riippuvuuksia, kunnes
yksikään ihminen ei enää tiedä, miksi jokin toimii.

Tämä tutoriaali opettaa verkkojen suunnittelua ja ylläpitoa: miten
osoitteet ja segmentit suunnitellaan, miten kytkentä, reititys ja
palomuurit rakennetaan, miten verkkopalvelut, palvelun laatu, langattomat
verkot, etäyhteydet ja valvonta toteutetaan, ja miten verkkoa
muutetaan hallitusti koodina. Protokollien perusteet (Ethernet, ARP, IP,
TCP, UDP, DNS, TLS) opetetaan taidossa *Tietoverkot*, ja tässä niihin
viitataan.

## Esitiedot ja rajaus

Tutoriaali on tarkoitettu ylläpitäjälle, infrastruktuuri- ja
DevOps-insinöörille sekä ohjelmistokehittäjälle, joka haluaa ymmärtää,
mitä hänen palvelunsa alla tapahtuu. Esitietona on taito *Tietoverkot*:
kerrosmalli, Ethernet ja ARP, IP-osoitteet ja aliverkot, reititystaulu,
NAT, TCP ja UDP, DHCP ja DNS sekä `ip`- ja `tcpdump`-komennot oletetaan
tutuiksi, ja niistä kerrataan vain se, mitä suunnittelu tarvitsee.
Bash-skriptejä luetaan, mutta niitä ei tarvitse osata kirjoittaa.

Tutoriaalin ulkopuolelle jäävät:

- siirtotiet, radiotekniikka ja jonoteoria (taito
  *Tietoliikennetekniikka*)
- palvelimet, tallennus ja konfiguraationhallinta (taito
  *Palvelinympäristöt*)
- konttien ja pilvialustojen verkot (taito *Kontit ja
  pilvi-infrastruktuuri*)
- palvelujen välinen todennus ja nollaluottamus (taito
  *Palveluarkkitehtuurin tietoturva*).

## Laboratorio: verkot nimiavaruuksissa

Verkkoja ei opi lukemalla. Tämän tutoriaalin esimerkit rakentavat
oikeita verkkoja: reitittimiä, kytkimiä, palomuureja, DHCP- ja
RADIUS-palvelimia sekä VPN-tunneleita. Laitteita ei tarvita, sillä
Linuxin *verkkonimiavaruus* (*network namespace*) on täysin erillinen
verkkopino: omat liitännät, osoitteet, reititystaulut, palomuurisäännöt
ja ARP-taulut. Kaksi nimiavaruutta yhdistetään *veth-parilla*, joka
toimii kuin kaapeli: kehys, joka lähetetään toiseen päähän, tulee ulos
toisesta.

Jokainen esimerkki on itsenäinen skripti, joka rakentaa verkkonsa,
ajaa kokeen ja purkaa verkon. Skriptit ottavat käyttöön pienen
apukirjaston `labra.sh`. Sen keskeiset funktiot ovat:

```{.bash tiedosto="esimerkit/labra.sh" osa="solmu"}
```

Funktio `ns h1 ip addr add …` on lyhenne komennosta `ip netns exec
<nimiavaruus> ip addr add …`. Kaikki verkkoasetukset vaativat
pääkäyttäjän oikeudet, joten kirjasto käyttää tavalliselle käyttäjälle
`sudo`a:

```{.bash tiedosto="esimerkit/labra.sh" osa="juuri"}
```

Nimiavaruuksien nimiin lisätään ajokohtainen etuliite, joten saman
esimerkin voi ajaa useaan kertaan rinnakkain, ja kaikki poistetaan, kun
skripti päättyy, myös virhetilanteessa. MAC-osoitteet asetetaan
ennustettaviksi, jotta tulosteet ovat samat joka ajolla.

Pienin laboratorio on kaksi isäntää samassa aliverkossa:

```{.bash tiedosto="esimerkit/01-kaapeli.sh" osa="verkko"}
```

```{.tuloste tiedosto="esimerkit/01-kaapeli.odotettu"}
```

Isäntä `h1` selvitti naapurinsa MAC-osoitteen ARPilla ennen kuin se
pystyi lähettämään ensimmäisen IP-paketin. Sama tapahtuu jokaisessa
lähiverkossa.

## Mitä laboratoriossa ei voi tehdä

Nimiavaruudet jakavat saman ytimen, joten niissä toimii se, minkä ydin
osaa. Tutoriaalin testiympäristöjen ytimissä ei kaikissa ole
802.1Q-VLAN-tukea, IPsecin ESP-muunnosta eikä viiveen ja häviön
simulointia (`netem`). Näiden kohdalla tutoriaali näyttää asetukset
ja kertoo selvästi, ettei niitä ajeta automaattisesti. Samoin radioon ja
laitteistoon sidotut asiat, kuten WLAN-kanavasuunnittelu ja kytkimen
porttikohtainen 802.1X, kuvataan konfiguraatioina.

Tuotannossa samat asiat tehdään kytkimissä, reitittimissä ja
palomuureissa, joiden käyttöliittymä vaihtelee valmistajittain. Käsitteet
ja periaatteet ovat silti samat, ja Linux on itse yleinen reititin,
palomuuri ja VPN-yhdyskäytävä.

## Työkalut

| Tehtävä | Työkalu |
|---------|---------|
| Liitännät, osoitteet, reitit, nimiavaruudet | `ip` (iproute2) |
| Sillat ja niiden välitystaulut | `ip link`, `bridge` |
| Palomuuri ja NAT | `nft` (nftables) |
| Dynaaminen reititys | BIRD (OSPF, BGP); vaihtoehtona FRRouting |
| DHCP, DNS ja TFTP | dnsmasq |
| Palvelun laatu | `tc` (traffic control) |
| RADIUS | FreeRADIUS, `radtest` |
| VPN | WireGuard (`wg`) |
| Valvonta | Net-SNMP, softflowd, nfcapd ja nfdump |
| Kahdennus ja linkkien yhdistäminen (vain asetuksina) | keepalived, `ip link … type bond` |
| Liikenteen kaappaus | `tcpdump`, Wireshark |

Esimerkit ajetaan tutoriaalin kehityskontissa, jossa työkalut ovat
valmiina ja kontilla on verkon hallintaan tarvittavat oikeudet:

```text
make -C verkkoinfrastruktuuri testaa
```

## Lukuohje

Luvut etenevät verkon kerroksina: suunnittelu ja osoitteet, kytkentä,
reititys, palomuurit, verkkopalvelut, palvelun laatu, langattomat verkot
ja pääsynhallinta, etäyhteydet, valvonta ja vianetsintä ja lopuksi
verkko koodina. Luvut
voi lukea myös erikseen. Jokaisen luvun lopussa on osio *Käytännössä*,
joka kokoaa ammattilaisten käytännöt perusteluineen, ja *Itsearviointi*,
jonka väitteistä näkee, voiko luvun ohittaa.
