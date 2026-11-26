"""Piirtää paketin kuvat: piirikaaviot (schemdraw) ja kuvaajat ngspicen
tuloksista. Käyttö: python3 kuvat/piirra.py kuvat

Kuvat ovat versionhallinnassa; skripti ajetaan uudelleen, kun piirit
tai esimerkit muuttuvat.
"""

from __future__ import annotations

import contextlib
import io
import math
import re
import runpy
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.path.insert(0, str(ESIMERKIT))
from spice import Tulos, simuloi  # noqa: E402

KOROSTUS = "#3E7F3C"
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
# Solmun nimi netlistissä: sama nimi kaaviossa ja .cir-tiedostossa.
SOLMU = {"color": HARMAA, "fontsize": 9}
# Sama suurissa kaavioissa, jotka ladotaan pienemmässä mittakaavassa.
ISO_SOLMU = {"color": HARMAA, "fontsize": 12}
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 100, "savefig.dpi": 200,
                     "savefig.bbox": "tight"})
schemdraw.use("matplotlib")


def tallenna_kaavio(d: schemdraw.Drawing, polku: Path) -> None:
    d.save(str(polku), dpi=200)


def ce_vahvistin(kohde: Path) -> None:
    """Yhteisemitterivahvistin jännitteenjakajabiasoinnilla."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        q = elm.BjtNpn(circle=True).label("Q1", loc="right")
        elm.Line().left(1.6).at(q.base)
        kanta = elm.Dot()
        d.push()
        elm.Resistor().up().label("R1 47 kΩ", loc="bottom")
        elm.Vdd().label("12 V")
        d.pop()
        elm.Resistor().down().label("R2 10 kΩ", loc="bottom")
        elm.Ground()
        elm.Capacitor().left().at(kanta.center).label("Cin 10 µF")
        elm.Dot(open=True).label("tulo", loc="left")
        elm.Line().up(0.6).at(q.collector)
        kollektori = elm.Dot()
        elm.Resistor().up().label("Rc 4,7 kΩ", loc="bottom")
        elm.Vdd().label("12 V")
        elm.Capacitor().right().at(kollektori.center).label("Cout 10 µF")
        elm.Dot(open=True).label("lähtö", loc="right")
        elm.Line().down(0.4).at(q.emitter)
        emitteri = elm.Dot()
        elm.Resistor().down().label("Re 1 kΩ", loc="bottom")
        elm.Ground()
        elm.Line().right(1.6).at(emitteri.center)
        elm.Capacitor().down().label("Ce 100 µF", loc="bottom")
        elm.Ground()
        tallenna_kaavio(d, kohde / "ce-vahvistin.png")


def invertoiva(kohde: Path) -> None:
    """Invertoiva vahvistin."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=11)
        op = elm.Opamp(leads=True)
        elm.Line().left(1.0).at(op.in1)
        miinus = elm.Dot()
        elm.Resistor().left().label("R1 10 kΩ")
        elm.Dot(open=True).label("u_tulo", loc="left")
        elm.Line().up(1.6).at(miinus.center)
        elm.Resistor().right().tox(op.out).label("R2 100 kΩ")
        elm.Line().down().toy(op.out)
        elm.Dot()
        elm.Line().right(0.8).at(op.out)
        elm.Dot(open=True).label("u_ulos", loc="right")
        elm.Line().down(0.6).at(op.in2)
        elm.Ground()
        tallenna_kaavio(d, kohde / "invertoiva.png")


