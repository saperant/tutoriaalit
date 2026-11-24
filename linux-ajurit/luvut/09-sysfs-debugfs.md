# sysfs ja debugfs

Ajurilla on kaksi tiedostojärjestelmää laitteen tilan näyttämiseen:

- **sysfs** (`/sys`) on ajurimallin näkymä: jokainen laite, ajuri,
  väylä ja luokka on hakemisto, ja *attribuutit* ovat tiedostoja.
  sysfs on käyttäjätilan rajapinta, ja sen tiedostot ovat yhtä pysyviä
  kuin järjestelmäkutsut.
- **debugfs** (`/sys/kernel/debug`) on kehittäjän työkalupakki ilman
  sääntöjä tai lupauksia. Sen sisältö voi muuttua joka versiossa, ja
  tuotantoytimessä se on usein pois päältä.

Valinta kannattaa tehdä tietoisesti: kun jokin sovellus alkaa lukea
sysfs-tiedostoa, tiedostoa ei voi enää poistaa eikä sen muotoa muuttaa.

## Attribuutit

sysfs-attribuutin sääntö on *yksi arvo tiedostoa kohden*, tekstinä ja
rivinvaihdolla päättyen. Ajuri antaa lukufunktion (`show`) ja
tarvittaessa kirjoitusfunktion (`store`):

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="sysfs"}
```

- **`DEVICE_ATTR_RO(nimi)` ja `DEVICE_ATTR_RW(nimi)`** luovat
  attribuutin, jonka funktioiden nimet ovat `nimi_show` ja
  `nimi_store` ja oikeudet `0444` tai `0644`.
- **`sysfs_emit`** kirjoittaa sivun kokoiseen puskuriin ja tarkistaa
  rajat. Vanha tapa `sprintf` ei tarkista.
- **`store`** saa käyttäjän tekstin, joka on jo kopioitu ytimen
  muistiin. Se jäsennetään `kstrto*`-funktiolla, joka hylkää
  roskan ja hyväksyy lopun rivinvaihdon. Paluuarvo on käytetty pituus
  tai negatiivinen virhe.
- **`ATTRIBUTE_GROUPS`** kokoaa attribuutit ryhmäksi, joka annetaan
  ajurin `dev_groups`-kentässä (luku 4). Ajurimalli luo tiedostot, kun
  ajuri sidotaan laitteeseen, ja poistaa ne irrotuksessa.

Ryhmä `dev_groups`-kentässä on parempi kuin `device_create_file`-kutsu
`probe`-funktiossa. Tiedostot syntyvät ennen sidonnasta kertovaa
*uevent*-tapahtumaa (`bind`), joten `udev`-sääntö näkee ne heti, eikä
ajurin tarvitse poistaa niitä itse. Luvun 5 testi kirjoitti
attribuuttiin `jakso` ja luki attribuutin `heratyksia` hakemistosta
`/sys/devices/platform/9010000.herateajastin/`.
## Binääriattribuutit

Laitteen muisti tai laiteohjelmisto ei ole tekstiä.
*Binääriattribuutti* on tiedosto, jota luetaan ja kirjoitetaan
tavuina ja jolla on koko ja kohta, kuten luvun 8 muistipiirillä:

```{.c tiedosto="esimerkit/06-spi/muisti.c" osa="sysfs"}
```

sysfs rajaa luvut ja kirjoitukset attribuutin kokoon, joten ajurin ei
tarvitse tarkistaa kohtaa. Isommat laitteet kannattaa silti antaa
alijärjestelmälle: EEPROM- ja OTP-muistit kuuluvat *nvmem*-alijärjestelmään
ja flash-muistit MTD:hen.

## debugfs

debugfs-tiedosto voi olla mitä tahansa: rekisterivedos, laskuri,
tilakoneen tila tai kirjoitettava tiedosto, joka käynnistää
testitoiminnon. Valmiit apufunktiot tekevät yksinkertaiset tiedostot
yhdellä rivillä:

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="debugfs"}
```

- **`debugfs_create_u32`** näyttää muuttujan arvon. Vastaavat ovat
  `bool`-, `x32`- ja `blob`-tiedostoille (luku 6).
- **`DEFINE_SHOW_ATTRIBUTE`** tekee `seq_file`-tiedoston yhdestä
  `show`-funktiosta. `seq_file` hoitaa puskuroinnin ja kohdan, joten
  tuloste voi olla pitkä.
- **Virheitä ei tarkisteta.** debugfs-funktioiden paluuarvoja ei kuulu
  tarkistaa: ajurin on toimittava, vaikka debugfs olisi pois päältä tai
  tiedoston luonti epäonnistuisi.

Hakemisto poistetaan `remove`-funktiossa `debugfs_remove_recursive`-
kutsulla. Rekisterivedos näkyy samassa testissä kuin attribuutit. Luvun 10
harjoitusmoduuli käyttää kirjoitettavia debugfs-tiedostoja virheiden
käynnistämiseen. Sellainen kuuluu juuri debugfsiin eikä sysfsiin.

## Muut rajapinnat

| Rajapinta | Käyttö |
|---------------------|------------------------------------------|
| sysfs-attribuutti | laitteen asetukset ja tila, yksi arvo tiedostoa kohden |
| laitetiedosto ja `ioctl` | datavirrat ja toiminnot, joissa on useita argumentteja |
| alijärjestelmän rajapinta (hwmon, IIO, input) | laitetyypin standardimuoto, valmiit työkalut |
| `configfs` | käyttäjä luo ytimen olioita hakemistoina, esimerkiksi USB-laitetila |
| netlink | tapahtumat ja suuret määrät tietoa, verkko ja uevent |
| debugfs | kehittäjän työkalut, ei vakaa rajapinta |

sysfs-attribuutti dokumentoidaan ytimessä hakemistoon
`Documentation/ABI/`: polku, versio, yhteyshenkilö ja kuvaus. Kuvaus on
osa rajapintaa, ja ytimen kehittäjät pyytävät sitä uudelta
attribuutilta.

## Käytännössä

- **Yksi arvo tiedostoa kohden.** Jos tiedostoa pitää jäsentää, se kuuluu
  debugfsiin, alijärjestelmälle tai laitetiedostolle.
- **Käytä `sysfs_emit`- ja `kstrto*`-funktioita.** Ne tarkistavat
  puskurin koon ja syötteen muodon.
- **Anna attribuutit `dev_groups`-kentässä.** Tiedostot syntyvät ennen
  uevent-tapahtumaa ja poistuvat itsestään.
- **Älä tarkista debugfs-funktioiden paluuarvoja.** Debug-tuen puuttuminen
  ei saa estää ajurin toimintaa.
- **Älä tee debugfs-tiedostosta sovelluksen rajapintaa.** Jos sovellus
  tarvitsee tiedon, tee siitä dokumentoitu sysfs-attribuutti tai
  alijärjestelmän rajapinta.

## Itsearviointi

- Osaat tehdä laitteelle luettavia ja kirjoitettavia sysfs-attribuutteja
  ja antaa ne ajurin `dev_groups`-kentässä.
- Osaat tehdä binääriattribuutin laitteen muistin lukemiseen ja
  kirjoittamiseen.
- Osaat luoda debugfs-hakemiston laskureineen ja `seq_file`-
  rekisterivedoksen ja poistaa sen irrotuksessa.
- Osaat valita sysfsin, laitetiedoston, alijärjestelmän ja debugfsin
  välillä ja perustella valinnan rajapinnan pysyvyydellä.
