"""Kotelointi: maapomppu ja piirin koko IO-nastojen mukaan.

Lankabondaus tuo jokaiselle nastalle muutaman nanohenryn
induktanssin. Kun monta lähtöä vaihtaa tilaa yhtä aikaa, maajohtimen
jännite pomppaa L·di/dt. Flip-chip-kuulien induktanssi on
kymmenesosa. Lisäksi IO-renkaan nastat voivat määrätä piirin koon:
piiri on tällöin nastarajoitteinen (pad-limited).
"""

# @alku maapomppu
V = 1.8            # V, IO-jännite
C_LAHTO = 10e-12   # F, piirilevyn kuorma lähtöä kohden
T_REUNA = 1e-9     # s, lähdön nousuaika


def maapomppu(lahtoja: int, maanastoja: int, l_nasta: float) -> float:
    """L·di/dt, kun lähdöt vaihtavat samaan aikaan (V)."""
    di_dt = C_LAHTO * V / T_REUNA**2          # A/s yhtä lähtöä kohden
    return l_nasta / maanastoja * lahtoja * di_dt
# @loppu maapomppu


# @alku nastat
def piirin_sivu(nastoja: int, jako_um: float, ydin_mm2: float
                ) -> tuple[float, str]:
    """Sivun pituus (mm): suurempi nastarenkaan ja ytimen vaatimasta."""
    renkaan_sivu = nastoja / 4 * jako_um / 1000
    ytimen_sivu = ydin_mm2 ** 0.5 + 2 * 0.25   # 0.25 mm IO-solujen syvyys
    if renkaan_sivu > ytimen_sivu:
        return renkaan_sivu, "nastarajoitteinen"
    return ytimen_sivu, "ydinrajoitteinen"
# @loppu nastat


def main() -> None:
    # @alku ajo
    print("16 lähtöä vaihtaa samaan aikaan:")
    for nimi, l_nasta in [("lankabondaus 2 nH", 2e-9),
                          ("flip-chip 0,1 nH", 0.1e-9)]:
        for maa in [1, 4]:
            print(f"  {nimi:18} {maa} maanastaa: "
                  f"{maapomppu(16, maa, l_nasta) * 1000:5.0f} mV")
    for nastoja, ydin in [(200, 4.0), (64, 4.0), (200, 25.0)]:
        sivu, laji = piirin_sivu(nastoja, 60.0, ydin)
        print(f"{nastoja} nastaa, ydin {ydin:4.1f} mm²: sivu {sivu:.2f} mm "
              f"({laji})")
    # @loppu ajo


if __name__ == "__main__":
    main()
