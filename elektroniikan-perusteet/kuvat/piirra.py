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
import schemdraw.logic as logic  # noqa: E402


KOROSTUS = "#3E7F3C"
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
VAALEA = "#B8C2C6"
ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.path.insert(0, str(ESIMERKIT))
from spice import simuloi  # noqa: E402

# Solmun nimi netlistissä: sama nimi kaaviossa ja .cir-tiedostossa.
SOLMU = {"color": HARMAA, "fontsize": 9}
# Sama usean piirin kaavioissa, jotka ladotaan pienemmässä mittakaavassa.
ISO_SOLMU = {"color": HARMAA, "fontsize": 12}
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
        elm.Resistor().right().label("R1\n10 kΩ")
        d.push()
        elm.Resistor().down().label("R2\n4,7 kΩ", loc="bottom")
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
        elm.Resistor().right().label("R1 1 kΩ")
        a = elm.Dot().label("a", loc="top")
        d.push()
        elm.Resistor().down().label("R2\n2 kΩ", loc="bottom")
        elm.Line().left().to(v1.start)
        d.pop()
        elm.Resistor().right().label("R3 1 kΩ")
        elm.Dot().label("b", loc="top")
        d.push()
        elm.Resistor().down().label("R5\n1 kΩ", loc="bottom")
        d.pop()
        elm.Resistor().right().label("R4 2 kΩ")
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
    piiri = (ESIMERKIT / "04-varahtely.cir").read_text("utf-8")
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
        elm.Resistor().left().at(q.base).label("Rb 470 Ω")
        elm.Dot(open=True).label("3,3 V\nohjaus", loc="left")
        elm.Resistor().up().at(q.collector).label("kuorma\n120 Ω")
        elm.Vdd().label("12 V")
        elm.Ground().at(q.emitter)
        tallenna_kaavio(d, kohde / "bjt-kytkin.png")


def cmos(kohde: Path) -> None:
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    piiri = (ESIMERKIT / "07-cmos.cir").read_text("utf-8")
    for wp, vari in (("2.5u", KOROSTUS), ("1u", "#B07A2A")):
        data = simuloi(piiri.replace(".param Wp=2.5u",
                                     f".param Wp={wp}")).data["cmos"]
        ax.plot(data[:, 0], data[:, 1], color=vari,
                label=f"W_p = {wp[:-1].replace('.', ',')} µm")
    ax.plot([0, 1.8], [0, 1.8], color=HARMAA, lw=0.6, ls=":")
    ax.set_xlabel("u_sisään (V)")
    ax.set_ylabel("u_ulos (V)")
    ax.legend(fontsize=8)
    fig.savefig(kohde / "cmos.png")
    plt.close(fig)


def rc_rl(kohde: Path) -> None:
    """Luvun 4 RC- ja RL-piiri rinnakkain."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.2, fontsize=14)
        for x, komponentti, arvo, solmu, lahde, r in (
                (0.0, elm.Capacitor, "C1\n100 nF", "c", "V1\n0 → 5 V",
                 "R1 10 kΩ"),
                (8.4, elm.Inductor2, "L1\n10 mH", "l", "V1\n0 → 12 V",
                 "R1 100 Ω")):
            v = elm.SourcePulse().up().at((x, 0)).label(lahde)
            elm.Dot().label("sisaan", loc="top", **ISO_SOLMU)
            elm.Resistor().right().label(r, loc="bottom")
            elm.Dot().label(solmu, loc="top", **ISO_SOLMU)
            komponentti().down().label(arvo, loc="bottom")
            elm.Line().left().to(v.start)
            elm.Ground().at(v.start)
        tallenna_kaavio(d, kohde / "rc-rl-piirit.png")


def vetovastus(kohde: Path) -> None:
    """I2C-väylän vetovastus, väylän kapasitanssi ja avoin nielu."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        q = elm.NFet().right().reverse()
        elm.Line().left(0.6).at(q.gate).label("laitteen\nlähtö", loc="left")
        elm.Ground().at(q.source)
        elm.Line().up(0.5).at(q.drain)
        sda = elm.Dot().label("sda", loc="left", **SOLMU)
        elm.Resistor().up().label("Rp\n4,7 kΩ")
        elm.Vdd().label("3,3 V")
        elm.Line().right(2.2).at(sda.center)
        elm.Dot()
        d.push()
        elm.Capacitor().down().label("Cb\n200 pF", loc="bottom")
        elm.Ground()
        d.pop()
        elm.Line().right(1.8)
        elm.Dot(open=True).label("muut\nlaitteet", loc="right")
        tallenna_kaavio(d, kohde / "vetovastus.png")


