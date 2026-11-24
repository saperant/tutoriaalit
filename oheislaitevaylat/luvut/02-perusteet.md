# Väylien perusteet

Sarjaväylä siirtää bitit peräkkäin yhtä johdinta pitkin. Rinnakkaisväylä
olisi bittiä kohden nopeampi, mutta piirien välillä johtimet, nastat ja
piirilevyn pinta-ala maksavat. Lisäksi rinnakkaisten johtimien
ajoituserot rajoittavat nopeutta. Siksi lähes kaikki piirien väliset
väylät ovat nykyään sarjamuotoisia, piirilevyn sisäisistä
anturiväylistä PCI Expressiin ja USB:hen asti. Tässä luvussa käydään
läpi käsitteet, joiden varassa luvun 3–6 väylät eroavat toisistaan.

## Kello: synkroninen ja asynkroninen

Vastaanottimen on tiedettävä, milloin linjaa luetaan. *Synkronisessa*
väylässä kello kulkee omaa johdintaan, ja data luetaan sen reunalla.
SPI ja I2C ovat synkronisia: isäntä tuottaa kellon, ja nopeus voi
vaihdella vapaasti, jopa kesken siirron. Laite seuraa kelloa eikä
tarvitse omaa tarkkaa aikaperustaa.

*Asynkronisessa* väylässä kelloa ei siirretä. Lähetin ja vastaanotin
sopivat nopeudesta etukäteen, ja vastaanotin tahdistuu signaalin
reunoihin. UART tahdistuu jokaisen tavun alussa START-bitin reunaan,
joten kellojen ero ehtii kertyä vain yhden kehyksen ajan. CAN tahdistuu
jokaiseen resessiivisestä dominanttiin vaihtuvaan reunaan, ja
bittitäyttö takaa, että reunoja tulee riittävän usein (luku 6).
Nopeat väylät, kuten USB ja PCI Express, palauttavat kellon datasta
koodauksella, joka takaa riittävän reunatiheyden.

| Ominaisuus | Synkroninen | Asynkroninen |
|------------|-------------|--------------|
| Johtimia | data ja kello | vain data |
| Nopeus | isäntä päättää, vaihtelu sallittu | sovittu, sallittu virhe muutamia prosentteja |
| Vastaanottimen kello | ei tarvita | tarvitaan, ylinäytteistys |
| Esimerkkejä | SPI, I2C, I2S | UART, CAN, RS-485 |

## Topologia ja suunta

*Pisteestä pisteeseen* -yhteydessä on kaksi osapuolta, kuten UARTissa.
*Monipisteväylällä* samat johtimet jakaa useampi laite, ja jokaisella
on osoite tai tunniste (I2C, CAN, RS-485). SPI on välimuoto: data- ja
kellojohtimet ovat yhteiset, mutta jokaisella laitteella on oma
piirinvalintajohtimensa (CS), joten isäntä valitsee laitteen
sähköisesti eikä osoitteella.

Suunnan mukaan väylä on *simplex* (vain yhteen suuntaan),
*half-duplex* (molempiin, mutta vuorotellen samoja johtimia pitkin,
kuten I2C, CAN ja kaksijohtiminen RS-485) tai *full-duplex*
(molempiin yhtä aikaa omia johtimia pitkin, kuten UART ja SPI).
Half-duplex-väylällä joku päättää, kuka lähettää. I2C:ssä vuoro on
isännällä, ja CANissa ristiriidan ratkaisee arbitraatio.

## Lähtöasteet: push-pull ja avokollektori

Tavallinen digitaalilähtö on *push-pull*: se kytkee linjan aktiivisesti
joko käyttöjännitteeseen tai maahan. Jos kaksi push-pull-lähtöä
yhdistetään ja toinen ajaa ykköstä ja toinen nollaa, syntyy oikosulku.
Siksi push-pull-linjalla saa olla vain yksi ajaja kerrallaan (UARTin
TX, SPI:n kello ja MOSI).

