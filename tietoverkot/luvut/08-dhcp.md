# DHCP

Kone, joka liitetään verkkoon, tarvitsee osoitteen, aliverkon maskin,
oletusreitittimen ja nimipalvelimen. DHCP (*Dynamic Host Configuration
Protocol*) jakaa ne keskitetysti palvelimelta, ja osoite *vuokrataan*
määräajaksi. Kotireititin, yritysverkon DHCP-palvelin ja pilven
virtuaaliverkko tekevät saman asian.

## Neljä viestiä: DORA

| Viesti | Suunta | Sisältö |
|--------|--------|---------|
| DISCOVER | asiakas → kaikki | "Tarvitsen osoitteen", oma MAC-osoite |
| OFFER | palvelin → asiakas | Tarjottu osoite ja asetukset |
| REQUEST | asiakas → kaikki | "Otan tämän palvelimen tarjouksen" |
| ACK | palvelin → asiakas | Vahvistus ja vuokra-aika |

Asiakkaalla ei ole vielä osoitetta, joten se lähettää lähdeosoitteesta
`0.0.0.0` porttiin 67 yleislähetysosoitteeseen `255.255.255.255`.
REQUEST lähetetään myös yleislähetyksenä, jotta muut palvelimet näkevät,
ettei niiden tarjousta valittu. Vuokran puolivälissä asiakas uusii
sen suoraan palvelimelta (REQUEST–ACK).

## Viestin rakenne

DHCP on rakennettu vanhan BOOTP:n päälle: 236 tavun kiinteä osa,
taikaluku `63 82 53 63` ja sen jälkeen optiot muodossa koodi, pituus,
arvo. Optio 53 kertoo viestin tyypin, ja asiakas pyytää haluamansa
optiot listalla 55:

```{.python tiedosto="esimerkit/08-dhcp.py" osa="viesti"}
```

```{.python tiedosto="esimerkit/08-dhcp.py" osa="tulkinta"}
```

```{.python tiedosto="esimerkit/08-dhcp.py" osa="esittely"}
```

```{.tuloste tiedosto="esimerkit/08-dhcp.odotettu"}
```

Tavalliset optiot: 1 aliverkon maski, 3 reititin, 6 nimipalvelimet,
15 toimialue, 42 NTP-palvelimet, 51 vuokra-aika, 54 palvelimen
tunniste, 66 ja 67 verkkokäynnistyksen TFTP-palvelin ja tiedosto.

## Laboratorio: dnsmasq ja oma asiakas

dnsmasq on pieni DHCP- ja DNS-palvelin, jota käyttävät monet
kotireitittimet, libvirt ja Linux-jakelut:

```{.bash tiedosto="esimerkit/08-dnsmasq.sh" osa="palvelin"}
```

`--dhcp-host` varaa kiinteän osoitteen MAC-osoitteen perusteella
(*static lease*): tulostin saa aina saman osoitteen, mutta asetukset
ovat silti keskitetysti palvelimella. `--no-ping` ohittaa dnsmasqin
tavan tarkistaa pingillä, onko tarjottava osoite jo käytössä, ja
`--dhcp-sequential-ip` jakaa osoitteet järjestyksessä. Molemmat
tehdään vain, jotta esimerkki on nopea ja toistettava.

Asiakas lähettää DISCOVER- ja REQUEST-viestit UDP-soketilla, joka on
sidottu liitäntään (`SO_BINDTODEVICE`):

```{.python tiedosto="esimerkit/08-dhcp.py" osa="asiakas"}
```

Komentotulkki asettaa saadun osoitteen ja reitin:

```{.bash tiedosto="esimerkit/08-dnsmasq.sh" osa="asiakas"}
```

```{.bash tiedosto="esimerkit/08-dnsmasq.sh" osa="vuokrat"}
```

```{.tuloste tiedosto="esimerkit/08-dnsmasq.odotettu"}
```

Oikeat DHCP-asiakkaat (systemd-networkd, NetworkManager, dhcpcd)
käyttävät raakasokettia, koska ilman osoitetta tavallinen IP-pino
hylkää vastauksen paluureitin tarkistuksessa. Siksi laboratoriossa
tarkistus (`rp_filter`) kytkettiin pois asiakkaalta.

## DHCP isommassa verkossa

- **Välitys** (*DHCP relay*): yleislähetys ei ylitä reititintä, joten
  reititin välittää viestit keskitetylle palvelimelle ja kertoo,
  mistä aliverkosta ne tulivat (kenttä `giaddr`, optio 82).
- **Vikasietoisuus**: kaksi palvelinta jakaa osoitealueen tai
  synkronoi vuokrat.
- **Verkkokäynnistys** (PXE): DHCP kertoo TFTP-palvelimen ja
  käynnistystiedoston, jolla kone asennetaan verkon yli. Tämä kuuluu
  taitoon *Verkkoinfrastruktuuri*.
- **IPv6** käyttää SLAACia, DHCPv6:ta tai molempia (luku *IPv6*).

## Käytännössä

- **169.254.x.y tarkoittaa DHCP-vikaa.** Tarkista, saapuuko DISCOVER
  palvelimelle (`tcpdump -n port 67 or port 68`) ja vastaako palvelin.
- **Kiinteät osoitteet palvelimille ja verkkolaitteille, vuokrat
  muille.** Varaa kiinteille osoitteille oma alue jaettavan alueen
  ulkopuolelta, ettei sama osoite päädy kahdelle.
- **DHCP:ssä ei ole todennusta.** Verkkoon tuotu väärä DHCP-palvelin voi
  jakaa oman reitittimensä ja nimipalvelimensa kaikille. Kytkimen
  *DHCP snooping* sallii vastaukset vain luotetuista porteista.
- **Lyhyt vuokra-aika** vieras- ja WLAN-verkoissa vapauttaa osoitteet
  nopeasti; pitkä vähentää liikennettä kiinteissä verkoissa.

## Itsearviointi

- Osaat kuvata DORA-vaiheet sekä sen, miksi viestit lähetetään
  yleislähetyksinä ja mistä osoitteista.
- Osaat jäsentää DHCP-viestin kiinteän osan ja optiot.
- Osaat konfiguroida dnsmasqin jakamaan osoitteita ja kiinteitä
  varauksia sekä tarkastella vuokria.
- Osaat selittää DHCP-välityksen, väärän DHCP-palvelimen riskin ja
  tavallisimmat DHCP-viat.
