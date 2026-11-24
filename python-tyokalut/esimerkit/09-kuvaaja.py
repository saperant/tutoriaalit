"""Mittauskuvaaja tiedostoon ilman näyttöä.

Työkalu käyttää matplotlibin olio-rajapintaa (Figure) eikä pyplotia:
ei globaalia tilaa, ei näyttöä vaativaa taustaosaa, ja kuva vapautuu
muistista, kun olio poistuu. Sama koodi toimii CI:ssä ja palvelimella.

Käyttö:  python3 09-kuvaaja.py [KUVA.png]
"""

import struct
import sys
import tempfile
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure


# @alku kuvaaja
def piirra(t: np.ndarray, x: np.ndarray, kynnys: float,
           polku: Path) -> None:
    fig = Figure(figsize=(8, 3), dpi=100, layout="constrained")
    ax = fig.add_subplot()
    ax.plot(t * 1e3, x, linewidth=1, label="jännite")
    ax.axhline(kynnys, color="tab:red", linestyle="--",
               label=f"kynnys {kynnys} V")
    yli = x > kynnys
    ax.plot(t[yli] * 1e3, x[yli], "o", color="tab:red", markersize=4,
            label="ylitykset")
    ax.set(xlabel="aika (ms)", ylabel="jännite (V)",
           title="Syöttöjännitteen mittaus")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")
    fig.savefig(polku)            # muoto päätteestä: png, pdf, svg
# @loppu kuvaaja


# @alku tarkistus
def png_koko(polku: Path) -> tuple[int, int]:
    """Leveys ja korkeus PNG-tiedoston IHDR-lohkosta."""
    otsake = polku.read_bytes()[:24]
    if otsake[:8] != b"\x89PNG\r\n\x1a\n" or otsake[12:16] != b"IHDR":
        raise ValueError(f"{polku} ei ole PNG-kuva")
    leveys, korkeus = struct.unpack(">II", otsake[16:24])
    return leveys, korkeus
# @loppu tarkistus


def main(argv: list[str]) -> int:
    t = np.linspace(0.0, 0.1, 500)
    x = 3.3 + 0.05 * np.sin(2 * np.pi * 50 * t)
    x[[100, 101, 350]] += 0.4                       # häiriöt
    with tempfile.TemporaryDirectory() as tmp:
        polku = Path(argv[0]) if argv else Path(tmp) / "mittaus.png"
        piirra(t, x, 3.5, polku)
        print("kuva:", polku.suffix, png_koko(polku))
        print(f"ylityksiä {(x > 3.5).sum()}, maksimi {x.max():.2f} V")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
