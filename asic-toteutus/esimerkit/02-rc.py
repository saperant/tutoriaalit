"""Solun viive RC-mallina: taulukon takana on kytkin ja vastus.

Kytkevä transistori on likimain vastus, joka varaa tai purkaa lähdön
kapasitanssin. Viive on silloin t = t0 + 0,69·R·C: sisäinen viive
plus aikavakio kertaa ln 2. Tässä vastus ja sisäinen viive sovitetaan
kirjaston NLDM-taulukoista, ja mallia verrataan taulukkoon.
"""

from pathlib import Path

from liberty import Ryhma, lue, taulukko

KIRJASTO = lue(Path(__file__).with_name("opetus.lib"))
SLEW = 0.02                    # ns, jyrkkä tulo: taulukon ensimmäinen rivi


# @alku sovitus
def sovita(solu: str, taulu: str) -> tuple[float, float]:
    """(R kΩ, sisäinen viive ns) taulukon kahdesta pienimmästä kuormasta.
    Viiveen kulmakerroin on 0,69·R; ns/pF on sama kuin kΩ."""
    s: Ryhma = KIRJASTO.yksi("cell", solu)
    lahto = next(p for p in s.kaikki("pin")
                 if p.attr["direction"] == "output")
    t = taulukko(KIRJASTO, lahto.kaikki("timing")[0].yksi(taulu,
                                                           "nldm_3x3"))
    c0, c1 = t.indeksi2[0], t.indeksi2[1]
    d0, d1 = t.arvo(SLEW, c0), t.arvo(SLEW, c1)
    kulma = (d1 - d0) / (c1 - c0)
    return kulma / 0.69, d0 - kulma * c0
# @loppu sovitus


def main() -> None:
    # @alku vertailu
    print("solu     tulo fF  R ylös kΩ  R alas kΩ  sisäinen ps  ala µm²")
    for nimi in ["INV_X1", "BUF_X1", "BUF_X4"]:
        s = KIRJASTO.yksi("cell", nimi)
        tulo = float(s.yksi("pin", "A").attr["capacitance"]) * 1000
        r_ylos, t0 = sovita(nimi, "cell_rise")
        r_alas, _ = sovita(nimi, "cell_fall")
        print(f"{nimi:8} {tulo:7.1f} {r_ylos:10.2f} {r_alas:10.2f} "
              f"{t0 * 1000:12.0f} {float(s.attr['area']):8.2f}")
    r, t0 = sovita("INV_X1", "cell_rise")
    for kuorma in [0.005, 0.030]:
        malli = t0 + 0.69 * r * kuorma
        s = KIRJASTO.yksi("cell", "INV_X1").yksi("pin", "Y")
        luettu = taulukko(KIRJASTO, s.kaikki("timing")[0].yksi(
            "cell_rise", "nldm_3x3")).arvo(SLEW, kuorma)
        print(f"INV_X1, kuorma {kuorma * 1000:.0f} fF: malli "
              f"{malli * 1000:.0f} ps, taulukko {luettu * 1000:.0f} ps")
    # @loppu vertailu


if __name__ == "__main__":
    main()
