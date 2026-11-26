# Linux-laiteajurit

Tiivis suomenkielinen tutoriaali Linux-ytimen laiteajureiden
kirjoittamisesta: moduulit, merkkilaitteet, platform-ajurit ja laitepuu,
keskeytykset ja lukitus, DMA, I2C- ja SPI-ajurit, kellot, säätimet ja
GPIO-linjat, virranhallinta, sysfs ja debugfs sekä ytimen vianetsintä. Valmiit dokumentit:
[linux-ajurit.pdf](https://saperant.github.io/tutoriaalit/materiaalit/linux-ajurit.pdf)
ja pikaopas
[linux-ajurit-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/linux-ajurit-pikaopas.pdf).

## Sisältö

1. Johdanto – ydintilan ohjelmointi, laboratorio, testit initinä
2. Ytimen moduulit – Kbuild, parametrit, symbolien vienti,
   riippuvuudet, viittauslaskenta, lisenssi ja tahrat
3. Merkkilaiteajurit – laitenumerot, `cdev`, `file_operations`, estävä
   luku, `poll`, `ioctl`, misc-laitteet, `mmap`
4. Platform-ajurit ja laitepuu – ajurimalli, `compatible`, rekisterit,
   `probe`, `devm`, sitominen ja irrotus
5. Keskeytykset ja lukitus – keskeytyksen polku, ylä- ja alapuolisko,
   työjonot, lukot konteksteittain, sysfs-attribuutit, viiveet ja
   ajastimet
6. DMA ytimessä – DMA-maski, koherentti muisti, virtauskuvaus,
   välimuistin koherenssi, dmaengine
7. I2C-ajurit – alijärjestelmä, SMBus, regmap, hwmon, `i2c-stub`
8. SPI-ajurit – siirrot ja viestit, ohjaimen ja laitteen ajuri, spidev
9. Kellot, jännitteet ja GPIO-linjat – resurssit laitepuussa,
   kytkentäjärjestys, lykätty sidonta, kellon tarjoaja, GPIO-keskeytys
10. Virranhallinta – käyttölaskuri ja lepoviive, tilat sysfsissä,
    järjestelmän lepotila ja sen testitila, herätyslähteet
11. sysfs ja debugfs – binääriattribuutit, debugfs, rajapinnan valinta
12. Ytimen vianetsintä – lokitasot, dynaaminen debug, ftrace,
    kaatumisilmoitus, lockdep ja muut tarkistimet
13. Lopuksi – nyrkkisäännöt, oikeaan laitteeseen, jatkotaidot, lähteet

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Sen Makefile kääntää
ARM64-ytimen Ubuntun ytimen lähteistä (kerran, välimuistiin
`~/.cache/tutoriaalit/linux-ajurit`), kääntää moduulit ja staattiset
testiohjelmat, kokoaa jokaiselle testille oman initramfs-arkiston,
käynnistää sen QEMU:n virt-koneessa ja vertaa tulosteen tiedostoon
`esimerkit/testit/<testi>.odotettu`. Jokaisen testijärjestelmän init on
vaiheajuri `esimerkit/kayttaja/ajo.c`, joka suorittaa testin
`.vaiheet`-tiedoston komennot.

Laitteet ovat QEMU:n virt-koneen omia: PL031-reaaliaikakello
(platform-ajuri ja keskeytykset) ja fw_cfg (DMA). I2C-väylän tarjoaa
ytimen testimoduuli `i2c-stub`, ja SPI-ohjain ja sen muistipiiri ovat
tämän tutoriaalin ohjelmallisia malleja. Kellojen, säätimien ja
GPIO-linjojen esimerkki käyttää ytimen GPIO-simulaattoria ja kiinteää
säädintä sekä omaa kellon tarjoajaa. Ympäristö
(`esimerkit/ymparisto/`) on kopioitu tutoriaalista *Sulautettu Linux*,
ja ytimeen on lisätty fragmentti `ajurit.config`.

## Rakentaminen

```text
make testaa   # rakenne ja esimerkit (esimerkit/Makefile)
make pdf      # tutoriaali ja pikaopas
```

Tarvitaan `linux-source-6.8.0`, `gcc`, `gcc-aarch64-linux-gnu`,
`libc6-dev-arm64-cross`, `qemu-system-arm`, `device-tree-compiler`,
`flex`, `bison`, `bc`, `libssl-dev`, `libelf-dev`, `cpio`, `kmod` ja
ShellCheck. Ensimmäinen ajo purkaa ytimen lähteet ja kääntää ytimen,
mikä kestää useita minuutteja ja vie noin 2 Gt levyä; sen jälkeen
kaikki testit kestävät alle minuutin. Kehityskontissa
(`.devcontainer/linux-ajurit`) paketit ovat valmiina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
