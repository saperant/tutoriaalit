---
title: Linux-laiteajurit
subtitle: Pikaopas · moduulit, laitteet, keskeytykset, DMA, väylät, virranhallinta, vianetsintä
---

# Moduuli

| Asia | Tapa |
|------|------|
| käännös | `Kbuild`: `obj-m := a.o`; `make -C $KDIR M=$PWD modules` |
| alku ja loppu | `module_init(f)`, `module_exit(g)`, `__init`, `__exit` |
| parametri | `module_param(nimi, int, 0644)`, `module_param_array` |
| vienti | `EXPORT_SYMBOL_GPL(f)`; käyttäjä ladataan viejän jälkeen |
| lisenssi | `MODULE_LICENSE("GPL")` pakollinen |
| tiedot | `modinfo a.ko`: depends, vermagic, parm |
| tila | `/sys/module/a/{parameters,holders,refcnt}` |
| lataus | `modprobe` (riippuvuudet), `insmod`, `finit_module` |

Alkufunktio palauttaa 0 tai `-EVIRHE`; virhepolku siivoaa
`goto`-ketjulla. Tahrat: `/proc/sys/kernel/tainted` (`O` 4096, `D` 128,
`P` 1). `pr_fmt` nimeää lokirivit.

# Merkkilaite

```{.c tiedosto="esimerkit/02-merkkilaite/jono.c" osa="fops"}
```

| Vaihe | Funktio |
|-------|---------|
| numerot | `alloc_chrdev_region` / `unregister_chrdev_region` |
| luokka | `class_create` / `class_destroy` |
| cdev | `cdev_init`, `cdev_add` / `cdev_del` |
| tiedosto | `device_create` / `device_destroy` |
| yksi laite | `misc_register` / `misc_deregister` |

Luku: tarkista ehto lukossa, `O_NONBLOCK` → `-EAGAIN`, nuku lukon
ulkopuolella `wait_event_interruptible`, signaali → `-ERESTARTSYS`,
kopioi `copy_to_user` → `-EFAULT`. `poll`: `poll_wait` + maski.
`ioctl`: `_IOR(magia, nro, tyyppi)`, tuntematon → `-ENOTTY`.

# Platform-ajuri

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="ajuri"}
```

| Resurssi | Funktio |
|----------|---------|
| rekisterit | `devm_platform_ioremap_resource(pdev, 0)` |
| keskeytys | `platform_get_irq`, `devm_request_threaded_irq` |
| ominaisuus | `of_property_read_u32`, `of_property_read_string` |
| muisti | `devm_kzalloc` |
| tila | `platform_set_drvdata`, `dev_get_drvdata` |
| virhe | `return dev_err_probe(dev, err, "...")` |

`readl`/`writel` (estein), `*_relaxed` (ilman), `ioread32be`.
Riippuvuus puuttuu → `-EPROBE_DEFER` (`debug/devices_deferred`). Käsin: `bind`, `unbind`,
`driver_override` ajurin ja laitteen hakemistoissa.

# Keskeytykset ja lukot

| Paluuarvo | Merkitys |
|-----------|----------|
| `IRQ_NONE` | ei tämän laitteen |
| `IRQ_HANDLED` | käsitelty |
| `IRQ_WAKE_THREAD` | aja keskeytyssäie |

Yläpuolisko: tarkista, kuittaa, ei nukkumista. Säie tai työjono saa
nukkua. `IRQF_ONESHOT`, kun kuittaus vaatii väylää.

| Konteksti | Lukko |
|-----------|-------|
| vain prosessi | `mutex` |
| keskeytys | `spin_lock` |
| prosessi + keskeytys | `spin_lock_irqsave` |
| laskuri | `atomic_t`, `READ_ONCE` |

Työ: `INIT_DELAYED_WORK`, `mod_delayed_work`,
`cancel_delayed_work_sync` ennen vapautusta.

# DMA

| Tarve | Funktio |
|-------|---------|
| maski | `dma_set_mask_and_coherent(dev, DMA_BIT_MASK(n))` |
| ohjausrakenne | `dma_alloc_coherent`, `dmam_alloc_coherent` |
| data | `dma_map_single(dev, p, n, suunta)` + `dma_mapping_error` |
| palautus CPU:lle | `dma_unmap_single`, `dma_sync_single_for_cpu` |
| hajautettu | `dma_map_sg` |
| DMA-ohjain | `dma_request_chan`, `dmaengine_prep_slave_sg` |

Ei pinon puskureita. Laitepuun `dma-coherent`: ei välimuistitoimia.

# I2C ja SPI

| Asia | I2C | SPI |
|-|-----|-----|
| ajuri | `i2c_driver`, `module_i2c_driver` | `spi_driver`, `module_spi_driver` |
| laite | `i2c_client` (`addr`) | `spi_device` (`chip_select`) |
| siirto | `i2c_smbus_*`, `i2c_transfer` | `spi_sync_transfer`, `spi_write_then_read` |
| rekisterit | `devm_regmap_init_i2c` | `devm_regmap_init_spi` |
| käsin | `echo nimi 0x49 > new_device` | `spi_new_device` |
| käyttäjätila | `/dev/i2c-N` | `/dev/spidevB.C` |

SMBus-sana on pienin tavu ensin (`REGMAP_ENDIAN_LITTLE`). Testiväylä:
`i2c-stub chip_addr=0x48,0x49`.

# Resurssit ja virranhallinta

| Asia | Tapa |
|------|------|
| kello | `devm_clk_get`, `clk_set_rate`, `clk_prepare_enable` |
| jännite, GPIO | `devm_regulator_get`, `devm_gpiod_get` (looginen arvo) |
| käyttö | `pm_runtime_resume_and_get` … `pm_runtime_put_autosuspend` |
| lepotila | `DEFINE_RUNTIME_DEV_PM_OPS`; testi `/sys/power/pm_test` |

# sysfs ja debugfs

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="debugfs"}
```

sysfs: yksi arvo tiedostoa kohden, `DEVICE_ATTR_RO/RW`, `sysfs_emit`,
`kstrtou32`, `ATTRIBUTE_GROUPS` + `dev_groups`, `BIN_ATTR_RW`.
Dokumentoi `Documentation/ABI/`. debugfs: ei vakaa, paluuarvoja ei
tarkisteta, `debugfs_remove_recursive`.

# Vianetsintä

| Väline | Käyttö |
|--------|--------|
| `dev_dbg` + dyndbg | `echo 'module m +p' > /proc/dynamic_debug/control`, `m.dyndbg=+p` |
| ftrace | `set_ftrace_filter` `:mod:m`, tracer `function` |
| oops | `pc`, `lr`, `Call trace`; `scripts/faddr2line m.ko f+0xc/0x14` |
| lockdep | `PROVE_LOCKING`: lukkojärjestys |
| nukkuminen | `DEBUG_ATOMIC_SLEEP`: mutex spinlockissa |
| muisti | KASAN, KFENCE, kmemleak |
| gdb | QEMU `-s -S`, `vmlinux`, `lx-symbols` |

Ytimen lokissa ASCII: `/dev/kmsg` näyttää muut tavut muodossa `\xHH`.