def kosketin(kohde: Path) -> None:
    """Painike, vetovastus, RC-suodin ja Schmitt-tulo."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        elm.Vdd().label("3,3 V")
        elm.Resistor().down().label("veto-\nvastus")
        raaka = elm.Dot().label("raaka", loc="left", **SOLMU)
        elm.Switch().down().label("painike", loc="bottom")
        elm.Ground()
        elm.Resistor().right().at(raaka.center).label("R1 10 kΩ")
        elm.Dot().label("suod", loc="top", **SOLMU)
        d.push()
        elm.Capacitor().down().label("C1\n22 nF", loc="bottom")
        elm.Ground()
        d.pop()
        elm.Line().right(1.2)
        logic.Schmitt().label("Schmitt-\ntulo", loc="bottom")
        elm.Line().right(0.6)
        elm.Dot(open=True)
        tallenna_kaavio(d, kohde / "kosketin.png")


def ac_piirit(kohde: Path) -> None:
    """Luvun 5 piirit: RC-alipäästö, RL-kuorma ja sarja-RLC."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=14)
        v = elm.SourceSin().up().label("V1")
        elm.Dot().label("sisaan", loc="top", **ISO_SOLMU)
        elm.Resistor().right().label("R1 1 kΩ", loc="bottom")
        elm.Dot().label("ulos", loc="top", **ISO_SOLMU)
        elm.Capacitor().down().label("C1\n100 nF", loc="bottom")
        elm.Line().left().to(v.start)
        elm.Ground().at(v.start)

        v = elm.SourceSin().up().at((7.0, 0)).label("V1\n230 V\n50 Hz")
        elm.Dot().label("verkko", loc="top", **ISO_SOLMU)
        elm.Resistor().right().label("R1 40 Ω", loc="bottom")
        elm.Dot().label("a", loc="top", **ISO_SOLMU)
        elm.Inductor2().down().label("L1\n95,5 mH", loc="bottom")
        elm.Line().left().to(v.start)
        elm.Ground().at(v.start)

        v = elm.SourceSin().up().at((14.0, 0)).label("V1")
        elm.Dot().label("sisaan", loc="top", **ISO_SOLMU)
        elm.Inductor2().right().label("L1 1 mH", loc="bottom")
        elm.Dot().label("a", loc="top", **ISO_SOLMU)
        elm.Capacitor().right().label("C1 10 nF", loc="bottom")
        elm.Dot().label("ulos", loc="top", **ISO_SOLMU)
        elm.Resistor().down().label("R1\n50 Ω", loc="bottom")
        elm.Line().left().to(v.start)
        elm.Ground().at(v.start)
        tallenna_kaavio(d, kohde / "ac-piirit.png")