*Avokollektori-* tai *avonielulähtö* (open collector, open drain) osaa
vain vetää linjan alas tai päästää sen irti. Ylätason tuottaa
vetovastus. Kun monta tällaista lähtöä on samassa johtimessa, linja on
ylhäällä vain, jos kaikki päästävät sen. Tämä on *johdotettu JA*
(wired-AND):

```{.python tiedosto="esimerkit/python/avokollektori.py" osa="ja"}
```

```{.tuloste tiedosto="esimerkit/python/avokollektori.odotettu"}
```

Johdotettu JA tekee monen isännän väylistä turvallisia. Kun yksi vetää
alas ja toinen päästää irti, kumpikaan ei vahingoitu, ja kumpikin voi
lukea linjalta todellisen tilan ja huomata ristiriidan. I2C:n
arbitraatio ja kellonvenytys sekä CANin dominantti ja resessiivinen
taso perustuvat tähän. Hinta on nopeus. Laskeva reuna on nopea, koska
transistori purkaa linjan kapasitanssin, mutta nouseva reuna on
RC-käyrä, jonka vetovastus ja linjan kapasitanssi määräävät.

### Vetovastuksen mitoitus

Vetovastukselle on kaksi rajaa. Pienin arvo tulee alatasosta: kun
lähtö vetää linjaa alas, vastuksen kautta kulkeva virta ei saa ylittää
lähdön nieluvirtaa $I_{OL}$, jolla alataso pysyy alle rajan $V_{OL}$.
Suurin arvo tulee nousuajasta: I2C-määrittely rajaa ajan, jossa linja
nousee 30 prosentista 70 prosenttiin käyttöjännitteestä. RC-piirissä
se kestää $\ln(0{,}7/0{,}3) \cdot RC \approx 0{,}847\,RC$:

$$R_{min} = \frac{V_{DD} - V_{OL}}{I_{OL}}, \qquad
R_{max} = \frac{t_r}{0{,}847 \cdot C_b}$$

```{.python tiedosto="esimerkit/python/avokollektori.py" osa="mitoitus"}
```

Tuloste on edellisen tulosteen lopussa: pitkällä väylällä (suuri
$C_b$) ja suurella nopeudella sallittu väli kapenee, ja Fast-moodin
400 pF:n väylälle sitä ei 3 mA:n lähdöillä ole lainkaan. Ratkaisuja
ovat lyhyempi väylä, vahvemmat lähdöt (Fast-mode Plus sallii 20 mA),
väylän jakaminen puskuripiirillä tai aktiivinen vetopiiri, joka
nostaa linjaa vastusta nopeammin. Mikrokontrollerin sisäiset
vetovastukset (tyypillisesti 20–50 kΩ) kelpaavat vain hitaalle ja
lyhyelle väylälle.

## Jännitetasot

Logiikkatasot riippuvat käyttöjännitteestä. 3,3 V:n CMOS-piiri
tulkitsee tyypillisesti alle 0,3 $V_{DD}$:n nollaksi ja yli
0,7 $V_{DD}$:n ykköseksi. Väli on kielletty: sen läpi kulkevan
signaalin tulkinta on satunnainen. Kun eri jännitteillä toimivia
piirejä yhdistetään, tarvitaan tasonmuunnin. Avokollektoriväylä on
tässä helppo: kummallakin puolella on oma vetovastuksensa omaan
jännitteeseensä, ja välissä on kaksisuuntainen MOSFET-muunnin. 5 V:n
signaali suoraan 3,3 V:n tuloon kuormittaa suojadiodeja, jos tulo ei
ole datalehden mukaan *5 V tolerant*.

Pitkillä matkoilla jännitetasoja muutetaan kestävämmiksi:

- **RS-232** käyttää ±3…15 V:n jännitettä ja käänteistä logiikkaa:
  negatiivinen jännite on looginen 1. Mikrokontrollerin UART kytketään
  siihen muunninpiirin kautta (esim. MAX232-tyyppinen). Matka on
  kymmeniä metrejä.
