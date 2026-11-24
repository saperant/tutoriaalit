# Käynnistysketju ja U-Boot

Edellisessä luvussa QEMU latasi ytimen ja initramfsin suoraan muistiin
ja hyppäsi ytimeen. Oikeassa laitteessa kukaan ei tee tätä valmiiksi:
virran kytkeytyessä prosessori alkaa suorittaa piirin sisäistä
ROM-koodia, ja ytimeen asti päästään usean vaiheen kautta. Jokainen
vaihe alustaa vähän lisää laitteistoa ja lataa seuraavan.

## Vaiheet

| Vaihe | Missä | Tehtävä |
|-------|-------|---------|
| ROM-käynnistin | piirin sisäinen ROM | lukee käynnistyslähteen nastoista tai sulakkeista, lataa SPL:n piirin SRAMiin |
| SPL | SRAM (kymmeniä tai satoja kt) | alustaa kellot ja DRAMin, lataa seuraavat vaiheet DRAMiin |
| TF-A (BL31) | DRAM, EL3 | ARM64:n turvamonitori: PSCI (virranhallinta, ytimien käynnistys), TrustZone |
| U-Boot | DRAM, EL2 tai EL1 | ajurit levyille ja verkolle, valikko, skriptit, ytimen lataus |
| Linux | DRAM, EL1 | ydin ja ajurit |
| init | käyttäjätila | palvelut |

*SPL* (Secondary Program Loader) on U-Bootista käännetty karsittu versio,
joka mahtuu piirin sisäiseen SRAMiin. *TF-A* (Trusted Firmware-A) on
ARM:n viitetoteutus laiteohjelmistolle, joka jää ajoon ytimen alle:
kun ydin sammuttaa koneen tai käynnistää toisen prosessoriytimen, se
kutsuu TF-A:n PSCI-rajapintaa (Power State Coordination Interface).
QEMU:n virt-koneessa QEMU itse toteuttaa PSCI:n, ja ROM-vaiheen tekee
QEMU lataamalla annetun tiedoston muistiin.

Turvallinen käynnistys rakentuu tämän ketjun päälle: jokainen vaihe
tarkistaa seuraavan allekirjoituksen ennen kuin hyppää siihen, ja
ensimmäisen vaiheen julkinen avain on poltettu piirin sulakkeisiin.
Siitä tarkemmin taidossa *Sulautettujen järjestelmien tietoturva*.

## ARM64-ytimen Image-otsake

Käynnistin ei tiedä ytimestä muuta kuin sen, mitä ydinkuvan alussa
oleva 64 tavun otsake kertoo. Sen muoto on määritelty ytimen
dokumentissa `Documentation/arch/arm64/booting.rst`:

```{.python tiedosto="esimerkit/04-ydin/otsake.py" osa="otsake"}
```

```{.tuloste tiedosto="esimerkit/testit/04-otsake.odotettu"}
```

Taikaluku `ARMd` kertoo käynnistimelle, että kyseessä on ARM64-ydin.
Ensimmäinen sana on hyppykäsky ytimen alkuun; jos ydin on käännetty
EFI-tuella, sen paikalla on PE/COFF-tunniste `MZ`, ja sama kuva
käynnistyy myös UEFI-ohjelmana. `text_offset` ja `image_size` kertovat,
mihin kohtaan muistia ydin on ladattava ja paljonko tilaa se tarvitsee
purkautuessaan, sillä muuttujat (`.bss`) eivät ole tiedostossa.

Käynnistimen on lisäksi välitettävä ytimelle laitepuun osoite
rekisterissä `x0`, ja välimuistit ja muistinhallintayksikkö on oltava
pois päältä. Tämä sopimus on *käynnistysprotokolla*; U-Bootin komento
`booti` toteuttaa sen.

## U-Boot

U-Boot on sulautettujen järjestelmien yleisin käynnistin. Siinä on
ajurit tallennusvälineille (eMMC, SD, NAND, SPI-flash, USB, virtio),
verkolle (TFTP, DHCP, NFS), tiedostojärjestelmille (FAT, ext4), komentotulkki
ja ympäristömuuttujat. Ubuntun `u-boot-qemu`-paketissa on valmiiksi
käännetty U-Boot QEMU:n ARM64-koneelle. QEMU käynnistää sen
valitsimella `-bios` ytimen sijaan.

