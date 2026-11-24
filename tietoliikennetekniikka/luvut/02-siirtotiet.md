# Siirtotiet

Siirtotie on fyysinen väylä, jota pitkin signaali kulkee: kuparijohdin,
valokuitu tai radiotie. Jokainen vaimentaa signaalia ja vääristää sitä
omalla tavallaan, ja nämä ominaisuudet ratkaisevat, kuinka pitkälle ja
kuinka nopeasti dataa voi siirtää.

## Kupari: kierretty pari

Ethernetin kaapelit koostuvat neljästä kierretystä johdinparista.
Parin johtimissa kulkee sama signaali vastakkaisina (differentiaalinen
siirto), ja kierto saa ulkoisen häiriön indusoitumaan molempiin
johtimiin lähes samanlaisena, jolloin se kumoutuu vastaanottimessa.

Kuparin vaimennus kasvaa taajuuden mukana. Suurilla taajuuksilla virta
ahtautuu johtimen pinnalle (virranahto, *skin effect*), jolloin
resistanssi kasvaa taajuuden neliöjuuren mukaan, ja lisäksi eriste
kuluttaa energiaa suoraan taajuuteen verrannollisesti:

```{.python tiedosto="esimerkit/02-kupari.py" osa="taulukko"}
```

```{.python tiedosto="esimerkit/02-kupari.py" osa="pituus"}
```

```{.tuloste tiedosto="esimerkit/02-kupari.odotettu"}
```

100 metrin kaapelista 100 MHz:n taajuudella pääsee perille vain
prosentti tehosta. Tämä selittää Ethernet-standardien rakenteen:
1000BASE-T ei lähetä 1000 Mbit/s yhdellä parilla vaan 250 Mbit/s
neljällä parilla yhtä aikaa, ja se pakkaa kaksi bittiä symboliin, jotta
symbolinopeus pysyy 125 megabaudissa ja käytetty taajuusalue noin
62,5 MHz:ssä.
Desibeleinä vaimennus on suoraan verrannollinen pituuteen, minkä vuoksi
standardit määrittelevät enimmäispituuden (kierretylle parille 100 m).

Vaimennuksen lisäksi kuparissa vaivaa **ylikuuluminen** (*crosstalk*):
parin signaali vuotaa viereisiin pareihin. Lähipään ylikuuluminen
(NEXT) on pahin, koska vuotava signaali on lähettimen lähellä vielä
voimakas. Nopeat Ethernet-tyypit poistavat tunnetun ylikuulumisen
digitaalisesti, koska vastaanotin tietää, mitä sen omat parit
lähettävät.

## Valokuitu

Valokuidussa signaali on valoa, joka pysyy kuidun ytimessä
kokonaisheijastuksen ansiosta. **Monimuotokuidussa** ydin on paksu
(50 µm), ja valo etenee monena muotona eri pituisia reittejä, mikä
levittää pulssia (muotodispersio) ja rajaa matkan satoihin metreihin.
**Yksimuotokuidussa** ydin on noin 9 µm, valo etenee yhtenä muotona,
ja yhteys voi olla kymmeniä kilometrejä ilman vahvistusta.

Kuituyhteys suunnitellaan **vaimennusbudjetilla**: lähettimen tehon ja
vastaanottimen herkkyyden ero jaetaan kuidun, liittimien ja jatkosten
vaimennuksille, ja varaa jätetään vanhenemiselle ja korjauksille.

```{.python tiedosto="esimerkit/02-kuitu.py" osa="budjetti"}
```

Vaimennus ei ole ainoa raja. Laserkin lähettää useaa aallonpituutta,
ja eri aallonpituudet kulkevat kuidussa hieman eri nopeudella
(**kromaattinen dispersio**). Pulssi leviää matkalla, ja kun se
leviää naapuribitin päälle, bitit sekoittuvat:

```{.python tiedosto="esimerkit/02-kuitu.py" osa="dispersio"}
```

