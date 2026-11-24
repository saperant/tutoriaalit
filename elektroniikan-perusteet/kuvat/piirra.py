"""Piirtää paketin kuvat: piirikaaviot (schemdraw) ja kuvaajat ngspicen
tuloksista. Käyttö: python3 kuvat/piirra.py kuvat

Kuvat ovat versionhallinnassa; skripti ajetaan uudelleen, kun piirit
tai esimerkit muuttuvat.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "esimerkit"))
from spice import simuloi  # noqa: E402

KOROSTUS = "#3E7F3C"
HARMAA = "#5B6B70"
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 100, "savefig.dpi": 200,
                     "savefig.bbox": "tight"})
schemdraw.use("matplotlib")


def tallenna_kaavio(d: schemdraw.Drawing, polku: Path) -> None:
    d.save(str(polku), dpi=200)


def jakaja(kohde: Path) -> None:
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.2, fontsize=11)
        elm.SourceV().up().label("12 V", loc="top")
        elm.Resistor().right().label("R1\n10 k")
        d.push()
        elm.Resistor().down().label("R2\n4,7 k", loc="bottom")
        elm.Line().left()
        d.pop()
        elm.Line().right(1.2)
        elm.Dot(open=True).label("ulos", loc="right")
        elm.Ground().at((0, 0))
        tallenna_kaavio(d, kohde / "jakaja.png")


def silta(kohde: Path) -> None:
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.2, fontsize=10)
        v1 = elm.SourceV().up().label("V1\n10 V", loc="top")
        elm.Resistor().right().label("R1 1 k")
        a = elm.Dot().label("a", loc="top")
        d.push()
        elm.Resistor().down().label("R2\n2 k", loc="bottom")
        elm.Line().left().to(v1.start)
        d.pop()
        elm.Resistor().right().label("R3 1 k")
        elm.Dot().label("b", loc="top")
        d.push()
        elm.Resistor().down().label("R5\n1 k", loc="bottom")
        d.pop()
        elm.Resistor().right().label("R4 2 k")
        elm.SourceV().down().reverse().label("V2\n5 V", loc="top")
        elm.Line().left().tox(a.start)
        elm.Ground().at(v1.start)
        tallenna_kaavio(d, kohde / "silta.png")


def rc_lataus(kohde: Path) -> None:
    data = simuloi("04-rc.cir").data["rc"]
    t, u = data[:, 0] * 1e3, data[:, 1]
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    ax.plot(t, u, color=KOROSTUS, label="SPICE")
    ax.plot(t, 5 * (1 - np.exp(-t)), "--", color=HARMAA,
            label="5 V (1 - e^(-t/tau))")
    for k in (1, 2, 3):
        ax.axvline(k, color=HARMAA, lw=0.6, ls=":")
    ax.annotate("63 %", (1, 3.16), (1.4, 2.4),
                arrowprops={"arrowstyle": "->", "color": HARMAA})
    ax.set_xlabel("aika (ms) = aika / tau")
    ax.set_ylabel("u_C (V)")
    ax.legend(loc="lower right")
    fig.savefig(kohde / "rc-lataus.png")
    plt.close(fig)


def varahtely(kohde: Path) -> None:
    piiri = (Path(__file__).resolve().parent.parent / "esimerkit" /
             "04-varahtely.cir").read_text("utf-8")
    data = simuloi(piiri).data["varahtely"]
    data100 = simuloi(piiri.replace("C1 suod 0 22n",
                                    "C1 suod 0 100n")).data["varahtely"]
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    t = data[:, 0] * 1e3
    ax.plot(t, data[:, 1], color=HARMAA, lw=0.8, label="raaka")
    ax.plot(t, data[:, 3], color=KOROSTUS, label="RC 22 nF")
    ax.plot(data100[:, 0] * 1e3, data100[:, 3], color="#B07A2A",
            label="RC 100 nF")
    for raja in (1.0, 2.3):
        ax.axhline(raja, color=HARMAA, lw=0.6, ls="--")
    ax.axhline(1.65, color=HARMAA, lw=0.6, ls=":")
    ax.set_xlim(0.5, 4)
    ax.set_xlabel("aika (ms)")
    ax.set_ylabel("jännite (V)")
    ax.legend(loc="upper right", fontsize=8)
    fig.savefig(kohde / "varahtely.png")
    plt.close(fig)


def bode(kohde: Path) -> None:
    data = simuloi("05-alipaasto.cir").data["alipaasto"]
    f, db, vaihe = data[:, 0], data[:, 1], data[:, 3]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.5, 3.6), sharex=True)
    a1.semilogx(f, db, color=KOROSTUS)
    a1.axhline(-3, color=HARMAA, lw=0.6, ls="--")
    a1.axvline(1591.5, color=HARMAA, lw=0.6, ls=":")
    a1.set_ylabel("vahvistus (dB)")
    a1.set_ylim(-60, 5)
    a2.semilogx(f, vaihe, color=KOROSTUS)
    a2.axvline(1591.5, color=HARMAA, lw=0.6, ls=":")
    a2.set_ylabel("vaihe (astetta)")
    a2.set_xlabel("taajuus (Hz)")
    fig.savefig(kohde / "bode.png")
    plt.close(fig)


def diodi(kohde: Path) -> None:
    data = simuloi("06-ominaiskayra.cir").data["ominaiskayra"]
    u, i = data[:, 0], data[:, 1]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 2.4))
    a1.plot(u, i * 1e3, color=KOROSTUS)
    a1.set_xlim(0, 0.9)
    a1.set_ylim(0, 50)
    a1.set_xlabel("U (V)")
    a1.set_ylabel("I (mA)")
    a2.semilogy(u[u > 0.05], i[u > 0.05], color=KOROSTUS)
    a2.set_xlabel("U (V)")
    a2.set_ylabel("I (A), log")
    fig.tight_layout()
    fig.savefig(kohde / "diodi.png")
    plt.close(fig)


def tasasuuntaaja(kohde: Path) -> None:
    data = simuloi("06-tasasuuntaaja.cir").data["tasasuuntaaja"]
    t, u = data[:, 0] * 1e3, data[:, 1]
    fig, ax = plt.subplots(figsize=(5.5, 2.4))
    ax.plot(t, u, color=KOROSTUS, label="u_ulos")
    tt = np.linspace(0, 300, 3000)
    ax.plot(tt, np.abs(16.97 * np.sin(2 * np.pi * 0.05 * tt)) - 1.7,
            color=HARMAA, lw=0.6, label="|u_toisio| - 2 U_F")
    ax.set_xlim(200, 260)
    ax.set_ylim(0, 17)
    ax.set_xlabel("aika (ms)")
    ax.set_ylabel("jännite (V)")
    ax.legend(loc="lower right", fontsize=8)
    fig.savefig(kohde / "tasasuuntaaja.png")
    plt.close(fig)


def kytkin(kohde: Path) -> None:
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.2, fontsize=10)
        q = elm.BjtNpn(circle=True).label("Q1", loc="right")
        elm.Resistor().left().at(q.base).label("Rb 470")
        elm.Dot(open=True).label("3,3 V\nohjaus", loc="left")
        elm.Resistor().up().at(q.collector).label("120 ohm\nkuorma")
        elm.Vdd().label("12 V")
        elm.Ground().at(q.emitter)
        tallenna_kaavio(d, kohde / "bjt-kytkin.png")


def cmos(kohde: Path) -> None:
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    piiri = (Path(__file__).resolve().parent.parent / "esimerkit" /
             "07-cmos.cir").read_text("utf-8")
    for wp, vari in (("2.5u", KOROSTUS), ("1u", "#B07A2A")):
        data = simuloi(piiri.replace(".param Wp=2.5u",
                                     f".param Wp={wp}")).data["cmos"]
        ax.plot(data[:, 0], data[:, 1], color=vari, label=f"W_p = {wp}m")
    ax.plot([0, 1.8], [0, 1.8], color=HARMAA, lw=0.6, ls=":")
    ax.set_xlabel("u_sisään (V)")
    ax.set_ylabel("u_ulos (V)")
    ax.legend(fontsize=8)
    fig.savefig(kohde / "cmos.png")
    plt.close(fig)


def main() -> None:
    kohde = Path(sys.argv[1] if len(sys.argv) > 1 else "kuvat")
    kohde.mkdir(exist_ok=True)
    for piirtaja in (jakaja, silta, rc_lataus, varahtely, bode, diodi,
                     tasasuuntaaja, kytkin, cmos):
        piirtaja(kohde)
        print("piirretty:", piirtaja.__name__)


if __name__ == "__main__":
    main()
