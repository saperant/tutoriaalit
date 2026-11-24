# Platform-ajurit ja laitepuu

Järjestelmäpiirin oheislaitteet, kuten ajastimet, sarjaportit,
GPIO-ohjaimet ja I2C-ohjaimet, ovat muistiin kuvattuja rekisterialueita
väylällä, joka ei osaa kertoa itse, mitä siinä on. PCI- tai
USB-laitteesta ydin voi kysyä valmistajan ja mallin, mutta piirin
sisäisestä ajastimesta ei. Linux kuvaa tällaiset laitteet
*platform-laitteina*, ja niiden tiedot tulevat laitepuusta.

Tässä luvussa kirjoitetaan ajuri QEMU:n virt-koneen PL031-
reaaliaikakellolle. Ajuri tekee laitteesta herätysajastimen: käyttäjä
asettaa herätyksen, ja laite keskeyttää, kun aika on kulunut. Luvussa
käsitellään laitteen ja ajurin sitominen sekä rekisterit, ja seuraava
luku käsittelee keskeytykset.

## Ajurimalli

Linuxin ajurimallissa on kolme osapuolta:

- **Väylä** (`bus_type`) tietää, miten sen laitteet löydetään ja miten
  laite ja ajuri sopivat yhteen: platform, I2C, SPI, PCI, USB.
- **Laite** (`struct device`) on yksi löydetty laite resursseineen:
  rekisterialueet, keskeytykset ja laitepuun solmu.
- **Ajuri** (`struct device_driver`) osaa käyttää tietynlaisia
  laitteita.

Kun laite tai ajuri rekisteröidään, väylä vertaa sitä toisen puolen
kaikkiin rekisteröityihin ja kutsuu ajurin `probe`-funktiota jokaiselle
sopivalle laitteelle. Järjestys on vapaa: ajuri voi tulla ennen laitetta
tai laite ennen ajuria. `probe` saa laitteen käyttöönsä, ja `remove`
luopuu siitä, kun laite tai ajuri poistuu.

Laitepuusta ydin luo käynnistyksessä platform-laitteen jokaisesta
solmusta, jolla on `compatible`-ominaisuus ja jonka vanhempi on väylä,
kuten juurisolmu tai `simple-bus`. Poikkeus ovat ARM:n *PrimeCell*-
oheislaitteet, kuten PL011 ja PL031: niiden `compatible`-luettelossa on
`arm,primecell`, ja ne tulevat AMBA-väylälle, joka lukee laitteen
tunnisterekisterit. Ytimen oma `rtc-pl031`-ajuri on AMBA-ajuri.

Tutoriaalin ajuria varten koneen `pl031`-solmu poistetaan ja tilalle
lisätään platform-laite omalla `compatible`-merkkijonolla:

```{.c tiedosto="esimerkit/03-platform/herate.dtsi"}
```

```{.make tiedosto="esimerkit/Makefile" osa="dtb"}
```

Laitepuu puretaan QEMU:lta (`dumpdtb`), muunnetaan tekstiksi, liitetään
lisäykseen ja käännetään takaisin. `/delete-node/` poistaa solmun ja
uusi solmu tulee sen tilalle. Oikeassa laitteessa muutos tehtäisiin
kortin `.dts`-tiedostoon tai päällysteeseen (*overlay*). Tiedoston
syntaksi on käsitelty *Sulautettu Linux* -tutoriaalissa.

## compatible ja sidonta

Ajuri kertoo, mitkä laitteet se tuntee, taulukolla:

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="ajuri"}
```

- **`of_match_table`** luettelee laitepuun `compatible`-merkkijonot.
  Platform-väylä vertaa niitä solmun luetteloon. Ensimmäinen osuma
  voittaa, joten luettelossa tarkin malli on ensin ja yleisempi
  yhteensopiva viimeisenä (`"vendor,piiri-v2", "vendor,piiri"`).
- **`MODULE_DEVICE_TABLE`** kopioi saman taulukon moduulin tietoihin.
  Siitä `depmod` tekee tiedoston `modules.alias`, jonka avulla `udev`
  lataa oikean moduulin laitteen *modaliasin* perusteella.
- **`dev_groups`** luo laitteelle sysfs-attribuutit, kun ajuri sidotaan
  (luku 9).
- **`module_platform_driver`** tekee moduulin alku- ja loppufunktion,
  jotka vain rekisteröivät ja poistavat ajurin.

Laitteen modalias on olemassa jo ennen ajurin latausta:

```{.text tiedosto="esimerkit/03-platform/herate.vaiheet" osa="sidonta"}
```

```{.tuloste tiedosto="esimerkit/testit/03-herate.odotettu" osa="sidonta"}
```

Merkkijonossa on solmun nimi (`N`), tyyppi (`T`, tässä puuttuu) ja
`compatible` (`C`). Lataus kutsuu heti `probe`-funktiota, ja laite
ilmestyy ajurin hakemistoon. Lokirivin alussa on ajurin ja laitteen
nimi, jonka `dev_info` lisää automaattisesti. Laitteen nimi
`9010000.herateajastin` tulee solmun osoitteesta ja nimestä.

## Rekisterit

Laitteen rekisterit kuvataan ytimen virtuaaliosoitteisiin, ja niitä
käytetään vain apufunktioilla `readl` ja `writel` (32 bittiä) tai
niiden muunnelmilla:

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="rekisterit"}
```

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="tunnista"}
```

*Oheislaiteväylät*-tutoriaalissa rekisterit käytettiin
`volatile`-osoittimilla. Ytimessä `readl` ja `writel` tekevät saman ja
lisäksi:

- **Ne järjestävät muistikäytöt.** `writel` takaa, että aiemmat
  kirjoitukset tavalliseen muistiin näkyvät laitteelle ennen
  rekisterikirjoitusta. DMA:ta käyttävä ajuri tarvitsee tätä (luku 6).
  Muunnelmat `readl_relaxed` ja `writel_relaxed` jättävät esteet pois,
  kun järjestyksellä ei ole väliä.
- **Ne tekevät tavujärjestyksen muunnoksen.** Rekisterit ovat
  pienimmän tavun ensin (*little-endian*); `ioread32be` ja
  `iowrite32be` lukevat isoa tavujärjestystä.
- **Ne merkitsevät osoitteen `__iomem`-tyypiksi.** Staattinen
  tarkistin `sparse` (`make C=1`) varoittaa, jos rekisteriosoitetta
  käytetään tavallisena osoittimena.

Rekisterirakenteita (`struct pl031_rekisterit { u32 dr; ... }`) ei
ytimessä käytetä, koska kääntäjä voi lisätä niihin täytettä ja ne
houkuttelevat käyttämään rekisterejä ilman `readl`- ja
`writel`-funktioita. Siirtymät määritellään vakioina.

Tunnisterekisterien tarkistus varmistaa, että laitepuu kuvaa oikeaa
laitetta. PL031:n tunniste on `0x00141031`: osanumero `0x031`,
valmistaja `0x41` (ARM) ja revisio 1. Ajuri vertaa vain osanumeroa ja
valmistajaa, koska uudempi revisio on yhteensopiva.

## probe ja devm

`probe` hakee laitteen resurssit, tarkistaa laitteen, alustaa sen ja
rekisteröi sen käyttäjälle:

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="probe"}
```

