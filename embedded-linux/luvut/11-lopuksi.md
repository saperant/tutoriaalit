# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

- **Kaikki on tekstiä versionhallinnassa.** Ytimen fragmentit,
  laitepuu, käynnistimen asetukset, palveluluettelot ja levykuvan
  rakennus. Laitteeseen käsin tehty muutos on vika, joka odottaa
  tapahtumistaan.
- **Rakennus on toistettava.** Lukitut versiot, tarkistetut lähteet,
  kiinteät aikaleimat ja arkistoidut lataukset. Sama lähde tuottaa
  saman kuvan myös vuosien päästä.
- **Tarkista, että pyysit sen, minkä sait.** Kconfig hylkää asetuksia
  hiljaa, laitepuu voi kuvata laitteen ilman ajuria, ja palvelu voi
  käynnistyä olematta valmis. Testaa lopputulos, älä syötettä.
- **Juuri on vain luku -tilassa, ja muuttuva data on erillään.** Laite
  kestää virrankatkoksen, palautuu tehdasasetuksiin ja päivittyy
  atomisesti.
- **Päivitys ja palautus suunnitellaan ensin.** A/B-osiot,
  käynnistyskertojen laskenta ja allekirjoitetut paketit on helppo tehdä
  alussa ja lähes mahdoton lisätä kentällä oleviin laitteisiin.
- **Käynnistys testataan automaattisesti.** Emulaattorissa jokaisesta
  muutoksesta ja oikeilla laitteilla säännöllisesti.
- **Pienennä vasta, kun mittaat.** Poista ytimestä ja juuresta se, mitä
  et tarvitse, mutta säilytä debuggauksen ja vianselvityksen välineet,
  kunnes tiedät, mitä ne maksavat.

## Oikeaan laitteeseen

Kun siirryt QEMU:sta kehityskorttiin, sama polku pätee, mutta jokaisessa
vaiheessa on piirikohtaisia yksityiskohtia:

1. **Sarjakonsoli ensin.** Kytke USB-sarjasovitin kortin konsolinastoihin
   ja tarkista jännitetaso (yleensä 3,3 V; 5 V voi rikkoa piirin). Ilman
   konsolia et näe, mihin käynnistys pysähtyy.
2. **Käynnistin piirin toimittajan tai yhteisön tuesta.** Etsi U-Bootin
   `configs/`-hakemistosta korttisi defconfig. Monessa ARM64-piirissä
   tarvitaan lisäksi TF-A ja piirin muistialustuksen binääri, ja
   käynnistyslevyn osiointi on piirin ROM-käynnistimen määräämä.
3. **Ydin pääkehityshaarasta, jos mahdollista.** Tarkista, onko korttisi
   laitepuu hakemistossa `arch/arm64/boot/dts/`. Jos ei ole, toimittajan
   ytimen versio ja sen päivityspolku kannattaa selvittää ennen piirin
   valintaa.
4. **Laitepuu kortin `.dts`:stä.** Ota käyttöön vain tarvitsemasi
   laitteet ja lisää kortillesi kytketyt komponentit.
5. **Rakennustyökalu kortin valmiista konfiguraatiosta.** Buildrootin
   `configs/` ja Yocton BSP-kerrokset sisältävät useimmille suosituille
   korteille toimivan lähtökohdan.

## Lähteet

- Linux-ytimen dokumentaatio:
  <https://docs.kernel.org/>, erityisesti *The kernel's command-line
  parameters*, *Kernel Build System* (`kbuild`), *Building External
  Modules*, *ramfs, rootfs and initramfs* ja ARM64:n *Booting AArch64
  Linux*.
- Kconfig-kieli: <https://docs.kernel.org/kbuild/kconfig-language.html>.
- U-Bootin dokumentaatio: <https://docs.u-boot.org/>, erityisesti
  *Standard Boot*, *Generic Distro Configuration Concept* (extlinux),
  *Flattened Image Tree* ja QEMU-ohjeet.
- Devicetree Specification:
  <https://www.devicetree.org/specifications/>.
- Laitepuun sidontojen skeemat: ytimen hakemisto
  `Documentation/devicetree/bindings/` ja <https://github.com/devicetree-org/dt-schema>.
- Arm: *Trusted Firmware-A* <https://www.trustedfirmware.org/> ja
  *Arm Power State Coordination Interface* -määrittely (DEN0022).
- QEMU:n dokumentaatio, *'virt' generic virtual platform*:
  <https://www.qemu.org/docs/master/system/arm/virt.html>.
- Buildrootin käsikirja: <https://buildroot.org/downloads/manual/manual.html>.
- Yocto Projectin dokumentaatio: <https://docs.yoctoproject.org/>,
  erityisesti *Yocto Project Quick Build*, *Development Tasks Manual*
  ja *Reference Manual*.
- Bootlinin koulutusmateriaalit *Embedded Linux system development* ja
  *Linux kernel and driver development*, CC BY-SA -lisensoituja:
  <https://bootlin.com/training/>.
- Filesystem Hierarchy Standard 3.0:
  <https://refspecs.linuxfoundation.org/fhs.shtml>.
- systemd:n dokumentaatio: `systemd.service(5)`, `systemd.unit(5)` ja
  `sd_notify(3)`, <https://www.freedesktop.org/software/systemd/man/>.
- BusyBox: <https://busybox.net/> ja `examples/inittab` sen
  lähdekoodissa.
- Päivitysjärjestelmät: SWUpdate <https://sbabic.github.io/swupdate/>,
  RAUC <https://rauc.io/> ja Mender <https://docs.mender.io/>.
- Testaus: LAVA <https://www.lavasoftware.org/>, labgrid
  <https://labgrid.readthedocs.io/> ja KernelCI <https://kernelci.org/>.
- Chris Simmonds ja Frank Vasquez: *Mastering Embedded Linux
  Development*, 4. painos, Packt 2023.
- Karim Yaghmour ym.: *Building Embedded Linux Systems*, 2. painos,
  O'Reilly 2008 (vanha mutta periaatteiltaan ajankohtainen).
