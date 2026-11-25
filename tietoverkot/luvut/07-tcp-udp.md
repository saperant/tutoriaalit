# TCP, UDP ja portit

IP toimittaa paketin koneelle. Kuljetuskerros toimittaa datan koneen
oikealle *ohjelmalle* ja päättää, millaisen palvelun sovellus saa.
Ohjelman tunnistaa **portti**, 16-bittinen luku. Yhteyden yksilöi
viisikko: protokolla, lähdeosoite, lähdeportti, kohdeosoite ja
kohdeportti. Siksi sama palvelin voi palvella tuhansia asiakkaita
samassa portissa. Luku käy läpi portit, UDP:n ja TCP:n erot
sovelluksen kannalta, TCP-yhteyden elinkaaren kaappauksesta, TCP:n
luotettavuuden ja nopeudensäädön sekä MTU:n.

## Portit

| Alue | Käyttö |
|------|--------|
| 0–1023 | Tunnetut palvelut; kuunteluun tarvitaan Linuxissa erityisoikeus |
| 1024–49151 | Rekisteröidyt palvelut (esim. 5432 PostgreSQL, 8080 HTTP-vaihtoehto) |
| 32768–60999 | Linuxin oletus lyhytikäisille asiakasporteille (`ip_local_port_range`) |

Tavallisia: 22 SSH, 25 SMTP, 53 DNS, 67/68 DHCP, 80 HTTP, 123 NTP,
443 HTTPS, 3389 RDP, 5353 mDNS. Portti on sopimus, ei tunniste:
palvelu voi kuunnella missä portissa tahansa, ja palomuurin "porttiin
443 sallittu" ei kerro, mitä liikenne oikeasti on.

`ss` näyttää koneen soketit. Valitsimet `-t` (TCP), `-u` (UDP), `-l`
(kuuntelevat), `-a` (kaikki), `-n` (numeroina) ja `-p` (prosessi):

```{.bash tiedosto="esimerkit/07-portit.sh" osa="portit"}
```

```{.tuloste tiedosto="esimerkit/07-portit.odotettu"}
```

Kuunteluosoite ratkaisee, mistä palveluun pääsee: `127.0.0.1:8080`
vain samalta koneelta, `0.0.0.0:5353` kaikista liitännöistä. Kehityksen
aikana avattu `0.0.0.0` on tavallinen tapa paljastaa keskeneräinen
palvelu koko verkolle.

## UDP ja TCP

| | UDP | TCP |
|--|-----|-----|
| Yhteys | ei | kättely ennen dataa |
| Toimitus | voi kadota, monistua, vaihtaa järjestystä | luotettava ja järjestyksessä |
| Rajat | viesti = datagrammi | tavuvirta ilman viestirajoja |
| Vuonhallinta | ei | vastaanottajan ikkuna |
| Ruuhkanhallinta | ei (sovelluksen vastuulla) | kyllä |
| Käyttö | DNS, DHCP, NTP, media, pelit, QUIC | HTTP/1–2, SSH, tietokannat |

Sovelluksen näkökulmasta tärkein ero on **viestirajat**:

```{.python tiedosto="esimerkit/07-yhteys.py" osa="palvelin"}
```

```{.python tiedosto="esimerkit/07-yhteys.py" osa="virta"}
```

```{.python tiedosto="esimerkit/07-yhteys.py" osa="datagrammi"}
```

```{.tuloste tiedosto="esimerkit/07-yhteys.odotettu"}
```

TCP-lukija sai kolme lähetystä yhdellä lukukerralla. TCP ei tunne
viestejä, joten sovellusprotokollan on itse merkittävä viestien rajat:
pituuskentällä, erotinmerkillä (rivinvaihto) tai otsakkeella (HTTP:n
`Content-Length`). Yleinen virhe on olettaa, että yksi `recv` palauttaa
yhden `send`-kutsun datan. Se toimii testissä omalla koneella ja
hajoaa verkossa. UDP taas säilyttää rajat, mutta datagrammi voi kadota.