Käynnistyksen alussa U-Boot lataa *ympäristön*: avain–arvo-parit, jotka
ohjaavat sen toimintaa. Ympäristö tallennetaan tavallisesti flashin
omalle alueelle tarkistussummineen. QEMU:ssa alue on tyhjä, joten
U-Boot ilmoittaa *bad CRC, using default environment* ja käyttää
käännöksen oletusarvoja. Tärkeimmät muuttujat:

| Muuttuja | Merkitys |
|----------|----------|
| `bootcmd` | komento, joka ajetaan, kun automaattikäynnistyksen odotus päättyy |
| `bootdelay` | odotusaika sekunteina; näppäinpainallus keskeyttää |
| `bootargs` | ytimen komentorivi |
| `kernel_addr_r`, `ramdisk_addr_r`, `fdt_addr_r` | muistiosoitteet, joihin tiedostot ladataan |
| `fdtcontroladdr` | U-Bootin oman laitepuun osoite |
| `filesize` | viimeksi ladatun tiedoston koko |

Linuxista ympäristöä luetaan ja muutetaan komennoilla `fw_printenv` ja
`fw_setenv` (paketti `libubootenv`), joille kerrotaan
asetustiedostossa, missä ympäristö on. Päivitysjärjestelmät käyttävät
tätä vaihtaessaan käynnistettävää osiota (luku 8).

## Käynnistys käsin

Kun automaattinen käynnistys keskeytetään, U-Boot antaa kehotteen
`=>`. Seuraava vaihetiedosto ohjaa U-Bootia samoilla komennoilla, jotka
ihminen kirjoittaisi sarjakonsoliin; sen ajaa luvun 10
käynnistystestien ajuri:

```{.text tiedosto="esimerkit/06-uboot/kasin.vaiheet"}
```

```{.tuloste tiedosto="esimerkit/testit/06-kasin.odotettu"}
```

Komento `virtio scan` etsii virtio-laitteet, `load` lukee tiedoston
osion tiedostojärjestelmästä annettuun osoitteeseen (`virtio 0:1` on
ensimmäisen virtio-levyn ensimmäinen osio) ja asettaa muuttujan
`filesize`. `booti` saa kolme argumenttia: ytimen osoitteen,
initramfsin osoitteen ja koon sekä laitepuun osoitteen. Tässä laitepuu
on se, jonka QEMU antoi U-Bootille; oikeassa laitteessa laitepuu
ladataan levyltä samalla tavalla kuin ydin.

## Levykuva

U-Boot tarvitsee levyn, jolla on osiotaulu ja tiedostojärjestelmä.
Levykuva tehdään ilman pääkäyttäjän oikeuksia kahdessa vaiheessa.
Ensin pieni Python-ohjelma kirjoittaa MBR-osiotaulun:

```{.python tiedosto="esimerkit/06-uboot/levykuva.py" osa="osio"}
```

Sitten `mke2fs` tekee osioon ext4-tiedostojärjestelmän ja kopioi siihen
hakemiston sisällön valitsimella `-d`. Valitsin `-E offset` sijoittaa
tiedostojärjestelmän osion alkuun:

```{.make tiedosto="esimerkit/Makefile" osa="levy"}
```

Ympäristömuuttuja `E2FSPROGS_FAKE_TIME` kiinnittää tiedostojärjestelmän
aikaleimat ja `-U clear` sen tunnisteen, joten levykuvakin on
toistettava. Työkalut kuten `genimage` ja Buildrootin
`post-image`-skriptit tekevät saman monelle osiolle kerralla.

## Standardikäynnistys: extlinux.conf

Uusissa U-Booteissa `bootcmd` käynnistää *standardikäynnistyksen*
(bootstd): U-Boot käy läpi käynnistyslaitteet ja etsii niiltä tunnettuja
käynnistystapoja. Yleisin on `extlinux.conf`, sama muoto, jota
PC-maailman Syslinux käyttää:

```{.text tiedosto="esimerkit/06-uboot/extlinux.conf"}
```

Tiedosto sijoitetaan osion hakemistoon `/extlinux/`, ja sen viereen ydin
ja initramfs. Kun laitepuu halutaan ladata levyltä, lisätään rivi
`fdt /polku/laite.dtb`. U-Bootin tulosteesta suodatetaan käynnistystapa
ja ladatut tiedostot:

```{.tuloste tiedosto="esimerkit/testit/06-extlinux.odotettu"}
```

Etu on, että käynnistysvalikko on tavallinen tekstitiedosto
juuritiedostojärjestelmän rinnalla: sitä voi muuttaa Linuxista käsin,
eikä U-Bootin ympäristöön tarvitse koskea.

## Käynnistysskripti: boot.scr

