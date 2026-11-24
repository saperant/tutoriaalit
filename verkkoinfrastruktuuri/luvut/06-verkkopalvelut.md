# Verkkopalvelut: DHCP, DNS ja verkkokäynnistys

Verkon perusasetukset jaetaan laitteille automaattisesti: DHCP kertoo
osoitteen, yhdyskäytävän ja nimipalvelimen, DNS muuntaa nimet
osoitteiksi, ja verkkokäynnistys (PXE) lataa käyttöjärjestelmän
asentimen ilman paikallista mediaa. Näiden palvelujen viat näkyvät
käyttäjälle tavallisesti viestinä "verkko ei toimi", vaikka kaapelit
ja reititys ovat kunnossa.

## DHCP

DHCP-asiakas lähettää yleislähetyksenä etsintäviestin (DISCOVER),
palvelin tarjoaa osoitteen (OFFER), asiakas pyytää sitä (REQUEST) ja
palvelin vahvistaa (ACK). Osoite on *vuokrattu* määräajaksi, jonka
puolivälissä asiakas uusii vuokran. Tarjous sisältää myös optiot:
yhdyskäytävä (3), nimipalvelimet (6), verkkotunnus (15),
käynnistystiedosto (67) ja niin edelleen.

dnsmasq on kevyt DHCP-, DNS- ja TFTP-palvelin, joka sopii pieniin
verkkoihin, laboratorioihin ja sulautettuihin reitittimiin. Isommissa
verkoissa käytetään esimerkiksi ISC Keaa ja erillistä
nimipalvelinta. Asetukset ovat samat:

```{.bash tiedosto="esimerkit/06-dhcp.sh" osa="dnsmasq"}
```

Asiakkaana on busyboxin `udhcpc`. Se ajaa tarjouksen saatuaan skriptin,
jolle tiedot välitetään ympäristömuuttujina:

```{.bash tiedosto="esimerkit/06-dhcp.sh" osa="asiakas"}
```

Tulostin saa aina saman osoitteen kiinteän varauksen ansiosta, ja
asiakas saa osoitteen dynaamiselta alueelta. Varaus tehdään DHCP-palvelimelle eikä
laitteeseen käsin: osoite pysyy dokumentoituna yhdessä paikassa, ja
laitteen vaihtuessa riittää päivittää MAC-osoite.

DHCP toimii yleislähetyksillä, joten se ei ylitä reititintä. Kun
palvelin on keskitetty, reititin välittää viestit sille
(*DHCP relay*, `ip helper-address`) ja lisää tiedon siitä, mistä
segmentistä pyyntö tuli. Tämän tiedon perusteella palvelin valitsee
oikean osoitealueen.

Väärä DHCP-palvelin samassa segmentissä (kuluttajareititin, jonka joku
kytki seinään, tai hyökkääjän palvelin) jakaa vääriä yhdyskäytäviä ja
nimipalvelimia. Kytkimen *DHCP snooping* sallii DHCP-tarjoukset vain
luotetuista porteista ja kirjaa, mikä osoite on missäkin portissa.
Kirjanpidon varassa toimivat myös ARP-väärennösten esto (*dynamic ARP
inspection*) ja lähdeosoitteen tarkistus.

## Verkkokäynnistys

PXE-käynnistyksessä verkkokortin laiteohjelmisto hakee DHCP:llä osoitteen
ja käynnistystiedoston nimen (`dhcp-boot`), lataa tiedoston TFTP:llä ja
suorittaa sen. Ladattava tiedosto on tyypillisesti iPXE tai GRUB, joka
hakee varsinaisen asentimen nopeammin HTTP:llä.

```{.bash tiedosto="esimerkit/06-dhcp.sh" osa="pxe"}
```

TFTP:ssä ei ole todennusta eikä salausta, joten käynnistyspalvelu
rajataan asennusverkkoon. UEFI-laitteissa käytetään mieluiten
HTTP-käynnistystä ja Secure Bootia, jolloin ladatun koodin
allekirjoitus tarkistetaan.

## DNS sisäverkossa

Sisäverkon nimipalvelu vastaa organisaation omille nimille ja välittää
muut kyselyt eteenpäin. Esimerkissä dnsmasq vastaa vain paikallisen
verkkotunnuksen kyselyihin. DHCP:llä osoitteen saaneet laitteet, kuten
tulostin, saavat nimen automaattisesti:

```{.bash tiedosto="esimerkit/06-dhcp.sh" osa="nimet"}
```

```{.tuloste tiedosto="esimerkit/06-dhcp.odotettu"}
```

Sisäverkon nimiä suunniteltaessa kannattaa käyttää organisaation oman
verkkotunnuksen aluetta (`sisa.esimerkki.fi`) tai sisäverkoille varattua
`internal`-tunnusta. Keksitty tunnus, kuten `.local` tai `.corp`, voi
törmätä mDNS:ään tai myöhemmin julkiseksi tulevaan ylätunnukseen.
`.lan` on esimerkeissä vain lyhyyden vuoksi.

## Käytännössä

- **Kiinteät varaukset DHCP:ssä, ei laitteissa.** Palvelimet ja
  verkkolaitteet ovat poikkeus: niiden osoitteet asetetaan
  kiinteästi, jotta ne toimivat, vaikka DHCP ei toimisi.
- **Kaksi palvelinta.** DHCP ja DNS ovat kriittisiä palveluja; niistä
  on aina kahdennettu toteutus (DHCP-vikasieto tai jaetut alueet,
  kaksi nimipalvelinta).
- **Vuokra-aika segmentin mukaan.** Vierasverkossa laitteet vaihtuvat
  nopeasti (tunnin vuokra), toimistossa harvoin (päivästä viikkoon).
- **DHCP snooping ja ARP-tarkistus päälle** pääsykytkimissä.
- **TFTP vain asennusverkkoon,** ja mieluiten HTTP-käynnistys
  allekirjoituksin.
- **Nimet ennen osoitteita.** Palvelut ja säännöt viittaavat nimiin, kun
  se on mahdollista; osoitteen vaihtuessa muutos tehdään yhteen paikkaan.

## Itsearviointi

- Osaat selittää DHCP:n viestit, vuokran ja tärkeimmät optiot sekä
  DHCP-välityksen reitittimen yli.
- Osaat määrittää DHCP-palvelimen dynaamisine alueineen ja kiinteine
  varauksineen ja tarkistaa asiakkaan saamat tiedot.
- Osaat kuvata verkkokäynnistyksen vaiheet ja sen tietoturvariskit.
- Osaat suunnitella sisäverkon nimiavaruuden ja selittää DHCP snoopingin
  ja ARP-tarkistuksen tarkoituksen.