Suljettuun porttiin TCP vastaa RST-paketilla, ja asiakas saa heti
virheen *Connection refused*. UDP:ssa ei ole yhteyttä, joten
vastaanottajan kone ilmoittaa ICMP-viestillä *port unreachable*. Linux
toimittaa sen sovellukselle vain, jos UDP-soketti on yhdistetty
(`connect`):

```{.python tiedosto="esimerkit/07-yhteys.py" osa="suljettu"}
```

Palomuuri, joka hylkää paketit hiljaa, näkyy asiakkaalle erilaisena:
yhteys ei torju vaan *aikakatkaisee*. Se on vianetsinnän vihje: torjunta
tarkoittaa, että kone vastasi, aikakatkaisu, että jokin välissä nieli
paketin.

## TCP-yhteyden elinkaari

Kaapataan yksi lyhyt TCP-yhteys verkkonimiavaruuksissa. Asiakas
lähettää "hei", palvelin vastaa "HEI", ja molemmat sulkevat:

```{.bash tiedosto="esimerkit/07-kattely.sh" osa="kaappaus"}
```

Kaappauksen tulkinnassa järjestysnumerot näytetään suhteellisina:

```{.bash tiedosto="esimerkit/07-kattely.sh" osa="tulkinta"}
```

```{.tuloste tiedosto="esimerkit/07-kattely.odotettu"}
```

Liput: `S` = SYN, `.` = ACK, `P` = PSH (data perille heti), `F` = FIN.

Sama kaappaus sekvenssikaaviona. Kaavio piirretään yllä olevasta
tulosteesta, joten viestit ovat ne, jotka laboratoriossa kulkivat:
kolmivaiheinen kättely, data kumpaankin suuntaan ja sulkeminen, jossa
kumpikin puoli lähettää oman FIN-viestinsä.

```{.dot tiedosto="kaaviot/07-kattely.dot" otsikko="TCP-yhteyden elinkaari kaappauksesta"}
```

1. **Kolmivaiheinen kättely**: SYN, SYN-ACK, ACK. Kumpikin osapuoli
   valitsee satunnaisen alkujärjestysnumeron (ISN) ja kuittaa toisen
   numeron +1. Kättely maksaa yhden edestakaisen viiveen (RTT) ennen
   ensimmäistä datatavua; TLS lisää siihen omansa.
2. **Data**: järjestysnumero kertoo tavun paikan virrassa, kuittaus
   seuraavan odotetun tavun.
3. **Lopetus**: kumpikin suunta suljetaan erikseen FIN-paketilla. FIN
   kuluttaa yhden järjestysnumeron, siksi kuittaus on 5 eikä 4.

Ensin sulkeva osapuoli jää tilaan `TIME_WAIT` (Linuxissa 60 sekuntia),
jotta myöhästyneet paketit eivät sekoitu uuteen yhteyteen. Palvelin,
joka avaa tuhansia lyhyitä yhteyksiä samaan kohteeseen, voi kuluttaa
asiakasporttinsa loppuun. Yhteyksien uudelleenkäyttö (*connection
pooling*, HTTP keep-alive) ratkaisee ongelman.

## Luotettavuus, vuonhallinta ja ruuhkanhallinta

IP saa kadottaa paketteja, toimittaa ne väärässä järjestyksessä ja
monistaa niitä. TCP rakentaa sen päälle luotettavan tavuvirran ja
säätää samalla lähetysnopeutta kahdesta syystä: vastaanottajan ja
verkon suojaksi.

