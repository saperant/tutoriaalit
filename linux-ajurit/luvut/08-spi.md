# SPI-ajurit

SPI-alijärjestelmä on rakennettu samoin kuin I2C: *ohjaimen ajuri*
(`spi_controller`) siirtää tavuja väylällä, ja *laitteen ajuri*
(`spi_driver`) tuntee yhden piirin komennot. Laitteet ovat ohjaimen
lapsia, ja ne valitaan piirinvalintalinjalla (CS). Laitteen nimi
`spi0.0` on ohjaimen numero ja CS-linjan numero.

QEMU:n virt-koneessa ei ole SPI-ohjainta. Tämän luvun ohjain on
ohjelma, jonka väylällä on simuloitu 256-tavuinen sarjamuistipiiri.
Sama simulaatio tehtiin Pythonilla *Oheislaiteväylät*-tutoriaalissa;
tässä se on ytimen sisällä, jotta piirin ajuri voidaan testata oikeaa
SPI-alijärjestelmää vasten. Luku näyttää samalla, miten ohjaimen ajuri
kirjoitetaan.

```{.dot otsikko="Luvun SPI-pino. Molemmat ajurit kirjoitetaan tässä luvussa; simuloitu muistipiiri on ohjaimen ajurin sisällä."}
digraph {
  rankdir=TB; node [shape=box];
  kayttaja [label="käyttäjätila: sysfs-tiedosto sisalto"];
  ajuri [label="laitteen ajuri muisti (spi_driver)"];
  ydin [label="SPI-alijärjestelmä: spi_sync, viestijono, CS"];
  ohjain [label="ohjaimen ajuri vspi (spi_controller)"];
  piiri [label="simuloitu 256 tavun muistipiiri", style="rounded,dashed"];
  kayttaja -> ajuri -> ydin -> ohjain -> piiri;
}
```

## Siirrot ja viestit

SPI-siirto on aina kaksisuuntainen: jokaista lähetettyä tavua kohden
vastaanotetaan yksi. Alijärjestelmä kuvaa tämän kahdella rakenteella:

- **`spi_transfer`** on yksi puskuripari: `tx_buf` lähetettävälle ja
  `rx_buf` vastaanotettavalle datalle, kumpikin voi puuttua, ja `len`.
  Siirrossa voi myös olla viive, nopeus ja tieto siitä, nostetaanko CS
  siirron jälkeen.
- **`spi_message`** on jono siirtoja, joiden ajan CS pysyy alhaalla.
  Viesti on atominen: muut saman väylän laitteet eivät pääse väliin.

Laitteen ajuri lähettää viestin funktiolla `spi_sync`, joka odottaa
valmistumista, tai `spi_async`, joka kutsuu takaisinkutsua.
Apufunktiot `spi_write`, `spi_read`, `spi_write_then_read` ja
`spi_sync_transfer` kokoavat tavallisimmat viestit.

## Ohjaimen ajuri

Ohjaimen ajuri täyttää `spi_controller`-rakenteen ja antaa ytimelle
funktiot, jotka ohjaavat CS-linjaa ja siirtävät yhden `spi_transfer`-
rakenteen. Jonon käsittely, viestien järjestys ja CS:n ohjaus siirtojen
välissä ovat alijärjestelmän työtä:

```{.c tiedosto="esimerkit/06-spi/vspi.c" osa="ohjain"}
```

```{.c tiedosto="esimerkit/06-spi/vspi.c" osa="probe"}
```

Oikeassa ohjaimessa `transfer_one` kirjoittaisi tavut ohjaimen
FIFO-puskuriin, palauttaisi positiivisen luvun ja kutsuisi
keskeytyksestä `spi_finalize_current_transfer`, kun siirto on valmis.
Ohjelmallinen ohjain on valmis heti ja palauttaa nollan. Simuloidun
piirin tila on ohjaimen yksityisessä datassa:

```{.c tiedosto="esimerkit/06-spi/vspi.c" osa="piiri"}
```

Laite luodaan `spi_new_device`-funktiolla ja `spi_board_info`-
rakenteella, jossa nimi (`modalias`) valitsee ajurin. Laitepuussa sama
tieto on ohjaimen solmun lapsessa: `reg` on CS-linjan numero,
`spi-max-frequency` suurin nopeus ja `compatible` ajurin valinta.
Moduuli luo vielä itselleen platform-laitteen, jonka laitepuu tavallisesti
antaisi:

```{.c tiedosto="esimerkit/06-spi/vspi.c" osa="moduuli"}
```

## Laitteen ajuri

Muistipiirin ajuri tunnistaa piirin `probe`-funktiossa komennolla
`0x9f`, jonka vastauksena piiri antaa valmistajan, tyypin ja koon.
Tunnistusta käyttävät myös ytimen SPI-NOR-ajurit:

