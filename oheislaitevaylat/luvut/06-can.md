# CAN

CAN (Controller Area Network) on Boschin 1980-luvulla autoihin
kehittämä väylä, ja nykyään sitä käyttävät myös työkoneet, teollisuus,
lääkintälaitteet ja hissit. Se on suunniteltu häiriöiseen
ympäristöön, jossa yhdellä väylällä on kymmeniä tasavertaisia
solmuja. Väylällä ei ole isäntää. Kuka tahansa voi lähettää, kun
väylä on vapaa, ja yhtäaikaisen lähetyksen ratkaisee arbitraatio,
joka ei hukkaa yhtään bittiä. Laitteisto hoitaa kuittaukset,
virheiden havaitsemisen ja uudelleenlähetykset. Ylemmät protokollat,
kuten CANopen, J1939 ja ISO-TP, määrittelevät viestien merkityksen ja
sen, miten kahdeksaa tavua pidempi viesti siirretään.

QEMU:ssa ei ole CAN-väylää mikrokontrollerikortille, joten tämän
luvun esimerkit ovat Python-malleja. Ne tuottavat kehyksen bitit
väylälle, purkavat ne ja simuloivat arbitraation ja virhelaskurit.

## Fyysinen kerros

Väylä on kierretty johdinpari CANH ja CANL, joka päätetään kummastakin
päästä 120 Ω:n vastuksella. Kun yksikin solmu lähettää *dominanttia*
bittiä (looginen 0), lähetinpiiri nostaa CANH:n noin 3,5 volttiin ja
laskee CANL:n noin 1,5 volttiin. Kun kaikki lähettävät *resessiivistä*
bittiä (1), molemmat johtimet ovat noin 2,5 voltissa ja ero on nolla.
Dominantti voittaa resessiivisen samaan tapaan kuin avokollektoriväylä
(luku 2). Mikrokontrollerin CAN-ohjain kytketään väylään
lähetinpiirin (transceiver) kautta TX- ja RX-nastoilla.

CAN on *viestipohjainen*. Kehyksessä ei ole vastaanottajan osoitetta
vaan tunniste, joka kertoo viestin sisällön ("moottorin kierrosluku")
ja samalla sen prioriteetin. Jokainen solmu vastaanottaa jokaisen
kehyksen, ja ohjaimen hyväksyntäsuodattimet päästävät ohjelmalle vain
sen tarvitsemat tunnisteet.

## Kehys

Perusmuotoisessa (CAN 2.0A) datakehyksessä on 11-bittinen tunniste ja
0–8 tavua dataa:

| Kenttä | Bittejä | Sisältö |
|------------------------|--------|------------------------------|
| SOF | 1 | dominantti, kehyksen alku |
| ID | 11 | tunniste, eniten merkitsevä bitti ensin |
| RTR | 1 | 0 = datakehys, 1 = pyyntökehys |
| IDE, r0 | 2 | 0 = 11-bittinen tunniste |
| DLC | 4 | datan pituus tavuina |
| DATA | 0–64 | data |
| CRC | 15 | tarkistussumma SOF:sta dataan |
| CRC-erotin, ACK, ACK-erotin | 3 | vastaanottajat kuittaavat ACK-paikassa |
| EOF | 7 | resessiivisiä, kehyksen loppu |

```{.python tiedosto="esimerkit/python/mallit/can.py" osa="kehys"}
```

CRC-15 lasketaan bitti kerrallaan siirtorekisterillä täsmälleen niin
kuin standardi sen kuvaa:

```{.python tiedosto="esimerkit/python/mallit/can.py" osa="crc"}
```

### Bittitäyttö

Solmut tahdistuvat resessiivisestä dominanttiin vaihtuviin reuniin.
Pitkä jono samoja bittejä veisi reunat, ja kellot ajautuisivat erilleen.
Siksi lähetin lisää jokaisen viiden samanarvoisen bitin jälkeen
vastakkaisen *täytebitin*, ja vastaanotin poistaa sen. Kuusi samaa
bittiä peräkkäin on siten aina virhe, ja sitä käytetään virhekehyksen
merkkinä.

```{.python tiedosto="esimerkit/python/mallit/can.py" osa="taytto"}
```

```{.python tiedosto="esimerkit/python/can_kehys.py" osa="kentat"}
```

