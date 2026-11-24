"""Suljettu malli: K ydintä, joista jokaisella on yksi hutipyyntö
kerrallaan kesken. Sama järjestelmä simuloidaan luvussa 5."""

from arkki.jonot import mva

# @alku parametrit
LASKENTA = 100.0  # ns pyyntöjen välissä (keskiarvo)
VIIVE = 44.0  # ns väylä ja DRAM-käyttö, ei jonoa
PALVELU = 10.0  # ns muistiohjaimen palveluaika, yksi kerrallaan
# @loppu parametrit


def main() -> None:
    print(f"{'ytimiä':>6} {'X GB/s':>7} {'viive ns':>9} {'käyttöaste':>11}"
          f" {'yläraja GB/s':>13}")
    for k in (1, 2, 4, 8, 16, 32):
        # @alku laskenta
        x, r = mva(k, LASKENTA + VIIVE, [PALVELU])
        # Asymptoottiset rajat: ei jonoa tai pullonkaula täynnä.
        raja = min(k / (LASKENTA + VIIVE + PALVELU), 1 / PALVELU)
        # @loppu laskenta
        print(f"{k:>6} {64 * x:7.2f} {VIIVE + r:9.1f} {x * PALVELU:10.0%}"
              f" {64 * raja:13.2f}")


if __name__ == "__main__":
    main()