**Luotettavuus.** Lähettäjä säilyttää jokaisen segmentin, kunnes
vastaanottaja on kuitannut sen. Jos kuittausta ei tule
uudelleenlähetysajan (RTO, *retransmission timeout*) kuluessa,
segmentti lähetetään uudelleen. Ydin mittaa kierrosaikaa jatkuvasti ja
johtaa RTO:n siitä, joten aika mukautuu yhteyteen: lähiverkossa se on
Linuxissa vähintään 200 ms, hitaalla yhteydellä sekunteja. Pitkässä
siirrossa katoaminen huomataan nopeammin: jos kadonneen segmentin
jälkeen saapuu muita, vastaanottaja toistaa saman kuittauksen, ja
kolmas toisto käynnistää uudelleenlähetyksen heti (*fast
retransmit*). SACK-optiolla vastaanottaja kertoo lisäksi, mitkä
myöhemmät tavut se jo sai, jolloin vain puuttuvat lähetetään.

Laboratoriossa palvelimen palomuurisääntö pudottaa ensimmäisen
datasegmentin:

```{.bash tiedosto="esimerkit/07-haviot.sh" osa="pudotus"}
```

```{.bash tiedosto="esimerkit/07-haviot.sh" osa="liikenne"}
```

```{.tuloste tiedosto="esimerkit/07-haviot.odotettu"}
```

Sovellus ei huomannut mitään: vastaus `HEI` tuli perille, vain hieman
myöhemmin. Kaappauksessa sama segmentti (`seq 1`, kolme tavua) lähtee
kahdesti, ja ytimen laskuri `TcpRetransSegs` kasvoi yhdellä. Laskurin
kasvu tuotantokoneessa (`nstat`, `ss -ti`) on ensimmäinen merkki
pakettihäviöstä polulla.

```{.dot tiedosto="kaaviot/07-haviot.dot" otsikko="Kadonnut segmentti ja sen uudelleenlähetys (kaavio on piirretty yllä olevasta kaappauksesta)"}
```

**Vuonhallinta** suojaa vastaanottajaa. Jokaisessa segmentissä
vastaanottaja ilmoittaa **ikkunan**: montako tavua sen
vastaanottopuskuriin vielä mahtuu. Lähettäjä ei pidä matkalla enempää
kuittaamatonta dataa. Jos vastaanottava sovellus ei lue sokettiaan,
puskuri täyttyy, ikkuna kutistuu nollaan ja lähettäjä pysähtyy,
kunnes tilaa vapautuu. Hidas lukija hidastaa siis lähettäjää
(vastapaine). Kättelyssä sovittu skaalauskerroin (*window scaling*)
sallii 64 kilotavua suuremmat ikkunat, joita nopeat ja pitkäviiveiset
yhteydet tarvitsevat.

**Ruuhkanhallinta** suojaa verkkoa. Lähettäjä ei tiedä polun
kapasiteettia, joten se etsii sen kokeilemalla. Sillä on oma
**ruuhkaikkunansa**, ja matkalla saa olla dataa enintään pienempi
kahdesta ikkunasta. Yhteys alkaa **hitaalla aloituksella**: ruuhkaikkuna
on aluksi noin kymmenen segmenttiä ja kaksinkertaistuu jokaisella
kierroksella. Kun raja löytyy, kasvu hidastuu tasaiseksi (**ruuhkan
välttäminen**), ja kun paketti katoaa, ikkunaa pienennetään
tuntuvasti. Algoritmeja on useita: Linuxin oletus CUBIC tulkitsee
katoamisen ruuhkaksi, BBR mallintaa polun kaistaa ja viivettä.
Periaate on kaikissa sama, ja siitä seuraa kolme asiaa, jotka näkyvät
sovellukselle:

- Uusi yhteys on aluksi hidas. Lyhyen siirron kesto määräytyy
  kierrosten määrästä, ei linkin nopeudesta, mikä on yksi syy käyttää
  yhteyksiä uudelleen.
- Pakettihäviö hidastaa TCP:tä enemmän kuin kadonneiden pakettien
  verran. Prosentin häviö langattomalla linkillä voi pudottaa
  nopeuden murto-osaan.
- Samaa pullonkaulaa käyttävät yhteydet jakavat kaistan keskenään
  suunnilleen tasan, koska jokainen perääntyy häviöistä.

