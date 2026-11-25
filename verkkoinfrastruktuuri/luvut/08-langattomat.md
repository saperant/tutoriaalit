# Langattomat verkot ja pääsynhallinta

Langaton verkko ulottuu seinien läpi ja parkkipaikalle. Siksi siinä
pääsynhallinta ja salaus ovat välttämättömiä, ja samat periaatteet
kannattaa ulottaa myös langallisiin portteihin. Tässä luvussa käydään
läpi WLAN-verkon suunnittelu ja 802.1X-pääsynhallinta, ja sen
taustajärjestelmä, RADIUS-palvelin, rakennetaan laboratorioon.

## WLAN-verkon suunnittelu

WLAN-verkon laatu ratkeaa suunnittelussa, ei laitteiden
asetuksissa. Keskeiset käsitteet:

- **Taajuusalueet.** 2,4 GHz kantaa kauas, mutta siinä on vain kolme
  toisistaan erillistä 20 MHz:n kanavaa (1, 6, 11), ja se on täynnä
  muita lähettimiä. 5 GHz:llä kanavia on kymmeniä, ja 6 GHz (Wi-Fi 6E
  ja 7) tarjoaa lisää puhdasta kaistaa lyhyemmällä kantamalla.
- **Kanavat ja kaistanleveys.** Leveä kanava (80–160 MHz) on nopea yhdelle
  laitteelle, mutta tiheässä verkossa kapeammat kanavat (20–40 MHz)
  vähentävät tukiasemien keskinäisiä häiriöitä ja antavat koko
  verkolle enemmän kapasiteettia.
- **Kapasiteetti ennen peittoa.** Tukiasemat mitoitetaan
  samanaikaisten käyttäjien ja sovellusten mukaan, ei pelkän kuuluvuuden.
  Lähetysteho pidetään maltillisena, jotta päätelaite ja tukiasema
  kuulevat toisensa yhtä hyvin ja laite vaihtaa tukiasemaa ajoissa.
- **Verkkovierailu.** Laite päättää itse, milloin se vaihtaa
  tukiasemaa. 802.11k/v/r auttavat laitetta valitsemaan ja nopeuttavat
  vaihtoa, mikä on tärkeää puheelle.
- **Mittaus.** Suunnitelma tehdään ja todennetaan mittaamalla
  (*site survey*), koska rakenteet vaimentavat signaalia ennalta
  arvaamattomasti.

Nämä asiat ovat radioon sidottuja, eikä niitä voi kokeilla
laboratoriossa.

## Salaus ja todennus

| Tila | Käyttö |
|------|--------|
| WPA3-Personal (SAE) | koti ja pieni toimisto: yhteinen salasana, suojattu sanakirjahyökkäyksiltä |
| WPA3-Enterprise (802.1X) | organisaatiot: jokainen käyttäjä tai laite todennetaan erikseen |
| OWE (Enhanced Open) | avoin vierasverkko, jossa liikenne silti salataan |

WEP ja WPA (TKIP) ovat murrettuja, eikä niitä käytetä. Yhteinen
salasana (PSK) on organisaatiossa ongelmallinen: jokainen, joka on
joskus tuntenut sen, pääsee verkkoon, ja sen vaihtaminen koskee kaikkia
laitteita.

## 802.1X

802.1X:ssä on kolme osapuolta:

- **Hakija** (*supplicant*): käyttäjän laite.
- **Todentaja** (*authenticator*): tukiasema tai kytkimen portti. Se
  päästää läpi vain todennusliikenteen, kunnes todennus on onnistunut.
- **Todennuspalvelin**: RADIUS-palvelin, joka tarkistaa tunnukset
  käyttäjähakemistosta ja päättää pääsystä.

```{.dot otsikko="802.1X-todennuksen kulku. Todentaja välittää EAP-viestit hakijan ja RADIUS-palvelimen välillä; menetelmän viestejä (esim. TLS-kättely) kulkee useita kierroksia. Access-Accept kertoo samalla, mihin VLANiin laite sijoitetaan."}
digraph {
  nodesep=0.62; ranksep=0.3;
  node [shape=point, width=0.04, color="#5B6B70"];
  edge [arrowhead=none, style=dashed, color="#B8C4C8"];
  t0 [shape=box, width=1.2, label="hakija\n(laite)"];
  t0 -> t0_0 -> t0_1 -> t0_2 -> t0_3 -> t0_4 -> t0_5 -> t0_6 -> t0_7 -> t0_8 -> t0_9;
  t1 [shape=box, width=1.2, label="todentaja\n(kytkin,\ntukiasema)"];
  t1 -> t1_0 -> t1_1 -> t1_2 -> t1_3 -> t1_4 -> t1_5 -> t1_6 -> t1_7 -> t1_8 -> t1_9;
  t2 [shape=box, width=1.2, label="RADIUS-\npalvelin"];
  t2 -> t2_0 -> t2_1 -> t2_2 -> t2_3 -> t2_4 -> t2_5 -> t2_6 -> t2_7 -> t2_8 -> t2_9;
  {rank=same; t0_0; t1_0; t2_0;}
  {rank=same; t0_1; t1_1; t2_1;}
  {rank=same; t0_2; t1_2; t2_2;}
  {rank=same; t0_3; t1_3; t2_3;}
  {rank=same; t0_4; t1_4; t2_4;}
  {rank=same; t0_5; t1_5; t2_5;}
  {rank=same; t0_6; t1_6; t2_6;}
  {rank=same; t0_7; t1_7; t2_7;}
  {rank=same; t0_8; t1_8; t2_8;}
  {rank=same; t0_9; t1_9; t2_9;}
  edge [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false];
  t1_0 -> t0_1 [label="EAP-Request (Identity)"];
  t0_1 -> t1_2 [label="EAP-Response (Identity)"];
  t1_2 -> t2_3 [label="Access-Request (EAP)"];
  t2_3 -> t1_4 [label="Access-Challenge (EAP)"];
  t1_4 -> t0_5 [label="EAP-Request"];
  t0_5 -> t1_6 [label="EAP-Response"];
  t1_6 -> t2_7 [label="Access-Request (EAP)"];
  t2_7 -> t1_8 [label="Access-Accept + VLAN"];
  t1_8 -> t0_9 [label="EAP-Success"];
}
```

