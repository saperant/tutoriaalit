# Suunnittelu, osoitteet ja segmentointi

Verkko suunnitellaan ennen kuin yhtään kaapelia kytketään. Suunnitelma
vastaa kolmeen kysymykseen: mitkä laitteet ja käyttäjät saavat puhua
keskenään, mihin verkon pitää venyä seuraavien vuosien aikana ja miten
vika tai virhe pysyy paikallisena. Vastaukset kirjataan
osoitesuunnitelmaan, segmenttikuvaukseen ja sallittujen liikennevirtojen
luetteloon.

## Rakenne: kerrokset ja vikaantumisalueet

Perinteinen kampusverkko jaetaan kolmeen kerrokseen:

- **Pääsykerros** (*access*): kytkimet, joihin työasemat, puhelimet,
  tulostimet ja tukiasemat kytketään. Täällä tehdään VLAN-jako,
  802.1X ja porttiturva.
- **Jakelukerros** (*distribution*): kokoaa pääsykytkimet, reitittää
  segmenttien välillä ja suodattaa liikennettä.
- **Runko** (*core*): nopea ja yksinkertainen siirtokerros
  rakennusten tai konesalien välillä.

Pienessä verkossa jakelu ja runko yhdistetään (*collapsed core*).
Konesaleissa käytetään *spine–leaf*-rakennetta: jokainen lehtikytkin
on yhteydessä jokaiseen runkokytkimeen, joten kahden palvelimen välillä
on aina yhtä monta hyppyä, ja kaikki yhteydet ovat käytössä yhtä aikaa
(ECMP) eikä STP estä niistä yhtäkään.

Kerrosten tärkein tehtävä on rajata **vikaantumisalue** (*failure
domain*). L2-segmentti on yksi yleislähetysalue: silmukka, ARP-myrsky tai
väärä DHCP-palvelin vaikuttaa koko segmenttiin. Siksi L2-alueet pidetään
pieninä ja ne yhdistetään reitittämällä.

## Segmentointi

Segmentti on joukko laitteita, joilla on sama luottamustaso ja sama
tehtävä. Tyypillinen yritysverkko jaetaan esimerkiksi näin:

| Segmentti | Sisältö | Saa puhua |
|-----------|---------|-----------|
| Hallinta | verkkolaitteiden ja palvelinten hallintaliitännät | vain ylläpidon hyppykoneelta |
| Toimisto | työasemat | palvelimille ja internetiin |
| Puhelimet | IP-puhelimet | puhepalvelimelle |
| Palvelimet | sisäiset palvelut | toisilleen sovitusti |
| IoT | kamerat, automaatio | vain omaan hallintapalveluunsa |
| Vieraat | vierailijoiden laitteet | vain internetiin |

Segmentointi on tietoturvan perusta: kun työasema saastuu, se näkee vain
oman segmenttinsä ja ne palvelut, jotka sille on erikseen sallittu.
Segmenttien välinen liikenne kulkee reitittimen tai palomuurin kautta,
jossa sääntöjä voi valvoa ja kirjata. Hienojakoisin muoto on
*mikrosegmentointi*, jossa jokaisella työkuormalla on omat sääntönsä.

## Osoitesuunnitelma

Osoitesuunnitelma kertoo, mikä osoitelohko kuuluu millekin segmentille ja
toimipisteelle. Hyvä suunnitelma on **hierarkkinen**: toimipisteen kaikki
segmentit ovat samassa lohkossa, jolloin muille toimipisteille riittää
yksi koottu reitti (*summarization*). Se jättää **kasvuvaraa** ja on
**ennustettava**: osoitteesta näkee, missä laite on.

IPv4-lohkon koko valitaan laitemäärän ja kasvuvaran mukaan. Esimerkin
ohjelma jakaa toimipisteen /21-lohkon segmenteille suurimmasta
pienimpään, jolloin jokainen aliverkko alkaa kokonsa rajalta:

```{.python tiedosto="esimerkit/02-osoitesuunnitelma.py"}
```

```{.tuloste tiedosto="esimerkit/02-osoitesuunnitelma.odotettu"}
```

