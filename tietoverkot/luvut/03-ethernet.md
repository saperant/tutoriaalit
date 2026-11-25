# Ethernet, ARP ja kytkentä

Ethernet on lähiverkon linkkikerros: kaapeloidut verkot, ja WLANin
kehykset muistuttavat sitä niin paljon, että käyttöjärjestelmä näyttää
ne Ethernet-liitäntöinä. Linkkikerros toimittaa kehyksen yhden
verkkosegmentin sisällä koneelta toiselle. Segmentin ulkopuolelle
päästään vasta IP:n ja reitityksen avulla.

## MAC-osoitteet ja kehys

MAC-osoite on 48-bittinen, ja se kirjoitetaan kuutena heksatavuna
(`02:00:00:00:00:0a`). Valmistaja polttaa verkkokorttiin yksilöllisen
osoitteen, jonka kolme ensimmäistä tavua (OUI) kertovat valmistajan.
Ensimmäisen tavun kaksi alinta bittiä ovat merkitseviä:

| Bitti | Arvo 0 | Arvo 1 |
|-------|--------|--------|
| `0x01` (I/G) | yksittäislähetys (*unicast*) | ryhmälähetys (*multicast*) |
| `0x02` (U/L) | maailmanlaajuisesti yksilöllinen | paikallisesti hallinnoitu |

Tämän tutoriaalin osoitteet alkavat tavulla `02`, eli ne ovat
paikallisesti hallinnoituja, kuten virtuaalikoneiden ja konttien
osoitteet. Puhelimet ja kannettavat käyttävät WLANissa satunnaisia
paikallisia osoitteita, jotta laitetta ei voi seurata verkosta toiseen.
Osoite `ff:ff:ff:ff:ff:ff` on *yleislähetys* (*broadcast*): kehys menee
kaikille segmentin koneille.

Kehyksessä on kohde, lähde, EtherType ja hyötykuorma (46–1500 tavua).
Hyötykuorman enimmäiskoko 1500 tavua on Ethernetin **MTU** (*maximum
transmission unit*). Jumbo-kehyksissä MTU on yleensä 9000 tavua, mutta
niitä käytetään vain hallituissa verkoissa, kuten konesalissa ja
tallennusverkoissa, koska jokaisen laitteen polulla on tuettava niitä.

## ARP: IP-osoitteesta MAC-osoitteeksi

Kun kone haluaa lähettää IP-paketin samassa aliverkossa olevalle
koneelle, se tarvitsee vastaanottajan MAC-osoitteen. ARP (*Address
Resolution Protocol*) kysyy sitä yleislähetyksenä: "kenellä on
192.0.2.2? kerro 192.0.2.1:lle". Osoitteen omistaja vastaa suoraan
kysyjälle. Vastaus tallennetaan *naapuritauluun* (ARP-välimuistiin),
jota `ip neigh` näyttää. Merkinnän tila on esimerkiksi `REACHABLE`
(vahvistettu äskettäin), `STALE` (vanha, tarkistetaan käytettäessä),
`INCOMPLETE` (kysely kesken) tai `FAILED` (ei vastausta).

ARP:ssa ei ole todennusta: kuka tahansa segmentin kone voi vastata
väärin tai lähettää pyytämättömän vastauksen (*gratuitous ARP*). Sitä
käytetään luvallisesti vikasietoisuuteen, kun osoite siirtyy koneelta
toiselle, ja luvattomasti liikenteen kaappaamiseen (*ARP spoofing*).
Hallituissa verkoissa kytkimet suodattavat väärennettyjä vastauksia
(taito *Verkkoinfrastruktuuri*).

## Kytkin

Kytkin välittää kehyksiä porttien välillä. Se oppii, minkä portin
takana mikin MAC-osoite on, lukemalla saapuvien kehysten
lähdeosoitteet:

```{.python tiedosto="esimerkit/03-kytkin.py" osa="kytkin"}
```

