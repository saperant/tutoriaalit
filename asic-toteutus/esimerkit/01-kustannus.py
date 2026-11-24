"""ASIC vai FPGA? Kokonaiskustannus tuotantomäärän funktiona.

Luvut ovat havainnollistavia suuruusluokkia, eivät tarjouksia:
ASIC-projektin kertakustannus (suunnittelu, verifiointi, maskit) on
suuri, mutta kappalehinta pieni; FPGA on päinvastoin.
"""

from dataclasses import dataclass


# @alku malli
@dataclass(frozen=True)
class Toteutus:
    nimi: str
    kertakustannus: float      # € (NRE: suunnittelu, työkalut, maskit)
    kappalehinta: float        # € / piiri valmiina ja testattuna

    def kustannus(self, maara: int) -> float:
        return self.kertakustannus + maara * self.kappalehinta


def tasapaino(a: Toteutus, b: Toteutus) -> float:
    """Määrä, jolla molemmat maksavat saman verran."""
    return (b.kertakustannus - a.kertakustannus) / (
        a.kappalehinta - b.kappalehinta)
# @loppu malli


def main() -> None:
    # @alku vertailu
    fpga = Toteutus("FPGA", 300_000, 45.0)
    asic = Toteutus("ASIC 130 nm", 2_500_000, 3.0)
    print(f"{'kpl':>9} {'FPGA':>12} {'ASIC':>12}  edullisempi")
    for maara in [1_000, 10_000, 50_000, 100_000, 1_000_000]:
        f, a = fpga.kustannus(maara), asic.kustannus(maara)
        kpl = f"{maara:,}".replace(",", " ")
        print(f"{kpl:>9} {f / 1e6:9.2f} M€ {a / 1e6:9.2f} M€  "
              f"{fpga.nimi if f < a else asic.nimi}")
    raja = f"{tasapaino(fpga, asic):,.0f}".replace(",", " ")
    print(f"tasapainopiste noin {raja} kpl")
    # @loppu vertailu


if __name__ == "__main__":
    main()