def led(kohde: Path) -> None:
    """LED ja etuvastus."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        elm.Dot(open=True).label("lahto\n3,3 V", loc="left")
        elm.Resistor().right().label("R1 150 Ω")
        elm.Dot().label("a", loc="top", **SOLMU)
        elm.LED().down().label("D1", loc="bottom")
        elm.Ground()
        tallenna_kaavio(d, kohde / "led.png")


def _silta(d: schemdraw.Drawing, x: float, positiivinen: bool) -> None:
    """Diodisilta, jossa johtavat diodit ja virran reitti on korostettu."""
    def vari(johtaa: bool) -> str:
        return KOROSTUS if johtaa else VAALEA
    p = positiivinen
    h, w, k = 1.6, 3.0, 5.0      # diodin korkeus, haarojen väli, kuorma
    a, b = (x, h), (x + w, h)    # vaihtojännitesolmut
    # Vasen haara: D3 (0 -> a) ja D1 (a -> plus); oikea: D4 ja D2.
    elm.Diode().endpoints((x, 0), a).color(vari(not p)).label(
        "D3", loc="top")
    elm.Diode().endpoints(a, (x, 2 * h)).color(vari(p)).label(
        "D1", loc="top")
    elm.Diode().endpoints((x + w, 0), b).color(vari(p)).label(
        "D4", loc="bottom")
    elm.Diode().endpoints(b, (x + w, 2 * h)).color(vari(not p)).label(
        "D2", loc="bottom")
    elm.SourceSin().endpoints(a, b).label(
        "+        −" if p else "−        +", loc="top")
    elm.Dot().at(a).label("a", loc="left", **ISO_SOLMU)
    elm.Dot().at(b).label("b", loc="right", **ISO_SOLMU)
    # Kiskot: korostetaan vain se osa, jossa virta kulkee.
    elm.Line().endpoints((x, 2 * h), (x + w, 2 * h)).color(vari(p))
    elm.Line().endpoints((x + w, 2 * h), (x + k, 2 * h)).color(KOROSTUS)
    elm.Line().endpoints((x, 0), (x + w, 0)).color(vari(not p))
    elm.Line().endpoints((x + w, 0), (x + k, 0)).color(KOROSTUS)
    elm.Dot().at((x + w, 2 * h))
    elm.Dot().at((x + w, 0))
    kuorma = elm.Resistor().endpoints((x + k, 2 * h), (x + k, 0)).color(
        KOROSTUS).label("kuorma", loc="bottom")
    elm.CurrentLabelInline(direction="in").at(kuorma).color(KOROSTUS)
    elm.Label().at((x + k, 2 * h)).label("plus", loc="right", **ISO_SOLMU)
    elm.Ground().at((x + k, 0))
    elm.Label().at((x + k / 2, -1.2)).label(
        "positiivinen puolijakso:\nD1 ja D4 johtavat" if p
        else "negatiivinen puolijakso:\nD2 ja D3 johtavat")


def diodisilta(kohde: Path) -> None:
    """Diodisillan virran reitti kummallakin puolijaksolla."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=14)
        _silta(d, 0.0, True)
        _silta(d, 7.4, False)
        tallenna_kaavio(d, kohde / "diodisilta.png")


def zener(kohde: Path) -> None:
    """Zener-säädin."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        v = elm.SourceV().up().label("V1\n9…12 V")
        elm.Dot().label("sisaan", loc="top", **SOLMU)
        elm.Resistor().right().label("Rs 220 Ω")
        ulos = elm.Dot().label("ulos", loc="top", **SOLMU)
        elm.Zener().down().reverse().label("Dz\n5,1 V", loc="bottom")
        ala = elm.Dot()
        elm.Line().right(2.0).at(ulos.center)
        elm.Resistor().down().label("Rkuorma\n1 kΩ", loc="bottom")
        elm.Line().left().to(ala.center)
        elm.Line().to(v.start)
        elm.Ground().at(v.start)
        tallenna_kaavio(d, kohde / "zener.png")


def saadin(kohde: Path) -> None:
    """Lineaarisäädin mustana laatikkona kondensaattoreineen."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=14)
        ic = elm.Ic(pins=[elm.IcPin(name="in", side="left"),
                          elm.IcPin(name="out", side="right"),
                          elm.IcPin(name="gnd", side="bottom")],
                    size=(2.6, 1.6)).label("lineaarisäädin", loc="top")
        elm.Line().left(1.2).at(ic["in"])
        a = elm.Dot()
        elm.Line().left(1.2)
        elm.Dot(open=True).label("12 V", loc="left")
        elm.Capacitor().down().at(a.center).label("tulo-\nkond.",
                                                  loc="bottom")
        ga = elm.Ground()
        elm.Line().right(1.2).at(ic["out"])
        b = elm.Dot()
        elm.Line().right(1.2)
        elm.Dot(open=True).label("5 V", loc="right")
        elm.Capacitor().down().at(b.center).label("lähtö-\nkond.",
                                                  loc="bottom")
        elm.Ground()
        elm.Line().at(ic["gnd"]).toy(ga.start)
        elm.Ground()
        tallenna_kaavio(d, kohde / "saadin.png")


