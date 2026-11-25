# Multipleksointi

Siirtotie on kallis, joten sitä jaetaan. Multipleksointi kuljettaa
monta yhteyttä samassa siirtotiessä niin, että vastaanotin osaa erottaa
ne. Yhteydet voidaan erottaa ajan, taajuuden, aallonpituuden tai koodin
perusteella.

## Aika ja taajuus: TDM ja FDM

**Aikajakoinen kanavointi** (TDM) antaa jokaiselle yhteydelle oman
aikavälin toistuvassa kehyksessä. Vanha puhelinverkko kuljetti 30
puhelua 2,048 Mbit/s:n E1-yhteydessä, ja nykyiset kuituverkot (OTN)
jakavat kapasiteettia samalla periaatteella. **Taajuusjakoinen
kanavointi** (FDM) antaa jokaiselle yhteydelle oman taajuusalueen;
radio- ja TV-asemat ovat FDM:ää. Valokuidussa sama periaate on
**aallonpituusjako** (WDM): eri värit kulkevat samassa kuidussa, ja
tiheä WDM kuljettaa kymmeniä 100–800 Gbit/s:n kanavia yhdessä
kuidussa.

![Kolmen käyttäjän A, B ja C jako aika–taajuus-tasossa. TDM jakaa
ajan, FDM taajuuden. OFDMA (luku Matkaviestinverkot) jakaa ruudukon
molempiin suuntiin ja voi muuttaa jakoa tarpeen
mukaan.](kuvat/kanavointi.png){width=100%}

```{.python tiedosto="esimerkit/06-tdm-fdm.py" osa="tdm"}
```

```{.python tiedosto="esimerkit/06-tdm-fdm.py" osa="fdm"}
```

```{.tuloste tiedosto="esimerkit/06-tdm-fdm.odotettu"}
```

FDM-vastaanotin erottaa kanavat, koska eri taajuiset kosinit ovat
**ortogonaalisia**: niiden tulon keskiarvo on nolla, kun tarkastelujakso
on riittävän pitkä. Sama ajatus on OFDM:n ja CDMA:n pohjana.

## OFDM

Nopeassa radiolinkissä symboli on lyhyt, ja monitie-etenemisen
heijastukset saapuvat seuraavan symbolin aikana (symbolien välinen
häiriö). **OFDM** (*orthogonal frequency-division multiplexing*) jakaa
datan satoihin tai tuhansiin hitaisiin alikantoaaltoihin, jotka ovat
taajuudeltaan niin lähekkäin, että ne menevät päällekkäin mutta ovat
silti ortogonaalisia. Lähetin muodostaa ne käänteisellä Fourier-
muunnoksella ja vastaanotin erottaa ne Fourier-muunnoksella.
Jokaisen symbolin eteen kopioidaan sen loppuosa (**syklinen
etuliite**), joka imee heijastukset ja tekee kanavasta jokaiselle
alikantoaallolle yksinkertaisen kertoimen. Vastaanotin korjaa kanavan
jakamalla jokaisen alikantoaallon arvon kanavan kertoimella.

![Vasemmalla viiden vierekkäisen alikantoaallon spektrit: jokaisen
huippu osuu kohtaan, jossa muiden spektri on nolla, joten ne eivät
häiritse toisiaan, vaikka menevät päällekkäin. Oikealla yksi
OFDM-symboli (64 näytettä) ja sen eteen kopioitu 16 näytteen
etuliite.](kuvat/ofdm.png){width=100%}

Esimerkki lähettää QPSK-symboleja 64 alikantoaallolla kanavassa, jossa
on kaksi heijastusta:

```{.python tiedosto="esimerkit/06-ofdm.py" osa="ofdm"}
```

```{.tuloste tiedosto="esimerkit/06-ofdm.odotettu"}
```

Ilman etuliitettä virheitä jää lähes 3 %, vaikka SNR olisi kuinka hyvä:
virheet johtuvat edellisen symbolin vuotamisesta, eivät kohinasta.
Etuliitteen kanssa virheet katoavat, kun kohina pienenee. Etuliite
maksaa 20 % kapasiteetista (16 näytettä 80:stä). OFDM on Wi-Fin, 4G:n,
5G:n, DVB-T:n ja DSL:n perusta. Matkaviestinverkoissa käyttäjät
jaetaan lisäksi alikantoaaltojen ja aikavälien ruudukkoon (OFDMA,
luku Matkaviestinverkot).

## CDMA

**Koodijakoinen kanavointi** antaa kaikille käyttäjille saman
taajuuden ja saman ajan, mutta jokainen bitti kerrotaan käyttäjän
omalla koodilla, joka on monta kertaa bittiä nopeampi. Koodit ovat
keskenään ortogonaalisia, joten vastaanotin erottaa käyttäjän
korreloimalla summasignaalin käyttäjän koodin kanssa:

```{.python tiedosto="esimerkit/06-cdma.py" osa="cdma"}
```

```{.tuloste tiedosto="esimerkit/06-cdma.odotettu"}
```

Kolmen käyttäjän signaalit ja voimakas kohina summautuvat, mutta
korrelaatio palauttaa kunkin bitit, koska muiden käyttäjien osuus
kumoutuu. CDMA oli 3G:n (WCDMA) perusta, ja sama levitys ilman
multipleksointia on GPS:ssä: satelliittien signaalit ovat kohinan
alapuolella, ja pitkä koodi nostaa ne esiin.

## Käytännössä

- **Valitse jako sen mukaan, mitä on runsaasti.** Kuidussa on
  aallonpituuksia (WDM), radiossa vähän kaistaa ja paljon tilaa (solut,
  MIMO), kuparissa taajuuksia (DSL, kaapelimodeemit).
- **Ortogonaalisuus on herkkä.** OFDM:n alikantoaallot vuotavat
  toisiinsa, jos taajuusvirhe tai Doppler on suuri; siksi
  alikantoaaltojen väli kasvaa nopeissa liikkuvissa järjestelmissä
  (5G:n numerologia).
- **Etuliite ja suojavälit ovat kapasiteettia.** Kun vertaat
  järjestelmiä, laske yleiskustannus mukaan: etuliite, opetussignaalit
  ja suojakaistat vievät tyypillisesti 10–25 %.
- **Staattinen jako hukkaa kapasiteettia.** TDM ja FDM varaavat
  kaistan, vaikka yhteys olisi hiljaa. Purskeiselle datalle
  tilastollinen jako on tehokkaampi (luku Kytkentätavat ja viive).

## Itsearviointi

- Osaat selittää TDM:n, FDM:n, WDM:n ja CDMA:n erot ja antaa esimerkin
  kustakin.
- Osaat selittää, miksi ortogonaaliset signaalit voidaan erottaa
  toisistaan, vaikka ne ovat päällekkäin.
- Osaat kuvata OFDM-lähettimen ja -vastaanottimen vaiheet ja syklisen
  etuliitteen tehtävän.
- Osaat laskea syklisen etuliitteen ja muun yleiskustannuksen osuuden
  kapasiteetista.