- **Differentiaalinen** siirto (RS-485, CAN, LVDS) lähettää signaalin
  kahta johdinta pitkin vastakkaisina. Vastaanotin katsoo vain
  johtimien eroa, joten molempiin johtimiin samalla tavalla tarttuva
  häiriö (yhteismuotoinen häiriö) kumoutuu. RS-485 kulkee yli
  kilometrin, CAN satoja metrejä.

Kun linja on pitkä suhteessa reunan nousuaikaan, se on siirtolinja:
signaali heijastuu johtimen päästä takaisin, ellei pää ole päätetty
linjan ominaisimpedanssilla. RS-485- ja CAN-väylä päätetään
kummastakin päästä 120 Ω:n vastuksella. Yksi päätevastus liian vähän
tai liikaa on yleisin syy väylään, joka toimii pöydällä mutta ei
kentällä. Taito *Tietoliikennetekniikka* käsittelee siirtoteitä
tarkemmin.

## Väylät rinnakkain

| Väylä | Johtimet | Topologia | Osoitus | Tyypillinen nopeus | Virheentarkistus |
|--------|--------------|------------|-----------|--------------------|------------------|
| UART | TX, RX (+RTS, CTS) | pisteestä pisteeseen | ei | 9,6 kbit/s – muutama Mbit/s | pariteetti, ylempi kerros |
| SPI | SCK, MOSI, MISO, CS/laite | isäntä ja laitteet | CS-johdin | 1–100 MHz | ei, ylempi kerros |
| I2C | SCL, SDA | monipiste, monta isäntää | 7 bittiä | 100 kHz – 1 MHz | ACK tavuittain |
| CAN | CANH, CANL | monipiste, kaikki tasavertaisia | 11 tai 29 bitin tunniste | 125 kbit/s – 1 Mbit/s (FD: 5–8) | CRC, ACK, virhelaskurit |
| RS-485 | A, B (+maa) | monipiste | ylempi kerros | 9,6 kbit/s – 10 Mbit/s | ylempi kerros |

Taulukosta näkyy työnjako. SPI on nopein ja yksinkertaisin, mutta se
ei tarkista mitään eikä kulje kauas. I2C säästää johtimia ja nastoja
ja sopii saman piirilevyn hitaille antureille. CAN on rakennettu
häiriöiseen ympäristöön: autoon, työkoneeseen ja teollisuuteen. Sen
laitteisto hoitaa arbitraation, kuittaukset, tarkistukset ja
uudelleenlähetykset. UART ja RS-485 siirtävät tavuja, ja kaikki muu on
protokollan asia (luku 3).

## Käytännössä

- **Valitse väylä etäisyyden, nopeuden ja häiriöympäristön mukaan**, ei
  tottumuksesta. Piirilevyn sisällä SPI ja I2C, laitteiden välillä
  UART tai RS-485, häiriöisessä monen solmun verkossa CAN.
- **Mitoita vetovastukset ja tarkista nousuaika mittaamalla.**
  Oskilloskoopin kuva reunasta kertoo enemmän kuin laskelma, koska
  väylän kapasitanssi on aina arvioitua suurempi.
- **Tarkista tasot ja 5 V:n sietokyky datalehdestä**, ja suunnittele
  tasonmuunnos, kun käyttöjännitteet eroavat.
- **Päätä pitkät differentiaaliväylät molemmista päistä** ja vain
  niistä.
- **Hanki logiikka-analysaattori.** Edullinenkin laite dekoodaa
  UARTin, SPI:n, I2C:n ja CANin, ja suurin osa väylävioista näkyy
  siinä heti.

## Itsearviointi

- Osaat selittää synkronisen ja asynkronisen väylän eron ja kertoa,
  miten vastaanotin kummassakin tietää, milloin bitti luetaan.
- Osaat selittää johdotetun JA:n ja sen, miksi avokollektoriväylällä
  voi olla monta ajajaa mutta push-pull-linjalla vain yksi.
- Osaat laskea vetovastuksen ala- ja ylärajan nousuajasta,
  kapasitanssista ja nieluvirrasta.
- Osaat kertoa, miksi differentiaalinen siirto kestää häiriöitä ja
  miksi pitkä väylä päätetään.
- Osaat valita väylän tehtävään ja perustella valinnan.