def mosfet_kytkin(kohde: Path) -> None:
    """N-kanavainen MOSFET alapuolen kytkimenä."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        q = elm.NFet().right().reverse().label("M1", loc="right")
        elm.Line().left(1.0).at(q.gate)
        elm.Dot(open=True).label("g\n(hila)", loc="left")
        elm.Dot().at(q.drain).label("d", loc="right", **SOLMU)
        elm.Resistor().up().at(q.drain).label("Rkuorma\n6 Ω")
        elm.Vdd().label("12 V")
        elm.Ground().at(q.source)
        tallenna_kaavio(d, kohde / "mosfet-kytkin.png")


def vapaakaynti_kaavio(kohde: Path) -> None:
    """Releen käämi, kytkin ja vapaakäyntidiodi."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=1.8, fontsize=10)
        q = elm.NFet().right().reverse().label("M1", loc="right")
        elm.Line().left(1.0).at(q.gate)
        elm.Dot(open=True).label("g", loc="left")
        nielu = elm.Dot().at(q.drain).label("d", loc="left", **SOLMU)
        elm.Resistor().up().label("Rkaami\n100 Ω")
        elm.Inductor2().up().label("Lkaami\n100 mH")
        yla = elm.Dot()
        elm.Vdd().label("12 V")
        elm.Line().right(2.2).at(nielu.center)
        elm.Diode().up().toy(yla.center).label("D1", loc="bottom")
        elm.Line().left().to(yla.center)
        elm.Ground().at(q.source)
        tallenna_kaavio(d, kohde / "vapaakaynti-kaavio.png")


def cmos_kaavio(kohde: Path) -> None:
    """CMOS-invertteri: P-kanava ylhäällä, N-kanava alhaalla."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=1.8, fontsize=10)
        n = elm.NFet().right().reverse().label("Mn", loc="right")
        elm.Ground().at(n.source)
        elm.Line().up(0.5).at(n.drain)
        ulos = elm.Dot()
        elm.Line().up(0.5)
        p = elm.PFet().right().reverse().anchor("drain").label("Mp", loc="right")
        elm.Vdd().at(p.source).label("1,8 V")
        elm.Line().left(0.8).at(n.gate)
        ga = elm.Line().up().toy(p.gate)
        elm.Line().right().tox(p.gate)
        keski = (ga.start[0], ulos.center[1])
        elm.Dot().at(keski)
        elm.Line().left(0.8).at(keski)
        elm.Dot(open=True).label("sisaan", loc="left")
        elm.Line().right(1.8).at(ulos.center)
        b = elm.Dot().label("ulos", loc="top", **SOLMU)
        elm.Capacitor().down().label("Ckuorma\n20 fF", loc="bottom")
        elm.Ground()
        elm.Line().right(0.8).at(b.center)
        elm.Dot(open=True)
        tallenna_kaavio(d, kohde / "cmos-invertteri.png")


def ylapuoli(kohde: Path) -> None:
    """Yläpuolen kytkin: N-kanava seuraajana ja P-kanava ohjaimineen."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=1.8, fontsize=14)
        # a) N-kanava
        q = elm.NFet().right().reverse().label("M1", loc="right")
        elm.Vdd().at(q.drain).label("12 V")
        elm.Line().left(0.8).at(q.gate)
        elm.Dot(open=True).label("ohj\n3,3 V", loc="left")
        elm.Dot().at(q.source).label("la", loc="right", **ISO_SOLMU)
        elm.Resistor().down().at(q.source).label("kuorma\n6 Ω",
                                                 loc="bottom")
        ga = elm.Ground()
        elm.Label().at((ga.start[0], ga.start[1] - 1.1)).label(
            "a) N-kanava:\nkuorma saa 1,5 V")
        # b) P-kanava ja NPN-ohjain
        p = elm.PFet().right().reverse().at((11.0, q.drain[1] - 0.2)).anchor(
            "source").label("M2", loc="right")
        yla = elm.Dot().at(p.source)
        elm.Vdd().label("12 V")
        elm.Dot().at(p.drain).label("lb", loc="right", **ISO_SOLMU)
        elm.Resistor().down().at(p.drain).toy(ga.start).label(
            "kuorma\n6 Ω", loc="bottom")
        gb = elm.Ground()
        elm.Line().left(1.6).at(p.gate)
        gp = elm.Dot().label("gp", loc="left", **ISO_SOLMU)
        elm.Resistor().up().toy(yla.center).label("Rveto\n10 kΩ")
        elm.Line().right().tox(yla.center)
        elm.Line().down(0.5).at(gp.center)
        npn = elm.BjtNpn().right().anchor("collector").label("Q1",
                                                             loc="right")
        elm.Line().at(npn.emitter).toy(gb.start)
        elm.Ground()
        elm.Resistor().left().at(npn.base).label("Rb 10 kΩ", loc="bottom")
        elm.Dot(open=True).label("ohj\n3,3 V", loc="left")
        elm.Label().at((gb.start[0] - 1.5, gb.start[1] - 1.1)).label(
            "b) P-kanava ja ohjaintransistori:\nkuorma saa 12 V")
        tallenna_kaavio(d, kohde / "ylapuoli.png")


