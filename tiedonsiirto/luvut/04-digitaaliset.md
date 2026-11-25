# Digitaaliset modulaatiot

Digitaalinen modulaatio valitsee joka symbolijaksolla yhden äärellisen
joukon aaltomuodoista. Kantataajuudella aaltomuoto on pulssi kerrottuna
kompleksiluvulla, joten modulaatio on luettelo kompleksilukuja, joiden
joukosta symboli valitaan: **konstellaatio**. Jos pisteitä on $M$,
kukin symboli kuljettaa $k = \log_2 M$ bittiä. Tämä luku rakentaa
yleisimmät konstellaatiot, näyttää miksi bittien järjestyksellä on
väliä ja esittelee taajuusmodulaation digitaaliset muodot.

## PSK ja QAM

**PSK** (*phase shift keying*) sijoittaa pisteet tasavälein
yksikköympyrälle: BPSK kahteen, QPSK neljään ja 8-PSK kahdeksaan
pisteeseen. Amplitudi on vakio, mikä sopii epälineaarisille
vahvistimille. **QAM** (*quadrature amplitude modulation*) sijoittaa
pisteet neliöhilaan, jossa I- ja Q-akseli ovat itsenäisiä
pulssiamplitudimodulaatioita. QAM käyttää tason tehokkaammin kuin PSK,
kun pisteitä on paljon.

Bittien sijoittelu pisteisiin tehdään **Gray-koodilla**: naapuripisteiden
bittinimiöt eroavat vain yhdessä bitissä. Neliö-QAM:ssä Gray-koodataan
kumpikin akseli erikseen.

```{.python tiedosto="esimerkit/04-konstellaatiot.py" osa="rakenna"}
```

Konstellaation tärkeimmät tunnusluvut ovat pisteiden pienin etäisyys
$d_\text{min}$ keskienergialla 1, koska se määrää virhetodennäköisyyden
suurella signaali-kohinasuhteella, ja huipun ja keskitehon suhde, koska
se määrää, kuinka paljon tehovahvistimelta vaaditaan varaa.

```{.python tiedosto="esimerkit/04-konstellaatiot.py" osa="tunnusluvut"}
```

```{.python tiedosto="esimerkit/04-konstellaatiot.py" osa="kartta"}
```

```{.tuloste tiedosto="esimerkit/04-konstellaatiot.odotettu"}
```

Etäisyys pienenee nopeasti, kun bittejä lisätään: 64-QAM:n pisteet ovat
4,6 kertaa lähempänä toisiaan kuin QPSK:n, joten se tarvitsee noin
$20\log_{10} 4{,}6 \approx 13$ dB enemmän signaali-kohinasuhdetta
samaan symbolivirheeseen. Kaksi bittiä lisää symbolia kohti maksaa
noin 6 dB, mikä on tiedonsiirron perusvaihtokauppa kaistan ja tehon
välillä. Kehä on huono tapa pakata pisteitä: 8-PSK:n pienin etäisyys
on vain vähän 16-QAM:n etäisyyttä suurempi, vaikka 8-PSK kuljettaa
bitin vähemmän, ja 16-PSK:n etäisyys (0,390) on jo selvästi 16-QAM:n
etäisyyttä (0,632) pienempi samalla bittimäärällä.

![Konstellaatiot Gray-nimiöineen keskienergialla 1. Oranssi jana on
pienin etäisyys $d_\text{min}$: samalla 16 pisteellä neliöhila pitää
pisteet kauempana toisistaan kuin kehä. Taidon *Tietoliikennetekniikka*
konstellaatiokuvat näyttävät samat pisteet
kohinassa.](kuvat/konstellaatiot.png){width=100%}

## Gray-koodauksen merkitys

Kohina siirtää vastaanotetun pisteen useimmiten naapuripisteen alueelle.
Gray-koodauksella tällainen symbolivirhe maksaa yhden bitin. Tavallisella
binäärijärjestyksellä naapureiden nimiöt voivat erota useammassa
bitissä, esimerkiksi 01 ja 10.

```{.python tiedosto="esimerkit/04-gray.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/04-gray.odotettu"}
```