```{.python tiedosto="esimerkit/python/can_kehys.py" osa="virheet"}
```

```{.tuloste tiedosto="esimerkit/python/can_kehys.odotettu"}
```

Sama kehys linjalla. Kaavio on tuotettu mallista: väylän taso bitti
bitiltä, kentät ja täytebittien paikat. Vastaanottaja on kuitannut
kehyksen vetämällä ACK-paikan dominantiksi.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/can-kehys.json" otsikko="Datakehys 0x123, data 00 ff, yhteensä 65 bittiä. S = SOF, R = RTR, I = IDE, r = r0, e = erotin, A = ACK-paikka. Alin rivi on ylhäällä täytebitin kohdalla: jokainen seuraa viittä samanarvoista bittiä."}
```

Datatavut `0x00` ja `0xFF` pakottavat täytebittejä: täytetty kehys on
viisi bittiä pidempi. Jokainen yksittäinen bittivirhe jää kiinni.
Kääntynyt databitti rikkoo CRC:n, kääntynyt bitti DLC:n kohdalla
muuttaa kehyksen pituuden, ja kääntynyt bitti viiden samanarvoisen
jonossa tuottaa kuuden samanlaisen jonon. Yksikkötesti
`test_yksittainen_bittivirhe_havaitaan` käy läpi kehyksen jokaisen
bitin.

## Kuittaus ja virheet

Lähettäjä lähettää ACK-paikassa resessiivisen bitin, ja jokainen
vastaanottaja, jonka mielestä kehys oli ehjä, vetää sen dominantiksi.
Kuittaus kertoo siis vain, että ainakin yksi solmu sai kehyksen ehjänä,
ei sitä, että oikea solmu sai sen. Jos ACK-paikka jää resessiiviseksi,
lähettäjä tulkitsee sen ACK-virheeksi. Yleinen syy on väylä, jolla
lähettäjä on ainoa solmu.

Solmu havaitsee viisi virhetyyppiä: bittivirheen (lähetti yhtä mutta
näki toista arbitraatiokentän ulkopuolella), täytevirheen, CRC-virheen,
muotovirheen (kiinteän bitin paikalla väärä arvo) ja ACK-virheen. Se,
joka havaitsee virheen, lähettää heti *virhekehyksen*: kuusi dominanttia
bittiä. Ne rikkovat täyttösäännön, joten kaikki muutkin solmut hylkäävät
kehyksen. Lähettäjä lähettää kehyksen myöhemmin uudelleen
automaattisesti. Väylällä jokainen kehys on siis joko kaikilla ehjänä
tai ei kenelläkään.

## Arbitraatio

Kun väylä vapautuu, solmut voivat aloittaa yhtä aikaa. Kukin lähettää
SOF:n ja tunnisteensa ja lukee samalla väylää. Solmu, joka lähettää
resessiivisen bitin mutta näkee dominantin, lopettaa ja jää
kuuntelemaan. Pienempi tunniste voittaa, eikä voittajan kehyksestä
häviä bittiäkään. Malli `arbitraatio` laskee väylän tason bitti
kerrallaan lähettäjien minimistä ja poistaa lähettäjän, jonka bitti
poikkeaa väylästä.

```{.python tiedosto="esimerkit/python/can_arbitraatio.py" osa="arbitraatio"}
```

```{.tuloste tiedosto="esimerkit/python/can_arbitraatio.odotettu"}
```

Tunniste `0x65A` luopuu jo ensimmäisellä tunnistebitillä. `0x12F` ja
`0x123` kulkevat rinnakkain kahdeksan bittiä, ja ensimmäinen ero
ratkaisee. Alla oleva kuva näyttää saman arbitraation aaltoina:
hävinnyt solmu jättää lähtönsä resessiiviseksi (1) ja jää
kuuntelemaan, eikä väylän tila muutu sen takia lainkaan.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/can-arbitraatio.json" otsikko="Kolmen solmun arbitraatio: väylä on johdotettu JA"}
```
 Arbitraatiosta seuraa kaksi suunnittelusääntöä. Ensinnäkin