def esarja(kohde: Path) -> None:
    """E12-sarjan arvot ja 10 %:n toleranssikaistat logaritmisella akselilla."""
    e12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2, 10.0]
    fig, ax = plt.subplots(figsize=(5.8, 1.3))
    for k, arvo in enumerate(e12):
        vari, y = (KOROSTUS, 0.22) if k % 2 == 0 else (TOINEN, -0.22)
        ax.barh(y, 0.2 * arvo, left=0.9 * arvo, height=0.4, color=vari,
                alpha=0.35)
        ax.plot([arvo, arvo], [y - 0.2, y + 0.2], color=vari, lw=1.5)
    ax.set_xscale("log")
    ax.set_xlim(0.88, 11.2)
    ax.set_xticks(e12)
    ax.set_xticklabels([f"{a:g}".replace(".", ",") for a in e12], fontsize=7)
    ax.set_xticks([], minor=True)
    ax.set_yticks([])
    ax.grid(False)
    ax.set_xlabel("arvo yhden dekadin sisällä (logaritminen asteikko)")
    fig.savefig(kohde / "esarja.png")
    plt.close(fig)


def nousuaika(kohde: Path) -> None:
    """I2C-väylän nousureuna kahdella vetovastuksella."""
    piiri = (ESIMERKIT / "04-nousuaika.cir").read_text("utf-8").replace(
        "print tr", "print tr\nwrdata nousu.dat v(sda)")
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    for rp, nimi, vari in (("4.7k", "4,7 kΩ", TOINEN),
                           ("1.5k", "1,5 kΩ", KOROSTUS)):
        tulos = simuloi(piiri.replace("Rp=4.7k", f"Rp={rp}"))
        data = tulos.data["nousu"]
        t30, t70 = tulos.arvot["t30"] * 1e9, tulos.arvot["t70"] * 1e9
        ax.plot(data[:, 0] * 1e9, data[:, 1], color=vari,
                label=f"Rp = {nimi}: nousuaika {t70 - t30:.0f} ns")
        ax.plot([t30, t70], [0.99, 2.31], "o", color=vari, ms=4)
    for taso, nimi in ((0.99, "30 %"), (2.31, "70 %")):
        ax.axhline(taso, color=HARMAA, lw=0.6, ls="--")
        ax.text(2950, taso + 0.05, nimi, fontsize=7, color=HARMAA,
                ha="right")
    ax.set_xlim(0, 3000)
    ax.set_xlabel("aika linjan vapautumisesta (ns)")
    ax.set_ylabel("u_sda (V)")
    ax.legend(fontsize=8, loc="lower right")
    fig.savefig(kohde / "nousuaika.png")
    plt.close(fig)


