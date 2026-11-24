# Kaikki yhteen: UDP-peli

Tämän luvun peli kulkee oikeiden UDP-pistokkeiden yli: palvelin ja kaksi
asiakasta ovat erillisiä prosesseja, ja niiden välillä on vain
käyttöjärjestelmän verkkopino. Peli on luvun *Lukitusaskel ja
rollback* kaksintaistelu, ja palvelin toimii lukitusaskeleen
tahdistajana: se kerää syötteet, laskee ruudun, kun molemmat ovat
perillä, ja jakaa vahvistetut syötteet. Asiakkaat simuloivat pelin
itse, ja lopuksi kaikkien kolmen tarkistussummien on oltava samat.

## Protokolla

Viestejä on kaksi. Asiakkaan viestissä on kahdeksan viimeisintä
syötettä, palvelimen viestissä kahdeksan viimeisintä vahvistettua
syötettä molemmilta pelaajilta. Toisto tekee kerroksesta luotettavan
ilman kuittauskirjanpitoa: kadonnut viesti korvautuu seuraavalla, kunhan
kumpikaan osapuoli ei ole yli kahdeksaa ruutua toisen edellä.

```{.cpp tiedosto="esimerkit/udp/src/protokolla.hpp" osa="viestit"}
```

Viestit sarjallistetaan tavuiksi kenttä kerrallaan
verkkotavujärjestyksessä. Rakenteen muistikuvaa ei koskaan lähetetä
sellaisenaan, koska täytetavut, tavujärjestys ja kääntäjä vaihtelevat.

```{.cpp tiedosto="esimerkit/udp/src/protokolla.hpp" osa="sarjallistus"}
```

## Palvelin

Palvelin sitoutuu silmukkaosoitteen vapaaseen porttiin ja kirjoittaa
portin tiedostoon, josta asiakkaat sen löytävät. Pääsilmukka odottaa
viestiä enintään 5 ms, tallentaa uudet syötteet ja laskee kaikki ruudut,
joihin molempien syötteet ovat perillä. Viallinen viesti hylätään:
pelaajan numero ja ruudun numero tarkistetaan ennen käyttöä.

```{.cpp tiedosto="esimerkit/udp/src/palvelin.cpp" osa="silmukka"}
```

Tilaviesti lähtee 5 ms:n välein, vaikka mikään ei muuttuisi, ja
lopetusviesti toistetaan 20 kertaa. Kumpikin on tapa saada
luotettavuutta epäluotettavan yhteyden yli ilman kuittauksia.

## Asiakas

Asiakas pysyy enintään ikkunan verran palvelimen vahvistaman edellä.
Tämä takaa, että palvelimen viestissä on aina kaikki asiakkaalta
puuttuvat vahvistetut syötteet.

```{.cpp tiedosto="esimerkit/udp/src/asiakas.cpp" osa="asiakas"}
```

## Ajo

Skripti käynnistää prosessit, odottaa portin ja tulostaa raportit aina
samassa järjestyksessä. Kaikilla prosesseilla on aikakatkaisu, ettei
jumiutunut testi jää ikuisesti odottamaan.

```{.bash tiedosto="esimerkit/udp/aja.sh"}
```

```{.make tiedosto="esimerkit/Makefile" osa="udp"}
```

```{.tuloste tiedosto="esimerkit/udp/udp.odotettu"}
```

Tuloste on sama joka ajolla, vaikka pakettien ajoitus vaihtelee:
lukitusaskel tekee lopputuloksesta riippumattoman siitä, milloin
mikäkin paketti saapui. Peli ei odota seinäkelloa, joten 600 ruutua
kuluu testissä alle sekunnissa; oikeassa pelissä asiakas lähettäisi
yhden uuden syötteen ruudun välein (16 ms).

## Käytännössä

- **Yksi pistoke, ei säikeitä:** `poll` aikakatkaisulla riittää
  pelipalvelimelle, ja silmukka pysyy deterministisenä ja helposti
  testattavana. Suuret palvelimet hajauttavat pelit prosesseihin, eivät
  säikeisiin.
- **Sarjallista kenttä kerrallaan** ja tarkista jokainen luettu arvo.
  Lukijan on kestettävä lyhyt, pitkä ja väärän tyyppinen viesti;
  `at` heittää poikkeuksen liian lyhyestä viestistä.
- **Toisto on halpa luotettavuus** pienille viesteille. Isommille
  viesteille tarvitaan luvun *Luotettavuuskerros* kuittaukset.
- **Testaa oikealla verkolla huonoissa oloissa.** Linuxissa
  `tc qdisc add dev lo root netem delay 50ms 20ms loss 5%`
  heikentää silmukkayhteyttä (vaatii pääkäyttäjän oikeudet ja
  netem-tuen ytimessä); tämän luvun tuloste ei saa muuttua.
- **Hinta:** oikea verkkokoodi tarvitsee lisäksi yhteyden muodostuksen
  ja todennuksen (palvelin ei saa uskoa pelkkää lähettäjän osoitetta),
  salauksen (DTLS tai oma AEAD), aikakatkaisut ja uudelleenliittymisen.

## Itsearviointi

- Osaat toteuttaa UDP-palvelimen ja -asiakkaan `poll`-pohjaisella
  silmukalla.
- Osaat sarjallistaa viestit tavuiksi ja tarkistaa vastaanotetut
  kentät.
- Osaat tehdä pienistä viesteistä luotettavia toistamalla ja
  ikkunoimalla.
- Osaat testata verkkopeliä niin, että tulos on toistettava.
