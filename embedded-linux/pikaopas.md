---
title: Sulautettu Linux
subtitle: Pikaopas · työkaluketju, ydin, käynnistys, laitepuu, juuri
---

# Työkaluketju

| Komento | Tarkoitus |
|---------|-----------|
| `aarch64-linux-gnu-gcc -static` | ristiinkäännös ilman kohteen kirjastoja |
| `aarch64-linux-gnu-gcc -dumpmachine` | kääntäjän kohdetripletti |
| `qemu-aarch64 ohjelma` | staattisen ohjelman ajo isännällä |
| `qemu-aarch64 -L /usr/aarch64-linux-gnu` | dynaamisen ohjelman ajo sysrootin kanssa |
| `readelf -h`, `-l`, `-d` | arkkitehtuuri, tulkki, `NEEDED`-kirjastot |

Sudenkuopat: `char` on ARM:ssä etumerkitön, isännän kirjastot vuotavat
(`pkg-config`), `configure` yrittää ajaa testiohjelmia.

# Ydin

| Komento | Tulos |
|---------|-------|
| `make O=k ARCH=arm64 tinyconfig` | pienin ydin |
| `merge_config.sh -m .config frag` | fragmentti mukaan |
| `make olddefconfig` | riippuvuudet ja oletukset |
| `make menuconfig`, haku `/` | symbolin riippuvuudet |
| `make savedefconfig` | minimaalinen defconfig |
| `make Image modules` | ydinkuva ja moduulit |
| `make M=hakemisto modules` | ulkopuolinen moduuli |
| `scripts/extract-ikconfig Image` | asetukset ydinkuvasta |

```{.ini tiedosto="esimerkit/ymparisto/perus.config" osa="konsoli"}
```

Toistettavuus: `KBUILD_BUILD_TIMESTAMP`, `KBUILD_BUILD_USER`,
`KBUILD_BUILD_HOST`. Tarkista aina, että fragmentin rivit ovat
`.config`issa: `depends on` hylkää asetuksen hiljaa.

# Ytimen komentorivi

| Parametri | Merkitys |
|-----------|----------|
| `console=ttyAMA0` | konsoli (PL011) |
| `earlycon` | konsoli ennen ajureita |
| `loglevel=N`, `quiet` | konsolin lokitaso |
| `root=/dev/vda ro rootwait` | pysyvä juuri |
| `init=`, `rdinit=` | init-ohjelma juuresta tai initramfsistä |
| `panic=-1` | uudelleenkäynnistys paniikissa |

# Initramfs ja init

```{.text tiedosto="esimerkit/04-init/initramfs.lista"}
```

`gen_init_cpio -t AIKA lista | gzip -n -9 > initramfs.cpio.gz`.
PID 1: ei saa päättyä (paniikki), perii orvot (`waitpid`), ei kuole
signaaleihin ilman käsittelijää. Kiinnitä `/proc`, `/sys`, `/dev`
(`devtmpfs`), `/run` (`tmpfs`); sammuta `sync()` ja
`reboot(RB_POWER_OFF)`.

# U-Boot

| Komento | Tarkoitus |
|---------|-----------|
| `printenv`, `setenv`, `saveenv` | ympäristömuuttujat |
| `virtio scan`, `mmc list`, `usb start` | laitteiden haku |
| `load virtio 0:1 ${kernel_addr_r} /Image` | tiedosto muistiin |
| `booti kern initrd:${filesize} fdt` | ARM64-ytimen käynnistys |
| `bootflow scan -lb` | standardikäynnistys |
| `dhcp`, `tftp ${kernel_addr_r} Image` | verkkokäynnistys |
| `fdt addr`, `fdt print /chosen` | laitepuun tarkastelu |

```{.text tiedosto="esimerkit/05-uboot/extlinux.conf"}
```

Skripti: `mkimage -A arm64 -T script -C none -d boot.cmd boot.scr`.
Linuxista: `fw_printenv`, `fw_setenv`.

# Laitepuu

| Komento | Tarkoitus |
|---------|-----------|
| `qemu-system-aarch64 -machine dumpdtb=x.dtb ...` | QEMU:n laitepuu |
| `dtc -I dtb -O dts x.dtb` | binääri tekstiksi |
| `dtc -I dts -O dtb -o x.dtb x.dts` | teksti binääriksi |
| `fdtget -t s x.dtb / model` | ominaisuuden luku |
| `dtc -I fs /sys/firmware/devicetree/base` | ytimen näkemä puu |

```{.c tiedosto="esimerkit/06-laitepuu/anturi.dtsi" osa="anturi"}
```

`reg`: solujen määrä vanhemman `#address-cells`/`#size-cells`. GIC:
`<tyyppi numero liipaisu>`, SPI n = keskeytys 32 + n. Ajuri valitaan
`compatible`-listan ensimmäisestä osumasta.

# Palvelut

| Tarve | minit | BusyBox | systemd |
|-------|-------|---------|---------|
| järjestys | luettelo | rcS-skriptit | `After=` |
| valmius | `/run/valmis` | ei | `Type=notify` |
| valvonta | raja ja viive | `respawn` | `Restart=` |
| sammutus | TERM, sitten KILL | `shutdown` | `TimeoutStopSec=` |

# Juuri ja päivitys

- Vain luku -juuri (`ro`), muuttuva data omalla osiolla tai overlayssa:
  `lowerdir=/etc,upperdir=/run/etc/yla,workdir=/run/etc/tyo`.
- Atominen tallennus: väliaikainen tiedosto, `fsync`, `rename`,
  hakemiston `fsync`.
- A/B-osiot, `bootcount`/`bootlimit`/`altbootcmd`, commit toimivan
  käynnistyksen jälkeen (SWUpdate, RAUC, Mender).

# Rakennustyökalut

| Buildroot | Yocto |
|-----------|-------|
| `make x_defconfig`, `make` | `bitbake core-image-minimal` |
| `BR2_EXTERNAL`, `package/*/x.mk` | oma kerros, `x_1.0.bb` |
| `make x-rebuild` | `bitbake -c cleansstate x` |
| `make legal-info` | lisenssiluettelo, SPDX |

# Vianetsintä

| Oire | Tavallinen syy |
|------|----------------|
| ei tulostetta lainkaan | väärä `console=`, puuttuva konsoliajuri; kokeile `earlycon` |
| `unable to open an initial console` | `/dev/console` puuttuu initramfsistä |
| `Unable to mount root fs` | ajuri tai tiedostojärjestelmä puuttuu, väärä `root=`, ei `rootwait` |
| `Attempted to kill init` | init päättyi tai kaatui |
| laite ilman ajuria | `compatible` ei täsmää, `status = "disabled"` |
| ominaisuus puuttuu ytimestä | Kconfig hylkäsi asetuksen (`depends on`) |
| `No such file`, vaikka ohjelma on olemassa | tulkki puuttuu: `readelf -l`, `-d` |
| `Exec format error` | väärä arkkitehtuuri: `readelf -h` |

| Kysymys | Keino |
|---------|-------|
| mitä ohjelma pyytää ytimeltä? | `strace -f -o loki ohjelma`, `qemu-aarch64 -strace` |
| missä se kaatui? | `exception-trace`, `addr2line -f -e ohjelma PC` |
| millä tilalla? | `core_pattern`, `ulimit -c`, `gdb-multiarch ohjelma core` |
| miten se etenee? | `gdbserver :2345 ohjelma`, `target remote laite:2345` |