def teho_aallot(kohde: Path) -> None:
    """Jännite, virta ja hetkellinen teho RL-kuormassa."""
    # Mittaus "P" korvaa samannimisen vektorin (ngspice ei erota isoja ja
    # pieniä kirjaimia), joten aaltomuoto tallennetaan omalla nimellään.
    piiri = (ESIMERKIT / "05-loisteho.cir").read_text("utf-8").replace(
        "meas tran P", "let virta = -i(V1)\nlet hetki = v(verkko) * virta\n"
        "wrdata teho.dat v(verkko) virta hetki\nmeas tran P")
    tulos = simuloi(piiri)
    data = tulos.data["teho"]
    osa = data[data[:, 0] >= 0.16]
    t = (osa[:, 0] - 0.16) * 1e3
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.5, 3.6), sharex=True)
    a1.plot(t, osa[:, 1], color=HARMAA, label="u (V)")
    a1b = a1.twinx()
    a1b.plot(t, osa[:, 3], color=KOROSTUS, label="i (A)")
    a1b.grid(False)
    a1.set_ylabel("jännite (V)")
    a1b.set_ylabel("virta (A)")
    a1.set_ylim(-360, 360)
    a1b.set_ylim(-9, 9)
    viivat = a1.get_lines() + a1b.get_lines()
    a1.legend(viivat, ["u", "i"], fontsize=8, loc="upper right")
    p = osa[:, 5]
    a2.plot(t, p, color=TOINEN)
    a2.fill_between(t, p, 0, where=p < 0, color=TOINEN, alpha=0.35)
    a2.axhline(tulos.arvot["p"], color="black", lw=0.8, ls="--")
    a2.text(39.5, tulos.arvot["p"] + 60, "pätöteho P (keskiarvo)",
            fontsize=7, ha="right")
    a2.set_ylabel("teho p = u·i (W)")
    a2.set_xlabel("aika (ms)")
    fig.savefig(kohde / "teho-aallot.png")
    plt.close(fig)


def resonanssi(kohde: Path) -> None:
    """Sarja-RLC:n resonanssikäyrä kolmella vastuksella (eri Q)."""
    piiri = (ESIMERKIT / "05-resonanssi.cir").read_text("utf-8").replace(
        "print kaista", "print kaista\nwrdata res.dat vm(ulos)")
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    for r, vari in ((20, TOINEN), (50, KOROSTUS), (200, HARMAA)):
        data = simuloi(piiri.replace("R1 ulos 0 50",
                                     f"R1 ulos 0 {r}")).data["res"]
        q = (1e-3 / 10e-9) ** 0.5 / r
        ax.semilogx(data[:, 0] / 1e3, data[:, 1], color=vari,
                    label=f"R = {r} Ω, Q = {q:.1f}".replace(".", ","))
    ax.axhline(2 ** -0.5, color=HARMAA, lw=0.6, ls="--")
    ax.text(11, 0.73, "−3 dB", fontsize=7, color=HARMAA)
    ax.set_xlim(10, 250)
    ax.set_xlabel("taajuus (kHz)")
    ax.set_ylabel("u_R / u_sisään")
    ax.legend(fontsize=8)
    fig.savefig(kohde / "resonanssi.png")
    plt.close(fig)


