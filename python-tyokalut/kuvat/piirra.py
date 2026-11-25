"""Piirtää luvun 8 kuvan esimerkin 08-analyysi.py funktioilla.

Käyttö: python3 kuvat/piirra.py KOHDEHAKEMISTO

Kuva commitoidaan, joten tätä ei ajeta testeissä. Signaali, liukuva
keskiarvo, häiriöpiikit ja spektri lasketaan samoilla funktioilla ja
samalla siemenellä kuin esimerkin testattu tuloste.
"""

import importlib
import sys
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.figure import Figure

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
KOROSTUS = "#2F5F9A"          # alueen Perusta väri
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
MUSTE = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
rcParams["text.color"] = MUSTE
rcParams["axes.edgecolor"] = HARMAA
rcParams["axes.labelcolor"] = MUSTE
rcParams["xtick.color"] = HARMAA
rcParams["ytick.color"] = HARMAA


def analyysi(polku: Path) -> None:
    sys.path.insert(0, str(ESIMERKIT))
    esimerkki = importlib.import_module("08-analyysi")
    fs, ikkuna = 1000.0, 20
    x = esimerkki.mittaus(1000, 50.0, fs, siemen=42)
    t_ms = np.arange(x.size) / fs * 1e3
    tasoitettu = esimerkki.liukuva_keskiarvo(x, ikkuna)
    piikit = esimerkki.piikit(x, kynnys=1.0)
    spektri = np.abs(np.fft.rfft(x - x.mean())) / x.size * 2
    taajuudet = np.fft.rfftfreq(x.size, d=1 / fs)
    huippu = esimerkki.hallitseva_taajuus(x, fs)

    fig = Figure(figsize=(6.4, 3.6), dpi=200, layout="constrained")
    ylempi, alempi = fig.subplots(2, 1, height_ratios=[3, 2])
    ylempi.plot(t_ms, x, color=KOROSTUS, linewidth=0.7, label="signaali")
    ylempi.plot(t_ms[ikkuna - 1:], tasoitettu, color=TOINEN, linewidth=1.4,
                label=f"liukuva keskiarvo ({ikkuna} näytettä)")
    ylempi.plot(t_ms[piikit], x[piikit], "o", color="#B03A2E", markersize=4,
                label="häiriöpiikit")
    ylempi.set(xlabel="aika (ms)", ylabel="jännite (V)", xlim=(0, 1000))
    ylempi.legend(frameon=False, ncols=3, loc="lower center",
                  bbox_to_anchor=(0.5, 1.0))
    alempi.plot(taajuudet, spektri, color=KOROSTUS, linewidth=0.9)
    alempi.annotate(f"{huippu:.0f} Hz", (huippu, spektri.max()),
                    xytext=(8, -4), textcoords="offset points")
    alempi.set(xlabel="taajuus (Hz)", ylabel="amplitudi (V)", xlim=(0, 250))
    fig.savefig(polku, metadata={"Software": None})


if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    analyysi(kohde / "analyysi.png")
