# Kerrokset ja kapselointi

Verkkoprotokollat on jaettu kerroksiin. Jokainen kerros ratkaisee yhden
ongelman ja käyttää alemman kerroksen palvelua: sovellus antaa datan
TCP:lle tietämättä, kulkeeko se Ethernetissä, WLANissa vai
mobiiliverkossa, ja reititin välittää IP-paketin tietämättä, mitä
sovellusta se palvelee.

## OSI- ja TCP/IP-mallit

| OSI-kerros | TCP/IP-malli | Esimerkkejä | Osoite |
|------------|--------------|-------------|--------|
| 7 sovellus, 6 esitys, 5 istunto | sovellus | HTTP, DNS, DHCP, TLS | nimi, URL |
| 4 kuljetus | kuljetus | TCP, UDP, QUIC | portti |
| 3 verkko | Internet | IPv4, IPv6, ICMP | IP-osoite |
| 2 siirtoyhteys | linkki | Ethernet, WLAN, ARP | MAC-osoite |
| 1 fyysinen | linkki | kupari, valokuitu, radio | – |

OSI-malli on käsitteellinen viitekehys, ja sen kerrosnumerot ovat
alan yleiskieltä: "L2-kytkin", "L4-kuormantasain", "L7-palomuuri".
Internetin protokollat noudattavat yksinkertaisempaa TCP/IP-mallia.
Kerrokset eivät ole tiukkoja: TLS istuu TCP:n ja sovelluksen välissä,
ARP sitoo verkko- ja linkkikerroksen yhteen, ja QUIC toteuttaa
kuljetuskerroksen UDP:n päällä.

## Kapselointi

Lähetettäessä jokainen kerros lisää datan eteen oman otsakkeensa:

```text
| Ethernet 14 | IPv4 20 | UDP 8 | sovelluksen data      | FCS 4 |
              |<-------------- IP-paketti ------------>|
                        |<------ UDP-datagrammi ------>|
```

Vastaanottaja purkaa kerrokset päinvastaisessa järjestyksessä. Kunkin
otsakkeen kenttä kertoo, mikä seuraava kerros on: Ethernetin
*EtherType* (`0x0800` = IPv4, `0x86dd` = IPv6, `0x0806` = ARP), IP:n
*protokolla* (6 = TCP, 17 = UDP, 1 = ICMP) ja kuljetuskerroksen
*portti* (53 = DNS, 443 = HTTPS). Ethernet-kehyksen lopun tarkistussumman
(FCS) laskee ja tarkistaa verkkokortti, joten ohjelmat eivät näe sitä.

## Kehys tavu tavulta

Rakennetaan UDP-datagrammi, joka kulkee IPv4-paketissa
Ethernet-kehyksen sisällä. Ensin tarvitaan Internetin tarkistussumma,
jota IPv4-otsake, UDP, TCP ja ICMP käyttävät:

```{.python tiedosto="esimerkit/02-kehys.py" osa="summa"}
```

Summa lasketaan 16-bittisinä sanoina yhden komplementin aritmetiikalla.
Algoritmi on nopea ja havaitsee yksittäiset bittivirheet, mutta ei
kaikkia virheitä. Tahallista muuttamista se ei estä lainkaan: siihen
tarvitaan kryptografinen tarkiste (TLS, taito *Kryptografia*).

Otsakkeet ladotaan `struct`-modulilla. Muotomerkkijonon `!` tarkoittaa
verkon tavujärjestystä (*big-endian*): kaikki Internetin protokollat
lähettävät eniten merkitsevän tavun ensin, vaikka x86- ja ARM-suorittimet
tallentavat luvut muistiin päinvastoin. Tavujärjestysvirhe on
klassinen verkkokoodin bugi.

```{.python tiedosto="esimerkit/02-kehys.py" osa="rakennus"}
```

Huomioita kentistä:

- **IPv4:n TTL** (*time to live*) on hyppyjen enimmäismäärä. Jokainen
  reititin vähentää sitä yhdellä ja hylkää paketin, kun arvo on nolla.
  Näin reitityssilmukka ei kierrätä pakettia ikuisesti.
- **DF-lippu** ("älä pilko") kieltää reitittimiä pilkkomasta pakettia.
  Nykyiset käyttöjärjestelmät asettavat sen ja selvittävät polun MTU:n
  itse (luku *TCP, UDP ja portit*).
- **UDP:n tarkistussumma** lasketaan myös *näennäisotsakkeen* yli, jossa
  ovat IP-osoitteet. Näin väärään osoitteeseen eksynyt datagrammi
  hylätään.

Jäsentäminen tehdään samoilla muotomerkkijonoilla toiseen suuntaan.
Hyvä jäsennin tarkistaa jokaisen oletuksensa (tyyppi, protokolla,
tarkistussumma) eikä luota syötteeseen:

```{.python tiedosto="esimerkit/02-kehys.py" osa="jasennys"}
```

```{.python tiedosto="esimerkit/02-kehys.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/02-kehys.odotettu"}
```

Heksavedoksesta näkee kerrokset: tavut `0x00–0x0d` ovat
Ethernet-otsake (kohde, lähde, `08 00`), `45` aloittaa IPv4-otsakkeen
(versio 4, pituus 5 × 4 tavua), `c0 00 02 0a` on `192.0.2.10`, `9c 40`
on portti 40000 ja lopussa on sovelluksen teksti. Kun yksi TTL-kentän
bitti käännetään, tarkistussumma paljastaa sen.

## Käytännössä

- **Ajattele kerroksittain vianetsinnässä.** Toimiiko linkki (`ip link`)?
  Onko osoite ja reitti (`ip addr`, `ip route`)? Vastaako kohde
  (`ping`)? Onko portti auki (`ss`, `curl`)? Toimiiko nimi (`dig`)?
  Jokainen vastaus rajaa vian.
- **Verkon tavujärjestys on big-endian.** Käytä Pythonissa `struct`-
  muotoa `!`, C:ssä funktioita `htons` ja `ntohl`. Älä koskaan kopioi
  rakennetta suoraan muistista verkkoon.
- **Jäsennä puolustavasti.** Verkosta tuleva data on hyökkääjän
  hallinnassa. Tarkista pituudet ennen indeksointia ja kenttien arvot
  ennen käyttöä. Monet tunnetut haavoittuvuudet ovat jäsentimissä.
- **Otsakkeet maksavat.** Jokaisessa kehyksessä kulkee vähintään 42
  tavua otsakkeita (Ethernet, IPv4, UDP). Pienien viestien lähettäminen
  yksi kerrallaan tuhlaa kaistaa ja suoritinta. Kokoa ne puskuriin.

## Itsearviointi

- Osaat nimetä TCP/IP-mallin kerrokset, kunkin kerroksen tehtävän ja
  osoitteen sekä tavallisimmat protokollat.
- Osaat selittää kapseloinnin ja sen, mistä kentistä vastaanottaja
  tietää seuraavan kerroksen protokollan.
- Osaat rakentaa ja jäsentää otsakkeita `struct`-modulilla verkon
  tavujärjestyksessä.
- Osaat laskea ja tarkistaa Internetin tarkistussumman ja kertoa, mitä
  se suojaa ja mitä ei.