def mosfet_kayrat(kohde: Path) -> None:
    """MOSFETin ominaiskäyrät, kuormasuora ja toimintapisteet."""
    fig, ax = plt.subplots(figsize=(5.5, 3.0))
    toiminta = simuloi("07-mosfet.cir").data["mosfet"]
    for u_gs, vari in ((2.0, TOINEN), (2.5, HARMAA), (3.3, KOROSTUS)):
        data = simuloi(f"""ominaiskäyrä
.include transistorit.lib
Vgs g 0 DC {u_gs}
Vds d 0 DC 0
M1 d g 0 0 NLOG
.control
dc Vds 0 12 0.02
let id = -i(Vds)
wrdata kayra.dat id
.endc
.end
""").data["kayra"]
        ax.plot(data[:, 0], data[:, 1], color=vari,
                label=f"U_GS = {u_gs:.1f} V".replace(".", ","))
        piste = toiminta[np.argmin(np.abs(toiminta[:, 0] - u_gs))]
        ax.plot(piste[1], piste[3], "o", color=vari, ms=5)
        if u_gs > 2.0:
            ax.annotate(f"{piste[1] * piste[3]:.2f} W".replace(".", ","),
                        (piste[1], piste[3]),
                        (1.2, 2.25 if u_gs > 3 else 1.6), fontsize=8,
                        color=vari, arrowprops={"arrowstyle": "-",
                                                "color": vari, "lw": 0.6})
        if u_gs == 2.0:
            ax.fill_between([0, piste[1]], 0, piste[3], color=vari,
                            alpha=0.15)
            ax.text(piste[1] / 2, piste[3] / 2, "häviö\nU·I = 5,9 W",
                    ha="center", va="center", fontsize=8)
    ax.plot([0, 12], [2, 0], color="black", lw=0.8, ls="--",
            label="kuormasuora (12 V, 6 Ω)")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 2.6)
    ax.set_xlabel("U_DS (V)")
    ax.set_ylabel("I_D (A)")
    ax.legend(fontsize=8, loc="upper right")
    fig.savefig(kohde / "mosfet-kayrat.png")
    plt.close(fig)


def vapaakaynti_aallot(kohde: Path) -> None:
    """Nielun jännite ja käämin virta ilman vapaakäyntidiodia ja sen kanssa."""
    piiri = (ESIMERKIT / "07-vapaakaynti.cir").read_text("utf-8").replace(
        "tran 10n 8m", "tran 100n 8m").replace(
        ".endc", "wrdata vk.dat v(d) i(Lkaami)\n.endc")
    ilman = simuloi(piiri.replace("D1 d vcc DPIEN", "* ei diodia"))
    kanssa = simuloi(piiri)
    # Sama ajo kuin testissä: huippuarvojen on vastattava esimerkin tulostetta.
    odotettu = (ESIMERKIT / "07-vapaakaynti.odotettu").read_text("utf-8")
    assert f"{ilman.arvot['huippu'] / 1e3:.2f} kV" in odotettu
    assert f"{kanssa.arvot['huippu']:.1f} V" in odotettu
    fig, axs = plt.subplots(2, 2, figsize=(5.8, 3.6), sharex="col")
    d = ilman.data["vk"]
    m = (d[:, 0] > 4.995e-3) & (d[:, 0] < 5.03e-3)
    t = (d[m, 0] - 5e-3) * 1e6
    axs[0, 0].plot(t, d[m, 1] / 1e3, color=TOINEN)
    axs[1, 0].plot(t, d[m, 3] * 1e3, color=TOINEN)
    axs[0, 0].set_title("ilman diodia", fontsize=9)
    axs[0, 0].set_ylabel("nielun jännite (kV)")
    axs[1, 0].set_ylabel("käämin virta (mA)")
    axs[1, 0].set_xlabel("aika katkaisusta (µs)")
    d = kanssa.data["vk"]
    m = (d[:, 0] > 4.5e-3) & (d[:, 0] < 8e-3)
    t = (d[m, 0] - 5e-3) * 1e3
    axs[0, 1].plot(t, d[m, 1], color=KOROSTUS)
    axs[1, 1].plot(t, d[m, 3] * 1e3, color=KOROSTUS)
    axs[0, 1].set_title("vapaakäyntidiodin kanssa", fontsize=9)
    axs[0, 1].set_ylabel("nielun jännite (V)")
    axs[1, 1].set_xlabel("aika katkaisusta (ms)")
    axs[0, 1].axhline(12, color=HARMAA, lw=0.6, ls="--")
    fig.tight_layout()
    fig.savefig(kohde / "vapaakaynti.png")
    plt.close(fig)