def sallen_key(kohde: Path) -> None:
    """Sallen-Key-alipäästö, vahvistus 1."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=1.8, fontsize=10)
        elm.Dot(open=True).label("u_tulo", loc="left")
        elm.Resistor().right().label("R1")
        a = elm.Dot()
        elm.Resistor().right().label("R2")
        b = elm.Dot()
        elm.Capacitor().down().label("C2", loc="bottom")
        elm.Ground()
        elm.Line().right(1.2).at(b.center)
        op = elm.Opamp(leads=True).flip().anchor("in2").right()
        elm.Line().right(0.6).at(op.out)
        ulos = elm.Dot()
        elm.Line().right(0.6)
        elm.Dot(open=True).label("u_ulos", loc="right")
        elm.Line().down(0.8).at(op.in1)
        elm.Line().tox(ulos.center)
        elm.Line().toy(ulos.center)
        elm.Line().up(2.2).at(a.center)
        elm.Capacitor().right().tox(ulos.center).label("C1")
        elm.Line().toy(ulos.center)
        tallenna_kaavio(d, kohde / "sallen-key.png")


def bode_suodatin(kohde: Path) -> None:
    """Sallen-Key: SPICE ja siirtofunktio."""
    data = simuloi("04-sallen-key.cir").data["sk"]
    f, db = data[:, 0], data[:, 1]
    R, C1, C2 = 11.254e3, 20e-9, 10e-9
    h = 1 / np.polyval([R**2 * C1 * C2, 2 * R * C2, 1], 2j * math.pi * f)
    fig, ax = plt.subplots(figsize=(5.5, 2.8))
    ax.semilogx(f, db, color=KOROSTUS, lw=2.5, alpha=0.5, label="SPICE")
    ax.semilogx(f, 20 * np.log10(np.abs(h)), "--", color=HARMAA,
                label="siirtofunktio")
    ax.axhline(-3.01, color=TOINEN, lw=0.8, ls=":")
    ax.set_xlabel("taajuus (Hz)")
    ax.set_ylabel("vahvistus (dB)")
    ax.set_ylim(-80, 5)
    ax.legend(fontsize=8)
    fig.savefig(kohde / "sallen-key-bode.png")
    plt.close(fig)


def askel_suodattimet(kohde: Path) -> None:
    """Butterworth- ja Bessel-suodattimen askelvaste."""
    data = simuloi("04-bessel.cir").data["askel"]
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    t = data[:, 0] * 1e3
    ax.plot(t, data[:, 1], color=KOROSTUS, label="Butterworth, Q = 0,707")
    ax.plot(t, data[:, 3], color=TOINEN, label="Bessel, Q = 0,577")
    ax.set_xlabel("aika (ms)")
    ax.set_ylabel("lähtö (V)")
    ax.legend(fontsize=8, loc="lower right")
    fig.savefig(kohde / "askel-suodattimet.png")
    plt.close(fig)


def askel_kuorma(kohde: Path) -> None:
    """Seuraaja 1 nF:n kuormalla, ilman ja kanssa eristysvastuksen."""
    data = simuloi("05-askel.cir").data["askelvaste"]
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    t = data[:, 0] * 1e6
    ax.plot(t, data[:, 1] * 1e3, color=TOINEN, label="suoraan kytketty")
    ax.plot(t, data[:, 3] * 1e3, color=KOROSTUS,
            label="eristysvastus 47 Ω")
    ax.set_xlabel("aika (µs)")
    ax.set_ylabel("lähtö (mV)")
    ax.legend(fontsize=8)
    fig.savefig(kohde / "askel-kuorma.png")
    plt.close(fig)


def sigmadelta(kohde: Path) -> None:
    """Sigma-delta-modulaattorin spektri: kohinanmuokkaus."""
    M, jaksot = 2**16, 31
    x = 0.5 * np.sin(2 * np.pi * jaksot * np.arange(M) / M)
    dither = np.random.default_rng(1).uniform(-0.5, 0.5, M)
    v = np.empty(M)
    integraali, y = 0.0, 0.0
    for n in range(M):
        integraali += x[n] - y
        y = 1.0 if integraali + dither[n] >= 0 else -1.0
        v[n] = y
    ikkuna = np.hanning(M)
    spektri = np.abs(np.fft.rfft(v * ikkuna)) ** 2
    spektri /= spektri[jaksot]
    # Kohina keskiarvona logaritmisesti jaetuissa lokeroissa ilman
    # signaalin lokeroita; signaali merkitään omana pisteenään.
    kohina = spektri.copy()
    kohina[jaksot - 3:jaksot + 4] = np.nan
    rajat = np.unique(np.geomspace(1, len(spektri) - 1, 120).astype(int))
    keskit, tasot = [], []
    for a, b in zip(rajat[:-1], rajat[1:], strict=True):
        osa = kohina[a:b]
        if np.isfinite(osa).any():
            keskit.append((a + b) / 2 / M)
            tasot.append(np.nanmean(osa))
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    ax.loglog(keskit, tasot, color=KOROSTUS, label="kvantisointikohina")
    ax.loglog([jaksot / M], [1.0], "o", color=TOINEN, label="signaali")
    for osr in (16, 128):
        ax.axvline(0.5 / osr, color=HARMAA, lw=0.8, ls=":")
        ax.text(0.5 / osr, 1e-1, f" OSR {osr}", fontsize=7, color=HARMAA)
    ax.set_xlabel("taajuus / näytetaajuus")
    ax.set_ylabel("teho signaaliin nähden")
    ax.legend(fontsize=8, loc="lower right")
    fig.savefig(kohde / "sigmadelta.png")
    plt.close(fig)


def heijastus(kohde: Path) -> None:
    """Siirtolinjan kuorman jännite kolmessa tapauksessa."""
    data = simuloi("07-heijastus.cir").data["heijastus"]
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    t = data[:, 0] * 1e9
    ax.plot(t, data[:, 3], color=TOINEN, label="10 Ω, pää auki")
    ax.plot(t, data[:, 1], color=KOROSTUS, label="50 Ω, pää auki")
    ax.plot(t, data[:, 5], color=HARMAA, label="10 Ω, päätetty 50 Ω")
    ax.set_xlabel("aika (ns)")
    ax.set_ylabel("kuorman jännite (V)")
    ax.legend(fontsize=8, loc="lower right")
    fig.savefig(kohde / "heijastus.png")
    plt.close(fig)


def montecarlo(kohde: Path) -> None:
    """Monte Carlo -ajon kulma- ja rajataajuuksien jakaumat."""
    polku = ESIMERKIT / "04-montecarlo.py"
    with contextlib.redirect_stdout(io.StringIO()):
        tulos = runpy.run_path(str(polku))
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    bins = np.linspace(940, 1060, 31)
    ax.hist(tulos["f0"], bins=bins, color=KOROSTUS, alpha=0.7,
            label="kulmataajuus f0")
    ax.hist(tulos["f3"], bins=bins, color=TOINEN, alpha=0.5,
            label="-3 dB:n taajuus")
    ax.set_xlabel("taajuus (Hz)")
    ax.set_ylabel("piirejä")
    ax.legend(fontsize=8)
    fig.savefig(kohde / "montecarlo.png")
    plt.close(fig)


def vaihevara(kohde: Path) -> None:
    """Seuraajan silmukkavahvistus kolmella kuormakapasitanssilla."""
    A_ol, GBW, f_p2, R_ulos = 1e5, 10e6, 30e6, 50.0
    f = np.logspace(4, 8.5, 400)
    s = 2j * np.pi * f
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.5, 4.0), sharex=True)
    for C_L, vari, nimi in ((1e-12, KOROSTUS, "C_L = 1 pF"),
                            (1e-9, TOINEN, "C_L = 1 nF"),
                            (4.7e-9, HARMAA, "C_L = 4,7 nF")):
        T = A_ol / ((1 + s / (2 * np.pi * GBW / A_ol))
                    * (1 + s / (2 * np.pi * f_p2))
                    * (1 + s * R_ulos * C_L))
        ax1.semilogx(f, 20 * np.log10(np.abs(T)), color=vari, label=nimi)
        ax2.semilogx(f, np.degrees(np.unwrap(np.angle(T))), color=vari)
    ax1.axhline(0, color="black", lw=0.6)
    ax2.axhline(-180, color="black", lw=0.6)
    ax1.set_ylabel("|T| (dB)")
    ax1.set_ylim(-40, 60)
    ax2.set_ylabel("vaihe (astetta)")
    ax2.set_ylim(-270, -60)
    ax2.set_xlabel("taajuus (Hz)")
    ax1.legend(fontsize=8)
    fig.savefig(kohde / "vaihevara.png")
    plt.close(fig)


def seuraaja(kohde: Path) -> None:
    """Emitteriseuraaja jakajabiasoinnilla."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        q = elm.BjtNpn(circle=True).label("Q1", loc="right")
        elm.Line().up(0.8).at(q.collector)
        elm.Vdd().label("12 V")
        elm.Line().left(1.4).at(q.base)
        kanta = elm.Dot().label("b", loc="top", **SOLMU)
        d.push()
        elm.Resistor().up().label("R1 22 kΩ", loc="bottom")
        elm.Vdd().label("12 V")
        d.pop()
        elm.Resistor().down().label("R2 27 kΩ", loc="bottom")
        elm.Ground()
        elm.Capacitor().left().at(kanta.center).label("Cin 10 µF")
        elm.Resistor().left().label("Rs 1 kΩ")
        elm.Dot(open=True).label("s", loc="left")
        elm.Line().down(0.9).at(q.emitter)
        em = elm.Dot().label("e", loc="left", **SOLMU)
        elm.Resistor().down().label("Re 2,2 kΩ", loc="bottom")
        elm.Ground()
        elm.Capacitor().right().at(em.center).label("Cout 100 µF")
        ulos = elm.Dot().label("out", loc="top", **SOLMU)
        elm.Resistor().down().label("RL", loc="bottom")
        elm.Ground()
        elm.Line().right(0.6).at(ulos.center)
        elm.Dot(open=True)
        tallenna_kaavio(d, kohde / "seuraaja.png")


def mosfet_vahvistin(kohde: Path) -> None:
    """Yhteislähdevahvistin."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        q = elm.NFet().right().reverse().label("M1", loc="right")
        elm.Line().up(0.4).at(q.drain)
        nielu = elm.Dot().label("d", loc="left", **SOLMU)
        elm.Resistor().up().label("Rd 10 kΩ", loc="bottom")
        elm.Vdd().label("12 V")
        elm.Line().right(1.2).at(nielu.center)
        elm.Dot(open=True).label("lähtö", loc="right")
        elm.Line().left(1.2).at(q.gate)
        hila = elm.Dot().label("g", loc="top", **SOLMU)
        d.push()
        elm.Resistor().up().label("R1 1 MΩ", loc="bottom")
        elm.Vdd().label("12 V")
        d.pop()
        elm.Resistor().down().label("R2 220 kΩ", loc="bottom")
        elm.Ground()
        elm.Capacitor().left().at(hila.center).label("Cin 1 µF")
        elm.Dot(open=True).label("s", loc="left")
        elm.Line().down(0.3).at(q.source)
        lahde = elm.Dot().label("l", loc="left", **SOLMU)
        elm.Resistor().down().label("Rs 1 kΩ", loc="bottom")
        elm.Ground()
        elm.Line().right(2.4).at(lahde.center)
        elm.Capacitor().down().label("Cs 100 µF", loc="bottom")
        elm.Ground()
        tallenna_kaavio(d, kohde / "mosfet-vahvistin.png")


def eropari(kohde: Path) -> None:
    """Differentiaalipari, häntänä vastus."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        q1 = elm.BjtNpn(circle=True).right()
        q2 = elm.BjtNpn(circle=True).right().reverse().at(
            (q1.base[0] + 4.6, q1.base[1])).anchor("base")
        elm.Label().at((q1.base[0] + 0.5, q1.base[1] - 1.0)).label("Q1")
        elm.Label().at((q2.base[0] - 0.5, q2.base[1] - 1.0)).label("Q2")
        for q, rc, c, puoli in ((q1, "Rc1 10 kΩ", "c1", "top"),
                                (q2, "Rc2 10 kΩ", "c2", "bottom")):
            elm.Line().up(0.3).at(q.collector)
            elm.Dot().label(c, loc="left" if c == "c1" else "right",
                            **SOLMU)
            elm.Resistor().up().label(rc, loc=puoli)
            elm.Vdd().label("12 V")
        elm.Line().down(0.5).at(q1.emitter)
        elm.Line().right().tox(q2.emitter)
        elm.Line().up().toy(q2.emitter)
        keski = ((q1.emitter[0] + q2.emitter[0]) / 2, q1.emitter[1] - 0.5)
        elm.Dot().at(keski).label("e", loc="top", **SOLMU)
        elm.Resistor().down().at(keski).label("Ree 10 kΩ", loc="bottom")
        elm.Vss().label("−12 V")
        elm.Line().left(0.6).at(q1.base)
        elm.Dot(open=True).label("b1", loc="left")
        elm.Line().right(0.6).at(q2.base)
        elm.Dot(open=True).label("b2", loc="right")
        elm.Line().right(0.8).at((q2.collector[0], q2.collector[1] + 0.3))
        elm.Dot(open=True).label("lähtö", loc="right")
        tallenna_kaavio(d, kohde / "eropari.png")