```{.tuloste tiedosto="esimerkit/02-kuitu.odotettu"}
```

Pitkillä yhteyksillä dispersio korjataan digitaalisesti koherentissa
vastaanottimessa tai dispersiota kompensoivalla kuidulla, ja vaimennus
optisilla vahvistimilla. Yksi kuitu kantaa useita aallonpituuksia
rinnakkain (WDM, luku Multipleksointi).

## Radiotie

Radiotiellä signaalin teho jakautuu laajenevalle pallopinnalle, joten
**vapaan tilan vaimennus** kasvaa etäisyyden neliön mukaan:
6 dB lisää aina, kun etäisyys kaksinkertaistuu, ja 20 dB, kun se
kymmenkertaistuu. Vaimennus riippuu myös aallonpituudesta: korkeammalla
taajuudella antennin vastaanottopinta-ala on pienempi.

```{.python tiedosto="esimerkit/02-radio.py" osa="fspl"}
```

Sisätiloissa ja kaupungeissa signaali saapuu vastaanottimeen monta
reittiä: suoraan ja heijastuneena seinistä. Eri reittien signaalit
summautuvat eri vaiheissa, joten vastaanotettu teho vaihtelee jo
muutaman senttimetrin siirrolla (**monitie-eteneminen** ja
**häipymä**). Kun suoraa reittiä ei ole, summa noudattaa
Rayleigh-jakaumaa:

```{.python tiedosto="esimerkit/02-radio.py" osa="rayleigh"}
```

```{.tuloste tiedosto="esimerkit/02-radio.odotettu"}
```

Kymmenesosan ajasta teho on yli 10 dB keskiarvon alapuolella ja
sadasosan ajasta yli 20 dB. Radiojärjestelmät torjuvat häipymää
monimuotoisuudella: useampi antenni (MIMO), useampi taajuus (OFDM:n
alikantoaallot, luku Multipleksointi) ja virheenkorjaus lomituksen
kanssa (luku Virheiden havaitseminen ja korjaus).

## Käytännössä

- **Laske budjetti ennen kuin valitset tekniikan.** Vaimennusbudjetti
  ja linkkibudjetti (luku Kanavan kapasiteetti) kertovat, riittääkö
  yhteys, ennen kuin kaapelia vedetään tai tukiasemaa ostetaan. Jätä
  aina varaa (3–10 dB): liittimet likaantuvat ja seinät muuttuvat.
- **Kupari lyhyille, kuitu pitkille matkoille.** Kierretty pari on
  halpa ja tuo tarvittaessa sähkön (PoE), mutta rajoittuu 100 metriin.
  Kuitu ei kerää sähkömagneettisia häiriöitä, eristää galvaanisesti
  rakennusten välillä ja kulkee kilometrejä.
- **Radiossa vaimennus ei ole vakio.** Suunnittele häipymävaraa ja
  monimuotoisuutta; yksittäinen mittaus yhdestä pisteestä ei kerro
  yhteyden laadusta.
- **Korkeampi taajuus ei kanna yhtä kauas.** 5 GHz:n Wi-Fi vaimenee
  vapaassa tilassa 7 dB enemmän kuin 2,4 GHz:n ja läpäisee seiniä
  huonommin, mutta sillä on enemmän kaistaa ja vähemmän häiriöitä.

## Itsearviointi

- Osaat laskea desibeleinä ketjun, jossa on vahvistuksia ja
  vaimennuksia, ja muuntaa tuloksen milliwateiksi.
- Osaat selittää, miksi kuparin vaimennus kasvaa taajuuden mukana ja
  miksi kierretty pari vähentää häiriöitä.
- Osaat laatia kuituyhteyden vaimennusbudjetin ja kertoa, milloin
  dispersio rajoittaa nopeutta.
- Osaat laskea vapaan tilan vaimennuksen ja selittää, miksi
  monitie-eteneminen aiheuttaa häipymää.
