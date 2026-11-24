# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

- **Käytä alijärjestelmää äläkä tee omaa.** Anturi kuuluu hwmoniin tai
  IIO:hon, flash MTD:hen, painike inputiin ja DMA-ohjain dmaengineen.
  Alijärjestelmä antaa valmiin käyttäjätilan rajapinnan, työkalut ja
  muiden ajureiden kokemuksen.
- **Laite tulee laitepuusta.** Ajuri ei tunne osoitteita, keskeytysten
  numeroita eikä kellotaajuuksia; ne luetaan laitteen resursseista, ja
  puuttuva riippuvuus on `-EPROBE_DEFER`.
- **Resurssit hallitusti.** `devm_`-funktiot poistavat
  virhepolkujen vuodot, ja `remove` pysäyttää laitteen ja peruu työt.
- **Konteksti ratkaisee lukon.** Keskeytyksessä ei nukuta: spinlock ja
  `spin_lock_irqsave` jaetulle tilalle, mutex muualla. Nukkuminen aina
  lukon ulkopuolella.
- **Käyttäjän data ja laitteen data ovat vieraita.** Käyttäjän muisti
  vain `copy_*_user`-funktioilla, laitteen DMA-puskurit omistussääntöjen
  mukaan ja laitteen tunniste tarkistetaan.
- **Käyttäjätilan rajapinta on ikuinen.** sysfs-attribuutit ja
  `ioctl`-rakenteet dokumentoidaan ja pidetään yhteensopivina; debugfs
  on kehittäjälle.
- **Tarkistimet päälle kehityksessä.** lockdep, KASAN, UBSAN ja
  nukkumistarkistus löytävät virheet ennen kuin ne löytyvät kentältä.

## Oikeaan laitteeseen

Tämän tutoriaalin ajurit toimivat QEMU:ssa. Oikeassa laitteessa polku on
sama, mutta laitteisto ei ole yhtä armollinen:

1. **Laitteen tiedot ensin.** Lue piirin datalehdestä rekisterit,
   ajoitus, käynnistysjärjestys ja virhetilat ennen koodaamista. Etsi
   ytimestä ajuri samanlaiselle piirille: usein valmistaja on käyttänyt
   samaa lohkoa ennenkin.
2. **Kellot, jännitteet ja nastat.** Oikea oheislaite tarvitsee
   kellonsa (`devm_clk_get_enabled`), jännitteensä (`regulator`),
   nastojen asetukset (`pinctrl`) ja usein reset-linjan. Puuttuva kello
   näkyy rekistereinä, jotka lukevat nollaa.
3. **Virranhallinta.** Ajuri sammuttaa laitteen, kun sitä ei käytetä
   (`pm_runtime`), ja tallentaa ja palauttaa tilan lepotilassa
   (`suspend`- ja `resume`-funktiot).
4. **Mittaa väylältä.** Logiikka-analysaattori tai oskilloskooppi
   kertoo, lähteekö SPI-viesti ja vastaako I2C-piiri. Ajurin
   jäljitystapahtumat (`events/i2c`, `events/spi`) näyttävät saman
   ytimen puolelta.
5. **Ytimeen lähettäminen.** Ajuri tarkistetaan skriptillä
   `scripts/checkpatch.pl`, sidonnan YAML-skeema komennolla `make
   dt_binding_check`, ja muutokset lähetetään sähköpostilla
   alijärjestelmän ylläpitäjälle (`scripts/get_maintainer.pl`).
   Ensimmäinen kierros tuo aina palautetta.

## Lähteet

- Linux-ytimen dokumentaatio: <https://docs.kernel.org/>, erityisesti
  *Driver implementer's API guide* (ajurimalli, `devm`, DMA-rajapinta,
  regmap, keskeytykset, sysfs), *Linux kernel coding style*,
  *Building External Modules* ja *Dynamic debug*.
- DMA-rajapinta: *Dynamic DMA mapping using the generic device*
  (`Documentation/core-api/dma-api.rst`) ja *DMA-API-HOWTO*
  (`Documentation/core-api/dma-api-howto.rst`).
- I2C ja SPI: `Documentation/i2c/` (erityisesti *Implementing I2C
  device drivers* ja *i2c-stub*) ja `Documentation/spi/`
  (*Overview of Linux kernel SPI support*).
- Jäljitys ja vianetsintä: *ftrace - Function Tracer*
  (`Documentation/trace/ftrace.rst`), *Bug hunting*
  (`Documentation/admin-guide/bug-hunting.rst`), *Runtime locking
  correctness validator* (`Documentation/locking/lockdep-design.rst`)
  ja *The Kernel Address Sanitizer*.
- sysfs-rajapinnat: `Documentation/ABI/` ja *sysfs - The filesystem for
  exporting kernel objects*.
- Laitepuun sidonnat: `Documentation/devicetree/bindings/` ja
  *Writing Devicetree Bindings in json-schema*.
- ARM: *PrimeCell Real Time Clock (PL031) Technical Reference Manual*
  (DDI 0224) ja *Arm Generic Interrupt Controller Architecture
  Specification*.
- QEMU: *QEMU Firmware Configuration (fw_cfg) Device*
  (`docs/specs/fw_cfg.rst`) ja *'virt' generic virtual platform*.
- Bootlinin koulutusmateriaali *Linux kernel and driver development*,
  CC BY-SA -lisensoitu: <https://bootlin.com/training/>.
- Jonathan Corbet, Alessandro Rubini ja Greg Kroah-Hartman: *Linux
  Device Drivers*, 3. painos (O'Reilly 2005, CC BY-SA 2.0). Rajapinnat
  ovat osin vanhentuneita, mutta käsitteet ovat ennallaan.
- LWN.net: ytimen kehityksen viikkokatsaukset ja artikkelisarjat,
  esimerkiksi *Driver porting* ja *The managed resource API*.