kahden solmun ei pidä koskaan lähettää samaa tunnistetta: ne
etenisivät rinnakkain arbitraation ohi, ja ero datassa olisi
bittivirhe (malli nostaa siitä virheen). Toiseksi tunniste on
prioriteetti. Kiireelliset viestit saavat pienet tunnisteet, ja
väylän kuormaa on seurattava: jos väylä on jatkuvasti varattu, suuret
tunnisteet eivät pääse koskaan lähetysvuoroon. Sama koskee ohjaimen
sisäistä jonoa. Jos ohjain lähettää puskurinsa saapumisjärjestyksessä
eikä tunnisteen mukaan, kiireellinen viesti voi jäädä odottamaan
vähemmän tärkeää.

## Vikojen rajaus

Viallinen solmu ei saa kaataa koko väylää jatkuvilla virhekehyksillä.
Jokaisella solmulla on lähetys- ja vastaanottovirhelaskuri (TEC ja
REC). Virhe kasvattaa laskuria enemmän kuin onnistuminen pienentää
sitä, joten satunnainen virhe ei haittaa, mutta toistuva virhe kasvattaa
laskuria.

```{.python tiedosto="esimerkit/python/mallit/can.py" osa="laskurit"}
```

| Tila | Ehto | Käytös |
|---------------|----------------------|------------------------------------|
| error active | TEC < 128 ja REC < 128 | normaali; virheestä aktiivinen virhekehys (6 dominanttia) |
| error passive | TEC tai REC ≥ 128 | virheestä passiivinen virhekehys (6 resessiivistä), lisätauko ennen uutta lähetystä |
| bus-off | TEC > 255 | ei lähetä mitään; paluu vasta 128 × 11 resessiivisen bitin jälkeen |

```{.python tiedosto="esimerkit/python/can_virheet.py" osa="rikki"}
```

```{.python tiedosto="esimerkit/python/can_virheet.py" osa="satunnainen"}
```

```{.tuloste tiedosto="esimerkit/python/can_virheet.odotettu"}
```

Rikkinäinen lähetin siirtyy passiiviseksi kuudennellatoista ja irtoaa
väylästä 32. yrityksellä, ja muut solmut jatkavat. Virhesuhde 1:8 on
raja: sitä tiheämmät virheet ajavat solmun lopulta väylältä, harvemmat
eivät. Ohjelman on seurattava ohjaimen tilaa. Bus-off on raportoitava ja
paluu hallittava: jatkuva automaattinen paluu voi pitää rikkinäisen
solmun väylää häiritsevänä.

## Bitin ajoitus

CAN-ohjaimen nopeus asetetaan aikakvantteina (TQ). Esijakaja (BRP)
jakaa ohjaimen kellon kvantiksi, ja bitti koostuu tahdistussegmentistä
(1 TQ), segmentistä TSEG1 (etenemisviive ja vaihesegmentti 1) ja
segmentistä TSEG2. Näyte otetaan TSEG1:n lopussa. Myöhäinen näytepiste
antaa signaalille aikaa kulkea väylän päästä päähän ja tasaantua,
mutta jättää vähemmän aikaa tahdistukselle. CiA (CAN in Automation)
suosittelee noin 87,5 %:n näytepistettä.

```{.python tiedosto="esimerkit/python/can_ajoitus.py" osa="ajoitus"}
```

```{.tuloste tiedosto="esimerkit/python/can_ajoitus.odotettu"}
```