def kohinamarginaalit(kohde: Path) -> None:
    """CMOS-invertterin siirtokäyrä, logiikkatasot ja kohinamarginaalit."""
    data = simuloi("07-cmos.cir").data["cmos"]
    u_in, u_out = data[:, 0], data[:, 1]
    jyrkka = np.flatnonzero(np.gradient(u_out, u_in) < -1.0)
    il, ih = u_in[jyrkka[0]], u_in[jyrkka[-1]]
    oh, ol = u_out[jyrkka[0]], u_out[jyrkka[-1]]
    fig, ax = plt.subplots(figsize=(4.4, 3.2))
    ax.plot(u_in, u_out, color=KOROSTUS)
    ax.plot([il, ih], [oh, ol], "o", color=KOROSTUS, ms=5)
    for x, nimi in ((il, "U_IL"), (ih, "U_IH")):
        ax.axvline(x, color=HARMAA, lw=0.6, ls="--")
        ax.text(x, 1.86, nimi, fontsize=8, ha="center", color=HARMAA)
    for y, nimi in ((oh, "U_OH"), (ol, "U_OL")):
        ax.axhline(y, color=HARMAA, lw=0.6, ls="--")
        ax.text(1.83, y, nimi, fontsize=8, va="center", color=HARMAA)
    ax.axvspan(ol, il, color=KOROSTUS, alpha=0.12)
    ax.axvspan(ih, oh, color=KOROSTUS, alpha=0.12)
    ax.text((ol + il) / 2, 0.9, "marginaali\nalhaalla", fontsize=7,
            ha="center")
    ax.text((ih + oh) / 2, 0.9, "marginaali\nylhäällä", fontsize=7,
            ha="center")
    ax.set_xlim(0, 1.8)
    ax.set_ylim(0, 1.8)
    ax.set_xlabel("u_sisään (V)")
    ax.set_ylabel("u_ulos (V)")
    fig.savefig(kohde / "kohinamarginaalit.png")
    plt.close(fig)


def montecarlo(kohde: Path) -> None:
    """Monte Carlo -ajon lähtöjännitteiden jakauma ja huonoin tapaus."""
    import contextlib
    import io
    import runpy
    with contextlib.redirect_stdout(io.StringIO()):
        tulos = runpy.run_path(str(ESIMERKIT / "08-montecarlo.py"))
    fig, ax = plt.subplots(figsize=(5.5, 2.4))
    ax.hist(tulos["u"], bins=30, color=KOROSTUS, alpha=0.7)
    for raja in (3.580, 4.103):
        ax.axvline(raja, color=TOINEN, lw=1.2, ls="--")
    ax.axvline(3.837, color="black", lw=0.8)
    ax.text(3.585, ax.get_ylim()[1] * 0.9, "huonoin\ntapaus", fontsize=7,
            color=TOINEN, va="top")
    ax.set_xlabel("jakajan lähtöjännite (V)")
    ax.set_ylabel("jakajia")
    fig.savefig(kohde / "montecarlo.png")
    plt.close(fig)


def main() -> None:
    kohde = Path(sys.argv[1] if len(sys.argv) > 1 else "kuvat")
    kohde.mkdir(exist_ok=True)
    for piirtaja in (jakaja, esarja, silta, rc_rl, rc_lataus, vetovastus,
                     nousuaika, kosketin, varahtely, ac_piirit, bode,
                     teho_aallot, resonanssi, diodi, led, diodisilta,
                     tasasuuntaaja, zener, saadin, kytkin, mosfet_kytkin,
                     mosfet_kayrat, ylapuoli, vapaakaynti_kaavio,
                     vapaakaynti_aallot, cmos_kaavio, cmos,
                     kohinamarginaalit, montecarlo):
        piirtaja(kohde)
        print("piirretty:", piirtaja.__name__)


if __name__ == "__main__":
    main()
