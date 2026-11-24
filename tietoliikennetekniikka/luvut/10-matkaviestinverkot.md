# Matkaviestinverkot

Matkaviestinverkko jakaa rajallisen radiospektrin miljoonille
liikkuville käyttäjille. Se yhdistää edellisten lukujen menetelmät:
OFDM ja MIMO radiolla, solut ja taajuuksien uudelleenkäyttö tilassa,
resurssiruudukko ajassa ja taajuudessa sekä pakettikytketty runkoverkko.

## Arkkitehtuuri

| Osa | 4G (LTE) | 5G (NR) | Tehtävä |
|-----|----------|---------|---------|
| päätelaite | UE | UE | puhelin, modeemi, IoT-laite |
| radioverkko | eNB | gNB | radio, ajoitus, resurssien jako |
| hallinta | MME | AMF (+ SMF) | kirjautuminen, liikkuvuus, istunnot |
| käyttäjädata | S-GW, P-GW | UPF | pakettien välitys Internetiin |
| tilaajatiedot | HSS | UDM | tunnisteet ja avaimet |

5G:n runkoverkko on rakennettu palveluina, jotka kommunikoivat
HTTP/2-rajapinnoilla, ja ohjaus (AMF, SMF) on erotettu käyttäjädatan
välityksestä (UPF). Erottelu sallii UPF:n sijoittamisen lähelle
käyttäjää viiveen pienentämiseksi.

## Numerologia ja resurssilohkot

NR jakaa radioresurssin ruudukkoon: taajuussuunnassa alikantoaaltoihin
ja aikasuunnassa OFDM-symboleihin. Kaksitoista alikantoaaltoa
muodostaa **resurssilohkon** (RB), ja tukiasema jakaa käyttäjille
lohkoja millisekunnin murto-osien välein. Toisin kuin LTE:ssä,
alikantoaaltojen väli ei ole kiinteä vaan **numerologian** $\mu$
mukainen $15 \cdot 2^\mu$ kHz:

```{.python tiedosto="esimerkit/10-numerologia.py" osa="numerologia"}
```

```{.python tiedosto="esimerkit/10-numerologia.py" osa="kaista"}
```

```{.tuloste tiedosto="esimerkit/10-numerologia.odotettu"}
```

Suurempi väli tarkoittaa lyhyempiä symboleita ja aikavälejä eli
pienempää viivettä ja parempaa Doppler-ilmiön sietoa, mutta lyhyempi symboli
sietää vähemmän monitieviivettä. Tavallinen matalien taajuuksien kanava
käyttää 15 tai 30 kHz:n väliä, millimetriaallot 120 kHz:n väliä.
Kanavan reunoille jätetään suojakaistaa, joten lohkot kattavat
92–98 % kaistasta.

## Huippunopeus

3GPP:n määrittelemä huippunopeus kertoo tasan, mistä nopeus syntyy:
MIMO-kerrokset × bittiä symbolissa × koodisuhde × alikantoaallot ×
symbolinopeus × (1 − yleiskustannus).

```{.python tiedosto="esimerkit/10-huippunopeus.py" osa="kaava"}
```

```{.python tiedosto="esimerkit/10-huippunopeus.py" osa="esimerkit"}
```

```{.tuloste tiedosto="esimerkit/10-huippunopeus.odotettu"}
```

Mainosten 2 Gbit/s edellyttää 100 MHz:n kaistaa, neljää
MIMO-kerrosta ja 256-QAM:ia, eli erinomaista signaalia lähellä
tukiasemaa. Huippunopeus on lisäksi koko solun kapasiteetti, joka
jaetaan aktiivisten käyttäjien kesken.

## Solut ja uudelleenkäyttö

Spektriä ei riitä jokaiselle käyttäjälle erikseen, joten sama taajuus
käytetään uudelleen toisissa soluissa. Solun keskellä signaali on
vahva, mutta reunalla naapurisolujen samaa taajuutta käyttävät
asemat häiritsevät. Uudelleenkäyttökerroin $N$ kertoo, kuinka moneen
osaan taajuudet jaetaan, jotta samaa taajuutta käyttävät solut olisivat
kauempana toisistaan:

```{.python tiedosto="esimerkit/10-solut.py" osa="kuusikulmio"}
```

```{.python tiedosto="esimerkit/10-solut.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/10-solut.odotettu"}
```

Kerroin 1 antaa keskellä solua suurimman nopeuden, mutta reunalla SINR
on negatiivinen. Kerroin 7 parantaa reunaa mutta jakaa kaistan
seitsemään osaan. GSM käytti kiinteää uudelleenkäyttöä, kun taas LTE
ja NR käyttävät kerrointa 1 ja hallitsevat reunan häiriöitä ajoituksella
(häiriöiden koordinointi, tehonsäätö) ja säteenmuodostuksella. Solujen
pienentäminen on tehokkain tapa lisätä kapasiteettia: sama spektri
käytetään useammin samalla alueella.

## Käytännössä

- **Erota huippu- ja käyttäjänopeus.** Kapasiteettisuunnittelussa
  tärkeintä on solun keskimääräinen spektritehokkuus (bit/s/Hz) ja
  reunan käyttäjien kokemus, ei huippunopeus.
- **Viive syntyy muualtakin kuin radiosta.** Ajoituspyynnöt, runkoverkko
  ja palvelimen sijainti kasvattavat viivettä; 5G:n lyhyet aikavälit
  auttavat vain radio-osuudessa.
- **Sovelluksen kannattaa sietää vaihtelua.** Matkaviestinyhteyden
  nopeus ja viive muuttuvat sekunneissa, kun käyttäjä liikkuu;
  mukautuva bittinopeus ja aikakatkaisut kuuluvat mobiilisovelluksiin
  (taito *Android-sovellukset*).
- **IoT-laitteelle eri radio.** NB-IoT ja LTE-M uhraavat nopeuden
  kantaman ja virrankulutuksen hyväksi (luku Kanavan kapasiteetti).

## Itsearviointi

- Osaat nimetä 4G- ja 5G-verkon pääosat ja niiden tehtävät.
- Osaat laskea NR:n alikantoaaltovälin, aikavälin ja resurssilohkon
  leveyden numerologiasta.
- Osaat laskea huippunopeuden kerrosten, modulaation, kaistan ja
  yleiskustannuksen avulla.
- Osaat selittää taajuuksien uudelleenkäytön hyödyn ja hinnan solun
  keskellä ja reunalla.
