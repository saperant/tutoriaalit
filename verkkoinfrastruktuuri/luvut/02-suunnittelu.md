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

```{.dot otsikko="Kampusverkon kolme kerrosta ja konesalin spine–leaf-rakenne. Jokainen kytkin on yhteydessä kahteen ylemmän kerroksen kytkimeen, joten yhden laitteen tai kaapelin vika ei katkaise yhteyttä."}
graph {
  rankdir=TB; nodesep=0.14; ranksep=0.45;
  subgraph cluster_kampus {
    label="kampus"; style=dashed; color="#B8C4C8";
    c1 [label="runko"]; c2 [label="runko"];
    d1 [label="jakelu"]; d2 [label="jakelu"];
    a1 [label="pääsy"]; a2 [label="pääsy"]; a3 [label="pääsy"];
    c1 -- d1; c1 -- d2; c2 -- d1; c2 -- d2;
    d1 -- a1; d1 -- a2; d1 -- a3; d2 -- a1; d2 -- a2; d2 -- a3;
  }
  subgraph cluster_konesali {
    label="konesali"; style=dashed; color="#B8C4C8";
    s1 [label="spine"]; s2 [label="spine"];
    l1 [label="leaf"]; l2 [label="leaf"]; l3 [label="leaf"]; l4 [label="leaf"];
    s1 -- l1; s1 -- l2; s1 -- l3; s1 -- l4;
    s2 -- l1; s2 -- l2; s2 -- l3; s2 -- l4;
  }
}
```

Kerrosten tärkein tehtävä on rajata **vikaantumisalue** (*failure
domain*). L2-segmentti on yksi yleislähetysalue: silmukka, ARP-myrsky tai
väärä DHCP-palvelin vaikuttaa koko segmenttiin. Siksi L2-alueet pidetään
pieninä ja ne yhdistetään reitittämällä.

## Kahdennettu yhdyskäytävä

Kahdennettu jakelukerros ei vielä auta työasemaa: sillä on yksi
oletusyhdyskäytävän osoite, ja jos sitä pitävä reititin vikaantuu,
segmentti on eristyksissä, vaikka viereinen reititin toimisi.
**VRRP** (*Virtual Router Redundancy Protocol*; valmistajakohtaisia
vastineita ovat HSRP ja GLBP) ratkaisee tämän virtuaalisella
osoitteella. Kaksi reititintä jakaa yhden IP-osoitteen ja siihen
kuuluvan virtuaalisen MAC-osoitteen. Vain aktiivinen reititin vastaa
niihin, ja se lähettää sekunnin välein ilmoituksen. Jos ilmoitukset
lakkaavat, varalla oleva reititin ottaa osoitteen itselleen ja lähettää
pyytämättömän ARP-vastauksen, jolloin kytkimet oppivat virtuaalisen
MAC-osoitteen uuden portin. Työasemien asetukset eivät muutu, ja katko
kestää muutaman sekunnin.

```{.dot otsikko="Kahdennettu yhdyskäytävä. Työasemien oletusyhdyskäytävä on virtuaalinen osoite 10.20.0.1, joka on kerrallaan vain toisella reitittimellä."}
graph {
  rankdir=TB; nodesep=0.5; ranksep=0.5;
  r1 [label="reititin 1\n10.20.0.2\naktiivinen: pitää osoitetta 10.20.0.1"];
  r2 [label="reititin 2\n10.20.0.3\nvaralla: kuuntelee ilmoituksia"];
  sw [label="kytkin, segmentti 10.20.0.0/23"];
  h1 [label="työasema\nyhdyskäytävä 10.20.0.1"];
  h2 [label="työasema\nyhdyskäytävä 10.20.0.1"];
  r1 -- sw; r2 -- sw; sw -- h1; sw -- h2;
  r1 -- r2 [style=dashed, label="VRRP-ilmoitukset", constraint=false];
}
```

Linux-reitittimessä VRRP:n toteuttaa keepalived. Asetusta ei ajeta
tutoriaalin testeissä; se näyttää, mitä kummallekin reitittimelle
kerrotaan:

```text
vrrp_instance toimisto {
    state BACKUP            # molemmat aloittavat varalla
    interface eth0.20
    virtual_router_id 20    # sama molemmilla reitittimillä
    priority 150            # toisella 100: suurin voittaa
    advert_int 1
    virtual_ipaddress { 10.20.0.1/23 }
}
```

Kahdennus on suunniteltava koko polulle. Jos aktiivisen reitittimen
ylävirran yhteys katkeaa mutta laite itse toimii, se pitää osoitteen ja
nielee liikenteen. Siksi prioriteetti sidotaan ylävirran liitännän tai
reitin tilaan (*tracking*), ja vikatilanteet testataan irrottamalla
kaapeleita ennen käyttöönottoa.

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

```{.dot otsikko="Taulukon sallitut liikennevirrat. Nuoli osoittaa yhteyden avaajasta kohteeseen; kaikki, mitä kuvassa ei ole, on estetty."}
digraph {
  rankdir=LR; nodesep=0.22; ranksep=0.9;
  hyppy [label="ylläpidon\nhyppykone"];
  hallinta [label="Hallinta"];
  toimisto [label="Toimisto"]; puhelimet [label="Puhelimet"];
  iot [label="IoT"]; vieraat [label="Vieraat"];
  palvelimet [label="Palvelimet\n(mm. puhepalvelin,\nIoT:n hallintapalvelu)"];
  internet [label="internet", shape=ellipse];
  hyppy -> hallinta;
  toimisto -> palvelimet; toimisto -> internet;
  puhelimet -> palvelimet [label="vain puhepalvelin"];
  iot -> palvelimet [label="vain hallintapalvelu"];
  vieraat -> internet;
}
```

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
- Osaat selittää, miten kahdennettu yhdyskäytävä (VRRP) siirtää
  virtuaalisen osoitteen varareitittimelle ja miksi ylävirran tila on
  otettava huomioon.
- Osaat jakaa toimipisteen verkon segmentteihin luottamustason mukaan ja
  perustella, miksi hallintaverkko on erillään.
- Osaat laatia hierarkkisen IPv4- ja IPv6-osoitesuunnitelman kasvuvaroineen
  ja selittää, miksi /64 on IPv6-segmentin koko.
- Osaat kertoa, miksi osoitesuunnitelman ja muun dokumentaation pitää olla
  totuuden lähde eikä jälkikäteen päivitettävä kuvaus.
