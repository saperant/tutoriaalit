# Palvelun laatu

Kun yhteys ei ole ruuhkautunut, kaikki liikenne kulkee viipymättä, eikä
laatujärjestelyjä tarvita. Ruuhka syntyy pullonkaulaan: lähiverkon
gigabitti kohtaa sadan megabitin internet-yhteyden, tai kymmenen
palvelinta lähettää samaan porttiin. Silloin paketit jonottavat, ja
jonon pituus näkyy viiveenä, viiveen vaihteluna ja lopulta
pudotuksina. Palvelun laatu (*Quality of Service*, QoS) päättää,
kenen paketit jonottavat ja kenen pudotetaan. Miksi viive kasvaa
jyrkästi kuormituksen lähestyessä sataa prosenttia ja miten
prioriteettijono ja rahakkeen ämpäri toimivat, on selitetty taidossa
*Tietoliikennetekniikka*. Tämä luku näyttää, miten samat mekanismit
asetetaan reitittimeen.

## Mihin QoS:ää tarvitaan

Sovellukset sietävät ruuhkaa eri tavoin:

| Liikenne | Kaistaa | Viive | Vaihtelu | Häviö |
|----------|---------|-------|----------|-------|
| Puhe (VoIP) | vähän | < 150 ms | < 30 ms | < 1 % |
| Videoneuvottelu | kohtalaisesti | < 150 ms | pieni | < 1 % |
| Interaktiivinen (SSH, verkkosivut) | vähän | pieni | sietää | sietää |
| Joukkosiirrot (varmuuskopiot, päivitykset) | paljon | sietää | sietää | sietää |

Puhe kärsii jo silloin, kun varmuuskopio täyttää jonon muutamaksi
sadaksi millisekunniksi. Ratkaisu ei ole lisäkaista vaan jonotus, joka
päästää puheen jonon ohi.

## Luokittelu ja merkintä

Liikenne luokitellaan verkon reunalla ja merkitään, jotta seuraavien
laitteiden ei tarvitse luokitella sitä uudelleen. IP-otsakkeen
DSCP-kentässä (6 bittiä) on merkinnät, kuten EF (*Expedited
Forwarding*, 46) puheelle, AF41 videolle ja CS0 tavalliselle
liikenteelle. Ethernet-tasolla vastaava kenttä on 802.1Q-merkinnän
PCP.

Merkintää ei voi ottaa vastaan sellaisenaan, sillä työasema voi merkitä
kaiken liikenteensä puheeksi. Siksi verkon reunalle asetetaan
**luottamusraja** (*trust boundary*): puhelinverkon liikenne merkitään
EF:ksi, ja kaiken muun merkinnät nollataan.

```{.bash tiedosto="esimerkit/07-qos.sh" osa="luottamusraja"}
```

## Jonotus ja muotoilu

Linuxissa jonotusta ohjaa `tc` (*traffic control*). Lähtevälle
liitännälle asetetaan jonotusalgoritmi (*qdisc*). HTB (*Hierarchical
Token Bucket*) jakaa kaistan hierarkkisiin luokkiin: kukin luokka saa
taatun osuutensa (`rate`), ja vapaata kaistaa voi lainata ylärajaan asti
(`ceil`). Prioriteetti ratkaisee, kuka lainaa ensin.

```{.bash tiedosto="esimerkit/07-qos.sh" osa="htb"}
```

```{.dot otsikko="Esimerkin HTB-luokkapuu. Luokat saavat taatun osuutensa ja voivat lainata vapaata kaistaa juuriluokan rajaan asti; puheluokka lainaa ensin."}
digraph {
  rankdir=TB; nodesep=0.5; ranksep=0.45;
  q [label="qdisc 1: htb\noletusluokka 1:30"];
  juuri [label="luokka 1:1\nrate 10 Mbit/s"];
  puhe [label="luokka 1:10 (puhe)\nrate 2, ceil 10 Mbit/s\nprio 0"];
  muu [label="luokka 1:30 (muu)\nrate 8, ceil 10 Mbit/s\nprio 1"];
  suodin [label="suodin: DSCP EF", shape=note, fillcolor="#FFFFFF"];
  q -> juuri; juuri -> puhe; juuri -> muu;
  suodin -> puhe [style=dashed];
  {rank=same; suodin; puhe; muu}
}
```