```{.c tiedosto="esimerkit/06-spi/muisti.c" osa="probe"}
```

Luku on yksi viesti, jossa komento ja osoite lähetetään ensimmäisessä
siirrossa ja data luetaan toisessa:

```{.c tiedosto="esimerkit/06-spi/muisti.c" osa="lue"}
```

Kirjoitus vaatii piirissä kirjoitusluvan, joka on oma komentonsa. CS:n on
noustava luvan jälkeen, joten lupa lähetetään omana viestinään:

```{.c tiedosto="esimerkit/06-spi/muisti.c" osa="kirjoita"}
```

SPI-puskurien on oltava DMA-kelpoisia, koska ohjaimen ajuri voi siirtää
ne DMA:lla (luku 6). Komentopuskuri on siksi ajurin varatussa rakenteessa
omalla välimuistirivillään (`____cacheline_aligned`) eikä pinossa.
`spi_write_then_read` on poikkeus: se kopioi puskurit omaansa, joten sille
voi antaa pinon muuttujia.

## Testi

Muistin sisältö näkyy sysfsissä binääritiedostona (luku 9). Testi
lataa ensin ohjaimen, jolloin laite syntyy ilman ajuria, ja sitten
ajurin:

```{.text tiedosto="esimerkit/06-spi/spi.vaiheet" osa="ohjain"}
```

```{.tuloste tiedosto="esimerkit/testit/06-spi.odotettu" osa="ohjain"}
```

```{.text tiedosto="esimerkit/06-spi/spi.vaiheet" osa="ajuri"}
```

```{.tuloste tiedosto="esimerkit/testit/06-spi.odotettu" osa="ajuri"}
```

Tyhjä flash-muisti on täynnä tavua `0xff`. Kirjoitettu teksti näkyy
muistin alussa, kun piiri on ottanut sen vastaan kirjoitusluvan jälkeen.

Väylän liikenteen voi nähdä ohjaimen `dev_dbg`-riveistä, jotka
kytketään päälle dynaamisella debugilla (luku 10). Lokirivien alussa
on laitteen eikä ohjaimen ajurin nimi, koska viestit liittyvät
laitteeseen `spi0.0`:

```{.text tiedosto="esimerkit/06-spi/spi.vaiheet" osa="dyndbg"}
```

```{.tuloste tiedosto="esimerkit/testit/06-spi.odotettu" osa="dyndbg"}
```

Neljän tavun luku on yksi CS-jakso, jossa on kaksi siirtoa: komento ja
osoite (2 tavua, lähetys) ja data (4 tavua, vastaanotto). Jos väylällä
olisi logiikka-analysaattori, sama jakso näkyisi siinä.

## spidev

Käyttäjätilasta SPI-laitetta voi käyttää `spidev`-ajurin kautta
(`/dev/spidevB.C`), jolloin ajuri on ohjelma eikä ytimen moduuli.
Tapa sopii kokeiluihin ja laitteisiin, joiden ainoa käyttäjä on yksi
sovellus. Ytimen ajuri tarvitaan, kun laitteen pitää näkyä
alijärjestelmässä (MTD-muisti, hwmon, IIO), kun sitä käyttää ydin itse
tai kun laite käyttää keskeytyksiä.

## Käytännössä

- **Kokoa komento ja data yhdeksi viestiksi.** CS pysyy alhaalla, eikä
  saman väylän toinen laite pääse väliin.
- **Käytä DMA-kelpoisia puskureita.** Ei pinon muuttujia `spi_sync`-
  kutsuissa; poikkeus on `spi_write_then_read`.
- **Tunnista piiri `probe`-funktiossa.** SPI:ssä ei ole osoitteita,
  joten väärä laitepuu antaa piirille väärän ajurin.
- **Jätä CS:n ja viestijonon käsittely alijärjestelmälle.** Ohjaimen
  ajurin tarvitsee toteuttaa vain yksi siirto ja CS-linjan ohjaus.
- **Käytä ytimen valmista alijärjestelmää flash-muisteille.** SPI-NOR ja
  MTD tuntevat satoja piirejä, joten omaa muistiajuria ei yleensä
  tarvita.

## Itsearviointi

- Osaat selittää `spi_transfer`- ja `spi_message`-rakenteiden roolin ja
  sen, miksi viesti pitää CS-linjan alhaalla.
- Osaat kirjoittaa SPI-laitteen ajurin, joka tunnistaa piirin ja lukee
  ja kirjoittaa sitä viesteillä.
- Osaat kirjoittaa yksinkertaisen ohjaimen ajurin `transfer_one`- ja
  `set_cs`-funktioilla ja lisätä väylälle laitteen.
- Osaat perustella, milloin `spidev` riittää ja milloin tarvitaan ytimen
  ajuri.