Kun käynnistys tarvitsee logiikkaa, kuten päivitysosion valinnan tai
laitteistoversion tunnistuksen, käytetään U-Bootin skriptiä. Se on
U-Bootin komentoja tekstitiedostossa:

```{.text tiedosto="esimerkit/06-uboot/boot.cmd"}
```

U-Boot ei lue tekstitiedostoa sellaisenaan, vaan skripti käännetään
`mkimage`-työkalulla otsakkeelliseksi kuvaksi, jossa on tarkistussumma:

```{.make tiedosto="esimerkit/Makefile" osa="mkimage"}
```

`mkimage` kirjoittaa otsakkeeseen luontiajan, jonka
`SOURCE_DATE_EPOCH` kiinnittää. Standardikäynnistys löytää tiedoston
`/boot.scr` ja ajaa sen:

```{.tuloste tiedosto="esimerkit/testit/06-skripti.odotettu"}
```

## FIT-kuvat ja verkkokäynnistys

*FIT* (Flattened Image Tree) on `mkimage`-muoto, joka pakkaa ytimen,
laitepuut ja initramfsin yhteen tiedostoon ja kuvaa ne laitepuun
syntaksilla. Siihen voi koota usean laiteversion laitepuut ja
*konfiguraatiot*, jotka yhdistävät oikean ytimen ja laitepuun, ja sen
voi allekirjoittaa. U-Boot tarkistaa allekirjoituksen julkisella
avaimella, joka on sen omassa laitepuussa. Tämä on U-Bootin
*verified boot*, ja se on yleisin tapa toteuttaa luottamusketjun
U-Bootista ytimeen asti.

Kehitysvaiheessa ydin ladataan usein verkosta: `dhcp` hakee osoitteen
ja `tftp ${kernel_addr_r} Image` lataa ytimen TFTP-palvelimelta, ja
juuri voidaan kiinnittää NFS:llä (`root=/dev/nfs nfsroot=...`). Uusi
ydin on silloin testattavissa sekunneissa ilman levyn kirjoittamista.
QEMU:n käyttäjätilan verkko sisältää TFTP-palvelimen
(`-netdev user,tftp=hakemisto`), joten saman voi kokeilla ilman omaa
palvelinta.

## Käytännössä

- **Tee käynnistyksestä tekstiä.** `extlinux.conf` ja skripti ovat
  versionhallittavia ja katselmoitavia. Ympäristöön kirjoitettu
  `bootcmd` on näkymätön tila, joka vaihtelee laitteittain.
- **Lukitse U-Bootin ympäristö tuotannossa.** Hyökkääjä, joka pääsee
  sarjakonsoliin ja keskeyttää käynnistyksen, voi antaa ytimelle
  komentorivin `init=/bin/sh`. Aseta `bootdelay=0` tai `-2`, käytä
  käännösaikaista oletusympäristöä ja allekirjoitettuja FIT-kuvia.
- **Pidä ydin, laitepuu ja initramfs samassa paketissa.** Laitepuu
  kuuluu ytimeen: uusi ydin voi tarvita uuden laitepuun. FIT-kuva tai
  saman hakemiston tiedostot yhdessä `extlinux.conf`in kanssa pitävät ne
  yhteensopivina.
- **Käytä verkkokäynnistystä kehityksessä.** TFTP ja NFS lyhentävät
  muutos–testi-kierroksen minuuteista sekunteihin.
- **Tunne laitteesi palautustila.** Useimmissa piireissä ROM-käynnistin
  voi ladata ohjelman USB:n tai sarjaportin kautta, kun flash on tyhjä
  tai rikki. Tarkista, miten tila otetaan käyttöön, ennen kuin laite
  ensimmäisen kerran ei käynnisty.

## Itsearviointi

- Osaat kuvata ARM64-laitteen käynnistysketjun ROM-käynnistimestä
  init-prosessiin ja kertoa, mitä SPL, TF-A ja U-Boot tekevät.
- Osaat lukea ARM64-ytimen Image-otsakkeen ja kertoa, mitä käynnistin
  siitä tarvitsee.
- Osaat käynnistää ytimen U-Bootista käsin komennoilla `load` ja
  `booti` ja käyttää ympäristömuuttujia.
- Osaat tehdä levykuvan, jossa on osiotaulu ja ext4-osio, ilman
  pääkäyttäjän oikeuksia.
- Osaat käynnistää järjestelmän `extlinux.conf`illa ja
  `mkimage`lla tehdyllä skriptillä sekä kertoa, mihin FIT-kuvia
  käytetään.
