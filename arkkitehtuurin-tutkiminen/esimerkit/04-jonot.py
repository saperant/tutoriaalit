"""Muistiohjaimen viive kuorman funktiona jonomalleilla.

Ohjain palvelee yhden 64 tavun pyynnön 10 ns:ssa (6,4 GB/s). Sama
kapasiteetti voi olla yksi nopea tai kaksi puolta hitaampaa kanavaa.
"""

from arkki.jonot import mg1, mm1, mmc

PALVELU_NS = 10.0
MU = 1 / PALVELU_NS  # pyyntöä / ns


def main() -> None:
    # @alku taulukko
    print("viipymä W (ns): jono + palvelu, palveluaika 10 ns")
    print(f"{'kuorma':>7} {'GB/s':>6} {'M/M/1':>7} {'M/D/1':>7}"
          f" {'M/M/2':>7}")
    for rho in (0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95):
        lam = rho * MU
        a = mm1(lam, MU)
        d = mg1(lam, PALVELU_NS, PALVELU_NS**2)
        c = mmc(lam, MU / 2, 2)  # kaksi kanavaa, kumpikin 20 ns
        print(f"{rho:>7.0%} {lam * 64:6.2f} {a.viipyma:7.1f}"
              f" {d.viipyma:7.1f} {c.viipyma:7.1f}")
    # @loppu taulukko
    # @alku little
    a = mm1(0.8 * MU, MU)
    print(f"\nLittle, M/M/1 80 %: L = lambda W = {0.8 * MU:.2f} * "
          f"{a.viipyma:.0f} = {a.maara:.1f} pyyntöä järjestelmässä")
    # @loppu little


if __name__ == "__main__":
    main()
