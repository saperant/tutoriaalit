# Kytkentä, VLANit ja silmukat

Kytkin välittää Ethernet-kehyksiä porttien välillä MAC-osoitteiden
perusteella. Se on L2-verkon perusosa, ja sen toiminnan ymmärtäminen
selittää suurimman osan lähiverkkojen vioista: miksi liikenne tulvii,
miksi silmukka kaataa verkon ja miksi väärin asetettu VLAN eristää
laitteen tai päinvastoin päästää sen väärään verkkoon.

## Oppiminen ja välitys

Kytkin oppii lähettäjien MAC-osoitteet: kun kehys tulee porttiin `p2`
osoitteesta `02:…:02:01`, kytkin kirjaa välitystauluunsa (*forwarding
database*, FDB), että tuo osoite on portin `p2` takana. Kehys, jonka
kohdeosoite on taulussa, lähetetään vain oikeaan porttiin. Tuntemattomat
kohteet, yleislähetykset ja ryhmälähetykset **tulvitetaan** kaikkiin
muihin portteihin. Merkintä vanhenee, jos osoitteesta ei kuulu mitään
(Linuxissa oletuksena 300 sekuntia).

Linuxin silta (*bridge*) on ohjelmistokytkin:

```{.bash tiedosto="esimerkit/03-kytkin.sh" osa="silta"}
```

```{.bash tiedosto="esimerkit/03-kytkin.sh" osa="fdb"}
```

```{.tuloste tiedosto="esimerkit/03-kytkin.odotettu"}
```

Kun `h1` pingasi kahta muuta isäntää, kytkin oppi kaikkien kolmen
osoitteet. Välitystaulu on L2-vianetsinnän ensimmäinen työkalu: jos
laitteen osoite ei ole taulussa, se ei ole lähettänyt mitään tai on
väärässä portissa tai VLANissa.

Välitystaulun koko on rajallinen. *MAC-tulvitushyökkäys* täyttää sen
väärennetyillä osoitteilla, jolloin kytkin alkaa tulvittaa kaiken
liikenteen kaikkiin portteihin. Suojana on porttiturva (*port
security*): portista hyväksytään vain rajallinen määrä osoitteita.

## VLANit

VLAN (*virtual LAN*) jakaa yhden fyysisen kytkimen useaksi loogiseksi.
Eri VLANien laitteet eivät näe toistensa kehyksiä, vaikka ne olisivat
samassa kytkimessä; niiden välillä liikenne kulkee reitittimen kautta.
Portti on joko

- **pääsyportti** (*access*, *untagged*): kuuluu yhteen VLANiin, ja
  laite lähettää tavallisia kehyksiä, tai
- **runkoportti** (*trunk*, *tagged*): kuljettaa useaa VLANia, ja
  jokaiseen kehykseen lisätään 802.1Q-merkintä, jossa on 12-bittinen
  VLAN-tunnus (1–4094) ja 3-bittinen prioriteetti (PCP).

Linuxissa VLAN-tietoinen silta asetetaan näin. Esimerkkiä ei ajeta
automaattisesti, koska kaikissa tutoriaalin testiympäristöissä ytimessä
ei ole 802.1Q-tukea; kehityskontissa omalla koneella se toimii:

```text
ip link add br0 type bridge vlan_filtering 1
ip link set dev p1 master br0      # työasema, VLAN 20
ip link set dev p2 master br0      # puhelin, VLAN 30
ip link set dev up1 master br0     # runkoyhteys jakelukytkimelle
bridge vlan add dev p1 vid 20 pvid untagged
bridge vlan add dev p2 vid 30 pvid untagged
bridge vlan add dev up1 vid 20
bridge vlan add dev up1 vid 30
bridge vlan del dev up1 vid 1      # oletus-VLAN pois rungosta
bridge vlan show
```

Reitittimellä kunkin VLANin yhdyskäytävä on oma aliliitäntänsä
(*router on a stick*) tai L3-kytkimen VLAN-liitäntä (SVI):

```text
ip link add link eth0 name eth0.20 type vlan id 20
ip addr add 10.20.0.1/23 dev eth0.20
```

VLANien yleisimmät virheet ovat:

- **Natiivi VLAN.** Runkoportin merkitsemätön liikenne kuuluu natiiviin
  VLANiin (usein 1). Jos se on sama kuin jonkin pääsyportin VLAN,
  hyökkääjä voi lähettää kaksoismerkityn kehyksen toiseen VLANiin
  (*VLAN hopping*). Natiivi VLAN asetetaan käyttämättömäksi, ja
  rungossa merkitään kaikki.
- **Liian sallivat rungot.** Runkoon sallitaan vain ne VLANit, joita
  sen takana tarvitaan. Muuten jokainen VLAN ulottuu joka kytkimelle,
  ja yleislähetysalueet kasvavat.
- **Dynaaminen runkoneuvottelu.** Valmistajien automaattiset
  runkoneuvottelut (esim. DTP) kytketään pois; pääsyportti asetetaan
  pääsyportiksi.

## Silmukat ja STP