def integraattori(kohde: Path) -> None:
    """Invertoiva integraattori ja tasavahvistusta rajoittava Rf."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        op = elm.Opamp(leads=True)
        elm.Line().left(0.8).at(op.in1)
        miinus = elm.Dot().label("inn", loc="bottom", **SOLMU)
        elm.Resistor().left().label("R1 10 kΩ")
        elm.Dot(open=True).label("in", loc="left")
        elm.Line().up(1.4).at(miinus.center)
        ylä = elm.Dot()
        elm.Capacitor().right().tox(op.out).label("C1 10 nF")
        oik = elm.Dot()
        elm.Line().down().toy(op.out)
        elm.Dot()
        elm.Line().up(1.2).at(ylä.center)
        elm.Resistor().right().tox(op.out).label("Rf 1 MΩ")
        elm.Line().down().to(oik.center)
        elm.Line().right(0.8).at(op.out)
        elm.Dot(open=True).label("out", loc="right")
        elm.Line().down(0.6).at(op.in2)
        elm.Ground()
        tallenna_kaavio(d, kohde / "integraattori.png")


def instrumentointi(kohde: Path) -> None:
    """Kolmen operaatiovahvistimen instrumentointivahvistin."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=12)
        x1 = elm.Opamp(leads=True).right().flip().label("X1", loc="center")
        x2 = elm.Opamp(leads=True).right().at((0, -6.4)).anchor(
            "in1").label("X2", loc="center")
        # Anturin navat plus-tuloihin
        elm.Line().left(0.8).at(x1.in2)
        elm.Dot(open=True).label("inp", loc="left")
        elm.Line().left(0.8).at(x2.in2)
        elm.Dot(open=True).label("inn", loc="left")
        # Rf1 - Rg - Rf2 lähtöjen välissä
        o1 = elm.Dot().at(x1.out).label("o1", loc="top", **ISO_SOLMU)
        o2 = elm.Dot().at(x2.out).label("o2", loc="bottom", **ISO_SOLMU)
        yla = (o1.center[0], x1.in1[1] - 1.2)
        ala = (o2.center[0], x2.in1[1] + 1.2)
        elm.Resistor().endpoints(o1.center, yla).label("Rf1\n10 kΩ",
                                                       loc="bottom")
        elm.Resistor().endpoints(yla, ala).label("Rg\n1 kΩ", loc="bottom")
        elm.Resistor().endpoints(ala, o2.center).label("Rf2\n10 kΩ",
                                                       loc="bottom")
        elm.Dot().at(yla).label("a1", loc="right", **ISO_SOLMU)
        elm.Dot().at(ala).label("a2", loc="right", **ISO_SOLMU)
        elm.Line().at(x1.in1).toy(yla)
        elm.Line().tox(yla)
        elm.Line().at(x2.in1).toy(ala)
        elm.Line().tox(ala)
        # Erovahvistin: plus ylhäällä, jolloin johdot eivät risteä
        keski = (o1.center[1] + o2.center[1]) / 2
        x3 = elm.Opamp(leads=True).right().flip().at(
            (o1.center[0] + 6.6, keski)).anchor("in1").label(
            "X3", loc="center")
        elm.Line().right(0.6).at(o1.center)
        elm.Resistor().right().length(3.4).label("R5 10 kΩ")
        p = elm.Dot().label("p", loc="top", **ISO_SOLMU)
        elm.Line().right(0.6).at(o2.center)
        elm.Resistor().right().length(3.4).label("R3 10 kΩ", loc="bottom")
        m = elm.Dot().label("m", loc="bottom", **ISO_SOLMU)
        elm.Line().at(p.center).tox(x3.in2[0] - 0.4)
        elm.Line().toy(x3.in2)
        elm.Line().tox(x3.in2)
        elm.Line().at(m.center).tox(x3.in1[0] - 0.4)
        elm.Dot()
        elm.Line().toy(x3.in1)
        elm.Line().tox(x3.in1)
        elm.Resistor().down().at(p.center).length(1.8).label(
            "R6\n10 kΩ", loc="top")
        elm.Ground()
        elm.Line().right(0.6).at(x3.out)
        ulos = elm.Dot()
        elm.Line().right(0.6)
        elm.Dot(open=True).label("out", loc="right")
        elm.Line().at(ulos.center).toy(m.center)
        elm.Resistor().left().tox(x3.in1[0] - 0.4).label(
            "R4 10 kΩ", loc="bottom")
        tallenna_kaavio(d, kohde / "instrumentointi.png")


def tasonsiirto(kohde: Path) -> None:
    """Ei-invertoiva summaaja tasonsiirtona."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        op = elm.Opamp(leads=True).flip()
        elm.Line().left(0.6).at(op.in2)
        p = elm.Dot().label("p", loc="top", **SOLMU)
        elm.Resistor().left().label("R1 10 kΩ")
        elm.Dot(open=True).label("in\n±1 V", loc="left")
        elm.Line().down(1.2).at(p.center)
        elm.Resistor().left().label("R2 10 kΩ")
        elm.Dot(open=True).label("ref\n1,1 V", loc="left")
        elm.Line().down(1.6).at(op.in1)
        n = elm.Dot().label("n", loc="left", **SOLMU)
        elm.Resistor().down().label("R3 10 kΩ", loc="bottom")
        elm.Ground()
        elm.Resistor().right().at(n.center).tox(op.out).label("R4 20 kΩ")
        elm.Line().up().toy(op.out)
        elm.Dot()
        elm.Line().right(0.8).at(op.out)
        elm.Dot(open=True).label("out\n0,15…3,15 V", loc="right")
        tallenna_kaavio(d, kohde / "tasonsiirto.png")


def mfb(kohde: Path) -> None:
    """Multiple feedback -alipäästö."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        elm.Dot(open=True).label("in", loc="left")
        elm.Resistor().right().label("R1")
        a = elm.Dot().label("a", loc="bottom", **SOLMU)
        d.push()
        elm.Capacitor().down().label("C1", loc="bottom")
        elm.Ground()
        d.pop()
        elm.Resistor().right().label("R3")
        m = elm.Dot().label("m", loc="bottom", **SOLMU)
        elm.Line().right(0.6)
        op = elm.Opamp(leads=True).anchor("in1")
        elm.Line().down(0.6).at(op.in2)
        elm.Ground()
        elm.Line().up(1.2).at(m.center)
        elm.Capacitor().right().tox(op.out).label("C2")
        c2 = elm.Dot()
        elm.Line().down().toy(op.out)
        elm.Dot()
        elm.Line().up(2.6).at(a.center)
        elm.Resistor().right().tox(op.out).label("R2")
        elm.Line().down().to(c2.center)
        elm.Line().right(0.8).at(op.out)
        elm.Dot(open=True).label("out", loc="right")
        tallenna_kaavio(d, kohde / "mfb.png")


