# Tilan synkronointi

Palvelin simuloi maailmaa ja lähettää asiakkaille *tilannevedoksia*
(snapshot): tiivistetyn kuvauksen niiden kannalta olennaisesta tilasta.
Vedosten koko ratkaisee, kuinka monta pelaajaa ja entiteettiä peli
kestää. Neljä keinoa pienentää sitä toistensa päälle: kvantisointi,
bittitason pakkaus, delta suhteessa kuitattuun vedokseen ja
kiinnostusalue.

## Kvantisointi ja bitit

Liukuluku vie 32 bittiä, vaikka pelin tarkkuudeksi riittäisi senttimetri
kilometrin alueella. Kvantisointi muuntaa arvon tunnetulta väliltä
kokonaisluvuksi, jossa on juuri tarvittava määrä bittejä:
1 024 metriä 1/128 metrin tarkkuudella vaatii 17 bittiä, suunta alle
asteen tarkkuudella 9 bittiä ja terveys 0–100 seitsemän.

```{.cpp tiedosto="esimerkit/05-bitit.cpp" osa="kvantisointi"}
```

Bittikirjoittaja pakkaa kentät peräkkäin ilman tavurajoja:

```{.cpp tiedosto="esimerkit/05-bitit.cpp" osa="kirjoittaja"}
```

```{.cpp tiedosto="esimerkit/05-bitit.cpp" osa="pakkaus"}
```

```{.tuloste tiedosto="esimerkit/05-bitit.odotettu"}
```

20 tavun rakenne mahtuu 51 bittiin, ja virhe on pienempi kuin pelaaja
voi nähdä. Kvantisointi tehdään myös palvelimen omaan tilaan tai
ainakin ennustukseen käytettävään tilaan: jos palvelin simuloi
täydellä tarkkuudella mutta asiakas saa pyöristetyn arvon, asiakkaan
ennustus (luku *Asiakkaan ennustus ja täsmäytys*) eroaa palvelimesta
jatkuvasti hieman.

## Delta suhteessa kuitattuun vedokseen

Useimmat entiteetit eivät muutu tikistä toiseen. Palvelin muistaa,
minkä vedoksen kukin asiakas on viimeksi kuitannut, ja lähettää vain
erot siihen. Pohjana on nimenomaan *kuitattu* vedos, ei edellinen
lähetetty: jos edellinen katosi, asiakas ei voi soveltaa siihen
perustuvaa deltaa. Kun kuittaus saapuu, pohja siirtyy eteenpäin.

```{.cpp tiedosto="esimerkit/05-vedokset.cpp" osa="koot"}
```

## Kiinnostusalue

Pelaajan ei tarvitse tietää kartan toisella puolella olevista
entiteeteistä. Palvelin valitsee jokaiselle asiakkaalle olennaiset
entiteetit etäisyyden, näkyvyyden tai joukkueen perusteella (interest
management, area of interest). Kiinnostusalue on samalla
huijaamisen esto: mitä ei lähetetä, sitä ei voi paljastaa (luku
*Auktoriteetti ja huijaamisen esto*).

```{.cpp tiedosto="esimerkit/05-vedokset.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/05-vedokset.odotettu"}
```

![Samat luvut kuvana: jokainen keino pienentää edellisen
tulosta.](kuvat/kaista.png){width=75%}

64 entiteetin täysi tila 30 kertaa sekunnissa vie 277 kbit/s
pelaajaa kohti. Kvantisointi pudottaa sen 96:een, delta 25:een ja
kiinnostusalue alle neljään. Kertoimet riippuvat pelistä: liikkuvat
entiteetit hyötyvät deltasta vähemmän kuin paikallaan olevat, ja tiheä
taistelu kasvattaa kiinnostusaluetta.

## Prioriteetit ja kaistan jako

Kun kaista ei riitä kaikkeen, palvelin valitsee, mitkä entiteetit
pääsevät tämän tikin pakettiin. Tavallinen malli on
*prioriteettikertymä*: jokaisen entiteetin prioriteetti kasvaa joka
tikki sen tärkeyden mukaan (lähellä, liikkuu, ampuu), suurimmat
lähetetään ja niiden kertymä nollataan. Kaukaiset entiteetit
päivittyvät harvemmin mutta eivät koskaan jää kokonaan pois.

## Käytännössä

- **Delta kuitattuun vedokseen, ei edelliseen.** Pidä palvelimella
  rengaspuskuri lähetetyistä vedoksista; jos kuittausta ei tule
  ajoissa, lähetä täysi vedos.
- **Kvantisoi myös simulaatiossa** sellaiset arvot, joiden pitää täsmätä
  asiakkaan ennustuksen kanssa.
- **Kiinteä paketin koko-budjetti** ja prioriteettikertymä sen
  täyttämiseen.
- **Pakkaus on mitattava.** Laske tavut tikkiä ja pelaajaa kohti
  tyypillisissä ja pahimmissa tilanteissa (koko joukkue samassa
  huoneessa).
- **Hinta:** delta ja kiinnostusalue lisäävät palvelimen muistia ja
  laskentaa pelaajaa kohti; bittipakkaus tekee protokollasta
  vaikeamman lukea. Versioi protokolla.

## Itsearviointi

- Osaat kvantisoida arvon ja valita bittimäärän tarkkuusvaatimuksen
  perusteella.
- Osaat toteuttaa bittikirjoittajan ja -lukijan.
- Osaat selittää, miksi delta lasketaan kuitattuun vedokseen eikä
  edelliseen lähetettyyn.
- Osaat arvioida vedosten kaistankulutuksen ja valita keinot sen
  pienentämiseen.
