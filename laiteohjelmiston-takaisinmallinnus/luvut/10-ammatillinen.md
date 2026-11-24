# Ammatilliset käyttötapaukset

Edelliset luvut rakensivat työkalupakin; tämä luku soveltaa sitä
kolmeen tilanteeseen, jotka toistuvat sulautetussa työssä: binääristä
paikannettu suorituskykyongelma, rikkoutuneen käännöksen tunnistus ja
oman laitteen tietoturva-auditointi. Kaikki kohteet ovat LT-100:n omia
muunnelmia.

## Suorituskykyregression paikannus

LT-100:n versio 2.4.1 on kentällä hitaampi kuin 2.4.0, vaikka
muutoslokin mukaan vain suodatusta muutettiin. Lähdekoodista vikaa ei
löydy. Binääri kertoo enemmän: suodatusfunktion prologi paljastaa, että
2.4.1 varaa suuren pinokehyksen ja tallettaa arvot pinoon rekisterien
sijaan — tunnusmerkki optimoimattomasta käännöksestä:

```{.bash tiedosto="esimerkit/10-ammatillinen/aja.sh" osa="prologi"}
```

```{.tuloste tiedosto="esimerkit/10-ammatillinen/odotettu" osa="s1"}
```

Ero varmistetaan emuloimalla: sama funktio molemmista kuvista samoilla
syötteillä, ja lasketaan käskyt:

```{.bash tiedosto="esimerkit/10-ammatillinen/aja.sh" osa="mittaa"}
```

```{.tuloste tiedosto="esimerkit/10-ammatillinen/odotettu" osa="s2"}
```

Tulos on sama, mutta 2.4.1 käyttää yli kaksinkertaisen määrän käskyjä.
Syy on kääntäjän asetus: funktioon on jäänyt `optimize("O0")`-attribuutti
tai käännösyksikkö on käännetty ilman optimointeja. Korjaus on
käännösasetuksissa, ei algoritmissa — ja sen löysi binääri, ei
lähdekoodi. Suorituskyvyn mittaamisen periaatteet ovat taidossa
*Suorituskyvyn analyysi ja optimointi*; tässä olennaista on, että
käskymäärän voi mitata emuloimalla ilman laitetta.

## Rikkoutunut käännös

Toinen muunnelma ei käynnisty lainkaan. Vika näkyy heti
vektoritaulusta: se sisältää koodia, ei kelvollisia osoitteita.

```{.bash tiedosto="esimerkit/10-ammatillinen/aja.sh" osa="rikki"}
```

```{.tuloste tiedosto="esimerkit/10-ammatillinen/odotettu" osa="s3"}
```

Pinon alkuarvo ei ole RAM-alueella ja Reset-osoitteesta puuttuu
Thumb-bitti, joten laite lukkiutuu heti käynnistyksessä. Syy on
linkkeriskriptissä: vektoritaulun osiosta puuttui `KEEP`, joten
linkkeri karsi sen pois käyttämättömänä (`--gc-sections`).
Käynnistyslatain silti hyväksyi kuvan, koska CRC täsmäsi — tarkiste ei
kerro, onko sisältö mielekäs. Tällaisen vian tunnistaa binääristä
minuutissa, kun tietää, miltä kelvollisen vektoritaulun kuuluu näyttää.

## Tietoturva-auditointi

Kun omaa tuotetta auditoidaan, etsitään heikkouksia, jotka hyökkääjä
löytäisi. Luvuissa 5 ja 9 löytyi jo kaksi: kovakoodattu, jaettu avain ja
sillä suojattu huoltosalasana, jotka emulointi paljasti. Tässä kaksi
muuta.

**Puskurin ylivuoto jäsentimessä.** Kehysten käsittelijä (luku 6)
kopioi NIMI-kehyksen datan kiinteään pinopuskuriin tarkistamatta
pituutta. Liian pitkä nimi ylittää puskurin. Laitteessa on onneksi
pinon suojaus (kanari), joka havaitsee ylivuodon ja pysäyttää laitteen
hallitusti:

```{.bash tiedosto="esimerkit/10-ammatillinen/aja.sh" osa="audit"}
```

```{.tuloste tiedosto="esimerkit/10-ammatillinen/odotettu" osa="s4"}
```

Pinon suojaus muuttaa muistin korruption hallituksi pysäytykseksi,
mutta oikea korjaus on tarkistaa pituus ennen kopiointia (korjattu
versiossa 2.4.2). Muistiturvallisuuden virheet ja niiden hyödyntäminen
ja torjunta ovat taidossa *Haavoittuvuuksien analyysi ja
hyödyntäminen*.

**Allekirjoittamaton päivitys.** Otsakkeen allekirjoituskenttä on nolla,
ja käynnistyslatain 1.2 hyväksyy sovelluksen pelkän CRC:n perusteella.
CRC havaitsee vahingon muttei hyökkäystä: kuka tahansa voi muuttaa
sovellusta ja laskea CRC:n uudelleen. Korjattu käynnistyslatain vaatii
allekirjoituksen ja hylkää allekirjoittamattoman kuvan:

```{.bash tiedosto="esimerkit/10-ammatillinen/aja.sh" osa="allekirjoitus"}
```

```{.tuloste tiedosto="esimerkit/10-ammatillinen/odotettu" osa="s5"}
```

Nykyinen latain käynnistää allekirjoittamattoman sovelluksen; korjattu
latain hylkää sen. Allekirjoituksen tarkistuksen oikea toteutus
(julkisen avaimen kryptografia, luottamusketju) on taidossa
*Sulautettujen järjestelmien tietoturva*. Takaisinmallinnuksen rooli on
osoittaa, että suojaus puuttuu tai ei toimi — ja antaa näin peruste
korjaukselle.

## Käytännössä

- **Paikanna suorituskykyongelma binääristä.** Prologi ja käskymäärä
  kertovat optimoimattoman käännöksen. Emuloimalla saat deterministisen
  käskymäärän ilman laitetta ja kellon kohinaa.
- **Tunnista rikkoutunut käännös vektoritaulusta.** Kelvoton pino tai
  Thumb-bititön Reset-osoite kertoo heti, ettei kuva käynnisty, vaikka
  tarkiste täsmäisi.
- **Auditoi oma tuote hyökkääjän tavoin.** Etsi kovakoodatut avaimet,
  tarkistamattomat jäsentimet, avoimet debug-portit ja
  allekirjoittamattomat päivitykset. Takaisinmallinnus on tähän nopein
  työkalu.
- **Puolustus:** CRC ei ole allekirjoitus, pinon suojaus ei korvaa
  pituustarkistusta, eikä jaettu avain ole salaisuus. Jokaiselle
  löydökselle on oikea korjaus, joka on taidossa *Sulautettujen
  järjestelmien tietoturva*.

## Itsearviointi

- Osaat paikantaa suorituskykyregression binääristä prologin ja
  emuloidun käskymäärän avulla.
- Osaat tunnistaa rikkoutuneen käännöksen vektoritaulusta ja selittää
  linkkerin osakarsinnan vaikutuksen.
- Osaat auditoida oman laitteen tavallisimmat heikkoudet:
  kovakoodatut avaimet, tarkistamattomat puskurit ja
  allekirjoittamattomat päivitykset.
- Osaat nimetä jokaiselle heikkoudelle oikean korjauksen ja tietää,
  mihin taitoon sen toteutus kuuluu.