Juuriluokka on 10 Mbit/s, vaikka liitäntä olisi gigabitin, koska
pullonkaula on operaattorin yhteydessä. Jos reititin lähettäisi
täydellä nopeudella, jono muodostuisi operaattorin laitteeseen, jota
emme hallitse. **Muotoilu** (*shaping*) hieman yhteyden nopeutta
hitaammaksi siirtää jonon omaan laitteeseen, jossa jonotus on meidän
päätettävissämme.

Puhelin lähettää tavallisia paketteja, ja työasema yrittää merkitä
omansa puheeksi:

```{.bash tiedosto="esimerkit/07-qos.sh" osa="laskurit"}
```

```{.tuloste tiedosto="esimerkit/07-qos.odotettu"}
```

Puhelimen kolme pakettia päätyivät puheluokkaan `1:10`, koska
luottamusraja merkitsi ne. Työaseman merkinnät nollattiin, joten sen
neljä pakettia päätyivät oletusluokkaan `1:30`. Laskurit (`tc -s`) ovat
QoS:n vianetsinnän perustyökalu: niistä näkee, luokitellaanko liikenne
oikein ja pudotetaanko jossain luokassa.

## Jonon pituus ja AQM

Pitkä jono ei lisää kaistaa, se lisää vain viivettä (*bufferbloat*).
Aktiivinen jononhallinta (AQM), kuten CoDel ja sen muunnelma fq_codel,
pudottaa tai merkitsee (ECN) paketteja jo silloin, kun viive alkaa
kasvaa, jolloin TCP hidastaa ajoissa. fq_codel jakaa lisäksi kaistan
virtojen kesken reilusti, joten yksittäinen suuri siirto ei tukahduta
muita. Se on monen Linux-jakelun oletus, ja HTB-luokkien lehtiin se
lisätään omana jonotusalgoritminaan. Kotireitittimissä samaa
tarkoitusta palvelee CAKE, joka yhdistää muotoilun, reiluuden ja AQM:n
yhteen algoritmiin.

## Rajoitukset

QoS toimii vain siinä, mitä hallitsemme. Internetissä DSCP-merkintöjä
ei kunnioiteta, joten operaattorin yli kulkevan puheen laatu riippuu
yhteyden ruuhkasta. Yrityksen toimipisteiden välillä laatua voidaan
taata MPLS-palvelulla tai SD-WAN-ratkaisulla, joka valitsee polun
mitatun laadun perusteella. Saapuvaa liikennettä voi vain rajoittaa
(*policing*) pudottamalla, ei jonottaa, koska paketit ovat jo
kulkeneet pullonkaulan läpi.

## Käytännössä

- **Mittaa ensin.** QoS:ää tarvitaan vain ruuhkautuvissa pisteissä.
  Liitäntöjen käyttöaste, pudotukset ja jonot kertovat, missä ne ovat.
- **Vähän luokkia.** Kolmesta viiteen luokkaa (puhe, video,
  interaktiivinen, oletus, joukkosiirto) riittää lähes aina. Jokainen
  lisäluokka on ylläpitoa ja vianetsintää.
- **Luottamusraja reunalle.** Merkinnät tehdään tai tarkistetaan siellä,
  missä liikenne tulee verkkoon; sisäverkko luottaa merkintöihin.
- **Muotoile hieman alle yhteyden nopeuden,** jotta jono on omassa
  laitteessa.
- **Prioriteettiluokalle katto.** Etuoikeutettu luokka ei saa viedä
  koko kaistaa; muuten väärin merkitty liikenne tukahduttaa kaiken
  muun.
- **fq_codel tai CAKE oletukseksi** ruuhkautuville linkeille.

## Itsearviointi

- Osaat selittää, missä ruuhka syntyy ja miksi QoS koskee vain
  pullonkauloja.
- Osaat määrittää luottamusrajan, joka merkitsee DSCP:n luotetuista
  lähteistä ja nollaa muut.
- Osaat rakentaa HTB-hierarkian taattuine ja lainattavine kaistoineen ja
  todentaa luokittelun laskureilla.
- Osaat selittää muotoilun, AQM:n ja bufferbloatin sekä QoS:n rajat
  internetissä.
