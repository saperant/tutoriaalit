# Johdanto {.runko-johdanto}

Lähes jokainen ohjelma käyttää verkkoa: selain hakee sivun, mobiilisovellus
kutsuu rajapintaa, palvelin kysyy tietokannalta ja sulautettu laite
raportoi mittauksia. Kun yhteys ei toimi tai on hidas, vika voi olla missä
tahansa kerroksessa: kaapelissa, osoitteissa, reitityksessä, nimipalvelussa,
palomuurissa, TLS-varmenteessa tai sovelluksen protokollassa. Kehittäjä
ja ylläpitäjä, joka ymmärtää kerrokset, löytää vian järjestelmällisesti
eikä arvaamalla.

Tämä tutoriaali opettaa Internetin protokollat siinä laajuudessa kuin
ohjelmoija ja ylläpitäjä niitä tarvitsee: kerrosmallit ja kapseloinnin,
Ethernetin ja ARP:n, IPv4:n ja IPv6:n osoitteet, reitityksen ja
osoitteenmuunnoksen (NAT), TCP:n ja UDP:n, DHCP:n, DNS:n ja mDNS:n,
HTTP:n ja TLS:n sekä liikenteen analyysin. Painopiste on siinä, miten
protokollat toimivat ja miten niiden toiminnan näkee omin silmin.

Rajaukset:

- Verkkojen suunnittelu ja ylläpito, kuten VLANit, dynaamiset
  reitityskäytännöt (OSPF, BGP), palomuurit, palvelun laatu (QoS),
  langattomat verkot, RADIUS ja VPN:t, kuuluvat taitoon
  *Verkkoinfrastruktuuri*, joka rakentuu tämän päälle.
- Sokettiohjelmointi, protokollien suunnittelu ja moniasiakaspalvelimet
  kuuluvat taitoon *Verkko-ohjelmointi*. Tässä soketteja käytetään vain
  protokollien havainnollistamiseen.
- Siirtotiet, modulaatiot ja kanavanvaraus ovat taidon
  *Tietoliikennetekniikka* aiheita.

Esitiedoksi riittää taito *Komentorivi ja Linux*. Python-esimerkkien
lukemiseen riittää taito *Ohjelmoinnin perusteet*.

## Kaksi tapaa oppia protokolla

Protokollan oppii parhaiten kahdesta suunnasta:

1. **Tavu tavulta.** Rakennetaan viesti itse, esimerkiksi UDP-datagrammi
   tai DNS-kysely, ja jäsennetään vastaus. Silloin näkee, mitä otsakkeen
   kentät ovat ja miksi ne ovat siellä. Tähän käytetään Pythonin
   vakiokirjastoa (`struct`, `socket`, `ipaddress`).
2. **Oikeassa verkossa.** Rakennetaan pieni verkko, lähetetään liikennettä
   ja katsotaan, mitä langalla kulkee. Tähän käytetään Linuxin
   verkkonimiavaruuksia ja vakiotyökaluja (`ip`, `ss`, `tcpdump`,
   `dig`, `dnsmasq`).

Molemmat ovat ammattilaisen arkea. Vianetsinnässä luetaan kaappauksia ja
otsakkeita, ja protokollaa toteutettaessa tai testattaessa viestejä
rakennetaan ja puretaan ohjelmallisesti.

## Verkkonimiavaruudet laboratoriona

Linuxin *verkkonimiavaruus* (*network namespace*) on erillinen kopio
verkkopinosta: omat liitännät, osoitteet, reititystaulut, ARP-taulut,
palomuurisäännöt ja portit. Kontit (Docker, Kubernetes) on rakennettu
niiden varaan. Kun nimiavaruuksia yhdistetään virtuaalisilla kaapeleilla
(*veth*-pareilla), yhdellä koneella syntyy oikea verkko, jossa on monta
konetta, reitittimiä ja kytkimiä. Paketit kulkevat samassa ytimen
verkkopinossa kuin fyysisessä verkossa, joten kaikki, mitä tässä näkee,
pätee oikeisiin laitteisiin.