Hakija ja palvelin keskustelevat EAP-protokollalla, jota todentaja
välittää. Suositeltava menetelmä on EAP-TLS, jossa laite todennetaan
varmenteella. Salasanapohjainen PEAP-MSCHAPv2 on yleinen mutta
haavoittuva, ellei laite tarkista palvelimen varmennetta tarkasti.

Langallisessa verkossa sama 802.1X toimii kytkimen portissa. Laitteet,
jotka eivät osaa 802.1X:ää (tulostimet, kamerat), todennetaan
MAC-osoitteen perusteella (MAB). MAC-osoitteen voi väärentää, joten
MAB-laitteet sijoitetaan rajattuun segmenttiin.

## RADIUS ja dynaaminen VLAN

RADIUS-palvelimen vastaus ei kerro vain sitä, pääseekö laite verkkoon,
vaan myös minne: vastauksen attribuutit voivat määrätä VLANin,
pääsylistan tai istunnon aikarajan. Näin sama seinäportti tai sama
WLAN-verkko vie työntekijän toimistoverkkoon ja vieraan vierasverkkoon.

Laboratoriossa RADIUS-palvelimena on FreeRADIUS. Käyttäjät ja heidän
VLANinsa ovat tiedostossa; tuotannossa ne tulevat hakemistosta (LDAP,
Active Directory) ja varmenteista:

```{.bash tiedosto="esimerkit/08-radius.sh" osa="kayttajat"}
```

Palvelimen asetuksissa luetellaan todentajat, jotka saavat kysyä, ja
niiden jaettu salaisuus:

```{.bash tiedosto="esimerkit/08-radius.sh" osa="palvelin"}
```

`require_message_authenticator` torjuu BlastRADIUS-hyökkäyksen (2024),
jossa verkkoyhteyttä manipuloiva hyökkääjä pystyi väärentämään
hylkäyksen hyväksynnäksi. Lisäksi hylkäyksestä poistetaan
valtuutusattribuutit, jotta niitä ei vuoda epäonnistuneille.

Todentajaa jäljittelee `radtest`:

```{.bash tiedosto="esimerkit/08-radius.sh" osa="kysely"}
```

```{.tuloste tiedosto="esimerkit/08-radius.odotettu"}
```

RADIUS-liikenne itsessään on vain osittain suojattu: salasana on
salattu jaetulla salaisuudella, mutta muu sisältö ei. Siksi RADIUS
kulkee hallintaverkossa, ja verkkojen välillä sitä suojataan TLS:llä
(RadSec) tai IPsecillä. Jaettu salaisuus on pitkä ja satunnainen ja
todentajakohtainen.

## Käytännössä

- **WPA3-Enterprise ja EAP-TLS** organisaation laitteille. Varmenteet
  jaetaan laitehallinnan kautta, eikä käyttäjän tarvitse tietää
  salasanaa verkkoon.
- **Laitteiden on tarkistettava palvelimen varmenne.** Muuten hyökkääjän
  tukiasema kerää tunnukset.
- **Dynaaminen VLAN** RADIUSista; porteissa ja verkoissa ei ole
  pysyviä käyttäjäkohtaisia asetuksia.
- **MAB vain rajattuun segmenttiin,** ja siellä vain laitteen tarvitsemat
  virrat.
- **Kaksi RADIUS-palvelinta.** Jos todennus ei toimi, kukaan ei pääse
  verkkoon; todentajille määritetään varapalvelin.
- **Vierasverkko erilleen** sekä radiossa (oma SSID) että
  verkossa (oma VLAN, vain internet).

## Itsearviointi

- Osaat selittää taajuusalueiden, kanavien ja kapasiteetin merkityksen
  WLAN-suunnittelussa.
- Osaat valita WPA3-Personalin, WPA3-Enterprisen ja OWE:n välillä ja
  perustella valinnan.
- Osaat kuvata 802.1X:n osapuolet ja EAP-TLS:n edut sekä MAB:n riskit.
- Osaat määrittää RADIUS-palvelimen todentajineen ja dynaamisine
  VLANeineen ja todentaa sen toiminnan.