def silmukka(kohde: Path) -> None:
    """Silmukan katkaisu vaihtosignaalilta ja eristysvastus."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=14)
        # a) silmukan katkaisu
        op = elm.Opamp(leads=True).right().flip()
        elm.Line().left(0.6).at(op.in2)
        elm.Ground()
        elm.Line().down(1.6).at(op.in1)
        inn = elm.Dot().label("inn", loc="top", ofst=(0.5, 0), **ISO_SOLMU)
        elm.Inductor2().right().tox(op.out).label("Lkatko", loc="bottom")
        elm.Line().up().toy(op.out)
        elm.Dot().label("out", loc="top", **ISO_SOLMU)
        elm.Line().right(1.4)
        elm.Capacitor().down().label("CL", loc="bottom")
        elm.Ground()
        elm.Capacitor().left().at(inn.center).label("Ckatko", loc="bottom")
        elm.Dot().label("t", loc="top", **ISO_SOLMU)
        elm.SourceSin().down().label("Vt", loc="top")
        maa = elm.Ground()
        elm.Label().at((1.0, maa.start[1] - 1.4)).label(
            "a) silmukka katkaistu\nvaihtosignaalilta")
        # b) eristysvastus
        op2 = elm.Opamp(leads=True).right().flip().at((7.6, 0))
        elm.Line().left(0.8).at(op2.in2)
        elm.Dot(open=True).label("in", loc="left")
        elm.Line().down(1.2).at(op2.in1)
        elm.Line().right().tox(op2.out)
        elm.Line().up().toy(op2.out)
        elm.Dot().label("o2", loc="top", **ISO_SOLMU)
        elm.Resistor().right().label("Riso 47 Ω", loc="bottom")
        elm.Dot().label("kuorma", loc="top", **ISO_SOLMU)
        elm.Capacitor().down().label("C2\n1 nF", loc="bottom")
        elm.Ground()
        elm.Label().at((10.0, maa.start[1] - 1.4)).label(
            "b) eristysvastus kuorman\nja lähdön välissä")
        tallenna_kaavio(d, kohde / "silmukka.png")


def naytteenotto(kohde: Path) -> None:
    """Näytteenotto- ja pitopiiri."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        elm.Dot(open=True).label("in", loc="left")
        elm.Switch().right().label("S1\n100 Ω")
        elm.Dot().label("c", loc="top", **SOLMU)
        d.push()
        elm.Capacitor().down().label("Ch\n1 nF", loc="bottom")
        elm.Ground()
        d.pop()
        elm.Line().right(1.0)
        op = elm.Opamp(leads=True).flip().anchor("in2")
        elm.Line().down(1.0).at(op.in1)
        elm.Line().right().tox(op.out)
        elm.Line().up().toy(op.out)
        elm.Dot()
        elm.Line().right(0.8).at(op.out)
        elm.Dot(open=True).label("AD-muuntimelle", loc="right")
        tallenna_kaavio(d, kohde / "naytteenotto.png")


def r2r(kohde: Path) -> None:
    """Nelibittinen R-2R-tikapuu."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=12)
        vali = 2.6
        elm.Resistor().endpoints((-1.4, 0), (-1.4, -2.0)).label(
            "2R", loc="top")
        elm.Ground().at((-1.4, -2.0))
        elm.Line().endpoints((-1.4, 0), (0, 0))
        for i in range(4):
            x = vali * i
            elm.Dot().at((x, 0)).label(f"n{i}", loc="top", **ISO_SOLMU)
            elm.Resistor().endpoints((x, 0), (x, -2.0)).label(
                "2R", loc="bottom")
            elm.Dot(open=True).at((x, -2.0)).label(
                f"bitti {i}" + (" (LSB)" if i == 0 else
                                " (MSB)" if i == 3 else ""), loc="bottom")
            if i < 3:
                elm.Resistor().endpoints((x, 0), (x + vali, 0)).label("R")
        elm.Line().endpoints((3 * vali, 0), (3 * vali + 1.2, 0))
        elm.Dot(open=True).at((3 * vali + 1.2, 0)).label("lähtö",
                                                         loc="right")
        tallenna_kaavio(d, kohde / "r2r.png")


def paatokset(kohde: Path) -> None:
    """Siirtolinjan sarja- ja rinnakkaispäätös."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=12)
        for y, rs, loppu, nimi in (
                (0.0, "Rs = 50 Ω", None, "sarjapäätös: lähde sovitettu"),
                (-4.0, "Rs = 10 Ω", "RL = 50 Ω",
                 "rinnakkaispäätös: kuorma sovitettu")):
            v = elm.SourcePulse().up().at((0, y)).label("Vs")
            elm.Resistor().right().label(rs)
            linja = elm.Coax(length=4.0).label("Z0 = 50 Ω, viive 5 ns",
                                               loc="top")
            elm.Line().at(linja.shieldstart).toy(v.start)
            elm.Line().right(0.8).at(linja.end)
            pää = elm.Dot()
            if loppu:
                elm.Resistor().down().toy(v.start).label(loppu, loc="bottom")
                elm.Line().left().to(v.start)
            else:
                elm.Line().at(v.start).tox(linja.shieldstart)
            elm.Line().right(0.6).at(pää.center)
            elm.Dot(open=True).label("kuorma", loc="right")
            elm.Ground().at(v.start)
            elm.Label().at((4.5, y - 1.0)).label(nimi)
        tallenna_kaavio(d, kohde / "paatokset.png")