Resurssit tulevat laitepuun solmusta:
`devm_platform_ioremap_resource` hakee `reg`-ominaisuuden alueen ja
kuvaa sen, `platform_get_irq` hakee `interrupts`-ominaisuuden
keskeytyksen ja `of_property_read_*` lukevat muut ominaisuudet.
Valinnainen ominaisuus luetaan oletusarvon päälle, koska funktio jättää
muuttujan ennalleen, jos ominaisuutta ei ole.

`devm_`-alkuiset funktiot ovat *hallittuja resursseja*: ydin kirjaa ne
laitteelle ja vapauttaa ne käänteisessä järjestyksessä, kun `probe`
epäonnistuu tai laite irrotetaan. Virhepolku on siksi pelkkä `return`,
eikä `remove`-funktion tarvitse vapauttaa muistia, kuvausta eikä
keskeytystä. `remove` purkaa vain sen, mitä ei tehty `devm_`-
funktioilla, ja pysäyttää laitteen.

`dev_err_probe` tulostaa virheen ja palauttaa virhekoodin. Se tuntee
erityisen virheen `-EPROBE_DEFER`: jos laite tarvitsee resurssia, jota ei
vielä ole, kuten kelloa tai jännitesäädintä, jonka ajuri ladataan
myöhemmin, `probe` palauttaa tämän virheen, ja ydin yrittää uudelleen,
kun uusia ajureita on sidottu. `dev_err_probe` ei tulosta lykkäystä
virheenä vaan kirjaa syyn tiedostoon
`/sys/kernel/debug/devices_deferred`.

## Sitominen ja irrotus käsin

Ajurin hakemiston tiedostot `bind` ja `unbind` sitovat ja irrottavat
laitteen ilman moduulin poistoa:

```{.text tiedosto="esimerkit/03-platform/herate.vaiheet" osa="irrotus"}
```

```{.tuloste tiedosto="esimerkit/testit/03-herate.odotettu" osa="irrotus"}
```

Irrotus on hyvä testi ajurille: jos `remove` jättää jotain jälkeensä,
kuten keskeytyksen päälle tai työn ajastetuksi, uusi sidonta tai
moduulin poisto paljastaa sen. Laitteen voi myös ohjata toiselle
ajurille kirjoittamalla ajurin nimen laitteen tiedostoon
`driver_override`.

## Käytännössä

- **Käytä `devm_`-funktioita aina kun voit.** Virhepolut lyhenevät
  ja yleisin ajurivirhe, unohtunut vapautus virhepolulla, katoaa.
  Varmista silti, että `remove` pysäyttää laitteen ennen kuin `devm`
  vapauttaa keskeytyksen.
- **Lue resurssit laitepuusta, älä kirjoita osoitteita ajuriin.**
  Sama ajuri toimii silloin eri piireissä ja eri osoitteissa.
- **Tarkista laitteen tunniste, jos laitteessa on sellainen.** Väärin
  kirjoitettu laitepuu on yleinen vika uudessa kortissa.
- **Palauta `-EPROBE_DEFER`, kun riippuvuus puuttuu, ja käytä
  `dev_err_probe`-funktiota.** Ajurien latausjärjestykseen ei voi
  luottaa.
- **Kirjoita uudelle laitteelle sidonnan kuvaus.** Ytimeen hyväksytään
  vain laitepuun ominaisuudet, joilla on YAML-skeema hakemistossa
  `Documentation/devicetree/bindings/`, ja `compatible` alkaa
  valmistajan tunnuksella.

## Itsearviointi

- Osaat selittää väylän, laitteen ja ajurin roolit sekä sen, miten
  laitepuun solmusta tulee platform-laite ja miten se sidotaan ajuriin.
- Osaat kirjoittaa platform-ajurin, joka hakee rekisterialueen,
  keskeytyksen ja ominaisuudet laitepuusta ja käyttää rekisterejä
  `readl`- ja `writel`-funktioilla.
- Osaat selittää `devm_`-resurssien vapautusjärjestyksen ja sen, mitä
  `remove`-funktioon silti tarvitaan.
- Osaat sitoa ja irrottaa laitteen sysfsin kautta ja selittää
  `-EPROBE_DEFER`-virheen tarkoituksen.
