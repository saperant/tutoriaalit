"""Tehonkulutuksen arvio porttitason simuloinnin aktiivisuudesta.

Dynaaminen teho syntyy, kun johtimen kapasitanssi varataan:
jokainen nouseva siirtymä ottaa käyttöjännitteestä energian C·V².
Simulointi tallentaa jokaisen johtimen siirtymät (VCD), kuormat
tulevat ajoitusanalyysista ja vuoto kirjastosta. Lopuksi arvioidaan,
paljonko kellon portitus säästäisi.
"""

import re
import subprocess
import tempfile
from pathlib import Path

from liberty import lue
from sta import Analyysi, Rajoitteet
from synteesi import rakenteellinen, syntetisoi

HAK = Path(__file__).parent
V, JAKSO, JAKSOJA = 1.8, 10e-9, 1000          # V, s, kpl


# @alku vcd
def siirtymat(vcd: str) -> dict[str, int]:
    """Laskee jokaisen signaalibitin arvon muutokset VCD-tiedostosta."""
    signaalit: dict[str, tuple[str, int]] = {}      # tunnus: (nimi, bittejä)
    for m in re.finditer(r"\$var wire (\d+) (\S+) (\S+)[^$]*\$end", vcd):
        signaalit.setdefault(m[2], (m[3], int(m[1])))
    edelliset: dict[str, str] = {}
    maarat: dict[str, int] = {}
    for rivi in vcd.split("$enddefinitions", 1)[1].splitlines():
        if rivi.startswith("b"):
            arvo, tunnus = rivi[1:].split()
        elif rivi[:1] in ("0", "1", "x", "z") and len(rivi) > 1:
            arvo, tunnus = rivi[0], rivi[1:]
        else:
            continue
        if tunnus not in signaalit:
            continue
        nimi, leveys = signaalit[tunnus]
        arvo = arvo.rjust(leveys, "0")
        vanha = edelliset.get(tunnus)
        if vanha is not None:
            for i, (a, b) in enumerate(zip(vanha[::-1], arvo[::-1],
                                           strict=True)):
                if a != b:
                    avain = f"{nimi}[{i}]" if leveys > 1 else nimi
                    maarat[avain] = maarat.get(avain, 0) + 1
        edelliset[tunnus] = arvo
    return maarat
# @loppu vcd


def main() -> None:
    tulos = syntetisoi([HAK / "laskuri.v"], "laskuri")
    m = tulos.moduuli()
    with tempfile.TemporaryDirectory() as tmp:
        netlista = Path(tmp, "n.v")
        netlista.write_text(rakenteellinen("laskuri", m), "utf-8")
        subprocess.run(["iverilog", "-o", f"{tmp}/sim", str(netlista),
                        str(HAK / "opetus_solut.v"),
                        str(HAK / "tp_teho.v")], check=True)
        subprocess.run(["vvp", "-n", f"{tmp}/sim"], cwd=tmp, check=True,
                       capture_output=True)
        maarat = siirtymat(Path(tmp, "aktiivisuus.vcd").read_text())
    # @alku teho
    analyysi = Analyysi(tulos, Rajoitteet(jakso=10.0))
    nimet = {b: f"{p}[{i}]" if len(v["bits"]) > 1 else p
             for p, v in m["ports"].items()
             for i, b in enumerate(v["bits"])}
    kello = m["ports"]["clk"]["bits"][0]
    aika = JAKSOJA * JAKSO
    dynaaminen = {"kello": 0.0, "logiikka": 0.0}
    for b, c in analyysi.kuorma.items():
        nousuja = maarat.get(nimet.get(b, f"n{b}"), 0) / 2
        teho = nousuja / aika * c * 1e-12 * V**2      # C pF:inä
        dynaaminen["kello" if b == kello else "logiikka"] += teho
    lib = lue(HAK / "opetus.lib")
    vuoto = sum(float(lib.yksi("cell", c["type"])
                      .attr["cell_leakage_power"]) * 1e-9
                for c in m["cells"].values())
    for nimi, teho in [*dynaaminen.items(), ("vuoto", vuoto)]:
        print(f"{nimi:9} {teho * 1e6:8.2f} µW")
    # @loppu teho
    # @alku portitus
    # Portitettu kello pysähtyy kiikuilta, kun sallinta = 0 (75 %).
    # Portituslohko (salpa + JA) kuormittaa kelloa itse noin 5 fF.
    kiikut = sum(1 for c in m["cells"].values() if c["type"] == "DFF_X1")
    c_kiikut = kiikut * 0.0025
    c_kello = analyysi.kuorma[kello]
    portitettu = dynaaminen["kello"] * (
        (c_kello - c_kiikut + 0.005) + 0.25 * c_kiikut) / c_kello
    print(f"kello portitettuna noin {portitettu * 1e6:.2f} µW "
          f"({portitettu / dynaaminen['kello'] - 1:+.0%})")
    # @loppu portitus


if __name__ == "__main__":
    main()