Ethernet-kehyksessä ei ole elinaikakenttää kuten IP-paketissa. Jos
kahden kytkimen välillä on kaksi kaapelia, yleislähetys kiertää
silmukkaa ikuisesti ja monistuu jokaisella kierroksella
(*broadcast storm*). Verkko kaatuu sekunneissa.

Silmukoiden esto (*Spanning Tree Protocol*, STP; nykyään RSTP 802.1w ja
MSTP 802.1s) valitsee kytkimistä *juurisillan* ja estää portit, jotka
muodostaisivat silmukan. Juureksi valitaan pienimmän prioriteetin
(ja tasatilanteessa pienimmän MAC-osoitteen) kytkin. Kukin muu kytkin
käyttää halvinta polkuaan juureen, ja jokaisella yhteydellä vain toinen
pää välittää. Kun yhteys katkeaa, estetty portti avautuu.

Kolme kytkintä renkaassa:

```{.bash tiedosto="esimerkit/03-stp.sh" osa="stp"}
```

```{.bash tiedosto="esimerkit/03-stp.sh" osa="tilat"}
```

```{.tuloste tiedosto="esimerkit/03-stp.odotettu"}
```

`k1` on juuri, joten sen molemmat portit välittävät. `k2` ja `k3`
käyttävät suoraa yhteyttään juureen. Niiden välinen yhteys on
tarpeeton, ja sen toinen pää, kytkimen `k3` portti `k2`, on estetty,
koska `k2`:lla on pienempi prioriteetti. Juurisilta valitaan aina
käsin: jos prioriteetit jätetään oletuksiksi, juureksi päätyy
vanhin laite, koska sen MAC-osoite on pienin.

STP:n suojaukset kuuluvat jokaiseen pääsykytkimeen:

- **PortFast / edge port**: työasemaportti siirtyy heti välittäväksi.
- **BPDU Guard**: jos työasemaportista tulee STP-viesti (joku kytki
  kytkimen seinään), portti suljetaan.
- **Root Guard**: jakelukytkimen alaspäin olevista porteista ei
  hyväksytä parempaa juurta.

## L2-verkot reititetyn verkon yli: VXLAN

Konesaleissa L2-alueita ei venytetä fyysisesti, vaan runko reititetään
(L3) ja L2-segmentit kuljetetaan sen yli tunneleissa. VXLAN kapseloi
Ethernet-kehyksen UDP-pakettiin (portti 4789). Segmentin tunnus VNI on
24-bittinen, joten segmenttejä voi olla 16 miljoonaa, kun VLANeja on
4094. Tunnelin päätepiste on VTEP, tyypillisesti lehtikytkin.

```{.bash tiedosto="esimerkit/03-vxlan.sh" osa="vtep"}
```

```{.tuloste tiedosto="esimerkit/03-vxlan.odotettu"}
```

`h1`, `h2` ja `h3` ovat samassa IP-aliverkossa, mutta `h3` on eri
segmentissä, joten se ei vastaa. Esimerkissä VTEPit tuntevat toisensa
kiinteästi (`remote`). Tuotannossa VTEPien osoitteet ja MAC-osoitteiden
sijainnit jaetaan BGP:llä (EVPN), jolloin tulvitusta ei tarvita.

## Käytännössä

- **Tee kytkentä tylsäksi.** Vakiomallin pääsyportti (VLAN, PortFast,
  BPDU Guard, porttiturva, 802.1X) ja runkoportti (sallitut VLANit,
  käyttämätön natiivi VLAN) kirjoitetaan kerran ja monistetaan.
  Poikkeukset ovat vianetsinnän pahin vihollinen.
- **Valitse juurisilta käsin** ja dokumentoi se. Juuri on jakelu- tai
  runkokytkin, ei koskaan pääsykytkin.
- **Älä luota STP:hen suunnittelun välineenä.** STP on turvaverkko
  vahingossa syntyvää silmukkaa vastaan. Redundanssi toteutetaan
  reitittämällä (ECMP) tai linkkien yhdistämisellä (LACP, MLAG), jolloin
  kaikki yhteydet ovat käytössä.
- **Sammuta käyttämättömät portit** ja siirrä ne käyttämättömään
  VLANiin.
- **Välitystaulu ja STP-tila ovat ensimmäiset tarkistukset**, kun
  laite ei näy verkossa: onko osoite opittu, ja missä portissa ja
  VLANissa?

## Itsearviointi

- Osaat selittää, miten kytkin oppii osoitteet, milloin se tulvittaa ja
  miten välitystaulua käytetään vianetsinnässä.
- Osaat määrittää pääsy- ja runkoportit sekä VLAN-liitännät ja välttää
  natiivin VLANin ja liian sallivien runkojen virheet.
- Osaat selittää, miten STP valitsee juuren ja estää silmukan, ja
  ottaa käyttöön PortFastin, BPDU Guardin ja Root Guardin.
- Osaat kertoa, miksi konesaleissa L2-segmentit kuljetetaan VXLANilla
  reititetyn rungon yli.
