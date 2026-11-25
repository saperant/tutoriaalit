"""Keskeneräisen työn raja: läpimenoaika, läpäisy ja Littlen laki."""

import statistics

from virtaus import simuloi

LAMMITYS = 100.0     # alun päivät jätetään pois mittauksesta
PAIVIA = 1000

print("WIP-raja  läpäisy/vk  kierto pv  läpimeno pv  85 % pv"
      "  WIP ka.  Little")
for raja in (2, 4, 6, 8, 12, None):
    tulos = simuloi(raja, PAIVIA)
    # @alku mittarit
    mitatut = [t for t in tulos.valmiit if t.aloitettu >= LAMMITYS]
    lapaisy = len(mitatut) / (PAIVIA - LAMMITYS)             # työtä/pv
    kierto = statistics.mean(t.kiertoaika for t in mitatut)
    lapimeno = sorted(t.lapimenoaika for t in mitatut)
    # Keskeneräisten keskiarvo päivittäisistä kertymistä.
    wip = statistics.mean(aloitettu - valmis for _, aloitettu, valmis
                          in tulos.kertymat[int(LAMMITYS):])
    little = lapaisy * kierto / wip      # Littlen laki: suhde on 1
    # @loppu mittarit
    print(f"{raja if raja else 'ei ole':>8}  {lapaisy * 5:10.1f}"
          f"  {kierto:9.1f}  {statistics.mean(lapimeno):11.1f}"
          f"  {lapimeno[int(0.85 * len(lapimeno))]:7.1f}"
          f"  {wip:7.1f}  {little:6.2f}")