```{.python tiedosto="esimerkit/03-kytkin.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/03-kytkin.odotettu"}
```

Kolme sääntöä riittää:

1. **Oppiminen**: lähdeosoite kirjataan tauluun saapumisporttiin.
2. **Välitys**: tunnettu kohde lähetetään vain sen porttiin.
3. **Tulvitus**: yleislähetys ja tuntematon kohde lähetetään kaikkiin
   muihin portteihin. Kun kohde vastaa, kytkin oppii senkin.

Merkinnät vanhenevat (oletus 300 sekuntia), jotta toiseen porttiin
siirretty kone löytyy. Tulvitus tekee kytketystä verkosta yhden
**yleislähetysalueen**: jokainen ARP-kysely ja muu yleislähetys menee
kaikille. Suuri litteä verkko hukkuu yleislähetyksiin, minkä vuoksi
verkot jaetaan VLANeilla ja reitittimillä pienempiin.

## Linux-silta

Linuxin silta (*bridge*) on ohjelmistokytkin. Sitä käyttävät
virtuaalikoneet, kontit ja Docker (`docker0`). Rakennetaan kolmen
koneen verkko, jossa kytkin on oma nimiavaruutensa.

```{.dot otsikko="Siltalaboratorio: kolme konetta kytkimen porteissa. Kaikki ovat samassa aliverkossa 192.0.2.0/24."}
graph {
  rankdir=LR; nodesep=0.3; ranksep=0.9;
  A [label="kone A\n192.0.2.1\n02:00:00:00:00:01"];
  B [label="kone B\n192.0.2.2\n02:00:00:00:00:02"];
  C [label="kone C\n192.0.2.3\n02:00:00:00:00:03"];
  K [label="kytkin\nsilta br0"];
  A -- K [label="portti1"];
  B -- K [label="portti2"];
  C -- K [label="portti3"];
}
```

```{.bash tiedosto="esimerkit/03-silta.sh" osa="kytkin"}
```

```{.bash tiedosto="esimerkit/03-silta.sh" osa="liikenne"}
```

```{.tuloste tiedosto="esimerkit/03-silta.odotettu"}
```

Kone A oppi ARP:lla B:n ja C:n osoitteet, ja silta oppi, minkä portin
takana kukin kone on. `bridge fdb` (*forwarding database*) on sama
taulu kuin Python-mallin `taulu`. Pysyvät (`permanent`) merkinnät ovat
sillan omia osoitteita, ja ne suodatettiin pois.

## Käytännössä

- **Katso naapuritaulu, kun saman aliverkon yhteys ei toimi.**
  `INCOMPLETE` tai `FAILED` tarkoittaa, että vika on linkkikerroksessa:
  kaapeli, VLAN, väärä aliverkko tai kone ei ole päällä.
- **Kaksi konetta samalla IP-osoitteella** näkyy naapuritaulussa
  vaihtelevana MAC-osoitteena ja katkonaisina yhteyksinä. Selvitä
  vaihtelevan MAC-osoitteen valmistaja OUI-luettelosta.
- **Älä luota MAC-osoitteeseen tunnisteena.** Se on helppo vaihtaa, ja
  laitteet satunnaistavat sen. Pääsynhallinta perustuu todennukseen
  (802.1X), ei osoitteisiin.
- **Pidä yleislähetysalueet pieninä.** Kymmeniä tai muutamia satoja
  koneita aliverkossa on tavallista; tuhannet kuormittavat kaikkia
  koneita ARP-liikenteellä.

## Itsearviointi

- Osaat tulkita MAC-osoitteen I/G- ja U/L-bitit sekä kertoa, mitä
  yleislähetysosoite tarkoittaa.
- Osaat selittää ARP:n kulun ja tulkita `ip neigh`-komennon tilat.
- Osaat kuvata kytkimen oppimisen, välityksen ja tulvituksen sekä
  yleislähetysalueen käsitteen.
- Osaat rakentaa Linux-sillan ja tarkastella sen oppimia osoitteita.