def vertailija_kaavio(kohde: Path) -> None:
    """Vertailija, jossa hystereesi tehdään positiivisella takaisinkytkennällä."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        op = elm.Opamp(leads=True)
        elm.Line().left(1.0).at(op.in1)
        elm.Dot(open=True).label("in", loc="left")
        elm.Line().down(1.2).at(op.in2)
        p = elm.Dot().label("p", loc="left", **SOLMU)
        elm.Resistor().down().label("R1 10 kΩ", loc="bottom")
        elm.Dot(open=True).label("ref 1,65 V", loc="bottom")
        elm.Resistor().right().at(p.center).tox(op.out).label("R2 100 kΩ",
                                                               loc="bottom")
        elm.Line().up().toy(op.out)
        elm.Dot()
        elm.Line().right(0.8).at(op.out)
        elm.Dot(open=True).label("out", loc="right")
        tallenna_kaavio(d, kohde / "vertailija-kaavio.png")


def _ajo(piiri: str, lisays: str) -> Tulos:
    """Ajaa netlistin niin, että .endc:n eteen on lisätty komentoja."""
    return simuloi(piiri.replace(".endc", lisays + "\n.endc"))


def ce_aallot(kohde: Path) -> None:
    """Yhteisemitterivahvistimen lähtö pienellä ja suurella signaalilla."""
    perus = (ESIMERKIT / "02-ce-vahvistin.cir").read_text("utf-8")
    ohjaus = perus[perus.index(".control"):]
    perus = perus.replace(ohjaus, ".control\ntran 1u 2.2m\n"
                          "wrdata ce.dat v(out)\n.endc\n.end\n")
    degen = perus.replace("Re e 0 1k\nCe e 0 100u",
                          "Re1 e e2 180\nRe2 e2 0 820\nCe e2 0 100u")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 2.5))
    for ax, piiri, tapaukset in (
            (a1, perus, (("1m", "1 mV", KOROSTUS), ("20m", "20 mV", TOINEN))),
            (a2, degen, (("20m", "20 mV", KOROSTUS),))):
        for amp, nimi, vari in tapaukset:
            data = simuloi(piiri.replace("Vs s 0 DC 0 AC 1",
                                         f"Vs s 0 SIN(0 {amp} 10k)")
                           ).data["ce"]
            m = data[:, 0] > 2.0e-3
            u = data[m, 1]
            ax.plot((data[m, 0] - 2e-3) * 1e6, u / np.abs(u).max(),
                    color=vari,
                    label=f"tulo {nimi}, lähtö {np.ptp(u) / 2:.2f} V"
                    .replace(".", ","))
        ax.set_xlabel("aika (µs)")
        ax.set_ylim(-1.15, 1.6)
        ax.legend(fontsize=7, loc="upper right")
    a1.set_title("emitterivastus ohitettu", fontsize=9)
    a2.set_title("180 Ω ohittamatta", fontsize=9)
    a1.set_ylabel("lähtö (huippuun skaalattu)")
    fig.tight_layout()
    fig.savefig(kohde / "ce-aallot.png")
    plt.close(fig)


def ce_bode(kohde: Path) -> None:
    """Yhteisemitterivahvistimen taajuusvaste ja rajataajuudet."""
    tulos = _ajo((ESIMERKIT / "02-ce-vahvistin.cir").read_text("utf-8"),
                 "wrdata cebode.dat vdb(out)")
    data = tulos.data["cebode"]
    fig, ax = plt.subplots(figsize=(5.5, 2.5))
    ax.semilogx(data[:, 0], data[:, 1], color=KOROSTUS)
    ax.axhline(tulos.arvot["a_kesk"] - 3.01, color=HARMAA, lw=0.6, ls="--")
    for f, nimi in ((tulos.arvot["f_ala"], "alaraja"),
                    (tulos.arvot["f_yla"], "yläraja")):
        ax.axvline(f, color=HARMAA, lw=0.6, ls=":")
        ax.text(f, 12, f" {nimi}", fontsize=7, color=HARMAA)
    ax.set_ylim(10, 48)
    ax.set_xlabel("taajuus (Hz)")
    ax.set_ylabel("vahvistus (dB)")
    fig.savefig(kohde / "ce-bode.png")
    plt.close(fig)


def kaista_bode(kohde: Path) -> None:
    """Suljetun silmukan vahvistus kolmella vahvistuksella ja avoin silmukka."""
    perus = (ESIMERKIT / "03-kaistanleveys.cir").read_text("utf-8")
    ohjaus = perus[perus.index(".control"):]
    fig, ax = plt.subplots(figsize=(5.5, 2.8))
    f = np.logspace(0, 7, 300)
    ax.semilogx(f, 20 * np.log10(np.abs(1e5 / (1 + 1j * f / 10))),
                color=HARMAA, ls="--", label="avoin silmukka")
    for r2, g, vari in (("0.001", 1, KOROSTUS), ("9k", 10, TOINEN),
                        ("99k", 100, "#7A5C99")):
        data = simuloi(perus.replace(".param R2=9k", f".param R2={r2}")
                       .replace(ohjaus, ".control\nac dec 50 1 10Meg\n"
                                "wrdata kaista.dat vdb(out)\n.endc\n.end\n")
                       ).data["kaista"]
        ax.semilogx(data[:, 0], data[:, 1], color=vari,
                    label=f"vahvistus {g}")
    ax.set_ylim(-20, 105)
    ax.set_xlim(1, 1e7)
    ax.set_xlabel("taajuus (Hz)")
    ax.set_ylabel("vahvistus (dB)")
    ax.legend(fontsize=8)
    fig.savefig(kohde / "kaista-bode.png")
    plt.close(fig)


def integraattori_aallot(kohde: Path) -> None:
    """Integraattorin tulo (kanttiaalto) ja lähtö (kolmioaalto)."""
    data = _ajo((ESIMERKIT / "03-integraattori.cir").read_text("utf-8"),
                "wrdata integ.dat v(in) v(out)").data["integ"]
    m = data[:, 0] >= 57e-3
    t = (data[m, 0] - 57e-3) * 1e3
    fig, ax = plt.subplots(figsize=(5.5, 2.3))
    ax.plot(t, data[m, 1], color=HARMAA, label="tulo")
    ax.plot(t, data[m, 3], color=KOROSTUS, label="lähtö")
    ax.set_xlabel("aika (ms)")
    ax.set_ylabel("jännite (V)")
    ax.legend(fontsize=8, loc="upper right")
    fig.savefig(kohde / "integraattori-aallot.png")
    plt.close(fig)


def opamp_rajat(kohde: Path) -> None:
    """Lähdön leikkautuminen ja nousunopeuden rajoittama askel."""
    perus = (ESIMERKIT / "03-rajat.cir").read_text("utf-8")
    # Staattinen siirtokäyrä: sama kytkentä kuin esimerkissä, tuloa
    # pyyhkäistään. Siniaalto kuvataan käyrän läpi (pätee taajuuksilla,
    # joilla nousunopeus ja toipuminen eivät rajoita).
    siirto = _ajo(perus, "dc Vin1 -0.8 0.8 0.005\n"
                  "wrdata siirto.dat v(o1) v(o2)").data["siirto"]
    askel = _ajo(perus, "wrdata askel.dat v(o3)").data["askel"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 2.6))
    t = np.linspace(0, 2, 400)
    tulo = 0.6 * np.sin(2 * np.pi * t)
    a1.plot(t, -10 * tulo, color=HARMAA, lw=0.8, ls="--",
            label="ihanteellinen")
    a1.plot(t, np.interp(tulo, siirto[:, 0], siirto[:, 3]), color=KOROSTUS,
            label="rail-to-rail")
    a1.plot(t, np.interp(tulo, siirto[:, 0], siirto[:, 1]), color=TOINEN,
            label="perinteinen")
    for raja in (5, -5):
        a1.axhline(raja, color="black", lw=0.6)
    a1.set_xlabel("aika (ms)")
    a1.set_ylabel("lähtö (V)")
    a1.set_ylim(-7.5, 10.5)
    a1.legend(fontsize=7, loc="upper right", ncol=2)
    a1.set_title("lähdön jännitealue (syöttö ±5 V)", fontsize=9)
    t = askel[:, 0] * 1e6
    a2.plot(t, askel[:, 1], color=TOINEN, label="simuloitu")
    gbw = 8 * (1 - np.exp(-2 * np.pi * 1e6 * (askel[:, 0] - 1e-6)))
    a2.plot(t, np.where(t > 1, gbw, 0), color=HARMAA, ls="--",
            label="pelkkä GBW")
    a2.set_xlabel("aika (µs)")
    a2.set_title("nousunopeus 0,5 V/µs", fontsize=9)
    a2.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(kohde / "opamp-rajat.png")
    plt.close(fig)


def vertailija(kohde: Path) -> None:
    """Hystereesisilmukka ja kohiseva tulo ilman hystereesiä ja sen kanssa."""
    with contextlib.redirect_stdout(io.StringIO()):
        esim = runpy.run_path(str(ESIMERKIT / "05-vertailija.py"))
    piiri, pwl = esim["piiri"], esim["pwl"]
    silmukka = simuloi(piiri).data["vertailija"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 2.7),
                                 gridspec_kw={"width_ratios": [1, 1.5]})
    a1.plot(silmukka[:, 1], silmukka[:, 3], color=KOROSTUS)
    for x, nimi in ((esim["alempi"], "1,5 V"), (esim["ylempi"], "1,8 V")):
        a1.axvline(x, color=HARMAA, lw=0.6, ls=":")
        a1.text(x, 3.45, nimi, fontsize=7, ha="center", color=HARMAA)
    a1.annotate("", (1.8, 1.2), (1.8, 2.4),
                arrowprops={"arrowstyle": "->", "color": KOROSTUS})
    a1.annotate("", (1.5, 2.4), (1.5, 1.2),
                arrowprops={"arrowstyle": "->", "color": KOROSTUS})
    a1.set_xlim(1.0, 2.3)
    a1.set_ylim(-0.2, 3.8)
    a1.set_xlabel("tulo (V)")
    a1.set_ylabel("lähtö (V)")
    for k, (r2, nimi, vari) in enumerate((("1G", "ilman hystereesiä", TOINEN),
                                          ("100k", "hystereesi 0,3 V",
                                           KOROSTUS))):
        netlist = (piiri.replace(".param R2=100k", f".param R2={r2}")
                   .replace("PULSE(0 3.3 0 10m 10m 1u 20m)", f"PWL({pwl})")
                   .replace("tran 2u 20m", "tran 1u 10m"))
        netlist = "\n".join(r for r in netlist.splitlines()
                            if not r.startswith("meas")) + "\n"
        data = simuloi(netlist).data["vertailija"]
        if k == 0:
            a2.plot(data[:, 0] * 1e3, data[:, 1], color=HARMAA, lw=0.6,
                    label="tulo")
        a2.plot(data[:, 0] * 1e3, data[:, 3] / 3.3 * 0.25 + 2.35 + 0.4 * k,
                color=vari, label=f"lähtö, {nimi}")
    a2.axhline(1.65, color=HARMAA, lw=0.6, ls="--")
    a2.set_ylim(1.1, 3.6)
    a2.set_yticks([1.2, 1.5, 1.8, 2.1])
    a2.set_xlabel("aika (ms)")
    a2.set_ylabel("tulo (V)")
    a2.legend(fontsize=7, loc="upper left", ncol=1)
    fig.tight_layout()
    fig.savefig(kohde / "vertailija.png")
    plt.close(fig)


def kvantisointi(kohde: Path) -> None:
    """Kolmibittisen kvantisoijan porrasfunktio ja virhe."""
    u = np.linspace(0, 1, 2000)
    lsb = 1 / 8
    q = np.clip(np.floor(u / lsb + 0.5), 0, 7) * lsb
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.0, 3.2), sharex=True,
                                 gridspec_kw={"height_ratios": [2, 1]})
    a1.plot(u, u, color=HARMAA, lw=0.8, ls="--", label="tulo")
    a1.plot(u, q, color=KOROSTUS, label="kvantisoitu (3 bittiä)")
    a1.set_ylabel("lähtö / U_ref")
    a1.legend(fontsize=8)
    a2.plot(u, (q - u) / lsb, color=TOINEN)
    a2.set_ylim(-1.2, 0.8)
    a2.set_ylabel("virhe (LSB)")
    a2.set_xlabel("tulo / U_ref")
    fig.savefig(kohde / "kvantisointi.png")
    plt.close(fig)


def sar_haku(kohde: Path) -> None:
    """SAR-muuntimen binäärihaku esimerkin 06-sar.py tulosteesta."""
    rivit = (ESIMERKIT / "06-sar.odotettu").read_text("utf-8")
    kokeet = [(float(u), tulos == "1") for u, tulos in
              re.findall(r"= ([0-9.]+) V -> ([01])", rivit)]
    fig, ax = plt.subplots(figsize=(5.5, 2.5))
    askeleet = np.arange(len(kokeet))
    arvot = [u for u, _ in kokeet]
    ax.step(np.append(askeleet, len(kokeet)), arvot + [arvot[-1]],
            where="post", color=HARMAA, lw=0.8)
    for k, (u, pidetaan) in enumerate(kokeet):
        ax.plot(k + 0.5, u, "o" if pidetaan else "x",
                color=KOROSTUS if pidetaan else TOINEN, ms=6)
    ax.axhline(1.234, color="black", lw=0.8, ls="--")
    ax.text(7.95, 1.26, "tulo 1,234 V", fontsize=7, ha="right")
    ax.plot([], [], "o", color=KOROSTUS, label="bitti jää päälle")
    ax.plot([], [], "x", color=TOINEN, label="bitti pois")
    ax.set_xticks(askeleet + 0.5)
    ax.set_xticklabels([f"bitti {7 - k}" for k in askeleet], fontsize=7)
    ax.set_ylabel("DA-muuntimen koejännite (V)")
    ax.legend(fontsize=7, loc="upper right")
    fig.savefig(kohde / "sar-haku.png")
    plt.close(fig)


def r2r_virheet(kohde: Path) -> None:
    """R-2R-muuntimen INL ja DNL, kun MSB-vastus poikkeaa 5 %."""
    with contextlib.redirect_stdout(io.StringIO()):
        esim = runpy.run_path(str(ESIMERKIT / "06-r2r.py"))
    u = np.array(esim["simuloi_muunnin"](0.05))
    lsb = esim["lsb"]
    koodit = np.arange(16)
    # INL päätepisteiden kautta kulkevaan suoraan nähden.
    suora = u[0] + (u[-1] - u[0]) * koodit / 15
    inl = (u - suora) / ((u[-1] - u[0]) / 15)
    dnl = np.diff(u) / lsb - 1
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 2.4))
    a1.bar(koodit, inl, color=KOROSTUS)
    a1.set_xlabel("koodi")
    a1.set_ylabel("INL (LSB)")
    a2.bar(koodit[:-1] + 0.5, dnl, color=TOINEN)
    a2.set_xlabel("koodien väli")
    a2.set_ylabel("DNL (LSB)")
    fig.tight_layout()
    fig.savefig(kohde / "r2r-virheet.png")
    plt.close(fig)


def asettuminen(kohde: Path) -> None:
    """Pitokondensaattorin asettuminen ja puolen LSB:n rajat."""
    data = _ajo((ESIMERKIT / "06-naytteenotto.cir").read_text("utf-8"),
                "wrdata sh.dat v(c)").data["sh"]
    t = (data[:, 0] - 10e-9) / 100e-9          # aikavakioina
    m = (t > 0) & (t < 14)
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    ax.semilogy(t[m], np.abs(1 - data[m, 1]), color=KOROSTUS,
                label="virhe loppuarvosta")
    for bitit, vari in ((8, HARMAA), (12, TOINEN), (16, "#7A5C99")):
        raja = 2.0 ** -(bitit + 1)
        ax.axhline(raja, color=vari, lw=0.8, ls="--")
        ax.text(0.2, raja * 1.3, f"½ LSB, {bitit} bittiä", fontsize=7,
                color=vari)
        ax.axvline(np.log(2 ** (bitit + 1)), color=vari, lw=0.6, ls=":")
    ax.set_xlim(0, 14)
    ax.set_ylim(3e-6, 1.5)
    ax.set_xlabel("aika kytkimen sulkeutumisesta (aikavakiota RC)")
    ax.set_ylabel("virhe / täysi alue")
    fig.savefig(kohde / "asettuminen.png")
    plt.close(fig)


def kohina(kohde: Path) -> None:
    """Kohinatiheys taajuuden funktiona ja kohinabudjetin osuudet."""
    with contextlib.redirect_stdout(io.StringIO()):
        esim = runpy.run_path(str(ESIMERKIT / "07-kohinabudjetti.py"))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 2.5))
    f = np.logspace(0, 5, 200)
    valkoinen, kulma = 10.0, 100.0
    a1.loglog(f, valkoinen * np.sqrt(1 + kulma / f), color=KOROSTUS)
    a1.axhline(valkoinen, color=HARMAA, lw=0.6, ls="--")
    a1.axvline(kulma, color=HARMAA, lw=0.6, ls=":")
    a1.text(kulma * 1.2, 60, "1/f-kulma", fontsize=7, color=HARMAA)
    a1.set_xlabel("taajuus (Hz)")
    a1.set_ylabel("kohinatiheys (nV/√Hz)")
    nimet = ["vahvistin\njännite", "vahvistin\nvirta · R_s",
             "lähteen\nterminen"]
    osat = np.array(list(esim["osat"].values())) * 1e9
    a2.bar(nimet + ["yhteensä"], list(osat) + [esim["yhteensa"] * 1e9],
           color=[KOROSTUS, KOROSTUS, KOROSTUS, TOINEN])
    a2.tick_params(axis="x", labelsize=7)
    a2.set_ylabel("nV/√Hz")
    fig.tight_layout()
    fig.savefig(kohde / "kohina.png")
    plt.close(fig)


def ohitus_aallot(kohde: Path) -> None:
    """Käyttöjännitteen notkahdus ilman ohituskondensaattoria ja sen kanssa."""
    data = _ajo((ESIMERKIT / "07-ohitus.cir").read_text("utf-8"),
                "wrdata ohitus.dat v(p1) v(p2)").data["ohitus"]
    fig, ax = plt.subplots(figsize=(5.5, 2.5))
    t = data[:, 0] * 1e9
    ax.plot(t, data[:, 1], color=TOINEN, label="ilman ohitusta")
    ax.plot(t, data[:, 3], color=KOROSTUS, label="100 nF piirin vieressä")
    ax.axhline(3.3, color=HARMAA, lw=0.6, ls="--")
    ax.set_xlim(0, 60)
    ax.set_xlabel("aika (ns)")
    ax.set_ylabel("piirin käyttöjännite (V)")
    ax.legend(fontsize=8, loc="lower right")
    fig.savefig(kohde / "ohitus.png")
    plt.close(fig)


def _saadin(x0: float, ldo: bool) -> schemdraw.elements.Element:
    """Säädin: päästötransistori ylärivillä, virhevahvistin sen alla
    osoittamassa vasemmalle hilaa kohti. Palauttaa lähtösolmun."""
    nimet = (("out", "g", "fb", "X1", "M1", "R1", "R2") if ldo
             else ("out2", "g2", "fb2", "X2", "M2", "R3", "R4"))
    elm.Dot(open=True).at((x0 - 1.2, 0)).label("in", loc="top", **ISO_SOLMU)
    elm.Line().right(1.2)
    if ldo:
        m = elm.PFet().down().flip().anchor("source")
        ulos = m.drain
    else:
        m = elm.NFet().down().flip().anchor("drain")
        ulos = m.source
    elm.Label().at((x0 + 0.75, 0.4)).label(nimet[4])
    elm.Line().right(5.2).at(ulos)
    jako = elm.Dot().label(nimet[0], loc="top", **ISO_SOLMU)
    elm.Resistor().down(2.0).label(f"{nimet[5]}\n16,4 kΩ", loc="bottom")
    fb = elm.Dot().label(nimet[2], loc="right", **ISO_SOLMU)
    elm.Resistor().down(2.0).label(f"{nimet[6]}\n10 kΩ", loc="bottom")
    elm.Ground()
    elm.Line().left(2.2).at(fb.center)
    if ldo:
        op = elm.Opamp(leads=True).left().anchor("in2")
        alempi = op.in1
    else:
        op = elm.Opamp(leads=True).left().flip().anchor("in1")
        alempi = op.in2
    elm.Label().at((op.out[0] + 1.75, op.out[1])).label(nimet[3])
    elm.Line().left().at(op.out).tox(m.gate)
    elm.Dot().label(nimet[1], loc="left", **ISO_SOLMU)
    elm.Line().up().toy(m.gate)
    elm.Dot().at(alempi).label("ref", loc="right", **ISO_SOLMU)
    elm.SourceV().down(1.6).at(alempi).reverse().label("1,25 V",
                                                       loc="bottom")
    elm.Ground()
    return jako


def saadin_kaavio(kohde: Path) -> None:
    """Lineaarisäädin kahdella päästötransistorilla."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=13)
        jako = _saadin(0, True)
        elm.Line().right(2.0).at(jako.center)
        elm.Dot()
        d.push()
        elm.Capacitor().down(1.6).label("Cout\n10 µF", loc="bottom")
        elm.Dot().label("c1", loc="left", **ISO_SOLMU)
        elm.Resistor().down(1.6).label("Resr", loc="bottom")
        elm.Ground()
        d.pop()
        elm.Line().right(2.0)
        elm.SourceI().down(3.2).label("Ikuorma", loc="bottom")
        elm.Ground()
        elm.Label().at((4.5, -6.7)).label(
            "a) LDO: P-kanavainen päästötransistori,\nlähde syötössä")
        jako2 = _saadin(15.0, False)
        elm.Line().right(2.6).at(jako2.center)
        elm.SourceI().down(3.2).label("Ikuorma2", loc="bottom")
        elm.Ground()
        elm.Label().at((19.0, -6.7)).label(
            "b) seuraaja: N-kanavainen,\nlähde lähdössä")
        tallenna_kaavio(d, kohde / "saadin-kaavio.png")


