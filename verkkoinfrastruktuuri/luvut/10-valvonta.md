# Valvonta

Verkkoa, jota ei valvota, ylläpidetään käyttäjien valitusten
perusteella. Valvonta vastaa kolmeen kysymykseen: toimiiko kaikki nyt
(saatavuus), miten verkko voi (kuormat, virheet, trendit) ja mitä verkossa
tapahtui (virrat ja tapahtumat vianetsintää ja tietoturvatutkintaa
varten).

## Mitä valvotaan

| Lähde | Mitä se kertoo | Väline |
|-------|----------------|--------|
| Saatavuustestit | vastaako laite tai palvelu | ping, HTTP- ja DNS-kyselyt keskitetysti |
| Laskurit | liitäntöjen liikenne, virheet, pudotukset, prosessori, muisti | SNMP, telemetria (gNMI) |
| Tilatiedot | naapuruudet (OSPF, BGP), STP-muutokset, liitäntöjen tila | SNMP-ilmoitukset, syslog |
| Virrat | kuka puhui kenelle, mihin palveluun ja kuinka paljon | NetFlow, IPFIX, sFlow |
| Lokit | kirjautumiset, asetusmuutokset, palomuurin pudotukset | syslog keskitetysti |

Kerätty tieto viedään aikasarjatietokantaan (esimerkiksi Prometheus,
InfluxDB) ja lokijärjestelmään, joista hälytykset ja näkymät
rakennetaan.

## SNMP

SNMP on verkkolaitteiden vanha mutta yhä yleisin hallintaprotokolla.
Laitteen agentti vastaa kyselyihin tietokohteista, jotka on nimetty
puurakenteisilla tunnisteilla (OID) ja kuvattu MIB-tiedostoissa.
Esimerkiksi `.1.3.6.1.2.1.1.5.0` on laitteen nimi ja
`.1.3.6.1.2.1.2.2.1.2` liitäntöjen kuvaukset.

SNMP:n versiot 1 ja 2c todentavat kyselyn pelkällä yhteisönimellä
(*community*), joka kulkee selväkielisenä ja on usein oletusarvoinen
`public`. SNMPv3 lisää käyttäjäkohtaisen todennuksen ja salauksen:

```{.bash tiedosto="esimerkit/10-snmp.sh" osa="agentti"}
```

```{.bash tiedosto="esimerkit/10-snmp.sh" osa="kysely"}
```

```{.tuloste tiedosto="esimerkit/10-snmp.odotettu"}
```

v2c-kyselyyn ei vastata lainkaan: agentti ei paljasta, onko se olemassa.
Agentti kuuntelee vain hallintaverkon osoitteessa, ja oikeus on vain
luku; kirjoitusoikeudella SNMP:n kautta voisi muuttaa laitteen
asetuksia.

Uudemmat laitteet tukevat suoratoistettavaa telemetriaa (gNMI,
NETCONF/YANG-mallit), jossa laite lähettää mittaukset itse tiheästi
sen sijaan, että valvonta kyselee niitä minuuttien välein. Periaatteet
ovat samat: todennettu, salattu ja vain hallintaverkossa.

## Virtatieto

Laskurit kertovat, että yhteys on täynnä; virtatieto kertoo, mikä sen
täyttää. **Virta** (*flow*) on pakettien joukko, jolla on sama
viisikko: protokolla, lähde- ja kohdeosoite sekä portit. Reititin tai
erillinen mittauspiste koostaa paketit virroiksi ja lähettää
virtatietueet keräimelle NetFlow- tai IPFIX-muodossa. Pakettien sisältöä
ei tallenneta, joten virtatieto on kevyttä ja sitä voi säilyttää
pitkään.

Laboratoriossa reitittimen lähiverkkoliitäntä kaapataan, ja softflowd
muuntaa kaappauksen virroiksi ja lähettää ne NetFlow v9 -muodossa
keräimelle (nfcapd). Tuotannossa softflowd tai reititin tekee saman
jatkuvasti.

```{.bash tiedosto="esimerkit/10-netflow.sh" osa="keruu"}
```

```{.bash tiedosto="esimerkit/10-netflow.sh" osa="raportti"}
```

```{.tuloste tiedosto="esimerkit/10-netflow.odotettu"}
```

Raportissa näkyvät kaksi verkkosivupyyntöä (kaksi virtaa porttiin 80)
ja nimikysely porttiin 53, johon palvelin vastasi ICMP-virheellä:
ICMP-virrassa portin paikalla on viestin tyyppi ja koodi (3.3 =
portti ei tavoitettavissa). Tällaisista raporteista löytyvät
kaistan suurkuluttajat, odottamattomat yhteydet (työasema, joka puhuu
tuntemattomaan osoitteeseen yöllä) ja palomuurisääntöjen tarve.

## Hälytykset

Hälytys on hyödyllinen vain, jos siihen reagoidaan. Hyvä hälytys kertoo
oireen, joka vaikuttaa käyttäjiin (palvelu ei vastaa, yhteys on
ruuhkautunut, varayhteys on käytössä), eikä jokaista mahdollista syytä.
Muut tiedot ovat näkymissä vianetsintää varten. Liian moni hälytys
opettaa ohittamaan ne kaikki.

## Käytännössä

- **SNMPv3 authPriv tai telemetria, vain luku, vain hallintaverkossa.**
  v1 ja v2c poistetaan käytöstä, ja jos niitä on pakko käyttää, yhteisönimi
  on pitkä ja satunnainen ja kyselyt rajataan pääsylistalla.
- **Keskitetty aika ja lokit.** Kaikki laitteet synkronoivat kellonsa
  (NTP) ja lähettävät lokinsa keskitettyyn järjestelmään; muuten
  tapahtumia ei voi yhdistää.
- **Virtatieto rajoilta.** Internetyhteys, konesalin raja ja
  segmenttien väliset palomuurit ovat paikat, joissa virrat kannattaa
  kerätä.
- **Perustaso.** Normaali kuorma ja normaalit virrat tunnetaan, jotta
  poikkeama erottuu.
- **Hälytä oireista,** ja jokaisella hälytyksellä on ohje (*runbook*):
  mitä tarkistetaan ja kuka vastaa.
- **Valvo valvontaa.** Hiljaisuus ei tarkoita, että kaikki on kunnossa,
  jos keräin on kaatunut.

## Itsearviointi

- Osaat luetella valvonnan tietolähteet ja sen, mitä kustakin saa
  selville.
- Osaat määrittää SNMPv3-agentin todennuksella ja salauksella ja kysellä
  sitä numeerisilla OID-tunnisteilla.
- Osaat selittää virran käsitteen, kerätä NetFlow-tietoa ja lukea siitä
  koostetun raportin.
- Osaat suunnitella hälytykset oireiden perusteella.