Esimerkit tarvitsevat pääkäyttäjän oikeudet. Kontissa tarvitaan
lisäksi oikeudet `NET_ADMIN`, `NET_RAW` ja `SYS_ADMIN` (nimiavaruuden
luonti on liitostoiminto), ja isännän AppArmor-profiili voi estää
liitokset, joten kehityskontti ajetaan etuoikeutettuna
(`--privileged`). Tee niin vain omalla koneellasi ja harjoituksia
varten. Jokainen
esimerkki luo nimiavaruutensa itse, siivoaa ne lopuksi (`trap … EXIT`)
ja käynnistää itsensä `sudo`:lla, jos oikeuksia ei ole.

Esimerkit käyttävät IPv4:ää. Jotta tulosteet olisivat samat kaikilla
koneilla, apufunktio kytkee IPv6:n pois uusista nimiavaruuksista, jos
ytimessä on IPv6-tuki:

```{.bash tiedosto="esimerkit/01-laboratorio.sh" osa="uusi-ns"}
```

Ensimmäinen laboratorio: kaksi konetta ja niiden välinen kaapeli.
Osoitteet `192.0.2.0/24` ovat dokumentaatiota varten varattuja (RFC 5737),
eivätkä ne koskaan ole käytössä Internetissä. MAC-osoitteet asetetaan
itse, jotta tulosteet ovat toistettavia:

```{.bash tiedosto="esimerkit/01-laboratorio.sh" osa="luonti"}
```

Sitten katsotaan, mitä syntyi: liitännät, osoitteet, yhteys ja
naapuritaulu, johon kone A oppi koneen B MAC-osoitteen:

```{.bash tiedosto="esimerkit/01-laboratorio.sh" osa="tarkastelu"}
```

```{.tuloste tiedosto="esimerkit/01-laboratorio.odotettu"}
```

`ip`-komennon valitsin `-br` (*brief*) antaa tiiviin taulukon, `-4`
rajaa IPv4:ään ja `-n NIMIAVARUUS` ajaa komennon toisessa
nimiavaruudessa. `eth0@if2` kertoo, että liitännän pari on toisen
nimiavaruuden liitäntä numero 2. `REACHABLE` tarkoittaa, että naapuri
on vastannut äskettäin.

## Työkalut

| Työkalu | Käyttö |
|---------|--------|
| `ip` (iproute2) | Liitännät, osoitteet, reitit, naapurit, nimiavaruudet |
| `ss` | Sokettien ja porttien tila (korvaa `netstat`in) |
| `ping`, `tracepath` | Saavutettavuus, viive, polun MTU |
| `tcpdump` | Liikenteen kaappaus ja suodatus komentoriviltä |
| Wireshark, `tshark` | Kaappausten graafinen ja syvällinen analyysi |
| `dig` | DNS-kyselyt |
| `curl` | HTTP- ja TLS-pyynnöt |
| `dnsmasq` | Pieni DHCP- ja DNS-palvelin |

Vanhat `ifconfig`, `route`, `arp` ja `netstat` (net-tools) toimivat
yhä monessa järjestelmässä, mutta ne eivät näe kaikkia nykyisen ytimen
ominaisuuksia, kuten useita osoitteita liitännässä tai nimiavaruuksia.
Uudet ohjeet ja skriptit kirjoitetaan `ip`- ja `ss`-komennoilla.

## Tutoriaalin esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Ne ajetaan ja tarkistetaan
automaattisesti, ja tekstissä näkyvät tulosteet ovat niiden oikeita
tulosteita. Python-esimerkit tarkistetaan työkaluilla ruff ja mypy
(tiukka tila), ja komentotulkin skriptit ShellCheckillä. Kehityskontissa
(`.devcontainer/tietoverkot`) on kaikki tarvittava.

Esimerkit, joissa on komento `ip netns`, muuttavat koneen verkkoasetuksia
vain omissa nimiavaruuksissaan. Isäntäkoneen verkkoon ne eivät koske.
