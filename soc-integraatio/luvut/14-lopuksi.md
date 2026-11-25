# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Muistikartta on rajapinta.** Se suunnitellaan, katselmoidaan ja
   versioidaan, ja jokainen tyhjä osoite vastaa virheellä.
2. **Yksi lähde.** Rekisterit, muistikartta ja niistä johdetut RTL,
   otsakkeet ja dokumentaatio generoidaan samasta kuvauksesta.
3. **Väylähierarkia.** Nopea väylä muisteille ja isännille, APB
   rekisteriliitännöille sillan takana.
4. **VALID ei odota READYä.** Ja kun VALID on noussut, se pysyy
   kättelyyn asti.
5. **Jokaiseen pyyntöön vastataan.** Myös virheeseen; oletusorja ja
   aikakatkaisu varmistavat sen.
6. **Kuittaa keskeytyksen syy.** Tasoliipaistu keskeytys kuitataan
   oheislaitteessa ennen keskeytysohjaimen valmis-kirjoitusta.
7. **Alueiden ylitykset tunnettuihin lohkoihin.** Kellotus-, nollaus- ja
   tehoalueiden rajat kootaan sovittuihin soluihin ja tarkistetaan
   työkalulla.
8. **Tarkistimet kaikkialle ja negatiiviset testit tarkistimille.**
9. **Integroi lohko kerrallaan.** Tunnisterekisterin luku ennen
   toimintoja, toiminnot ennen kuormitusta.
10. **Älä muokkaa IP:tä.** Sovitukset kääreisiin ja parametreihin.

## Mallit ja niiden paikat

| Malli | Tässä tutoriaalissa |
|-------|---------------------|
| Väyläsilta | `silta.sv` (ydin → AXI4-Lite), `apb_silta.sv` (AXI4-Lite → APB) |
| Oletusorja | `kytkin.sv`, tila `VASTAUS` |
| Vuorotteleva välittäjä | `kytkin.sv`, `pyytaja` ja `vuoro` |
| Generoitu rekisterilohko ja kääre | `gen/gpio_regs.sv` ja `rtl/gpio.sv` |
| W1C-tilarekisteri | GPIO:n REUNAT, DMA:n TILA |
| Lunastus ja valmis (claim/complete) | `plic.sv` ja `keskeytykset.c` |
| MMIO-rakenne `volatile`-kentin | `soc.h`, `gen/*_regs.h` |
| Protokollatarkistin | `axil_tarkistin.sv` ja negatiivinen testi `huono_orja.sv` |
| Tehoalueen sekvenssi ja eristys | `tehoalue.sv` |
| Väyläisäntä testissä ja testikääre | `cocotb-testit/axil.py`, `apb.py`, `tb/cocotb_*.sv` |
| Mutaatio testin tehon mittana | luku 13, `--mutaatio` |

## Jatkotaidot

- *ASIC-toteutus*: synteesi, ajoitusanalyysi, testattavuus ja
  sijoittelu – miten SoC:n RTL:stä tulee piiri.
- *FPGA-toteutus*: SoC:n kokoaminen FPGA:lle ja testaus kortilla.
- *Laitteiston verifiointi*: rajoitettu satunnaistus, kattavuus,
  SVA ja formaali tarkistus, UVM.
- *Mikrokontrollerit ja bare-metal-ohjelmointi* ja *Sulautettu Linux*:
  ohjelmisto oikean SoC:n päällä, laitepuu ja ajurit.
- *Sulautettujen järjestelmien tietoturva*: turvallinen käynnistys,
  väylän palomuurit ja IOMMU.
- *Arkkitehtuurin mallinnus ja suunnittelutilan tutkiminen*: väylien
  ja muistien suorituskyvyn mallintaminen ennen RTL:ää.
- *EDA-työkaluketjujen automatisointi*: luvun 8 rekisterikuvaus
  bittikenttineen, generaattorin rakentaminen, tuotetut testit ja CI.
- *Laitteiston kuvausstandardit (SystemRDL, IP-XACT)*: sama
  standardimuodoilla ja valmiilla generaattoreilla, IP-XACT-kuvaukset
  ja laitepuu.

## Lähteet

Määrittelyt ja työkalut:

- Arm: *AMBA AXI Protocol Specification* (IHI 0022), *AMBA APB
  Protocol Specification* (IHI 0024), *AMBA AHB Protocol
  Specification* (IHI 0033). Maksutta ladattavissa: developer.arm.com.
- RISC-V International: *The RISC-V Instruction Set Manual, Volume I:
  Unprivileged ISA* ja *Volume II: Privileged Architecture*.
  CC BY 4.0. github.com/riscv/riscv-isa-manual
- RISC-V International: *RISC-V Platform-Level Interrupt Controller
  Specification* ja *Advanced Interrupt Architecture*. CC BY 4.0.
- RISC-V International: *RISC-V Advanced Core Local Interruptor
  (ACLINT)*. CC BY 4.0.
- IEEE 1685-2022: *IP-XACT*. IEEE 1801-2018: *Unified Power Format*.
- Accellera: *SystemRDL 2.0 Register Description Language*.

Avoimet järjestelmäpiirit ja työkalut, joista näkee tuotantolaatuisia
ratkaisuja:

- OpenTitan: avoin turvapiiri, rekisterityökalu `regtool`,
  kytkingeneraattori `tlgen` ja kattava dokumentaatio. Apache 2.0.
  opentitan.org
- PULP Platform: AXI-kirjasto (kytkimet, sillat, rekisteriviipaleet)
  ja RISC-V-ytimet. Solderpad. github.com/pulp-platform
- PicoRV32: pieni RV32-ydin AXI4-Lite- ja Wishbone-sovittimineen. ISC.
  github.com/YosysHQ/picorv32
- LiteX: Python-pohjainen SoC-rakennustyökalu. BSD.
- PeakRDL: SystemRDL-työkalut RTL:n, otsakkeiden ja dokumentaation
  generointiin. LGPL/MIT.
- Verilator. LGPL/Artistic. verilator.org
- cocotb: testit Pythonilla. BSD. docs.cocotb.org
- cocotbext-axi: AXI-ajurit ja -mallit cocotbille. MIT.
  github.com/alexforencich/cocotbext-axi
- Icarus Verilog. GPL. steveicarus.github.io/iverilog

Kirjat:

- Patterson, Waterman: *The RISC-V Reader*. Strawberry Canyon, 2017.
- Harris, Harris: *Digital Design and Computer Architecture, RISC-V
  Edition*. Morgan Kaufmann, 2021.
- Keating ym.: *Low Power Methodology Manual*. Springer, 2007.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
Pikku-SoC:n lohkot on kirjoitettu tätä tutoriaalia varten.
