# Palvelinlaitteisto

Palvelin eroaa pöytäkoneesta harvoin suorittimen nopeudelta. Ero on
siinä, että palvelin on suunniteltu toimimaan vuosia keskeytyksettä ja
kertomaan itse viasta ennen kuin vika kaataa palvelun: virheitä
korjaava muisti, kahdennetut virtalähteet ja tuulettimet, vaihdettavat
levyt käynnissä ollessa sekä erillinen hallintaprosessori, jonka kautta
konetta voi hallita, vaikka käyttöjärjestelmä ei vastaisi.

## Virheitä korjaava muisti (ECC)

Muistin bitti voi kääntyä kosmisen säteilyn, sähköisen häiriön tai
vanhenevan piirin takia. Pöytäkoneessa kääntynyt bitti näkyy
satunnaisena kaatumisena tai korruptoituneena tiedostona. Palvelimella,
jossa on satoja gigatavuja muistia ja joka käsittelee rahaliikennettä
vuosia, se on varma tapahtuma. Siksi palvelinmuisti on *ECC-muistia*
(error-correcting code): jokaisen 64-bittisen sanan rinnalla on 8
tarkistusbittiä, joiden avulla muistiohjain korjaa yhden kääntyneen
bitin ja havaitsee kaksi.

Periaate on Hamming-koodi, jonka teoria (etäisyys, korjauskyky) on
taidossa *Tietoliikennetekniikka*. Tarkistusbitit ovat paikoissa 1, 2, 4 ja 8,
ja kukin kattaa ne databitit, joiden paikkanumerossa on vastaava bitti.
Virheen jälkeen epäonnistuneiden tarkistusten summa (oireyhtymä,
*syndrome*) on suoraan virheellisen bitin paikka:

```{.python tiedosto="esimerkit/02-ecc.py" osa="koodaus"}
```

```{.python tiedosto="esimerkit/02-ecc.py" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/02-ecc.odotettu"}
```

Viimeinen rivi on tärkein. Kahden bitin virhettä ei voi korjata, mutta
se havaitaan, ja muistiohjain pysäyttää koneen (machine check) sen
sijaan, että väärä data jatkaisi matkaa. Palvelimelle kaatuminen on
parempi kuin hiljaa väärä tulos.

Korjatut virheet (CE, correctable error) eivät näy käyttäjälle, mutta
ne kertovat kammasta, joka on hajoamassa. Linuxin EDAC-ajuri laskee ne
muistikammoittain hakemistoon `/sys/devices/system/edac`. Valvonnan
kannattaa seurata laskurien kasvua:

```{.bash tiedosto="esimerkit/02-edac.sh" osa="raportti"}
```

```{.tuloste tiedosto="esimerkit/02-edac.odotettu"}
```

Testiä varten skripti rakentaa saman hakemistorakenteen
tilapäishakemistoon. Oikealla koneella juurena on `/`, ja samat tiedot
saa myös `rasdaemon`-palvelulta (`ras-mc-ctl --error-count`).

## Kahdennettu virransyöttö ja jäähdytys

Palvelimessa on tyypillisesti kaksi virtalähdettä, joista kumpikin
jaksaa yksin (*N+1*). Kahdennus suojaa kuitenkin vain, jos:

- virtalähteet kytketään **eri syöttöihin** (A- ja B-puoli, eri
  UPS-laitteet ja eri sulakkeet). Kaksi virtalähdettä samassa
  jatkojohdossa suojaa vain virtalähteen viasta.
- kumpikin syöttö **kestää koko kuorman**. Jos räkin koneet vievät
  yhteensä 70 % kummankin syötön kapasiteetista, toisen syötön
  katkeaminen ylikuormittaa toisen.
- **redundanssin menetys hälyttää.** Kone toimii yhdelläkin
  virtalähteellä, joten vika jää muuten huomaamatta kuukausiksi.