def saadin_pudotus(kohde: Path) -> None:
    """Lähtö syötön funktiona ja LDO:n lähtö kuormavirran funktiona."""
    data = _ajo((ESIMERKIT / "08-saadin.cir").read_text("utf-8"),
                "wrdata pud.dat v(out) v(out2)\nalter Vin DC = 5\n"
                "dc Ikuorma 1m 100m 1m\nwrdata kuorma.dat v(out)").data
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 2.6))
    pud = data["pud"]
    a1.plot(pud[:, 0], pud[:, 1], color=KOROSTUS, label="LDO (P-kanava)")
    a1.plot(pud[:, 0], pud[:, 3], color=TOINEN, label="seuraaja (N-kanava)")
    a1.plot(pud[:, 0], pud[:, 0], color=HARMAA, lw=0.6, ls=":",
            label="lähtö = syöttö")
    a1.axhline(0.99 * 3.3, color=HARMAA, lw=0.6, ls="--")
    a1.set_xlim(3.0, 7.0)
    a1.set_ylim(2.6, 3.5)
    a1.set_xlabel("syöttöjännite (V)")
    a1.set_ylabel("lähtö (V), kuorma 100 mA")
    a1.legend(fontsize=7, loc="lower right")
    kuorma = data["kuorma"]
    a2.plot(kuorma[:, 0] * 1e3, (kuorma[:, 1] - kuorma[0, 1]) * 1e3,
            color=KOROSTUS)
    a2.set_xlabel("kuormavirta (mA)")
    a2.set_ylabel("LDO:n lähdön muutos (mV)")
    fig.tight_layout()
    fig.savefig(kohde / "saadin-pudotus.png")
    plt.close(fig)