Tulosteen ensimmäinen rivi kuvana: kahdeksan kvanttia bittiä kohti,
ja arvo luetaan TSEG1:n ja TSEG2:n rajalla.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/can-bitti.json" otsikko="Kaksi bittiä aikakvantteina (8 MHz, 1 Mbit/s). Solmu tahdistuu reunaan SYNC-segmentissä ja lukee väylän TSEG1:n lopussa, tässä kohdassa 6/8 = 75 %."}
```

8 MHz:n kello riittää 1 Mbit/s:iin vain kahdeksalla kvantilla bittiä
kohti, ja koska TSEG2 vaatii vähintään kaksi kvanttia, näytepiste jää
75 %:iin. Siksi CAN-laitteissa käytetään yleensä 16, 20, 40 tai 80 MHz:n
ohjainkelloa. Kaikkien solmujen on käytettävä samaa nopeutta ja
lähelle samaa näytepistettä. Väylän pituus rajoittaa nopeutta, koska
signaalin on ehdittävä väylän päästä päähän ja takaisin ennen
näytepistettä. Nyrkkisääntö on noin 40 m 1 Mbit/s:n nopeudella,
100 m 500 kbit/s:n ja 500 m 125 kbit/s:n nopeudella.

## Pitkä viesti: ISO-TP

Kahdeksan tavun raja on liian pieni esimerkiksi diagnostiikalle ja
ohjelmistopäivityksille. Ylemmät protokollat ratkaisevat tämän
pilkkomalla viestin. Autojen diagnostiikan kuljetuskerros ISO-TP
(ISO 15765-2) käyttää datakentän ensimmäistä tavua kehyksen lajin ja
järjestyksen kertomiseen:

```{.python tiedosto="esimerkit/python/can_isotp.py" osa="pilko"}
```

```{.python tiedosto="esimerkit/python/can_isotp.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/python/can_isotp.odotettu"}
```

Ensimmäinen kehys kertoo koko viestin pituuden (`0x014` = 20) ja vie
kuusi tavua. Vastaanottaja vastaa vuonohjauskehyksellä, jolla se voi
myös hidastaa lähettäjää, ja loput tulevat numeroituina
jatkokehyksinä. Järjestysnumero paljastaa kadonneen kehyksen, mutta
uudelleenlähetys on sovelluksen asia: koko viesti lähetetään uudelleen.
Kahdenkymmenen tavun siirto vei väylällä 411 bittiä, joista 160 on
hyötykuormaa. CANopen ja J1939 pilkkovat pitkät viestit samalla
periaatteella mutta omilla kehysmuodoillaan.

## CAN FD ja CAN XL

CAN FD (Flexible Data-rate) säilyttää arbitraation ennallaan mutta
vaihtaa datavaiheessa suurempaan nopeuteen (BRS-bitti), tyypillisesti
2–8 Mbit/s:iin, ja sallii enintään 64 tavua dataa. CRC on 17- tai
21-bittinen, ja täytebittien määrä lasketaan mukaan tarkistukseen.
CAN XL nostaa datan 2048 tavuun ja nopeuden yli 10 Mbit/s:iin. Klassinen
CAN-ohjain tulkitsee FD-kehyksen virheeksi, joten FD- ja klassisia
solmuja ei voi sekoittaa samalla väylällä ilman suunnittelua.

## Käytännössä

- **Päätä väylä kummastakin päästä 120 Ω:lla**, ja mittaa
  sammutetun väylän resistanssi: noin 60 Ω on oikein.
- **Suunnittele tunnisteet prioriteetteina** ja laske väylän kuorma
  pahimmassa tilanteessa. Pidä kuorma selvästi alle 100 %:n, jotta
  suurimmatkin tunnisteet pääsevät läpi.
- **Älä anna kahden solmun lähettää samaa tunnistetta.**
- **Valitse kello, joka jakautuu nopeudeksi** noin 87,5 %:n
  näytepisteellä, ja käytä samaa ajoitusta kaikissa solmuissa.
- **Seuraa ohjaimen virhelaskureita ja tilaa**, raportoi
  error passive ja bus-off, ja hallitse paluu väylälle.
- **Käytä hyväksyntäsuodattimia** äläkä suodata ohjelmassa jokaista
  kehystä.

## Itsearviointi

- Osaat selittää dominantin ja resessiivisen tason ja sen, miten
  arbitraatio ratkaisee yhtäaikaisen lähetyksen hukkaamatta bittejä.
- Osaat muodostaa CAN-kehyksen kentät, lisätä täytebitit ja
  selittää, miksi täyttö tarvitaan.
- Osaat nimetä CAN:n viisi virhetyyppiä ja kertoa, miten virhekehys
  takaa, että kaikki hylkäävät virheellisen kehyksen.
- Osaat kuvata virhelaskurien säännöt ja solmun tilat ja laskea,
  milloin rikkinäinen solmu irtoaa väylästä.
- Osaat laskea bitin ajoituksen annetulle kellolle ja nopeudelle ja
  perustella näytepisteen valinnan.
- Osaat selittää, miten kahdeksaa tavua pidempi viesti pilkotaan
  kehyksiksi ja mitä vuonohjauskehys ja järjestysnumero tekevät.
