# SoC-integraatio

Järjestelmäpiirin (system on chip) kokoaminen: SoC:n rakenne, AMBA-väylät
(AXI4, AXI4-Lite, APB ja AHB), kytkentäverkot ja muistikartta, valmiit
IP-lohkot, rekisterikuvaukset ja niistä generoitu koodi, keskeytykset,
DMA, kello-, nollaus- ja tehoalueet sekä ohjelmiston ajaminen
simuloidussa RISC-V-SoC:ssa. Valmis dokumentti:
[soc-integraatio.pdf](https://saperant.github.io/tutoriaalit/materiaalit/soc-integraatio.pdf),
pikaopas:
[soc-integraatio-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/soc-integraatio-pikaopas.pdf).

Esitiedot: taidot *RTL-suunnittelu SystemVerilogilla* ja
*Tietokonearkkitehtuuri*.

## Sisältö

1. Johdanto – Pikku-SoC, työkalut ja esimerkkien ajaminen
2. SoC:n rakenne – isännät ja orjat, väylähierarkia, muistikartta
3. Ydin ja ohjelmisto – ytimen väylä, käynnistyskoodi,
   linkkeriskripti, MMIO-ajurit
4. AXI4 ja AXI4-Lite – kanavat, kättelyt, purskeet, tunnisteet
5. APB, AHB ja sillat
6. Kytkentäverkot ja muistikartta – dekoodaus, välittäjä,
   oletusorja
7. Valmiit IP-lohkot – hard ja soft IP, IP-XACT, lisenssit
8. Rekisterikuvaukset ja generointi
9. Keskeytykset – RISC-V:n ansat, CLINT ja PLIC
10. DMA
11. Kello-, nollaus- ja tehoalueet
12. Virheet ja protokollatarkistus
13. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Esimerkit

`esimerkit/` sisältää *Pikku-SoC:n*: opetuskäyttöön kirjoitetun
monivaiheisen RV32I-ytimen, AXI4-Lite-kytkimen kahdelle isännälle,
RAMin, APB-sillan ja oheislaitteet (UART, SYSCON, GPIO, DMA, CLINT ja
yksinkertaistettu PLIC). SYSCONin ja GPIO:n rekisterilohkot on
generoitu JSON-kuvauksista (`gen/rekisterit.py`). Ohjelmat
(`sw/*.c`) käännetään RISC-V-ristikääntäjällä ja ajetaan
Verilator-simulaatiossa; UARTin tuloste verrataan odotettuun.

```text
make -C esimerkit            # kaikki tarkistukset ja simulaatiot
make -C esimerkit aja-dma    # yksi ohjelma simulaatiossa
make -C esimerkit generoi    # rekisterilohkot kuvauksista
```

Työkalut: Verilator 5, `gcc-riscv64-unknown-elf` (Ubuntu 24.04) ja
Python 3 (ruff, mypy). Kehityskontti `.devcontainer/soc-integraatio`
sisältää ne.

Lisenssi: CC BY-SA 4.0.