Liukuvan ikkunan protokollien teoria ja ikkunan mitoitus kaistan ja
viiveen tulosta ovat taidossa *Tietoliikennetekniikka*, ja soketin
puskurit sovelluksen kannalta taidossa *Verkko-ohjelmointi*.

## MTU ja pilkkominen

Polun pienin MTU määrää, kuinka suuri IP-paketti pääsee perille
pilkkomatta. Tunnelit (VPN, VXLAN, PPPoE) pienentävät MTU:ta
otsakkeillaan. Laboratoriossa R–B-linkin MTU on 1400:

```{.bash tiedosto="esimerkit/07-mtu.sh" osa="mtu"}
```

```{.bash tiedosto="esimerkit/07-mtu.sh" osa="df"}
```

```{.bash tiedosto="esimerkit/07-mtu.sh" osa="pilkonta"}
```

```{.tuloste tiedosto="esimerkit/07-mtu.odotettu"}
```

DF-lipullinen 1500 tavun paketti ei mahdu, ja reititin palauttaa
ICMP-viestin *Fragmentation needed* (mtu = 1400). Lähettäjän ydin
tallentaa polun MTU:n (`ip route get` näyttää sen), ja seuraava
lähetys mahtuu. Tätä kutsutaan *Path MTU Discoveryksi*. Ilman DF-lippua
reititin pilkkoo paketin kahdeksi, ja vastaanottaja kokoaa palat. Vain
ensimmäisessä palassa on ICMP- tai TCP-otsake, joten palomuurit ja
kuormantasaimet eivät näe muiden palojen porttinumeroita.

TCP välttää pilkkomisen kokonaan: kättelyssä osapuolet kertovat
suurimman segmenttikokonsa (MSS, tavallisesti MTU − 40).

## Käytännössä

- **Kehystä viestit TCP:ssä itse** pituuskentällä tai erottimella, ja
  lue silmukassa, kunnes viesti on kokonainen.
- **Aseta aikakatkaisut.** Oletuksena `connect` ja `recv` voivat odottaa
  minuutteja. Jokainen verkkokutsu tarvitsee aikarajan.
- **Erota torjunta ja aikakatkaisu.** *Connection refused*: kone vastaa,
  mutta portti on kiinni. Aikakatkaisu: reitti, palomuuri tai kone
  alhaalla.
- **MTU-ongelman tunnistaa** siitä, että pienet pyynnöt toimivat mutta
  suuret vastaukset jumittuvat (SSH-yhteys aukeaa, mutta `ls` suuressa
  hakemistossa jää kesken). Syy on lähes aina estetty ICMP tai tunnelin
  pienempi MTU.
- **UDP vaatii sovellukselta enemmän**: uudelleenlähetyksen, järjestyksen
  ja nopeuden rajoittamisen. Valitse UDP vain, kun ymmärrät miksi, tai
  käytä valmista protokollaa (QUIC).

## Itsearviointi

- Osaat selittää porttien, viisikon ja kuunteluosoitteen merkityksen ja
  tarkastella niitä `ss`-komennolla.
- Osaat vertailla TCP:tä ja UDP:tä ja perustella valinnan.
- Osaat kuvata TCP:n kättelyn, järjestysnumerot ja lopetuksen
  kaappauksesta sekä `TIME_WAIT`-tilan seuraukset.
- Osaat selittää, miten TCP havaitsee kadonneen segmentin, ja
  tunnistaa uudelleenlähetyksen kaappauksesta ja ytimen laskureista.
- Osaat erottaa vuonhallinnan ja ruuhkanhallinnan ja kertoa, miten
  hidas aloitus ja pakettihäviö näkyvät sovelluksen nopeudessa.
- Osaat selittää MTU:n, polun MTU:n selvityksen ja pilkkomisen sekä
  tunnistaa MTU-ongelman oireet.
- Osaat kertoa, miksi TCP-sovelluksen on kehystettävä viestinsä itse.