```{.dot otsikko="Kahdennettu virransyöttö. Kumpikin virtalähde saa sähkönsä omasta ketjustaan, joten yhden UPS-laitteen, sulakkeen tai jakelukiskon vika ei sammuta palvelinta. Kummankin ketjun on jaksettava koko kuorma yksin."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.55;
  a0 [label="syöttö A"]; a1 [label="UPS A"]; a2 [label="jakelukisko A"]; pa [label="virtalähde 1"];
  b0 [label="syöttö B"]; b1 [label="UPS B"]; b2 [label="jakelukisko B"]; pb [label="virtalähde 2"];
  s [label="palvelin", penwidth=1.6];
  a0 -> a1 -> a2 -> pa -> s;
  b0 -> b1 -> b2 -> pb -> s;
}
```

Tuulettimet ja lämpötila-anturit valvotaan samoin. Tuloilman
lämpötila on usein parempi hälytyksen lähde kuin suorittimen
lämpötila, koska se kertoo konesalin jäähdytyksen tilasta.

## Hallintaprosessori: IPMI, BMC ja Redfish

Palvelimen emolevyllä on oma pieni tietokone, *BMC* (baseboard
management controller). Se toimii, kun palvelin on sammutettu tai
käyttöjärjestelmä on jumissa, ja sen kautta voi:

- käynnistää, sammuttaa ja käynnistää koneen uudelleen,
- käyttää konsolia etänä (virtuaalinen näyttö ja näppäimistö),
- liittää asennuslevyn kuvan verkon yli,
- lukea anturit, virhelokin ja laitteiston kokoonpanon.

Valmistajat käyttävät omia nimiään (iDRAC, iLO, XClarity), mutta
rajapinnat ovat standardeja. Vanha *IPMI* on binääriprotokolla
(`ipmitool`), uusi *Redfish* on REST-rajapinta, joka palauttaa JSONia.
Valvonta lukee Redfishistä virtalähteiden ja lämpötilojen tilan:

```{.python tiedosto="esimerkit/02-redfish.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/02-redfish.odotettu"}
```

Paluuarvo 0, 1 tai 2 (OK, WARNING, CRITICAL) on Nagios-yhteensopivien
valvontajärjestelmien yleinen sopimus, joten saman tarkistuksen voi
liittää useimpiin valvontatyökaluihin.

BMC on täysivaltainen pääsy koneeseen, joten se on myös houkutteleva
hyökkäyskohde. BMC:t kytketään **erilliseen hallintaverkkoon**, jonne
pääsee vain ylläpitäjien hyppykoneelta tai VPN:n kautta (ks.
*Verkkoinfrastruktuuri*). Oletustunnukset vaihdetaan, ja BMC:n
laiteohjelmisto päivitetään samalla vakavuudella kuin
käyttöjärjestelmä: BMC-haavoittuvuuksia on löytynyt jokaiselta
valmistajalta.

## Käytännössä

- **Hälytä korjatuista virheistä ennen korjaamattomia.** Kammaa
  vaihdetaan, kun korjattujen virheiden määrä kasvaa, ei vasta, kun
  kone kaatuu.
- **Redundanssin menetys on hälytys, ei tieto.** Kahdennettu osa,
  jonka parin vika ei hälytä, on yksittäinen vikaantumispiste, josta
  ei tiedetä.
- **Kahdennus loppuun asti.** Kaksi virtalähdettä vaatii kaksi
  syöttöä, kaksi verkkokorttia vaatii kaksi kytkintä.
- **Hallintaverkko erilleen.** BMC ei ole koskaan tuotantoverkossa
  eikä internetissä.
- **Inventaario automaattisesti.** Sarjanumerot, laiteohjelmistojen
  versiot ja takuun päättyminen kerätään Redfishistä, ei taulukkoon
  käsin.

## Itsearviointi

- Osaat selittää, miten ECC-muisti korjaa yhden ja havaitsee kahden
  bitin virheen, ja miksi korjaamaton virhe pysäyttää koneen.
- Osaat seurata muistin korjattuja virheitä ja päättää, milloin kampa
  vaihdetaan.
- Osaat kertoa, mitä kahdennettu virransyöttö vaatii, jotta se todella
  suojaa.
- Osaat lukea palvelimen kunnon Redfish-rajapinnasta ja kertoa, miksi
  BMC kuuluu erilliseen hallintaverkkoon.
