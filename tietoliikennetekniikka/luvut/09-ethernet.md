# Ethernet

Ethernet on edellisten lukujen ideoiden kokoelma: linjakoodaus,
CRC, kanavanvaraus ja kehystys. Se on kasvanut 10 megabitistä
800 gigabittiin säilyttäen saman kehysmuodon, minkä vuoksi
kerran kirjoitettu verkkokoodi toimii yhä. Tämä luku katsoo Ethernetiä
fyysisen kerroksen ja kehyksen mitoituksen kannalta. Kehyksen kentät,
osoitteet ja kytkimen toiminta kuuluvat taitoon *Tietoverkot* ja
VLANit ja kytkentäverkon suunnittelu taitoon *Verkkoinfrastruktuuri*.

## Nopeudet ja fyysiset kerrokset

| Standardi | Nopeus | Siirtotie | Koodaus |
|-----------|--------|-----------|---------|
| 10BASE-T | 10 Mbit/s | 2 paria, 100 m | Manchester |
| 100BASE-TX | 100 Mbit/s | 2 paria, 100 m | 4B5B, MLT-3 |
| 1000BASE-T | 1 Gbit/s | 4 paria, 100 m | PAM5, 4 paria rinnakkain |
| 10GBASE-T | 10 Gbit/s | 4 paria, 100 m (Cat 6A) | PAM16, LDPC |
| 10GBASE-SR/LR | 10 Gbit/s | moni-/yksimuotokuitu | 64b/66b |
| 100GBASE-LR4 | 100 Gbit/s | yksimuotokuitu | 4 aallonpituutta |
| 400GBASE-DR4 | 400 Gbit/s | 4 yksimuotokuituparia | PAM4, FEC |

Standardin nimi kertoo rakenteen: nopeus, kantataajuuksinen siirto
(BASE) ja siirtotie (T = kierretty pari, S/L = lyhyen tai pitkän
matkan kuitu). Nopeat versiot yhdistävät useita rinnakkaisia kaistoja
(pareja, kuituja tai aallonpituuksia), ja niiden linkit vaativat
virheenkorjauksen.

## Kehys ja tehokkuus

Ethernet-kehyksessä on tahdisteosa, kohde- ja lähdeosoite, tyyppikenttä,
46–1500 tavun hyötykuorma ja CRC-32. Kehysten väliin jätetään 12 tavun
tauko. Yleiskustannus on kiinteä, joten pienet kehykset ovat
tehottomia:

```{.python tiedosto="esimerkit/09-kehystehokkuus.py" osa="kehys"}
```

```{.tuloste tiedosto="esimerkit/09-kehystehokkuus.odotettu"}
```

Pienimmillä kehyksillä kymmenen gigabitin linkki välittää lähes
15 miljoonaa kehystä sekunnissa. Laitteen on siis käsiteltävä kehys
67 nanosekunnissa. Siksi kytkimen ja ohjelmallisen reitittimen
suorituskyky ilmoitetaan kehyksinä sekunnissa eikä bitteinä. Suuret
kehykset (*jumbo frames*, 9000 tavua) parantavat tehokkuutta vain
vähän, mutta vähentävät käsiteltävien kehysten määrää kuudesosaan.

## Miksi kehys on vähintään 64 tavua

Kehyksen vähimmäiskoko on perintöä jaetun väylän ajalta. CSMA/CD toimii
vain, jos lähettäjä huomaa törmäyksen vielä lähettäessään. Kehyksen
lähettämisen on siis kestettävä vähintään signaalin edestakainen matka
verkon kauimpaan pisteeseen. Standardi kiinnitti aikaviipaleeksi
512 bittiä (64 tavua), mikä rajaa verkon halkaisijan:

```{.python tiedosto="esimerkit/09-minimikehys.py" osa="slotti"}
```

```{.tuloste tiedosto="esimerkit/09-minimikehys.odotettu"}
```

Todelliset rajat ovat teoreettisia pienempiä, koska toistimet,
lähetin-vastaanottimet ja törmäyksestä ilmoittava häirintäsignaali
vievät osan budjetista. Gigabitin nopeudella sama viipale olisi
rajannut verkon 50 metriin, joten puolidupleksi-gigabitti venytti
viipaleen 4096 bittiin (*carrier extension*). Käytännössä
puolidupleksia ei enää käytetä: kytketty, täysdupleksinen Ethernet
ei törmää, mutta vähimmäiskoko on säilynyt yhteensopivuuden vuoksi.

## Automaattinen neuvottelu

Kun kaapeli kytketään, laitteet kertovat toisilleen tukemansa tilat
pulsseilla, joita ei sekoita dataan, ja valitsevat parhaan yhteisen
tilan sovitulla prioriteettijärjestyksellä:

```{.python tiedosto="esimerkit/09-autoneg.py" osa="neuvottelu"}
```

```{.python tiedosto="esimerkit/09-autoneg.py" osa="duplex"}
```

```{.tuloste tiedosto="esimerkit/09-autoneg.odotettu"}
```

Klassinen vika syntyy, kun toinen pää on asetettu kiinteästi ja toinen
neuvottelee. Neuvotteleva pää päättelee nopeuden signaalista mutta
olettaa puolidupleksin. Yhteys toimii pienellä kuormalla mutta
tuottaa myöhäisiä törmäyksiä ja CRC-virheitä kuormassa – vaikeasti
löydettävä vika, joka näkyy kytkimen virhelaskureista.

## Käytännössä

- **Anna molempien päiden neuvotella.** Kiinteät asetukset kuuluvat
  vain erikoistapauksiin, ja silloin molempiin päihin.
- **Seuraa virhelaskureita.** CRC-virheet, myöhäiset törmäykset ja
  hylätyt kehykset kertovat kaapeli-, liitin- ja dupleksivioista ennen
  kuin käyttäjät valittavat (`ethtool -S`, kytkimen tilastot).
- **Mitoita kehyksinä sekunnissa.** Palomuurin, reitittimen tai
  ohjelmallisen verkkotoiminnon kapasiteetti pienillä paketeilla on
  usein murto-osa ilmoitetusta bittinopeudesta.
- **Valitse kaapeli nopeuden mukaan.** 10GBASE-T vaatii Cat 6A
  -kaapelin 100 metrille; vanhalla Cat 5e:llä 2.5GBASE-T ja 5GBASE-T
  ovat usein realistisempia.

## Itsearviointi

- Osaat tulkita Ethernet-standardin nimen ja kertoa, miten nopeat
  versiot jakavat datan rinnakkaisille kaistoille.
- Osaat laskea kehyksen tehokkuuden ja kehysnopeuden linjanopeudesta.
- Osaat selittää, miksi kehyksen vähimmäiskoko on 64 tavua ja miten se
  liittyy verkon halkaisijaan.
- Osaat selittää automaattisen neuvottelun ja dupleksiristiriidan
  synnyn ja tunnistamisen.