def _saadin_ajo(esr: str, ohjaus: str) -> Tulos:
    """Ajaa stabiilisuusnetlistin yhdellä ESR:n arvolla ja omalla
    .control-lohkolla."""
    perus = (ESIMERKIT / "08-vakaus.cir").read_text("utf-8")
    perus = perus[:perus.index(".control")].replace(
        ".param ESR=0.5", f".param ESR={esr}")
    return simuloi(perus + f".control\n{ohjaus}\n.endc\n.end\n")


def saadin_vaihevara(kohde: Path) -> None:
    """LDO:n silmukkavahvistus kolmella ESR:llä ja vaihevara ESR:n
    funktiona kolmella kuormalla."""
    with contextlib.redirect_stdout(io.StringIO()):
        esim = runpy.run_path(str(ESIMERKIT / "08-vakaus.py"))
    fig = plt.figure(figsize=(5.8, 3.4))
    ruudut = fig.add_gridspec(2, 2, width_ratios=(1.15, 1.0))
    a1 = fig.add_subplot(ruudut[0, 0])
    a2 = fig.add_subplot(ruudut[1, 0], sharex=a1)
    a3 = fig.add_subplot(ruudut[:, 1])
    for esr, nimi, vari in (("0.01", "10 mΩ", TOINEN),
                            ("0.5", "0,5 Ω", KOROSTUS),
                            ("10", "10 Ω", HARMAA)):
        data = _saadin_ajo(esr, "ac dec 50 10 10Meg\n"
                           "let T = -v(fb)/v(fbi)\n"
                           "wrdata t.dat db(T) 180/pi*cph(T)").data["t"]
        a1.semilogx(data[:, 0], data[:, 1], color=vari, label=f"ESR {nimi}")
        a2.semilogx(data[:, 0], data[:, 3], color=vari)
    a1.axhline(0, color=HARMAA, lw=0.6)
    a2.axhline(-180, color=HARMAA, lw=0.6, ls="--")
    a1.set_ylabel("|T| (dB)")
    a1.set_ylim(-40, 90)
    a1.legend(fontsize=7)
    a1.tick_params(labelbottom=False)
    a2.set_ylabel("vaihe (°)")
    a2.set_ylim(-200, 0)
    a2.set_xlabel("taajuus (Hz), kuorma 100 mA")
    esrt = np.logspace(-2, 1.2, 60)
    for virta, vari in ((1e-3, HARMAA), (10e-3, TOINEN), (100e-3, KOROSTUS)):
        a3.semilogx(esrt, [esim["vaihevara"](virta, r)[1] for r in esrt],
                    color=vari, label=f"{virta * 1e3:g} mA")
    a3.axhspan(45, 90, color=KOROSTUS, alpha=0.08)
    a3.axhline(0, color=HARMAA, lw=0.6)
    a3.set_xlabel("lähtökondensaattorin ESR (Ω)")
    a3.set_ylabel("vaihevara (°)")
    a3.set_ylim(-10, 90)
    a3.legend(fontsize=7, title="kuorma", title_fontsize=7)
    fig.tight_layout()
    fig.savefig(kohde / "saadin-vaihevara.png")
    plt.close(fig)