IPv6:ssa koon miettiminen jää pois: jokainen segmentti saa /64-verkon,
koska osoitteiden automaattinen määritys (SLAAC) edellyttää sitä.
Toimipiste saa tyypillisesti /48:n, josta riittää 65 536 segmentille.
Esimerkissä VLAN-numero on upotettu etuliitteeseen, joten osoitteesta
`2001:db8:20:30::15` näkee heti, että laite on puhelinverkossa (VLAN 30).
Sama numerointi kannattaa ulottaa IPv4:ään, jos lohkot sallivat.

Yksityiset IPv4-lohkot (RFC 1918) ovat `10.0.0.0/8`, `172.16.0.0/12`
ja `192.168.0.0/16`. Koti- ja kuluttajalaitteet käyttävät lähes aina
`192.168.0.0/24`- tai `192.168.1.0/24`-verkkoa. Jos yrityksen
segmentti on samassa verkossa, kotoa tehty VPN-yhteys ei toimi, koska
sama verkko on molemmissa päissä. Siksi yritysverkkoon valitaan
harvinaisempi lohko `10.`-avaruudesta.

## Nimeäminen ja dokumentointi

Laitteiden, liitäntöjen ja segmenttien nimet noudattavat sovittua
kaavaa, esimerkiksi `hki-sw-03` (toimipiste, laitetyyppi, numero) ja
`vl30-puhelimet`. Kun vianetsijä näkee lokissa nimen, sen pitää kertoa
paikka ja tehtävä.

Dokumentaatio on ajan tasalla vain, jos se on totuuden lähde
(*source of truth*), josta asetukset tuotetaan, eikä erillinen
taulukko, jota päivitetään käsin muutosten jälkeen. Tähän palataan
luvussa *Verkko koodina*. Yleisiä totuuden lähteitä ovat NetBox ja
Nautobot sekä versionhallinnassa oleva kuvaus.

## Käytännössä

- **Segmentoi luottamuksen mukaan, ei organisaatiokaavion.** Taloushallinnon
  ja myynnin työasemat ovat samanlaisia laitteita; tulostimet ja kamerat
  eivät ole. Segmentti on turvallisuusraja, ja jokainen raja maksaa
  sääntöjen ylläpitona.
- **Hallintaverkko erillään.** Verkkolaitteiden ja palvelinten
  hallintaliitännät (SSH, SNMP, BMC) ovat omassa segmentissään, johon pääsee
  vain hyppykoneelta. Kun käyttäjäverkko on hyökkääjän hallussa,
  infrastruktuuri ei ole.
- **Pienet L2-alueet, reititys niiden välissä.** Vika jää segmenttiin,
  ja reitittävä raja on luonteva paikka suodatukselle.
- **Hierarkkinen ja harva osoitteistus.** Kasvuvara kannattaa varata
  heti: osoitteiden vaihtaminen jälkikäteen on yksi kalleimmista
  verkkomuutoksista, koska se koskee jokaista laitetta, sääntöä ja
  dokumenttia.
- **Varaa IPv6 alusta asti**, vaikka sitä ei heti otettaisi käyttöön.
  Samanrakenteinen suunnitelma tekee siirtymästä halvan.
- **Sallittujen virtojen luettelo on osa suunnitelmaa.** Kun
  luettelossa lukee, että puhelimet saavat puhua vain puhepalvelimelle,
  palomuurisääntö syntyy suoraan siitä.

## Itsearviointi

- Osaat selittää pääsy-, jakelu- ja runkokerroksen sekä spine–leaf-rakenteen
  tehtävät ja sen, miksi L2-alueet pidetään pieninä.
- Osaat jakaa toimipisteen verkon segmentteihin luottamustason mukaan ja
  perustella, miksi hallintaverkko on erillään.
- Osaat laatia hierarkkisen IPv4- ja IPv6-osoitesuunnitelman kasvuvaroineen
  ja selittää, miksi /64 on IPv6-segmentin koko.
- Osaat kertoa, miksi osoitesuunnitelman ja muun dokumentaation pitää olla
  totuuden lähde eikä jälkikäteen päivitettävä kuvaus.
