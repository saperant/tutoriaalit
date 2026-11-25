"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Ristikattavuuden
kuva tuotetaan ajamalla luvun 4 cocotb-testit (tarvitsee Icarus
Verilogin ja cocotb:n); osumat tulevat samasta ajosta kuin kirjan
raportti. Täyttöasteen kuva on kymmenen rivin simulaatio kiinteällä
siemenellä.
"""

import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from matplotlib import rcParams
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure

JUURI = Path(__file__).resolve().parent.parent
ESIMERKIT = JUURI / "esimerkit"
KUVAT = JUURI / "kuvat"

KOROSTUS = "#B04848"
TOINEN = "#546676"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
TUMMA = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def uusi(leveys: float, korkeus: float) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def ristikattavuus(polku: Path) -> None:
    """Täyttöaste x toimenpide -osumat kolmelle testille."""
    with tempfile.TemporaryDirectory() as hak:
        tiedosto = Path(hak) / "osumat.jsonl"
        subprocess.run(
            [sys.executable, "pythonpenkit/aja.py", "--top", "fifo",
             "--moduuli", "test_fifo", "--lahde", "rtl/fifo.sv"],
            cwd=ESIMERKIT, check=True, stdout=subprocess.DEVNULL,
            env={**os.environ, "KATTAVUUS_TIEDOSTO": str(tiedosto),
                 "SIEMEN": "1"})
        ajot = [json.loads(r) for r in tiedosto.read_text().splitlines()]
    nimet = ["ohjattu", "satunnaistettu (siemen 1)", "kulmat"]
    assert len(ajot) == len(nimet), len(ajot)
    kartta = LinearSegmentedColormap.from_list(
        "osumat", ["#F3E3E3", KOROSTUS])
    kartta.set_under("white")
    fig = uusi(7.0, 2.1)
    akselit = fig.subplots(1, 3, sharey=True)
    for ax, nimi, ajo in zip(akselit, nimet, ajot):
        rivit, sarakkeet = ajo["rivit"], ajo["sarakkeet"]
        luvut = [[ajo["osumat"].get(f"{r}*{s}", 0) for s in sarakkeet]
                 for r in rivit]
        suurin = max(max(rivi) for rivi in luvut)
        ax.imshow(luvut, cmap=kartta, vmin=0.5, vmax=suurin,
                  aspect="auto")
        for i, rivi in enumerate(luvut):
            for j, n in enumerate(rivi):
                vari = "white" if n > 0.6 * suurin else TUMMA
                ax.text(j, i, str(n) if n else "–", ha="center",
                        va="center", color=vari if n else HARMAA)
        ax.set_xticks(range(len(sarakkeet)), sarakkeet)
        ax.set_yticks(range(len(rivit)), rivit)
        ax.set_title(nimi, fontsize=9, color=TUMMA)
        ax.tick_params(length=0)
        for reuna in ax.spines.values():
            reuna.set_visible(True)
            reuna.set_color(VAALEA)
        ax.set_xticks([x - 0.5 for x in range(1, len(sarakkeet))],
                      minor=True)
        ax.set_yticks([y - 0.5 for y in range(1, len(rivit))], minor=True)
        ax.grid(which="minor", color=VAALEA, linewidth=0.6)
        ax.tick_params(which="minor", length=0)
    fig.savefig(polku, metadata=METATIEDOT)


def tayttoaste(polku: Path) -> None:
    """1024 paikan FIFO: tasainen satunnaisuus ja vaiheistettu ärsyke."""
    syvyys, jaksoja = 1024, 200_000
    rng = random.Random(1)
    tasainen, maara = [], 0
    for _ in range(jaksoja):
        maara += rng.choice((-1, 0, 0, 1))      # push ja pop 50 % kumpikin
        maara = min(max(maara, 0), syvyys)
        tasainen.append(maara)
    rng = random.Random(1)
    vaiheet, maara, suunta = [], 0, 1
    for _ in range(jaksoja):
        # Täyttövaiheessa kirjoitetaan 60 %:n ja luetaan 40 %:n
        # todennäköisyydellä, tyhjennysvaiheessa päinvastoin.
        p_push = 0.6 if suunta > 0 else 0.4
        maara += (rng.random() < p_push) - (rng.random() < 1 - p_push)
        maara = min(max(maara, 0), syvyys)
        if maara in (0, syvyys):
            suunta = 1 if maara == 0 else -1
        vaiheet.append(maara)
    fig = uusi(5.6, 2.4)
    ax = fig.subplots()
    x = [i / 1000 for i in range(0, jaksoja, 50)]
    ax.plot(x, vaiheet[::50], color=TOINEN, linewidth=0.9,
            label="vaiheistettu: täyttö ja tyhjennys")
    ax.plot(x, tasainen[::50], color=KOROSTUS, linewidth=0.9,
            label="tasainen satunnaisuus")
    ax.axhline(syvyys, color=HARMAA, linewidth=0.6, linestyle="--")
    ax.set_xlabel("jakso (tuhatta)")
    ax.set_ylabel("sanoja jonossa")
    ax.set_yticks([0, 256, 512, 768, 1024],
                  ["0", "256", "512", "768", "1024 (täynnä)"])
    ax.set_ylim(0, syvyys * 1.05)
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0),
              ncols=2, fontsize=8)
    huippu = max(tasainen)
    taysia = sum(1 for a, b in zip(vaiheet, vaiheet[1:])
                 if b == syvyys and a != syvyys)
    print(f"tasainen: suurin täyttö {huippu}; vaiheistettu: täynnä "
          f"{taysia} kertaa")
    fig.savefig(polku, metadata=METATIEDOT)


if __name__ == "__main__":
    tayttoaste(KUVAT / "tayttoaste.png")
    ristikattavuus(KUVAT / "ristikattavuus.png")