Symbolivirheitä on täsmälleen yhtä paljon, koska pisteet ja kohina ovat
samat. Gray-koodauksella bittivirheitä on 1,01 symbolivirhettä kohti,
binäärijärjestyksellä 1,34, joten bittivirhesuhde on kolmanneksen
suurempi. Gray-koodatun $M$-QAM:n bittivirhesuhde on siksi hyvällä
tarkkuudella symbolivirhesuhde jaettuna bittien määrällä, mikä
yksinkertaistaa luvun 6 kaavoja.

## FSK ja MSK

**FSK** (*frequency shift keying*) valitsee symbolille taajuuden.
Kaksi taajuutta ovat erotettavissa toisistaan parhaiten, kun ne ovat
**ortogonaaliset**: niiden korrelaatio symbolin aikana on nolla.
Koherentissa ilmaisussa (vaihe tunnetaan) riittää ero $\Delta f =
1/(2T)$, epäkoherentissa (vaihe tuntematon, ilmaistaan energialla)
tarvitaan $\Delta f = 1/T$.

```{.python tiedosto="esimerkit/04-fsk.py" osa="ortogonaalisuus"}
```

Jos FSK tehdään kytkemällä kahden erillisen oskillaattorin välillä,
vaihe hyppää symbolien rajalla, ja hyppy levittää spektriä. **CPFSK**
(*continuous phase FSK*) jatkaa vaihetta saumattomasti.
Pienimmällä ortogonaalisella erolla $\Delta f T = 1/2$ se on **MSK**
(*minimum shift keying*), ja Gaussin suotimella pehmennettynä
**GMSK**, jota käytettiin GSM:ssä. Bluetooth käyttää samaa periaatetta
pienemmällä modulaatioindeksillä (GFSK, $\Delta f T \approx 0{,}32$).

```{.python tiedosto="esimerkit/04-fsk.py" osa="vaihe"}
```

```{.tuloste tiedosto="esimerkit/04-fsk.odotettu"}
```

Jatkuvalla vaiheella kaistan ulkopuolelle vuotava teho on 16–22 dB
pienempi. FSK:n vahvuudet ovat vakioamplitudi ja yksinkertainen,
epäkoherenttikin vastaanotin. Heikkoutena on huono spektritehokkuus:
binäärinen FSK kuljettaa yhden bitin symbolia kohti ja vie enemmän
kaistaa kuin BPSK.

## Käytännössä

- **Valitse konstellaatio linkin laadun mukaan.** Nykyiset
  järjestelmät (WLAN, LTE, 5G, DVB-S2) vaihtavat modulaatiota ja
  koodinopeutta mitatun signaali-kohinasuhteen mukaan: huonolla
  yhteydellä QPSK, hyvällä 256- tai 1024-QAM. Tätä kutsutaan
  **linkkiadaptaatioksi**.
- **Käytä Gray-koodausta.** Se on maksuton parannus, ja kaikki
  standardit käyttävät sitä. Tarkista nimiöinti automaattisesti
  naapuritestillä niin kuin esimerkissä.
- **Normita konstellaatio.** Keskienergia 1 tekee kohinan
  kalibroinnista yksiselitteistä (luku 6). Normittamaton 16-QAM
  (energia 10) on yleinen 10 dB:n virhe.
- **Huomioi huipputeho.** QAM:n ja erityisesti OFDM:n (luku 10)
  huiput vaativat tehovahvistimelta varaa (*back-off*), mikä huonontaa
  hyötysuhdetta. Siksi akkukäyttöiset ja satelliittilaitteet suosivat
  vakioamplitudisia modulaatioita, kuten MSK:ta, GMSK:ta ja PSK:ta.

## Itsearviointi

- Osaat rakentaa M-PSK- ja neliö-QAM-konstellaation Gray-nimiöinnillä
  ja normittaa sen keskienergiaan 1.
- Osaat laskea konstellaation pienimmän etäisyyden sekä huippu- ja
  keskitehon suhteen ja arvioida niistä modulaatioiden eroja.
- Osaat selittää, miksi Gray-koodaus pienentää bittivirhesuhdetta,
  vaikka symbolivirheiden määrä ei muutu.
- Osaat selittää FSK:n ortogonaalisuusehdon sekä jatkuvan vaiheen ja
  MSK:n edun.