def saadin_askel(kohde: Path) -> None:
    """Kuorma-askel 10 -> 100 mA kahdella ESR:llä."""
    fig, akselit = plt.subplots(1, 2, figsize=(5.8, 2.4), sharey=True)
    for ax, esr, nimi, vari, alue in zip(
            akselit, ("0.01", "0.5"),
            ("ESR 10 mΩ: värähtelee", "ESR 0,5 Ω: asettuu"),
            (TOINEN, KOROSTUS), ((-50, 400), (-10, 60)), strict=True):
        data = _saadin_ajo(esr, "tran 0.2u 1.5m\n"
                           "wrdata askel.dat v(out)").data["askel"]
        ax.plot((data[:, 0] - 0.2e-3) * 1e6, data[:, 1], color=vari, lw=0.8)
        ax.axvline(0, color=HARMAA, lw=0.6, ls=":")
        ax.set_title(nimi, fontsize=9)
        ax.set_xlabel("aika askeleesta (µs)")
        ax.set_xlim(alue)
    akselit[0].set_ylabel("lähtö (V)")
    fig.tight_layout()
    fig.savefig(kohde / "saadin-askel.png")
    plt.close(fig)


def saadin_hairiot(kohde: Path) -> None:
    """LDO:n PSRR ja lähdön kohinatiheys ilman referenssin suodatusta
    ja sen kanssa."""
    with contextlib.redirect_stdout(io.StringIO()):
        esim = runpy.run_path(str(ESIMERKIT / "08-hairiot.py"))
    perus = (ESIMERKIT / "08-hairiot.cir").read_text("utf-8")
    perus = perus[:perus.index(".control")]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 2.6))
    data = simuloi(perus + ".control\nac dec 20 10 10Meg\n"
                   "wrdata psrr.dat -db(v(out))\n.endc\n.end\n").data["psrr"]
    a1.semilogx(data[:, 0], data[:, 1], color=KOROSTUS, lw=2.5, alpha=0.5,
                label="SPICE")
    a1.semilogx(data[:, 0], [esim["psrr"](f) for f in data[:, 0]], "--",
                color=HARMAA, label="malli")
    a1.axvline(200e3, color=TOINEN, lw=0.8, ls=":")
    a1.text(230e3, 45, "hakkurin\n200 kHz", fontsize=7, color=TOINEN)
    a1.set_xlabel("taajuus (Hz)")
    a1.set_ylabel("PSRR (dB)")
    a1.set_ylim(0, 60)
    a1.legend(fontsize=7, loc="lower left")
    for cnr, nimi, vari in (("1f", "ilman suodatusta", TOINEN),
                            ("100n", "Cnr = 100 nF", KOROSTUS)):
        kohina = simuloi(
            perus.replace(".param CNR=1f", f".param CNR={cnr}")
            + ".control\nnoise v(out) Vin dec 20 10 100k\nsetplot noise1\n"
            "wrdata n.dat onoise_spectrum\n.endc\n.end\n").data["n"]
        a2.loglog(kohina[:, 0], kohina[:, 1] * 1e9, color=vari, label=nimi)
    a2.set_xlabel("taajuus (Hz)")
    a2.set_ylabel("lähdön kohina (nV/√Hz)")
    a2.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(kohde / "saadin-hairiot.png")
    plt.close(fig)


def buck_kaavio(kohde: Path) -> None:
    """Buck-muuntimen tehoaste."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=10)
        v = elm.SourceV().up().label("Vin\n12 V")
        elm.Dot().label("in", loc="top", **SOLMU)
        elm.Switch().right().label("S1\n(ohjaus pwm)", loc="top")
        sw = elm.Dot().label("sw", loc="top", **SOLMU)
        elm.Inductor2().right().label("L1 100 µH")
        ulos = elm.Dot().label("out", loc="top", **SOLMU)
        elm.Line().right(1.6)
        elm.Resistor().down().label("Rk", loc="bottom")
        elm.Line().left().tox(v.start)
        elm.Diode().up().at((sw.center[0], v.start[1])).toy(
            sw.center).label("D1", loc="bottom")
        elm.Capacitor().down().at(ulos.center).toy(v.start).label(
            "C1\n47 µF", loc="bottom")
        elm.Ground().at(v.start)
        tallenna_kaavio(d, kohde / "buck-kaavio.png")


def buck_aallot(kohde: Path) -> None:
    """Kytkentäsolmun jännite, kelan virta ja lähdön rippeli jatkuvassa
    ja katkeavassa johtumisessa."""
    perus = (ESIMERKIT / "08-buck.cir").read_text("utf-8")
    perus = perus[:perus.index(".control")]
    fig, akselit = plt.subplots(3, 2, figsize=(5.8, 4.0), sharex=True)
    for sarake, (korvaus, nimi) in enumerate((
            ("RK=3.3 UALKU=3.3 IALKU=1", "kuorma 3,3 Ω: jatkuva"),
            ("RK=330 UALKU=6.45 IALKU=0", "kuorma 330 Ω: katkeava"))):
        data = simuloi(
            perus.replace("RK=3.3 UALKU=3.3 IALKU=1", korvaus)
            + ".control\ntran 25n 3m 2.98m 25n uic\n"
            "wrdata b.dat v(sw) i(L1) v(out)\n.endc\n.end\n").data["b"]
        t = (data[:, 0] - data[0, 0]) * 1e6
        for rivi, (arvot, vari) in enumerate((
                (data[:, 1], HARMAA), (data[:, 3] * 1e3, KOROSTUS),
                ((data[:, 5] - data[:, 5].mean()) * 1e3, TOINEN))):
            akselit[rivi, sarake].plot(t, arvot, color=vari, lw=0.9)
        akselit[0, sarake].set_title(nimi, fontsize=9)
        akselit[2, sarake].set_xlabel("aika (µs)")
        akselit[2, sarake].set_xlim(0, 20)
    akselit[0, 0].set_ylabel("u(sw) (V)")
    akselit[1, 0].set_ylabel("kelan virta (mA)")
    akselit[2, 0].set_ylabel("lähdön\nrippeli (mV)")
    fig.tight_layout()
    fig.savefig(kohde / "buck-aallot.png")
    plt.close(fig)


def main() -> None:
    kohde = Path(sys.argv[1] if len(sys.argv) > 1 else "kuvat")
    kohde.mkdir(exist_ok=True)
    for piirtaja in (invertoiva, ce_vahvistin, ce_aallot, ce_bode, seuraaja,
                     mosfet_vahvistin, eropari, kaista_bode, integraattori,
                     integraattori_aallot, instrumentointi, tasonsiirto,
                     opamp_rajat, sallen_key, bode_suodatin, mfb, montecarlo,
                     askel_suodattimet, silmukka, vaihevara, askel_kuorma,
                     vertailija_kaavio, vertailija, kvantisointi, r2r,
                     r2r_virheet, sar_haku, naytteenotto, asettuminen,
                     sigmadelta, kohina, paatokset, heijastus,
                     ohitus_aallot, saadin_kaavio, saadin_pudotus,
                     saadin_vaihevara, saadin_askel, saadin_hairiot,
                     buck_kaavio, buck_aallot):
        piirtaja(kohde)
        print("piirretty:", piirtaja.__name__)


if __name__ == "__main__":
    main()
