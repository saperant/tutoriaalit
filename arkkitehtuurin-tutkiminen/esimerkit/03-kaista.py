"""Muistikaista Littlen lain avulla: kuinka monta hutipyyntöä on oltava
yhtä aikaa kesken, jotta muistikanava saadaan täyteen."""

from arkki.mallit import littlen_kaista, tarvittava_rinnakkaisuus

RIVI = 64  # B
VIIVE = 90.0  # ns, kuormittamaton muistiviive
KANAVA = 25.6  # GB/s, yksi DDR4-3200-kanava


def main() -> None:
    # @alku taulukko
    print(f"viive {VIIVE:.0f} ns, rivi {RIVI} B, kanava {KANAVA} GB/s")
    print(f"{'kesken':>7} {'kaista GB/s':>12} {'käyttöaste':>11}")
    for kesken in (1, 4, 10, 16, 32, 48):
        b = min(littlen_kaista(kesken, RIVI, VIIVE), KANAVA)
        print(f"{kesken:>7} {b:12.1f} {100 * b / KANAVA:10.0f}%")
    n = tarvittava_rinnakkaisuus(KANAVA, RIVI, VIIVE)
    print(f"kanavan täyttämiseen tarvitaan {n:.0f} pyyntöä kesken")
    # @loppu taulukko
    # @alku ytimet
    # Ytimellä on 10 hutirekisteriä (MSHR). Montako ydintä tarvitaan?
    ydin = littlen_kaista(10, RIVI, VIIVE)
    print(f"yksi ydin (10 MSHR): {ydin:.1f} GB/s, kanava täyttyy "
          f"{KANAVA / ydin:.1f} ytimellä")
    # @loppu ytimet


if __name__ == "__main__":
    main()
