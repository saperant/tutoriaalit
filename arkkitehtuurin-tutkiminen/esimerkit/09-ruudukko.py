"""Moniydinsirun suunnittelutila täytenä faktorikokeena."""

from arkki.siru import arvioi
from arkki.tutkimus import Tila, ruudukko

# @alku tila
TILA: Tila = {
    "r": [1, 2, 4, 8, 16],  # ytimen koko, BCE
    "c": [2, 4, 8, 16, 32],  # yhteinen välimuisti, MiB
    "v": [0.6, 0.7, 0.8, 0.9, 1.0, 1.1],  # jännite, V
}
TEHORAJA = 80.0  # W
# @loppu tila


def main() -> None:
    # @alku haku
    pisteet = ruudukko(TILA)
    tulokset = [(p, arvioi(p["r"], p["c"], p["v"])) for p in pisteet]
    sallitut = [(p, t) for p, t in tulokset if t.teho <= TEHORAJA]
    sallitut.sort(key=lambda pt: -pt[1].nopeutus)
    # @loppu haku
    print(f"pisteitä {len(pisteet)}, tehorajan {TEHORAJA:.0f} W alittaa"
          f" {len(sallitut)}")
    print(f"{'r':>3} {'c':>3} {'v':>4} {'ytimiä':>6} {'nopeutus':>9}"
          f" {'teho W':>7}")
    for p, t in sallitut[:6]:
        print(f"{p['r']:>3} {p['c']:>3} {p['v']:>4} {t.ytimia:>6}"
              f" {t.nopeutus:9.2f} {t.teho:7.1f}")
    # @alku reuna
    paras = sallitut[0][0]
    for nimi, tasot in TILA.items():
        if paras[nimi] in (tasot[0], tasot[-1]):
            print(f"huom: paras {nimi} = {paras[nimi]} on tilan reunalla")
    # @loppu reuna


if __name__ == "__main__":
    main()
