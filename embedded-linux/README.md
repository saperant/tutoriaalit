# Sulautettu Linux

Tiivis suomenkielinen tutoriaali Linux-järjestelmän rakentamisesta
sulautettuun laitteeseen: ristiinkääntäminen, ytimen konfigurointi,
initramfs ja init, käynnistysketju ja U-Boot, laitepuu, palvelut,
juuritiedostojärjestelmä ja päivitykset, Buildroot ja Yocto,
käynnistystestit sekä vianetsintä kohteessa. Valmiit dokumentit:
[embedded-linux.pdf](https://saperant.github.io/tutoriaalit/materiaalit/embedded-linux.pdf)
ja pikaopas
[embedded-linux-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/embedded-linux-pikaopas.pdf).

## Sisältö

1. Johdanto – laboratorio: QEMU:n virt-kone, Cortex-A53, ytimen
   rakennusympäristö
2. Ristiinkääntäminen ja työkaluketjut – tripletti, sysroot, glibc,
   musl ja uClibc-ng, staattinen ja dynaaminen linkitys, `qemu-aarch64`
3. Ytimen konfigurointi ja kääntäminen – Kconfig, tinyconfig,
   fragmentit, hylätyt asetukset, toistettava käännös, moduulit
4. Ensimmäinen käynnistys – komentorivi, käynnistysloki, initramfs ja
   `gen_init_cpio`, init ja PID 1
5. Käynnistysketju ja U-Boot – SPL, TF-A, Image-otsake, ympäristö,
   `booti`, levykuva, extlinux.conf, boot.scr, FIT
6. Laitepuu – solmut ja ominaisuudet, `reg`, keskeytykset ja phandlet,
   `compatible` ja ajurin sidonta, `chosen`, päällysteet
7. Palvelut ja init-järjestelmät – valmius, valvonta, sammutus,
   BusyBox init, systemd, vahtikoira
8. Juuritiedostojärjestelmä ja päivitykset – FHS, tiedostojärjestelmät,
   vain luku -juuri, overlayfs, atominen tallennus, A/B-päivitys
9. Buildroot ja Yocto – defconfig, BR2_EXTERNAL-paketti, kerrokset ja
   reseptit, vertailu, lisenssit ja SBOM
10. Käynnistystestit ja jatkuva integraatio – testauksen tasot,
    käynnistystestien ajuri, vikojen tunnistus, CI
11. Vianetsintä kohteessa – käynnistymättömän ohjelman virhekoodit,
    järjestelmäkutsujen jäljitys, ytimen loki ja `addr2line`,
    ydinvedos, `gdbserver` ja `gdb-multiarch`
12. Lopuksi – nyrkkisäännöt, oikeaan laitteeseen, jatkotaidot, lähteet

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Sen Makefile kääntää ARM64-
ytimen Ubuntun ytimen lähteistä (kerran, välimuistiin
`~/.cache/tutoriaalit/embedded-linux`), ristiinkääntää init-ohjelmat ja
palvelut, rakentaa initramfs-arkistot, laitepuut ja levykuvat ilman
pääkäyttäjän oikeuksia, käynnistää jokaisen järjestelmän QEMU:n
virt-koneessa (myös U-Bootin kautta) ja vertaa tulosteet tiedostoihin
`esimerkit/testit/<testi>.odotettu`. Hakemistot on numeroitu lukujen
mukaan. Buildroot- ja Yocto-asetuksia (`esimerkit/09-buildroot/`) ei
ajeta, koska rakennus hakee lähteet verkosta ja kestää tunteja; niiden
viittaukset tarkistetaan. Luvun 11 esimerkit ajavat gdb-istunnon
QEMU:n gdb-palvelinta vasten ja avaavat kohteessa syntyneen
ydinvedoksen isännällä.

`esimerkit/ymparisto/` on uudelleenkäytettävä: `ydin.mk` kääntää ytimen
fragmenteista, `aja-qemu.sh` käynnistää virt-koneen ja
`tarkista-config.sh` tarkistaa, että kaikki pyydetyt ytimen asetukset
otettiin käyttöön. Taito *Linux-laiteajurit* käyttää samaa ympäristöä.

## Rakentaminen

```text
make testaa   # rakenne ja esimerkit (esimerkit/Makefile)
make pdf      # tutoriaali ja pikaopas
```

Tarvitaan `linux-source-6.8.0`, `gcc-aarch64-linux-gnu`,
`libc6-dev-arm64-cross`, `qemu-system-arm`, `qemu-user`, `u-boot-qemu`,
`u-boot-tools`, `device-tree-compiler`, `flex`, `bison`, `bc`,
`libssl-dev`, `libelf-dev`, `cpio`, `kmod`, `e2fsprogs`,
`gdb-multiarch` sekä ruff, mypy ja ShellCheck. Ensimmäinen ajo purkaa ytimen lähteet ja kääntää
ytimen, mikä kestää useita minuutteja ja vie noin 2 Gt levyä.
Kehityskontissa (`.devcontainer/embedded-linux`) paketit ovat valmiina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
