"""Piirtää paketin kuvat: piirikaaviot (schemdraw) ja kuvaajat ngspicen
tuloksista. Käyttö: python3 kuvat/piirra.py kuvat

Kuvat ovat versionhallinnassa; skripti ajetaan uudelleen, kun piirit
tai esimerkit muuttuvat.
"""

from __future__ import annotations

import math
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
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
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
        elm.Resistor().up().label("R1 47 k", loc="bottom")
        elm.Vdd().label("12 V")
        d.pop()
        elm.Resistor().down().label("R2 10 k", loc="bottom")
        elm.Ground()
        elm.Capacitor().left().at(kanta.center).label("Cin 10 u")
        elm.Dot(open=True).label("tulo", loc="left")
        elm.Line().up(0.6).at(q.collector)
        kollektori = elm.Dot()
        elm.Resistor().up().label("Rc 4,7 k", loc="bottom")
        elm.Vdd().label("12 V")
        elm.Capacitor().right().at(kollektori.center).label("Cout 10 u")
        elm.Dot(open=True).label("lähtö", loc="right")
        elm.Line().down(0.4).at(q.emitter)
        emitteri = elm.Dot()
        elm.Resistor().down().label("Re 1 k", loc="bottom")
        elm.Ground()
        elm.Line().right(1.6).at(emitteri.center)
        elm.Capacitor().down().label("Ce 100 u", loc="bottom")
        elm.Ground()
        tallenna_kaavio(d, kohde / "ce-vahvistin.png")


def invertoiva(kohde: Path) -> None:
    """Invertoiva vahvistin."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=2.0, fontsize=11)
        op = elm.Opamp(leads=True)
        elm.Line().left(1.0).at(op.in1)
        miinus = elm.Dot()
        elm.Resistor().left().label("R1 10 k")
        elm.Dot(open=True).label("u_tulo", loc="left")
        elm.Line().up(1.6).at(miinus.center)
        elm.Resistor().right().tox(op.out).label("R2 100 k")
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
            label="eristysvastus 47 ohm")
    ax.set_xlabel("aika (us)")
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
    ax.plot(t, data[:, 3], color=TOINEN, label="10 ohm, pää auki")
    ax.plot(t, data[:, 1], color=KOROSTUS, label="50 ohm, pää auki")
    ax.plot(t, data[:, 5], color=HARMAA, label="10 ohm, päätetty 50 ohm")
    ax.set_xlabel("aika (ns)")
    ax.set_ylabel("kuorman jännite (V)")
    ax.legend(fontsize=8, loc="lower right")
    fig.savefig(kohde / "heijastus.png")
    plt.close(fig)


def montecarlo(kohde: Path) -> None:
    """Monte Carlo -ajon kulma- ja rajataajuuksien jakaumat."""
    import runpy
    import contextlib
    import io
    polku = Path(__file__).resolve().parent.parent / "esimerkit" / \
        "04-montecarlo.py"
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


def main() -> None:
    kohde = Path(sys.argv[1] if len(sys.argv) > 1 else "kuvat")
    kohde.mkdir(exist_ok=True)
    for piirtaja in (ce_vahvistin, invertoiva, sallen_key, bode_suodatin,
                     montecarlo, askel_suodattimet, vaihevara, askel_kuorma,
                     sigmadelta, heijastus):
        piirtaja(kohde)
        print("piirretty:", piirtaja.__name__)


if __name__ == "__main__":
    main()
