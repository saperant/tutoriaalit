# Liikenteen analyysi ja vianetsintä

Verkkovika ratkeaa, kun nähdään, mitä langalla oikeasti kulkee.
Kaappaus erottaa arvaukset tosiasioista: lähtikö kysely, tuliko vastaus,
mitä siinä oli ja kuka sen lähetti.

## tcpdump ja suodattimet

`tcpdump` kaappaa liitännän liikenteen. Tavallisimmat valitsimet:

| Valitsin | Merkitys |
|----------|----------|
| `-i eth0`, `-i any` | Liitäntä |
| `-n` | Ei nimien selvitystä (nopeampi, ei omaa DNS-liikennettä) |
| `-w tiedosto.pcap`, `-r tiedosto.pcap` | Tallennus ja luku |
| `-c 100` | Lopeta sadan paketin jälkeen |
| `-e`, `-v`, `-X` | MAC-osoitteet, lisätiedot, sisältö heksana |
| `-s 128` | Tallenna vain otsakkeet (pienempi tiedosto, vähemmän dataa) |

Suodatin kirjoitetaan BPF-kielellä, ja ydin suodattaa paketit jo ennen
kuin ne kopioidaan tcpdumpille: `host 192.0.2.20`, `net 10.0.0.0/8`,
`port 53`, `tcp port 443 and not host 10.0.0.5`, `icmp`,
`'tcp[tcpflags] & tcp-syn != 0'` (vain yhteyden avaukset). Suodata aina
pois oma etäyhteytesi (`not port 22`), muuten kaappaus kaappaa itseään.

Kaappaa tiedostoon ja analysoi myöhemmin. Wireshark näyttää saman
tiedoston kerroksittain, seuraa TCP-virtoja ja purkaa satoja
protokollia. Palvelimella kaapataan, työasemalla analysoidaan.

```{.bash tiedosto="esimerkit/11-kaappaus.sh" osa="kaappaus"}
```

```{.tuloste tiedosto="esimerkit/11-kaappaus.odotettu"}
```

ICMP-vastauksia on kuusi: kolme pingin vastausta ja kolme *port
unreachable* -ilmoitusta, koska B:llä ei kuunnellut mikään UDP-portti.

## pcap-tiedosto

Kaappaustiedoston muoto on yksinkertainen: 24 tavun tiedosto-otsake,
sitten jokaiselle paketille 16 tavun tietueotsake (aikaleima,
tallennettu ja alkuperäinen pituus) ja kehyksen tavut. Taikaluku kertoo
tavujärjestyksen. Uudempi pcapng-muoto tallentaa lisäksi liitännät ja
kommentit; tcpdump kirjoittaa oletuksena pcapia.

```{.python tiedosto="esimerkit/11-pcap.py" osa="luku"}
```

```{.python tiedosto="esimerkit/11-pcap.py" osa="tiivistys"}
```

```{.tuloste tiedosto="esimerkit/11-pcap.odotettu"}
```

Oma lukija on hyödyllinen, kun kaappauksesta halutaan tilasto tai
automaattinen tarkistus testissä. Laajempaan analyysiin on valmiita
kirjastoja (Scapy, dpkt, pyshark).

## Vianetsintä kerros kerrallaan

Järjestelmällinen vianetsintä etenee alhaalta ylös ja rajaa vian:

1. **Linkki**: `ip -br link` – onko liitäntä `UP` ja kaapeli kiinni
   (`LOWER_UP`)?
2. **Osoite**: `ip -br addr` – onko osoite ja oikea maski?
3. **Reitti**: `ip route get KOHDE` – mitä kautta paketti lähtisi?
4. **Naapuri**: `ip neigh` – vastaako seuraava reititin ARP:iin?
5. **Saavutettavuus**: `ping`, `tracepath` – mihin asti päästään?
6. **Portti**: `ss -tln` palvelimella, `curl -v` tai `nc -vz` asiakkaalla.
7. **Nimi**: `dig`, `getent hosts`.
8. **Sovellus**: lokit, `curl -v`, kaappaus.

Laboratoriossa on kolme tavallista vikaa:

```{.bash tiedosto="esimerkit/11-vianetsinta.sh" osa="vika1"}
```

```{.bash tiedosto="esimerkit/11-vianetsinta.sh" osa="vika2"}
```

```{.bash tiedosto="esimerkit/11-vianetsinta.sh" osa="vika3"}
```

```{.tuloste tiedosto="esimerkit/11-vianetsinta.odotettu"}
```

1. **Väärä maski** `/32`: koneen mielestä edes oma reititin ei ole
   samassa aliverkossa, ja reitityshaku epäonnistuu heti.
2. **Väärä oletusyhdyskäytävä**: reitti on olemassa, mutta seuraavaa
   reititintä ei löydy. Naapuritaulun `INCOMPLETE` kertoo, että ARP-
   kyselyyn ei vastattu.
3. **Puuttuva paluureitti**: paketti pääsee perille, mutta palvelin ei
   tiedä, minne vastata. Kaappaus palvelimella näyttäisi saapuvat
   pyynnöt ilman lähteviä vastauksia.

## Käytännössä

- **Kaappaa molemmista päistä.** Kun liikenne katoaa, kahden kaappauksen
  vertailu kertoo, millä välillä.
- **Rajaa kaappaus suodattimella ja koolla** (`-c`, `-s`, `-W` ja `-C`
  rengaspuskuriksi). Rajaamaton kaappaus täyttää levyn kiireisellä
  palvelimella.
- **Kaappauksissa on luottamuksellista dataa**: salasanoja, evästeitä ja
  henkilötietoja. Käsittele niitä kuten tuotantodataa ja poista, kun
  työ on tehty.
- **Etene kerroksittain ja kirjaa havainnot.** Hyppiminen suoraan
  sovelluksen lokeihin ohittaa usein sen, että liitännällä ei ollut
  osoitetta.
- **Toista vika laboratoriossa.** Verkkonimiavaruudet tai kontit
  riittävät useimpien vikojen jäljittelyyn ilman tuotannon riskejä.

## Itsearviointi

- Osaat kaapata liikennettä tcpdumpilla, rajata sen BPF-suodattimilla
  ja tallentaa sen tiedostoon Wiresharkia varten.
- Osaat lukea pcap-tiedoston ohjelmallisesti ja tiivistää sen.
- Osaat edetä vianetsinnässä kerros kerrallaan ja valita kullekin
  kerrokselle oikean komennon.
- Osaat tunnistaa väärän maskin, väärän yhdyskäytävän ja puuttuvan
  paluureitin oireista.
